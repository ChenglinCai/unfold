"""Chinese subtitles: a model translates whole beats, and code splits them into cues.

The rules come from Netflix's Simplified Chinese style guide: at most two lines
of 16 characters in a cue, and at most 9 characters per second. A single space
takes the place of each comma and period.
"""

import argparse
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from unfold import jobs
from unfold.build import RETRIES, Job, run_job
from unfold.build.graph import Guarded, SeriesError, read_series
from unfold.build.steps import prompt
from unfold.episodes.stitch import EPISODE, Beat, episode_beats, read_parts
from unfold.episodes.subtitles import Cue, srt_text
from unfold.fields import Model, Text

LINE = 16
LINES = 2
# Characters per second, the guide's limit for adult programs.
RATE = 9
# A full-width or plain comma, a full-width period, or a period that is not a
# decimal point.
PUNCTUATION = re.compile("[\uff0c\u3002,]|(?<!\\d)\\.|\\.(?!\\d)")
FULL_WIDTH_DIGIT = re.compile("[\uff10-\uff19]")
CHINESE = re.compile(r"[\u4e00-\u9fff]")
# Untranslated English: capital acronyms and short variables pass.
ENGLISH = re.compile(r"[a-z]{4,}")
OUTPUT = "episode.zh.srt"
# Tests replace the runner, so that no test calls a model.
RUNNER: jobs.Runner | None = None
BeatId = Annotated[
    str, StringConstraints(pattern=r"^s\d+-[a-z0-9-]+/[a-z0-9][a-z0-9-]*$")
]


class TranslatedBeat(Model):
    id: BeatId
    text: Text


class TranslationReply(Model):
    beats: Annotated[list[TranslatedBeat], Field(min_length=1)]


def _phrases(text: str) -> list[str]:
    """The phrases between spaces. A phrase longer than a line splits evenly, as a
    last resort, because the checks ask for a space at least every 16 characters."""
    phrases: list[str] = []
    for token in text.split():
        count = math.ceil(len(token) / LINE)
        size = math.ceil(len(token) / count)
        phrases += [token[i : i + size] for i in range(0, len(token), size)]
    return phrases


def _groups(phrases: list[str]) -> list[list[str]]:
    """Pack whole phrases into lines, then every two lines into one cue."""
    lines: list[list[str]] = []
    for phrase in phrases:
        if lines and len(" ".join([*lines[-1], phrase])) <= LINE:
            lines[-1].append(phrase)
        else:
            lines.append([phrase])
    pairs = [lines[i : i + LINES] for i in range(0, len(lines), LINES)]
    return [[phrase for line in pair for phrase in line] for pair in pairs]


def _lines(phrases: list[str]) -> list[str]:
    """One line, or two split between phrases, with the shorter line on top."""
    whole = " ".join(phrases)
    if len(whole) <= LINE:
        return [whole]
    splits = [
        (" ".join(phrases[:k]), " ".join(phrases[k:])) for k in range(1, len(phrases))
    ]
    fits = [(top, end) for top, end in splits if len(top) <= LINE and len(end) <= LINE]
    # The most even split, with ties going to a shorter top line.
    top, bottom = min(
        fits, key=lambda s: (abs(len(s[1]) - len(s[0])), len(s[0]) > len(s[1]))
    )
    return [top, bottom]


def zh_cues(text: str, start: float, end: float) -> list[Cue]:
    """Split one translated beat into cues, timed by each one's share of characters."""
    groups = _groups(_phrases(text))
    counts = [len("".join(group)) for group in groups]
    total = sum(counts) or 1
    cues, clock = [], start
    for group, count in zip(groups, counts, strict=True):
        span = (end - start) * count / total
        text_of = "\n".join(_lines(group))
        cues.append(Cue(round(clock, 3), round(clock + span, 3), text_of))
        clock += span
    if cues:
        cues[-1] = Cue(cues[-1].start, end, cues[-1].text)
    return cues


def budget(beat: Beat) -> int:
    """The most characters a beat may hold: 9 for each spoken second, rounded down."""
    return math.floor(RATE * (beat.end - beat.start) + 1e-6)


def _rules(beat: Beat, text: str) -> list[str]:
    errors = []
    if PUNCTUATION.search(text):
        errors.append(f"{beat.id}: uses a comma or a period. Put a space in its place")
    if FULL_WIDTH_DIGIT.search(text):
        errors.append(
            f"{beat.id}: uses a full-width digit. Use half-width digits, such as 3"
        )
    if not CHINESE.search(text):
        errors.append(f"{beat.id}: holds no Chinese")
    if word := ENGLISH.search(text):
        errors.append(f"{beat.id}: keeps the English word {word.group()}")
    if long := next((run for run in text.split() if len(run) > LINE), None):
        errors.append(
            f"{beat.id}: runs {len(long)} characters without a space. "
            "Put a space at a pause, at least every 16 characters"
        )
    size, allowed = len(text.replace(" ", "")), budget(beat)
    if size > allowed:
        errors.append(f"{beat.id}: {size} characters, but its time allows {allowed}")
    return errors


def check_translation(beats: list[Beat], reply: list[tuple[str, str]]) -> list[str]:
    """Every way a reply breaks the style guide or misses a beat, each named by its beat."""
    ids = [beat_id for beat_id, _ in reply]
    expected = {beat.id for beat in beats}
    errors = [f"{beat.id}: missing" for beat in beats if beat.id not in ids]
    unique = list(dict.fromkeys(ids))
    errors += [
        f"{beat_id}: appears twice" for beat_id in unique if ids.count(beat_id) > 1
    ]
    errors += [
        f"{beat_id}: not a beat in this episode"
        for beat_id in unique
        if beat_id not in expected
    ]
    texts = dict(reply)
    for beat in beats:
        if beat.id in texts:
            errors += _rules(beat, texts[beat.id])
    return errors


def request_text(beats: list[Beat]) -> str:
    lines = [
        f"[{beat.id}] (at most {budget(beat)} characters) {beat.text}" for beat in beats
    ]
    body = "\n".join(lines)
    return f"Translate each beat into Simplified Chinese.\n\n<beats>\n{body}\n</beats>"


def translate_job(series: Path, episode: Path, model: str) -> Job | None:
    """The job that translates one rendered episode, or None when it has no beats."""
    beats = episode_beats(read_parts(episode))
    if not beats:
        return None
    output = episode / OUTPUT

    def pairs(reply: BaseModel) -> list[tuple[str, str]]:
        assert isinstance(reply, TranslationReply)
        return [(beat.id, beat.text) for beat in reply.beats]

    def check(reply: BaseModel) -> list[str]:
        return check_translation(beats, pairs(reply))

    def render(reply: BaseModel) -> str:
        texts = dict(pairs(reply))
        cues = [c for b in beats for c in zh_cues(texts[b.id], b.start, b.end)]
        return srt_text(cues)

    record = series / "records" / f"{output.relative_to(series)}.json"
    system = prompt("translate-zh")
    request = request_text(beats)
    return Job(
        "translate",
        output,
        record,
        system,
        request,
        TranslationReply,
        model,
        check,
        render,
    )


def translate(
    folder: Path, runner: jobs.Runner, model: str | None = None, retries: int = RETRIES
) -> list[tuple[str, Path]]:
    """Translate every rendered episode of a series, and report each one's status."""
    spec = read_series(folder)
    log = folder / "calls.jsonl"
    guarded = Guarded(runner, log)
    lines: list[tuple[str, Path]] = []
    for episode in sorted(path.parent for path in folder.glob("E*/outline.yaml")):
        job = translate_job(folder, episode, model or spec.model)
        if job is None or not (episode / EPISODE).is_file():
            lines.append(("skipped", episode))
            continue
        outcome = run_job(job, guarded, retries, log)
        ok = outcome.record.outcome == "ok"
        lines.append(
            ("reused" if outcome.reused else "written" if ok else "failed", job.output)
        )
    return lines


def add_translate_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    command = commands.add_parser(
        "translate", help="Write Chinese subtitles for each rendered episode."
    )
    command.add_argument("series", metavar="SERIES", help="A folder with series.yaml.")
    command.add_argument(
        "--to", required=True, choices=["zh"], help="zh writes Simplified Chinese."
    )
    command.add_argument("--model", help="Override the series file's model.")
    command.add_argument("--retries", type=int, default=RETRIES)
    command.set_defaults(run=run_translate)


def run_translate(args: argparse.Namespace) -> int:
    if args.retries < 0:
        return fail("--retries must be 0 or more", 2)
    runner = RUNNER or jobs.run_claude
    try:
        lines = translate(Path(args.series), runner, args.model, args.retries)
    except SeriesError as error:
        return fail(str(error), 2)
    except jobs.CanaryError as error:
        return fail(f"{error}. No translation ran.", 3)
    for status, path in lines:
        print(f"{status:8} {path}")
    counts = Counter(status for status, _ in lines)
    print(
        f"{counts['written']} written, {counts['reused']} reused, "
        f"{counts['failed']} failed, {counts['skipped']} skipped"
    )
    return 1 if counts["failed"] else 0


def fail(message: str, code: int) -> int:
    print(f"unfold translate: {message}", file=sys.stderr)
    return code

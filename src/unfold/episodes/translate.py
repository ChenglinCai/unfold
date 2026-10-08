"""Chinese subtitles: a model translates whole beats, and code splits them into cues.

The rules come from Netflix's Simplified Chinese style guide: at most two lines
of 16 characters in a cue, and at most 9 characters per second. A single space
takes the place of each comma and period.
"""

import math
import re
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from unfold import jobs
from unfold.build import RETRIES, Job, run_job
from unfold.build.graph import Guarded, read_series
from unfold.build.steps import prompt
from unfold.episodes.stitch import EPISODE, Beat, episode_beats, read_parts
from unfold.episodes.subtitles import Cue, srt_text
from unfold.fields import Model, Text

LINE = 16
LINES = 2
CUE = LINE * LINES
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
BeatId = Annotated[
    str, StringConstraints(pattern=r"^s\d+-[a-z0-9-]+/[a-z0-9][a-z0-9-]*$")
]


class TranslatedBeat(Model):
    id: BeatId
    text: Text


class TranslationReply(Model):
    beats: Annotated[list[TranslatedBeat], Field(min_length=1)]


def _pieces(token: str) -> list[str]:
    """Split a run with no spaces into even pieces that each fit one cue."""
    count = math.ceil(len(token) / CUE)
    size = math.ceil(len(token) / count)
    return [token[i : i + size] for i in range(0, len(token), size)]


def _chunks(text: str) -> list[str]:
    """Pack the beat's phrases into cues, breaking at spaces when it can."""
    chunks: list[str] = []
    current = ""
    for token in text.split():
        joined = f"{current} {token}" if current else token
        if len(joined) <= CUE:
            current = joined
            continue
        if current:
            chunks.append(current)
        *whole, current = _pieces(token)
        chunks += whole
    return [*chunks, current] if current else chunks


def _lines(chunk: str) -> list[str]:
    """One line, or two with the shorter on top, broken at a space if one fits."""
    if len(chunk) <= LINE:
        return [chunk]
    fits = [
        i
        for i, char in enumerate(chunk)
        if char == " " and i <= LINE and len(chunk) - i - 1 <= LINE
    ]
    if fits:
        # The most even break, with ties going to a shorter top line.
        best = min(
            fits, key=lambda i: (abs(len(chunk) - 2 * i - 1), i > len(chunk) - i - 1)
        )
        return [chunk[:best], chunk[best + 1 :]]
    half = len(chunk) // 2
    return [chunk[:half], chunk[half:]]


def zh_cues(text: str, start: float, end: float) -> list[Cue]:
    """Split one translated beat into cues, timed by each one's share of characters."""
    chunks = _chunks(" ".join(text.split()))
    counts = [len(chunk.replace(" ", "")) for chunk in chunks]
    total = sum(counts) or 1
    cues, clock = [], start
    for chunk, count in zip(chunks, counts, strict=True):
        span = (end - start) * count / total
        cues.append(
            Cue(round(clock, 3), round(clock + span, 3), "\n".join(_lines(chunk)))
        )
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

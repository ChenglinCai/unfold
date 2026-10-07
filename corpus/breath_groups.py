"""Test the breath-group hypothesis on 3Blue1Brown transcripts.

The 3Blue1Brown captions repository has no license, so its transcripts stay in
the maintainer's private folder. This script reads them by path and writes
numbers only. `corpus/README.md` says how to download them.

Usage:
    uv run python corpus/breath_groups.py PATH_TO_CAPTIONS [--out REPORT]
"""

import argparse
import dataclasses
import datetime
import itertools
import json
import math
import statistics
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from unfold.lint import lint_text
from unfold.lint.prose import breath_groups, paragraphs, words
from unfold.lint.rules import PROFILES

THRESHOLDS = (0.15, 0.25, 0.4)
ENDS = tuple(",;:.?!")
CLOSERS = "\"'\u201d\u2019)]"
Timing = tuple[str, float, float]


@dataclass(frozen=True)
class Transcript:
    name: str
    text: str
    timings: list[Timing]


def load(root: Path) -> list[Transcript]:
    """Read every English transcript under root, with its word timings if present."""
    found = []
    for path in sorted(root.glob("*/*/english/transcript.txt")):
        timing_file = path.parent / "word_timings.json"
        rows = (
            json.loads(timing_file.read_text(encoding="utf-8"))
            if timing_file.exists()
            else []
        )
        timings = [(str(w), float(s), float(e)) for w, s, e in rows]
        name = f"{path.parents[2].name}/{path.parents[1].name}"
        found.append(Transcript(name, path.read_text(encoding="utf-8"), timings))
    return found


def sentences_of(text: str) -> list[str]:
    return [s.text for p in paragraphs(text) for s in p.sentences]


def group_lengths(text: str) -> list[int]:
    return [len(words(g)) for s in sentences_of(text) for g in breath_groups(s)]


def percentile(values: Sequence[int], q: float) -> int:
    """The nearest-rank percentile."""
    ordered = sorted(values)
    return ordered[max(math.ceil(q * len(ordered)), 1) - 1]


def pause_agreement(timings: Sequence[Timing], threshold: float) -> tuple[float, float]:
    """Return the share of punctuation followed by a pause, and of pauses after punctuation."""
    punct = pauses = both = 0
    for (word, _, end), (_, next_start, _) in itertools.pairwise(timings):
        at_mark = word.strip().rstrip(CLOSERS).endswith(ENDS)
        at_pause = round(next_start - end, 3) >= threshold
        punct += at_mark
        pauses += at_pause
        both += at_mark and at_pause
    return (both / punct if punct else 0.0, both / pauses if pauses else 0.0)


def speaking_rate(timings: Sequence[Timing]) -> float:
    seconds = timings[-1][2] - timings[0][1]
    return len(timings) / seconds * 60


def calibrate(lengths: Sequence[int], total_words: int, per_thousand: float) -> int:
    """The smallest limit at which over-long breath groups stay below the given rate."""
    for limit in range(1, max(lengths) + 1):
        over = sum(length > limit for length in lengths)
        if over / total_words * 1000 < per_thousand:
            return limit
    return max(lengths)


def firing(transcripts: Sequence[Transcript], limit: int) -> tuple[float, Counter[str]]:
    """Errors per 1,000 words for the spoken profile with this breath-group limit."""
    profile = dataclasses.replace(PROFILES["spoken"], breath_words=limit)
    errors: Counter[str] = Counter()
    for transcript in transcripts:
        for finding in lint_text(transcript.text, profile):
            if finding.severity == "error":
                errors[finding.rule] += 1
    total_words = sum(len(words(t.text)) for t in transcripts)
    return sum(errors.values()) / total_words * 1000, errors


def punctuation_density(text: str) -> float:
    count = len(words(text))
    return sum(text.count(mark) for mark in ENDS) / count if count else 0.0


def usable(
    transcripts: Sequence[Transcript],
) -> tuple[list[Transcript], list[Transcript], float]:
    """Set aside transcripts with under half the median punctuation per word.

    Breath groups need punctuation. A transcript with almost none looks like
    unpunctuated captions, so its breath groups cannot be measured.
    """
    densities = [punctuation_density(t.text) for t in transcripts if words(t.text)]
    cutoff = statistics.median(densities) / 2
    keep = [
        t
        for t in transcripts
        if words(t.text) and punctuation_density(t.text) >= cutoff
    ]
    kept = {id(t) for t in keep}
    return keep, [t for t in transcripts if id(t) not in kept], cutoff


def report(everything: Sequence[Transcript]) -> str:
    """Compute every number, and return the report as Markdown."""
    transcripts, set_aside, cutoff = usable(everything)
    lengths = [n for t in transcripts for n in group_lengths(t.text)]
    total_words = sum(len(words(t.text)) for t in transcripts)
    sentence_words = [len(words(s)) for t in transcripts for s in sentences_of(t.text)]
    share_19 = sum(n <= 19 for n in lengths) / len(lengths)
    long_sentences = sum(n > 25 for n in sentence_words) / len(sentence_words)
    timed = [t for t in transcripts if len(t.timings) > 1]
    rate = statistics.median(speaking_rate(t.timings) for t in timed) if timed else 0.0
    limit = calibrate(lengths, total_words, per_thousand=1.0)
    rate_20, _ = firing(transcripts, 20)
    rate_limit, by_rule = firing(transcripts, limit)
    verdict = "holds" if share_19 >= 0.9 else "does not hold"
    rows = []
    for threshold in THRESHOLDS:
        pairs = [pause_agreement(t.timings, threshold) for t in timed]
        marks = statistics.mean(p[0] for p in pairs) if pairs else 0.0
        stops = statistics.mean(p[1] for p in pairs) if pairs else 0.0
        rows.append(f"| {threshold:.2f} s | {marks:.0%} | {stops:.0%} |")
    rules = (
        ", ".join(f"{rule} {count}" for rule, count in by_rule.most_common()) or "none"
    )
    today = datetime.date.today().isoformat()
    return "\n".join(
        [
            "# Study: breath groups in 3Blue1Brown narration",
            "",
            f"`corpus/breath_groups.py` wrote this report on {today}. It read the "
            "3Blue1Brown captions from the maintainer's private folder. The captions "
            "have no license, so this report holds numbers only.",
            "",
            "## Hypothesis",
            "",
            "The plan stated, from three transcripts, that 90 percent of breath groups "
            "have 19 words or fewer. A breath group is the run of words between two "
            "pauses, at a comma, semicolon, colon, or sentence end.",
            "",
            "## Results",
            "",
            f"- Transcripts: {len(everything)}. The study set aside {len(set_aside)} of them, "
            f"which have fewer than {cutoff:.3f} punctuation marks per word, half the median. "
            "They look like unpunctuated captions: "
            + (", ".join(t.name for t in set_aside) or "none")
            + ".",
            f"- Words in the transcripts studied: {total_words:,}",
            f"- Breath groups: {len(lengths):,}",
            f"- Breath groups with 19 words or fewer: {share_19:.1%}. The hypothesis {verdict}.",
            f"- Breath-group length, in words: median {percentile(lengths, 0.5)}, "
            f"90th percentile {percentile(lengths, 0.9)}, 95th {percentile(lengths, 0.95)}, "
            f"99th {percentile(lengths, 0.99)}, longest {max(lengths)}.",
            f"- Sentences with more than 25 words: {long_sentences:.1%}.",
            f"- Speaking rate: median {rate:.0f} words per minute, over {len(timed)} "
            "transcripts with word timings.",
            "",
            "## Punctuation and real pauses",
            "",
            "A pause is a silence of at least the threshold between two words. "
            "Goldman-Eisler's 0.25-second criterion is common, though not a gold standard, "
            "so the table also shows a shorter and a longer threshold. Source: "
            "https://pmc.ncbi.nlm.nih.gov/articles/11119743",
            "",
            "| Pause threshold | Punctuation marks followed by a pause "
            "| Pauses that follow punctuation |",
            "|---|---|---|",
            *rows,
            "",
            "## Calibration",
            "",
            f"- At a limit of 20 words, the spoken profile reports {rate_20:.2f} errors per "
            "1,000 words.",
            f"- The smallest limit with fewer than 1 breath-group error per 1,000 words is "
            f"{limit} words.",
            f"- At that limit, the spoken profile reports {rate_limit:.2f} errors per 1,000 "
            f"words in total. By rule: {rules}.",
            "",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("captions", type=Path, help="The 3Blue1Brown captions folder.")
    parser.add_argument(
        "--out", type=Path, default=Path("docs/studies/breath-groups.md")
    )
    args = parser.parse_args(argv)
    transcripts = load(args.captions)
    if not transcripts:
        parser.error(f"no transcripts under {args.captions}")
    args.out.write_text(report(transcripts), encoding="utf-8")
    print(f"Wrote {args.out} from {len(transcripts)} transcripts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

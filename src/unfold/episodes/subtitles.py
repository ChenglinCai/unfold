"""Subtitles: SRT cues for each beat, timed by its narration.

A cue holds at most two lines of 42 characters. A long beat splits into
several cues, each timed by its share of the beat's words.
"""

import re
import textwrap
from dataclasses import dataclass

LINE = 42
LINES = 2


@dataclass(frozen=True)
class Cue:
    start: float
    end: float
    text: str


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def beat_cues(text: str, start: float, end: float) -> list[Cue]:
    """Split one beat into cues that share its time by their words."""
    lines = textwrap.wrap(" ".join(text.split()), LINE) or [text]
    chunks = [" ".join(lines[i : i + LINES]) for i in range(0, len(lines), LINES)]
    counts = [len(chunk.split()) for chunk in chunks]
    total = sum(counts)
    cues, clock = [], start
    for chunk, count in zip(chunks, counts, strict=True):
        span = (end - start) * count / total
        cues.append(Cue(round(clock, 3), round(clock + span, 3), chunk))
        clock += span
    cues[-1] = Cue(cues[-1].start, end, cues[-1].text)
    return cues


def srt_text(cues: list[Cue]) -> str:
    blocks = [
        f"{number}\n{srt_time(cue.start)} --> {srt_time(cue.end)}\n{cue.text}\n"
        for number, cue in enumerate(cues, start=1)
    ]
    return "\n".join(blocks)


def vtt_text(srt: str) -> str:
    """WebVTT, which browsers play, from SubRip: a header, and a dot in each time."""
    return "WEBVTT\n\n" + re.sub(r"(\d{2}:\d{2}:\d{2}),(\d{3})", r"\1.\2", srt)

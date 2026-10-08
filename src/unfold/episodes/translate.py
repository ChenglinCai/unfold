"""Chinese subtitles: a model translates whole beats, and code splits them into cues.

The rules come from Netflix's Simplified Chinese style guide: at most two lines
of 16 characters in a cue, and at most 9 characters per second. A single space
takes the place of each comma and period.
"""

import math

from unfold.episodes.subtitles import Cue

LINE = 16
LINES = 2
CUE = LINE * LINES


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

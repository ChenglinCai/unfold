"""Chinese subtitles: a model translates whole beats, and code splits them into cues.

The rules come from Netflix's Simplified Chinese style guide: at most two lines
of 16 characters in a cue, and at most 9 characters per second. A single space
takes the place of each comma and period.
"""

import math
import re

from unfold.episodes.stitch import Beat
from unfold.episodes.subtitles import Cue

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

"""The audio check: Whisper transcribes a segment, and code compares it with the script.

Both sides become plain spoken words first, so "$10,000" in a transcript
matches "ten thousand dollars" in a script.
"""

import re
from pathlib import Path

# A segment fails when more than this share of its script's words went wrong.
LIMIT = 0.15
ONES = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
TENS = [
    "zero",
    "ten",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]
SCALES = [(10**9, "billion"), (10**6, "million"), (1000, "thousand")]
NUMBER = re.compile(r"(\$)?(\d[\d,]*)(?:\.(\d+))?(%)?")


def spoken(n: int) -> str:
    """An integer in English words, such as "one hundred five"."""
    if n < 0:
        return "minus " + spoken(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000:
        rest = "" if n % 100 == 0 else " " + spoken(n % 100)
        return ONES[n // 100] + " hundred" + rest
    for size, name in SCALES:
        if n >= size:
            rest = "" if n % size == 0 else " " + spoken(n % size)
            return f"{spoken(n // size)} {name}{rest}"
    raise AssertionError("unreachable")


def _say_number(match: re.Match[str]) -> str:
    dollars, whole, fraction, percent = match.groups()
    text = spoken(int(whole.replace(",", "")))
    if fraction:
        text += " point " + " ".join(ONES[int(digit)] for digit in fraction)
    if percent:
        text += " percent"
    if dollars:
        text += " dollars"
    return f" {text} "


def words(text: str) -> list[str]:
    """Lower-case spoken words, with numbers, money, and percents written out."""
    text = NUMBER.sub(_say_number, text)
    text = text.lower().replace("'", "").replace(chr(0x2019), "")
    return re.findall(r"[a-z]+", text)


def error_rate(reference: list[str], heard: list[str]) -> float:
    """Word edits needed to turn the script into the transcript, per script word."""
    if not reference:
        return 0.0 if not heard else 1.0
    previous = list(range(len(heard) + 1))
    for i, word in enumerate(reference, start=1):
        current = [i]
        for j, other in enumerate(heard, start=1):
            cost = 0 if word == other else 1
            current.append(
                min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
            )
        previous = current
    return previous[-1] / len(reference)


def transcribe(video: Path, model: str = "base.en") -> str:
    """What Whisper hears in a video's audio. Needs the audio extra."""
    from faster_whisper import WhisperModel  # pyright: ignore[reportMissingImports]

    from unfold.sources.recording import decode

    whisper = WhisperModel(model, device="cpu", compute_type="int8")
    segments, _ = whisper.transcribe(
        decode(video), beam_size=5, language="en", vad_filter=True
    )
    return " ".join(segment.text.strip() for segment in segments)


def check_audio(video: Path, script_text: str) -> float:
    """The word error rate of a rendered segment against its script."""
    return error_rate(words(script_text), words(transcribe(video)))

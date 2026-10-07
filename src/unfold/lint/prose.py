"""Prose units: paragraphs, sentences, breath groups, and words.

Preprocessing removes what is not prose: YAML front matter, fenced code, HTML
comments, tables, and images. It replaces inline code with the word "code" and
each link with its text, and it removes emphasis marks and cue markers. Each
unit keeps the line where it starts, so a finding can point at it.
"""

import bisect
import re
from dataclasses import dataclass

CUE = re.compile(r"^\[\[([a-z0-9][a-z0-9-]*)\]\]\s*")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|(\d+)[.)])\s+(?:\[[ xX]\]\s+)?")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
URL = re.compile(r"<https?://[^>]+>|https?://\S+")
STRONG = re.compile(r"\*\*|__")
EMPHASIS = re.compile(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

ABBREVIATIONS = (
    "e.g.", "i.e.", "vs.", "cf.", "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "St.",
    "Jr.", "No.", "Fig.", "fig.", "Eq.", "eq.", "approx.", "a.k.a.", "U.S.",
    "Ph.D.", "w.r.t.",
)  # fmt: skip
HELD = "\u2024"  # a one-character stand-in for a period that ends nothing
COMMA_HELD = "\u201a"  # stands in for a comma inside a number
COLON_HELD = "\u2236"  # stands in for a colon inside a time
CLOSERS = "\"'\u201d\u2019)\\]"
OPENERS = "\"'\u201c\u2018(\\["
SENTENCE_END = re.compile(rf"[.!?]+[{CLOSERS}]*(?=\s+[{OPENERS}]?[A-Z0-9]|\s*$)")
PAUSE = re.compile(rf"[,;:]|[.!?]+(?=[{CLOSERS}]*(?:\s|$))")
WORD = re.compile(
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|\d+(?:\.\d+)*%?"
    r"|[^\W\d_]+(?:['\u2019][^\W\d_]+)*(?:-[^\W_]+)*"
)


@dataclass(frozen=True)
class Sentence:
    text: str
    line: int
    numbered: bool


@dataclass(frozen=True)
class Paragraph:
    text: str
    line: int
    sentences: list[Sentence]
    heading: bool = False
    numbered: bool = False
    cue: str | None = None


def words(text: str) -> list[str]:
    """Return the words of a text. A number with commas counts as one word."""
    return WORD.findall(text)


def _hold(text: str) -> str:
    """Hide periods and commas that end nothing. The text keeps its length."""
    for abbreviation in ABBREVIATIONS:
        text = text.replace(abbreviation, abbreviation.replace(".", HELD))
    text = re.sub(r"(?<=\d)\.(?=\d)", HELD, text)
    text = re.sub(r"(?<=\d),(?=\d{3})", COMMA_HELD, text)
    return re.sub(r"(?<=\d):(?=\d)", COLON_HELD, text)


def _release(text: str) -> str:
    return text.replace(HELD, ".").replace(COMMA_HELD, ",").replace(COLON_HELD, ":")


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, without splitting decimals or abbreviations."""
    held = _hold(text)
    pieces, start = [], 0
    for end in SENTENCE_END.finditer(held):
        pieces.append(held[start : end.end()])
        start = end.end()
    pieces.append(held[start:])
    return [_release(p).strip() for p in pieces if p.strip()]


def breath_groups(sentence: str) -> list[str]:
    """Split a sentence at commas, semicolons, colons, and its end."""
    groups = (_release(g).strip() for g in PAUSE.split(_hold(sentence)))
    return [g for g in groups if words(g)]


def _inline(line: str) -> str:
    line = IMAGE.sub("", line)
    line = INLINE_CODE.sub("code", line)
    line = LINK.sub(r"\1", line)
    line = URL.sub("link", line)
    line = STRONG.sub("", line)
    return re.sub(r"\s+", " ", EMPHASIS.sub(r"\1", line))


def _prose_lines(text: str) -> list[tuple[int, str]]:
    """Return (line number, line) pairs, with blank strings for non-prose lines."""
    # A comment becomes the newlines it spanned, so later lines keep their numbers.
    text = COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    lines = text.splitlines()
    out: list[tuple[int, str]] = []
    in_fence = False
    body = 0
    if lines and lines[0].strip() == "---":
        ends = (i for i in range(1, len(lines)) if lines[i].strip() == "---")
        closing = next(ends, None)
        if closing is not None:
            body = closing + 1
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            out.append((number, ""))
        elif number <= body or in_fence or line.lstrip().startswith("|"):
            out.append((number, ""))
        else:
            out.append((number, re.sub(r"^\s*>\s?", "", line)))
    return out


def _make(parts: list[tuple[int, str]], heading: bool, numbered: bool) -> Paragraph:
    cue = None
    first_line, first = parts[0]
    match = CUE.match(first)
    if match:
        cue = match.group(1)
        parts[0] = (first_line, first[match.end() :])
    starts, chunks, offset = [], [], 0
    for line, chunk in parts:
        chunk = _inline(chunk).strip()
        if not chunk:
            continue
        starts.append((offset, line))
        chunks.append(chunk)
        offset += len(chunk) + 1
    text = " ".join(chunks)
    sentences: list[Sentence] = []
    if not heading:
        offsets = [o for o, _ in starts]
        cursor = 0
        for piece in split_sentences(text):
            at = text.find(piece, cursor)
            cursor = at + len(piece)
            line = starts[max(bisect.bisect_right(offsets, at) - 1, 0)][1]
            sentences.append(Sentence(piece, line, numbered))
    return Paragraph(text, parts[0][0], sentences, heading, numbered, cue)


def paragraphs(text: str) -> list[Paragraph]:
    """Split Markdown or plain text into prose paragraphs, list items, and headings."""
    found: list[Paragraph] = []
    current: list[tuple[int, str]] = []
    numbered = False

    def close() -> None:
        nonlocal current
        if current and any(chunk.strip() for _, chunk in current):
            found.append(_make(current, heading=False, numbered=numbered))
        current = []

    for number, line in _prose_lines(text):
        if not line.strip():
            close()
        elif HEADING.match(line):
            close()
            title = [(number, HEADING.sub("", line))]
            found.append(_make(title, heading=True, numbered=False))
        elif item := LIST_ITEM.match(line):
            close()
            numbered = item.group(1) is not None
            current = [(number, line[item.end() :])]
        else:
            if not current:
                numbered = False
            current.append((number, line))
    close()
    return [p for p in found if p.text]

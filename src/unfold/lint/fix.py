"""The safe fixer: it rewrites abbreviations and avoided terms, and nothing else.

It skips front matter, fenced code, inline code, HTML comments, link addresses,
and URLs, so it never changes code or a link.
"""

import re

from unfold.lint import words as lists
from unfold.lint.prose import FENCE
from unfold.lint.rules import ABBREVIATION, keep_capital

PROTECTED = re.compile(r"`[^`\n]*`|\]\([^)]*\)|<!--.*?-->|https?://\S+")


def _replacer(terms: dict[str, str]) -> re.Pattern[str] | None:
    if not terms:
        return None
    ordered = sorted(terms, key=len, reverse=True)
    return re.compile(
        r"\b(" + "|".join(map(re.escape, ordered)) + r")\b", re.IGNORECASE
    )


def _fix_prose(
    segment: str, terms: dict[str, str], term_pattern: re.Pattern[str] | None
) -> str:
    def spoken(match: re.Match[str]) -> str:
        short = match.group(1)
        return keep_capital(short, lists.ABBREVIATIONS[short.lower()])

    segment = ABBREVIATION.sub(spoken, segment)
    if term_pattern is not None:
        segment = term_pattern.sub(
            lambda m: keep_capital(m.group(1), terms[m.group(1).lower()]), segment
        )
    return segment


def _fix_line(
    line: str, terms: dict[str, str], term_pattern: re.Pattern[str] | None
) -> str:
    out, start = [], 0
    for protected in PROTECTED.finditer(line):
        out.append(_fix_prose(line[start : protected.start()], terms, term_pattern))
        out.append(protected.group(0))
        start = protected.end()
    out.append(_fix_prose(line[start:], terms, term_pattern))
    return "".join(out)


def fix_text(text: str, terms: dict[str, str]) -> str:
    """Return text with abbreviations spelled out and avoided terms replaced."""
    term_pattern = _replacer(terms)
    lines = text.split("\n")
    front_matter = bool(lines) and lines[0].strip() == "---"
    in_fence = in_comment = False
    for index, line in enumerate(lines):
        if front_matter:
            front_matter = not (index > 0 and line.strip() == "---")
            continue
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if in_comment:
            in_comment = "-->" not in line
            continue
        if "<!--" in line and "-->" not in line.split("<!--", 1)[1]:
            in_comment = True
            before = line.split("<!--", 1)[0]
            lines[index] = _fix_line(before, terms, term_pattern) + line[len(before) :]
            continue
        lines[index] = _fix_line(line, terms, term_pattern)
    return "\n".join(lines)

"""Rules and profiles of the Narration Standard.

Each check yields hits. The profile decides whether a rule runs, and whether
its hits are errors or warnings. `specs/002-language/contracts/cli.md` lists
every rule with its severity in each profile.
"""

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Literal

from unfold.lint import words as lists
from unfold.lint.prose import Paragraph, words

Severity = Literal["error", "warning"]
ERROR: Severity = "error"
WARNING: Severity = "warning"


@dataclass(frozen=True)
class Hit:
    """What a check finds, before a profile gives it a severity."""

    line: int
    excerpt: str
    message: str
    fix: tuple[str, str] | None = None


@dataclass(frozen=True)
class Finding:
    """One rule firing at one place in one file."""

    rule: str
    name: str
    severity: Severity
    path: str
    line: int
    excerpt: str
    message: str
    fix: tuple[str, str] | None = None


@dataclass(frozen=True)
class Profile:
    name: str
    severities: dict[str, Severity]
    sentence_words: int
    step_words: int = 20
    breath_words: int | None = None
    paragraph_sentences: int | None = None


@dataclass(frozen=True)
class Context:
    paragraphs: list[Paragraph]
    profile: Profile
    terms: dict[str, str] = field(default_factory=dict)


Check = Callable[[Context], Iterator[Hit]]
RULES: dict[str, tuple[str, Check]] = {}


def rule(rule_id: str, name: str) -> Callable[[Check], Check]:
    def register(check: Check) -> Check:
        RULES[rule_id] = (name, check)
        return check

    return register


def excerpt(text: str, limit: int = 80) -> str:
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def prose(context: Context) -> Iterator[tuple[int, str]]:
    """Every sentence, and every heading, with its line."""
    for paragraph in context.paragraphs:
        if paragraph.heading:
            yield paragraph.line, paragraph.text
        for sentence in paragraph.sentences:
            yield sentence.line, sentence.text


def matches(
    context: Context, pattern: re.Pattern[str]
) -> Iterator[tuple[int, re.Match[str]]]:
    for line, text in prose(context):
        for match in pattern.finditer(text):
            yield line, match


@rule("N101", "sentence-length")
def sentence_length(context: Context) -> Iterator[Hit]:
    limit = context.profile.sentence_words
    for paragraph in context.paragraphs:
        for sentence in paragraph.sentences:
            count = len(words(sentence.text))
            if not sentence.numbered and count > limit:
                yield Hit(
                    sentence.line,
                    excerpt(sentence.text),
                    f"{count} words; the limit is {limit}.",
                )


@rule("N102", "step-length")
def step_length(context: Context) -> Iterator[Hit]:
    limit = context.profile.step_words
    for paragraph in context.paragraphs:
        for sentence in paragraph.sentences:
            count = len(words(sentence.text))
            if sentence.numbered and count > limit:
                message = f"{count} words; a numbered step allows {limit}."
                yield Hit(sentence.line, excerpt(sentence.text), message)


@rule("N104", "paragraph-length")
def paragraph_length(context: Context) -> Iterator[Hit]:
    limit = context.profile.paragraph_sentences
    for paragraph in context.paragraphs:
        count = len(paragraph.sentences)
        if limit is not None and count > limit:
            message = f"{count} sentences; a paragraph allows {limit}."
            yield Hit(paragraph.line, excerpt(paragraph.text), message)


SYMBOLS = re.compile("->|<-|=>|⇒|⇐|→|←|↔|·")


@rule("N201", "symbol-shorthand")
def symbol_shorthand(context: Context) -> Iterator[Hit]:
    for line, match in matches(context, SYMBOLS):
        yield Hit(line, match.group(0), f"Write {match.group(0)!r} out in words.")


@rule("N202", "parentheses")
def parentheses(context: Context) -> Iterator[Hit]:
    for line, match in matches(context, re.compile(r"\([^)]*\)?")):
        yield Hit(
            line,
            excerpt(match.group(0)),
            "Use a separate sentence instead of parentheses.",
        )


BE = r"\b(?:am|is|are|was|were|be|been|being)"
PARTICIPLE = r"(?:\w{2,}ed|" + "|".join(sorted(lists.IRREGULAR_PARTICIPLES)) + r")"
PASSIVE = re.compile(rf"{BE}\s+(?:\w+ly\s+)?{PARTICIPLE}\b", re.IGNORECASE)


@rule("N301", "passive-voice")
def passive_voice(context: Context) -> Iterator[Hit]:
    for line, match in matches(context, PASSIVE):
        yield Hit(line, match.group(0), "Use active voice: say who does it.")


W, E = WARNING, ERROR
PROFILES = {
    "written": Profile(
        "written",
        {"N101": E, "N102": E, "N104": W, "N201": E, "N202": W, "N203": W, "N301": W,
         "N302": W, "N303": W, "N304": W, "N305": W, "N900": E},
        sentence_words=25,
        paragraph_sentences=6,
    ),
    "spoken": Profile(
        "spoken",
        {"N101": W, "N102": E, "N103": E, "N201": E, "N202": E, "N203": E, "N204": E,
         "N205": E, "N206": W, "N302": W, "N303": W, "N304": W, "N305": W, "N900": E},
        sentence_words=40,
        breath_words=20,
    ),
    "strict": Profile(
        "strict",
        {"N101": E, "N102": E, "N103": E, "N104": E, "N201": E, "N202": W, "N203": E,
         "N301": W, "N302": W, "N303": W, "N304": W, "N305": W, "N900": E},
        sentence_words=25,
        breath_words=20,
        paragraph_sentences=6,
    ),
}  # fmt: skip

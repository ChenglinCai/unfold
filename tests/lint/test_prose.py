"""Prose units: paragraphs, sentences, and breath groups, with their lines."""

from unfold.lint.prose import breath_groups, paragraphs, split_sentences, words

DOC = """---
title: front matter is not prose
---

# A heading

First sentence here. Second sentence
continues on the next line.

```python
code = "is not prose. Not at all."
```

| a table | is not prose |
|---|---|

<!-- a comment is not prose -->
Use `inline code` and [a link](https://example.com/x.y).

- A list item without a period
- Another item.

1. A numbered step.
"""


def texts(doc: str) -> list[str]:
    return [p.text for p in paragraphs(doc) if not p.heading]


def test_keeps_only_prose() -> None:
    assert texts(DOC) == [
        "First sentence here. Second sentence continues on the next line.",
        "Use code and a link.",
        "A list item without a period",
        "Another item.",
        "A numbered step.",
    ]


def test_headings_are_kept_apart() -> None:
    headings = [p.text for p in paragraphs(DOC) if p.heading]
    assert headings == ["A heading"]


def test_sentences_keep_the_line_where_they_start() -> None:
    first = paragraphs(DOC)[1]
    assert [(s.text, s.line) for s in first.sentences] == [
        ("First sentence here.", 7),
        ("Second sentence continues on the next line.", 7),
    ]
    later = paragraphs("One.\nTwo starts here.\n")[0]
    assert [s.line for s in later.sentences] == [1, 2]


def test_numbered_steps_are_marked() -> None:
    steps = [p for p in paragraphs(DOC) if p.numbered]
    assert [p.text for p in steps] == ["A numbered step."]
    assert steps[0].sentences[0].numbered


def test_splits_sentences_but_not_numbers_or_abbreviations() -> None:
    assert split_sentences("It costs 1.40 dollars. Then it rises.") == [
        "It costs 1.40 dollars.",
        "Then it rises.",
    ]
    assert split_sentences("Use a word, e.g. Python here. Next one?") == [
        "Use a word, e.g. Python here.",
        "Next one?",
    ]
    assert split_sentences("Version 0.21.0 is out. Dr. Smith agrees.") == [
        "Version 0.21.0 is out.",
        "Dr. Smith agrees.",
    ]


def test_breath_groups_split_at_pauses() -> None:
    assert breath_groups("One, two three; four: five six.") == [
        "One",
        "two three",
        "four",
        "five six",
    ]
    assert breath_groups("About 1,000 people came, and left.") == [
        "About 1,000 people came",
        "and left",
    ]


def test_counts_words_and_numbers() -> None:
    assert words("It's 1,000 well-known points, roughly.") == [
        "It's",
        "1,000",
        "well-known",
        "points",
        "roughly",
    ]


def test_cue_markers_are_not_prose() -> None:
    beat = paragraphs("[[points]] Here are points.\n")[0]
    assert beat.text == "Here are points."
    assert beat.cue == "points"


def test_comments_hide_only_themselves() -> None:
    assert texts("Before <!-- hidden --> after.\n") == ["Before after."]
    assert texts("<!--\nhidden\n-->\nText after.\n") == ["Text after."]
    kept = paragraphs("Kept text <!-- starts\nhidden\n--> tail words.\n")
    assert [(p.text, p.line) for p in kept] == [("Kept text", 1), ("tail words.", 3)]


def test_only_indented_lines_continue_a_list_item() -> None:
    text = "1. A numbered step.\n   It continues here.\nA plain sentence follows.\n"
    found = paragraphs(text)
    assert [(p.text, p.numbered) for p in found] == [
        ("A numbered step. It continues here.", True),
        ("A plain sentence follows.", False),
    ]


def test_task_checkboxes_are_not_words() -> None:
    assert texts("- [ ] T001 Write it.\n- [X] T002 Done.\n") == [
        "T001 Write it.",
        "T002 Done.",
    ]


def test_empty_text_has_no_paragraphs() -> None:
    assert paragraphs("") == []

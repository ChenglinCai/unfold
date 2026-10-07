"""The fixer rewrites abbreviations and avoided terms, and nothing else."""

from pathlib import Path

from unfold.cli import main
from unfold.lint.fix import fix_text

TERMS = {"bookmark": "cue", "in order to": "to"}


def test_expands_abbreviations() -> None:
    assert fix_text("Pick one, e.g. a cat.", TERMS) == "Pick one, for example a cat."
    assert fix_text("E.g. this works.", TERMS) == "For example this works."


def test_replaces_avoided_terms_and_keeps_capitals() -> None:
    text = "Add a bookmark. Bookmark it in order to find it."
    assert fix_text(text, TERMS) == "Add a cue. Cue it to find it."


def test_leaves_code_alone() -> None:
    text = "Run `e.g. bookmark` now.\n\n```\ne.g. bookmark\n```\n"
    assert fix_text(text, TERMS) == text


def test_leaves_link_targets_alone() -> None:
    text = "See [the bookmark page](https://example.com/bookmark-e.g.html)."
    assert (
        fix_text(text, TERMS)
        == "See [the cue page](https://example.com/bookmark-e.g.html)."
    )


def test_running_twice_changes_nothing_more() -> None:
    once = fix_text("A bookmark, e.g. one.", TERMS)
    assert fix_text(once, TERMS) == once


def test_the_command_fixes_files_in_place(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("Pick one, e.g. a cat.\n", encoding="utf-8")

    assert main(["lint", "--fix", str(doc)]) == 0
    assert doc.read_text(encoding="utf-8") == "Pick one, for example a cat.\n"

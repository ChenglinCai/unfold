"""The linter flags every AI-style paragraph, and no clean one."""

from pathlib import Path

import pytest

from unfold.lint import lint_text
from unfold.lint.prose import paragraphs

SETS = Path(__file__).parent / "sets"
AI_HABITS = {"N302", "N303", "N304"}


def paragraphs_of(name: str) -> list[str]:
    return [p.text for p in paragraphs((SETS / name).read_text(encoding="utf-8"))]


def test_the_sets_are_big_enough() -> None:
    assert len(paragraphs_of("ai_style.md")) >= 10
    assert len(paragraphs_of("clean.md")) >= 5


@pytest.mark.parametrize("profile", ["written", "spoken", "strict"])
def test_every_ai_style_paragraph_gets_an_ai_habit_finding(profile: str) -> None:
    for text in paragraphs_of("ai_style.md"):
        rules = {f.rule for f in lint_text(text, profile)}
        assert rules & AI_HABITS, text


@pytest.mark.parametrize("profile", ["written", "spoken", "strict"])
def test_clean_paragraphs_get_no_errors_and_no_ai_habits(profile: str) -> None:
    for text in paragraphs_of("clean.md"):
        findings = lint_text(text, profile)
        assert not [f for f in findings if f.severity == "error"], text
        assert not {f.rule for f in findings} & AI_HABITS, text


def test_avoided_terms_name_the_preferred_term() -> None:
    [finding] = lint_text("Each bookmark marks a word.", terms={"bookmark": "cue"})
    assert (finding.rule, finding.severity) == ("N305", "warning")
    assert "cue" in finding.message
    assert finding.fix == ("bookmark", "cue")

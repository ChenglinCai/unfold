"""The spoken profile: breath groups, and what a voice cannot read well."""

from unfold.lint import lint_text
from unfold.lint.rules import PROFILES


def found(text: str) -> dict[str, str]:
    """Each rule that fires, with its severity."""
    return {f.rule: f.severity for f in lint_text(text, profile="spoken")}


def words(n: int) -> str:
    return " ".join(["Word"] + ["word"] * (n - 1))


LIMIT = PROFILES["spoken"].breath_words or 0


def test_a_long_breath_group_is_an_error() -> None:
    assert found(words(LIMIT + 1) + ".") == {"N103": "error"}
    assert found(words(LIMIT) + ".") == {}


def test_long_sentences_with_short_breath_groups_only_warn() -> None:
    short_groups = ", ".join([words(9)] * 5) + "."
    assert found(short_groups) == {"N101": "warning"}


def test_parentheses_are_errors() -> None:
    assert found("It works (mostly) well.") == {"N202": "error"}


def test_abbreviations_are_errors_with_a_fix() -> None:
    [finding] = lint_text("Pick one, e.g. a cat.", profile="spoken")
    assert (finding.rule, finding.severity) == ("N203", "error")
    assert finding.fix == ("e.g.", "for example")


def test_math_symbols_are_errors_but_currency_is_fine() -> None:
    assert found("So x = 2 + y.") == {"N204": "error"}
    assert found("We take $x$ here.") == {"N204": "error"}
    assert found("It was worth $700 million.") == {}


def test_references_to_source_layout_are_errors() -> None:
    assert found("As Figure 3 shows, it grows.") == {"N205": "error"}
    assert found("See slide 12 for more.") == {"N205": "error"}
    assert found("Look at the table above.") == {"N205": "error"}
    assert found("In chapter 2, we saw this.") == {}


def test_this_far_from_its_cue_warns() -> None:
    # "this" may be the 15th word after the cue, but not the 16th.
    fifteenth = "[[cue]] " + words(13) + " and this one."
    sixteenth = "[[cue]] " + words(14) + " and this one."
    assert found(fifteenth) == {}
    assert found(sixteenth) == {"N206": "warning"}


def test_this_without_a_cue_is_not_checked() -> None:
    assert found(words(16) + " and this one.") == {}


def test_cue_markers_are_not_words() -> None:
    sentence = ", ".join([words(8)] * 5) + "."
    assert found("[[cue]] " + sentence) == {}
    assert found("[[cue]] " + sentence.replace(".", " more.")) == {"N101": "warning"}

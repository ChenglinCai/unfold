"""The written profile: limits from data-model.md and the constitution."""

from unfold.lint import lint_text


def sentence(n: int) -> str:
    """A sentence of n words. It starts with a capital, as real sentences do."""
    return " ".join(["Word"] + ["word"] * (n - 1)) + "."


def rules(text: str) -> list[str]:
    return [f.rule for f in lint_text(text, profile="written")]


def test_sentences_may_have_25_words() -> None:
    assert "N101" not in rules(sentence(25))


def test_a_26_word_sentence_is_an_error() -> None:
    [finding] = [
        f for f in lint_text(sentence(26), profile="written") if f.rule == "N101"
    ]
    assert finding.severity == "error"
    assert "26 words" in finding.message
    assert finding.line == 1


def test_numbered_steps_allow_20_words() -> None:
    assert "N102" not in rules("1. " + sentence(20))
    assert "N102" in rules("1. " + sentence(21))
    assert "N101" not in rules("1. " + sentence(21))


def test_paragraphs_allow_6_sentences() -> None:
    six = " ".join([sentence(3)] * 6)
    seven = " ".join([sentence(3)] * 7)
    assert "N104" not in rules(six)
    [finding] = [f for f in lint_text(seven, profile="written") if f.rule == "N104"]
    assert finding.severity == "warning"


def test_arrows_in_prose_are_errors_but_not_in_code() -> None:
    assert "N201" in rules("Data flows from A -> B.")
    assert "N201" in rules("Data flows from A → B.")
    assert "N201" not in rules("Run `a -> b` to see it.")
    assert "N201" not in rules("```\na -> b\n```\n")


def test_parentheses_are_warnings() -> None:
    [finding] = [
        f for f in lint_text("It works (mostly) well.", "written") if f.rule == "N202"
    ]
    assert finding.severity == "warning"


def test_passive_voice_is_a_warning() -> None:
    assert "N301" in rules("The file is written by the hook.")
    assert "N301" in rules("The tests were quickly run.")
    assert "N301" not in rules("The hook writes the file.")


def test_headings_are_not_sentences() -> None:
    assert rules("# " + " ".join(["word"] * 30)) == []


def test_clean_prose_has_no_findings() -> None:
    assert rules("The hook formats each file. It runs after every edit.") == []


def test_findings_come_in_line_order() -> None:
    text = f"{sentence(30)}\n\nShort one.\n\n{sentence(27)}\n"
    assert [f.line for f in lint_text(text, "written")] == [1, 5]

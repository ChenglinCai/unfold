"""The audio check compares what Whisper hears with what the script says."""

from unfold.episodes.audio import error_rate, spoken, words


def test_numbers_become_spoken_words() -> None:
    assert spoken(105) == "one hundred five"
    assert spoken(10000) == "ten thousand"
    assert spoken(1200000) == "one million two hundred thousand"


def test_words_normalize_digits_money_and_percents() -> None:
    assert words("It grew to $10,000, a 5% gain.") == [
        "it",
        "grew",
        "to",
        "ten",
        "thousand",
        "dollars",
        "a",
        "five",
        "percent",
        "gain",
    ]
    assert words("Euler's well-known identity") == [
        "eulers",
        "well",
        "known",
        "identity",
    ]


def test_the_error_rate_counts_edits_per_script_word() -> None:
    script = words("the price moves toward the crossing point")

    assert error_rate(script, script) == 0.0
    assert error_rate(script, words("the price moves to the crossing point")) == 1 / 7
    assert error_rate(script, []) == 1.0

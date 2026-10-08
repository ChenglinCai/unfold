"""Chinese subtitles: whole beats, translated, then split into cues by code."""

from itertools import pairwise

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from unfold.episodes.stitch import Beat
from unfold.episodes.subtitles import Cue
from unfold.episodes.translate import budget, check_translation, zh_cues

# Thirty and ten Chinese characters, for beats of known length.
THIRTY = "复利就是利息再生利息" * 3
TEN = "这就是复利增长的道理"


def lines_of(cues: list[Cue]) -> list[list[str]]:
    return [cue.text.split("\n") for cue in cues]


def test_a_short_beat_stays_one_cue() -> None:
    assert zh_cues("把一百美元存进银行", 0.0, 4.0) == [
        Cue(0.0, 4.0, "把一百美元存进银行")
    ]


def test_a_long_beat_splits_into_cues_of_two_short_lines() -> None:
    text = f"{THIRTY} {TEN}"

    cues = zh_cues(text, 0.0, 8.0)

    assert len(cues) > 1
    assert all(len(lines) <= 2 for lines in lines_of(cues))
    assert all(len(line) <= 16 for lines in lines_of(cues) for line in lines)
    shown = "".join(cue.text for cue in cues).replace("\n", "").replace(" ", "")
    assert shown == text.replace(" ", "")


def test_two_lines_break_at_a_space_with_the_shorter_line_on_top() -> None:
    [cue] = zh_cues("一年后你有一百零五美元 两年后大约有一百一十美元", 0.0, 5.0)

    top, bottom = cue.text.split("\n")
    assert (top, bottom) == ("一年后你有一百零五美元", "两年后大约有一百一十美元")
    assert len(top) <= len(bottom)


def test_time_follows_each_cues_share_of_characters() -> None:
    first, second = zh_cues(f"{THIRTY} {TEN}", 0.0, 4.0)

    assert (first.start, first.end) == (0.0, 3.0)
    assert (second.start, second.end) == (3.0, 4.0)


def test_a_long_run_without_spaces_splits_into_even_pieces() -> None:
    cues = zh_cues(THIRTY + TEN, 1.0, 5.0)

    assert [len(cue.text.replace("\n", "")) for cue in cues] == [20, 20]
    assert cues[-1].end == pytest.approx(5.0)


phrases = st.text(alphabet="复利就是利息再生这道理一二三45", min_size=1, max_size=40)


@settings(max_examples=200, deadline=None)
@given(words=st.lists(phrases, min_size=1, max_size=8), seconds=st.floats(1, 60))
def test_any_beat_splits_into_cues_that_fit(words: list[str], seconds: float) -> None:
    text = " ".join(words)

    cues = zh_cues(text, 10.0, 10.0 + seconds)

    for cue in cues:
        lines = cue.text.split("\n")
        assert len(lines) <= 2 and all(len(line) <= 16 for line in lines)
    kept = "".join(cue.text for cue in cues).replace("\n", "").replace(" ", "")
    assert kept == text.replace(" ", "")
    assert cues[0].start == 10.0 and cues[-1].end == 10.0 + seconds
    assert all(first.end <= second.start for first, second in pairwise(cues))


BEATS = [
    Beat("s1-a/one", "One hundred dollars.", 0.0, 4.0),
    Beat("s1-a/two", "It grows.", 4.3, 6.3),
]
GOOD = [("s1-a/one", "一百美元"), ("s1-a/two", "它会增长")]
PUNCTUATION = "s1-a/one: uses a comma or a period. Put a space in its place"


def test_a_clean_translation_passes() -> None:
    assert check_translation(BEATS, GOOD) == []


@pytest.mark.parametrize(
    ("text", "error"),
    [
        ("一百美元\uff0c存进银行", PUNCTUATION),
        ("一百美元。", PUNCTUATION),
        ("一百美元, 存进银行", PUNCTUATION),
        ("一百美元.", PUNCTUATION),
        (
            "一百美元 \uff13年",
            "s1-a/one: uses a full-width digit. Use half-width digits, such as 3",
        ),
        ("one hundred", "s1-a/one: holds no Chinese"),
        ("一百 dollars", "s1-a/one: keeps the English word dollars"),
    ],
)
def test_each_rule_fails_and_names_the_beat(text: str, error: str) -> None:
    assert error in check_translation(BEATS, [("s1-a/one", text), GOOD[1]])


@pytest.mark.parametrize(
    "text", ["利率是3.5", "NPV 是一百美元", "x 等于 3", "真的吗\uff1f"]
)
def test_decimals_acronyms_variables_and_question_marks_pass(text: str) -> None:
    assert check_translation(BEATS, [("s1-a/one", text), GOOD[1]]) == []


def test_missing_extra_and_repeated_beats_are_named() -> None:
    reply = [GOOD[0], GOOD[0], ("s1-a/three", "额外的")]

    assert check_translation(BEATS, reply) == [
        "s1-a/two: missing",
        "s1-a/one: appears twice",
        "s1-a/three: not a beat in this episode",
    ]


def test_a_beat_over_its_budget_states_the_budget() -> None:
    assert budget(BEATS[0]) == 36 and budget(BEATS[1]) == 18

    errors = check_translation(BEATS, [("s1-a/one", THIRTY + TEN), GOOD[1]])

    assert errors == ["s1-a/one: 40 characters, but its time allows 36"]

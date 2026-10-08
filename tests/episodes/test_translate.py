"""Chinese subtitles: whole beats, translated, then split into cues by code."""

from itertools import pairwise

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from unfold.episodes.subtitles import Cue
from unfold.episodes.translate import zh_cues

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

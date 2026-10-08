"""Subtitles give each beat cues that start when its narration starts."""

from unfold.episodes.subtitles import Cue, beat_cues, srt_text, srt_time, vtt_text


def test_times_use_the_srt_format() -> None:
    assert srt_time(3725.5) == "01:02:05,500"


def test_a_short_beat_is_one_cue() -> None:
    cues = beat_cues("Money grows.", 2.0, 4.5)

    assert cues == [Cue(2.0, 4.5, "Money grows.")]


def test_a_long_beat_splits_into_cues_timed_by_their_words() -> None:
    text = " ".join(["word"] * 30)

    cues = beat_cues(text, 0.0, 10.0)

    assert len(cues) == 2
    assert cues[0].start == 0.0 and cues[-1].end == 10.0
    assert all(len(cue.text) <= 84 for cue in cues)
    assert abs(cues[0].end - cues[1].start) < 1e-9


def test_srt_text_numbers_each_cue() -> None:
    text = srt_text([Cue(0.0, 1.5, "One."), Cue(1.5, 3.0, "Two.")])

    assert (
        text
        == "1\n00:00:00,000 --> 00:00:01,500\nOne.\n\n2\n00:00:01,500 --> 00:00:03,000\nTwo.\n"
    )


def test_webvtt_adds_a_header_and_puts_a_dot_in_each_time() -> None:
    srt = "1\n00:00:02,000 --> 00:00:04,500\nHello, world\n"

    assert vtt_text(srt) == "WEBVTT\n\n1\n00:00:02.000 --> 00:00:04.500\nHello, world\n"

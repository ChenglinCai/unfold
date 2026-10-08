"""Stitching joins title cards and segments into one episode, with its subtitles."""

import shutil
import subprocess
from pathlib import Path

import av
import pytest

from unfold.episodes.stitch import Part, concat, episode_cues, seconds_of
from unfold.episodes.subtitles import Cue

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="needs ffmpeg")


def clip(path: Path, seconds: float, audio: bool = True) -> Path:
    command = ["ffmpeg", "-y", "-loglevel", "error"]
    command += ["-f", "lavfi", "-i", f"testsrc=duration={seconds}:size=160x90:rate=15"]
    if audio:
        command += ["-f", "lavfi", "-i", f"sine=duration={seconds}", "-shortest"]
    subprocess.run([*command, "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


@needs_ffmpeg
def test_concat_joins_videos_in_order_with_their_sound(tmp_path: Path) -> None:
    parts = [clip(tmp_path / "a.mp4", 1.0), clip(tmp_path / "b.mp4", 2.0)]

    out = concat(parts, tmp_path / "episode.mp4")

    assert abs(seconds_of(out) - 3.0) < 0.2
    with av.open(str(out)) as container:
        assert container.streams.audio


@needs_ffmpeg
def test_concat_works_without_sound_when_a_part_is_silent(tmp_path: Path) -> None:
    parts = [clip(tmp_path / "a.mp4", 1.0, audio=False), clip(tmp_path / "b.mp4", 1.0)]

    out = concat(parts, tmp_path / "episode.mp4")

    assert abs(seconds_of(out) - 2.0) < 0.2


def test_episode_cues_shift_each_segment_by_what_came_before() -> None:
    parts = [
        Part(card=2.0, segment=5.0, beats=[("First beat.", 0.0, 5.0)]),
        Part(card=2.0, segment=3.0, beats=[("Second beat.", 0.0, 3.0)]),
    ]

    assert episode_cues(parts) == [
        Cue(2.0, 7.0, "First beat."),
        Cue(9.0, 12.0, "Second beat."),
    ]

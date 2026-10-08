"""Stitching joins title cards and segments into one episode, with its subtitles."""

import json
import shutil
import subprocess
from pathlib import Path

import av
import pytest
import yaml

from unfold.episodes import stitch
from unfold.episodes.stitch import (
    Beat,
    Part,
    concat,
    episode_beats,
    episode_cues,
    read_parts,
    seconds_of,
)
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


def test_episode_beats_name_each_beat_and_shift_its_time() -> None:
    parts = [
        Part(2.0, 5.0, [("First beat.", 0.0, 4.7)], names=["s1-a/first"]),
        Part(2.0, 3.0, [("Second beat.", 0.0, 2.7)], names=["s2-b/second"]),
    ]

    assert episode_beats(parts) == [
        Beat("s1-a/first", "First beat.", 2.0, 6.7),
        Beat("s2-b/second", "Second beat.", 9.0, 11.7),
    ]


def test_episode_cues_take_another_splitter() -> None:
    parts = [Part(2.0, 5.0, [("first beat", 0.0, 5.0)])]

    def shout(text: str, start: float, end: float) -> list[Cue]:
        return [Cue(start, end, text.upper())]

    assert episode_cues(parts, split=shout) == [Cue(2.0, 7.0, "FIRST BEAT")]


SCRIPT = """---
format: script/v1
episode: E01-a
segment: s1-x
voice: default
anchors:
  hello: []
  bye: []
---

[[hello]] Hello there.

[[bye]] Goodbye now.
"""


def test_read_parts_reads_cards_timing_and_scripts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    segments = [
        {"id": "s1-x", "title": "X", "target_seconds": 30},
        {"id": "s2-y", "title": "Y", "target_seconds": 30},
    ]
    outline = {"format": "outline/v0", "series": "demo", "episode": "E01-a"}
    outline |= {"title": "A", "core_question": "Why?", "audience": "Adults."}
    (tmp_path / "outline.yaml").write_text(
        yaml.safe_dump({**outline, "segments": segments})
    )
    segment = tmp_path / "s1-x"
    segment.mkdir()
    (segment / "script.md").write_text(SCRIPT)
    beats = [
        {"cue": "hello", "start": 0.0, "end": 2.3},
        {"cue": "bye", "start": 2.3, "end": 4.6},
    ]
    (segment / "timing.json").write_text(json.dumps({"voice": None, "beats": beats}))
    (segment / "segment.mp4").write_bytes(b"")
    (tmp_path / "titles").mkdir()
    (tmp_path / "titles" / "s1-x.mp4").write_bytes(b"")
    lengths = {"segment.mp4": 4.6, "s1-x.mp4": 2.0}
    monkeypatch.setattr(stitch, "seconds_of", lambda path: lengths[path.name])

    [part] = read_parts(tmp_path)

    assert (part.card, part.segment) == (2.0, 4.6)
    assert part.names == ["s1-x/hello", "s1-x/bye"]
    assert [text for text, _, _ in part.beats] == ["Hello there.", "Goodbye now."]
    times = [time for _, start, end in part.beats for time in (start, end)]
    assert times == pytest.approx([0.0, 2.0, 2.3, 4.3])

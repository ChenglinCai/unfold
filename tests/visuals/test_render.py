"""Renders turn scenes into videos, and each video gets a contact sheet."""

import json
import shutil
from pathlib import Path

import av
import numpy as np
import pytest
import yaml
from PIL import Image

from unfold.cli import main
from unfold.visuals.render import beat_ends, contact_sheet, sample_times, segments
from unfold.visuals.scene import durations
from unfold.voice import Clip

SCRIPT = """---
format: script/v1
episode: E01-growth
segment: s1-interest
voice: default
anchors:
  title: []
  chart: []
---

[[title]] Money grows when it earns interest.

[[chart]] One hundred dollars becomes one hundred five after a year.
"""
SCENE: dict[str, object] = {
    "format": "scene/v0",
    "episode": "E01-growth",
    "segment": "s1-interest",
    "entries": [
        {
            "cue": "title",
            "region": "top",
            "visual": {"component": "text-card", "title": "Growth"},
        },
        {
            "cue": "chart",
            "region": "plot",
            "visual": {
                "component": "bar-chart",
                "labels": ["Now", "Later"],
                "values": [100, 105],
            },
        },
    ],
}


def segment_folder(root: Path, scene: dict[str, object] | None = None) -> Path:
    folder = root / "E01-growth" / "s1-interest"
    folder.mkdir(parents=True)
    (folder / "script.md").write_text(SCRIPT)
    (folder / "scene.yaml").write_text(yaml.safe_dump(scene or SCENE))
    return folder


def test_segments_are_the_folders_with_scenes(tmp_path: Path) -> None:
    folder = segment_folder(tmp_path)
    (tmp_path / "E01-growth" / "s2-empty").mkdir()

    assert segments(tmp_path) == [folder]


def test_each_beat_ends_after_its_narration() -> None:
    assert beat_ends([2.0, 4.0]) == [2.0, 6.0]


def test_a_voiced_beat_lasts_its_clip_and_a_pause(tmp_path: Path) -> None:
    from unfold.script import parse_script

    script = parse_script(SCRIPT)
    clips = [Clip(tmp_path / "a.wav", 2.5), Clip(tmp_path / "b.wav", 3.0)]

    assert durations(script, clips) == [2.8, 3.3]
    assert durations(script, None) == [2.18, 3.64]


def test_a_contact_sheet_holds_one_frame_per_time(tmp_path: Path) -> None:
    video = tmp_path / "tiny.mp4"
    with av.open(str(video), "w") as container:
        stream = container.add_stream("libx264", rate=10)
        stream.width, stream.height, stream.pix_fmt = 160, 90, "yuv420p"
        for index in range(20):
            shade = 0 if index < 10 else 255
            pixels = np.full((90, 160, 3), shade, dtype=np.uint8)
            frame = av.VideoFrame.from_ndarray(pixels, format="rgb24")
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)

    sheet = contact_sheet(video, [0.5, 1.5], ["dark", "light"], tmp_path / "sheet.png")

    image = Image.open(sheet).convert("L")
    dark, light = image.getpixel((240, 150)), image.getpixel((720, 150))
    assert image.size[0] == 2 * 480
    assert isinstance(dark, int) and dark < 60
    assert isinstance(light, int) and light > 200


def test_a_layout_failure_stops_the_render(tmp_path: Path) -> None:
    long_title = {"component": "text-card", "title": "Long " * 60}
    entries = SCENE["entries"]
    assert isinstance(entries, list)
    title = {"cue": "title", "region": "top", "visual": long_title}
    folder = segment_folder(tmp_path, {**SCENE, "entries": [title, entries[1]]})
    (tmp_path / "plan.yaml").write_text("format: series-plan/v0\n")

    assert main(["render", str(tmp_path)]) == 1
    assert not (folder / "segment.mp4").exists()


@pytest.mark.slow
def test_a_segment_renders_with_a_contact_sheet_and_then_reuses_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder = segment_folder(tmp_path)
    (tmp_path / "plan.yaml").write_text("format: series-plan/v0\n")

    assert main(["render", str(tmp_path)]) == 0
    assert (folder / "segment.mp4").stat().st_size > 0
    assert Image.open(folder / "contact-sheet.png").size[0] == 2 * 480

    assert main(["render", str(tmp_path)]) == 0
    assert "reused" in capsys.readouterr().out.splitlines()[-2]


def test_contact_sheets_sample_the_middle_of_each_hold() -> None:
    assert sample_times([2.0, 4.0]) == [1.4, 4.4]


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("say") is None, reason="the voice needs macOS say")
def test_a_voiced_segment_carries_its_narration(tmp_path: Path) -> None:
    folder = segment_folder(tmp_path)
    (tmp_path / "plan.yaml").write_text("format: series-plan/v0\n")

    assert main(["render", str(tmp_path)]) == 0

    timing = json.loads((folder / "timing.json").read_text())
    with av.open(str(folder / "segment.mp4")) as container:
        assert container.streams.audio
        seconds = float(container.duration or 0) / av.time_base
    assert timing["voice"].startswith("say:")
    assert abs(seconds - timing["beats"][-1]["end"]) < 0.5


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("say") is None, reason="the voice needs macOS say")
@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="stitching needs ffmpeg")
def test_render_stitches_the_episode_and_checks_the_audio(tmp_path: Path) -> None:
    import importlib.util

    folder = segment_folder(tmp_path)
    outline = {
        "format": "outline/v0",
        "series": "growth",
        "episode": "E01-growth",
        "title": "Growth",
        "core_question": "Why does money grow?",
        "audience": "Adults.",
        "segments": [{"id": "s1-interest", "title": "Interest", "target_seconds": 30}],
    }
    (folder.parent / "outline.yaml").write_text(yaml.safe_dump(outline))
    check = importlib.util.find_spec("faster_whisper") is not None

    assert main(["render", str(tmp_path), *(["--check-audio"] if check else [])]) == 0

    assert (folder / "segment.srt").read_text().startswith("1\n00:00:00,000")
    assert (folder.parent / "episode.mp4").stat().st_size > 0
    assert "Money grows" in (folder.parent / "episode.srt").read_text()
    with Image.open(folder.parent / "episode-sheet.png") as sheet:
        assert sheet.width > 0 and sheet.height > 0


def test_render_adds_a_missing_episode_sheet_without_stitching_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from unfold.episodes import stitch as episodes
    from unfold.visuals import command

    episode = tmp_path / "E01-growth"
    segment = episode / "s1-interest"
    segment.mkdir(parents=True)
    (episode / "outline.yaml").write_text("format: outline/v0\n")
    (episode / "episode.mp4").write_bytes(b"")
    made: list[Path] = []

    def stitch_again(folder: Path, quality: str) -> Path:
        raise AssertionError("an unchanged episode must not stitch again")

    monkeypatch.setattr(episodes, "stitch_episode", stitch_again)
    monkeypatch.setattr(
        episodes, "episode_sheet", lambda folder: made.append(folder) or folder
    )

    command.stitch([segment], [], "low")

    assert made == [episode]

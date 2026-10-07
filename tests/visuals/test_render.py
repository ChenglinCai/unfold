"""Renders turn scenes into videos, and each video gets a contact sheet."""

from pathlib import Path

import av
import numpy as np
import pytest
import yaml
from PIL import Image

from unfold.cli import main
from unfold.visuals.render import beat_ends, contact_sheet, sample_times, segments

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
    assert beat_ends(["Three short words.", " ".join(["word"] * 11)]) == [2.0, 6.0]


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
    assert sample_times(["Three short words.", " ".join(["word"] * 11)]) == [1.4, 4.4]

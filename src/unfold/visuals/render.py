"""Renders: each segment's video, in parallel, and one contact sheet per video.

A contact sheet is one image with a frame from the end of every beat, so a
person can review a whole segment at a glance.
"""

import json
import math
import shutil
from importlib import metadata
from pathlib import Path

from PIL import Image, ImageDraw

from unfold import jobs
from unfold.formats import read_data
from unfold.formats.episode import SceneV0
from unfold.script import load_script
from unfold.visuals import params
from unfold.visuals.scene import beat_seconds

VIDEO = "segment.mp4"
SHEET = "contact-sheet.png"
RECORD = "render.json"
QUALITIES = {"low": "low_quality", "medium": "medium_quality", "high": "high_quality"}
THUMB = 480


def segments(series: Path) -> list[Path]:
    """Every segment folder in a series that holds a scene."""
    return sorted(p.parent for p in series.glob("E*/s*/scene.yaml"))


def beat_ends(texts: list[str]) -> list[float]:
    """The time at which each beat ends, from the start of the segment."""
    ends, clock = [], 0.0
    for text in texts:
        clock += beat_seconds(text)
        ends.append(round(clock, 2))
    return ends


def render_key(folder: Path, quality: str) -> str:
    texts = [
        (folder / name).read_text(encoding="utf-8")
        for name in ("scene.yaml", "script.md")
    ]
    return jobs.key(*texts, params.VERSION, metadata.version("manim"), quality)


def current(folder: Path, quality: str) -> bool:
    record = folder / RECORD
    if not (
        record.is_file() and (folder / VIDEO).is_file() and (folder / SHEET).is_file()
    ):
        return False
    return json.loads(record.read_text(encoding="utf-8")).get("key") == render_key(
        folder, quality
    )


def render_segment(folder: Path, quality: str = "low") -> Path:
    """Render one segment and its contact sheet. Runs in a worker process."""
    from manim import tempconfig

    from unfold.visuals import theme
    from unfold.visuals.scene import SegmentScene

    scene = SceneV0.model_validate(read_data(folder / "scene.yaml"))
    script = load_script(folder / "script.md")
    settings = {
        "quality": QUALITIES[quality],
        "media_dir": str(folder / "media"),
        "background_color": theme.BACKGROUND,
        "output_file": "segment",
        "verbosity": "ERROR",
        "progress_bar": "none",
        "disable_caching": True,
    }
    with tempconfig(settings):
        movie = SegmentScene(scene, script)
        movie.render()
        shutil.copyfile(movie.renderer.file_writer.movie_file_path, folder / VIDEO)
    texts = [beat.text for beat in script.beats]
    times = [max(end - 0.1, 0.0) for end in beat_ends(texts)]
    contact_sheet(folder / VIDEO, times, [b.cue for b in script.beats], folder / SHEET)
    record = {"key": render_key(folder, quality), "quality": quality}
    (folder / RECORD).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return folder / VIDEO


def contact_sheet(
    video: Path, times: list[float], labels: list[str], out: Path, columns: int = 4
) -> Path:
    """Tile the frames at the given times into one image, each with its label."""
    import av

    frames: list[Image.Image] = []
    targets = list(times)
    last: Image.Image | None = None
    with av.open(str(video)) as container:
        for frame in container.decode(video=0):
            image: Image.Image = frame.to_image()
            last = image
            while targets and (frame.time or 0.0) >= targets[0] - 1e-6:
                frames.append(image)
                targets.pop(0)
            if not targets:
                break
    if last is not None:
        frames.extend([last] * len(targets))
    columns = max(1, min(columns, len(frames)))
    width, height = frames[0].size
    thumb_h = round(THUMB * height / width)
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new("RGB", (columns * THUMB, rows * thumb_h), "black")
    draw = ImageDraw.Draw(sheet)
    for index, (frame, label) in enumerate(zip(frames, labels, strict=False)):
        x, y = (index % columns) * THUMB, (index // columns) * thumb_h
        sheet.paste(frame.resize((THUMB, thumb_h)), (x, y))
        draw.text((x + 8, y + 6), label, fill="white")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out

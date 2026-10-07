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
from unfold.visuals.scene import FADE_SECONDS, durations
from unfold.voice import default_voice

VIDEO = "segment.mp4"
SHEET = "contact-sheet.png"
RECORD = "render.json"
TIMING = "timing.json"
QUALITIES = {"low": "low_quality", "medium": "medium_quality", "high": "high_quality"}
THUMB = 480


def segments(series: Path) -> list[Path]:
    """Every segment folder in a series that holds a scene."""
    return sorted(p.parent for p in series.glob("E*/s*/scene.yaml"))


def beat_ends(lengths: list[float]) -> list[float]:
    """The time at which each beat ends, from the start of the segment."""
    ends, clock = [], 0.0
    for seconds in lengths:
        clock += seconds
        ends.append(round(clock, 2))
    return ends


def sample_times(lengths: list[float]) -> list[float]:
    """The middle of each beat's hold, after its fade, safe from frame drift."""
    times, start = [], 0.0
    for seconds in lengths:
        fade = min(FADE_SECONDS, seconds / 2)
        times.append(round(start + fade + (seconds - fade) / 2, 2))
        start += seconds
    return times


def render_key(folder: Path, quality: str) -> str:
    texts = [
        (folder / name).read_text(encoding="utf-8")
        for name in ("scene.yaml", "script.md")
    ]
    voice = default_voice()
    name = voice.name if voice else "silent"
    return jobs.key(*texts, params.VERSION, metadata.version("manim"), quality, name)


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
    voice = default_voice()
    cache = folder.parent.parent / ".voice-cache"
    clips = [voice.speak(b.text, cache) for b in script.beats] if voice else None
    lengths = durations(script, clips)
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
        movie = SegmentScene(scene, script, clips)
        movie.render()
        shutil.copyfile(movie.renderer.file_writer.movie_file_path, folder / VIDEO)
    times = sample_times(lengths)
    ends = beat_ends(lengths)
    beats = [
        {"cue": beat.cue, "start": round(end - length, 2), "end": end}
        for beat, end, length in zip(script.beats, ends, lengths, strict=True)
    ]
    timing = {"voice": voice.name if voice else None, "beats": beats}
    (folder / TIMING).write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")
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

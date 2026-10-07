"""Stitching: a title card before each segment, then one episode video and its subtitles.

ffmpeg's concat filter joins the parts. It re-encodes, so parts whose audio
settings differ still join cleanly.
"""

import json
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

from unfold.episodes.subtitles import Cue, beat_cues, srt_text

TITLE_SECONDS = 2.0
EPISODE = "episode.mp4"
SUBTITLES = "episode.srt"


@dataclass(frozen=True)
class Part:
    """One segment in an episode: its card's length, its length, and its beats."""

    card: float
    segment: float
    beats: list[tuple[str, float, float]]


def seconds_of(video: Path) -> float:
    import av

    with av.open(str(video)) as container:
        return float(container.duration or 0) / av.time_base


def has_audio(video: Path) -> bool:
    import av

    with av.open(str(video)) as container:
        return bool(container.streams.audio)


def concat(videos: list[Path], out: Path) -> Path:
    """Join videos in order. Sound joins too, when every part has sound."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("Stitching needs the ffmpeg program, such as from Homebrew.")
    sound = all(has_audio(video) for video in videos)
    inputs = [arg for video in videos for arg in ("-i", str(video))]
    streams = "".join(
        f"[{i}:v][{i}:a]" if sound else f"[{i}:v]" for i in range(len(videos))
    )
    joined = f"{streams}concat=n={len(videos)}:v=1:a={int(sound)}[v]" + (
        "[a]" if sound else ""
    )
    maps = ["-map", "[v]", *(["-map", "[a]", "-c:a", "aac"] if sound else [])]
    partial = out.with_name(f".{out.stem}.partial{out.suffix}")
    command = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", joined]
    command += [*maps, "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p"]
    subprocess.run([*command, str(partial)], check=True)
    partial.replace(out)
    return out


def episode_cues(parts: list[Part]) -> list[Cue]:
    """Every beat's cues, shifted by the cards and segments that came before."""
    cues: list[Cue] = []
    clock = 0.0
    for part in parts:
        clock += part.card
        for text, start, end in part.beats:
            cues += beat_cues(text, round(clock + start, 3), round(clock + end, 3))
        clock += part.segment
    return cues


def silence(path: Path, seconds: float, rate: int = 22050) -> Path:
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(b"\x00\x00" * int(rate * seconds))
    return path


def title_card(title: str, out: Path, quality: str) -> Path:
    """Render a short card with a segment's title, and a silent sound track."""
    from manim import FadeIn, Scene, Text, tempconfig

    from unfold.visuals import theme
    from unfold.visuals.render import QUALITIES

    out.parent.mkdir(parents=True, exist_ok=True)
    quiet = silence(out.with_suffix(".wav"), TITLE_SECONDS)

    class Card(Scene):
        def construct(self) -> None:
            self.add_sound(str(quiet))
            words = Text(title, font_size=theme.TITLE_SIZE, color=theme.YELLOW)
            if words.width > 12:
                words.scale(12 / words.width)
            self.play(FadeIn(words), run_time=0.6)
            self.wait(TITLE_SECONDS - 0.6)

    settings = {
        "quality": QUALITIES[quality],
        "media_dir": str(out.parent / "media"),
        "background_color": theme.BACKGROUND,
        "output_file": out.stem,
        "verbosity": "ERROR",
        "progress_bar": "none",
        "disable_caching": True,
    }
    with tempconfig(settings):
        card = Card()
        card.render()
        shutil.copyfile(card.renderer.file_writer.movie_file_path, out)
    return out


def stitch_episode(folder: Path, quality: str = "low") -> Path:
    """Join an episode's rendered segments, each after its title card."""
    from unfold.formats import read_data
    from unfold.formats.episode import OutlineV0
    from unfold.script import load_script
    from unfold.visuals.render import TIMING, VIDEO
    from unfold.visuals.scene import PAUSE

    outline = OutlineV0.model_validate(read_data(folder / "outline.yaml"))
    videos: list[Path] = []
    parts: list[Part] = []
    for segment in outline.segments:
        video = folder / segment.id / VIDEO
        if not video.is_file():
            continue
        card = title_card(
            segment.title, folder / "titles" / f"{segment.id}.mp4", quality
        )
        timing = json.loads((folder / segment.id / TIMING).read_text(encoding="utf-8"))
        texts = [
            beat.text for beat in load_script(folder / segment.id / "script.md").beats
        ]
        beats = [
            (text, t["start"], max(t["start"], t["end"] - PAUSE))
            for text, t in zip(texts, timing["beats"], strict=True)
        ]
        parts.append(Part(seconds_of(card), seconds_of(video), beats))
        videos += [card, video]
    if not videos:
        raise ValueError(f"{folder} has no rendered segments")
    concat(videos, folder / EPISODE)
    (folder / SUBTITLES).write_text(srt_text(episode_cues(parts)), encoding="utf-8")
    return folder / EPISODE

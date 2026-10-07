"""A stand-in voice: the macOS `say` command turns text into speech.

M6 replaces it with Kokoro. Until then, it lets a scene time each animation
to the length of its narration. Each clip's file name comes from the voice and
the text, so the same text is never spoken twice.
"""

import hashlib
import shutil
import subprocess
import wave
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from manim import Scene

DEFAULT_VOICE = "Samantha"


@dataclass(frozen=True)
class Clip:
    """A spoken beat: the audio file and its length in seconds."""

    path: Path
    seconds: float


def available() -> bool:
    """Report whether this machine has the `say` command."""
    return shutil.which("say") is not None


def synthesize(text: str, cache_dir: Path, voice: str = DEFAULT_VOICE) -> Clip:
    """Speak text into a WAV file in cache_dir, unless that clip exists already."""
    key = hashlib.sha256(f"say|{voice}|{text}".encode()).hexdigest()[:16]
    path = cache_dir / f"{key}.wav"
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        partial = cache_dir / f"{key}.part.wav"
        subprocess.run(
            ["say", "-v", voice, "-o", str(partial), "--data-format=LEI16@22050"],
            input=text,
            text=True,
            check=True,
        )
        partial.replace(path)
    return Clip(path, seconds(path))


def seconds(path: Path) -> float:
    """Return the length of a WAV file in seconds."""
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


@contextmanager
def voiced(scene: Scene, text: str, cache_dir: Path) -> Iterator[Clip]:
    """Play one beat's narration, then keep the scene going until it ends.

    Animations inside the block can use clip.seconds to fit the narration.
    """
    clip = synthesize(text, cache_dir)
    start = scene.renderer.time
    scene.add_sound(str(clip.path))
    yield clip
    remaining = clip.seconds - (scene.renderer.time - start)
    if remaining > 1 / 60:
        scene.wait(remaining)

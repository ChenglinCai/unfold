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


def synthesize(
    text: str, cache_dir: Path, voice: str = DEFAULT_VOICE, rate: int | None = None
) -> Clip:
    """Speak text into a WAV file in cache_dir, unless that clip exists already.

    The rate is in words per minute. None keeps the voice's own rate.
    """
    key = hashlib.sha256(f"say|{voice}|{rate}|{text}".encode()).hexdigest()[:16]
    path = cache_dir / f"{key}.wav"
    if not path.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        partial = cache_dir / f"{key}.part.wav"
        command = ["say", "-v", voice, "-o", str(partial), "--data-format=LEI16@22050"]
        if rate is not None:
            command += ["-r", str(rate)]
        subprocess.run(command, input=text, text=True, check=True)
        partial.replace(path)
    return Clip(path, seconds(path))


def seconds(path: Path) -> float:
    """Return the length of a WAV file in seconds."""
    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


@contextmanager
def voiced(
    scene: Scene,
    text: str,
    cache_dir: Path,
    rate: int | None = None,
    pause: float = 0.0,
) -> Iterator[Clip]:
    """Play one beat's narration, then keep the scene going until it ends.

    Animations inside the block can use clip.seconds to fit the narration.
    The pause adds silence after the narration, like a breath between beats.
    """
    clip = synthesize(text, cache_dir, rate=rate)
    start = scene.renderer.time
    scene.add_sound(str(clip.path))
    yield clip
    remaining = clip.seconds + pause - (scene.renderer.time - start)
    if remaining > 1 / 60:
        scene.wait(remaining)

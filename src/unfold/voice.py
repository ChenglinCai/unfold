"""Voices: each one turns a beat's text into a clip that a scene can time.

Kokoro, in `unfold.kokoro`, is the natural voice. The macOS `say` command is
the fallback. Each clip's file name comes from the voice and the text, so the
same text is never spoken twice. Set UNFOLD_VOICE to choose a voice.
"""

import hashlib
import os
import shutil
import subprocess
import wave
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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


class Voice(Protocol):
    """Anything that turns one beat's text into a clip, such as Kokoro or `say`."""

    @property
    def name(self) -> str: ...

    def speak(
        self, text: str, cache_dir: Path, before: str = "", after: str = ""
    ) -> Clip:
        """Speak one beat. Before and after hold the neighboring beats' text."""
        ...


@dataclass(frozen=True)
class SayVoice:
    """The macOS `say` command. Rate 140 speaks about 165 words a minute."""

    voice: str = DEFAULT_VOICE
    rate: int = 140

    @property
    def name(self) -> str:
        return f"say:{self.voice}@{self.rate}"

    def speak(
        self, text: str, cache_dir: Path, before: str = "", after: str = ""
    ) -> Clip:
        return synthesize(text, cache_dir, self.voice, self.rate)


def speak_beats(voice: Voice, texts: list[str], cache_dir: Path) -> list[Clip]:
    """Speak a segment's beats in order. Each beat hears only its neighbors.

    So an edit to one beat re-speaks at most three beats.
    """
    padded = ["", *texts, ""]
    return [
        voice.speak(padded[i], cache_dir, before=padded[i - 1], after=padded[i + 1])
        for i in range(1, len(padded) - 1)
    ]


SETTING = "UNFOLD_VOICE takes elevenlabs:VOICE@MODEL, kokoro:VOICE@SPEED, say:VOICE@RATE, or none"


def parse_voice(setting: str) -> Voice | None:
    """Read a voice setting, such as elevenlabs:VOICE_ID@eleven_multilingual_v2, or none."""
    from unfold.elevenlabs import ElevenLabsVoice
    from unfold.kokoro import KokoroVoice

    kind, _, rest = setting.strip().partition(":")
    name, _, number = rest.partition("@")
    try:
        if kind == "none" and not rest:
            return None
        if kind == "elevenlabs":
            default = ElevenLabsVoice()
            return ElevenLabsVoice(name or default.voice, number or default.model)
        if kind == "kokoro":
            return KokoroVoice(name or "af_heart", float(number or 1.0))
        if kind == "say":
            return SayVoice(name or DEFAULT_VOICE, int(number or 140))
    except ValueError:
        pass
    raise ValueError(f"{SETTING}, not {setting!r}")


def default_voice() -> Voice | None:
    """The voice to use: UNFOLD_VOICE, else Kokoro, else `say`, else None."""
    from unfold import kokoro

    setting = os.environ.get("UNFOLD_VOICE")
    if setting:
        return parse_voice(setting)
    if kokoro.installed():
        return kokoro.KokoroVoice()
    return SayVoice() if available() else None

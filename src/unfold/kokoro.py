"""The Kokoro voice: an open voice model that sounds like a person explaining.

Misaki turns text into phonemes, so words sound right in context, and Kokoro
speaks them. Each clip then loses its edge silence and reaches one loudness, so
beats and voices sound even. The model files download once, and a pinned
SHA-256 guards each one. Install the voice extra with: uv sync --extra voice
"""

import hashlib
import importlib.util
import os
import shutil
import urllib.request
import wave
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

from unfold.voice import Clip, seconds

MODEL_VERSION = "1.0"
_RELEASE = (
    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
)
FILES = {
    "kokoro-v1.0.onnx": (
        f"{_RELEASE}/kokoro-v1.0.onnx",
        "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
    ),
    "voices-v1.0.bin": (
        f"{_RELEASE}/voices-v1.0.bin",
        "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    ),
}
RATE = 24_000
# Speech sits near -20 dBFS in broadcast practice, with peaks kept below -1.
TARGET_DBFS = -20.0
PEAK_DBFS = -1.0
# Each clip keeps this much silence at each end, so the pause between beats is even.
EDGE = 0.05
SILENT = 0.01

Download = Callable[[str, Path], None]


def installed() -> bool:
    """Whether the voice extra is installed."""
    return all(importlib.util.find_spec(m) for m in ("kokoro_onnx", "misaki", "spacy"))


def trim(samples: np.ndarray, rate: int = RATE) -> np.ndarray:
    """Cut the silence at each end, keeping EDGE seconds of it."""
    loud = np.flatnonzero(np.abs(samples) > SILENT)
    if loud.size == 0:
        return samples[:0]
    keep = int(EDGE * rate)
    return samples[max(loud[0] - keep, 0) : loud[-1] + 1 + keep]


def level(samples: np.ndarray) -> np.ndarray:
    """Scale to the target loudness, then lower the whole clip if a peak runs over."""
    rms = (
        float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))
        if samples.size
        else 0
    )
    if rms == 0:
        return samples
    scaled = samples * (10 ** (TARGET_DBFS / 20) / rms)
    peak, ceiling = float(np.abs(scaled).max()), 10 ** (PEAK_DBFS / 20)
    return (scaled * min(1.0, ceiling / peak)).astype(np.float32)


def cache_folder() -> Path:
    """Where the model files live: UNFOLD_CACHE, else the user's cache folder."""
    root = os.environ.get("UNFOLD_CACHE") or os.environ.get("XDG_CACHE_HOME")
    base = Path(root) if root else Path.home() / ".cache"
    return base / "unfold" / "kokoro"


def _download(url: str, target: Path) -> None:
    with urllib.request.urlopen(url, timeout=60) as response, target.open("wb") as out:
        shutil.copyfileobj(response, out)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(
    name: str,
    folder: Path,
    files: dict[str, tuple[str, str]] = FILES,
    download: Download = _download,
) -> Path:
    """Return a model file, downloading it once. A file must match its pinned hash."""
    url, expected = files[name]
    path = folder / name
    if path.is_file():
        return path
    folder.mkdir(parents=True, exist_ok=True)
    partial = folder / f"{name}.part"
    print(f"unfold: downloading {name} for the voice, once")
    try:
        download(url, partial)
        if _sha256(partial) != expected:
            raise ValueError(
                f"{name} does not match its pinned SHA-256, so it was deleted"
            )
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)
    return path


@cache
def _engine() -> Any:
    # The voice extra provides these, so CI type-checks without it.
    from kokoro_onnx import Kokoro  # pyright: ignore[reportMissingImports]

    folder = cache_folder()
    return Kokoro(
        str(fetch("kokoro-v1.0.onnx", folder)), str(fetch("voices-v1.0.bin", folder))
    )


@cache
def _g2p(british: bool) -> Callable[[str], str]:
    from misaki import en, espeak  # pyright: ignore[reportMissingImports]

    g2p = en.G2P(
        trf=False, british=british, fallback=espeak.EspeakFallback(british=british)
    )
    return lambda text: g2p(text)[0]


def write_wav(path: Path, samples: np.ndarray) -> None:
    """Write mono 16-bit audio at 24 kHz."""
    pcm = np.round(np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(RATE)
        audio.writeframes(pcm.tobytes())


@dataclass(frozen=True)
class KokoroVoice:
    """A Kokoro voice, such as af_heart. Voices that start with b speak British English."""

    voice: str = "af_heart"
    speed: float = 1.0

    @property
    def name(self) -> str:
        return f"kokoro-{MODEL_VERSION}:{self.voice}@{self.speed:g}"

    def speak(
        self, text: str, cache_dir: Path, before: str = "", after: str = ""
    ) -> Clip:
        """Speak one beat. Kokoro ignores the neighboring beats."""
        key = hashlib.sha256(f"{self.name}|{text}".encode()).hexdigest()[:16]
        path = cache_dir / f"{key}.wav"
        if not path.exists():
            engine = _engine()
            voices = sorted(engine.voices)
            if self.voice not in voices:
                raise ValueError(
                    f"Kokoro has no voice {self.voice}. Choose from: {', '.join(voices)}"
                )
            phonemes = _g2p(self.voice.startswith("b"))(text)
            samples, rate = engine.create(
                phonemes, voice=self.voice, speed=self.speed, is_phonemes=True
            )
            if rate != RATE:
                raise ValueError(f"Kokoro spoke at {rate} Hz, not {RATE}")
            cache_dir.mkdir(parents=True, exist_ok=True)
            partial = cache_dir / f"{key}.part.wav"
            write_wav(partial, level(trim(np.asarray(samples, dtype=np.float32))))
            partial.replace(path)
        return Clip(path, seconds(path))

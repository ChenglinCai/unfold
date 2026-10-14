"""The Kokoro voice, with fakes for the model, so no test downloads anything."""

import hashlib
import math
import wave
from pathlib import Path

import numpy as np
import pytest

from unfold import kokoro, voice
from unfold.kokoro import EDGE, PEAK_DBFS, RATE, TARGET_DBFS, KokoroVoice, fetch

QUIET = np.zeros(RATE, dtype=np.float32)


def tone(seconds: float, loudness: float) -> np.ndarray:
    times = np.arange(int(seconds * RATE)) / RATE
    return (loudness * np.sin(2 * math.pi * 220 * times)).astype(np.float32)


def dbfs(samples: np.ndarray) -> float:
    return 20 * math.log10(float(np.sqrt(np.mean(samples**2))))


def test_trim_keeps_a_short_edge_of_silence() -> None:
    trimmed = kokoro.trim(np.concatenate([QUIET, tone(1, 0.3), QUIET]))
    assert math.isclose(len(trimmed) / RATE, 1 + 2 * EDGE, abs_tol=0.01)


@pytest.mark.parametrize("loudness", [0.02, 0.1, 0.3, 0.99])
def test_level_reaches_one_loudness_without_clipping(loudness: float) -> None:
    leveled = kokoro.level(tone(1, loudness))
    assert abs(dbfs(leveled) - TARGET_DBFS) < 1
    assert np.abs(leveled).max() <= 10 ** (PEAK_DBFS / 20) + 1e-6


def test_level_caps_a_loud_peak() -> None:
    spiky = tone(1, 0.05)
    spiky[100] = 1.0
    assert np.abs(kokoro.level(spiky)).max() <= 10 ** (PEAK_DBFS / 20) + 1e-6


def test_level_leaves_silence_silent() -> None:
    assert not kokoro.level(QUIET).any()


def test_fetch_keeps_a_file_whose_hash_matches(tmp_path: Path) -> None:
    body = b"model weights"
    files = {
        "m.onnx": ("https://example.test/m.onnx", hashlib.sha256(body).hexdigest())
    }
    calls: list[str] = []

    def download(url: str, target: Path) -> None:
        calls.append(url)
        target.write_bytes(body)

    path = fetch("m.onnx", tmp_path, files, download)
    assert path.read_bytes() == body
    assert fetch("m.onnx", tmp_path, files, download) == path
    assert calls == ["https://example.test/m.onnx"]


def test_fetch_deletes_a_file_whose_hash_differs(tmp_path: Path) -> None:
    files = {"m.onnx": ("https://example.test/m.onnx", "0" * 64)}

    def download(url: str, target: Path) -> None:
        target.write_bytes(b"something else")

    with pytest.raises(ValueError, match="SHA-256"):
        fetch("m.onnx", tmp_path, files, download)
    assert list(tmp_path.iterdir()) == []


class FakeEngine:
    voices = ("af_heart", "bf_emma")

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, float]] = []

    def create(
        self, phonemes: str, voice: str, speed: float, is_phonemes: bool
    ) -> tuple[np.ndarray, int]:
        assert is_phonemes
        self.calls.append((phonemes, voice, speed))
        return np.concatenate([QUIET[:2400], tone(2, 0.4), QUIET[:2400]]), RATE


@pytest.fixture
def engine(monkeypatch: pytest.MonkeyPatch) -> FakeEngine:
    fake = FakeEngine()
    monkeypatch.setattr(kokoro, "_engine", lambda: fake)
    monkeypatch.setattr(kokoro, "_g2p", lambda british: lambda t: f"{british}:{t}")
    return fake


def test_speak_writes_a_leveled_24_khz_clip_once(
    engine: FakeEngine, tmp_path: Path
) -> None:
    speaker = KokoroVoice("af_heart", 1.1)
    clip = speaker.speak("Supply meets demand.", tmp_path)
    again = speaker.speak("Supply meets demand.", tmp_path)

    assert again == clip
    assert engine.calls == [("False:Supply meets demand.", "af_heart", 1.1)]
    with wave.open(str(clip.path), "rb") as audio:
        assert (audio.getframerate(), audio.getsampwidth()) == (RATE, 2)
    assert math.isclose(clip.seconds, 2 + 2 * EDGE, abs_tol=0.01)


def test_british_voices_use_british_g2p(engine: FakeEngine, tmp_path: Path) -> None:
    KokoroVoice("bf_emma").speak("Colour", tmp_path)
    assert engine.calls[0][0] == "True:Colour"


def test_an_unknown_voice_lists_the_voices(engine: FakeEngine, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="af_heart, bf_emma"):
        KokoroVoice("zz_nobody").speak("Hello", tmp_path)


def test_the_name_changes_with_the_model_voice_and_speed() -> None:
    names = {
        KokoroVoice().name,
        KokoroVoice("am_michael").name,
        KokoroVoice(speed=0.9).name,
    }
    assert len(names) == 3
    assert KokoroVoice().name == "kokoro-1.0:af_heart@1"


@pytest.mark.parametrize(
    ("setting", "name"),
    [
        ("kokoro:am_michael@0.95", "kokoro-1.0:am_michael@0.95"),
        ("kokoro:bf_emma", "kokoro-1.0:bf_emma@1"),
        ("say:Samantha@150", "say:Samantha@150"),
        ("say", "say:Samantha@140"),
    ],
)
def test_the_voice_setting_picks_a_voice(
    monkeypatch: pytest.MonkeyPatch, setting: str, name: str
) -> None:
    monkeypatch.setenv("UNFOLD_VOICE", setting)
    chosen = voice.default_voice()
    assert chosen is not None and chosen.name == name


def test_the_setting_none_renders_silent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNFOLD_VOICE", "none")
    assert voice.default_voice() is None


def test_a_bad_setting_says_what_it_accepts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNFOLD_VOICE", "robot")
    with pytest.raises(ValueError, match="kokoro:VOICE@SPEED"):
        voice.default_voice()


def test_kokoro_comes_before_say(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UNFOLD_VOICE", raising=False)
    monkeypatch.setattr(kokoro, "installed", lambda: True)
    chosen = voice.default_voice()
    assert chosen is not None and chosen.name == KokoroVoice().name

    monkeypatch.setattr(kokoro, "installed", lambda: False)
    monkeypatch.setattr(voice, "available", lambda: True)
    chosen = voice.default_voice()
    assert chosen is not None and chosen.name.startswith("say:")

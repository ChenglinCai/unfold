"""The ElevenLabs voice, with a fake transport, so no test reaches ElevenLabs."""

import json
import math
import wave
from pathlib import Path

import numpy as np
import pytest

from unfold import elevenlabs, voice
from unfold.elevenlabs import ElevenLabsVoice, Request
from unfold.kokoro import RATE, TARGET_DBFS


def speech(seconds: float = 1.5) -> bytes:
    times = np.arange(int(seconds * RATE)) / RATE
    wave_ = 0.2 * np.sin(2 * math.pi * 180 * times)
    return (np.round(wave_ * 32767)).astype("<i2").tobytes()


class FakeServer:
    def __init__(self, body: bytes | None = None, error: str = "") -> None:
        self.requests: list[Request] = []
        self.body = speech() if body is None else body
        self.error = error

    def __call__(self, request: Request) -> bytes:
        self.requests.append(request)
        if self.error:
            raise elevenlabs.ElevenLabsError(self.error)
        return self.body


@pytest.fixture
def server(monkeypatch: pytest.MonkeyPatch) -> FakeServer:
    fake = FakeServer()
    monkeypatch.setattr(elevenlabs, "send", fake)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk-test-secret")
    return fake


def test_a_beat_becomes_one_request_with_its_neighbors(
    server: FakeServer, tmp_path: Path
) -> None:
    speaker = ElevenLabsVoice("voice123", "eleven_multilingual_v2")
    clip = speaker.speak("Demand slopes down.", tmp_path, before="Look.", after="Now.")

    (request,) = server.requests
    assert request.url == (
        "https://api.elevenlabs.io/v1/text-to-speech/voice123?output_format=pcm_24000"
    )
    assert request.headers["xi-api-key"] == "sk-test-secret"
    body = json.loads(request.body)
    assert body["text"] == "Demand slopes down."
    assert body["model_id"] == "eleven_multilingual_v2"
    assert (body["previous_text"], body["next_text"]) == ("Look.", "Now.")
    assert body["voice_settings"]["stability"] == 0.5

    with wave.open(str(clip.path), "rb") as audio:
        assert (audio.getframerate(), audio.getsampwidth()) == (RATE, 2)
        samples = np.frombuffer(audio.readframes(audio.getnframes()), "<i2") / 32767
    assert abs(20 * math.log10(np.sqrt(np.mean(samples**2))) - TARGET_DBFS) < 1


def test_an_unchanged_beat_sends_nothing(server: FakeServer, tmp_path: Path) -> None:
    speaker = ElevenLabsVoice()
    first = speaker.speak("Same words.", tmp_path, before="A.", after="B.")
    assert speaker.speak("Same words.", tmp_path, before="A.", after="B.") == first
    speaker.speak("Same words.", tmp_path, before="Other.", after="B.")
    assert len(server.requests) == 2


def test_a_refused_request_stops_without_showing_the_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(elevenlabs, "send", FakeServer(error="quota_exceeded"))
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk-test-secret")
    with pytest.raises(elevenlabs.ElevenLabsError) as error:
        ElevenLabsVoice().speak("Hello.", tmp_path)
    assert "quota_exceeded" in str(error.value)
    assert "sk-test-secret" not in str(error.value)
    assert list(tmp_path.glob("*.wav")) == []


def test_a_missing_key_names_the_variable(
    monkeypatch: pytest.MonkeyPatch, server: FakeServer, tmp_path: Path
) -> None:
    monkeypatch.delenv("ELEVENLABS_API_KEY")
    with pytest.raises(elevenlabs.ElevenLabsError, match="ELEVENLABS_API_KEY"):
        ElevenLabsVoice().speak("Hello.", tmp_path)
    assert server.requests == []


@pytest.mark.parametrize(
    ("setting", "name"),
    [
        ("elevenlabs", "elevenlabs:JBFqnCBsd6RMkjVDRZzb@eleven_multilingual_v2"),
        ("elevenlabs:abc", "elevenlabs:abc@eleven_multilingual_v2"),
        ("elevenlabs:abc@eleven_v3", "elevenlabs:abc@eleven_v3"),
    ],
)
def test_the_setting_chooses_elevenlabs(
    monkeypatch: pytest.MonkeyPatch, setting: str, name: str
) -> None:
    monkeypatch.setenv("UNFOLD_VOICE", setting)
    chosen = voice.default_voice()
    assert chosen is not None and chosen.name == name


def test_a_key_alone_keeps_the_free_voice(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("UNFOLD_VOICE")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk-test-secret")
    chosen = voice.default_voice()
    assert chosen is None or not chosen.name.startswith("elevenlabs")


def test_tests_cannot_reach_elevenlabs(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="ElevenLabs"):
        elevenlabs.send(Request("https://api.elevenlabs.io/", {}, b""))


def test_each_beat_hears_only_its_neighbors(tmp_path: Path) -> None:
    heard: list[tuple[str, str, str]] = []

    class Recorder:
        name = "recorder"

        def speak(
            self, text: str, cache_dir: Path, before: str = "", after: str = ""
        ) -> voice.Clip:
            heard.append((before, text, after))
            return voice.Clip(cache_dir / f"{text}.wav", 1.0)

    voice.speak_beats(Recorder(), ["One.", "Two.", "Three."], tmp_path)
    assert heard == [
        ("", "One.", "Two."),
        ("One.", "Two.", "Three."),
        ("Two.", "Three.", ""),
    ]

"""The ElevenLabs voice: a paid voice service, on each user's own API key.

Each beat is one request. The request carries the narration before and after
the beat, so ElevenLabs keeps the intonation flowing between beats. Clips get
the same trimming and leveling as Kokoro's, and a clip is never requested twice.
ElevenLabs runs only when UNFOLD_VOICE names it, because each request costs
money and sends narration to ElevenLabs.
"""

import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from unfold.kokoro import RATE, level, trim, write_wav
from unfold.voice import Clip, seconds

API = "https://api.elevenlabs.io/v1/text-to-speech"
KEY = "ELEVENLABS_API_KEY"
# George, a warm narrator from ElevenLabs' default voices.
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_MODEL = "eleven_multilingual_v2"
# ElevenLabs' defaults. Style above 0 adds drama, which can unsteady long narration.
SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
}


class ElevenLabsError(RuntimeError):
    """ElevenLabs refused a request, or no key is set. Messages never hold the key."""


@dataclass(frozen=True)
class Request:
    url: str
    headers: dict[str, str]
    body: bytes


def send(request: Request) -> bytes:
    """Send one request, and return raw 16-bit audio at 24 kHz."""
    message = urllib.request.Request(
        request.url, data=request.body, headers=request.headers, method="POST"
    )
    try:
        with urllib.request.urlopen(message, timeout=120) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        raise ElevenLabsError(f"ElevenLabs answered {error.code}: {detail}") from None
    except urllib.error.URLError as error:
        raise ElevenLabsError(f"could not reach ElevenLabs: {error.reason}") from None


@dataclass(frozen=True)
class ElevenLabsVoice:
    """An ElevenLabs voice id and model, such as George on eleven_multilingual_v2."""

    voice: str = DEFAULT_VOICE
    model: str = DEFAULT_MODEL

    @property
    def name(self) -> str:
        return f"elevenlabs:{self.voice}@{self.model}"

    def speak(
        self, text: str, cache_dir: Path, before: str = "", after: str = ""
    ) -> Clip:
        settings = json.dumps(SETTINGS, sort_keys=True)
        source = f"{self.name}|{settings}|{before}|{text}|{after}"
        key = hashlib.sha256(source.encode()).hexdigest()[:16]
        path = cache_dir / f"{key}.wav"
        if not path.exists():
            pcm = send(self._request(text, before, after))
            samples = np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768
            cache_dir.mkdir(parents=True, exist_ok=True)
            partial = cache_dir / f"{key}.part.wav"
            write_wav(partial, level(trim(samples)))
            partial.replace(path)
        return Clip(path, seconds(path))

    def _request(self, text: str, before: str, after: str) -> Request:
        api_key = os.environ.get(KEY)
        if not api_key:
            raise ElevenLabsError(f"set {KEY} to your ElevenLabs API key")
        body = {
            "text": text,
            "model_id": self.model,
            "voice_settings": SETTINGS,
            "previous_text": before,
            "next_text": after,
        }
        return Request(
            f"{API}/{self.voice}?output_format=pcm_{RATE}",
            {"xi-api-key": api_key, "Content-Type": "application/json"},
            json.dumps(body).encode(),
        )

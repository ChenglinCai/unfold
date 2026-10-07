"""Recordings: faster-whisper transcribes speech into timestamped segments.

It needs the audio extra: `uv sync --extra audio`. The first run downloads the
English base model, about 145 MB, from Hugging Face. Later runs work offline.
"""

import math
import statistics
from pathlib import Path

import av
import numpy as np

from unfold.sources import Anchor, Meta, SourceDocument, build

MODEL = "base.en"
LOW_CONFIDENCE = 0.5
SAMPLE_RATE = 16_000


def decode(path: Path) -> np.ndarray:
    """Decode audio to 16 kHz mono samples between -1 and 1.

    faster-whisper 1.2.1 has its own decoder, but it passes an option that
    PyAV 19 removed. Decoding here keeps the two libraries apart.
    """
    resampler = av.AudioResampler(format="s16", layout="mono", rate=SAMPLE_RATE)
    chunks: list[np.ndarray] = []
    with av.open(str(path)) as container:
        for frame in container.decode(audio=0):
            chunks += [
                out.to_ndarray().reshape(-1) for out in resampler.resample(frame)
            ]
        chunks += [out.to_ndarray().reshape(-1) for out in resampler.resample(None)]
    samples = np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.int16)
    return samples.astype(np.float32) / 32768.0


def read(path: Path, meta: Meta, model: str = MODEL) -> SourceDocument:
    try:  # The audio extra is optional, so CI type-checks without it.
        from faster_whisper import WhisperModel  # pyright: ignore[reportMissingImports]
    except ImportError as error:
        raise RuntimeError(
            "Recordings need the audio extra: uv sync --extra audio"
        ) from error
    whisper = WhisperModel(model, device="cpu", compute_type="int8")
    # The voice filter skips silences. Without it, speech after a long pause joins
    # the segment before it, and takes that segment's start time.
    segments, info = whisper.transcribe(
        decode(path), beam_size=5, language="en", vad_filter=True
    )
    anchors: list[Anchor] = []
    confidences: list[float] = []
    used: set[str] = set()
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        second = int(segment.start)
        anchor_id, extra = f"t-{second:04d}", 2
        while anchor_id in used:
            anchor_id, extra = f"t-{second:04d}-{extra}", extra + 1
        used.add(anchor_id)
        minutes, seconds = divmod(second, 60)
        anchors.append(Anchor(anchor_id, "timestamp", f"{minutes}:{seconds:02d}", text))
        confidences.append(math.exp(segment.avg_logprob))
    words = sum(len(a.text.split()) for a in anchors)
    mean = statistics.fmean(confidences) if confidences else 0.0
    profile = {
        "format": path.suffix.lstrip(".").lower(),
        "size": {"minutes": round(info.duration / 60, 2), "words": words},
        "quality": {"speech_confidence": round(mean, 2), "low": mean < LOW_CONFIDENCE},
    }
    return build(meta, anchors, profile)

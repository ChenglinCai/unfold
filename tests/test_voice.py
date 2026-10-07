"""The stand-in voice turns text into a WAV file and reports its length."""

from pathlib import Path

import pytest

from unfold import voice

needs_say = pytest.mark.skipif(not voice.available(), reason="needs macOS say")


@needs_say
def test_speaks_text_into_a_clip_with_its_length(tmp_path: Path) -> None:
    clip = voice.synthesize("Points that are close tend to share a label.", tmp_path)

    assert clip.path.exists()
    assert clip.path.suffix == ".wav"
    assert 1.0 < clip.seconds < 8.0


@needs_say
def test_reuses_the_saved_clip_for_the_same_text(tmp_path: Path) -> None:
    first = voice.synthesize("Hello there.", tmp_path)
    saved = first.path.stat().st_mtime_ns

    second = voice.synthesize("Hello there.", tmp_path)

    assert second.path == first.path
    assert second.path.stat().st_mtime_ns == saved


@needs_say
def test_different_text_gets_a_different_clip(tmp_path: Path) -> None:
    first = voice.synthesize("Hello there.", tmp_path)
    second = voice.synthesize("Goodbye now.", tmp_path)

    assert first.path != second.path


def test_reports_whether_the_voice_is_available() -> None:
    assert isinstance(voice.available(), bool)

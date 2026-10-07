"""Recordings become timestamped segments. Needs the audio extra and macOS say."""

import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

from unfold.sources import Meta

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        importlib.util.find_spec("faster_whisper") is None or not shutil.which("say"),
        reason="needs the audio extra and macOS say",
    ),
]


def test_transcribes_speech_into_timestamp_anchors(tmp_path: Path) -> None:
    from unfold.sources.recording import read

    path = tmp_path / "talk.aiff"
    subprocess.run(
        ["say", "-o", str(path), "Money changes hands many times each year."],
        check=True,
    )

    doc = read(
        path, Meta(id="talk", title="Talk", family="recording", origin="talk.aiff")
    )

    assert doc.anchors[0].id == "t-0000"
    assert doc.anchors[0].kind == "timestamp"
    text = " ".join(a.text for a in doc.anchors).lower()
    assert "money" in text
    assert "hands" in text
    size = doc.profile["size"]
    assert isinstance(size, dict)
    assert size["minutes"] < 1

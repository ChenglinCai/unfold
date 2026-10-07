"""Scans become text through Apple's Vision framework, on macOS only."""

import platform
import shutil
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from unfold.sources import Meta
from unfold.sources.scan import read

FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(
        platform.system() != "Darwin" or not shutil.which("swift") or not FONT.exists(),
        reason="needs macOS, Swift, and Arial",
    ),
]


def test_reads_printed_text_with_its_confidence(tmp_path: Path) -> None:
    image = Image.new("RGB", (1400, 300), "white")
    draw = ImageDraw.Draw(image)
    draw.text(
        (40, 60),
        "The derivative measures change.",
        fill="black",
        font=ImageFont.truetype(str(FONT), 64),
    )
    path = tmp_path / "page.png"
    image.save(path)

    doc = read(
        path, Meta(id="scan", title="A page", family="slides", origin="page.png")
    )

    [anchor] = doc.anchors
    assert (anchor.id, anchor.kind) == ("scan-1", "scan")
    assert "derivative measures change" in anchor.text.lower()
    quality = doc.profile["quality"]
    assert isinstance(quality, dict)
    assert quality["confidence"] > 0.5
    assert quality["low"] is False

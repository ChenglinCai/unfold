"""Scans: Apple's Vision framework reads printed and handwritten text, on macOS.

`vision.swift` does the reading. It only reads the image, and it writes nothing.
"""

import json
import platform
import shutil
import statistics
import subprocess
from pathlib import Path

from unfold.sources import Anchor, Meta, SourceDocument, build

VISION = Path(__file__).with_name("vision.swift")
IMAGES = {".png", ".jpg", ".jpeg", ".heic", ".tif", ".tiff"}
LOW_CONFIDENCE = 0.5


def recognize(image: Path) -> list[dict[str, object]]:
    """Return the lines of text in an image, top to bottom, with confidences."""
    if platform.system() != "Darwin" or not shutil.which("swift"):
        raise RuntimeError(
            "Scans need macOS with Swift, because they use Apple's Vision."
        )
    result = subprocess.run(
        ["swift", str(VISION), str(image)],
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Vision could not read {image.name}: {result.stderr.strip()[:300]}"
        )
    return json.loads(result.stdout)


def read(path: Path, meta: Meta) -> SourceDocument:
    """Read one image, or every image in a folder, one anchor each."""
    if path.is_dir():
        images = sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGES)
    else:
        images = [path]
    anchors: list[Anchor] = []
    confidences: list[float] = []
    for number, image in enumerate(images, start=1):
        lines = recognize(image)
        confidences += [float(str(line["confidence"])) for line in lines]
        text = "\n".join(str(line["text"]) for line in lines)
        anchors.append(Anchor(f"scan-{number}", "scan", f"Scan {number}", text))
    words = sum(len(a.text.split()) for a in anchors)
    mean = statistics.fmean(confidences) if confidences else 0.0
    profile = {
        "format": images[0].suffix.lstrip(".").lower() if images else "image",
        "size": {"images": len(images), "words": words},
        "quality": {"confidence": round(mean, 2), "low": mean < LOW_CONFIDENCE},
    }
    return build(meta, anchors, profile)

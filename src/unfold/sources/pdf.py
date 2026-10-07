"""PDFs: textbooks and papers get one anchor per page, and decks one per slide."""

import re
from pathlib import Path

import pypdfium2 as pdfium

from unfold.sources import Anchor, Meta, SourceDocument, build
from unfold.sources.profile import quality

SCAN_HINT = (
    "The pages hold almost no text, so they may be scans. "
    "Export them as images, and ingest those with the scan reader."
)


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def read(path: Path, meta: Meta) -> SourceDocument:
    kind, prefix = ("slide", "s") if meta.family == "slides" else ("page", "p")
    pdf = pdfium.PdfDocument(str(path))
    try:
        texts = []
        for index in range(len(pdf)):
            page = pdf[index]
            textpage = page.get_textpage()
            texts.append(_clean(textpage.get_text_range()))
            textpage.close()
            page.close()
    finally:
        pdf.close()
    anchors = [
        Anchor(f"{prefix}-{number}", kind, f"{kind.title()} {number}", text)
        for number, text in enumerate(texts, start=1)
    ]
    words = sum(len(text.split()) for text in texts)
    checked = quality(words, len(texts), kind)
    if checked["low"]:
        checked["hint"] = SCAN_HINT
    profile = {
        "format": "pdf",
        "size": {f"{kind}s": len(texts), "words": words},
        "quality": checked,
    }
    return build(meta, anchors, profile)

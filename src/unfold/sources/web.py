"""Web pages and Markdown: one anchor per section."""

import re
from pathlib import Path

import trafilatura

from unfold.sources import Anchor, Meta, SourceDocument, build
from unfold.sources.profile import quality

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def _slug(title: str, seen: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
    candidate, number = base, 2
    while candidate in seen:
        candidate, number = f"{base}-{number}", number + 1
    seen.add(candidate)
    return candidate


def sections(markdown: str) -> list[Anchor]:
    """Split Markdown at its headings. Text before the first heading is the intro."""
    anchors: list[Anchor] = []
    seen: set[str] = set()
    anchor_id, title, lines = "intro", "Introduction", []

    def close() -> None:
        text = "\n".join(lines).strip()
        if text or anchor_id != "intro":
            if anchor_id == "intro":
                seen.add("intro")
            anchors.append(Anchor(anchor_id, "section", title, text))

    for line in markdown.splitlines():
        match = HEADING.match(line)
        if match:
            close()
            title = match.group(2).strip()
            anchor_id, lines = _slug(title, seen), []
        else:
            lines.append(line)
    close()
    return anchors


def _document(markdown: str, meta: Meta, file_format: str) -> SourceDocument:
    anchors = sections(markdown)
    words = sum(len(a.text.split()) for a in anchors)
    profile = {
        "format": file_format,
        "size": {"sections": len(anchors), "words": words},
        "quality": quality(words, len(anchors), "section"),
    }
    return build(meta, anchors, profile)


def read_markdown(path: Path, meta: Meta) -> SourceDocument:
    return _document(path.read_text(encoding="utf-8"), meta, "md")


def read_html(html: str, meta: Meta) -> SourceDocument:
    """Keep the page's main text, without menus and footers."""
    markdown = trafilatura.extract(
        html, output_format="markdown", include_formatting=True, include_comments=False
    )
    if not markdown:
        raise ValueError("the page has no main text")
    return _document(markdown, meta, "html")


def read_url(url: str, meta: Meta) -> SourceDocument:
    html = trafilatura.fetch_url(url)
    if not html:
        raise ValueError(f"could not download {url}")
    return read_html(html, meta)

"""Web pages and Markdown: one anchor per section."""

import re
from pathlib import Path

import trafilatura
from lxml import html as lxml_html

from unfold.sources import Anchor, Meta, SourceDocument, build
from unfold.sources.profile import quality

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
# Fewer words of main text means a menu or a stub, not an article.
MIN_WORDS = 20
TEX_WRAPPER = re.compile(r"^\{\\(?:display|text)style\s*(.*)\}$", re.DOTALL)


def _with_class(tag: str, name: str) -> str:
    return f"//{tag}[contains(concat(' ', normalize-space(@class), ' '), ' {name} ')]"


# Wiki clutter: edit links, reference marks, and navigation boxes.
CLUTTER = [
    _with_class("*", "mw-editsection"),
    _with_class("sup", "reference"),
    _with_class("*", "navbox"),
    _with_class("table", "sidebar"),
]


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


def prepare(html: str) -> lxml_html.HtmlElement:
    """Keep each formula's TeX, and drop wiki clutter, before extraction.

    Pages such as Wikipedia's put TeX in the `alttext` of each `<math>` element.
    trafilatura drops `<math>`, so without this step every formula vanishes.
    """
    tree = lxml_html.fromstring(html)
    for math in list(tree.iter("math")):
        tex = TEX_WRAPPER.sub(r"\1", (math.get("alttext") or "").strip()).strip()
        wrapper = next(
            (
                span
                for span in math.iterancestors("span")
                if "mwe-math-element" in (span.get("class") or "")
            ),
            math,
        )
        parent = wrapper.getparent()
        if not tex or parent is None:
            continue
        formula = lxml_html.Element("span")
        formula.text = f"${tex}$"
        formula.tail = wrapper.tail
        parent.replace(wrapper, formula)
    for xpath in CLUTTER:
        for element in tree.xpath(xpath):
            element.drop_tree()
    return tree


def read_html(html: str, meta: Meta) -> SourceDocument:
    """Keep the page's main text and formulas, without menus and footers."""
    if not html.strip():
        raise ValueError("the page is empty")
    markdown = trafilatura.extract(
        prepare(html),
        output_format="markdown",
        include_formatting=True,
        include_comments=False,
    )
    words = len((markdown or "").split())
    if markdown is None or words < MIN_WORDS:
        raise ValueError(f"the page has no main text, only {words} words")
    return _document(markdown, meta, "html")


def read_page(path: Path, meta: Meta) -> SourceDocument:
    """Read a web page saved as a file."""
    return read_html(path.read_text(encoding="utf-8", errors="replace"), meta)


def read_url(url: str, meta: Meta) -> SourceDocument:
    html = trafilatura.fetch_url(url)
    if not html:
        raise ValueError(f"could not download {url}")
    return read_html(html, meta)

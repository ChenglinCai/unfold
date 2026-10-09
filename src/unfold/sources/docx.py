"""Word files: styled headings start anchors, and equations become TeX.

A .docx file is a zip of XML parts. The reader reads the main document and its
styles straight from the zip, through an archive that resolves no entities and
stops after MAX_BYTES. A paragraph is a heading when its style, or a style that
the style builds on, is named "heading N" or "Title", or sets an outline level.
A table of contents, deleted text, and field codes stay out, and each equation
becomes TeX.
"""

import posixpath
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]

from unfold.sources import Meta, SourceDocument
from unfold.sources.archive import Archive
from unfold.sources.omml import omml_tex
from unfold.sources.web import _document, markdown_table

MAX_BYTES = 200 * 2**20
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
MAIN = "/officeDocument"
HEADING = re.compile(r"heading (\d)$")
# A paragraph longer than this is no heading, however bold and large it looks.
HEADING_WORDS = 12
# Bullets typed as text, where a list has no numbering of its own.
BULLETS = {chr(code) for code in (0x2022, 0x25E6, 0x25AA, 0x2023, 0x2043)}
# Parts of a paragraph that hold no text for a reader: deleted text, field codes,
# and formatting.
HIDDEN = {f"{W}{name}" for name in ("del", "delText", "instrText", "rPr", "pPr")}


def _value(element: etree._Element | None, path: str) -> str | None:
    found = element.find(path) if element is not None else None
    return found.get(f"{W}val") if found is not None else None


def heading_levels(styles: etree._Element | None) -> dict[str, int]:
    """The heading level of each paragraph style, following the styles it builds on."""
    own: dict[str, tuple[int | None, str | None]] = {}
    for style in styles.iter(f"{W}style") if styles is not None else []:
        name = (_value(style, f"{W}name") or "").lower()
        outline = _value(style, f"{W}pPr/{W}outlineLvl")
        level = None
        if match := HEADING.match(name):
            level = int(match.group(1))
        elif name == "title":
            level = 1
        elif outline is not None and outline.isdigit():
            level = int(outline) + 1
        own[style.get(f"{W}styleId") or ""] = (level, _value(style, f"{W}basedOn"))
    levels: dict[str, int] = {}
    for style_id in own:
        current, seen = style_id, set()
        while current in own and current not in seen:
            seen.add(current)
            level, current = own[current]
            if level is not None:
                if level <= 9:  # level 10 is an outline level of body text
                    levels[style_id] = level
                break
    return levels


def _inline(node: etree._Element, parts: list[str]) -> None:
    """Append the text and equations of a paragraph, in order."""
    for child in node:
        tag = child.tag
        if tag == f"{W}t":
            parts.append(child.text or "")
        elif tag in (f"{W}tab", f"{W}br", f"{W}cr"):
            parts.append(" ")
        elif tag == f"{W}noBreakHyphen":
            parts.append("-")
        elif tag == f"{M}oMathPara":
            parts += [f" $${omml_tex(math)}$$ " for math in child.iter(f"{M}oMath")]
        elif tag == f"{M}oMath":
            parts.append(f"${omml_tex(child)}$")
        elif tag not in HIDDEN:
            _inline(child, parts)


def _text(node: etree._Element) -> str:
    parts: list[str] = []
    _inline(node, parts)
    return " ".join("".join(parts).split())


@dataclass
class _Block:
    """One paragraph, list item, or table, before its heading level is settled."""

    kind: str
    text: str
    level: int | None = None
    depth: int = 0
    size: int | None = None  # the font size of a paragraph that is bold throughout


def _runs(node: etree._Element) -> list[tuple[etree._Element, str]]:
    found = []
    for run in node.iter(f"{W}r"):
        text = "".join(t.text or "" for t in run.iter(f"{W}t"))
        if text.strip():
            found.append((run, text))
    return found


def _size(run: etree._Element) -> int:
    size = _value(run.find(f"{W}rPr"), f"{W}sz")
    return int(size) if size and size.isdigit() else 0


def _bold_size(paragraph: etree._Element) -> int | None:
    """The font size, in half-points, of a paragraph whose every run is bold."""
    runs = _runs(paragraph)
    for run, _ in runs:
        weight = run.find(f"{W}rPr/{W}b")
        if weight is None or weight.get(f"{W}val") in ("0", "false"):
            return None
    return max((_size(run) for run, _ in runs), default=None)


def _paragraph(paragraph: etree._Element, levels: dict[str, int]) -> _Block | None:
    text = _text(paragraph)
    if not text:
        return None
    level = levels.get(_value(paragraph, f"{W}pPr/{W}pStyle") or "")
    outline = _value(paragraph, f"{W}pPr/{W}outlineLvl")
    if outline is not None and outline.isdigit() and int(outline) < 9:
        level = int(outline) + 1
    depth = _value(paragraph, f"{W}pPr/{W}numPr/{W}ilvl")
    if level:
        return _Block("text", text, level=level)
    if depth is not None:
        return _Block("item", text, depth=int(depth) if depth.isdigit() else 0)
    if text[:1] in BULLETS:
        return _Block("item", text[1:].strip())
    return _Block("text", text, size=_bold_size(paragraph))


def _blocks(body: etree._Element, levels: dict[str, int], out: list[_Block]) -> None:
    """Append the blocks of each paragraph and table, in order."""
    for child in body:
        if child.tag == f"{W}p" and (block := _paragraph(child, levels)):
            out.append(block)
        elif child.tag == f"{W}tbl":
            rows = [
                [
                    " ".join(filter(None, (_text(p) for p in cell.iter(f"{W}p"))))
                    for cell in row.iterchildren(f"{W}tc")
                ]
                for row in child.iterchildren(f"{W}tr")
            ]
            out.append(_Block("table", markdown_table(rows)))
        elif child.tag == f"{W}sdt":
            gallery = _value(child, f".//{W}docPartObj/{W}docPartGallery") or ""
            content = child.find(f"{W}sdtContent")
            if "contents" not in gallery.lower() and content is not None:
                _blocks(content, levels, out)


def _guess_headings(blocks: list[_Block], body: etree._Element) -> None:
    """With no styled heading, a short paragraph that is bold throughout and larger
    than the body text is a heading. The largest size makes level 1."""
    weights: Counter[int] = Counter()
    for run, text in _runs(body):
        weights[_size(run)] += len(text)
    normal = weights.most_common(1)[0][0] if weights else 0
    sizes = sorted(
        {
            b.size
            for b in blocks
            if b.size and b.size > normal and len(b.text.split()) <= HEADING_WORDS
        },
        reverse=True,
    )
    for block in blocks:
        if block.size in sizes and len(block.text.split()) <= HEADING_WORDS:
            block.level = sizes.index(block.size) + 1


def document_markdown(document: etree._Element, levels: dict[str, int]) -> str:
    """A Word document's body as Markdown. List items stay on adjacent lines."""
    body = document.find(f"{W}body")
    if body is None:
        return "\n"
    blocks: list[_Block] = []
    _blocks(body, levels, blocks)
    if not any(block.level for block in blocks):
        _guess_headings(blocks, body)
    out = []
    for block in blocks:
        if block.level:
            out.append(f"\n\n{'#' * min(block.level, 6)} {block.text}")
        elif block.kind == "item":
            out.append(f"\n{'  ' * block.depth}- {block.text}")
        else:
            out.append(f"\n\n{block.text}")
    return "".join(out).strip() + "\n"


def _main_part(book: Archive, present: set[str]) -> str:
    """The name of the main document part, which the package's relations give."""
    if "_rels/.rels" in present:
        for relation in book.xml("_rels/.rels"):
            if (relation.get("Type") or "").endswith(MAIN) and relation.get("Target"):
                return posixpath.normpath((relation.get("Target") or "").lstrip("/"))
    return "word/document.xml"


def read_docx(path: Path, meta: Meta) -> SourceDocument:
    with zipfile.ZipFile(path) as archive:
        book = Archive(archive, MAX_BYTES, "Word file")
        present = set(archive.namelist())
        main = _main_part(book, present)
        if main not in present:
            raise ValueError(f"the Word file has no main document, {main}")
        styles = posixpath.join(posixpath.dirname(main), "styles.xml")
        levels = heading_levels(book.xml(styles) if styles in present else None)
        markdown = document_markdown(book.xml(main), levels)
    if not markdown.strip():
        raise ValueError("the Word file has no text")
    return _document(markdown, meta, "docx")

"""EPUB books: chapters in reading order, with each heading as an anchor.

An EPUB is a zip of XHTML chapters, and its package file gives their reading
order. The reader reads them from the zip in that order, and never unpacks to
disk. Its XML parser resolves no entities, loads no DTD, and opens no network,
and it stops after MAX_BYTES of unpacked text, so a hostile book cannot read
local files or fill memory.

A chapter holds no menus or ads, so the reader converts every block in order,
instead of guessing at the main text as the web reader must.
"""

import posixpath
import re
import urllib.parse
import zipfile
from pathlib import Path

from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]
from lxml import html as lxml_html

from unfold.sources import Meta, SourceDocument
from unfold.sources.web import _document, markdown_table, prepare

MAX_BYTES = 200 * 2**20
PARSER = etree.XMLParser(
    resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False
)
CHAPTERS = {"application/xhtml+xml", "text/html"}
# An XML declaration and a DOCTYPE, whose inline entities the HTML parser would print.
PROLOG = re.compile(
    r"^\s*(?:<\?xml[^>]*\?>)?\s*(?:<!DOCTYPE[^\[>]*(?:\[.*?\])?\s*>)?", re.DOTALL
)
HEADINGS = {f"h{level}" for level in range(1, 7)}
SKIPPED = {"head", "script", "style", "nav", "hr"}
TEXT = {"p", "blockquote", "dt", "dd", "address", "figcaption"}
BLOCKS = (
    HEADINGS
    | SKIPPED
    | TEXT
    | {"div", "section", "article", "main", "header", "footer", "aside", "body"}
    | {"ul", "ol", "dl", "table", "pre", "figure"}
)


class _Book:
    """A zip that counts what it unpacks, and stops at MAX_BYTES."""

    def __init__(self, archive: zipfile.ZipFile) -> None:
        self.archive, self.left = archive, MAX_BYTES

    def read(self, name: str) -> bytes:
        with self.archive.open(name) as member:
            data = member.read(self.left + 1)
        self.left -= len(data)
        if self.left < 0:
            raise ValueError(f"the EPUB unpacks to more than {MAX_BYTES // 2**20} MB")
        return data

    def xml(self, name: str) -> etree._Element:
        return etree.fromstring(self.read(name), PARSER)


def spine(book: _Book) -> list[str]:
    """The names of the book's chapters inside the zip, in reading order."""
    rootfile = book.xml("META-INF/container.xml").find(".//{*}rootfile")
    package_name = rootfile.get("full-path") if rootfile is not None else None
    if not package_name:
        raise ValueError("the EPUB names no package file")
    package = book.xml(package_name)
    hrefs = {
        item.get("id"): item.get("href")
        for item in package.iterfind(".//{*}manifest/{*}item")
        if item.get("media-type") in CHAPTERS
    }
    base = posixpath.dirname(package_name)
    names = []
    for ref in package.iterfind(".//{*}spine/{*}itemref"):
        href = hrefs.get(ref.get("idref"))
        if href and ref.get("linear") != "no":
            target = urllib.parse.unquote(href.split("#")[0])
            names.append(posixpath.normpath(posixpath.join(base, target)))
    return names


def _words(text: str) -> str:
    return " ".join(text.split())


def _tag(element: lxml_html.HtmlElement) -> str:
    return element.tag if isinstance(element.tag, str) else ""


def _item_text(item: lxml_html.HtmlElement) -> str:
    """A list item's own text, without the lists nested inside it."""
    parts = [item.text or ""]
    for child in item:
        if _tag(child) not in ("ul", "ol"):
            parts.append(child.text_content())
        parts.append(child.tail or "")
    return _words("".join(parts))


def _list(element: lxml_html.HtmlElement, lines: list[str], depth: int) -> None:
    bullet = "1." if _tag(element) == "ol" else "-"
    for item in element.iterchildren("li"):
        lines.append(f"{'  ' * depth}{bullet} {_item_text(item)}")
        for nested in item.iterchildren("ul", "ol"):
            _list(nested, lines, depth + 1)


def _block(element: lxml_html.HtmlElement, out: list[str]) -> None:
    """Append the Markdown blocks of one element, in document order."""
    tag = _tag(element)
    if tag in SKIPPED:
        return
    if tag in HEADINGS:
        out.append(f"{'#' * int(tag[1])} {_words(element.text_content())}")
    elif tag in ("ul", "ol"):
        lines: list[str] = []
        _list(element, lines, 0)
        out.append("\n".join(lines))
    elif tag == "pre":
        code = element.text_content().strip("\n")
        out.append(f"```\n{code}\n```")
    elif tag == "table":
        rows = [
            [_words(cell.text_content()) for cell in row.iterchildren("td", "th")]
            for row in element.iter("tr")
        ]
        out.append(markdown_table(rows))
    elif tag == "figure":
        for caption in element.iter("figcaption"):
            out.append(f"*Figure: {_words(caption.text_content())}*")
    elif tag in TEXT:
        out.append(_words(element.text_content()))
    else:
        _container(element, out)


def _container(element: lxml_html.HtmlElement, out: list[str]) -> None:
    """Text that sits between child blocks becomes a paragraph of its own."""
    run = [element.text or ""]
    for child in element:
        if _tag(child) in BLOCKS:
            out.append(_words("".join(run)))
            _block(child, out)
            run = [child.tail or ""]
        else:
            run += [child.text_content(), child.tail or ""]
    out.append(_words("".join(run)))


def chapter_markdown(xhtml: str) -> str:
    """One chapter as Markdown: every heading, paragraph, list, table, and caption."""
    tree = prepare(PROLOG.sub("", xhtml))
    for br in tree.iter("br"):
        br.tail = "\n" + (br.tail or "")
    blocks: list[str] = []
    _block(tree, blocks)
    return "\n\n".join(block for block in blocks if block.strip("# "))


def read_epub(path: Path, meta: Meta) -> SourceDocument:
    with zipfile.ZipFile(path) as archive:
        book = _Book(archive)
        present = set(archive.namelist())
        names = [name for name in spine(book) if name in present]
        if "META-INF/encryption.xml" in present:
            locked = {
                ref.get("URI")
                for ref in book.xml("META-INF/encryption.xml").iterfind(
                    ".//{*}CipherReference"
                )
            }
            if locked & set(names):
                raise ValueError(
                    "the EPUB's chapters are encrypted, so unfold cannot read them"
                )
        chapters = [
            chapter_markdown(book.read(name).decode("utf-8", errors="replace"))
            for name in names
        ]
    markdown = "\n\n".join(chapter for chapter in chapters if chapter.strip())
    if not markdown:
        raise ValueError("the EPUB has no chapter with text")
    return _document(markdown, meta, "epub")

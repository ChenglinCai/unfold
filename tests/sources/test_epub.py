"""EPUB books become Markdown: chapters in reading order, with their headings as anchors."""

import zipfile
from pathlib import Path

import pytest

from unfold.cli import main
from unfold.sources import Meta, epub, load
from unfold.sources.epub import read_epub

META = Meta(id="wn", title="Wealth", family="textbook", origin="wn.epub", license=None)
CONTAINER = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf"
    media-type="application/oebps-package+xml"/></rootfiles>
</container>"""
PACKAGE = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <manifest>
    <item id="two" href="money.xhtml" media-type="application/xhtml+xml"/>
    <item id="one" href="text/labour.xhtml" media-type="application/xhtml+xml"/>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
  </manifest>
  <spine><itemref idref="nav" linear="no"/><itemref idref="one"/><itemref idref="two"/></spine>
</package>"""
PAGE = """<?xml version="1.0" encoding="utf-8"?>
{doctype}<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Page title</title></head>
<body>{body}</body></html>"""
LABOUR = """<h1>Of the Division of Labour</h1>
<p>The greatest improvement in the productive powers of labour seems to have been
the effects of the division of labour.</p>
<h2>A pin factory</h2>
<p>One man draws out the wire, another straights it, and a third cuts it.</p>
<p>Output grows at a rate of <math alttext="r = 0.05"><mi>r</mi></math> each year.</p>
<ul><li>Dexterity<ul><li>of each workman</li></ul></li><li>Saving <em>time</em></li></ul>
<table><tr><th>Workers</th><th>Pins a day</th></tr><tr><td>10</td><td>48,000</td></tr></table>"""
MONEY = """<h1>Of Money</h1>
<div>Money is the great wheel <em>of circulation</em>.<p>It is the instrument of commerce.</p>
Each nation<br/>keeps some.</div>"""
NAV = "<h1>Contents</h1><p>A list of chapters that a reader skips past.</p>"


def _book(
    folder: Path, pages: dict[str, str], extra: dict[str, str] | None = None
) -> Path:
    path = folder / "wn.epub"
    with zipfile.ZipFile(path, "w") as book:
        book.writestr("mimetype", "application/epub+zip")
        book.writestr("META-INF/container.xml", CONTAINER)
        book.writestr("OEBPS/content.opf", PACKAGE)
        for name, body in pages.items():
            book.writestr(f"OEBPS/{name}", PAGE.format(doctype="", body=body))
        for name, text in (extra or {}).items():
            book.writestr(name, text)
    return path


PAGES = {"text/labour.xhtml": LABOUR, "money.xhtml": MONEY, "nav.xhtml": NAV}


def test_chapters_come_in_reading_order_with_their_headings(tmp_path: Path) -> None:
    doc = read_epub(_book(tmp_path, PAGES), META)

    assert [a.id for a in doc.anchors] == [
        "of-the-division-of-labour",
        "a-pin-factory",
        "of-money",
    ]
    text = doc.text()
    assert "Output grows at a rate of $r = 0.05$ each year." in text
    assert "- Dexterity\n  - of each workman\n- Saving time" in text
    assert "| Workers | Pins a day |\n| --- | --- |\n| 10 | 48,000 |" in text
    assert (
        "wheel of circulation.\n\nIt is the instrument of commerce.\n\nEach nation keeps"
        in text
    )
    assert "Contents" not in text and "Page title" not in text
    assert doc.profile["format"] == "epub"


def test_a_chapter_cannot_read_local_files_through_an_entity(tmp_path: Path) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("The secret.\n")
    doctype = f'<!DOCTYPE html [<!ENTITY leak SYSTEM "file://{secret}">]>\n'
    path = tmp_path / "wn.epub"
    with zipfile.ZipFile(path, "w") as book:
        book.writestr("META-INF/container.xml", CONTAINER)
        book.writestr("OEBPS/content.opf", PACKAGE)
        book.writestr("OEBPS/money.xhtml", PAGE.format(doctype="", body=MONEY))
        book.writestr(
            "OEBPS/text/labour.xhtml",
            PAGE.format(
                doctype=doctype, body=LABOUR.replace("third cuts it.", "&leak;")
            ),
        )

    text = read_epub(path, META).text()

    assert "secret" not in text.lower() and "]>" not in text
    assert "One man draws out the wire" in text


def test_a_book_that_unpacks_too_large_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(epub, "MAX_BYTES", 1000)

    with pytest.raises(ValueError, match="MB"):
        read_epub(_book(tmp_path, {**PAGES, "money.xhtml": MONEY * 20}), META)


def test_encrypted_chapters_fail(tmp_path: Path) -> None:
    locked = """<encryption xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
      xmlns:enc="http://www.w3.org/2001/04/xmlenc#"><enc:EncryptedData><enc:CipherData>
      <enc:CipherReference URI="OEBPS/money.xhtml"/></enc:CipherData></enc:EncryptedData>
      </encryption>"""

    with pytest.raises(ValueError, match="encrypted"):
        read_epub(_book(tmp_path, PAGES, {"META-INF/encryption.xml": locked}), META)


def test_ingest_reads_an_epub(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _book(tmp_path, PAGES)
    out = tmp_path / "sources"

    assert (
        main(["ingest", str(path), "--out", str(out), "--license", "Public domain"])
        == 0
    )

    doc = load(out / "wn")
    assert doc.family == "textbook"
    assert doc.anchors[0].id == "of-the-division-of-labour"

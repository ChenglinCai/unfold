"""PDFs become one anchor per page, or per slide for decks."""

from pathlib import Path

import cairo
import pytest

from unfold.sources import Meta
from unfold.sources.pdf import read

PAGES = ["Demand slopes down as the price rises.", "Supply slopes up with the price."]


@pytest.fixture
def two_pages(tmp_path: Path) -> Path:
    path = tmp_path / "two-pages.pdf"
    surface = cairo.PDFSurface(str(path), 612, 792)
    context = cairo.Context(surface)
    context.set_font_size(14)
    for text in PAGES:
        context.move_to(72, 72)
        context.show_text(text)
        context.show_page()
    surface.finish()
    return path


def meta(family: str) -> Meta:
    return Meta(
        id="demo", title="Demo", family=family, origin="demo.pdf", license="CC BY 4.0"
    )


def test_each_page_becomes_an_anchor(two_pages: Path) -> None:
    doc = read(two_pages, meta("textbook"))

    assert [(a.id, a.kind) for a in doc.anchors] == [("p-1", "page"), ("p-2", "page")]
    assert "Demand slopes down" in doc.anchors[0].text
    assert "Supply slopes up" in doc.anchors[1].text


def test_a_deck_gets_slide_anchors(two_pages: Path) -> None:
    doc = read(two_pages, meta("slides"))

    assert [(a.id, a.kind) for a in doc.anchors] == [("s-1", "slide"), ("s-2", "slide")]


def test_the_profile_counts_pages_and_flags_sparse_text(two_pages: Path) -> None:
    profile = read(two_pages, meta("textbook")).profile

    assert profile["format"] == "pdf"
    assert profile["size"] == {"pages": 2, "words": 13}
    assert profile["quality"] == {"words_per_page": 6, "low": True}
    assert profile["needs"] == "cut"


def test_rights_come_from_the_license(two_pages: Path) -> None:
    assert read(two_pages, meta("textbook")).rights["public_outputs"] is True

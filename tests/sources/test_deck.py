"""PowerPoint decks become one anchor per slide, with speaker notes."""

from pathlib import Path

import pytest
from pptx import Presentation
from pptx.shapes.autoshape import Shape

from unfold.sources import Meta
from unfold.sources.deck import read


@pytest.fixture
def deck(tmp_path: Path) -> Path:
    presentation = Presentation()
    layout = presentation.slide_layouts[1]
    for title, body in [
        ("Variance", "Spread around the mean."),
        ("Bias", "Error from assumptions."),
    ]:
        slide = presentation.slides.add_slide(layout)
        heading, placeholder = slide.shapes.title, slide.placeholders[1]
        assert heading is not None
        assert isinstance(placeholder, Shape)
        heading.text = title
        placeholder.text_frame.text = body
    notes = presentation.slides[0].notes_slide.notes_text_frame
    assert notes is not None
    notes.text = "Square the distances first."
    path = tmp_path / "deck.pptx"
    presentation.save(str(path))
    return path


def test_each_slide_becomes_an_anchor(deck: Path) -> None:
    doc = read(deck, Meta(id="d", title="Deck", family="slides", origin="deck.pptx"))

    assert [(a.id, a.title) for a in doc.anchors] == [
        ("s-1", "Variance"),
        ("s-2", "Bias"),
    ]
    assert "Spread around the mean." in doc.anchors[0].text
    assert "Square the distances first." in doc.anchors[0].text
    assert doc.profile["size"] == {"slides": 2, "words": 13}
    assert doc.profile["needs"] == "fill-gaps"

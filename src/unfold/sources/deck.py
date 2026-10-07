"""PowerPoint decks: one anchor per slide, with the slide's speaker notes."""

from pathlib import Path

from pptx import Presentation
from pptx.shapes.autoshape import Shape

from unfold.sources import Anchor, Meta, SourceDocument, build
from unfold.sources.profile import quality


def read(path: Path, meta: Meta) -> SourceDocument:
    deck = Presentation(str(path))
    anchors: list[Anchor] = []
    words = 0
    for number, slide in enumerate(deck.slides, start=1):
        title_shape = slide.shapes.title
        title = title_shape.text.strip() if title_shape is not None else ""
        title_id = title_shape.shape_id if title_shape is not None else None
        parts = [
            shape.text_frame.text.strip()
            for shape in slide.shapes
            if isinstance(shape, Shape)
            and shape.has_text_frame
            and shape.shape_id != title_id
        ]
        frame = slide.notes_slide.notes_text_frame if slide.has_notes_slide else None
        notes = frame.text.strip() if frame is not None else ""
        words += sum(len(text.split()) for text in [title, *parts, notes])
        body = "\n\n".join(part for part in parts if part)
        if notes:
            body += f"\n\nSpeaker notes: {notes}"
        anchors.append(Anchor(f"s-{number}", "slide", title or f"Slide {number}", body))
    profile = {
        "format": "pptx",
        "size": {"slides": len(anchors), "words": words},
        "quality": quality(words, len(anchors), "slide"),
    }
    return build(meta, anchors, profile)

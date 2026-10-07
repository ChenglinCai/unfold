"""A source document saves and loads its manifest and its anchored text."""

from pathlib import Path

import pytest
import yaml

from unfold.sources import Anchor, SourceDocument, load


def sample() -> SourceDocument:
    return SourceDocument(
        id="demo",
        title="A demo source",
        family="textbook",
        origin="demo.pdf",
        rights={"license": "CC-BY-4.0", "owner": "Someone", "public_outputs": True},
        profile={"format": "pdf", "subject": "statistics"},
        anchors=[
            Anchor("p-1", "page", "Page 1", "First page text."),
            Anchor("p-2", "page", "Page 2", "Second page text."),
        ],
    )


def test_saves_a_manifest_and_anchored_text(tmp_path: Path) -> None:
    folder = sample().save(tmp_path)

    manifest = yaml.safe_load((folder / "source.yaml").read_text(encoding="utf-8"))
    assert manifest["format"] == "source/v1"
    assert manifest["anchors"] == [
        {"id": "p-1", "kind": "page", "title": "Page 1"},
        {"id": "p-2", "kind": "page", "title": "Page 2"},
    ]
    assert manifest["retrieved"]
    text = (folder / "document.md").read_text(encoding="utf-8")
    assert text.index("<!-- anchor: p-1 -->") < text.index("<!-- anchor: p-2 -->")


def test_loads_what_it_saved(tmp_path: Path) -> None:
    original = sample()
    loaded = load(original.save(tmp_path))

    assert loaded == original


def test_rejects_bad_anchor_ids() -> None:
    with pytest.raises(ValueError, match="anchor id"):
        Anchor("Page 1", "page", "Page 1", "text")


def test_a_bare_topic_has_no_anchors(tmp_path: Path) -> None:
    topic = SourceDocument("clt", "The central limit theorem", "topic", "topic", {})
    loaded = load(topic.save(tmp_path))

    assert loaded.anchors == []
    assert (tmp_path / "clt" / "document.md").read_text(encoding="utf-8") == ""

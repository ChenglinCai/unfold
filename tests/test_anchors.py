"""Anchor references name real places in a source manifest."""

from unfold.anchors import anchor_ids, references, unresolved

MANIFEST = {
    "id": "econ",
    "anchors": [
        {"id": "table-3-1", "kind": "table"},
        {"id": "supply", "kind": "heading"},
    ],
}


def test_lists_the_anchors_a_manifest_offers() -> None:
    assert anchor_ids(MANIFEST) == {"econ#table-3-1", "econ#supply"}


def test_finds_references_under_any_anchors_key() -> None:
    doc = {
        "anchors": ["econ#supply"],
        "concepts": [{"id": "demand", "anchors": ["econ#table-3-1"]}],
        "note": "econ#ignored, because it is not under an anchors key",
    }

    assert references(doc) == ["econ#supply", "econ#table-3-1"]


def test_reports_references_that_resolve_nowhere() -> None:
    doc = {"concepts": [{"anchors": ["econ#supply", "econ#figure-9", "other#x"]}]}

    assert unresolved(doc, [MANIFEST]) == ["econ#figure-9", "other#x"]

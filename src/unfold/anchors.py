"""Anchors: pointers from our files to places in a source.

A source manifest lists the places a source offers, such as headings, tables,
and figures. Other files point at them as `<source-id>#<anchor-id>` in any list
under a key named `anchors`. `docs/formats.md` describes both sides.
"""

from collections.abc import Iterable, Mapping


def anchor_ids(manifest: Mapping[str, object]) -> set[str]:
    """Return every reference that a source manifest can resolve."""
    anchors = manifest.get("anchors") or []
    assert isinstance(anchors, list)
    return {f"{manifest['id']}#{anchor['id']}" for anchor in anchors}


def references(doc: object) -> list[str]:
    """Collect, in order, every string listed under a key named `anchors`."""
    found: list[str] = []
    if isinstance(doc, Mapping):
        for key, value in doc.items():
            if key == "anchors" and isinstance(value, list):
                found.extend(str(item) for item in value)
            else:
                found.extend(references(value))
    elif isinstance(doc, list):
        for item in doc:
            found.extend(references(item))
    return found


def unresolved(doc: object, manifests: Iterable[Mapping[str, object]]) -> list[str]:
    """Return each reference in doc that no manifest offers."""
    offered = set().union(*(anchor_ids(m) for m in manifests))
    return [ref for ref in references(doc) if ref not in offered]

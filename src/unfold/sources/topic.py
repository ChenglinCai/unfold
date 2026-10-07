"""Bare topics: a phrase such as "the central limit theorem", with no source text."""

from unfold.sources import Meta, SourceDocument, build


def read(meta: Meta) -> SourceDocument:
    """Make a source document with no text and no anchors.

    No source text can reach the outputs, so no license limits them. The
    understand step flags every claim instead, because no source supports it.
    """
    profile = {"format": "topic", "size": {"words": 0}, "quality": {"low": True}}
    doc = build(meta, [], profile)
    doc.rights = {
        "license": "none",
        "owner": "",
        "attribution": "",
        "public_outputs": True,
    }
    return doc

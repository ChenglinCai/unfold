"""A bare topic is a phrase with no source text."""

from unfold.sources import Meta
from unfold.sources.topic import read


def test_a_topic_has_no_text_and_needs_a_fact_check() -> None:
    phrase = "the central limit theorem"

    doc = read(Meta(id="clt", title=phrase, family="topic", origin=phrase))

    assert (doc.anchors, doc.text()) == ([], "")
    assert doc.profile["needs"] == "fact-check"
    assert doc.profile["family"] == "topic"
    assert doc.rights["public_outputs"] is True

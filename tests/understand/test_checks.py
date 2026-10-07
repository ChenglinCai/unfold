"""Code checks every knowledge map and every set of study notes."""

import pytest
import yaml

from unfold.sources import Anchor, SourceDocument
from unfold.understand.checks import check_map, check_notes

DOC = SourceDocument(
    id="demo",
    title="Spread",
    family="textbook",
    origin="demo.pdf",
    rights={},
    anchors=[Anchor("p-1", "page", "Page 1"), Anchor("p-2", "page", "Page 2")],
)
TOPIC = SourceDocument(
    id="clt", title="the central limit theorem", family="topic", origin="", rights={}
)
MAP = {
    "format": "knowledge-map/v0",
    "source": "demo",
    "concepts": [
        {
            "id": "mean",
            "name": "mean",
            "meaning": "The sum divided by the count.",
            "requires": [],
            "anchors": ["demo#p-1"],
        },
        {
            "id": "variance",
            "name": "variance",
            "meaning": "The mean squared distance from the mean.",
            "requires": ["mean"],
            "anchors": ["demo#p-2"],
        },
    ],
    "claims": [{"text": "Variance is never negative.", "anchors": ["demo#p-2"]}],
    "gaps": [],
    "suspected_errors": [],
}


def changed(**fields: object) -> str:
    return yaml.safe_dump({**MAP, **fields})


def test_a_valid_map_passes() -> None:
    assert check_map(yaml.safe_dump(MAP), DOC) == []


def test_text_that_is_not_yaml_fails() -> None:
    [error] = check_map("concepts: [", DOC)
    assert "not valid YAML" in error


@pytest.mark.parametrize("missing", ["concepts", "claims", "gaps", "suspected_errors"])
def test_a_missing_section_is_named(missing: str) -> None:
    data = {name: value for name, value in MAP.items() if name != missing}

    assert any(missing in error for error in check_map(yaml.safe_dump(data), DOC))


def test_a_concept_without_a_meaning_is_named() -> None:
    concepts = [MAP["concepts"][0] | {"meaning": ""}, MAP["concepts"][1]]

    errors = check_map(changed(concepts=concepts), DOC)

    assert errors == ["concept 'mean' has no meaning"]


def test_the_map_must_name_its_own_source_and_format() -> None:
    errors = check_map(changed(source="other", format="knowledge-map/v9"), DOC)

    assert len(errors) == 2


def test_every_anchor_must_resolve() -> None:
    claims = [{"text": "Variance is never negative.", "anchors": ["demo#p-9"]}]

    assert check_map(changed(claims=claims), DOC) == ["unknown anchor: demo#p-9"]


def test_every_required_concept_must_exist() -> None:
    concepts = [MAP["concepts"][0], MAP["concepts"][1] | {"requires": ["median"]}]

    errors = check_map(changed(concepts=concepts), DOC)

    assert errors == ["concept 'variance' requires 'median', which the map lacks"]


def test_concept_ids_are_unique_slugs() -> None:
    concepts = [MAP["concepts"][0], MAP["concepts"][0] | {"id": "Mean Value"}]
    concepts.append(MAP["concepts"][0])

    errors = check_map(changed(concepts=concepts), DOC)

    assert any("Mean Value" in error for error in errors)
    assert any("twice" in error for error in errors)


def test_a_claim_needs_an_anchor_or_the_unsupported_flag() -> None:
    bare = {"text": "Variance has units squared.", "anchors": []}

    assert check_map(changed(claims=[bare]), DOC) != []
    assert check_map(changed(claims=[bare | {"unsupported": True}]), DOC) == []


def test_every_claim_of_a_bare_topic_is_flagged() -> None:
    concepts = [{**c, "anchors": []} for c in MAP["concepts"]]
    claim = {"text": "Sample means look normal.", "anchors": []}
    data = {**MAP, "source": "clt", "concepts": concepts, "claims": [claim]}

    [error] = check_map(yaml.safe_dump(data), TOPIC)
    assert "unsupported" in error

    data["claims"] = [claim | {"unsupported": True}]
    assert check_map(yaml.safe_dump(data), TOPIC) == []


def test_study_notes_cite_anchors_that_exist() -> None:
    notes = (
        "# Spread\n\nThe mean is the center [§p-1]. Variance measures spread [§p-7].\n"
    )

    assert check_notes(notes, DOC) == ["unknown citation: [§p-7]"]


def test_study_notes_must_cite_the_source() -> None:
    [error] = check_notes("# Spread\n\nThe mean is the center.\n", DOC)

    assert "cite" in error


def test_empty_study_notes_fail() -> None:
    assert check_notes("  \n", DOC) == ["the study notes are empty"]


def test_notes_on_a_bare_topic_cite_nothing() -> None:
    assert (
        check_notes("# The central limit theorem\n\nMeans settle down.\n", TOPIC) == []
    )


def test_a_citation_may_list_several_anchors() -> None:
    assert check_notes("Spread grows [§p-1, §p-2].", DOC) == []
    assert check_notes("Spread grows [§p-1, §p-8].", DOC) == [
        "unknown citation: [§p-8]"
    ]

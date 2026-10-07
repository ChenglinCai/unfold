"""Checks for what the understand step writes. Each check returns a list of errors.

An empty list means the output passes. When a check fails, the errors go back
to the model as feedback for its next try.
"""

import re

import yaml

from unfold.anchors import unresolved
from unfold.sources import ANCHOR_ID, SourceDocument

FORMAT = "knowledge-map/v0"
SECTIONS = ("concepts", "claims", "gaps", "suspected_errors")
CONCEPT_FIELDS = ("id", "name", "meaning")
CITATION = re.compile(r"\[§([^\]]*)\]")


def check_map(text: str, doc: SourceDocument) -> list[str]:
    """Check a knowledge map in the knowledge-map/v0 format against its source."""
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        return [f"the knowledge map is not valid YAML: {error}"]
    if not isinstance(data, dict):
        return ["the knowledge map must be a YAML mapping"]
    errors: list[str] = []
    if data.get("format") != FORMAT:
        errors.append(f"format must be {FORMAT}")
    if data.get("source") != doc.id:
        errors.append(f"source must be {doc.id}")
    missing = [name for name in SECTIONS if not isinstance(data.get(name), list)]
    errors += [f"the map needs a list named {name}" for name in missing]
    if missing:
        return errors
    errors += _concepts(data["concepts"])
    errors += _claims(data["claims"], topic=doc.family == "topic")
    unknown = dict.fromkeys(unresolved(data, [doc.manifest()]))
    errors += [f"unknown anchor: {ref}" for ref in unknown]
    return errors


def _concepts(concepts: list[object]) -> list[str]:
    errors: list[str] = []
    ids: list[str] = []
    for number, concept in enumerate(concepts, start=1):
        if not isinstance(concept, dict):
            errors.append(f"concept {number} must be a mapping")
            continue
        label = str(concept.get("id") or number)
        for name in CONCEPT_FIELDS:
            value = concept.get(name)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"concept {label!r} has no {name}")
        for name in ("requires", "anchors"):
            if not isinstance(concept.get(name, []), list):
                errors.append(f"concept {label!r}: {name} must be a list")
        concept_id = concept.get("id")
        if isinstance(concept_id, str) and concept_id:
            if not ANCHOR_ID.match(concept_id):
                errors.append(
                    f"concept id {concept_id!r} must use lower-case letters, digits, and -"
                )
            if concept_id in ids:
                errors.append(f"concept {concept_id!r} appears twice")
            ids.append(concept_id)
    for concept in concepts:
        if isinstance(concept, dict) and isinstance(concept.get("requires"), list):
            errors += [
                f"concept {concept.get('id')!r} requires {needed!r}, which the map lacks"
                for needed in concept["requires"]
                if needed not in ids
            ]
    return errors


def _claims(claims: list[object], topic: bool) -> list[str]:
    errors: list[str] = []
    for number, claim in enumerate(claims, start=1):
        if not isinstance(claim, dict) or not str(claim.get("text") or "").strip():
            errors.append(f"claim {number} needs a text")
            continue
        anchors = claim.get("anchors", [])
        flagged = claim.get("unsupported") is True
        if not isinstance(anchors, list):
            errors.append(f"claim {number}: anchors must be a list")
        elif topic and not flagged:
            errors.append(
                f"claim {number} needs unsupported: true, because a bare topic has no source"
            )
        elif not anchors and not flagged:
            errors.append(
                f"claim {number} cites no anchor, so it needs unsupported: true"
            )
    return errors


def citations(text: str) -> list[str]:
    """Every anchor id cited as [§id], including lists such as [§p-1, §p-2]."""
    found: list[str] = []
    for group in CITATION.findall(text):
        found += [part.strip().lstrip("§").strip() for part in group.split(",")]
    return found


def check_notes(text: str, doc: SourceDocument) -> list[str]:
    """Check that study notes exist and that each citation names an anchor."""
    if not text.strip():
        return ["the study notes are empty"]
    known = {anchor.id for anchor in doc.anchors}
    cited = citations(text)
    errors = [
        f"unknown citation: [§{anchor_id}]"
        for anchor_id in dict.fromkeys(cited)
        if anchor_id not in known
    ]
    if known and not cited:
        errors.append("the study notes must cite the source, as [§anchor-id]")
    return errors

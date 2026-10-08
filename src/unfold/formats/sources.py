"""Schemas for source manifests, knowledge maps, and job records."""

import datetime
from typing import Annotated, Literal

from pydantic import Field

from unfold.fields import Model, Ref, Slug, Text

__all__ = ["Model", "Ref", "Slug", "Text"]  # shared types that other formats import


class Anchor(Model):
    id: Slug
    kind: Text
    title: str


class RightsV0(Model):
    license: str | None = None
    license_url: str | None = None
    owner: str | None = None
    attribution: str | None = None
    public_outputs: bool


class SourceV0(Model):
    """A manifest written by hand in M1."""

    format: Literal["source/v0"]
    id: Slug
    title: Text
    family: Text
    subject: str | None = None
    work: str | None = None
    authors: list[str] = Field(default_factory=list)
    publisher: str | None = None
    published: datetime.date | str | None = None
    url: str | None = None
    files: dict[str, str] = Field(default_factory=dict)
    rights: RightsV0
    anchors: list[Anchor]


class Rights(Model):
    license: Text
    owner: str
    attribution: str
    public_outputs: bool


class Profile(Model):
    family: str | None = None
    format: Text
    size: dict[str, int | float]
    quality: dict[str, object]
    subject: str
    needs: Text


class SourceV1(Model):
    """The manifest of a source document that `unfold ingest` wrote."""

    format: Literal["source/v1"]
    id: Slug
    title: Text
    family: Literal["textbook", "slides", "web", "recording", "topic"]
    origin: str
    retrieved: datetime.date | str
    files: dict[str, str] = Field(default_factory=lambda: {"text": "document.md"})
    rights: Rights
    profile: Profile
    anchors: list[Anchor]


class Concept(Model):
    id: Slug
    name: Text
    meaning: Text
    requires: list[Slug] = Field(default_factory=list)
    anchors: list[Ref] = Field(default_factory=list)


class Claim(Model):
    text: Text
    anchors: list[Ref] = Field(default_factory=list)
    unsupported: bool = False


class SuspectedError(Model):
    text: Text
    anchors: list[Ref] = Field(default_factory=list)


class KnowledgeMapV0(Model):
    format: Literal["knowledge-map/v0"]
    source: Slug
    written_by: str | None = None
    concepts: Annotated[list[Concept], Field(min_length=1)]
    claims: list[Claim]
    gaps: list[str]
    suspected_errors: list[str | SuspectedError]


class JobV0(Model):
    """What one model job did. M2 records have no format or tries."""

    format: Literal["job/v0"] = "job/v0"
    key: Text
    model: Text
    attempts: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    outcome: Literal["running", "ok", "failed"]
    errors: list[str] = Field(default_factory=list)
    tries: list[list[str]] = Field(default_factory=list)
    last_reply: dict[str, object] | None = None

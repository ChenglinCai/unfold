"""Schemas for one episode: its outline, and each segment's script and storyboard."""

from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from unfold.formats.series import EpisodeId
from unfold.formats.sources import Model, Ref, Slug, Text

SegmentId = Annotated[str, StringConstraints(pattern=r"^s\d+-[a-z0-9][a-z0-9-]*$")]
# What a segment needs or teaches, such as term:demand or visual:demand-curve.
Item = Annotated[
    str, StringConstraints(pattern=r"^(term|idea|visual):[a-z0-9][a-z0-9-]*$")
]


class Callback(Model):
    to: SegmentId
    visual: str | None = None
    how: Text


class Segment(Model):
    id: SegmentId
    title: Text
    target_seconds: Annotated[int, Field(gt=0)]
    requires: list[Item] = Field(default_factory=list)
    establishes: list[Item] = Field(default_factory=list)
    anchors: list[Ref] = Field(default_factory=list)
    callbacks: list[Callback] = Field(default_factory=list)
    setups: list[str | dict[str, str]] = Field(default_factory=list)


class Transition(Model):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    from_: SegmentId = Field(alias="from")
    to: SegmentId
    idea: Text


class OutlineV0(Model):
    format: Literal["outline/v0"]
    series: Slug
    episode: EpisodeId
    title: Text
    core_question: Text
    audience: Text
    written_by: str | None = None
    previously: list[str] = Field(default_factory=list)
    segments: Annotated[list[Segment], Field(min_length=1)]
    transitions: list[Transition] = Field(default_factory=list)


class Beat(Model):
    cue: Slug
    text: Text


class ScriptV0(Model):
    """A script written by hand in M1, with no anchors."""

    format: Literal["script/v0"]
    episode: EpisodeId
    segment: SegmentId
    voice: Text
    beats: Annotated[list[Beat], Field(min_length=1)]


class ScriptV1(Model):
    """A script whose front matter maps each cue to the anchors of its beat."""

    format: Literal["script/v1"]
    episode: EpisodeId
    segment: SegmentId
    voice: Text
    written_by: str | None = None
    anchors: dict[Slug, list[Ref]]
    beats: Annotated[list[Beat], Field(min_length=1)]

    @model_validator(mode="after")
    def every_cue_lists_its_anchors(self) -> Self:
        cues = [beat.cue for beat in self.beats]
        missing = [cue for cue in cues if cue not in self.anchors]
        extra = [cue for cue in self.anchors if cue not in cues]
        if missing or extra:
            raise ValueError(
                f"anchors must list every cue once: missing {missing}, unknown {extra}"
            )
        return self


class Entry(Model):
    cue: Slug
    visual: Text
    # A component's name, or "custom" for a visual that no component draws.
    component: Text
    region: Text


class StoryboardV0(Model):
    format: Literal["storyboard/v0"]
    episode: EpisodeId
    segment: SegmentId
    written_by: str | None = None
    entries: Annotated[list[Entry], Field(min_length=1)]

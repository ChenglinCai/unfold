"""What each step asks the model for. Code fills in the rest of each file.

These are the schemas that jobs send through structured output. The file
formats in `unfold.formats` add the fields that code knows, such as `format`,
the series, the episode, and `written_by`.
"""

from typing import Annotated

from pydantic import Field

from unfold.formats.episode import Entry, Segment, Transition
from unfold.formats.series import PlannedEpisode
from unfold.formats.sources import Model, Ref, Slug, Text


class PlanReply(Model):
    episodes: Annotated[list[PlannedEpisode], Field(min_length=1, max_length=8)]


class OutlineReply(Model):
    title: Text
    core_question: Text
    segments: Annotated[list[Segment], Field(min_length=2, max_length=4)]
    transitions: list[Transition] = Field(default_factory=list)


class DraftBeat(Model):
    cue: Slug
    text: Text
    anchors: list[Ref] = Field(default_factory=list)


class ScriptReply(Model):
    beats: Annotated[list[DraftBeat], Field(min_length=3, max_length=12)]


class StoryboardReply(Model):
    entries: Annotated[list[Entry], Field(min_length=1)]

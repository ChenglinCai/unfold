"""Schemas for a series: the user's request, and the plan that a job writes."""

from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from unfold.formats.sources import Model, Ref, Slug, Text

EpisodeId = Annotated[str, StringConstraints(pattern=r"^E\d{2}-[a-z0-9][a-z0-9-]*$")]


class SeriesV0(Model):
    """What the user asks for: the sources, the audience, and the limits."""

    format: Literal["series/v0"]
    id: Slug
    title: str | None = None
    audience: Text
    sources: Annotated[list[Text], Field(min_length=1)]
    episodes: Annotated[int, Field(ge=1)] = 1
    segments: Annotated[int, Field(ge=1)] = 2
    model: Text = "sonnet"


class PlannedEpisode(Model):
    id: EpisodeId
    title: Text
    core_question: Text
    concepts: Annotated[list[Slug], Field(min_length=1)]
    anchors: list[Ref] = Field(default_factory=list)


class SeriesPlanV0(Model):
    """The episodes that a series could hold, in teaching order."""

    format: Literal["series-plan/v0"]
    series: Slug
    written_by: str | None = None
    episodes: Annotated[list[PlannedEpisode], Field(min_length=1)]

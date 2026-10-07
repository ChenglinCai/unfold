"""The parameters of each component, and the names of the regions.

These schemas never import manim, so `unfold check` and the build graph can
validate scenes without loading it. `components.py` draws them.
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, TypeAdapter, model_validator

from unfold.formats.sources import Model
from unfold.formats.sources import Text as NonEmpty

# Raise this whenever a component draws differently, so saved scenes rebuild.
VERSION = "2"
REGION_NAMES = ("full", "plot", "top", "bottom", "left", "right")
Region = Literal["full", "plot", "top", "bottom", "left", "right"]


class TextCard(Model):
    component: Literal["text-card"]
    title: str = ""
    lines: Annotated[list[NonEmpty], Field(max_length=6)] = Field(default_factory=list)


class Equation(Model):
    component: Literal["equation"]
    tex: NonEmpty
    caption: str = ""


class BarChart(Model):
    component: Literal["bar-chart"]
    labels: Annotated[list[str], Field(min_length=1, max_length=12)]
    values: Annotated[list[float], Field(min_length=1, max_length=12)]
    title: str = ""
    highlight: int | None = None

    @model_validator(mode="after")
    def one_value_per_label(self) -> Self:
        if len(self.labels) != len(self.values):
            raise ValueError("a bar chart needs one value for each label")
        return self


# A pair of numbers. A two-item list, not a tuple, because the runner rejects
# the prefixItems keyword that Pydantic writes for tuples.
Pair = Annotated[list[float], Field(min_length=2, max_length=2)]


class ScatterPlot(Model):
    component: Literal["scatter-plot"]
    points: Annotated[list[Pair], Field(min_length=1, max_length=60)]
    groups: list[Annotated[int, Field(ge=0, le=4)]] = Field(default_factory=list)
    x_label: str = ""
    y_label: str = ""
    # An optional line, as its slope and intercept.
    line: Pair | None = None


class Event(Model):
    at: float
    label: str
    amount: float | None = None


class Timeline(Model):
    component: Literal["timeline"]
    start: float
    end: float
    events: Annotated[list[Event], Field(min_length=1, max_length=12)]

    @model_validator(mode="after")
    def runs_forward(self) -> Self:
        if self.end <= self.start:
            raise ValueError("a timeline must end after it starts")
        return self


class Custom(Model):
    """A visual that no component draws yet. It renders as a labeled card."""

    component: Literal["custom"]
    description: NonEmpty


Visual = Annotated[
    TextCard | Equation | BarChart | ScatterPlot | Timeline | Custom,
    Field(discriminator="component"),
]
NAMES = ("text-card", "equation", "bar-chart", "scatter-plot", "timeline", "custom")
_ADAPTER: TypeAdapter[Visual] = TypeAdapter(Visual)


class ComponentError(ValueError):
    """A component could not draw its parameters, such as TeX that fails."""


def parse(data: object) -> BaseModel:
    return _ADAPTER.validate_python(data)

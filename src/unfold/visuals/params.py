"""The parameters of each component, and the names of the regions.

These schemas never import manim, so `unfold check` and the build graph can
validate scenes without loading it. `components.py` draws them.
"""

from itertools import pairwise
from typing import Annotated, Literal, Self

from pydantic import BaseModel, Field, TypeAdapter, field_validator, model_validator

from unfold.formats.sources import Model, Slug
from unfold.formats.sources import Text as NonEmpty

# Raise this whenever a component draws differently, so saved scenes rebuild.
VERSION = "4"
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


class PlanePoint(Model):
    label: str = ""
    radius: Annotated[float, Field(ge=0, le=100)]
    # Degrees, counterclockwise from the positive real axis.
    angle: float
    guides: bool = False
    real_label: str = ""
    imag_label: str = ""


class Turn(Model):
    """An arc with an arrow tip, from one angle to another, in degrees."""

    start: float
    end: float
    label: str = ""

    @model_validator(mode="after")
    def sweeps(self) -> Self:
        if self.end == self.start:
            raise ValueError("a turn must sweep some angle")
        return self


class ComplexPlane(Model):
    component: Literal["complex-plane"]
    points: Annotated[list[PlanePoint], Field(min_length=1, max_length=6)]
    unit_circle: bool = True
    rays: bool = True
    turn: Turn | None = None


class Box(Model):
    id: Slug
    label: NonEmpty


class Link(Model):
    from_: Slug = Field(alias="from")
    to: Slug
    label: str = ""


class FlowDiagram(Model):
    """A few labeled boxes in a row or a column, joined by arrows."""

    component: Literal["flow-diagram"]
    boxes: Annotated[list[Box], Field(min_length=2, max_length=6)]
    links: Annotated[list[Link], Field(max_length=10)] = Field(default_factory=list)
    direction: Literal["right", "down"] = "right"
    highlight: Slug | None = None

    @model_validator(mode="after")
    def links_join_boxes(self) -> Self:
        ids = [box.id for box in self.boxes]
        if len(set(ids)) != len(ids):
            raise ValueError("box ids must be unique")
        for link in self.links:
            for end in (link.from_, link.to):
                if end not in ids:
                    raise ValueError(f"a link names no box called {end}")
            if link.from_ == link.to:
                raise ValueError("a link must join two different boxes")
        if self.highlight is not None and self.highlight not in ids:
            raise ValueError("highlight must name a box")
        return self


class Histogram(Model):
    """Counts in touching bins, with an optional mean, spread, and bell curve."""

    component: Literal["histogram"]
    edges: Annotated[list[float], Field(min_length=2, max_length=41)]
    counts: list[Annotated[float, Field(ge=0)]]
    labels: list[str] = Field(default_factory=list)
    mean: float | None = None
    # The standard deviation.
    spread: Annotated[float, Field(gt=0)] | None = None
    curve: bool = False
    highlight: int | None = None
    title: str = ""
    x_label: str = ""

    @model_validator(mode="after")
    def bins_agree(self) -> Self:
        bins = len(self.edges) - 1
        if any(right <= left for left, right in pairwise(self.edges)):
            raise ValueError("a histogram's edges must increase")
        if len(self.counts) != bins:
            raise ValueError("a histogram needs one count for each bin")
        if self.labels and len(self.labels) != bins:
            raise ValueError("a histogram needs one label for each bin, or none")
        if self.curve and (self.mean is None or self.spread is None):
            raise ValueError("a bell curve needs a mean and a spread")
        if self.highlight is not None and not 0 <= self.highlight < bins:
            raise ValueError("highlight must name a bin, counting from 0")
        return self


class Flow(Model):
    at: Annotated[float, Field(ge=0, le=100)]
    amount: float

    @field_validator("amount")
    @classmethod
    def not_zero(cls, amount: float) -> float:
        if amount == 0:
            raise ValueError("a flow's amount cannot be zero")
        return amount


class PresentValue(Model):
    """Cash flows, and what each is worth today. Code computes every present value."""

    component: Literal["present-value"]
    # Percent per period, compounded once per period.
    rate: Annotated[float, Field(ge=0, le=100)]
    flows: Annotated[list[Flow], Field(min_length=1, max_length=24)]
    total: bool = True
    prefix: Annotated[str, Field(max_length=3)] = ""
    title: str = ""

    @model_validator(mode="after")
    def one_flow_per_time(self) -> Self:
        times = [flow.at for flow in self.flows]
        if len(set(times)) != len(times):
            raise ValueError("each flow needs its own time")
        return self


class Custom(Model):
    """A visual that no component draws yet. It renders as a labeled card."""

    component: Literal["custom"]
    description: NonEmpty


Visual = Annotated[
    TextCard
    | Equation
    | BarChart
    | ScatterPlot
    | Timeline
    | ComplexPlane
    | Histogram
    | PresentValue
    | FlowDiagram
    | Custom,
    Field(discriminator="component"),
]
NAMES = (
    "text-card",
    "equation",
    "bar-chart",
    "scatter-plot",
    "timeline",
    "complex-plane",
    "histogram",
    "present-value",
    "flow-diagram",
    "custom",
)
_ADAPTER: TypeAdapter[Visual] = TypeAdapter(Visual)


class ComponentError(ValueError):
    """A component could not draw its parameters, such as TeX that fails."""


def parse(data: object) -> BaseModel:
    return _ADAPTER.validate_python(data)

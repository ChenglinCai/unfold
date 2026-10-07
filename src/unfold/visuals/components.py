"""Components: tested parts that draw one kind of visual from typed parameters.

The model picks a component and fills in its parameters, and a Pydantic schema
checks them. `build()` draws the visual and fits it inside a named region. A
drawing only ever shrinks to fit, so the layout check can catch tiny text.
"""

import math
import textwrap
from typing import Annotated, Literal, Self

from manim import (
    DOWN,
    LEFT,
    UP,
    Arrow,
    Axes,
    DashedVMobject,
    Dot,
    Line,
    MathTex,
    NumberLine,
    Rectangle,
    RoundedRectangle,
    SingleStringMathTex,
    Text,
    VGroup,
)
from pydantic import BaseModel, Field, TypeAdapter, model_validator

from unfold.formats.sources import Model
from unfold.formats.sources import Text as NonEmpty
from unfold.visuals import theme
from unfold.visuals.layout import REGIONS

# Raise this whenever a component draws differently, so saved scenes rebuild.
VERSION = "1"
PAD = 0.92
WRAP = 42


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


class ScatterPlot(Model):
    component: Literal["scatter-plot"]
    points: Annotated[list[tuple[float, float]], Field(min_length=1, max_length=60)]
    groups: list[Annotated[int, Field(ge=0, le=4)]] = Field(default_factory=list)
    x_label: str = ""
    y_label: str = ""
    # An optional line, as its slope and intercept.
    line: tuple[float, float] | None = None


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


def build(visual: BaseModel, region: str) -> tuple[VGroup, float | None]:
    """Draw a visual inside a region, and return it with its smallest text size."""
    name = str(getattr(visual, "component", "visual"))
    try:
        box = REGIONS[region]
        drawing = _DRAW[type(visual)](visual, box.width * PAD, box.height * PAD)
    except Exception as error:  # manim and LaTeX fail in many ways
        raise ComponentError(f"{name}: {str(error).splitlines()[0]}") from error
    scale = min(1.0, box.width * PAD / max(drawing.width, 1e-6))
    scale = min(scale, box.height * PAD / max(drawing.height, 1e-6))
    drawing.scale(scale)
    drawing.move_to([*box.center, 0])
    sizes = [
        float(m.font_size)
        for m in drawing.get_family()
        if isinstance(m, Text | SingleStringMathTex)
    ]
    return drawing, min(sizes) if sizes else None


def _text(words: str, size: int = theme.BODY_SIZE, color: str = theme.TEXT) -> Text:
    return Text(words, font_size=size, color=color)


def _wrapped(words: str, size: int = theme.BODY_SIZE) -> VGroup:
    lines = textwrap.wrap(words, WRAP) or [words]
    return VGroup(*[_text(line, size) for line in lines]).arrange(
        DOWN, aligned_edge=LEFT, buff=0.15
    )


def _text_card(card: TextCard, width: float, height: float) -> VGroup:
    parts: list[VGroup | Text] = []
    if card.title:
        parts.append(_text(card.title, theme.TITLE_SIZE, theme.YELLOW))
    parts += [_wrapped(line) for line in card.lines]
    return VGroup(*parts).arrange(DOWN, aligned_edge=LEFT, buff=0.35)


def _equation(equation: Equation, width: float, height: float) -> VGroup:
    parts: list[MathTex | Text] = [
        MathTex(equation.tex, font_size=72, color=theme.TEXT)
    ]
    if equation.caption:
        parts.append(_text(equation.caption, theme.LABEL_SIZE, theme.MUTED))
    return VGroup(*parts).arrange(DOWN, buff=0.5)


def _number(value: float) -> str:
    return f"{value:,.0f}" if abs(value) >= 1000 else f"{value:g}"


def _bar_chart(chart: BarChart, width: float, height: float) -> VGroup:
    room = height - 1.0 - (0.7 if chart.title else 0)
    high = max(max(chart.values), 0)
    low = min(min(chart.values), 0)
    scale = room / max(high - low, 1e-9)
    slot = width / len(chart.values)
    bars, labels, values = VGroup(), VGroup(), VGroup()
    for index, (label, value) in enumerate(
        zip(chart.labels, chart.values, strict=True)
    ):
        color = theme.YELLOW if index == chart.highlight else theme.BLUE
        bar = Rectangle(
            width=slot * 0.6,
            height=max(abs(value) * scale, 0.02),
            fill_color=color,
            fill_opacity=0.9,
            stroke_width=0,
        )
        x = -width / 2 + slot * (index + 0.5)
        bar.move_to((x, 0, 0), aligned_edge=DOWN if value >= 0 else UP)
        bars.add(bar)
        name = _text(label, theme.LABEL_SIZE, theme.MUTED)
        labels.add(name.move_to((x, low * scale - 0.35, 0)))
        tip = bar.get_top() if value >= 0 else bar.get_bottom()
        offset = 0.25 if value >= 0 else -0.25
        values.add(_text(_number(value), theme.LABEL_SIZE).move_to(tip + UP * offset))
    axis = Line((-width / 2, 0, 0), (width / 2, 0, 0), color=theme.MUTED)
    group = VGroup(axis, bars, labels, values)
    if chart.title:
        group.add(_text(chart.title, theme.BODY_SIZE).next_to(group, UP, buff=0.3))
    return group


def _step(span: float) -> float:
    raw = span / 5 if span > 0 else 1
    power = 10 ** math.floor(math.log10(raw))
    return next(power * m for m in (1, 2, 5, 10) if power * m >= raw)


def _padded(values: list[float]) -> list[float]:
    low, high = min(values), max(values)
    pad = (high - low) * 0.1 or 1
    return [low - pad, high + pad, _step(high - low + 2 * pad)]


def _scatter_plot(plot: ScatterPlot, width: float, height: float) -> VGroup:
    xs = [p[0] for p in plot.points]
    ys = [p[1] for p in plot.points]
    x_range, y_range = _padded(xs), _padded(ys)
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=width - 0.4,
        y_length=height - 1.3,
        tips=False,
        axis_config={"include_numbers": False, "color": theme.MUTED},
    )
    groups = plot.groups or [0] * len(plot.points)
    dots = VGroup(
        *[
            Dot(
                axes.c2p(x, y),
                radius=0.09,
                color=theme.PALETTE[groups[i % len(groups)]],
            )
            for i, (x, y) in enumerate(plot.points)
        ]
    )
    group = VGroup(axes, dots)
    if plot.line is not None:
        slope, intercept = plot.line
        line = axes.plot(lambda x: slope * x + intercept, x_range=x_range[:2])
        group.add(line.set_color(theme.YELLOW))
    if plot.x_label:
        group.add(
            _text(plot.x_label, theme.LABEL_SIZE, theme.MUTED).next_to(axes, DOWN)
        )
    if plot.y_label:
        group.add(_text(plot.y_label, theme.LABEL_SIZE, theme.MUTED).next_to(axes, UP))
    return group


def _timeline(timeline: Timeline, width: float, height: float) -> VGroup:
    span = timeline.end - timeline.start
    line = NumberLine(
        x_range=[timeline.start, timeline.end, _step(span)],
        length=width - 1.2,
        include_numbers=False,
        color=theme.MUTED,
    )
    group = VGroup(line)
    biggest = max((abs(e.amount) for e in timeline.events if e.amount), default=1)
    reach = max(min(1.6, height / 2 - 0.9), 0.4)
    for event in timeline.events:
        point = line.n2p(event.at)
        group.add(Dot(point, radius=0.1, color=theme.YELLOW))
        group.add(
            _text(event.label, theme.LABEL_SIZE, theme.MUTED).next_to(point, DOWN)
        )
        if event.amount:
            length = 0.3 + reach * abs(event.amount) / biggest
            direction = UP if event.amount > 0 else DOWN
            color = theme.GREEN if event.amount > 0 else theme.RED
            start = point + direction * (0.55 if event.amount < 0 else 0.15)
            arrow = Arrow(start, start + direction * length, buff=0, color=color)
            sign = "+" if event.amount > 0 else "-"
            amount = _text(
                f"{sign}{_number(abs(event.amount))}", theme.LABEL_SIZE, color
            )
            group.add(arrow, amount.next_to(arrow, direction, buff=0.1))
    return group


def _custom(custom: Custom, width: float, height: float) -> VGroup:
    words = VGroup(
        _text("Custom visual, to review", theme.LABEL_SIZE, theme.YELLOW),
        _wrapped(custom.description),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
    frame = RoundedRectangle(
        corner_radius=0.2,
        width=words.width + 0.8,
        height=words.height + 0.8,
        stroke_color=theme.MUTED,
    )
    return VGroup(DashedVMobject(frame, num_dashes=40), words.move_to(frame))


_DRAW = {
    TextCard: _text_card,
    Equation: _equation,
    BarChart: _bar_chart,
    ScatterPlot: _scatter_plot,
    Timeline: _timeline,
    Custom: _custom,
}

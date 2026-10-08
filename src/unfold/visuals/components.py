"""Components: tested parts that draw one kind of visual from typed parameters.

The model picks a component and fills in its parameters, and a Pydantic schema
checks them. `build()` draws the visual and fits it inside a named region. A
drawing only ever shrinks to fit, so the layout check can catch tiny text.
"""

import math
import textwrap
from itertools import combinations, pairwise

from manim import (
    DOWN,
    LEFT,
    RIGHT,
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
    Square,
    Text,
    VGroup,
)
from pydantic import BaseModel

from unfold.visuals import theme
from unfold.visuals.finance import present_value, shown
from unfold.visuals.layout import REGIONS, box_of
from unfold.visuals.params import (
    NAMES,
    BarChart,
    ComponentError,
    Custom,
    Equation,
    PresentValue,
    ScatterPlot,
    TextCard,
    Timeline,
    parse,
)

__all__ = ["NAMES", "ComponentError", "build", "crowded", "parse"]

PAD = 0.92
WRAP = 42
# A wide letter's share of the frame at the body size, with room for wider fonts.
CHAR_WIDTH = 0.2


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


def crowded(drawing: VGroup) -> int:
    """How many pairs of labels in a drawing overlap each other."""
    texts = [
        m for m in drawing.get_family() if isinstance(m, Text) or type(m) is MathTex
    ]
    boxes = [box_of(text) for text in texts]
    return sum(1 for a, b in combinations(boxes, 2) if a.overlaps(b))


def _text(words: str, size: int = theme.BODY_SIZE, color: str = theme.TEXT) -> Text:
    return Text(words, font_size=size, color=color)


def _wrapped(words: str, width: float, size: int = theme.BODY_SIZE) -> VGroup:
    """Wrap words to the width at hand, so fonts that run wide still fit."""
    lines = textwrap.wrap(words, max(12, min(WRAP, int(width / CHAR_WIDTH)))) or [words]
    return VGroup(*[_text(line, size) for line in lines]).arrange(
        DOWN, aligned_edge=LEFT, buff=0.15
    )


def _text_card(card: TextCard, width: float, height: float) -> VGroup:
    parts: list[VGroup | Text] = []
    if card.title:
        parts.append(_text(card.title, theme.TITLE_SIZE, theme.YELLOW))
    parts += [_wrapped(line, width) for line in card.lines]
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
        room = slot * 0.92
        lines = textwrap.wrap(label, max(6, int(room / 0.15)))[:2] or [label]
        name = VGroup(*[_text(line, theme.LABEL_SIZE, theme.MUTED) for line in lines])
        name.arrange(DOWN, buff=0.08)
        if name.width > room:
            name.scale(room / name.width)
        labels.add(name.move_to((x, low * scale - 0.15, 0), aligned_edge=UP))
        tip = bar.get_top() if value >= 0 else bar.get_bottom()
        offset = 0.25 if value >= 0 else -0.25
        number = _text(_number(value), theme.LABEL_SIZE)
        if number.width > room:
            number.scale(room / number.width)
        values.add(number.move_to(tip + UP * offset))
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
    # Labels that would touch a kept neighbor stay out, so a crowded line stays legible.
    edges = {"label": -math.inf, "amount": -math.inf}

    def fits(text: Text, kind: str) -> bool:
        if text.get_left()[0] < edges[kind] + 0.15:
            return False
        edges[kind] = text.get_right()[0]
        return True

    for event in sorted(timeline.events, key=lambda e: e.at):
        point = line.n2p(event.at)
        group.add(Dot(point, radius=0.1, color=theme.YELLOW))
        label = _text(event.label, theme.LABEL_SIZE, theme.MUTED).next_to(point, DOWN)
        if fits(label, "label"):
            group.add(label)
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
            group.add(arrow)
            if fits(amount.next_to(arrow, direction, buff=0.1), "amount"):
                group.add(amount)
    return group


class Row:
    """Keeps labels in one row apart: a label that would touch a kept one drops out."""

    def __init__(self) -> None:
        self.edge = -math.inf

    def fits(self, text: Text) -> bool:
        if text.get_left()[0] < self.edge + 0.15:
            return False
        self.edge = text.get_right()[0]
        return True


def _legend(rate: float) -> VGroup:
    paid = Square(0.3, stroke_color=theme.MUTED, stroke_width=2)
    today = Square(0.3, fill_color=theme.GREEN, fill_opacity=0.85, stroke_width=0)
    words = (
        _text("when paid", theme.LABEL_SIZE, theme.MUTED),
        _text(f"worth today at {rate:g}%", theme.LABEL_SIZE, theme.MUTED),
    )
    return VGroup(
        VGroup(paid, words[0]).arrange(RIGHT, buff=0.15),
        VGroup(today, words[1]).arrange(RIGHT, buff=0.15),
    ).arrange(RIGHT, buff=0.6)


def _present_value(chart: PresentValue, width: float, height: float) -> VGroup:
    """An outline bar for each amount when paid, and a filled bar for its worth today."""
    flows = sorted(chart.flows, key=lambda flow: flow.at)
    worth = [present_value(f.amount, chart.rate, f.at) for f in flows]
    head = VGroup(*([_text(chart.title, theme.BODY_SIZE)] if chart.title else []))
    if chart.total:
        words = f"Worth today in all: {shown(sum(worth), chart.prefix)}"
        total = _text(words, theme.BODY_SIZE, theme.YELLOW)
        total.name = "total"
        head.add(total)
    head.add(_legend(chart.rate)).arrange(DOWN, buff=0.2)
    paying = any(f.amount < 0 for f in flows)
    # Rows of labels: worth above the bars, worth below paid-out bars, then times.
    room = max(height - head.height - 0.35 - 0.45 * (3 if paying else 2), 0.8)
    high = max(max(f.amount for f in flows), 0)
    low = min(min(f.amount for f in flows), 0)
    scale = room / (high - low)
    end = max(flows[-1].at, 1)
    times = [f.at for f in flows]
    gap = min([b - a for a, b in pairwise(times)] or [end])
    usable = width - 1.2
    bar = min(0.6 * usable * gap / end, 0.9)
    axis = Line((-width / 2, 0, 0), (width / 2, 0, 0), color=theme.MUTED)
    axis.name = "axis"
    bars, labels, whens = VGroup(), VGroup(), VGroup()
    rows = {"up": Row(), "down": Row(), "time": Row()}
    for flow, value in zip(flows, worth, strict=True):
        x = -usable / 2 + usable * flow.at / end
        up = flow.amount > 0
        side, color = (UP, theme.GREEN) if up else (DOWN, theme.RED)
        paid = Rectangle(
            width=bar,
            height=abs(flow.amount) * scale,
            stroke_color=theme.MUTED,
            stroke_width=2,
        )
        today = Rectangle(
            width=bar,
            height=max(abs(value) * scale, 0.02),
            fill_color=color,
            fill_opacity=0.85,
            stroke_width=0,
        )
        for part, name in ((paid, "paid"), (today, "today")):
            part.move_to((x, 0, 0), aligned_edge=DOWN if up else UP)
            part.name = name
            bars.add(part)
        label = _text(shown(value, chart.prefix), theme.LABEL_SIZE, color)
        label.name = "worth"
        if rows["up" if up else "down"].fits(label.next_to(paid, side, buff=0.1)):
            labels.add(label)
    floor = min([low * scale, *(m.get_bottom()[1] for m in labels)]) - 0.3
    for flow in flows:
        x = -usable / 2 + usable * flow.at / end
        when = _text(f"{flow.at:g}", theme.LABEL_SIZE, theme.MUTED).move_to(
            (x, floor, 0)
        )
        if rows["time"].fits(when):
            whens.add(when)
    body = VGroup(axis, bars, labels, whens)
    return VGroup(head.next_to(body, UP, buff=0.35), body)


def _custom(custom: Custom, width: float, height: float) -> VGroup:
    words = VGroup(
        _text("Custom visual, to review", theme.LABEL_SIZE, theme.YELLOW),
        _wrapped(custom.description, width - 0.8),
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
    PresentValue: _present_value,
    Custom: _custom,
}

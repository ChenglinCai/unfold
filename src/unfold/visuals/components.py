"""Components: tested parts that draw one kind of visual from typed parameters.

The model picks a component and fills in its parameters, and a Pydantic schema
checks them. `build()` draws the visual and fits it inside a named region. A
drawing only ever shrinks to fit, so the layout check can catch tiny text.
"""

import math
import textwrap
from collections.abc import Iterable
from itertools import combinations, pairwise

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arc,
    ArcBetweenPoints,
    Arrow,
    Axes,
    Circle,
    DashedLine,
    DashedVMobject,
    Dot,
    DoubleArrow,
    Line,
    MathTex,
    Mobject,
    NumberLine,
    NumberPlane,
    Rectangle,
    RoundedRectangle,
    SingleStringMathTex,
    Square,
    Text,
    VGroup,
    VMobject,
)
from pydantic import BaseModel

from unfold.visuals import theme
from unfold.visuals.finance import present_value, shown
from unfold.visuals.layout import REGIONS, box_of
from unfold.visuals.params import (
    NAMES,
    BarChart,
    ComplexPlane,
    ComponentError,
    Custom,
    Equation,
    FlowDiagram,
    Histogram,
    Link,
    PlanePoint,
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


def _keep_apart(labels: list[Text], taken: Iterable[Mobject] = ()) -> VGroup:
    """Labels in priority order, leaving out any that would overlap a kept one."""
    blocked = [box_of(mobject) for mobject in taken]
    kept: list[Text] = []
    for label in labels:
        if not any(box_of(label).overlaps(other) for other in blocked):
            kept.append(label)
            blocked.append(box_of(label))
    return VGroup(*kept)


def _named[M: Mobject](mobject: M, name: str) -> M:
    mobject.name = name
    return mobject


def _end_tip(path: VMobject, color: str) -> Arrow:
    """A short arrow at a path's end, along its tangent.

    manim's own `add_tip` rescales an arc to fit the tip, and that blows up when
    the arc's ends meet, as in a full turn.
    """
    end = path.get_end()
    toward = end - path.point_from_proportion(0.97)
    tangent = toward / max(float(np.linalg.norm(toward)), 1e-9)
    return Arrow(
        end - tangent * 0.2,
        end,
        buff=0,
        color=color,
        max_tip_length_to_length_ratio=0.75,
    )


def _same_ray(point: PlanePoint, other: PlanePoint) -> bool:
    """Whether another point sits farther out at nearly the same angle."""
    turn = (other.angle - point.angle) % 360
    return other.radius > point.radius and min(turn, 360 - turn) < 5


def _complex_plane(plane: ComplexPlane, width: float, height: float) -> VGroup:
    """Points by radius and angle, with an optional unit circle, guides, and turn."""
    need = 1.2 * max(1.0, *(point.radius for point in plane.points))
    step = 0.5 if need <= 2 else 1.0 if need <= 6 else _step(need)
    reach = step * math.ceil(need / step)
    side = min(width, height) - 0.9  # room for the labels around the plane
    grid = NumberPlane(
        x_range=[-reach, reach, step],
        y_range=[-reach, reach, step],
        x_length=side,
        y_length=side,
        background_line_style={
            "stroke_color": theme.MUTED,
            "stroke_width": 1,
            "stroke_opacity": 0.3,
        },
        axis_config={"stroke_color": theme.MUTED},
    )
    grid.name = "plane"
    origin, unit = grid.c2p(0, 0), side / (2 * reach)
    group, labels = VGroup(grid), []
    if plane.unit_circle:
        circle = Circle(radius=unit, color=theme.BLUE, stroke_width=3).move_to(origin)
        circle.name = "unit-circle"
        group.add(circle)
    for point in plane.points:
        theta = math.radians(point.angle)
        direction = np.array([math.cos(theta), math.sin(theta), 0.0])
        spot = origin + direction * point.radius * unit
        if plane.rays and point.radius > 0:
            group.add(_named(Line(origin, spot, color=theme.YELLOW), "ray"))
        group.add(_named(Dot(spot, radius=0.08, color=theme.YELLOW), "point"))
        if point.label:
            # A point with another farther out on its ray labels beside the ray.
            shaded = any(_same_ray(point, other) for other in plane.points)
            side = np.array([-direction[1], direction[0], 0.0]) if shaded else direction
            text = _named(_text(point.label, theme.LABEL_SIZE), "point-label")
            labels.append(text.next_to(spot, side, buff=0.15))
        if not point.guides:
            continue
        feet = (
            np.array([spot[0], origin[1], 0.0]),
            np.array([origin[0], spot[1], 0.0]),
        )
        for foot in feet:
            if np.linalg.norm(foot - spot) > 1e-6:
                guide = DashedLine(spot, foot, dash_length=0.1, color=theme.MUTED)
                group.add(_named(guide, "guide"))
        sides = (
            DOWN if spot[1] >= origin[1] else UP,
            LEFT if spot[0] >= origin[0] else RIGHT,
        )
        for words, foot, side_of in zip(
            (point.real_label, point.imag_label), feet, sides, strict=True
        ):
            if words:
                text = _named(
                    _text(words, theme.LABEL_SIZE, theme.MUTED), "guide-label"
                )
                labels.append(text.next_to(foot, side_of, buff=0.12))
    if plane.turn is not None:
        turn, radius = plane.turn, 0.45 * unit
        arc = Arc(
            radius=radius,
            start_angle=math.radians(turn.start),
            angle=math.radians(turn.end - turn.start),
            arc_center=origin,
            color=theme.GREEN,
        )
        sweep = turn.end - turn.start
        tip = _end_tip(arc, theme.GREEN)
        group.add(_named(arc, "turn"), _named(tip, "turn-tip"))
        if turn.label:
            words = _text(turn.label, theme.LABEL_SIZE, theme.GREEN)
            text = _named(words, "turn-label")
            if abs(sweep) >= 300:  # a loop leaves no gap, so the label goes below
                labels.append(text.next_to(grid, DOWN, buff=0.15))
            else:
                middle = math.radians((turn.start + turn.end) / 2)
                out = np.array([math.cos(middle), math.sin(middle), 0.0])
                labels.append(text.move_to(origin + out * (radius + 0.3)))
    for words, end, side_of in (("Re", (reach, 0), RIGHT), ("Im", (0, reach), UP)):
        text = _text(words, theme.LABEL_SIZE, theme.MUTED)
        labels.append(text.next_to(grid.c2p(*end), side_of, buff=0.1))
    return group.add(_keep_apart(labels))


def _box_label(words: str, width: float) -> VGroup:
    lines = textwrap.wrap(words, max(6, int((width - 0.3) / 0.16))) or [words]
    texts = [_named(_text(line, theme.LABEL_SIZE), "box-label") for line in lines]
    return VGroup(*texts).arrange(DOWN, buff=0.08)


def _flow_diagram(chart: FlowDiagram, width: float, height: float) -> VGroup:
    """Boxes in a row or a column. Neighbors join straight, and other links curve."""
    across, count = chart.direction == "right", len(chart.boxes)
    order = {box.id: index for index, box in enumerate(chart.boxes)}
    pairs = {(link.from_, link.to) for link in chart.links}

    def straight(link: Link) -> bool:
        neighbors = abs(order[link.to] - order[link.from_]) == 1
        return neighbors and (link.to, link.from_) not in pairs

    # In a row, a straight link's label sits between two boxes, so the gap fits it.
    widest = [
        _text(link.label, theme.LABEL_SIZE).width
        for link in chart.links
        if link.label and straight(link)
    ]
    gap = max([0.9, *(width + 0.4 for width in widest)]) if across else 0.6
    row = min((width - gap * (count - 1)) / count, 3.2)
    box_w = row if across else min(width * 0.5, 4.0)
    words = [_box_label(box.label, box_w) for box in chart.boxes]
    nominal = 1.0 if across else min((height - gap * (count - 1)) / count, 1.0)
    box_h = max(nominal, *(text.height + 0.3 for text in words))
    frames: dict[str, RoundedRectangle] = {}
    group = VGroup()
    for index, (box, text) in enumerate(zip(chart.boxes, words, strict=True)):
        step = index - (count - 1) / 2
        center = (
            (step * (box_w + gap), 0, 0) if across else (0, -step * (box_h + gap), 0)
        )
        color = theme.YELLOW if box.id == chart.highlight else theme.BLUE
        frame = RoundedRectangle(
            corner_radius=0.15, width=box_w, height=box_h, stroke_color=color
        )
        frames[box.id] = _named(frame.move_to(center), "box")
        group.add(frame, text.move_to(center))
    labels = []
    for link in chart.links:
        start_box, end_box = frames[link.from_], frames[link.to]
        forward = order[link.to] > order[link.from_]
        if straight(link):
            ends = ("get_right", "get_left") if across else ("get_bottom", "get_top")
            first, last = ends if forward else ends[::-1]
            start, end = getattr(start_box, first)(), getattr(end_box, last)()
            path: VMobject = Arrow(start, end, buff=0.08, color=theme.MUTED)
            group.add(_named(path, "link"))
            side = UP if across else RIGHT
        else:
            # Forward links curve on one side and backward links on the other, so
            # opposite links stay apart. A negative angle bends right of travel.
            if across:
                side, name = (UP, "get_top") if forward else (DOWN, "get_bottom")
            else:
                side, name = (LEFT, "get_left") if forward else (RIGHT, "get_right")
            start, end = getattr(start_box, name)(), getattr(end_box, name)()
            chord = float(np.linalg.norm(end - start))
            path = ArcBetweenPoints(
                start, end, angle=-4 * math.atan(1.4 / chord), color=theme.MUTED
            )
            group.add(
                _named(path, "link"), _named(_end_tip(path, theme.MUTED), "link-tip")
            )
        if link.label:
            text = _named(
                _text(link.label, theme.LABEL_SIZE, theme.MUTED), "link-label"
            )
            labels.append(text.next_to(path.point_from_proportion(0.5), side, buff=0.1))
    taken = [line for text in words for line in text]
    return group.add(_keep_apart(labels, taken))


def _histogram(chart: Histogram, width: float, height: float) -> VGroup:
    """Touching bars, with an optional mean line, spread arrow, and bell curve."""
    low, high = chart.edges[0], chart.edges[-1]
    usable = width - 0.6

    def x_of(value: float) -> float:
        return -usable / 2 + usable * (value - low) / (high - low)

    bins = list(pairwise(chart.edges))
    area = sum(c * (b - a) for c, (a, b) in zip(chart.counts, bins, strict=True))
    mean, spread = chart.mean, chart.spread
    peak = area / (spread * math.sqrt(2 * math.pi)) if chart.curve and spread else 0.0
    top = max(*chart.counts, peak, 1e-9)
    head = VGroup(*([_text(chart.title, theme.BODY_SIZE)] if chart.title else []))
    below = 0.45 + (0.45 if chart.x_label else 0)
    scale = max(height - head.height - 0.3 - 0.5 - below, 0.8) / top
    axis = _named(
        Line((-width / 2, 0, 0), (width / 2, 0, 0), color=theme.MUTED), "axis"
    )
    body, row = VGroup(axis), Row()
    for index, (count, (left, right)) in enumerate(
        zip(chart.counts, bins, strict=True)
    ):
        bar = Rectangle(
            width=x_of(right) - x_of(left),
            height=max(count * scale, 0.001),
            fill_color=theme.YELLOW if index == chart.highlight else theme.BLUE,
            fill_opacity=0.85,
            stroke_color=theme.BACKGROUND,
            stroke_width=2,
        )
        middle = (x_of(left) + x_of(right)) / 2
        body.add(_named(bar.move_to((middle, 0, 0), aligned_edge=DOWN), "bar"))
        if chart.labels:
            text = _text(chart.labels[index], theme.LABEL_SIZE, theme.MUTED)
            if row.fits(_named(text, "bin-label").move_to((middle, -0.3, 0))):
                body.add(text)
    for edge in [] if chart.labels else chart.edges:
        text = _text(f"{edge:g}", theme.LABEL_SIZE, theme.MUTED)
        if row.fits(_named(text, "edge-label").move_to((x_of(edge), -0.3, 0))):
            body.add(text)
    if chart.x_label:
        body.add(
            _text(chart.x_label, theme.LABEL_SIZE, theme.MUTED).move_to((0, -0.75, 0))
        )
    labels = []
    if peak and mean is not None and spread:

        def density(value: float) -> float:
            return peak * math.exp(-0.5 * ((value - mean) / spread) ** 2)

        dots = [
            np.array([x_of(v), density(v) * scale, 0.0])
            for v in np.linspace(low, high, 81)
        ]
        curve = VMobject(color=theme.PURPLE, stroke_width=4).set_points_smoothly(dots)
        body.add(_named(curve, "curve"))
    if mean is not None:
        x = x_of(mean)
        line = DashedLine(
            (x, 0, 0), (x, top * scale + 0.15, 0), dash_length=0.1, color=theme.TEXT
        )
        body.add(_named(line, "mean"))
        text = _named(_text(f"mean {mean:g}", theme.LABEL_SIZE), "mean-label")
        labels.append(text.next_to(line, UP, buff=0.1))
        if spread:
            # At one spread from the mean, a bell curve stands at e^(-1/2) of its peak.
            level = (peak * math.exp(-0.5) if peak else 0.6 * max(chart.counts)) * scale
            ends = (x_of(max(low, mean - spread)), x_of(min(high, mean + spread)))
            arrow = DoubleArrow(
                (ends[0], level, 0),
                (ends[1], level, 0),
                buff=0,
                color=theme.GREEN,
                tip_length=0.15,
            )
            body.add(_named(arrow, "spread"))
            text = _text(f"spread {spread:g}", theme.LABEL_SIZE, theme.GREEN)
            # The label joins the mean's, above the bars, where nothing crosses it.
            labels.append(
                _named(text, "spread-label").next_to(labels[0], RIGHT, buff=0.4)
            )
    body.add(_keep_apart(labels))
    return VGroup(head.next_to(body, UP, buff=0.3), body) if chart.title else body


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
    ComplexPlane: _complex_plane,
    Histogram: _histogram,
    PresentValue: _present_value,
    FlowDiagram: _flow_diagram,
    Custom: _custom,
}

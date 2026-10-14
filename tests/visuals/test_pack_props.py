"""Property tests: each new component, drawn with random valid parameters.

Hypothesis makes up the parameters. Every drawing must fit its region and keep
its labels apart, whatever the inputs.
"""

import math
from typing import Any

import numpy as np
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from manim import Axes, Text, VGroup

from unfold.visuals.components import build, crowded, parse
from unfold.visuals.finance import present_value, shown
from unfold.visuals.layout import REGIONS, box_of
from unfold.visuals.neighbors import tied

FAST = settings(max_examples=25, deadline=None)
regions = st.sampled_from(["full", "plot", "left", "right"])
labels = st.sampled_from(
    ["", "z", "pays", "train", "same question", "Gas station owner"]
)


def drawn(visual: dict[str, Any], region: str) -> VGroup:
    drawing, _ = build(parse(visual), region)
    assert crowded(drawing) == 0
    assert REGIONS[region].contains(box_of(drawing))
    return drawing


@st.composite
def present_values(draw: st.DrawFn) -> dict[str, Any]:
    times = draw(st.lists(st.integers(0, 40), min_size=1, max_size=24, unique=True))
    amount = st.floats(-1e6, 1e6).filter(lambda a: abs(a) >= 1)
    amounts = draw(st.lists(amount, min_size=len(times), max_size=len(times)))
    flows = [{"at": t, "amount": a} for t, a in zip(times, amounts, strict=True)]
    rate = draw(st.floats(0, 100))
    return {"component": "present-value", "rate": rate, "flows": flows, "prefix": "$"}


@st.composite
def complex_planes(draw: st.DrawFn) -> dict[str, Any]:
    point = st.fixed_dictionaries(
        {
            "label": labels,
            "radius": st.floats(0, 100),
            "angle": st.floats(-720, 720),
            "guides": st.booleans(),
            "real_label": st.sampled_from(["", "cos x", "a"]),
            "imag_label": st.sampled_from(["", "sin x", "b"]),
        }
    )
    visual = {
        "component": "complex-plane",
        "points": draw(st.lists(point, min_size=1, max_size=6)),
    }
    start, end = draw(st.floats(-360, 360)), draw(st.floats(-720, 720))
    if draw(st.booleans()) and start != end:
        visual["turn"] = {"start": start, "end": end, "label": draw(labels)}
    return visual


@st.composite
def histograms(draw: st.DrawFn) -> dict[str, Any]:
    bins = draw(st.integers(1, 40))
    widths = draw(st.lists(st.floats(0.1, 10), min_size=bins, max_size=bins))
    edges = [draw(st.floats(-100, 100))]
    for width in widths:
        edges.append(edges[-1] + width)
    counts = draw(st.lists(st.floats(0, 1000), min_size=bins, max_size=bins))
    mean = draw(st.none() | st.floats(edges[0], edges[-1]))
    spread = draw(st.none() | st.floats(0.1, 50))
    visual = {"component": "histogram", "edges": edges, "counts": counts}
    visual |= {"mean": mean, "spread": spread}
    visual["curve"] = mean is not None and spread is not None and draw(st.booleans())
    if draw(st.booleans()):
        visual["labels"] = [str(n) for n in range(bins)]
    return visual


@st.composite
def flow_diagrams(draw: st.DrawFn) -> dict[str, Any]:
    ids = [f"b{n}" for n in range(draw(st.integers(2, 6)))]
    boxes = [{"id": box, "label": draw(labels.filter(bool))} for box in ids]
    ends = st.tuples(st.sampled_from(ids), st.sampled_from(ids)).filter(
        lambda e: e[0] != e[1]
    )
    links = [
        {"from": start, "to": end, "label": draw(labels)}
        for start, end in draw(st.lists(ends, max_size=10))
    ]
    direction = draw(st.sampled_from(["right", "down"]))
    return {
        "component": "flow-diagram",
        "boxes": boxes,
        "links": links,
        "direction": direction,
    }


@FAST
@given(visual=present_values(), region=regions)
def test_present_value_labels_fit_and_match_the_formula(
    visual: dict[str, Any], region: str
) -> None:
    drawing = drawn(visual, region)

    rate, flows = visual["rate"], visual["flows"]
    expected = {shown(present_value(f["amount"], rate, f["at"]), "$") for f in flows}
    family = drawing.get_family()
    worth = [
        m.original_text for m in family if isinstance(m, Text) and m.name == "worth"
    ]
    assert set(worth) <= expected


@FAST
@given(visual=complex_planes(), region=regions)
def test_complex_planes_fit_and_keep_labels_apart(
    visual: dict[str, Any], region: str
) -> None:
    drawn(visual, region)


@FAST
@given(visual=histograms(), region=regions)
def test_histograms_fit_and_keep_labels_apart(
    visual: dict[str, Any], region: str
) -> None:
    drawn(visual, region)


@FAST
@given(visual=flow_diagrams(), region=regions)
def test_flow_diagrams_fit_and_keep_labels_apart(
    visual: dict[str, Any], region: str
) -> None:
    drawn(visual, region)


@st.composite
def neighborhoods(draw: st.DrawFn) -> dict[str, Any]:
    coordinate = st.floats(-50, 50).map(lambda v: round(v, 1))
    pair = st.lists(coordinate, min_size=2, max_size=2)
    points = draw(st.lists(pair, min_size=1, max_size=60))
    query = draw(pair)
    k = draw(st.integers(1, len(points)))
    assume(not tied(points, query, k))
    groups = draw(st.lists(st.integers(0, 4), min_size=len(points), max_size=60))
    return {
        "component": "scatter-plot",
        "points": points,
        "groups": groups[: len(points)],
        "query": query,
        "k": k,
    }


@settings(max_examples=50, deadline=None)
@given(visual=neighborhoods(), region=regions)
def test_neighborhoods_ring_the_nearest_points_and_reach_the_kth(
    visual: dict[str, Any], region: str
) -> None:
    drawing = drawn(visual, region)
    axes = drawing[0]
    assert isinstance(axes, Axes)
    points, query, k = visual["points"], visual["query"], visual["k"]

    distances = sorted(math.dist(p, query) for p in points)
    inside = [p for p in points if math.dist(p, query) <= distances[k - 1]]
    rings = [m for m in drawing.get_family() if m.name == "ring"]
    assert len(rings) == k == len(inside)
    for point in inside:
        spot = axes.c2p(*point)
        assert any(np.allclose(spot, r.get_center(), atol=1e-6) for r in rings)

    (boundary,) = [m for m in drawing.get_family() if m.name == "reach"]
    middle = axes.c2p(*query)
    wide = axes.c2p(query[0] + distances[k - 1], query[1])[0] - middle[0]
    tall = axes.c2p(query[0], query[1] + distances[k - 1])[1] - middle[1]
    # A ring's radius is 0.16 before build() shrinks the drawing to fit.
    floor = 0.4 * rings[0].width / 0.32
    assert np.allclose(boundary.get_center(), middle, atol=1e-6)
    assert math.isclose(boundary.width, max(2 * wide, floor), rel_tol=1e-3)
    assert math.isclose(boundary.height, max(2 * tall, floor), rel_tol=1e-3)

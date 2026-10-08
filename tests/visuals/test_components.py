"""Each component draws inside any region it fits, with readable text."""

import pytest
from pydantic import ValidationError

from unfold.visuals.components import NAMES, ComponentError, build, crowded, parse
from unfold.visuals.layout import Placed, box_of, check_layout

SAMPLES: dict[str, dict[str, object]] = {
    "text-card": {
        "component": "text-card",
        "title": "Time value of money",
        "lines": ["A dollar today can earn interest.", "A dollar next year cannot."],
    },
    "equation": {
        "component": "equation",
        "tex": r"e^{i\pi} + 1 = 0",
        "caption": "Euler's identity",
    },
    "bar-chart": {
        "component": "bar-chart",
        "labels": ["Year 1", "Year 2", "Year 3"],
        "values": [100, 105, 110.25],
        "title": "Growth at 5 percent",
    },
    "scatter-plot": {
        "component": "scatter-plot",
        "points": [[1, 2], [2, 3], [3, 5], [4, 4]],
        "groups": [0, 0, 1, 1],
        "x_label": "size",
        "y_label": "price",
        "line": [0.8, 1.2],
    },
    "timeline": {
        "component": "timeline",
        "start": 0,
        "end": 3,
        "events": [
            {"at": 0, "label": "Invest", "amount": -100},
            {"at": 3, "label": "Payoff", "amount": 120},
        ],
    },
    "complex-plane": {
        "component": "complex-plane",
        "points": [
            {"label": "z", "radius": 1, "angle": 60, "guides": True}
            | {"real_label": "cos x", "imag_label": "sin x"}
        ],
        "turn": {"start": 0, "end": 60, "label": "x"},
    },
    "histogram": {
        "component": "histogram",
        "edges": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
        "counts": [1, 1, 1, 1, 1, 1],
        "labels": ["1", "2", "3", "4", "5", "6"],
        "mean": 3.5,
        "spread": 1.71,
        "curve": True,
        "title": "One fair die",
    },
    "flow-diagram": {
        "component": "flow-diagram",
        "boxes": [
            {"id": "data", "label": "Labeled data"},
            {"id": "method", "label": "A method"},
            {"id": "guess", "label": "A prediction"},
        ],
        "links": [
            {"from": "data", "to": "method", "label": "train"},
            {"from": "method", "to": "guess"},
        ],
        "highlight": "method",
    },
    "present-value": {
        "component": "present-value",
        "rate": 8,
        "flows": [{"at": 0, "amount": -25_000}]
        + [{"at": year, "amount": 8_000} for year in range(1, 5)],
        "prefix": "$",
        "title": "An investment at 8 percent",
    },
    "custom": {
        "component": "custom",
        "description": "Cash rains on a small town while store shelves stay full.",
    },
}


def test_every_component_has_a_sample() -> None:
    assert set(SAMPLES) == set(NAMES)


@pytest.mark.parametrize("region", ["full", "plot", "left", "right"])
@pytest.mark.parametrize("name", sorted(SAMPLES))
def test_every_component_fits_its_region(name: str, region: str) -> None:
    drawing, min_font = build(parse(SAMPLES[name]), region)

    assert check_layout([Placed(name, region, box_of(drawing), min_font)]) == []


def test_a_short_text_card_fits_the_top_band() -> None:
    card = parse({"component": "text-card", "title": "Supply and demand", "lines": []})
    drawing, min_font = build(card, "top")

    assert check_layout([Placed("title", "top", box_of(drawing), min_font)]) == []


def test_a_bar_chart_needs_one_value_per_label() -> None:
    with pytest.raises(ValidationError):
        parse({**SAMPLES["bar-chart"], "values": [1, 2]})


def test_a_bar_chart_holds_at_most_12_bars() -> None:
    labels = [f"b{n}" for n in range(13)]
    with pytest.raises(ValidationError):
        parse({"component": "bar-chart", "labels": labels, "values": [1] * 13})


def test_an_unknown_component_fails() -> None:
    with pytest.raises(ValidationError):
        parse({"component": "hologram"})


def test_tex_that_does_not_compile_names_the_component() -> None:
    with pytest.raises(ComponentError, match="equation"):
        build(parse({"component": "equation", "tex": r"\frac{1"}), "full")


def test_a_timeline_with_twelve_flows_keeps_its_labels_apart() -> None:
    events = [{"at": 0, "label": "Invest", "amount": -100000}]
    events += [{"at": n, "label": f"Year {n}", "amount": 10000} for n in range(1, 12)]
    timeline = parse({"component": "timeline", "start": 0, "end": 11, "events": events})

    drawing, _ = build(timeline, "plot")

    assert crowded(drawing) == 0


def test_a_bar_chart_with_long_labels_keeps_them_apart() -> None:
    names = [
        "Euler's identity",
        "Pythagorean theorem",
        "Fundamental theorem of calculus",
    ]
    chart = parse({"component": "bar-chart", "labels": names, "values": [3, 2, 1]})

    drawing, min_font = build(chart, "plot")

    assert crowded(drawing) == 0
    assert min_font is not None and min_font >= 18

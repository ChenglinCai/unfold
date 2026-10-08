"""The domain packs: components that the golden set asked for at least three times."""

import itertools
import math
from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
import yaml
from manim import Mobject, Text, VGroup
from pydantic import ValidationError

from unfold.cli import main
from unfold.visuals.components import build, crowded, parse
from unfold.visuals.finance import present_value, shown
from unfold.visuals.layout import Placed, box_of, check_layout

SCRIPT = """---
format: script/v1
episode: E01-packs
segment: s1-show
voice: default
anchors:
  show: []
---

[[show]] Look at the picture for a moment.
"""


def texts(drawing: VGroup, name: str) -> list[str]:
    family = drawing.get_family()
    return [m.original_text for m in family if isinstance(m, Text) and m.name == name]


def parts(drawing: VGroup, name: str) -> list[Mobject]:
    found = [m for m in drawing.get_family() if m.name == name]
    return sorted(found, key=lambda m: m.get_center()[0])


def render_one(root: Path, visual: dict[str, object]) -> Path:
    """Render a one-beat segment that shows a single visual in the plot band."""
    folder = root / "E01-packs" / "s1-show"
    folder.mkdir(parents=True)
    (folder / "script.md").write_text(SCRIPT)
    entry = {"cue": "show", "region": "plot", "visual": visual}
    head = {"format": "scene/v0", "episode": "E01-packs", "segment": "s1-show"}
    (folder / "scene.yaml").write_text(yaml.safe_dump({**head, "entries": [entry]}))
    assert main(["render", str(root)]) == 0
    assert (folder / "segment.mp4").stat().st_size > 0
    assert (folder / "contact-sheet.png").stat().st_size > 0
    return folder


YEARLY: dict[str, object] = {
    "component": "present-value",
    "rate": 8,
    "flows": [{"at": year, "amount": 10_000} for year in range(1, 13)],
    "prefix": "$",
}


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"rate": -1}, r"present-value\.rate"),
        ({"rate": 101}, r"present-value\.rate"),
        ({"flows": []}, r"present-value\.flows"),
        ({"flows": [{"at": year, "amount": 1} for year in range(25)]}, r"value\.flows"),
        ({"flows": [{"at": -1, "amount": 1}]}, r"flows\.0\.at"),
        ({"flows": [{"at": 101, "amount": 1}]}, r"flows\.0\.at"),
        ({"flows": [{"at": 1, "amount": 0}]}, r"flows\.0\.amount"),
        ({"flows": [{"at": 1, "amount": 5}, {"at": 1, "amount": 6}]}, "own time"),
        ({"prefix": "USD$"}, r"present-value\.prefix"),
    ],
)
def test_present_value_rejects_bad_parameters(
    change: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse({**YEARLY, **change})


def test_every_present_value_label_matches_the_formula() -> None:
    drawing, _ = build(parse(YEARLY), "plot")

    expected = {shown(present_value(10_000, 8, year), "$") for year in range(1, 13)}
    worth = texts(drawing, "worth")
    assert worth and set(worth) <= expected
    total = sum(present_value(10_000, 8, year) for year in range(1, 13))
    assert texts(drawing, "total") == [f"Worth today in all: {shown(total, '$')}"]


@pytest.mark.parametrize("region", ["plot", "left"])
def test_twelve_flows_show_no_overlapping_labels(region: str) -> None:
    drawing, _ = build(parse(YEARLY), region)

    assert crowded(drawing) == 0


def test_a_present_value_shrinks_with_time_inside_its_amount() -> None:
    drawing, _ = build(parse(YEARLY), "plot")

    paid, today = parts(drawing, "paid"), parts(drawing, "today")
    assert len(paid) == len(today) == 12
    assert all(t.height <= p.height + 1e-6 for t, p in zip(today, paid, strict=True))
    heights = [t.height for t in today]
    assert heights == sorted(heights, reverse=True)


def test_money_paid_out_sits_below_the_axis() -> None:
    flows = [
        {"at": 0, "amount": -100},
        {"at": 1, "amount": 60},
        {"at": 2, "amount": 60},
    ]
    visual = {"component": "present-value", "rate": 10, "flows": flows}
    drawing, _ = build(parse(visual), "plot")

    [axis] = parts(drawing, "axis")
    today = parts(drawing, "today")
    assert today[0].get_top()[1] <= axis.get_center()[1] + 1e-6
    assert today[1].get_bottom()[1] >= axis.get_center()[1] - 1e-6


@pytest.mark.slow
def test_a_present_value_renders(tmp_path: Path) -> None:
    render_one(tmp_path, YEARLY)


ROTATION: dict[str, object] = {
    "component": "complex-plane",
    "points": [{"label": "z", "radius": 1, "angle": 60}],
}


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"points": []}, r"complex-plane\.points"),
        (
            {"points": [{"radius": 1, "angle": n} for n in range(7)]},
            r"complex-plane\.points",
        ),
        ({"points": [{"radius": -1, "angle": 0}]}, r"points\.0\.radius"),
        ({"points": [{"radius": 101, "angle": 0}]}, r"points\.0\.radius"),
        ({"turn": {"start": 30, "end": 30}}, "sweep"),
    ],
)
def test_complex_plane_rejects_bad_parameters(
    change: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse({**ROTATION, **change})


def polar(point: Mobject, center: Mobject) -> tuple[float, float]:
    dx, dy = (point.get_center() - center.get_center())[:2]
    return math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))


def test_a_point_at_radius_one_sits_on_the_unit_circle() -> None:
    drawing, _ = build(parse(ROTATION), "plot")

    [circle], [point] = parts(drawing, "unit-circle"), parts(drawing, "point")
    distance, angle = polar(point, circle)
    assert distance == pytest.approx(circle.width / 2, rel=0.02)
    assert angle == pytest.approx(60, abs=1)


def test_a_far_point_grows_the_plane_and_still_fits() -> None:
    visual = {**ROTATION, "points": [{"label": "3z", "radius": 3, "angle": 200}]}
    drawing, min_font = build(parse(visual), "plot")

    [plane], [point] = parts(drawing, "plane"), parts(drawing, "point")
    assert plane.get_left()[0] < point.get_center()[0] < plane.get_right()[0]
    assert plane.get_bottom()[1] < point.get_center()[1] < plane.get_top()[1]
    placed = Placed("plane", "plot", box_of(drawing), min_font, crowded(drawing))
    assert check_layout([placed]) == []


def test_guides_drop_dashed_lines_to_both_axes() -> None:
    point = {"radius": 1, "angle": 40, "guides": True}
    point |= {"real_label": "cos x", "imag_label": "sin x"}
    drawing, _ = build(parse({**ROTATION, "points": [point]}), "plot")

    assert len(parts(drawing, "guide")) == 2
    assert sorted(texts(drawing, "guide-label")) == ["cos x", "sin x"]


@pytest.mark.parametrize("end", [359, 360, 400, -360])
def test_a_full_turn_draws_a_loop_that_fits(end: float) -> None:
    turn = {"start": 0, "end": end, "label": "one turn"}
    drawing, min_font = build(parse({**ROTATION, "turn": turn}), "plot")

    [arc] = parts(drawing, "turn")
    assert arc.angle == pytest.approx(math.radians(end))
    assert texts(drawing, "turn-label") == ["one turn"]
    placed = Placed("plane", "plot", box_of(drawing), min_font, crowded(drawing))
    assert check_layout([placed]) == []


def test_crowded_points_keep_their_labels_apart() -> None:
    points = [{"label": f"z{n}", "radius": 1, "angle": 40 + n} for n in range(6)]
    drawing, _ = build(parse({**ROTATION, "points": points}), "left")

    assert crowded(drawing) == 0


@pytest.mark.slow
def test_a_complex_plane_renders(tmp_path: Path) -> None:
    point = {"label": "z", "radius": 1, "angle": 60, "guides": True}
    render_one(
        tmp_path, {**ROTATION, "points": [point], "turn": {"start": 0, "end": 60}}
    )


def test_a_full_turn_puts_its_label_below_the_plane() -> None:
    turn = {"start": 0, "end": 360, "label": "one full turn"}
    drawing, _ = build(parse({**ROTATION, "turn": turn}), "plot")

    [plane], [label] = parts(drawing, "plane"), parts(drawing, "turn-label")
    assert label.get_top()[1] <= plane.get_bottom()[1]


def test_an_inner_point_labels_beside_its_ray() -> None:
    points = [{"label": "z", "radius": 1, "angle": 200}]
    points.append({"label": "3z", "radius": 3, "angle": 200})
    drawing, _ = build(parse({**ROTATION, "points": points}), "plot")

    inner = next(m for m in parts(drawing, "point-label") if m.original_text == "z")
    [_, outer_dot] = sorted(parts(drawing, "point"), key=lambda m: -m.get_center()[0])
    origin = parts(drawing, "plane")[0].get_center()
    ray = outer_dot.get_center() - origin
    offset = inner.get_center() - origin
    gap = abs(ray[0] * offset[1] - ray[1] * offset[0]) / float(np.linalg.norm(ray))
    assert gap > 0.25


DIE: dict[str, object] = {
    "component": "histogram",
    "edges": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5],
    "counts": [1, 1, 1, 1, 1, 1],
    "labels": ["1", "2", "3", "4", "5", "6"],
    "mean": 3.5,
    "spread": 1.708,
    "curve": True,
}


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"edges": [0.5], "counts": []}, r"histogram\.edges"),
        ({"edges": list(range(42)), "counts": [1] * 41}, r"histogram\.edges"),
        ({"edges": [0, 2, 1], "counts": [1, 1], "labels": []}, "must increase"),
        ({"counts": [1, 1]}, "one count for each bin"),
        ({"counts": [1, 1, 1, 1, 1, -1]}, r"histogram\.counts\.5"),
        ({"labels": ["1", "2"]}, "one label for each bin"),
        ({"spread": 0}, r"histogram\.spread"),
        ({"spread": None}, "bell curve"),
        ({"highlight": 6}, "name a bin"),
    ],
)
def test_histogram_rejects_bad_parameters(
    change: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse({**DIE, **change})


def test_bins_touch_and_the_mean_line_sits_at_the_mean() -> None:
    drawing, _ = build(parse(DIE), "plot")

    bars, [mean] = parts(drawing, "bar"), parts(drawing, "mean")
    assert len(bars) == 6
    for left, right in itertools.pairwise(bars):
        assert left.get_right()[0] == pytest.approx(right.get_left()[0], abs=1e-6)
    assert mean.get_center()[0] == pytest.approx(bars[2].get_right()[0], abs=1e-6)
    assert texts(drawing, "bin-label") == ["1", "2", "3", "4", "5", "6"]


def test_the_bell_curve_matches_the_histograms_area() -> None:
    drawing, _ = build(parse(DIE), "plot")

    [curve], [axis] = parts(drawing, "curve"), parts(drawing, "axis")
    bars = parts(drawing, "bar")
    peak = 6 / (1.708 * math.sqrt(2 * math.pi))
    rise = curve.get_top()[1] - axis.get_center()[1]
    assert rise / bars[0].height == pytest.approx(peak, rel=0.03)


def test_many_bins_keep_their_edge_labels_apart() -> None:
    visual = {"component": "histogram", "edges": list(range(41)), "counts": [3] * 40}
    drawing, _ = build(parse(visual), "left")

    assert texts(drawing, "edge-label")
    assert crowded(drawing) == 0


@pytest.mark.slow
def test_a_histogram_renders(tmp_path: Path) -> None:
    render_one(tmp_path, {**DIE, "highlight": 2, "title": "One fair die"})


def test_the_spread_label_sits_beside_the_mean_label_above_the_bars() -> None:
    drawing, _ = build(parse(DIE), "plot")

    [mean], [spread] = parts(drawing, "mean-label"), parts(drawing, "spread-label")
    tallest = max(bar.get_top()[1] for bar in parts(drawing, "bar"))
    assert spread.get_bottom()[1] > tallest
    assert spread.get_center()[1] == pytest.approx(mean.get_center()[1], abs=0.05)


CYCLE: dict[str, object] = {
    "component": "flow-diagram",
    "boxes": [
        {"id": "you", "label": "You"},
        {"id": "barista", "label": "Barista"},
        {"id": "owner", "label": "Owner"},
    ],
    "links": [
        {"from": "you", "to": "barista", "label": "pays"},
        {"from": "barista", "to": "owner"},
        {"from": "owner", "to": "you"},
    ],
}


@pytest.mark.parametrize(
    ("change", "field"),
    [
        ({"boxes": [{"id": "a", "label": "A"}], "links": []}, r"flow-diagram\.boxes"),
        (
            {"boxes": [{"id": f"b{n}", "label": "B"} for n in range(7)], "links": []},
            r"flow-diagram\.boxes",
        ),
        ({"links": [{"from": "you", "to": "owner"}] * 11}, r"flow-diagram\.links"),
        ({"boxes": [{"id": "you", "label": "A"}] * 3, "links": []}, "unique"),
        ({"links": [{"from": "you", "to": "ghost"}]}, "no box called ghost"),
        ({"links": [{"from": "you", "to": "you"}]}, "two different boxes"),
        ({"highlight": "ghost"}, "highlight must name a box"),
        (
            {"boxes": [{"id": "Big Box", "label": "A"}] * 2, "links": []},
            r"boxes\.0\.id",
        ),
    ],
)
def test_flow_diagram_rejects_bad_parameters(
    change: dict[str, object], field: str
) -> None:
    with pytest.raises(ValidationError, match=field):
        parse({**CYCLE, **change})


def test_a_link_back_to_the_start_curves_past_the_middle_box() -> None:
    drawing, _ = build(parse(CYCLE), "plot")

    boxes, links = parts(drawing, "box"), parts(drawing, "link")
    assert texts(drawing, "box-label") == ["You", "Barista", "Owner"]
    back = max(links, key=lambda link: link.width)
    assert back.get_top()[1] <= boxes[1].get_bottom()[1] + 1e-6
    assert texts(drawing, "link-label") == ["pays"]


def test_opposite_links_curve_apart() -> None:
    links = [{"from": "you", "to": "barista"}, {"from": "barista", "to": "you"}]
    drawing, _ = build(parse({**CYCLE, "links": links}), "plot")

    first, second = parts(drawing, "link")
    assert not box_of(first).overlaps(box_of(second))


def test_boxes_can_run_down_with_no_links() -> None:
    drawing, _ = build(parse({**CYCLE, "links": [], "direction": "down"}), "plot")

    boxes = sorted(parts(drawing, "box"), key=lambda box: -box.get_center()[1])
    assert len(boxes) == 3 and not parts(drawing, "link")
    assert max(b.get_center()[0] for b in boxes) == pytest.approx(
        min(b.get_center()[0] for b in boxes), abs=1e-6
    )


@pytest.mark.slow
def test_a_flow_diagram_renders(tmp_path: Path) -> None:
    render_one(tmp_path, {**CYCLE, "highlight": "barista"})


def test_labels_on_straight_links_stay_clear_of_the_boxes() -> None:
    links = [
        {"from": "you", "to": "barista", "label": "applies"},
        {"from": "barista", "to": "owner", "label": "predicts"},
    ]
    drawing, _ = build(parse({**CYCLE, "links": links}), "plot")

    frames = [box_of(frame) for frame in parts(drawing, "box")]
    labels = [box_of(label) for label in parts(drawing, "link-label")]
    assert len(labels) == 2
    for label, (left, right) in zip(labels, itertools.pairwise(frames), strict=True):
        assert label.left - left.right > 0.1
        assert right.left - label.right > 0.1


def test_the_total_nets_money_paid_out_against_money_received() -> None:
    flows = [
        {"at": 0, "amount": -100},
        {"at": 1, "amount": 60},
        {"at": 2, "amount": 60},
    ]
    visual = {"component": "present-value", "rate": 10, "flows": flows}
    drawing, _ = build(parse(visual), "plot")

    net = -100 + 60 / 1.1 + 60 / 1.1**2
    assert texts(drawing, "total") == [f"Worth today in all: {shown(net)}"]


@pytest.mark.parametrize("angle", [420, -300])
def test_an_angle_past_a_full_turn_lands_like_its_remainder(angle: float) -> None:
    plain, _ = build(
        parse({**ROTATION, "points": [{"radius": 1, "angle": 60}]}), "plot"
    )
    turned, _ = build(
        parse({**ROTATION, "points": [{"radius": 1, "angle": angle}]}), "plot"
    )

    [first], [second] = parts(plain, "point"), parts(turned, "point")
    assert np.allclose(first.get_center(), second.get_center(), atol=1e-6)


def test_a_box_label_never_splits_a_word() -> None:
    labels = ["Training data", "Distance function", "Majority vote", "k-NN Classifier"]
    boxes = [{"id": f"b{n}", "label": label} for n, label in enumerate(labels)]
    boxes.append({"id": "b4", "label": "No training step"})
    drawing, _ = build(parse({**CYCLE, "boxes": boxes, "links": []}), "plot")

    words = " ".join(texts(drawing, "box-label")).split()
    assert sorted(words) == sorted(" ".join([*labels, "No training step"]).split())


@pytest.fixture
def wide_font() -> Iterator[None]:
    """Draw with Verdana where it exists. Linux's default font already runs as wide."""
    import manimpango

    wide = "Verdana" in manimpango.list_fonts()
    if wide:
        Text.set_default(font="Verdana")
    yield
    if wide:
        Text.set_default()


@pytest.mark.parametrize("region", ["left", "right"])
def test_a_flow_diagram_keeps_room_in_half_regions_with_a_wide_font(
    wide_font: None, region: str
) -> None:
    boxes = [
        {"id": "data", "label": "Labeled data"},
        {"id": "method", "label": "A method"},
        {"id": "guess", "label": "A prediction"},
    ]
    links = [{"from": "data", "to": "method", "label": "train"}]
    visual = {"component": "flow-diagram", "boxes": boxes, "links": links}

    _, min_font = build(parse(visual), region)

    # 19 points leaves room above the 18-point floor for Linux's wider default font.
    assert min_font is not None and min_font >= 19

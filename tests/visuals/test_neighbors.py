"""The neighborhood on a scatter plot: nearest points, ties, the vote, and the drawing."""

import math

import numpy as np
import pytest
from manim import Axes, Mobject, VGroup
from pydantic import ValidationError

from unfold.visuals import theme
from unfold.visuals.components import build, crowded
from unfold.visuals.layout import REGIONS, box_of
from unfold.visuals.neighbors import nearest, tied, vote
from unfold.visuals.params import ScatterPlot, parse

POINTS = [[1, 1], [2, 1.5], [1.5, 3], [4, 4], [5, 3.5], [4.5, 5]]
GROUPS = [0, 0, 0, 1, 1, 1]


def test_nearest_lists_the_k_closest_points_nearest_first() -> None:
    assert nearest(POINTS, [3, 3], 3) == [3, 2, 1]


def test_a_query_on_a_point_counts_that_point_first() -> None:
    assert nearest(POINTS, [4, 4], 1) == [3]


def test_tied_finds_a_next_point_at_the_kth_distance() -> None:
    square = [[1, 0], [0, 1], [-1, 0], [0, -1], [3, 3]]
    assert tied(square, [0, 0], 2)
    assert not tied(square, [0, 0], 4)
    assert not tied(square, [0, 0], 5)


def test_vote_picks_the_largest_group_or_none_on_a_tie() -> None:
    assert vote(GROUPS, [3, 2, 1]) == 0
    assert vote(GROUPS, [3, 2]) is None
    assert vote([], [0, 1]) == 0


def scatter(**extra: object) -> dict[str, object]:
    return {"component": "scatter-plot", "points": POINTS, "groups": GROUPS} | extra


def test_a_plot_without_a_query_still_parses() -> None:
    plot = parse(scatter())
    assert isinstance(plot, ScatterPlot)
    assert plot.query is None


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ({"query": [3, 3]}, "needs both"),
        ({"k": 2}, "needs both"),
        ({"query": [3, 3], "k": 7}, "k is 7, but the plot has 6 points"),
        ({"query": [0, 0], "k": 0}, "greater than or equal to 1"),
        ({"query": [4.5, 3.75], "k": 1}, "tie"),
    ],
)
def test_a_misleading_neighborhood_fails_with_a_message(
    extra: dict[str, object], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        parse(scatter(**extra))


def test_a_tie_inside_the_neighborhood_is_fine() -> None:
    assert math.isclose(math.dist([3, 2.25], [2, 1.5]), math.dist([3, 2.25], [4, 3]))
    parse(scatter(points=[*POINTS, [4, 3]], groups=[*GROUPS, 1], query=[3, 2.25], k=3))


def drawn(region: str = "plot", **extra: object) -> VGroup:
    drawing, _ = build(parse(scatter(**extra)), region)
    assert crowded(drawing) == 0
    assert REGIONS[region].contains(box_of(drawing))
    return drawing


def parts(drawing: VGroup, name: str) -> list[Mobject]:
    return [m for m in drawing.get_family() if m.name == name]


def at(drawing: VGroup, point: list[float]) -> np.ndarray:
    axes = drawing[0]
    assert isinstance(axes, Axes)
    return np.asarray(axes.c2p(*point))


def test_rings_sit_on_exactly_the_k_nearest_points() -> None:
    drawing = drawn(query=[3, 3], k=3)
    centers = [ring.get_center() for ring in parts(drawing, "ring")]
    expected = [at(drawing, POINTS[i]) for i in (3, 2, 1)]
    assert len(centers) == 3
    for center in expected:
        assert any(np.allclose(center, c, atol=1e-6) for c in centers)


def test_the_boundary_passes_through_the_kth_nearest_point() -> None:
    drawing = drawn(query=[3, 3], k=3)
    (boundary,) = parts(drawing, "reach")
    middle = at(drawing, [3, 3])
    half_x, half_y = boundary.width / 2, boundary.height / 2
    assert np.allclose(boundary.get_center(), middle, atol=1e-6)

    def scaled(point: list[float]) -> float:
        dx, dy = (at(drawing, point) - middle)[:2]
        return math.hypot(dx / half_x, dy / half_y)

    assert math.isclose(scaled(POINTS[1]), 1, rel_tol=0.02)
    assert all(scaled(POINTS[i]) < 1 for i in (3, 2))
    assert all(scaled(POINTS[i]) > 1 for i in (0, 4, 5))


@pytest.mark.parametrize("region", ["full", "plot", "left", "right"])
def test_a_distant_query_stays_inside_the_region(region: str) -> None:
    drawn(region, query=[40, -30], k=2)


def test_the_query_takes_the_winning_color_or_the_text_color() -> None:
    (winner,) = parts(drawn(query=[3, 3], k=3), "query")
    (tie,) = parts(drawn(query=[3, 3], k=2), "query")
    assert winner.get_fill_color().to_hex().upper() == theme.PALETTE[0].upper()
    assert tie.get_fill_color().to_hex().upper() == theme.TEXT.upper()


def test_a_plot_without_a_query_draws_no_neighborhood() -> None:
    drawing = drawn()
    assert (
        not parts(drawing, "query") + parts(drawing, "ring") + parts(drawing, "reach")
    )


@pytest.mark.parametrize("region", ["full", "plot", "left", "right"])
def test_similar_spans_draw_a_round_circle(region: str) -> None:
    (boundary,) = parts(drawn(region, query=[3, 3], k=3), "reach")
    assert math.isclose(boundary.width, boundary.height, rel_tol=1e-3)


def test_very_different_spans_keep_the_plot_wide() -> None:
    stretched = [[x * 100, y] for x, y in POINTS]
    drawing = drawn(points=stretched, query=[400, 4], k=1)
    assert drawing[0].width > 2 * drawing[0].height

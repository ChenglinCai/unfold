"""The layout grid names regions of the frame, and the check measures placed objects."""

from manim import Square

from unfold.visuals.layout import FRAME, REGIONS, Box, Placed, box_of, check_layout


def test_the_grid_names_six_regions_inside_the_frame() -> None:
    assert set(REGIONS) == {"full", "plot", "top", "bottom", "left", "right"}
    assert all(FRAME.contains(box) for box in REGIONS.values())


def test_which_regions_overlap() -> None:
    assert not REGIONS["left"].overlaps(REGIONS["right"])
    assert not REGIONS["top"].overlaps(REGIONS["plot"])
    assert REGIONS["plot"].overlaps(REGIONS["left"])
    assert REGIONS["full"].overlaps(REGIONS["bottom"])


def test_box_of_measures_a_manim_object() -> None:
    box = box_of(Square(side_length=2))

    assert (box.left, box.bottom, box.right, box.top) == (-1.0, -1.0, 1.0, 1.0)


def test_a_fitting_layout_passes() -> None:
    placed = [
        Placed("title", "top", Box(-3, 2.6, 3, 3.4)),
        Placed("chart", "left", Box(-6, -2, -1, 2)),
        Placed("dots", "right", Box(1, -2, 6, 2)),
    ]

    assert check_layout(placed) == []


def test_an_object_outside_its_region_is_named() -> None:
    errors = check_layout([Placed("chart", "left", Box(-2, -1, 2, 1))])

    assert errors == ["chart: leaves region left"]


def test_an_object_outside_the_frame_is_named() -> None:
    errors = check_layout([Placed("chart", "full", Box(-9, -1, 0, 1))])

    assert errors == ["chart: leaves the frame"]


def test_regions_in_use_at_once_must_not_overlap() -> None:
    placed = [
        Placed("card", "full", Box(-1, -1, 1, 1)),
        Placed("caption", "bottom", Box(-1, -3.4, 1, -3)),
    ]

    assert check_layout(placed) == ["regions bottom and full are in use at once"]


def test_text_below_the_minimum_size_fails() -> None:
    errors = check_layout([Placed("card", "full", Box(-1, -1, 1, 1), min_font=12)])

    assert errors == ["card: text size 12 is below 18"]

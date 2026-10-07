"""The layout grid: named regions of the 16:9 frame, and the layout check.

Coordinates are manim's: the frame spans 14.2 units across and 8 units up,
with the origin at its center.
"""

from dataclasses import dataclass
from itertools import combinations

from manim import Mobject, config

from unfold.visuals.theme import MIN_FONT

MARGIN = 0.4
GAP = 0.2
BAND = 1.3
TOLERANCE = 0.01


@dataclass(frozen=True)
class Box:
    left: float
    bottom: float
    right: float
    top: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    @property
    def center(self) -> tuple[float, float]:
        return ((self.left + self.right) / 2, (self.bottom + self.top) / 2)

    def contains(self, other: "Box") -> bool:
        return (
            other.left >= self.left - TOLERANCE
            and other.bottom >= self.bottom - TOLERANCE
            and other.right <= self.right + TOLERANCE
            and other.top <= self.top + TOLERANCE
        )

    def overlaps(self, other: "Box") -> bool:
        across = min(self.right, other.right) - max(self.left, other.left)
        up = min(self.top, other.top) - max(self.bottom, other.bottom)
        return across > TOLERANCE and up > TOLERANCE


half_w, half_h = config.frame_width / 2, config.frame_height / 2
FRAME = Box(-half_w, -half_h, half_w, half_h)
_safe = Box(-half_w + MARGIN, -half_h + MARGIN, half_w - MARGIN, half_h - MARGIN)
_top = Box(_safe.left, _safe.top - BAND, _safe.right, _safe.top)
_bottom = Box(_safe.left, _safe.bottom, _safe.right, _safe.bottom + BAND)
_plot = Box(_safe.left, _bottom.top + GAP, _safe.right, _top.bottom - GAP)
REGIONS: dict[str, Box] = {
    "full": _safe,
    "top": _top,
    "bottom": _bottom,
    "plot": _plot,
    "left": Box(_plot.left, _plot.bottom, -GAP / 2, _plot.top),
    "right": Box(GAP / 2, _plot.bottom, _plot.right, _plot.top),
}


def box_of(mobject: Mobject) -> Box:
    return Box(
        float(mobject.get_left()[0]),
        float(mobject.get_bottom()[1]),
        float(mobject.get_right()[0]),
        float(mobject.get_top()[1]),
    )


@dataclass(frozen=True)
class Placed:
    """One object on screen: what it is, its region, its box, and its smallest text."""

    name: str
    region: str
    box: Box
    min_font: float | None = None
    # Pairs of labels inside the object that overlap each other.
    overlaps: int = 0


def check_layout(placed: list[Placed]) -> list[str]:
    """Every way the objects on screen at one moment break the layout."""
    errors: list[str] = []
    for item in placed:
        if not FRAME.contains(item.box):
            errors.append(f"{item.name}: leaves the frame")
        elif not REGIONS[item.region].contains(item.box):
            errors.append(f"{item.name}: leaves region {item.region}")
        if item.min_font is not None and item.min_font < MIN_FONT:
            share = int(100 * item.min_font / MIN_FONT) // 5 * 5
            errors.append(
                f"{item.name}: text size {item.min_font:.1f} is below {MIN_FONT}. "
                f"Cut its text to about {share} percent, or give it a bigger region"
            )
        if item.overlaps:
            errors.append(
                f"{item.name}: {item.overlaps} labels overlap. "
                "Use shorter labels, or fewer items"
            )
    in_use = sorted({item.region for item in placed})
    errors += [
        f"regions {a} and {b} are in use at once"
        for a, b in combinations(in_use, 2)
        if REGIONS[a].overlaps(REGIONS[b])
    ]
    return errors

"""The domain packs: components that the golden set asked for at least three times."""

from pathlib import Path

import pytest
import yaml
from manim import Mobject, Text, VGroup
from pydantic import ValidationError

from unfold.cli import main
from unfold.visuals.components import build, crowded, parse
from unfold.visuals.finance import present_value, shown

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

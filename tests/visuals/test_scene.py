"""A scene plays one segment's visuals, cue by cue, and its layout is checked."""

from pathlib import Path

import yaml

from unfold.formats import problems
from unfold.formats.episode import SceneV0
from unfold.visuals.scene import beat_seconds, check_scene, on_screen

TITLE = {"component": "text-card", "title": "Growth at 5 percent", "lines": []}
BARS = {"component": "bar-chart", "labels": ["Now", "Later"], "values": [100, 105]}
CARD = {"component": "custom", "description": "Coins stack up, one row each year."}
SCENE: dict[str, object] = {
    "format": "scene/v0",
    "episode": "E01-growth",
    "segment": "s1-interest",
    "entries": [
        {"cue": "title", "region": "top", "visual": TITLE},
        {"cue": "chart", "region": "plot", "visual": BARS},
        {"cue": "card", "region": "full", "visual": CARD},
    ],
}
CUES = ["title", "chart", "card"]


def scene(**changes: object) -> SceneV0:
    return SceneV0.model_validate({**SCENE, **changes})


def test_a_beat_lasts_as_long_as_its_narration() -> None:
    assert beat_seconds("Three short words.") == 2.0
    assert beat_seconds(" ".join(["word"] * 55)) == 20.0


def test_a_scene_file_passes_its_schema(tmp_path: Path) -> None:
    path = tmp_path / "scene.yaml"
    path.write_text(yaml.safe_dump(SCENE))

    assert problems(path) == []


def test_a_new_visual_clears_the_regions_it_overlaps() -> None:
    visible = [[entry.cue for entry in beat] for beat in on_screen(scene().entries)]

    assert visible == [["title"], ["title", "chart"], ["card"]]


def test_a_good_scene_passes_the_layout_check() -> None:
    assert check_scene(scene(), CUES) == []


def test_entries_must_follow_the_script() -> None:
    errors = check_scene(scene(), ["chart", "title", "card"])

    assert errors == [
        "entries must follow the script's cues in order: chart, title, card"
    ]


def test_a_layout_failure_names_its_cue() -> None:
    long_title = {"component": "text-card", "title": "Growth " * 30, "lines": []}
    entries = [{"cue": "title", "region": "top", "visual": long_title}]

    [error] = check_scene(scene(entries=entries), ["title"])

    assert error.startswith("title: ")
    assert "below 18" in error


def test_tex_that_fails_names_its_cue() -> None:
    entries = [
        {
            "cue": "eq",
            "region": "full",
            "visual": {"component": "equation", "tex": r"\frac{1"},
        }
    ]

    [error] = check_scene(scene(entries=entries), ["eq"])

    assert error.startswith("eq: equation: ")


def test_tex_in_a_text_card_fails() -> None:
    card = {"component": "text-card", "title": "Euler", "lines": [r"e^{i\pi} + 1 = 0"]}
    entries = [{"cue": "card", "region": "full", "visual": card}]

    [error] = check_scene(scene(entries=entries), ["card"])

    assert (
        error == "card: a text card shows TeX as plain text. Use an equation, or words"
    )


def test_checks_use_a_private_manim_cache() -> None:
    from manim import config

    check_scene(scene(), CUES)

    assert Path(config.media_dir).name.startswith("unfold-manim-")

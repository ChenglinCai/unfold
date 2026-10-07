"""Scenes: one segment's visuals cue by cue, their layout check, and the manim scene.

Each beat shows one entry. A new entry clears the visuals whose regions it
overlaps, so a scene never stacks two drawings in one place.
"""

import re
from typing import Any

from manim import UP, FadeIn, FadeOut, Scene, VGroup

from unfold.formats.episode import SceneEntry, SceneV0
from unfold.script import Script
from unfold.visuals.components import ComponentError, build, crowded
from unfold.visuals.layout import REGIONS, Placed, box_of, check_layout
from unfold.visuals.params import TextCard

# A voice speaks about 165 words a minute, and no beat is shorter than 2 seconds.
WORDS_PER_SECOND = 2.75
MIN_SECONDS = 2.0
FADE_SECONDS = 0.8
# TeX commands, superscripts, or subscripts, which a text card would print literally.
TEX = re.compile(r"\\[a-zA-Z]+|\^\{|_\{")


def beat_seconds(text: str) -> float:
    return max(MIN_SECONDS, round(len(text.split()) / WORDS_PER_SECOND, 2))


def on_screen(entries: list[SceneEntry]) -> list[list[SceneEntry]]:
    """The entries visible during each beat."""
    visible: list[SceneEntry] = []
    beats: list[list[SceneEntry]] = []
    for entry in entries:
        region = REGIONS[entry.region]
        visible = [v for v in visible if not REGIONS[v.region].overlaps(region)]
        visible.append(entry)
        beats.append(list(visible))
    return beats


def check_scene(scene: SceneV0, cues: list[str]) -> list[str]:
    """Every layout failure in a scene, each named by its cue."""
    if [entry.cue for entry in scene.entries] != cues:
        return [f"entries must follow the script's cues in order: {', '.join(cues)}"]
    errors: list[str] = []
    placed: dict[str, Placed] = {}
    for entry in scene.entries:
        visual = entry.visual
        if isinstance(visual, TextCard) and any(
            TEX.search(text) for text in [visual.title, *visual.lines]
        ):
            errors.append(
                f"{entry.cue}: a text card shows TeX as plain text. Use an equation, or words"
            )
            continue
        try:
            drawing, min_font = build(visual, entry.region)
        except ComponentError as error:
            errors.append(f"{entry.cue}: {error}")
            continue
        box = box_of(drawing)
        placed[entry.cue] = Placed(
            entry.cue, entry.region, box, min_font, crowded(drawing)
        )
    for beat in on_screen(scene.entries):
        found = check_layout([placed[e.cue] for e in beat if e.cue in placed])
        errors += [error for error in found if error not in errors]
    return errors


class SegmentScene(Scene):
    """Plays a scene's visuals, one beat at a time, as long as the narration lasts."""

    def __init__(self, spec: SceneV0, script: Script, **kwargs: Any) -> None:
        self.spec, self.script = spec, script
        super().__init__(**kwargs)

    def construct(self) -> None:
        shown: dict[str, tuple[SceneEntry, VGroup]] = {}
        for entry, beat in zip(self.spec.entries, self.script.beats, strict=True):
            seconds = beat_seconds(beat.text)
            region = REGIONS[entry.region]
            leaving = [
                cue
                for cue, (old, _) in shown.items()
                if REGIONS[old.region].overlaps(region)
            ]
            drawing, _ = build(entry.visual, entry.region)
            fade = min(FADE_SECONDS, seconds / 2)
            exits = [FadeOut(shown.pop(cue)[1]) for cue in leaving]
            self.play(*exits, FadeIn(drawing, shift=UP * 0.2), run_time=fade)
            shown[entry.cue] = (entry, drawing)
            self.wait(seconds - fade)

"""Scenes: one segment's visuals cue by cue, their layout check, and the manim scene.

Each beat shows one entry. A new entry clears the visuals whose regions it
overlaps, so a scene never stacks two drawings in one place.
"""

import functools
import math
import re
import tempfile
from itertools import pairwise
from typing import Any

from manim import UP, FadeIn, FadeOut, Scene, VGroup, config

from unfold.formats.episode import SceneEntry, SceneV0
from unfold.script import Script
from unfold.visuals.components import ComponentError, build, crowded
from unfold.visuals.layout import REGIONS, Placed, box_of, check_layout
from unfold.visuals.params import Histogram, TextCard
from unfold.voice import Clip

# A voice speaks about 165 words a minute, and no beat is shorter than 2 seconds.
WORDS_PER_SECOND = 2.75
MIN_SECONDS = 2.0
FADE_SECONDS = 0.8
# Silence after each spoken beat, like a breath.
PAUSE = 0.3
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


@functools.cache
def private_media() -> str:
    """Give this process its own manim cache, so parallel builds never race."""
    folder = tempfile.mkdtemp(prefix="unfold-manim-")
    config.media_dir = folder
    return folder


def labels(data: object) -> list[str]:
    """Every string a component prints as plain text.

    An equation's TeX compiles, and a custom note is for a person, so both stay out.
    """
    if isinstance(data, str):
        return [data]
    if isinstance(data, dict):
        skip = {"tex", "description"}
        return [
            s for key, value in data.items() if key not in skip for s in labels(value)
        ]
    if isinstance(data, list):
        return [s for value in data for s in labels(value)]
    return []


def histogram_problems(chart: Histogram) -> list[str]:
    """A mean or spread that disagrees with the histogram's own bins.

    The grounded-numbers check sees only whether a number appears in the narration,
    so it cannot tell a spread from another distance that the narration mentions.
    """
    total = sum(chart.counts)
    if total <= 0:
        return []
    centers = [(left + right) / 2 for left, right in pairwise(chart.edges)]
    weighted = list(zip(chart.counts, centers, strict=True))
    mean = sum(count * x for count, x in weighted) / total
    spread = math.sqrt(sum(count * (x - mean) ** 2 for count, x in weighted) / total)
    width = min(right - left for left, right in pairwise(chart.edges))
    problems = []
    near = max(0.5 * width, 0.05 * (chart.edges[-1] - chart.edges[0]))
    if chart.mean is not None and abs(chart.mean - mean) > near:
        problems.append(
            f"the histogram's mean {chart.mean:g} differs from its bins' mean, "
            f"about {mean:.3g}. Use the bins' own mean, or change the counts"
        )
    if (
        chart.spread is not None
        and spread > 0
        and abs(chart.spread - spread) > 0.25 * spread
    ):
        problems.append(
            f"the histogram's spread {chart.spread:g} differs from its bins' standard "
            f"deviation, about {spread:.3g}. Use that, or change the counts"
        )
    return problems


def check_scene(scene: SceneV0, cues: list[str]) -> list[str]:
    """Every layout failure in a scene, each named by its cue."""
    private_media()
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
        if any(TEX.search(text) for text in labels(visual.model_dump())):
            name = getattr(visual, "component", "visual")
            errors.append(
                f"{entry.cue}: a {name} label shows TeX as plain text. "
                "Write plain symbols instead, such as e^(iθ)"
            )
            continue
        if isinstance(visual, Histogram) and (problems := histogram_problems(visual)):
            errors += [f"{entry.cue}: {problem}" for problem in problems]
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


def durations(script: Script, clips: list[Clip] | None) -> list[float]:
    """Each beat's length: its clip and a pause, or an estimate when no voice exists."""
    if clips is None:
        return [beat_seconds(beat.text) for beat in script.beats]
    return [round(clip.seconds + PAUSE, 2) for clip in clips]


class SegmentScene(Scene):
    """Plays a scene's visuals, one beat at a time, as long as the narration lasts."""

    def __init__(
        self,
        spec: SceneV0,
        script: Script,
        clips: list[Clip] | None = None,
        **kwargs: Any,
    ) -> None:
        self.spec, self.script, self.clips = spec, script, clips
        super().__init__(**kwargs)

    def construct(self) -> None:
        shown: dict[str, tuple[SceneEntry, VGroup]] = {}
        lengths = durations(self.script, self.clips)
        for index, entry in enumerate(self.spec.entries):
            seconds = lengths[index]
            if self.clips is not None:
                self.add_sound(str(self.clips[index].path))
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

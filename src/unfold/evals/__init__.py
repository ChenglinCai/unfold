"""Binary checks from the M4 error analysis. Each check passes or fails.

Error analysis came first, as principle IV requires: Claude read every golden
output, wrote open notes, and grouped them into failure types. Each check below
measures one type. `docs/evals/M4-report.md` gives their origin and pass rates.
"""

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from unfold.episodes.links import check_links
from unfold.formats import read_data
from unfold.formats.episode import OutlineV0
from unfold.script import load_script
from unfold.sources import load

WORDS_PER_EPISODE = 500
TOPIC_EPISODES = 3
# A voice speaks about 165 words a minute.
WORDS_PER_SECOND = 2.75
TOLERANCE = 0.3
# The source's own framing, such as "this course" or "the slides". The idiom
# "the course of" is fine.
FRAMING = re.compile(
    r"\b(?:this|these|the)\s+(?:whole\s+|entire\s+)?"
    r"(?:course|class|lectures?|article|slides?|deck|recording|textbook|chapter|handout)\b"
    r"(?!\s+of\b)",
    re.IGNORECASE,
)
CHECKS = (
    "plan-fits-source",
    "first-episode-reaches-title",
    "episode-stays-in-plan",
    "narration-fits-target",
    "beats-are-grounded",
    "no-source-framing",
    "storyboard-reuses-components",
    "scene-uses-components",
    "chart-numbers-grounded",
    "ideas-link",
)
UNITS = {
    w: n
    for n, w in enumerate(
        [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ]
    )
}
TENS = {
    w: 10 * n
    for n, w in enumerate(
        [
            "x",
            "x",
            "twenty",
            "thirty",
            "forty",
            "fifty",
            "sixty",
            "seventy",
            "eighty",
            "ninety",
        ]
    )
    if n > 1
}
SCALES = {"thousand": 1_000, "million": 1_000_000, "billion": 1_000_000_000}
DIGITS = re.compile(r"\d[\d,]*(?:\.\d+)?")


def plan_fits_source(episodes: int, words: int, topic: bool) -> bool:
    """At most one episode per 500 words of source, or 3 for a bare topic."""
    limit = TOPIC_EPISODES if topic else max(1, math.ceil(words / WORDS_PER_EPISODE))
    return episodes <= limit


STOP_WORDS = {"the", "of", "a", "an", "and", "to", "in", "on", "for", "s"}


def _words(text: str) -> set[str]:
    """Lower-case words without plural endings or stop words."""
    found = re.findall(r"[a-z0-9]+", text.lower())
    return {w[:-1] if len(w) > 3 and w.endswith("s") else w for w in found} - STOP_WORDS


def first_episode_reaches_title(title: str, concepts: list[str]) -> bool:
    """Episode 1 teaches a concept named in the source's title.

    A concept matches when it shares two words with the title, or all its
    words when it has only one.
    """
    wanted = _words(title)
    for concept in concepts:
        words = _words(concept.replace("-", " "))
        if words and len(words & wanted) >= min(2, len(words)):
            return True
    return False


def episode_stays_in_plan(establishes: list[str], later: set[str]) -> bool:
    """No segment teaches a concept that the plan gives to a later episode."""
    return not any(item.split(":", 1)[-1] in later for item in establishes)


def narration_fits_target(words: int, target_seconds: int) -> bool:
    """The narration lands within 30 percent of its target length."""
    target = target_seconds * WORDS_PER_SECOND
    return abs(words - target) <= TOLERANCE * target


def beats_are_grounded(anchors: dict[str, list[str]], topic: bool) -> bool:
    """At least half the beats cite an anchor. A bare topic has none to cite."""
    cited = sum(1 for refs in anchors.values() if refs)
    return topic or 2 * cited >= len(anchors)


def flagged_beats(anchors: dict[str, list[str]]) -> int:
    """Beats that cite no anchor. The maintainer reviews each one."""
    return sum(1 for refs in anchors.values() if not refs)


def count_flags(folder: Path) -> tuple[int, int]:
    """The flagged beats and all beats, across a series' scripts."""
    flagged = beats = 0
    for path in sorted(folder.glob("E*/s*/script.md")):
        anchors = load_script(path).anchors()
        flagged += flagged_beats(anchors)
        beats += len(anchors)
    return flagged, beats


def custom_share(folder: Path) -> tuple[int, int]:
    """The custom entries and all entries, across a series' scenes."""
    custom = entries = 0
    for path in sorted(folder.glob("E*/s*/scene.yaml")):
        found = yaml.safe_load(path.read_text(encoding="utf-8"))["entries"]
        custom += sum(1 for e in found if e["visual"]["component"] == "custom")
        entries += len(found)
    return custom, entries


def share_line(custom: int, entries: int) -> str:
    line = f"custom visuals: {custom} of {entries} beats"
    return f"{line} ({round(100 * custom / entries)} percent)" if entries else line


def no_source_framing(narration: str) -> bool:
    """The narration never speaks as if it were the source, such as "this course"."""
    return FRAMING.search(narration) is None


def storyboard_reuses_components(components: list[str]) -> bool:
    """At most half the entries need a custom visual."""
    custom = sum(1 for component in components if component == "custom")
    return 2 * custom <= len(components)


def numbers_in(text: str) -> set[float]:
    """Every number in a text, written in digits or in words."""
    found = {float(match.replace(",", "")) for match in DIGITS.findall(text)}
    current: int | None = None
    total = 0
    for word in [*re.findall(r"[a-z]+", text.lower()), "."]:
        if word in UNITS or word in TENS:
            current = (current or 0) + UNITS.get(word, TENS.get(word, 0))
        elif word == "hundred" and current is not None:
            current *= 100
        elif word in SCALES and current is not None:
            total, current = total + current * SCALES[word], 0
        elif word == "and" and current is not None:
            continue
        else:
            if current is not None:
                found.add(float(total + current))
            current, total = None, 0
    return found


def chart_numbers_grounded(values: list[float], said: str) -> bool:
    """Every number a chart shows appears in the narration or the storyboard."""
    known = numbers_in(said)
    return all(
        any(abs(v - k) <= max(0.01, 0.005 * abs(k)) for k in known) for v in values
    )


def chart_values(visuals: list[dict[str, Any]]) -> list[float]:
    """The numbers a model supplied to charts, which the narration must back."""
    values: list[float] = []
    for visual in visuals:
        kind = visual["component"]
        if kind == "bar-chart":
            values += visual["values"]
        elif kind == "timeline":
            values += [
                e["amount"] for e in visual["events"] if e.get("amount") is not None
            ]
        elif kind == "present-value":
            # Code computes each present value, so only the inputs need backing.
            values += [flow["amount"] for flow in visual["flows"]] + [visual["rate"]]
        elif kind == "histogram":
            # Counts describe a shape, so only the mean and the spread need backing.
            values += [
                visual[k] for k in ("mean", "spread") if visual.get(k) is not None
            ]
    return [abs(float(value)) for value in values]


def scene_uses_components(components: list[str]) -> bool:
    """At most half a scene's entries fall back to a custom card."""
    return storyboard_reuses_components(components)


def links_by_episode(outlines: list[OutlineV0], knows: set[str]) -> dict[str, bool]:
    """Whether every idea each episode needs comes from earlier, or is known."""
    errors = check_links(outlines, knows)
    return {
        o.episode: not any(e.startswith(f"{o.episode}/") for e in errors)
        for o in outlines
    }


@dataclass(frozen=True)
class Verdict:
    check: str
    subject: Path
    passed: bool


def evaluate(folder: Path) -> list[Verdict]:
    """Run every check on one built series."""
    series = yaml.safe_load((folder / "series.yaml").read_text(encoding="utf-8"))
    docs = [load((folder / name).resolve()) for name in series["sources"]]
    words = sum(len(a.text.split()) for doc in docs for a in doc.anchors)
    topic = all(doc.family == "topic" for doc in docs)
    plan_path = folder / "plan.yaml"
    episodes = yaml.safe_load(plan_path.read_text(encoding="utf-8"))["episodes"]
    fits = plan_fits_source(len(episodes), words, topic)
    verdicts = [Verdict("plan-fits-source", plan_path, fits)]
    title = " ".join(doc.title for doc in docs)
    reaches = first_episode_reaches_title(title, episodes[0]["concepts"])
    verdicts.append(Verdict("first-episode-reaches-title", plan_path, reaches))
    built = [
        OutlineV0.model_validate(read_data(folder / e["id"] / "outline.yaml"))
        for e in episodes
        if (folder / e["id"] / "outline.yaml").is_file()
    ]
    links = links_by_episode(built, set(series.get("knows") or []))
    verdicts += [
        Verdict("ideas-link", folder / episode / "outline.yaml", ok)
        for episode, ok in links.items()
    ]
    for index, episode in enumerate(episodes):
        outline_path = folder / episode["id"] / "outline.yaml"
        if not outline_path.is_file():
            continue
        outline = yaml.safe_load(outline_path.read_text(encoding="utf-8"))
        later = {c for e in episodes[index + 1 :] for c in e["concepts"]}
        later -= set(episode["concepts"])
        taught = [i for s in outline["segments"] for i in s.get("establishes") or []]
        stays = episode_stays_in_plan(taught, later)
        verdicts.append(Verdict("episode-stays-in-plan", outline_path, stays))
        for segment in outline["segments"]:
            verdicts += _segment(outline_path.parent / segment["id"], segment, topic)
    return verdicts


def _segment(folder: Path, segment: dict[str, object], topic: bool) -> list[Verdict]:
    script_path = folder / "script.md"
    if not script_path.is_file():
        return []
    script = load_script(script_path)
    narration = " ".join(beat.text for beat in script.beats)
    target = int(str(segment["target_seconds"]))
    verdicts = [
        Verdict(
            "narration-fits-target",
            script_path,
            narration_fits_target(len(narration.split()), target),
        ),
        Verdict(
            "beats-are-grounded",
            script_path,
            beats_are_grounded(script.anchors(), topic),
        ),
        Verdict("no-source-framing", script_path, no_source_framing(narration)),
    ]
    board_path = folder / "storyboard.yaml"
    if board_path.is_file():
        board = yaml.safe_load(board_path.read_text(encoding="utf-8"))
        components = [str(entry["component"]) for entry in board["entries"]]
        reuses = storyboard_reuses_components(components)
        verdicts.append(Verdict("storyboard-reuses-components", board_path, reuses))
    scene_path = folder / "scene.yaml"
    if scene_path.is_file():
        verdicts += _scene(scene_path, narration, board_path)
    return verdicts


def _scene(path: Path, narration: str, board_path: Path) -> list[Verdict]:
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))["entries"]
    visuals = [entry["visual"] for entry in entries]
    board = board_path.read_text(encoding="utf-8") if board_path.is_file() else ""
    said = f"{narration} {board}"
    return [
        Verdict(
            "scene-uses-components",
            path,
            scene_uses_components([v["component"] for v in visuals]),
        ),
        Verdict(
            "chart-numbers-grounded",
            path,
            chart_numbers_grounded(chart_values(visuals), said),
        ),
    ]

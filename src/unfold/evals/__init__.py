"""Binary checks from the M4 error analysis. Each check passes or fails.

Error analysis came first, as principle IV requires: Claude read every golden
output, wrote open notes, and grouped them into failure types. Each check below
measures one type. `docs/evals/M4-report.md` gives their origin and pass rates.
"""

import math
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

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
)


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


def no_source_framing(narration: str) -> bool:
    """The narration never speaks as if it were the source, such as "this course"."""
    return FRAMING.search(narration) is None


def storyboard_reuses_components(components: list[str]) -> bool:
    """At most half the entries need a custom visual."""
    custom = sum(1 for component in components if component == "custom")
    return 2 * custom <= len(components)


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
    return verdicts

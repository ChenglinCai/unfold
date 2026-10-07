"""A script file splits into beats, each with a cue and its narration."""

import pytest

from unfold.script import ScriptError, parse_script

SCRIPT = """---
segment: s1-neighbours-vote
episode: E01-knn
---

[[points]] Here are points of two kinds.

[[query]] A new point arrives.
How would you label it?
"""


def test_reads_the_front_matter() -> None:
    script = parse_script(SCRIPT)

    assert script.meta == {"segment": "s1-neighbours-vote", "episode": "E01-knn"}


def test_splits_beats_at_cues_and_joins_wrapped_lines() -> None:
    script = parse_script(SCRIPT)

    assert [beat.cue for beat in script.beats] == ["points", "query"]
    assert script.beats[1].text == "A new point arrives. How would you label it?"


def test_finds_a_beat_by_its_cue() -> None:
    assert parse_script(SCRIPT)["query"].text.startswith("A new point")


def test_rejects_a_beat_without_a_cue() -> None:
    with pytest.raises(ScriptError, match="cue"):
        parse_script("---\nsegment: s1\n---\n\nNo cue here.\n")


def test_rejects_a_repeated_cue() -> None:
    with pytest.raises(ScriptError, match="twice"):
        parse_script("---\nsegment: s1\n---\n\n[[a]] One.\n\n[[a]] Two.\n")


def test_script_v0_beats_have_no_anchors() -> None:
    script = parse_script("---\nformat: script/v0\n---\n\n[[one]] Hello.\n")

    assert script.anchors() == {"one": []}

"""Meaning checks: what a schema cannot see in each step's reply."""

from unfold.build.checks import (
    check_outline,
    check_plan,
    check_script,
    check_storyboard,
)
from unfold.build.replies import OutlineReply, PlanReply, ScriptReply, StoryboardReply

ANCHORS = {"demo#p-1", "demo#p-2"}


def plan(**episode: object) -> PlanReply:
    base = {"id": "E01-spread", "title": "Spread", "core_question": "Why?"}
    return PlanReply.model_validate(
        {"episodes": [{**base, "concepts": ["mean"], **episode}]}
    )


def test_a_plan_names_known_concepts_and_anchors() -> None:
    assert check_plan(plan(anchors=["demo#p-1"]), {"mean"}, ANCHORS) == []
    assert check_plan(plan(concepts=["median"]), {"mean"}, ANCHORS) == [
        "E01-spread: concept 'median' is in no knowledge map"
    ]
    assert check_plan(plan(anchors=["demo#p-9"]), {"mean"}, ANCHORS) == [
        "E01-spread: unknown anchor demo#p-9"
    ]


def outline(
    segments: list[dict[str, object]], transitions: list[dict[str, str]]
) -> OutlineReply:
    data = {"title": "Spread", "core_question": "Why?", "segments": segments}
    return OutlineReply.model_validate({**data, "transitions": transitions})


def segment(number: int, **fields: object) -> dict[str, object]:
    base = {"id": f"s{number}-part", "title": "Part", "target_seconds": 90}
    return {**base, "anchors": ["demo#p-1"], **fields}


def test_an_outline_has_unique_segments_and_real_transitions() -> None:
    good = outline(
        [segment(1), segment(2)],
        [{"from": "s1-part", "to": "s2-part", "idea": "Next."}],
    )
    assert check_outline(good, ANCHORS) == []

    bad = outline(
        [segment(1), segment(1, anchors=["demo#p-9"], target_seconds=900)],
        [{"from": "s1-part", "to": "s3-part", "idea": "Next."}],
    )
    assert check_outline(bad, ANCHORS) == [
        "segment s1-part appears twice",
        "s1-part: unknown anchor demo#p-9",
        "s1-part: 900 seconds is outside 30 to 300",
        "a transition names s3-part, which the outline lacks",
    ]


def script(*beats: tuple[str, str, list[str]]) -> ScriptReply:
    return ScriptReply.model_validate(
        {"beats": [{"cue": c, "text": t, "anchors": a} for c, t, a in beats]}
    )


GOOD_BEATS = [
    ("start", "Every list of numbers has a center.", ["demo#p-1"]),
    ("spread", "Some lists bunch up, and others spread out.", ["demo#p-2"]),
    ("end", "Next, we measure that spread.", []),
]


def test_a_script_resolves_anchors_and_speaks_plainly() -> None:
    assert check_script(script(*GOOD_BEATS), ANCHORS, topic=False) == []

    bad = script(
        (
            "start",
            "As slide 3 shows, the mean is the center (the average).",
            ["demo#p-9"],
        ),
        *GOOD_BEATS[1:],
    )
    errors = check_script(bad, ANCHORS, topic=False)
    assert errors[0] == "beat start: unknown anchor demo#p-9"
    assert any(
        error.startswith("beat start: ") and "slide" in error for error in errors
    )


def test_a_script_with_a_repeated_cue_fails() -> None:
    errors = check_script(script(*GOOD_BEATS, GOOD_BEATS[0]), ANCHORS, topic=False)

    assert "cue start appears twice" in errors


def test_a_bare_topic_script_cites_nothing() -> None:
    errors = check_script(script(*GOOD_BEATS), set(), topic=True)

    assert "beat start: a bare topic has no anchors to cite" in errors


def test_a_storyboard_follows_the_script_cues_in_order() -> None:
    entry = {"visual": "Dots on a line.", "component": "custom", "region": "plot"}
    board = StoryboardReply.model_validate(
        {"entries": [{"cue": "spread", **entry}, {"cue": "start", **entry}]}
    )

    assert check_storyboard(board, ["spread", "start"]) == []
    assert check_storyboard(board, ["start", "spread"]) == [
        "entries must follow the script's cues in order: start, spread"
    ]


def test_a_callback_may_name_a_segment_of_an_earlier_episode() -> None:
    callback = {"to": "s1-old", "visual": "timeline", "how": "It returns."}
    later = outline([segment(1), segment(2, callbacks=[callback])], [])

    assert check_outline(later, ANCHORS) == [
        "s2-part: a callback names s1-old, which the outline lacks"
    ]
    assert check_outline(later, ANCHORS, earlier={"s1-old"}) == []

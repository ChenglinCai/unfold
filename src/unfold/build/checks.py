"""Meaning checks for each step's reply: what a schema cannot see.

Each check returns a list of errors, and an empty list means the reply passes.
The errors go back to the model as feedback for its next try.
"""

from collections import Counter

from unfold.build.replies import OutlineReply, PlanReply, ScriptReply, StoryboardReply
from unfold.lint import lint_text
from unfold.lint.rules import ERROR

SECONDS = (30, 300)


def repeated(ids: list[str]) -> list[str]:
    return [item for item, count in Counter(ids).items() if count > 1]


def check_plan(reply: PlanReply, concepts: set[str], anchors: set[str]) -> list[str]:
    errors = [
        f"episode {id_} appears twice"
        for id_ in repeated([e.id for e in reply.episodes])
    ]
    for episode in reply.episodes:
        errors += [
            f"{episode.id}: concept {name!r} is in no knowledge map"
            for name in episode.concepts
            if name not in concepts
        ]
        errors += [
            f"{episode.id}: unknown anchor {a}"
            for a in episode.anchors
            if a not in anchors
        ]
    return errors


def check_outline(
    reply: OutlineReply,
    anchors: set[str],
    earlier: frozenset[str] | set[str] = frozenset(),
) -> list[str]:
    ids = [segment.id for segment in reply.segments]
    errors = [f"segment {id_} appears twice" for id_ in repeated(ids)]
    low, high = SECONDS
    for segment in reply.segments:
        errors += [
            f"{segment.id}: unknown anchor {a}"
            for a in segment.anchors
            if a not in anchors
        ]
        if not low <= segment.target_seconds <= high:
            errors.append(
                f"{segment.id}: {segment.target_seconds} seconds is outside {low} to {high}"
            )
        errors += [
            f"{segment.id}: a callback names {callback.to}, which the outline lacks"
            for callback in segment.callbacks
            if callback.to not in ids and callback.to not in earlier
        ]
    for transition in reply.transitions:
        errors += [
            f"a transition names {name}, which the outline lacks"
            for name in (transition.from_, transition.to)
            if name not in ids
        ]
    return errors


def check_script(reply: ScriptReply, anchors: set[str], topic: bool) -> list[str]:
    errors = [
        f"cue {cue} appears twice" for cue in repeated([b.cue for b in reply.beats])
    ]
    for beat in reply.beats:
        if topic and beat.anchors:
            errors.append(f"beat {beat.cue}: a bare topic has no anchors to cite")
        else:
            errors += [
                f"beat {beat.cue}: unknown anchor {a}"
                for a in beat.anchors
                if a not in anchors
            ]
        errors += [
            f'beat {beat.cue}: {finding.name}: {finding.message} "{finding.excerpt}"'
            for finding in lint_text(beat.text, "spoken")
            if finding.severity == ERROR
        ]
    return errors


def check_storyboard(reply: StoryboardReply, cues: list[str]) -> list[str]:
    if [entry.cue for entry in reply.entries] == cues:
        return []
    return [f"entries must follow the script's cues in order: {', '.join(cues)}"]

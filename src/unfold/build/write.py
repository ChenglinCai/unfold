"""Output files from checked replies, with the fields that code knows.

The model never writes `format`, `written_by`, or the ids that the build
already knows. Code adds them here, so each file passes its own schema.
"""

from collections.abc import Mapping

import yaml

from unfold.build.replies import (
    OutlineReply,
    PlanReply,
    SceneReply,
    ScriptReply,
    StoryboardReply,
)

VOICE = "default"


def yaml_text(data: Mapping[str, object], flow: bool = False) -> str:
    return yaml.safe_dump(
        dict(data),
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=None if flow else False,
    )


def by(model: str) -> str:
    return f"unfold build, model {model}"


def plan_text(reply: PlanReply, series: str, model: str) -> str:
    head = {"format": "series-plan/v0", "series": series, "written_by": by(model)}
    return yaml_text({**head, **reply.model_dump(mode="json")})


def outline_text(
    reply: OutlineReply, series: str, episode: str, audience: str, model: str
) -> str:
    data = reply.model_dump(mode="json", by_alias=True)
    head = {"format": "outline/v0", "series": series, "episode": episode}
    return yaml_text(
        {
            **head,
            "title": data["title"],
            "core_question": data["core_question"],
            "audience": audience,
            "written_by": by(model),
            "previously": [],
            "segments": data["segments"],
            "transitions": data["transitions"],
        }
    )


def script_text(reply: ScriptReply, episode: str, segment: str, model: str) -> str:
    front = {
        "format": "script/v1",
        "episode": episode,
        "segment": segment,
        "voice": VOICE,
        "written_by": by(model),
        "anchors": {beat.cue: beat.anchors for beat in reply.beats},
    }
    body = "\n\n".join(f"[[{b.cue}]] {' '.join(b.text.split())}" for b in reply.beats)
    return f"---\n{yaml_text(front, flow=True)}---\n\n{body}\n"


def storyboard_text(
    reply: StoryboardReply, episode: str, segment: str, model: str
) -> str:
    head = {"format": "storyboard/v0", "episode": episode, "segment": segment}
    return yaml_text({**head, "written_by": by(model), **reply.model_dump(mode="json")})


def scene_text(reply: SceneReply, episode: str, segment: str, model: str) -> str:
    head = {"format": "scene/v0", "episode": episode, "segment": segment}
    return yaml_text({**head, "written_by": by(model), **reply.model_dump(mode="json")})

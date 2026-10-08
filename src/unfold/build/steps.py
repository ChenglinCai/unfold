"""The four generation steps. Each turns its inputs into one job.

A step's request holds every input as text, so the job's key changes whenever
an input does. Source text sits inside tags, and each prompt says to treat it
as data.
"""

from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

import yaml
from pydantic import BaseModel

from unfold.build import Job
from unfold.build.checks import (
    check_outline,
    check_plan,
    check_script,
    check_storyboard,
)
from unfold.build.replies import (
    OutlineReply,
    PlanReply,
    SceneReply,
    ScriptReply,
    StoryboardReply,
)
from unfold.build.write import (
    outline_text,
    plan_text,
    scene_text,
    script_text,
    storyboard_text,
)
from unfold.formats.episode import OutlineV0, SceneV0, Segment
from unfold.formats.series import PlannedEpisode, SeriesV0
from unfold.script import Script
from unfold.sources import SourceDocument
from unfold.visuals import params

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


@dataclass(frozen=True)
class Source:
    folder: Path
    doc: SourceDocument
    knowledge_map: str
    notes: str


@dataclass(frozen=True)
class Context:
    """What every step of one series can read."""

    folder: Path
    spec: SeriesV0
    sources: list[Source]
    model: str

    @property
    def anchors(self) -> dict[str, tuple[str, str]]:
        """Each anchor reference, with its title and text."""
        return {
            f"{s.doc.id}#{a.id}": (a.title, a.text)
            for s in self.sources
            for a in s.doc.anchors
        }

    @property
    def concepts(self) -> set[str]:
        found: set[str] = set()
        for source in self.sources:
            data = yaml.safe_load(source.knowledge_map) or {}
            found |= {str(c["id"]) for c in data.get("concepts") or []}
        return found

    @property
    def topic(self) -> bool:
        return all(source.doc.family == "topic" for source in self.sources)

    def record(self, output: Path) -> Path:
        return self.folder / "records" / f"{output.relative_to(self.folder)}.json"


def prompt(name: str) -> str:
    return (PROMPTS / f"{name}.md").read_text(encoding="utf-8")


def as_yaml(model: BaseModel) -> str:
    data = model.model_dump(mode="json", by_alias=True, exclude_defaults=True)
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)


def materials(ctx: Context) -> str:
    """Every source's knowledge map and study notes."""
    parts = [
        f'<source id="{s.doc.id}" title="{s.doc.title}" family="{s.doc.family}">\n'
        f"<knowledge-map>\n{s.knowledge_map.strip()}\n</knowledge-map>\n"
        f"<study-notes>\n{s.notes.strip()}\n</study-notes>\n</source>"
        for s in ctx.sources
    ]
    return "\n\n".join(parts)


def plan_job(ctx: Context) -> Job:
    output = ctx.folder / "plan.yaml"
    request = f"Audience: {ctx.spec.audience}\n\n{materials(ctx)}"

    def check(reply: BaseModel) -> list[str]:
        assert isinstance(reply, PlanReply)
        return check_plan(reply, ctx.concepts, set(ctx.anchors))

    def render(reply: BaseModel) -> str:
        assert isinstance(reply, PlanReply)
        return plan_text(reply, ctx.spec.id, ctx.model)

    system = prompt("series-plan")
    return Job(
        "plan",
        output,
        ctx.record(output),
        system,
        request,
        PlanReply,
        ctx.model,
        check,
        render,
    )


def outline_job(
    ctx: Context,
    episode: PlannedEpisode,
    previously: str = "",
    earlier: frozenset[str] = frozenset(),
) -> Job:
    output = ctx.folder / episode.id / "outline.yaml"
    listing = "\n".join(f"- {ref}: {title}" for ref, (title, _) in ctx.anchors.items())
    request = (
        f"Audience: {ctx.spec.audience}\n\n<episode>\n{as_yaml(episode)}</episode>\n\n"
        f"{materials(ctx)}\n\nAnchors you may cite:\n{listing or '- none'}"
    )
    if previously:
        request += (
            f"\n\n<previously>\n{previously}</previously>\n\n"
            "The episodes in <previously> come before this one. Build on what they "
            "establish, and call back to their visuals. A callback may name one of "
            "their segments."
        )

    def check(reply: BaseModel) -> list[str]:
        assert isinstance(reply, OutlineReply)
        return check_outline(reply, set(ctx.anchors), earlier)

    def render(reply: BaseModel) -> str:
        assert isinstance(reply, OutlineReply)
        return outline_text(
            reply, ctx.spec.id, episode.id, ctx.spec.audience, ctx.model
        )

    system = prompt("outline")
    return Job(
        "outline",
        output,
        ctx.record(output),
        system,
        request,
        OutlineReply,
        ctx.model,
        check,
        render,
    )


def script_job(ctx: Context, outline: OutlineV0, segment: Segment) -> Job:
    output = ctx.folder / outline.episode / segment.id / "script.md"
    ids = [s.id for s in outline.segments]
    index = ids.index(segment.id)
    around = [
        f"Previous segment: {outline.segments[index - 1].title}" if index > 0 else "",
        f"Next segment: {outline.segments[index + 1].title}"
        if index + 1 < len(ids)
        else "",
    ]
    blocks = [
        f'<block anchor="{ref}" title="{ctx.anchors[ref][0]}">\n{ctx.anchors[ref][1]}\n</block>'
        for ref in segment.anchors
        if ref in ctx.anchors
    ]
    request = (
        f"Audience: {ctx.spec.audience}\nEpisode: {outline.title}\n"
        f"Core question: {outline.core_question}\n"
        + "\n".join(line for line in around if line)
        + f"\n\n<segment>\n{as_yaml(segment)}</segment>\n\n"
        + "\n\n".join(
            f"<knowledge-map>\n{s.knowledge_map.strip()}\n</knowledge-map>"
            for s in ctx.sources
        )
        + "\n\n"
        + ("\n\n".join(blocks) if blocks else "This segment has no source blocks.")
    )

    def check(reply: BaseModel) -> list[str]:
        assert isinstance(reply, ScriptReply)
        return check_script(reply, set(ctx.anchors), ctx.topic)

    def render(reply: BaseModel) -> str:
        assert isinstance(reply, ScriptReply)
        return script_text(reply, outline.episode, segment.id, ctx.model)

    system = prompt("narration")
    return Job(
        "script",
        output,
        ctx.record(output),
        system,
        request,
        ScriptReply,
        ctx.model,
        check,
        render,
    )


def storyboard_job(
    ctx: Context, outline: OutlineV0, segment: Segment, script: Script
) -> Job:
    output = ctx.folder / outline.episode / segment.id / "storyboard.yaml"
    beats = "\n\n".join(f"[[{beat.cue}]] {beat.text}" for beat in script.beats)
    request = f"<segment>\n{as_yaml(segment)}</segment>\n\n<script>\n{beats}\n</script>"
    cues = [beat.cue for beat in script.beats]

    def check(reply: BaseModel) -> list[str]:
        assert isinstance(reply, StoryboardReply)
        return check_storyboard(reply, cues)

    def render(reply: BaseModel) -> str:
        assert isinstance(reply, StoryboardReply)
        return storyboard_text(reply, outline.episode, segment.id, ctx.model)

    system = prompt("storyboard")
    return Job(
        "storyboard",
        output,
        ctx.record(output),
        system,
        request,
        StoryboardReply,
        ctx.model,
        check,
        render,
    )


def scene_job(
    ctx: Context, outline: OutlineV0, segment: Segment, script: Script, storyboard: str
) -> Job:
    output = ctx.folder / outline.episode / segment.id / "scene.yaml"
    beats = "\n\n".join(f"[[{beat.cue}]] {beat.text}" for beat in script.beats)
    # The versions sit in the request, so the key covers them, as principle II says.
    versions = (
        f"Components: version {params.VERSION}. manim: {metadata.version('manim')}."
    )
    request = (
        f"{versions}\n\n<script>\n{beats}\n</script>\n\n"
        f"<storyboard>\n{storyboard.strip()}\n</storyboard>"
    )
    cues = [beat.cue for beat in script.beats]

    def check(reply: BaseModel) -> list[str]:
        assert isinstance(reply, SceneReply)
        from unfold.visuals.scene import check_scene  # loads manim only when needed

        head = {"format": "scene/v0", "episode": outline.episode, "segment": segment.id}
        data = reply.model_dump(mode="json", by_alias=True)
        scene = SceneV0.model_validate({**head, **data})
        return check_scene(scene, cues)

    def render(reply: BaseModel) -> str:
        assert isinstance(reply, SceneReply)
        return scene_text(reply, outline.episode, segment.id, ctx.model)

    system = prompt("scene")
    return Job(
        "scene",
        output,
        ctx.record(output),
        system,
        request,
        SceneReply,
        ctx.model,
        check,
        render,
    )

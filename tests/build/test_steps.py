"""Each step builds its job's request from its inputs, and renders its output."""

from pathlib import Path

import yaml

from unfold.build.replies import PlanReply, ScriptReply
from unfold.build.steps import (
    Context,
    Source,
    outline_job,
    plan_job,
    script_job,
    storyboard_job,
)
from unfold.formats import problems
from unfold.formats.episode import OutlineV0
from unfold.formats.series import SeriesV0
from unfold.script import parse_script
from unfold.sources import Anchor, SourceDocument

MAP = """format: knowledge-map/v0
source: demo
concepts:
  - {id: mean, name: mean, meaning: The center., requires: [], anchors: [demo#p-1]}
claims: []
gaps: []
suspected_errors: []
"""
OUTLINE = OutlineV0.model_validate(
    {
        "format": "outline/v0",
        "series": "spread",
        "episode": "E01-center",
        "title": "The center",
        "core_question": "Where is the middle?",
        "audience": "Adults.",
        "segments": [
            {
                "id": "s1-mean",
                "title": "Mean",
                "target_seconds": 60,
                "anchors": ["demo#p-1"],
            },
            {"id": "s2-spread", "title": "Spread", "target_seconds": 60},
        ],
    }
)


def context(tmp_path: Path, family: str = "textbook") -> Context:
    anchors = [
        Anchor("p-1", "page", "Page 1", "The mean is the sum over the count."),
        Anchor("p-2", "page", "Page 2", "Variance squares each distance."),
    ]
    doc = SourceDocument("demo", "Demo", family, "demo.pdf", {}, {}, anchors)
    spec = SeriesV0.model_validate(
        {"format": "series/v0", "id": "spread", "audience": "Adults.", "sources": ["s"]}
    )
    source = Source(tmp_path / "s", doc, MAP, "# Notes\n\nThe mean is the center.\n")
    return Context(tmp_path / "series", spec, [source], "sonnet")


def test_the_plan_request_holds_the_audience_maps_and_notes(tmp_path: Path) -> None:
    job = plan_job(context(tmp_path))

    assert job.output == tmp_path / "series" / "plan.yaml"
    assert job.record == tmp_path / "series" / "records" / "plan.yaml.json"
    assert "Adults." in job.request
    assert "id: mean" in job.request
    assert "The mean is the center." in job.request
    reply = PlanReply.model_validate(
        {
            "episodes": [
                {
                    "id": "E01-center",
                    "title": "C",
                    "core_question": "Q?",
                    "concepts": ["mean"],
                }
            ]
        }
    )
    assert job.check(reply) == []
    assert yaml.safe_load(job.render(reply))["series"] == "spread"


def test_the_outline_request_lists_the_anchors_it_may_cite(tmp_path: Path) -> None:
    episode = PlanReply.model_validate(
        {
            "episodes": [
                {
                    "id": "E01-center",
                    "title": "C",
                    "core_question": "Q?",
                    "concepts": ["mean"],
                }
            ]
        }
    ).episodes[0]

    job = outline_job(context(tmp_path), episode)

    assert job.output == tmp_path / "series" / "E01-center" / "outline.yaml"
    assert "- demo#p-2: Page 2" in job.request


def test_a_script_request_holds_only_the_cited_blocks(tmp_path: Path) -> None:
    job = script_job(context(tmp_path), OUTLINE, OUTLINE.segments[0])

    assert job.output == tmp_path / "series" / "E01-center" / "s1-mean" / "script.md"
    assert "The mean is the sum over the count." in job.request
    assert "Variance squares each distance." not in job.request
    assert "Next segment: Spread" in job.request


def test_a_bare_topic_script_request_says_there_is_no_source(tmp_path: Path) -> None:
    job = script_job(context(tmp_path, family="topic"), OUTLINE, OUTLINE.segments[1])

    assert "no source blocks" in job.request


def test_the_storyboard_request_holds_the_beats(tmp_path: Path) -> None:
    reply = ScriptReply.model_validate(
        {
            "beats": [
                {"cue": "one", "text": "First.", "anchors": []},
                {"cue": "two", "text": "Second.", "anchors": []},
                {"cue": "three", "text": "Third.", "anchors": []},
            ]
        }
    )
    ctx = context(tmp_path)
    script_path = script_job(ctx, OUTLINE, OUTLINE.segments[0]).output
    script_path.parent.mkdir(parents=True)
    script_path.write_text(script_job(ctx, OUTLINE, OUTLINE.segments[0]).render(reply))
    assert problems(script_path) == []

    job = storyboard_job(
        ctx, OUTLINE, OUTLINE.segments[0], parse_script(script_path.read_text())
    )

    assert "[[two]] Second." in job.request
    assert job.output.name == "storyboard.yaml"

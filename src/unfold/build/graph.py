"""The build graph: run each step of a series in order, up to a chosen step.

A series folder holds the user's `series.yaml`. The build writes a plan, then
the first episodes' outlines, then each segment's script and storyboard, up to
the limits in the series file. `specs/004-text-generation/` holds the design.
"""

import datetime
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import ValidationError

from unfold import jobs
from unfold.build import RETRIES, Job, append_log, run_job
from unfold.build.steps import (
    Context,
    Source,
    outline_job,
    plan_job,
    scene_job,
    script_job,
    storyboard_job,
)
from unfold.formats import describe, read_data
from unfold.formats.episode import OutlineV0
from unfold.formats.series import SeriesPlanV0, SeriesV0
from unfold.script import load_script
from unfold.sources import load
from unfold.understand import MAP_FILE, NOTES_FILE, understand

STEPS = ("understand", "plan", "outline", "script", "storyboard", "scene")
CANARY_KEY = jobs.key(
    "canary", jobs.CANARY_MODEL, json.dumps(jobs.CANARY_SCHEMA, sort_keys=True)
)


class SeriesError(ValueError):
    """The series file is missing, or breaks its schema."""


@dataclass(frozen=True)
class Line:
    output: Path
    status: str


@dataclass
class Result:
    lines: list[Line] = field(default_factory=list)
    failed: bool = False
    # What the series' limits left out, such as later episodes.
    notes: list[str] = field(default_factory=list)

    def add(self, output: Path, status: str) -> bool:
        self.lines.append(Line(output, status))
        self.failed = status == "failed"
        return not self.failed


def read_series(folder: Path) -> SeriesV0:
    try:
        data = yaml.safe_load((folder / "series.yaml").read_text(encoding="utf-8"))
        return SeriesV0.model_validate(data)
    except OSError as error:
        raise SeriesError(f"{folder} has no series.yaml: {error}") from error
    except ValidationError as error:
        raise SeriesError("; ".join(describe(d) for d in error.errors())) from error


def logged(
    runner: jobs.Runner, lines: list[dict[str, object]], step: str, output: Path
) -> jobs.Runner:
    """A runner that keeps one call-log line per call, for the caller to write."""

    def call(
        prompt: str,
        *,
        system: str,
        model: str,
        schema: Mapping[str, object] | None = None,
    ) -> jobs.Reply:
        line: dict[str, object] = {
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "step": step,
            "output": str(output),
            "model": model,
        }
        try:
            reply = runner(prompt, system=system, model=model, schema=schema)
        except jobs.JobError as error:
            lines.append({**line, "outcome": "failed", "errors": [str(error)]})
            raise
        tokens = {
            "input_tokens": reply.input_tokens,
            "output_tokens": reply.output_tokens,
        }
        lines.append(
            {**line, **tokens, "seconds": reply.seconds, "outcome": "answered"}
        )
        return reply

    return call


class Guarded:
    """A runner that proves itself with the canary before its first real call."""

    def __init__(self, runner: jobs.Runner, log: Path) -> None:
        self.runner, self.log, self.proven = runner, log, False

    def __call__(
        self,
        prompt: str,
        *,
        system: str,
        model: str,
        schema: Mapping[str, object] | None = None,
    ) -> jobs.Reply:
        if not self.proven:
            now = datetime.datetime.now().isoformat(timespec="seconds")
            line: dict[str, object] = {
                "time": now,
                "step": "canary",
                "key": CANARY_KEY,
                "model": jobs.CANARY_MODEL,
            }
            try:
                reply = jobs.canary(self.runner)
            except jobs.CanaryError as error:
                append_log(
                    self.log, {**line, "outcome": "failed", "errors": [str(error)]}
                )
                raise
            tokens = {
                "input_tokens": reply.input_tokens,
                "output_tokens": reply.output_tokens,
            }
            append_log(
                self.log, {**line, **tokens, "seconds": reply.seconds, "outcome": "ok"}
            )
            self.proven = True
        return self.runner(prompt, system=system, model=model, schema=schema)


def build(
    folder: Path,
    runner: jobs.Runner,
    until: str = "scene",
    model: str | None = None,
    retries: int = RETRIES,
) -> Result:
    """Run the steps of one series in order, and stop after `until`."""
    spec = read_series(folder)
    model = model or spec.model
    log = folder / "calls.jsonl"
    runner = Guarded(runner, log)
    result = Result()
    sources = []
    for name in spec.sources:
        path = (folder / name).resolve()
        pending: list[dict[str, object]] = []
        understood = understand(
            path,
            runner=logged(runner, pending, "understand", path),
            model=model,
            retries=retries,
        )
        for line in pending:
            append_log(log, {**line, "key": understood.record.key})
        ok = understood.record.outcome == "ok"
        status = "reused" if understood.reused else "written" if ok else "failed"
        if not result.add(understood.folder, status):
            return result
        text = (understood.folder / MAP_FILE).read_text(encoding="utf-8")
        notes = (understood.folder / NOTES_FILE).read_text(encoding="utf-8")
        sources.append(Source(path, load(path), text, notes))
    if until == "understand":
        return result
    ctx = Context(folder, spec, sources, model)

    def run(job: Job) -> bool:
        outcome = run_job(job, runner, retries, log)
        ok = outcome.record.outcome == "ok"
        return result.add(
            job.output, "reused" if outcome.reused else "written" if ok else "failed"
        )

    if not run(plan_job(ctx)) or until == "plan":
        return result
    plan = SeriesPlanV0.model_validate(read_data(folder / "plan.yaml"))
    if len(plan.episodes) > spec.episodes:
        count = f"{spec.episodes} of {len(plan.episodes)}"
        result.notes.append(f"plan.yaml: building {count} episodes")
    for episode in plan.episodes[: spec.episodes]:
        job = outline_job(ctx, episode)
        if not run(job):
            return result
        if until == "outline":
            continue
        outline = OutlineV0.model_validate(read_data(job.output))
        if len(outline.segments) > spec.segments:
            place = job.output.relative_to(folder)
            count = f"{spec.segments} of {len(outline.segments)}"
            result.notes.append(f"{place}: building {count} segments")
        for segment in outline.segments[: spec.segments]:
            job = script_job(ctx, outline, segment)
            if not run(job):
                return result
            if until == "script":
                continue
            script = load_script(job.output)
            board = storyboard_job(ctx, outline, segment, script)
            if not run(board):
                return result
            if until == "storyboard":
                continue
            text = board.output.read_text(encoding="utf-8")
            if not run(scene_job(ctx, outline, segment, script, text)):
                return result
    return result

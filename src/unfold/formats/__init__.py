"""Schemas for every file format: one Pydantic model per format and version.

`docs/formats.md` describes each format, and `schemas/` holds the exported JSON
Schema files. `unfold check` validates files with these models.
"""

import json
from pathlib import Path

import yaml
from pydantic import BaseModel, ValidationError
from pydantic_core import ErrorDetails

from unfold.formats.episode import (
    OutlineV0,
    SceneV0,
    ScriptV0,
    ScriptV1,
    StoryboardV0,
)
from unfold.formats.series import LedgerV0, SeriesPlanV0, SeriesV0
from unfold.formats.sources import JobV0, KnowledgeMapV0, SourceV0, SourceV1
from unfold.script import ScriptError, parse_script

FORMATS: dict[str, type[BaseModel]] = {
    "source/v0": SourceV0,
    "source/v1": SourceV1,
    "knowledge-map/v0": KnowledgeMapV0,
    "job/v0": JobV0,
    "series/v0": SeriesV0,
    "series-plan/v0": SeriesPlanV0,
    "outline/v0": OutlineV0,
    "script/v0": ScriptV0,
    "script/v1": ScriptV1,
    "storyboard/v0": StoryboardV0,
    "scene/v0": SceneV0,
    "ledger/v0": LedgerV0,
}


class FormatError(ValueError):
    """A file names no format, or a format that has no schema."""


def read_data(path: Path) -> dict[str, object]:
    """Read a file's data: YAML, a job record, or a script with its beats."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        script = parse_script(text)
        beats = [{"cue": beat.cue, "text": beat.text} for beat in script.beats]
        return {**script.meta, "beats": beats}
    data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        raise FormatError(f"{path} holds no mapping")
    if path.suffix == ".json" and "format" not in data and "key" in data:
        data = {"format": "job/v0", **data}  # M2 wrote records with no format
    return data


def built_segments(series: Path) -> list[Path]:
    """Each episode's segment folders, in the order that its outline gives.

    A rebuilt outline can drop a segment whose folder stays on disk, so the outline
    decides. An episode without an outline keeps every segment folder.
    """
    found: list[Path] = []
    for episode in sorted(path for path in series.glob("E*") if path.is_dir()):
        outline = episode / "outline.yaml"
        if not outline.is_file():
            found += sorted(path for path in episode.glob("s*") if path.is_dir())
            continue
        listed = read_data(outline).get("segments")
        ids = (
            [s.get("id") for s in listed if isinstance(s, dict)]
            if isinstance(listed, list)
            else []
        )
        found += [episode / str(i) for i in ids if (episode / str(i)).is_dir()]
    return found


def model_for(data: dict[str, object]) -> type[BaseModel]:
    name = data.get("format")
    if not name:
        raise FormatError("the file names no format")
    if name not in FORMATS:
        raise FormatError(f"no schema exists for the format {name}")
    return FORMATS[str(name)]


def load_any(path: Path) -> BaseModel:
    """Read a file and validate it against its format's schema."""
    data = read_data(path)
    return model_for(data).model_validate(data)


def problems(path: Path) -> list[str]:
    """Every way a file breaks its format's schema, each with its place."""
    try:
        data = read_data(path)
    except ScriptError as error:
        return [str(error)]
    try:
        model_for(data).model_validate(data)
    except ValidationError as error:
        return [describe(detail) for detail in error.errors()]
    return []


def describe(detail: ErrorDetails) -> str:
    place = ".".join(str(part) for part in detail["loc"])
    return f"{place}: {detail['msg']}" if place else detail["msg"]

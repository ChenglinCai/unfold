"""The files in schemas/ match the models, so readers always see current schemas."""

import json
from pathlib import Path

from unfold.formats import FORMATS
from unfold.formats.export import file_name, schema_of

SCHEMAS = Path(__file__).resolve().parents[2] / "schemas"
FIX = "run: uv run python -m unfold.formats.export"


def test_every_format_has_a_current_schema_file() -> None:
    for name, model in FORMATS.items():
        path = SCHEMAS / file_name(name)
        assert path.is_file(), f"{path} is missing; {FIX}"
        assert json.loads(path.read_text()) == schema_of(name, model), (
            f"{path} is stale; {FIX}"
        )


def test_every_schema_file_belongs_to_a_format() -> None:
    expected = {file_name(name) for name in FORMATS}

    assert {path.name for path in SCHEMAS.glob("*.json")} == expected


def test_file_names_carry_the_version() -> None:
    assert file_name("outline/v0") == "outline.v0.json"
    assert file_name("knowledge-map/v0") == "knowledge-map.v0.json"

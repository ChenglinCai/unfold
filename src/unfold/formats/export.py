"""Write each format's JSON Schema into a folder, `schemas/` by default.

Run `uv run python -m unfold.formats.export` after changing a model.
`tests/formats/test_export.py` fails until the files match the models.
"""

import json
import sys
from pathlib import Path

from pydantic import BaseModel

from unfold.formats import FORMATS

DIALECT = "https://json-schema.org/draft/2020-12/schema"


def file_name(format_name: str) -> str:
    """outline/v0 becomes outline.v0.json."""
    return format_name.replace("/", ".") + ".json"


def schema_of(format_name: str, model: type[BaseModel]) -> dict[str, object]:
    return {
        "$schema": DIALECT,
        "$id": file_name(format_name),
        **model.model_json_schema(),
    }


def export(folder: Path) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for name, model in FORMATS.items():
        path = folder / file_name(name)
        text = json.dumps(schema_of(name, model), indent=2, ensure_ascii=False)
        path.write_text(text + "\n", encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    for path in export(Path(sys.argv[1] if len(sys.argv) > 1 else "schemas")):
        print(path)

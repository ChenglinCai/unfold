"""The format hook formats Python files inside the project, and nothing else."""

from pathlib import Path
from typing import Any

MESSY = "import sys\nimport os\nx=1\n"


def edit_event(path: Path) -> dict[str, object]:
    return {"hook_event_name": "PostToolUse", "tool_input": {"file_path": str(path)}}


def test_formats_a_python_file(run_hook: Any, tmp_path: Path) -> None:
    source = tmp_path / "messy.py"
    source.write_text(MESSY)

    result = run_hook("format_python", edit_event(source), tmp_path)

    assert result.returncode == 0, result.stderr
    text = source.read_text()
    assert text.index("import os") < text.index("import sys")
    assert "x = 1" in text


def test_leaves_other_file_types_alone(run_hook: Any, tmp_path: Path) -> None:
    notes = tmp_path / "notes.md"
    notes.write_text(MESSY)

    result = run_hook("format_python", edit_event(notes), tmp_path)

    assert result.returncode == 0
    assert notes.read_text() == MESSY


def test_leaves_files_outside_the_project_alone(run_hook: Any, tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text(MESSY)

    result = run_hook("format_python", edit_event(outside), project)

    assert result.returncode == 0
    assert outside.read_text() == MESSY


def test_shows_syntax_errors_to_claude(run_hook: Any, tmp_path: Path) -> None:
    broken = tmp_path / "broken.py"
    broken.write_text("def broken(:\n")

    result = run_hook("format_python", edit_event(broken), tmp_path)

    assert result.returncode == 2
    assert result.stderr.strip()

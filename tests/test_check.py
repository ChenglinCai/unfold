"""`unfold check` validates each file against its format, and folders file by file."""

import json
from pathlib import Path

import pytest

from unfold.cli import main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "econ-supply-demand"


def test_the_examples_pass(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", str(EXAMPLES)]) == 0
    assert capsys.readouterr().out.strip().endswith("5 files, 0 problems")


def test_a_broken_file_fails_and_names_the_place(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "outline.yaml"
    text = (EXAMPLES / "outline.yaml").read_text()
    path.write_text(text.replace("core_question:", "question:"))

    assert main(["check", str(path)]) == 1
    assert f"{path}: core_question: Field required" in capsys.readouterr().out


def test_a_file_with_an_unknown_format_is_a_usage_error(tmp_path: Path) -> None:
    path = tmp_path / "poem.yaml"
    path.write_text("format: poem/v9\n")

    assert main(["check", str(path)]) == 2


def test_a_missing_path_is_a_usage_error(tmp_path: Path) -> None:
    assert main(["check", str(tmp_path / "nothing.yaml")]) == 2


def test_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["check", "--format", "json", str(EXAMPLES / "outline.yaml")]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report == {"files": 1, "problems": [], "unknown": []}


def test_folders_skip_rendered_media(tmp_path: Path) -> None:
    (tmp_path / "media").mkdir()
    (tmp_path / "media" / "frames.yaml").write_text("no: format\n")
    (tmp_path / "outline.yaml").write_text((EXAMPLES / "outline.yaml").read_text())

    assert main(["check", str(tmp_path)]) == 0


def test_a_folder_reached_through_dot_dot_still_counts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "series").mkdir()
    (tmp_path / "series" / "outline.yaml").write_text(
        (EXAMPLES / "outline.yaml").read_text()
    )

    assert main(["check", str(tmp_path / "series" / ".." / "series")]) == 0
    assert capsys.readouterr().out.strip().endswith("1 file, 0 problems")

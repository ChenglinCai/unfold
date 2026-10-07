"""`unfold lint` follows specs/002-language/contracts/cli.md."""

import json
from pathlib import Path

import pytest

from unfold.cli import main

LONG = " ".join(["word"] * 30) + "."


def write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_clean_file_exits_0(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    doc = write(tmp_path / "ok.md", "Short and clear.\n")

    assert main(["lint", str(doc)]) == 0
    assert "0 errors, 0 warnings in 1 file" in capsys.readouterr().out


def test_errors_exit_1_and_print_one_line_each(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = write(tmp_path / "bad.md", f"Fine.\n\n{LONG}\n")

    assert main(["lint", str(doc)]) == 1
    first = capsys.readouterr().out.splitlines()[0]
    assert first.startswith(f"{doc}:3: error N101 sentence-length: 30 words")


def test_warnings_alone_exit_0(tmp_path: Path) -> None:
    doc = write(tmp_path / "warn.md", "It works (mostly).\n")

    assert main(["lint", str(doc)]) == 0


def test_json_output_matches_the_contract(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = write(tmp_path / "bad.md", f"{LONG}\n")

    main(["lint", "--format", "json", str(doc)])
    report = json.loads(capsys.readouterr().out)

    assert report["profile"] == "written"
    assert report["errors"] == 1
    assert report["warnings"] == 0
    finding = report["findings"][0]
    assert set(finding) >= {
        "rule",
        "name",
        "severity",
        "path",
        "line",
        "excerpt",
        "message",
    }


def test_a_directory_means_its_markdown_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write(tmp_path / "a.md", "Fine.\n")
    (tmp_path / "sub").mkdir()
    write(tmp_path / "sub" / "b.md", "Also fine.\n")
    write(tmp_path / "skip.txt", f"{LONG}\n")

    assert main(["lint", str(tmp_path)]) == 0
    assert "in 2 files" in capsys.readouterr().out


def test_a_missing_path_exits_2(tmp_path: Path) -> None:
    assert main(["lint", str(tmp_path / "nope.md")]) == 2


def test_an_unreadable_file_is_an_error_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    doc = tmp_path / "binary.md"
    doc.write_bytes(b"\xff\xfe\x00bad")

    assert main(["lint", str(doc)]) == 1
    assert "N900" in capsys.readouterr().out

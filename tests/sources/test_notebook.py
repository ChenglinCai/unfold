"""Jupyter notebooks become Markdown: their text, their code, and their printed output."""

import json
from pathlib import Path

import pytest

from unfold.cli import main
from unfold.sources import Meta, load
from unfold.sources.notebook import notebook_markdown, read_notebook

META = Meta(
    id="nb", title="Regression", family="web", origin="fit.ipynb", license="CC BY 4.0"
)
FENCE = "```"
NOTEBOOK: dict[str, object] = {
    "nbformat": 4,
    "metadata": {"kernelspec": {"language": "python", "name": "python3"}},
    "cells": [
        {
            "cell_type": "markdown",
            "source": ["# Least squares\n", "\n", "We fit a line."],
        },
        {
            "cell_type": "code",
            "source": "# the slope\nslope = 2\nprint(slope)",
            "outputs": [{"output_type": "stream", "name": "stdout", "text": ["2\n"]}],
        },
        {"cell_type": "raw", "source": "skip me"},
        {"cell_type": "markdown", "source": "## Residuals\n\nThe gaps to the line."},
    ],
}


def test_cells_become_markdown_with_fenced_code_and_output() -> None:
    text = notebook_markdown(NOTEBOOK)

    assert "# Least squares" in text and "We fit a line." in text
    assert f"{FENCE}python\n# the slope\nslope = 2\nprint(slope)\n{FENCE}" in text
    assert f"{FENCE}text\n2\n{FENCE}" in text
    assert "skip me" not in text


def test_long_output_is_cut_short() -> None:
    printed = "".join(f"{n}\n" for n in range(100))
    output = {"output_type": "stream", "name": "stdout", "text": printed}
    cell = {"cell_type": "code", "source": "print(n)", "outputs": [output]}

    text = notebook_markdown({"metadata": {}, "cells": [cell]})

    assert "\n19\n" in text and "\n20\n" not in text
    assert "80 more lines" in text


def test_headings_become_anchors_and_code_comments_do_not(tmp_path: Path) -> None:
    path = tmp_path / "fit.ipynb"
    path.write_text(json.dumps(NOTEBOOK))

    doc = read_notebook(path, META)

    assert [a.id for a in doc.anchors] == ["least-squares", "residuals"]
    assert doc.profile["format"] == "ipynb"


def test_ingest_reads_a_notebook(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "fit.ipynb"
    path.write_text(json.dumps(NOTEBOOK))
    out = tmp_path / "sources"

    assert main(["ingest", str(path), "--out", str(out), "--license", "CC BY 4.0"]) == 0

    doc = load(out / "fit")
    assert doc.family == "web"
    assert [a.id for a in doc.anchors] == ["least-squares", "residuals"]

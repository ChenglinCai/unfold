"""Jupyter notebooks: Markdown cells stay text, and code cells become fenced code.

A code cell's printed output follows it, cut to its first 20 lines, because an
explainer quotes results, not pages of numbers. Images in the output stay out.
"""

import json
from pathlib import Path
from typing import Any

from unfold.sources import Meta, SourceDocument
from unfold.sources.web import _document

LINES = 20


def _joined(value: object) -> str:
    """A notebook stores text as one string or as a list of lines."""
    return "".join(value) if isinstance(value, list) else str(value or "")


def _printed(output: dict[str, Any]) -> str:
    if output.get("output_type") == "stream":
        return _joined(output.get("text"))
    if output.get("output_type") in ("execute_result", "display_data"):
        return _joined((output.get("data") or {}).get("text/plain"))
    return ""


def notebook_markdown(notebook: dict[str, Any]) -> str:
    """The notebook as Markdown, cell by cell."""
    kernel = (notebook.get("metadata") or {}).get("kernelspec") or {}
    language = kernel.get("language") or "python"
    parts = []
    for cell in notebook.get("cells") or []:
        source = _joined(cell.get("source")).strip()
        if not source:
            continue
        if cell.get("cell_type") == "markdown":
            parts.append(source)
        elif cell.get("cell_type") == "code":
            parts.append(f"```{language}\n{source}\n```")
            printed = "".join(_printed(o) for o in cell.get("outputs") or []).strip(
                "\n"
            )
            if printed:
                lines = printed.split("\n")
                kept = "\n".join(lines[:LINES])
                if len(lines) > LINES:
                    kept += f"\n... {len(lines) - LINES} more lines"
                parts.append(f"```text\n{kept}\n```")
    return "\n\n".join(parts) + "\n"


def read_notebook(path: Path, meta: Meta) -> SourceDocument:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return _document(notebook_markdown(notebook), meta, "ipynb")

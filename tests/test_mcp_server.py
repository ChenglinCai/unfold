"""The MCP server offers unfold's commands as tools for Claude Code."""

import asyncio
import inspect
from pathlib import Path

import pytest

pytest.importorskip("mcp")

from unfold import mcp_server

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "econ-supply-demand"


def settle(value: object) -> object:
    return asyncio.run(value) if inspect.isawaitable(value) else value  # type: ignore[arg-type]


def test_the_server_offers_the_unfold_tools() -> None:
    tools = settle(mcp_server.server.list_tools())
    assert isinstance(tools, list)

    names = {tool.name for tool in tools}

    assert {
        "doctor",
        "ingest",
        "check",
        "build",
        "render",
        "review",
        "evaluate",
        "translate",
    } <= names


def test_the_check_tool_runs_unfold_check() -> None:
    result = settle(mcp_server.server.call_tool("check", {"path": str(EXAMPLES)}))

    assert "5 files, 0 problems" in str(result)


def test_the_ingest_tool_writes_a_source_document(tmp_path: Path) -> None:
    note = tmp_path / "interest.md"
    note.write_text(
        "# Interest\n\n" + "Interest earns interest, so savings grow faster. " * 5
    )
    out = tmp_path / "sources"
    request = {"source": str(note), "out": str(out), "license": "CC BY 4.0"}

    result = settle(mcp_server.server.call_tool("ingest", request))

    assert "exit code 0" in str(result)
    assert (out / "interest" / "source.yaml").is_file()


def test_a_tool_argument_never_becomes_an_option() -> None:
    result = str(settle(mcp_server.server.call_tool("check", {"path": "--help"})))

    assert "usage:" not in result
    assert "exit code 2" in result

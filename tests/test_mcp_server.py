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

    assert {"doctor", "check", "build", "render", "review", "evaluate"} <= names


def test_the_check_tool_runs_unfold_check() -> None:
    result = settle(mcp_server.server.call_tool("check", {"path": str(EXAMPLES)}))

    assert "5 files, 0 problems" in str(result)

"""The MCP server: unfold's commands as tools for Claude Code. Needs the mcp extra.

Each tool runs its command in a subprocess, because MCP's stdio transport owns
standard output, and a render worker could otherwise print into it.
"""

import subprocess
import sys

from mcp.server.mcpserver import MCPServer  # pyright: ignore[reportMissingImports]

server = MCPServer(
    "unfold",
    instructions=(
        "Turn learning material into explainer videos. Run doctor first. "
        "Build runs model jobs on the user's own Claude subscription."
    ),
)


def unfold(*args: str, timeout: float = 3600) -> str:
    """Run one unfold command, and return its exit code and output.

    Callers put `--` before positional values, so a value never becomes an option.
    """
    result = subprocess.run(
        [sys.executable, "-m", "unfold.cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return f"exit code {result.returncode}\n{result.stdout}{result.stderr}".strip()


@server.tool()
def doctor() -> str:
    """Check the programs and packages that unfold needs, with a fix for each gap."""
    return unfold("doctor")


@server.tool()
def ingest(
    source: str,
    out: str,
    license: str = "",
    owner: str = "",
    attribution: str = "",
    family: str = "",
    title: str = "",
) -> str:
    """Turn a file, a URL, or a topic into a source document in a private folder.

    The license decides whether videos from the source may be public, and an
    unknown license keeps them private. Set family to topic for a bare topic.
    """
    options = {
        "--license": license,
        "--owner": owner,
        "--attribution": attribution,
        "--family": family,
        "--title": title,
    }
    given = [part for flag, value in options.items() if value for part in (flag, value)]
    return unfold("ingest", "--out", out, *given, "--", source)


@server.tool()
def check(path: str) -> str:
    """Validate a file, or every file in a folder, against unfold's schemas."""
    return unfold("check", "--", path)


@server.tool()
def build(series: str, until: str = "scene") -> str:
    """Build a series folder up to a step, such as outline or scene.

    It runs model jobs on the user's own Claude subscription, and reuses every
    saved result whose inputs have not changed.
    """
    return unfold("build", "--until", until, "--", series)


@server.tool()
def render(series: str, check_audio: bool = False) -> str:
    """Render a series into segment videos, contact sheets, and stitched episodes."""
    return unfold("render", *(["--check-audio"] if check_audio else []), "--", series)


@server.tool()
def review(series: str) -> str:
    """Write review.html for a series, and return its path."""
    return unfold("review", "--", series)


@server.tool()
def evaluate(series: str) -> str:
    """Run the binary checks on a built series, and list each failure."""
    return unfold("eval", "--failures", "--", series)


def serve() -> None:
    server.run(transport="stdio")

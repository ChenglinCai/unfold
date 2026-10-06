"""Shared fixtures for testing the Claude Code hooks in .claude/hooks."""

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parents[2] / ".claude" / "hooks"

RunHook = Callable[[str, dict[str, object], Path], subprocess.CompletedProcess[str]]


def _run_hook(
    name: str, event: dict[str, object], project: Path
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOKS / f"{name}.py")],
        input=json.dumps(event),
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def run_hook() -> RunHook:
    """Run a hook script as Claude Code does: JSON in, exit code and output out."""
    return _run_hook

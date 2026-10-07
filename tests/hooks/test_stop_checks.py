"""The Stop hook blocks while checks fail, but at most three times in a row.

It also runs only tools that read code, so it never runs code Claude wrote.
"""

import json
import os
import subprocess
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

FAILURE = [("ruff lint", "F401 `os` imported but unused")]
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


def test_runs_only_tools_that_read_code(stop_checks: ModuleType) -> None:
    """Decision record 0005: a hook must never run tests or other project code."""
    tools = {command[0] for _, command in stop_checks.CHECKS}
    assert tools <= {"ruff", "pyright"}


def test_allows_the_stop_when_checks_pass(stop_checks: ModuleType) -> None:
    assert stop_checks.decide([], stop_hook_active=True, attempts=2) == (None, 0)


def test_blocks_the_first_failed_stop(stop_checks: ModuleType) -> None:
    reply, attempts = stop_checks.decide(FAILURE, stop_hook_active=False, attempts=0)

    assert reply["decision"] == "block"
    assert "ruff lint" in reply["reason"]
    assert "F401" in reply["reason"]
    assert attempts == 1


def test_counts_blocks_in_a_row(stop_checks: ModuleType) -> None:
    reply, attempts = stop_checks.decide(FAILURE, stop_hook_active=True, attempts=1)

    assert reply["decision"] == "block"
    assert attempts == 2


def test_gives_up_and_warns_after_three_blocks(stop_checks: ModuleType) -> None:
    reply, attempts = stop_checks.decide(FAILURE, stop_hook_active=True, attempts=3)

    assert "decision" not in reply
    assert "ruff lint" in reply["systemMessage"]
    assert attempts == 0


def test_a_new_turn_restarts_the_count(stop_checks: ModuleType) -> None:
    _, attempts = stop_checks.decide(FAILURE, stop_hook_active=False, attempts=3)

    assert attempts == 1


def git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], env=GIT_ENV, check=True)


def make_repo(path: Path) -> None:
    git(path, "init", "-q")
    (path / "ok.py").write_text("x = 1\n")
    git(path, "add", ".")
    git(path, "commit", "-qm", "init")


def test_skips_the_checks_when_nothing_changed(run_hook: Any, tmp_path: Path) -> None:
    make_repo(tmp_path)

    result = run_hook(
        "stop_checks", {"session_id": "s1", "stop_hook_active": False}, tmp_path
    )

    assert result.returncode == 0
    assert result.stdout == ""


@pytest.mark.slow
def test_blocks_a_real_lint_failure(run_hook: Any, tmp_path: Path) -> None:
    make_repo(tmp_path)
    (tmp_path / "bad.py").write_text("import os\n")

    result = run_hook(
        "stop_checks", {"session_id": "s2", "stop_hook_active": False}, tmp_path
    )

    reply = json.loads(result.stdout)
    assert reply["decision"] == "block"
    assert "ruff lint" in reply["reason"]
    assert (tmp_path / ".claude" / "state" / "stop-attempts-s2").read_text() == "1"

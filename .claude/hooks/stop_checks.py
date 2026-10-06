"""Stop hook: Claude cannot end its turn while ruff or pyright fails.

Claude Code runs this script whenever Claude tries to stop. If files changed
since the last commit, the script runs ruff and pyright. Both read code without
running it. Hooks run with your full access, outside the sandbox and without
classifier review, so this hook never runs tests or other code that Claude
wrote. Decision record 0005 explains why.

When a check fails, the script blocks the stop and tells Claude what failed.
After three blocked stops in a row, it lets Claude stop and warns you instead.
That way, a problem that Claude cannot fix does not trap it in a loop.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

MAX_ATTEMPTS = 3
OUTPUT_LIMIT = 2000
CHECKS = (
    ("ruff lint", ["ruff", "check", "."]),
    ("ruff format", ["ruff", "format", "--check", "."]),
    ("pyright", ["pyright"]),
)

Failure = tuple[str, str]


def has_changes(project: Path) -> bool:
    """Report whether the working tree differs from the last commit."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode != 0 or bool(result.stdout.strip())


def run_checks(project: Path) -> list[Failure]:
    """Run every check, and return the name and output of each one that fails."""
    failures: list[Failure] = []
    for name, command in CHECKS:
        result = subprocess.run(
            [sys.executable, "-m", *command],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            failures.append((name, output[-OUTPUT_LIMIT:]))
    return failures


def decide(
    failures: list[Failure], stop_hook_active: bool, attempts: int
) -> tuple[dict[str, str] | None, int]:
    """Choose the reply to Claude Code and the new count of blocked stops.

    A reply of None lets Claude stop without a message. Claude Code sets
    stop_hook_active when Claude is still working because of an earlier block.
    """
    if not failures:
        return None, 0
    attempts = attempts + 1 if stop_hook_active else 1
    names = ", ".join(name for name, _ in failures)
    if attempts > MAX_ATTEMPTS:
        message = (
            f"Checks still fail after {MAX_ATTEMPTS} attempts: {names}. "
            "Claude stopped anyway, so please run the checks yourself."
        )
        return {"systemMessage": message}, 0
    details = "\n\n".join(f"## {name}\n{output}" for name, output in failures)
    reason = (
        f"These checks fail: {names}. Fix them before you stop. "
        f"This is attempt {attempts} of {MAX_ATTEMPTS}.\n\n{details}"
    )
    return {"decision": "block", "reason": reason}, attempts


def main() -> int:
    event = json.load(sys.stdin)
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    session = re.sub(r"[^A-Za-z0-9-]", "", str(event.get("session_id", "unknown")))
    state = project / ".claude" / "state" / f"stop-attempts-{session}"

    attempts = int(state.read_text()) if state.is_file() else 0
    failures = run_checks(project) if has_changes(project) else []
    reply, attempts = decide(failures, bool(event.get("stop_hook_active")), attempts)

    if attempts:
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(str(attempts))
    else:
        state.unlink(missing_ok=True)
    if reply:
        print(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(main())

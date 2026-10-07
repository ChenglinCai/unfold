"""PostToolUse hook: format a Python file right after Claude edits it.

Claude Code sends each edit as JSON on standard input. When the edited file is
a Python file inside the project, this script sorts its imports and formats it
with ruff. When ruff cannot parse the file, the script exits with code 2, so
Claude sees the error and can fix it.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SHOW_ERROR_TO_CLAUDE = 2
RUFF_STEPS = (["check", "--select", "I", "--fix"], ["format"])


def main() -> int:
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path")
    if not file_path:
        return 0

    project = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    path = Path(file_path).resolve()
    if path.suffix not in {".py", ".pyi"} or not path.is_file():
        return 0
    if not path.is_relative_to(project):
        return 0

    for step in RUFF_STEPS:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", *step, "--quiet", str(path)],
            cwd=project,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            return SHOW_ERROR_TO_CLAUDE
    return 0


if __name__ == "__main__":
    sys.exit(main())

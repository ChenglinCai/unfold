# Journal

One line for each finished task, newest first.

## 2026-10-06

- Added CLAUDE.md and a hook that formats each Python file that Claude edits. Four tests cover the hook.
- Created the Python project with uv, Python 3.12, and manim 0.21. The hello scene renders, and its test passes locally.
- Started M0 with a pre-mortem, which named five risks. The render setup could break, or private files could reach the public repo. A Stop hook could loop, memory notes could be lost, and a pull request could be too big to review. Each risk has a guard in the M0 pull requests.

# Journal

One line for each finished task, newest first.

## 2026-10-06

- Wrote the economics example by hand: a source manifest, a knowledge map with 13 concepts, an outline, and one segment's script and storyboard. Added an anchor checker, and tests that every example anchor resolves.
- Rendered the first episode: two segments on k-NN, 102 seconds, in the private content repo. Contact sheets found four problems, and each one is fixed. The voice now takes a speaking rate and a pause after each beat.
- Added a stand-in voice that uses the macOS `say` command, and a parser for the script format. Nine tests cover them. Found that macOS hid the `.pth` file that makes the package importable, and guarded the tests against it.
- Set up the overnight harness: the `dev` branch, `docs/progress.md`, `docs/milestones.json` with a test, `docs/dependencies.md`, and decision record 0006.
- Wrote the first five decision records and started the mistake log with thirteen entries.
- Installed Spec Kit 1.1.0 with its bug and idea-assessment extensions. Wrote constitution 1.0.0 from the plan, with a ninth principle on safety, and moved the glossary into `docs/glossary.md`.
- Added a Stop hook that runs ruff and pyright before Claude ends a turn. It never runs tests, so no hook runs code that Claude wrote. It blocks at most three times in a row, and eight tests cover it.
- Added CLAUDE.md and a hook that formats each Python file that Claude edits. Four tests cover the hook.
- Created the Python project with uv, Python 3.12, and manim 0.21. The hello scene renders, and its test passes locally.
- Started M0 with a pre-mortem, which named five risks. The render setup could break, or private files could reach the public repo. A Stop hook could loop, memory notes could be lost, and a pull request could be too big to review. Each risk has a guard in the M0 pull requests.

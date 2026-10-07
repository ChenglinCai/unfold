# Journal

One line for each finished task, newest first.

## 2026-10-07

- Finished M5: a theme, a layout grid and check, five components, a scene step, and `unfold render` with contact sheets. All 12 golden segments render with no layout failures. Tagged `m5-done`.
- Finished M4: schemas for every format, `unfold check`, and a build graph with saved results. It adds four generation steps, a canary, a call log, and the first eval report. Six golden series built with 42 calls, and a second build made none. Tagged `m4-done`.
- Finished M2: readers for every family, `unfold ingest`, a job runner with no tools, output checks, and `unfold understand`. Six golden sources passed with 8 model calls, and every anchor resolves. Tagged `m2-done`.
- Finished M3: `unfold lint` with three profiles and 16 rules, a fixer, and a breath-group study on 144 transcripts. The hypothesis holds, and CI now lints the docs. Tagged `m3-done`.
- Finished M1: wrote `docs/formats.md` and the retro, recorded every gate's evidence, and tagged `m1-done`.

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

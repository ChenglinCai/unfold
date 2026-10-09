# Journal

One line for each finished task, newest first.

## 2026-10-08

- Made the web and EPUB readers turn MathML into TeX, so OpenStax pages keep their formulas. One page went from 0 of 7 formulas to 7 of 7.
- Made the LaTeX reader read whole books. It follows includes that a macro hides, keeps restyled structural commands, and no longer takes `\\[2mm]` for math.
- Made render and the eval counts follow each episode's outline, so a segment that a rebuilt outline dropped is neither rendered nor counted.
- Made the outline step retry when a segment teaches a concept that the plan saves for a later episode. The same rule was only an eval before.
- Made job records and call logs keep each call's model turns, and corrected the stated reason for understand's word limit.
- Added `unfold ingest --part FIRST..LAST`, which keeps one span of anchors, such as a chapter, so a long book can feed one series.
- Made `unfold understand` stop before any call when a source holds over 60,000 words, with a message that asks for one chapter instead.
- Capped anchor ids from headings at 60 characters, cut between words, so citations of long book headings stay short.
- Added an EPUB reader to `unfold ingest`. It reads chapters in reading order from the zip, with an XML parser that resolves no entities and a 200 MB cap.
- Made `unfold ingest` name each LaTeX include that it could not find, in the source profile and in a warning.
- Made the LaTeX reader turn theorems, lists, tables, figures, and Beamer frames into Markdown. A Beamer deck now gets the slides family.
- Made the LaTeX reader expand each document's own macros, such as `\newcommand` and `\DeclareMathOperator`, so each formula stands alone.
- Added a LaTeX reader to `unfold ingest`. It follows includes only inside the main file's folder, keeps formulas as TeX, and turns sections into anchors.
- Added a scene check that compares a histogram's stated mean and spread with its bins, and regenerated the one golden scene that failed it.
- Changed the storyboard prompt to name only real components and prefer their still pictures. Custom beats fell from 13 to 7 of 96, and grounded chart numbers rose from 7 to 10 of 14, so the change stays.
- Added an episode contact sheet, with one frame per beat, to each stitched episode and to the review page. The review page also shows the custom share.
- Added a Jupyter notebook reader to `unfold ingest`, and made the Markdown section parser skip code fences.
- Added English and Chinese subtitle tracks to the gallery and review players, and fixed a gallery link that PR 11 broke.
- Added Chinese subtitles: `unfold translate SERIES --to zh` writes `episode.zh.srt` for each rendered episode, checked against Netflix's style guide. All seven golden episodes passed, with 242 cues.
- Changed the translation prompt and checks once, after reading the golden output. A space at least every 16 characters keeps words whole across lines. Every check still passed, so the change stays.
- Added four domain-pack components with schema, drawing, layout, property, and render tests. The golden custom share fell from 28 to 13.5 percent, short of the 10 percent goal. `docs/evals/M8-packs-report.md` gives the numbers.
- Changed the scene prompt twice to improve the evals, as principle IV allows. A motion rule cut custom beats from 18 to 12, and a plain-label rule fixed TeX in labels. No scene check fell below its starting point, so both stay.
- Finished M7: `unfold doctor`, the review page, the gallery, an MCP server with seven tools, a Claude Code plugin, and a quickstart. A CI job renders the quickstart on a clean Mac, and a security review fixed two gaps. Tagged `m7-done`.

## 2026-10-07

- Finished M6: voiced segments, a Whisper audio check, subtitles, stitched episodes, a ledger, and the idea-link check. Three episodes play, and every segment passes the audio check. Tagged `m6-done`.
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

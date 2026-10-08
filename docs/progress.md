# Progress

This file holds the current state of the work, so that a new session can resume from it. The gates live in `docs/milestones.json`, and finished tasks live in `docs/journal.md`.

## Current state

- Mode: the overnight run began on 2026-10-06 and ended at 09:30 on 2026-10-07. Decision record 0006 set its rules.
- Branch: one branch per milestone, such as `m5`. The maintainer asked on 2026-10-07 to merge each finished milestone after CI passes.
- Done: M1 through M7, each tagged, such as `m7-done`. M0 lacks only the settings file that the maintainer writes.
- Next: your review of M7 and of items 19 to 22. Then M8, growth: more domain packs, Chinese subtitles, more source formats, and outside contributors.
- Backup job: a session-only job checked in every hour, and resumed the run after two usage limits. The run deleted it when the run ended.

## Check-ins

### M1, the walking skeleton

- What to watch: run `content/cis5200/episodes/E01-knn/render.sh`, then play `episode.mp4`. It lasts 102 seconds.
- What to read: `docs/formats.md`, `examples/econ-supply-demand/`, and `docs/retros/M1.md`.
- Evidence: every M1 gate in `docs/milestones.json`. The beat timing holds by construction, because each beat's audio starts at the same scene time as its first animation. No test measures it yet.
- Walkthrough to ask for: `src/unfold/voice.py`, which shows how a scene waits for its narration.

### M3, the Narration Standard linter

- What to try: `uv run unfold lint docs`, then `uv run unfold lint --profile spoken examples/econ-supply-demand/s3-equilibrium/script.md`.
- What to read: `docs/studies/breath-groups.md`, and `specs/002-language/`, which Spec Kit's own skills produced this time.
- Evidence: every M3 gate in `docs/milestones.json`. CI now runs the linter on every pull request.
- Walkthrough to ask for: `src/unfold/lint/prose.py`, which shows how text becomes sentences and breath groups.
- Not done, by design: labeling teaching moves with models, and the narration and visual style guides. They wait for the M4 job runner and M5. Khan Academy transcripts were not downloaded, because their policy forbids commercial use.

### M2, source understanding

- What to try: `uv run unfold ingest <file or URL> --out ../content/sources --id <id>`, then `uv run unfold understand ../content/sources/<id>`.
- What to read: the six outputs in `content/sources/*/understand/`, then `docs/retros/M2.md` and `docs/studies/study-notes-lint.md`.
- Evidence: every M2 gate in `docs/milestones.json`, and `specs/003-source-understanding/tasks.md` with its convergence phase.
- Walkthrough to ask for: `src/unfold/understand/__init__.py`, which shows one job's loop: prompt, check, retry, and save.
- Not done, by design: the CUNY deck, which needs a browser download, and your handwritten page. Items 13 and 14 below wait for you.

### M4, text generation

- What to try: `uv run unfold build ../content/series/velocity-of-money`, which reuses every result. Then try `uv run unfold eval ../content/series/*/ --failures`.
- What to read: `docs/evals/M4-report.md`, then the open notes in `content/series/notes.md`, then `docs/retros/M4.md`.
- Evidence: every M4 gate in `docs/milestones.json`.
- Walkthrough to ask for: `src/unfold/build/__init__.py`, which shows the job loop that every step shares.
- Not done, by design: model checks for paraphrase drift, and the fixes that the report proposes. They wait for your review.

### M5, visuals

- What to try: `uv run unfold render ../content/series/net-present-value`, which reuses its videos. Then open a `contact-sheet.png`.
- What to read: `docs/evals/M5-report.md`, then `docs/retros/M5.md`.
- Evidence: every M5 gate in `docs/milestones.json`.
- Walkthrough to ask for: `src/unfold/visuals/components.py`, which shows how a component fits its region.
- Not done, by design: model-written manim code for custom visuals, and its sandbox. Custom entries render as cards to review.

### M6, episodes

- What to watch: `content/series/net-present-value/E01-time-value-of-money/episode.mp4`, then its episode 2, then `content/series/velocity-of-money/E01-equation-of-exchange/episode.mp4`.
- What to read: `docs/retros/M6.md`, and the `ledger.yaml` of net-present-value.
- Evidence: every M6 gate in `docs/milestones.json`.
- Walkthrough to ask for: `src/unfold/episodes/stitch.py`, which shows how cards, segments, and subtitles line up.
- Not done, by design: Kokoro, which waits for item 18. The voice is macOS `say`.

### M7, product and release

- What to try: follow `docs/quickstart.md` on your Mac. Then run `uv run unfold review ../content/series/net-present-value`, and open its `review.html`.
- What to read: `docs/retros/M7.md`, then `plugin/README.md`, which says what the plugin installs and runs.
- Evidence: every M7 gate in `docs/milestones.json`, and the macOS quickstart job on each pull request.
- Walkthrough to ask for: `src/unfold/mcp_server.py`, which shows how each tool runs one unfold command.
- Not done, by design: Cowork support, a release tag, and a package on PyPI. Items 19 and 22 wait for you.

## Decisions for the maintainer to confirm

1. Claude wrote the M1 scenes, which the plan reserved for the maintainer.
2. The economics source is OpenStax Principles of Economics 2e, which is CC BY 4.0. The 3rd edition is CC BY-NC-SA, which forbids commercial use.
3. The stand-in voice is the macOS `say` command at rate 140, which is about 165 words per minute. M6 replaces it with Kokoro.
4. New dependency: PyYAML, under the MIT license.
5. iCloud syncs your Desktop, so it hid `.venv` and broke imports. The environment now lives in `.venv.nosync`, with a `.venv` link. Moving the project out of iCloud would be cleaner.
6. The spoken breath-group limit is 31 words, from the study. The strict profile keeps 20.
7. The linter treats every numbered list item as a procedure step, which allows 20 words. Bullet lists allow 25.
8. Every commit now runs the linter through pre-commit. It only reads files, like the pyright hook.
9. PyAV comes with manim, and the recording reader uses it too. Its wheels bundle FFmpeg with the x264 and x265 encoders, which use the GPL. Users install these wheels from PyPI, so unfold does not redistribute them. A packaged app would need a license review first.
10. A bare topic's outputs may be public, because no source text reaches them. Every claim still starts flagged for a fact check.
11. The CUNY statistics deck sits behind Cloudflare's bot wall, which refuses any download outside a browser. MIT 18.05's Class 10 slides take its place, under CC BY-NC-SA 4.0. To add the CUNY deck, save the PDF from a browser and run `unfold ingest` on the file.
12. The web reader now keeps each formula's TeX from the page's MathML. Without it, the Euler's identity article lost every equation.
13. Principle II says a job writes one output file. The understand job writes two: the knowledge map and the study notes. The spec asked for one job. I recommend a map job and a notes job in M4, when the build graph arrives. The other choice is a wording patch to principle II.
14. Principle II says every key covers the manim and component-library versions. The understand outputs use neither, so the key leaves them out, and a manim upgrade costs no model calls. Proposed patch: "A key MUST cover everything its output depends on: the inputs, the prompt version, and the model. Scene jobs add the component-library and manim versions."
15. Claude did the M4 error analysis, a step that principle IV prefers a domain expert for. Please read the open notes, and correct any failure type.
16. New dependencies overnight: PyAV, NumPy, lxml, and pydantic. Each uses a permissive license, and `docs/dependencies.md` logs each one.
17. Five golden charts show numbers that the narration never states. Some are correct computations, and one is an invented poll. Please review them, and decide whether charts may show computed numbers.
18. M6 needs a voice. Kokoro, the plan's default, depends on espeak-ng and phonemizer for some words, and both use the GPL. Until you decide, M6 keeps the macOS voice behind an interface that Kokoro can fill later.
19. The plugin says version 0.1.0, but it installs unfold from the main branch. A release would tag `v0.1.0`, and the plugin would pin that tag. Decision record 0004 also asks for a package name first, because another project already holds `unfold` on PyPI.
20. `unfold doctor` now treats LaTeX as optional, because only equations need it. The quickstart and its CI job install no LaTeX.
21. The plugin installs the audio extra, so a user's first audio check downloads a Whisper model from Hugging Face. `plugin/README.md` says so.
22. The plan's M7 gate names Cowork as well as Claude Code. The spec moved Cowork to a later release, so that half of the gate is still open.

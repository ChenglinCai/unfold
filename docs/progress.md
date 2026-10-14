# Progress

This file holds the current state of the work, so that a new session can resume from it. The gates live in `docs/milestones.json`, and finished tasks live in `docs/journal.md`.

## Current state

- Mode: the overnight run began on 2026-10-06 and ended at 09:30 on 2026-10-07. Decision record 0006 set its rules.
- Branch: one branch per milestone, such as `m5`. The maintainer asked on 2026-10-07 to merge each finished milestone after CI passes.
- Done: M1 through M7, each tagged, such as `m7-done`. M0 lacks only the settings file that the maintainer writes.
- Next: the steps under "Waiting on the maintainer's Mac". M8, growth, now has the domain packs, Chinese subtitles, subtitle tracks in the players, and episode contact sheets. It also reads notebooks, LaTeX, EPUB books, and Word files, and ingests one part of a long source. On 2026-10-14, a cloud session added the neighborhood circle, the first part of the machine-learning pack.
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

### M8, the domain packs

- What to try: `uv run unfold eval ../content/series/*/`, which ends with the custom share. Then open the contact sheet of `content/series/eulers-identity/E01-five-constants/s2-numbers-that-spin`.
- What to read: `docs/evals/M8-packs-report.md`, then `specs/008-domain-packs/research.md`.
- Evidence: the report's tables, and `tests/visuals/test_pack_props.py`, which draws 25 random cases of each new component.
- Walkthrough to ask for: `src/unfold/visuals/finance.py` and `_present_value`, which show how code, not the model, computes each number.
- Not done, by design: motion inside components, and the machine-learning pack.

### M8, more source formats

- What to try: `uv run unfold ingest notes.tex --out ../content/sources`, with a LaTeX file of your own. A Beamer deck gets the slides family, and an EPUB book works the same way. Then open `content/series/division-of-labour/review.html`, a series from three chapters of *The Wealth of Nations*.
- What to read: `docs/evals/M8-sources-report.md`, then the docstrings of `src/unfold/sources/latex.py` and `src/unfold/sources/epub.py`.
- Evidence: `tests/sources/test_latex.py`, including the tests that keep includes inside the folder.
- Walkthrough to ask for: `gather` and `_target`, which decide which files the reader may open.
- Not done, by design: includes that a macro hides, such as `\includechapter`. Item 30 waits for you.

### M8, the neighborhood circle

- What to try: render a scatter plot with `query` and `k`, such as the example in `specs/010-neighborhood-circle/data-model.md`.
- What to read: `specs/010-neighborhood-circle/research.md`, which lists each design call.
- Evidence: `tests/visuals/test_neighbors.py`, and a property test that draws 50 random neighborhoods.
- Walkthrough to ask for: `_neighborhood` and `_same_scale`, which show how the circle stays true to the data.
- Not done, by design: the golden rebuild, which needs the content folder and model calls. The component version rose to 5, so the next build remakes every scene. Item 34 waits for you.

## Decisions for the maintainer to confirm

1. Claude wrote the M1 scenes, which the plan reserved for the maintainer.
2. The economics source is OpenStax Principles of Economics 2e, which is CC BY 4.0. The 3rd edition is CC BY-NC-SA, which forbids commercial use.
3. The stand-in voice is the macOS `say` command at rate 140, which is about 165 words per minute. M6 replaces it with Kokoro.
4. New dependency: PyYAML, under the MIT license.
5. iCloud syncs your Desktop, so it hid `.venv` and broke imports. The environment now lives in `.venv.nosync`, with a `.venv` link. Moving the project out of iCloud would be cleaner. On 2026-10-08, iCloud also made 90 conflict copies after a pull. A pre-commit hook now rejects them, but moving the project would end the problem.
6. The spoken breath-group limit is 31 words, from the study. The strict profile keeps 20.
7. The linter treats every numbered list item as a procedure step, which allows 20 words. Bullet lists allow 25.
8. Every commit now runs the linter through pre-commit. It only reads files, like the pyright hook.
9. PyAV comes with manim, and the recording reader uses it too. Its wheels bundle FFmpeg with the x264 and x265 encoders, which use the GPL. Users install these wheels from PyPI, so unfold does not redistribute them. A packaged app would need a license review first.
10. A bare topic's outputs may be public, because no source text reaches them. Every claim still starts flagged for a fact check.
11. The CUNY statistics deck sits behind Cloudflare's bot wall, which refuses any download outside a browser. MIT 18.05's Class 10 slides take its place, under CC BY-NC-SA 4.0. To add the CUNY deck, save the PDF from a browser and run `unfold ingest` on the file.
12. The web reader now keeps each formula's TeX from the page's MathML. Without it, the Euler's identity article lost every equation.

## Decided on 2026-10-14

The maintainer asked Claude to settle items 13 to 33. The maintainer chose items 13, 14, 18, 19, and 28 from options. Claude reviewed the rest, and the maintainer accepted each recommendation.

13. Principle II now says a job writes the files that its one reply holds. Constitution 1.1.0 records the patch, so the understand job stays one job.
14. Principle II now says a key covers everything its output depends on. Scene jobs add the component-library and manim versions.
15. Moved to the next list, because the open notes live in the content folder.
16. Confirmed. PyAV, NumPy, lxml, and pydantic each use a permissive license.
17. Charts may show numbers that code or the model computes from the narration's numbers. Made-up data needs "Example" in its title, as the scene prompt says. The five charts still need a reading, in the next list.
18. Kokoro is now the voice, through the `voice` extra. Decision record 0007 and `specs/011-natural-voice/` explain. The default is `af_heart` until the maintainer picks a voice by ear.
19. The package is now `unfold-video`, and the command stays `unfold`. Tagging `v0.1.0` waits for a release.
20. Confirmed. LaTeX stays optional.
21. Confirmed. The plugin's first audio check downloads a Whisper model.
22. Confirmed. Cowork waits for a later release.
23. Confirmed. The design calls in `specs/008-domain-packs/research.md` stay.
24. Confirmed. Hypothesis stays a dev dependency.
25. Done, and kept as a record.
26. Done, and kept as a record.
27. Done. The neighborhood circle has since shipped.
28. `SECURITY.md` points to GitHub's private vulnerability reporting. The maintainer switches it on in the repository settings. The code of conduct waits for a contact.
29. Moved to the next list, because the subtitles live in the content folder.
30. Confirmed. Includes stay inside the main file's folder.
31. Confirmed. The limit stays at 60,000 words.
32. Confirmed. The option stays `--part FIRST..LAST`.
33. Ingest both sources again with the next golden rebuild, so the two series rebuild only once.

## Waiting on the maintainer's Mac

Each of these needs the private content folder, so a cloud session cannot do them.

1. Ingest net present value and Euler's identity again, then rebuild the golden set. This covers items 33 and 34.
2. Compare `unfold eval` with `docs/evals/M8-packs-report.md`. Keep the neighborhood circle only if the custom share and the scene checks hold or improve.
3. Read the M4 open notes, and correct any failure type. This is item 15.
4. Read the five charts that fail `chart-numbers-grounded`, and fix any invented number. This is item 17.
5. Read `episode.zh.srt` of velocity-of-money beside its video. This is item 29.
6. Write `.claude/settings.json`, which closes the M0 gate.
7. Switch on private vulnerability reporting in the repository's security settings.
8. Run `uv sync --extra voice`, then listen to a rendered episode. Pick the default voice, and check that Whisper hears each segment with under 5 percent word errors.

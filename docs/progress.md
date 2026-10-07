# Progress

This file holds the current state of the work, so that a new session can resume from it. The gates live in `docs/milestones.json`, and finished tasks live in `docs/journal.md`.

## Current state

- Mode: overnight autonomous run, which began on 2026-10-06. Decision record 0006 sets its rules.
- Branch: `dev`. Nothing merges into `main` without the maintainer.
- Done: M1, tagged `m1-done`, and M3, tagged `m3-done`. M0 lacks only the settings file that the maintainer writes.
- Now: M2, source understanding. Every family has its reader. Next come `unfold ingest` and the understand step.
- Backup job: a session-only job checks in every hour at minute 17. It resumes the run after a usage limit, and it ends when this session closes. The run deletes it when the run finishes.

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

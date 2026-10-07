# Progress

This file holds the current state of the work, so that a new session can resume from it. The gates live in `docs/milestones.json`, and finished tasks live in `docs/journal.md`.

## Current state

- Mode: overnight autonomous run, which began on 2026-10-06. Decision record 0006 sets its rules.
- Branch: `dev`. Nothing merges into `main` without the maintainer.
- Done: M1, tagged `m1-done`. M0 is done except the settings file that the maintainer writes.
- Next: M2 and M3.

## Check-ins

### M1, the walking skeleton

- What to watch: run `content/cis5200/episodes/E01-knn/render.sh`, then play `episode.mp4`. It lasts 102 seconds.
- What to read: `docs/formats.md`, `examples/econ-supply-demand/`, and `docs/retros/M1.md`.
- Evidence: every M1 gate in `docs/milestones.json`. The beat timing holds by construction, because each beat's audio starts at the same scene time as its first animation. No test measures it yet.
- Walkthrough to ask for: `src/unfold/voice.py`, which shows how a scene waits for its narration.

## Decisions for the maintainer to confirm

1. Claude wrote the M1 scenes, which the plan reserved for the maintainer.
2. The economics source is OpenStax Principles of Economics 2e, which is CC BY 4.0. The 3rd edition is CC BY-NC-SA, which forbids commercial use.
3. The stand-in voice is the macOS `say` command at rate 140, which is about 165 words per minute. M6 replaces it with Kokoro.
4. New dependency: PyYAML, under the MIT license.
5. macOS hides the `.pth` file in `.venv`. If imports fail, run `chflags -R nohidden .venv`. The tests no longer depend on that file.

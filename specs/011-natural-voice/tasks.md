# Tasks: Natural voice

**Input**: Design documents from `specs/011-natural-voice/`

**Tests**: requested. Each test runs and fails before its code exists. Each task names its check.

## Phase 1: Foundational

- [X] T001 Write tests for `trim` and `level` in `tests/test_kokoro.py`, then implement them in `src/unfold/kokoro.py`. Check: edges keep 50 milliseconds, every clip lands within 1 dB of the target, and no peak passes minus 1 dBFS.
- [X] T002 Write tests for `fetch`, with a fake download, then implement it. Check: a good file stays, and a file with the wrong hash is deleted with an error.

## Phase 2: User Stories 1 and 4, hear a natural voice from a trusted model (Priority: P1)

- [X] T003 [US1] Write tests for `KokoroVoice.speak` with a fake engine and fake G2P. Check: the clip is a 24 kHz WAV, its length matches, the same text is spoken once, and British voices use British G2P.

## Phase 3: User Stories 2 and 3, voice on Linux and a choice of voice (Priority: P1 and P2)

- [X] T004 [US3] Write tests for `UNFOLD_VOICE` and `default_voice()`, then implement them in `src/unfold/voice.py`. Check: each form parses, an unknown voice lists the voices, and Kokoro comes before `say`.
- [X] T005 [US2] Add the `voice` extra and the doctor finding, with a test for the finding. Check: `uv sync --extra voice` installs no PyTorch, and the doctor tests pass.

## Phase 4: Polish

- [X] T006 Add the extra to the plugin, and update `docs/dependencies.md`, `docs/quickstart.md`, and decision record 0007. Check: the plugin and lint tests pass.
- [X] T007 Render the bundled example with Kokoro on Linux, and send the maintainer the video. Check: the video has narration, and each clip meets SC-002.
- [X] T008 Run every check and the whole suite, then update `docs/progress.md` and `docs/journal.md`. Check: `uv run pre-commit run --all-files` and `uv run pytest` pass.

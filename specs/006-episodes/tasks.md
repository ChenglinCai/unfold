# Tasks: Episodes

**Input**: Design documents from `specs/006-episodes/`

**Tests**: requested. Each test runs and fails before its code exists.

## Phase 1: User Story 1, voiced segments (Priority: P1)

- [X] T001 [US1] Write tests for clip timing in `tests/visuals/test_render.py`, with a slow test that renders a voiced segment. Check: the tests fail.
- [X] T002 [US1] Add the Voice interface to `src/unfold/voice.py`, time each beat by its clip in `src/unfold/visuals/scene.py`, and voice renders in `src/unfold/visuals/render.py`. Check: the tests pass.
- [X] T003 [US1] Write `tests/episodes/test_audio.py` for the word error rate, then implement `src/unfold/episodes/audio.py`. Check: the tests pass.

## Phase 2: User Story 2, episodes with subtitles (Priority: P1)

- [X] T004 [US2] Write `tests/episodes/test_subtitles.py`, then implement `src/unfold/episodes/subtitles.py`. Check: the tests pass.
- [X] T005 [US2] Write `tests/episodes/test_stitch.py`, then implement `src/unfold/episodes/stitch.py`, and stitch episodes in `unfold render`. Check: the tests pass.

## Phase 3: User Story 3, linked ideas (Priority: P1)

- [X] T006 [US3] Write tests for ledger/v0 and the idea-link check. Then implement `src/unfold/episodes/ledger.py` and `src/unfold/episodes/links.py`, and add `knows` to series/v0. Check: the tests pass.
- [X] T007 [US3] Write the ledger after each episode, show it to the outline step, and let callbacks name an earlier episode. Check: tests in `tests/build/test_graph.py` pass.
- [X] T008 [US3] Add the `ideas-link` check to `unfold eval`. Check: a test passes.

## Phase 4: The gate

- [ ] T009 Build episode 2 of net-present-value, then render it, its episode 1, and velocity-of-money's episode 1. Check: three episodes play, every segment passes the audio check, and every outline links.
- [ ] T010 Converge, record the M6 gates, write `docs/retros/M6.md`, tag `m6-done`, and merge. Check: every M6 gate has evidence.

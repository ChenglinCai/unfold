# Tasks: Visuals

**Input**: Design documents from `specs/005-visuals/`

**Tests**: requested. Each test runs and fails before its code exists.

## Phase 1: User Story 1, a checked grid (Priority: P1)

- [X] T001 [US1] Write `tests/visuals/test_layout.py` for the regions and the layout check. Check: the tests fail.
- [X] T002 [US1] Implement `src/unfold/visuals/theme.py` and `src/unfold/visuals/layout.py`. Check: `tests/visuals/test_layout.py` passes.
- [X] T003 [US1] Write `tests/visuals/test_components.py`, which builds every component in every region and checks the fit. Check: the tests fail.
- [X] T004 [US1] Implement the five components in `src/unfold/visuals/components.py`. Check: `tests/visuals/test_components.py` passes.

## Phase 2: User Story 2, scenes from storyboards (Priority: P1)

- [X] T005 [US2] Write `tests/visuals/test_scene.py` for the scene/v0 format, beat timing, and the layout check of a whole scene. Check: the tests fail.
- [X] T006 [US2] Implement `src/unfold/visuals/scene.py`, and add scene/v0 to `unfold.formats`. Check: the tests pass, and `schemas/` holds the new file.
- [X] T007 [US2] Write tests for the scene step in `tests/build/test_graph.py`, with a fake runner. Check: the tests fail.
- [X] T008 [US2] Add the scene step to the build graph, with `src/unfold/prompts/scene.md`. Check: the tests pass.

## Phase 3: User Story 3, renders and contact sheets (Priority: P1)

- [X] T009 [US3] Write `tests/visuals/test_render.py`, with a slow test that renders a small scene. Check: the tests fail.
- [X] T010 [US3] Implement `src/unfold/visuals/render.py` and `unfold render`. Check: the tests pass.
- [ ] T011 [US3] Build the scenes of the six golden series, then render all 12 segments. Check: no layout failures, and 12 contact sheets.

## Phase 4: Polish

- [ ] T012 Describe scene/v0 in `docs/formats.md`, then converge, record the M5 gates, write `docs/retros/M5.md`, and tag `m5-done`. Check: every M5 gate has evidence.

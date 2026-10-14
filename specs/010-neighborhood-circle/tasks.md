# Tasks: Neighborhood circle

**Input**: Design documents from `specs/010-neighborhood-circle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, and quickstart.md

**Tests**: requested. Each test runs and fails before its code exists. Each task names its check.

**Organization**: the pure functions come first, because the checks and the drawing need them. Then one phase per user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel, because it touches other files and waits on no open task.
- **[Story]**: the user story from spec.md, such as US1.

## Phase 1: Foundational

The feature adds no dependency, so it needs no setup phase.

- [X] T001 Write tests in `tests/visuals/test_neighbors.py` for `nearest`, `tied`, and `vote`. Then implement them in `src/unfold/visuals/neighbors.py`, with no manim import. Check: the tests pass.

## Phase 2: User Story 3, reject a misleading circle (Priority: P1)

**Goal**: a scene with an impossible or tied neighborhood fails its check, with a message for the retry.

**Independent test**: parse scenes that break each rule in data-model.md.

- [X] T002 [US3] Write parameter tests for each rule in data-model.md, and one that a plot without a query still parses. Then add `query` and `k` to `ScatterPlot` in `src/unfold/visuals/params.py`, and raise VERSION to 5. Check: the tests pass.

## Phase 3: User Story 1, show the nearest neighbors (Priority: P1) 🎯 MVP

**Goal**: the plot draws the query point, a ring on each neighbor, and the boundary.

**Independent test**: draw a plot and read the positions of its parts.

- [X] T003 [US1] Write drawing tests: k rings sit on the k nearest dots, and the boundary passes through the k-th one. Add one that a distant query stays inside the region. Then draw them in `src/unfold/visuals/components.py`. Check: the tests pass.
- [X] T004 [US1] Add a property test to `tests/visuals/test_pack_props.py`. It draws 50 random plots with a query, and checks the rings, the boundary, and the layout. Check: the test passes.
- [X] T005 [US1] Add a query point and k to the scatter-plot sample that `tests/visuals/test_components.py` draws in each region. Check: the layout tests pass.

## Phase 4: User Story 2, show the vote (Priority: P2)

**Goal**: the query point takes the winning group's color.

**Independent test**: draw plots with a clear winner and with a tie.

- [X] T006 [US2] Write tests that the query point takes the winner's color, or the text color on a tie. Then color it in the drawing. Check: the tests pass.

## Phase 5: Polish

- [X] T007 [P] Describe `query` and `k` in `src/unfold/prompts/scene.md`, and regenerate `schemas/`. Check: `tests/formats` and `tests/build` pass.
- [X] T008 Render the data-model.md example as a still, and read the picture. Check: the picture matches quickstart.md step 3.
- [X] T009 Run every check and the whole suite. Then update `docs/progress.md` and `docs/journal.md`. Check: `uv run pre-commit run --all-files` and `uv run pytest` pass.

## Dependencies

- T001 comes first. T002 needs it, and T003 needs T002.
- T004, T005, and T006 need T003.
- T007 needs T002. T008 and T009 come last.

The golden rebuild in quickstart.md step 4 needs the content folder and model calls, so it waits for the maintainer.

# Tasks: Domain packs

**Input**: Design documents from `specs/008-domain-packs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, and quickstart.md

**Tests**: requested. Each test runs and fails before its code exists. Each task names its check.

**Organization**: one phase per user story, so each component ships and proves itself alone.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel, because it touches other files and waits on no open task.
- **[Story]**: the user story from spec.md, such as US1.

## Phase 1: Setup

- [X] T001 Add Hypothesis with `uv add --dev hypothesis`, put `.hypothesis/` in `.gitignore`, and add its row and safety note to `docs/dependencies.md`. Check: `uv run python -c "import hypothesis"` works, and `uv lock --check` passes.

## Phase 2: Foundational

- [X] T002 Write tests for the custom share in `tests/evals/test_eval_checks.py`. Then add `custom_share()` to `src/unfold/evals/__init__.py`, and print it from `src/unfold/evals/command.py` in text and JSON. Check: the tests pass.
- [X] T003 Record the numbers before the change: run `unfold eval` on the six golden series into `../content/series/before-packs.json`, and run `unfold render` on each. Check: the file shows 27 custom beats of 96, and each render reuses its videos with 0 layout failures.

## Phase 3: User Story 1, present value (Priority: P1) 🎯 MVP

**Goal**: a finance beat shows cash flows and what each is worth today, with numbers that code computes.

**Independent test**: draw yearly flows of 10,000 at 8 percent, and compare each label with the formula.

- [X] T004 [P] [US1] Write `tests/visuals/test_finance.py`, then implement `src/unfold/visuals/finance.py` with no manim import. A present value is "its amount divided by one plus the rate over 100, raised to the power of its time". Values of 1,000 or more show whole units with separators. Smaller values show at most two decimals, without trailing zeros. Check: the tests pass.
- [X] T005 [US1] Write tests for `present-value` in `tests/visuals/test_packs.py`, and add its sample to `tests/visuals/test_components.py`. Cover these rules: `rate` is "percent per period, from 0 to 100", and `flows` holds "1 to 24". Each flow's `at` runs "from 0 to 100" with a "nonzero `amount`", and `prefix` has "at most 3 characters". Every shown label must equal the formula's shown value, and twelve flows must show no overlapping labels. Add a slow test that renders the component. Check: the new tests fail.
- [X] T006 [US1] Add `PresentValue` to `src/unfold/visuals/params.py`, and `_present_value` to `src/unfold/visuals/components.py`, as research.md D4 describes. Raise `VERSION` to "4". Check: the T005 tests pass.

## Phase 4: User Story 2, complex plane (Priority: P1)

**Goal**: a math beat shows points on a complex plane, with a unit circle, guides, and a turn.

**Independent test**: draw points at known angles, and check where each lands.

- [X] T007 [US2] Write tests for `complex-plane` in `tests/visuals/test_packs.py`, with its sample in `tests/visuals/test_components.py`. Cover these rules: `points` holds "1 to 6", and each `radius` runs "from 0 to 100", with angles in degrees. Assert that a point at radius 1 and 60 degrees lands on the unit circle, and that radius 3 grows the plane. Assert that guides draw dashed lines with their labels, and that a turn past 360 degrees draws a loop. Add a slow render test. Check: the new tests fail.
- [X] T008 [US2] Add `ComplexPlane`, `PlanePoint`, and `Turn` to `src/unfold/visuals/params.py`, and `_complex_plane` to `src/unfold/visuals/components.py`, as research.md D2 describes. Check: the T007 tests pass.

## Phase 5: User Story 3, histogram (Priority: P1)

**Goal**: a statistics beat shows a distribution, with a mean line, a spread, and a bell curve.

**Independent test**: draw six dice bins with a mean of 3.5, and check the bars, the line, and the curve.

- [ ] T009 [US3] Write tests for `histogram` in `tests/visuals/test_packs.py`, with its sample in `tests/visuals/test_components.py`. Cover these rules: `edges` holds "2 to 41, each greater than the one before", and `counts` has "one fewer than the edges, none below zero". `labels` is "empty, or one per bin", `spread` is "above zero", and `curve` "needs both `mean` and `spread`". Assert that six dice bins with a mean of 3.5 put the mean line at 3.5. Add a slow render test. Check: the new tests fail.
- [ ] T010 [US3] Add `Histogram` to `src/unfold/visuals/params.py`, and `_histogram` to `src/unfold/visuals/components.py`, as research.md D5 describes. Check: the T009 tests pass.

## Phase 6: User Story 4, flow diagram (Priority: P2)

**Goal**: a beat shows a short process or cycle as boxes and arrows.

**Independent test**: draw a cycle of three boxes, and check that every arrow joins the right boxes.

- [ ] T011 [US4] Write tests for `flow-diagram` in `tests/visuals/test_packs.py`, with its sample in `tests/visuals/test_components.py`. Cover these rules: `boxes` holds "2 to 6, with unique ids", and `links` holds "0 to 10". A link's ends must name two different boxes, and `highlight` "must name a box". Assert that a link from the last box to the first curves past the middle, and that opposite links curve apart. Add a slow render test. Check: the new tests fail.
- [ ] T012 [US4] Add `FlowDiagram`, `Box`, and `Link` to `src/unfold/visuals/params.py`, and `_flow_diagram` to `src/unfold/visuals/components.py`, as research.md D6 describes. Check: the T011 tests pass.

## Phase 7: User Story 5, the golden rebuild (Priority: P1)

**Goal**: the scene step uses the four components, and the golden set shows the gain.

**Independent test**: rebuild and render the golden set, then compare the custom share, the layout failures, and the eval pass rates.

- [ ] T013 [P] [US5] Write `tests/visuals/test_pack_props.py`, with a Hypothesis strategy for each new component. Each random drawing must fit its region, and `crowded()` must find no overlapping labels. Use `deadline=None` and about 25 examples each. Check: the tests pass, and the suite grows by at most about 20 seconds.
- [ ] T014 [P] [US5] Write tests in `tests/evals/test_eval_checks.py`, then extend `chart-numbers-grounded` in `src/unfold/evals/__init__.py`, as research.md D7 describes. Check: the tests pass, and the golden before-numbers stay the same.
- [ ] T015 [US5] Describe the four components in `src/unfold/prompts/scene.md`, and when each beats a custom visual. List them in `docs/formats.md`, and regenerate `schemas/scene.v0.json`. Check: a new test finds every component name in the prompt, and the schema test passes.
- [ ] T016 [US5] Run `unfold build SERIES --until scene`, then `unfold render SERIES`, for each of the six golden series. Check: only scene jobs call a model, and every render reports 0 layout failures.
- [ ] T017 [US5] Record the after numbers in `../content/series/after-packs.json`. Read every contact sheet that holds a new component, then write `docs/evals/M8-packs-report.md`. Check: the custom share is at most 10 percent, and no scene check passes less often than before.

## Phase 8: Polish

- [ ] T018 Converge, then update `docs/progress.md` and `docs/journal.md`, open the pull request, and merge after CI passes. Check: the converge pass appends no task, and every CI job passes.

## Dependencies and execution order

- Setup and the foundational tasks come first. T003 must run before T006 raises the version, or the before-numbers change.
- User stories 1 to 4 each need only the foundation. They share `params.py` and `components.py`, so one agent does them in order: US1, US2, US3, then US4.
- User story 5 needs all four components. T013 and T014 can run in parallel. T015 comes before the rebuild, and T016 before the report.

## Parallel example

T004 writes new files only, so it can run while T002 and T003 run. Within user story 5:

```text
Task: "T013 property tests in tests/visuals/test_pack_props.py"
Task: "T014 grounded numbers in src/unfold/evals/__init__.py"
```

## Implementation strategy

1. MVP: the setup, the foundation, and user story 1. The present-value component alone removes six custom visuals and every invented present value.
2. Add one component per story, test first, with one commit each near 300 changed lines.
3. Rebuild the golden set only after the prompt knows every component, so the model makes one round of calls.

# Tasks: Text generation

**Input**: Design documents from `specs/004-text-generation/`

**Tests**: requested. Each test runs and fails before its code exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel, because it touches different files and depends on nothing unfinished.
- Each task ends with its check.

## Phase 1: Setup

- [ ] T001 Add pydantic, and log it in `docs/dependencies.md` with its license and safety note. Check: `uv sync --extra audio` succeeds, and `import pydantic` works.

## Phase 2: Foundational

- [ ] T002 Write tests in `tests/understand/test_jobs.py` for structured output and records. `command()` adds `--json-schema`, and `parse()` reads `structured_output` into the reply. Records gain `format: job/v0` and `tries`, and old records still load. Check: the new tests fail.
- [ ] T003 Implement those changes in `src/unfold/jobs.py`. Check: `tests/understand` passes.

## Phase 3: User Story 1, check any file (Priority: P1)

**Goal**: every format has a schema, and `unfold check` validates any file.

**Independent Test**: check every example file, then files with one deliberate error each.

- [ ] T004 [P] [US1] Write `tests/formats/test_formats.py`. Every example file validates, a broken outline names its missing field and place, and an unknown format fails. Check: the tests fail.
- [ ] T005 [US1] Implement source/v0, source/v1, knowledge-map/v0, and job/v0 in `src/unfold/formats/sources.py`. Check: their tests pass.
- [ ] T006 [US1] Implement series/v0 and series-plan/v0 in `src/unfold/formats/series.py`. Implement outline/v0, script/v0, script/v1, and storyboard/v0 in `src/unfold/formats/episode.py`. Add the registry and `load_any()` to `src/unfold/formats/__init__.py`. Check: `tests/formats` passes.
- [ ] T007 [P] [US1] Write `tests/formats/test_export.py`, which compares `schemas/` with each model's JSON Schema. Then write `src/unfold/formats/export.py` and export the files. Check: the test passes.
- [ ] T008 [US1] Write `tests/test_check.py` for exit codes 0, 1, and 2, and for folders. Then implement `unfold check` in `src/unfold/check.py`. Check: the tests pass, and `uv run unfold check examples/econ-supply-demand` exits 0.

## Phase 4: User Story 3, checked text at each step (Priority: P1)

**Goal**: each step asks for data that matches its schema, then checks its meaning.

**Independent Test**: a fake runner returns good data, bad data, and data that is good on the second try.

- [ ] T009 [P] [US3] Write `tests/build/test_job.py` for the job loop. Success writes the output, and a retry carries the errors. Four failures write nothing and keep every try's errors. Data that breaks the schema counts as a failed try, and a matching key means reuse. Check: the tests fail.
- [ ] T010 [US3] Implement the job loop, keys, and records in `src/unfold/build/__init__.py`. Check: `tests/build/test_job.py` passes.
- [ ] T011 [P] [US3] Write `tests/build/test_checks.py` for the meaning checks of each step, as `data-model.md` lists them. Check: the tests fail.
- [ ] T012 [US3] Implement `src/unfold/build/checks.py`. Check: `tests/build/test_checks.py` passes.
- [ ] T013 [P] [US3] Write `tests/build/test_write.py`. A written script/v1 reads back through `parse_script()`, and each YAML output validates. Check: the tests fail.
- [ ] T014 [US3] Implement `src/unfold/build/write.py`, and teach `src/unfold/script.py` the script/v1 anchors. Check: `tests/build/test_write.py` and `tests/test_script.py` pass.
- [ ] T015 [US3] Write the prompts `series-plan.md`, `outline.md`, `script.md`, and `storyboard.md` in `src/unfold/prompts/`. Check: each passes `unfold lint`.
- [ ] T016 [P] [US3] Write `tests/build/test_steps.py`. Each step builds its request from its inputs, and a script request holds only the cited source blocks. Check: the tests fail.
- [ ] T017 [US3] Implement `src/unfold/build/steps.py`. Check: `tests/build/test_steps.py` passes.

## Phase 5: User Story 2, build a series (Priority: P1)

**Goal**: `unfold build` runs every step in order, and reuses saved results.

**Independent Test**: build with a fake runner, change one input, and check which steps run again.

- [ ] T018 [P] [US2] Write `tests/build/test_graph.py`. A build writes a plan, an outline, two scripts, and two storyboards. A second run calls nothing. A changed knowledge map reruns only later steps, and `--until` stops early. Check: the tests fail.
- [ ] T019 [US2] Implement the graph in `src/unfold/build/graph.py`. Check: `tests/build/test_graph.py` passes.
- [ ] T020 [US2] Write `tests/build/test_command.py` for exit codes 0, 1, 2, and 3. Then implement `unfold build` in `src/unfold/build/command.py`. Check: the tests pass.

## Phase 6: User Story 4, stop early (Priority: P2)

**Goal**: a canary guards each build, and a log records each call.

**Independent Test**: a build whose canary fails makes no other call.

- [ ] T021 [P] [US4] Write `tests/build/test_canary.py`. A failing canary stops the build, and a build with nothing to run makes no call. Each call adds one line to `calls.jsonl`. Check: the tests fail.
- [ ] T022 [US4] Implement the canary in `src/unfold/jobs.py` and the call log in `src/unfold/build/__init__.py`. Check: `tests/build/test_canary.py` passes.

## Phase 7: User Story 5, the first eval report (Priority: P2)

**Goal**: error analysis on real outputs, then binary checks with pass rates.

**Independent Test**: run the checks on the golden outputs, and compare the pass rates with the report.

- [ ] T023 [US5] Write six series files in `../content/series/`, one per golden source, and build each. Check: every output passes `unfold check`, and the call logs hold at most 60 calls.
- [ ] T024 [US5] Build all six again. Check: no call log gains a line.
- [ ] T025 [US5] Read every output, and write open notes in `../content/series/notes.md`. Group them into failure types. Check: at least 3 failure types, each with a count.
- [ ] T026 [P] [US5] Write `tests/evals/test_checks.py`, with one binary check per failure type on small examples. Check: the tests fail.
- [ ] T027 [US5] Implement the checks in `src/unfold/evals/__init__.py` and `unfold eval` in `src/unfold/evals/command.py`. Check: the tests pass, and `unfold eval` prints a pass rate per check.
- [ ] T028 [US5] Write `docs/evals/M4-report.md` with the failure types, checks, and pass rates. Check: it passes `unfold lint`, and it quotes only sources with public outputs.

## Phase 8: Polish

- [ ] T029 Describe series/v0, series-plan/v0, script/v1, and `schemas/` in `docs/formats.md`. Check: `unfold lint docs` passes.
- [ ] T030 Converge, record the M4 gates in `docs/milestones.json`, write `docs/retros/M4.md`, and tag `m4-done`. Check: every M4 gate has evidence.

## Dependencies & Execution Order

- Setup and Foundational come first, because every story needs the runner changes.
- User Story 1 is independent. Its schemas also serve the steps.
- User Story 3 comes before User Story 2, because the graph runs the steps.
- User Story 4 needs the job loop from User Story 3.
- User Story 5 needs every other story, because it runs the real build.

## Parallel Example: Phase 4

```text
Task: "T009 Write tests/build/test_job.py"
Task: "T011 Write tests/build/test_checks.py"
Task: "T013 Write tests/build/test_write.py"
```

## Implementation Strategy

1. Setup and Foundational: the runner speaks structured output.
2. User Story 1: schemas and `unfold check`, which stand alone.
3. User Stories 3, 2, and 4: the steps, the graph, and the guards, all driven by fake runners.
4. User Story 5: the real build, then error analysis and the report.

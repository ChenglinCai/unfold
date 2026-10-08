# Tasks: Product and release

**Input**: Design documents from `specs/007-product/`

**Tests**: requested. Each test runs and fails before its code exists.

## Phase 1: User Story 1, the doctor (Priority: P1)

- [X] T001 [US1] Write `tests/test_doctor.py`, then implement `src/unfold/doctor.py` and `unfold doctor`. Check: the tests pass.

## Phase 2: User Stories 2 and 3, review and gallery

- [X] T002 [US2] Write `tests/test_pages.py` for the review page, then implement it in `src/unfold/pages.py`. Check: the tests pass.
- [X] T003 [US3] Add tests for the gallery's rights rule, then implement `unfold gallery`. Check: the tests pass.

## Phase 3: User Story 4, Claude Code

- [X] T004 [US4] Add the `mcp` extra, write `tests/test_mcp_server.py`, then implement `src/unfold/mcp_server.py`. Check: the tests pass.
- [X] T005 [US4] Write the plugin in `plugin/`, with its manifest, skill, and server config. Check: a test reads the manifest and the skill.

## Phase 4: User Story 5, the quickstart

- [X] T006 [US5] Write `examples/quickstart/` and `docs/quickstart.md`, and a test that renders the example. Check: the slow test passes.
- [ ] T007 [US5] Add `.github/workflows/quickstart.yml`, which runs the quickstart on a clean macOS runner. Check: the job passes.

## Phase 5: Polish

- [ ] T008 Converge, record the M7 gates, write `docs/retros/M7.md`, tag `m7-done`, and merge. Check: every M7 gate has evidence.

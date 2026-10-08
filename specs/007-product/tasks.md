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
- [X] T007 [US5] Add `.github/workflows/quickstart.yml`, which runs the quickstart on a clean macOS runner. Check: the job passes.

## Phase 5: Polish

- [X] T008 Converge, record the M7 gates, write `docs/retros/M7.md`, tag `m7-done`, and merge. Check: every M7 gate has evidence.

## Phase 6: Convergence

- [X] T009 Make the gallery fail closed, so a series with no sources or unclear rights stays private, per FR-003 and Constitution VII (partial)
- [X] T010 Add an `ingest` tool to `src/unfold/mcp_server.py`, and point step 2 of `plugin/skills/unfold/SKILL.md` at it, per US4 (partial)
- [X] T011 Install the `audio` extra with the plugin's server, so step 5 of the skill can check audio, per US4 (partial)
- [X] T012 Write `plugin/README.md`: what the plugin installs and runs, what could go wrong, and how to remove it, per Constitution IX (partial)

## Phase 7: Security review

The plan names a security review as an M7 practice. It found two gaps.

- [X] T013 Pass `--` before each positional value in `src/unfold/mcp_server.py`, so a tool argument never becomes an option
- [X] T014 Keep ids that are not plain names out of the review page and the gallery, and so out of paths and HTML

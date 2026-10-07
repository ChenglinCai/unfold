# Tasks: Source understanding

**Input**: Design documents from `specs/003-source-understanding/`

**Tests**: requested. Each test runs and fails before its code exists.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel, because it touches different files and depends on nothing unfinished.
- Each task ends with its check.

## Phase 1: Setup

- [X] T001 Add pypdfium2, python-pptx, and trafilatura, and faster-whisper as the `audio` extra. Log each one in `docs/dependencies.md`. Check: `uv sync --extra audio` succeeds.

## Phase 2: Foundational

- [X] T002 Write `tests/sources/test_document.py` for saving and loading a source document, its anchor markers, and its manifest. Check: the tests fail.
- [X] T003 Implement the SourceDocument type in `src/unfold/sources/__init__.py`. Check: `tests/sources/test_document.py` passes.
- [X] T004 [P] Write `tests/sources/test_profile.py` for the public-output rule and the low-quality flag. Check: the tests fail.
- [X] T005 Implement `src/unfold/sources/profile.py`. Check: `tests/sources/test_profile.py` passes.

## Phase 3: User Stories 1 and 2, ingest and profile (Priority: P1) MVP

**Goal**: every family becomes a source document with a profile.

**Independent Test**: each adapter's test builds a small sample, ingests it, and checks the anchors and profile.

- [X] T006 [P] [US1] Write `tests/sources/test_pdf.py`, which draws a two-page PDF with cairo. Check: the tests fail.
- [X] T007 [US1] Implement `src/unfold/sources/pdf.py` for textbooks and slides. Check: `tests/sources/test_pdf.py` passes.
- [X] T008 [P] [US1] Write `tests/sources/test_deck.py`, which builds a two-slide deck. The name avoids `pptx`, the package it reads. Check: the tests fail.
- [X] T009 [US1] Implement `src/unfold/sources/deck.py`. Check: `tests/sources/test_deck.py` passes.
- [X] T010 [P] [US1] Write `tests/sources/test_web.py` for a Markdown file and a local HTML page. Check: the tests fail.
- [X] T011 [US1] Implement `src/unfold/sources/web.py`. Check: `tests/sources/test_web.py` passes.
- [X] T012 [P] [US1] Write `tests/sources/test_scan.py`, which draws text into an image and skips off macOS. Check: the tests fail.
- [X] T013 [US1] Implement `src/unfold/sources/scan.py` and `src/unfold/sources/vision.swift`. Check: `tests/sources/test_scan.py` passes.
- [ ] T014 [P] [US1] Write `tests/sources/test_recording.py`, which speaks a sentence and skips without the audio extra. Check: the tests fail.
- [ ] T015 [US1] Implement `src/unfold/sources/recording.py`. Check: `tests/sources/test_recording.py` passes.
- [ ] T016 [US1] Implement `src/unfold/sources/topic.py` and `unfold ingest` in `src/unfold/sources/command.py`, test first. Check: `tests/sources/test_command.py` passes.

## Phase 4: User Story 3, understand (Priority: P1)

**Goal**: a validated knowledge map and study notes, from one job with no tools.

**Independent Test**: a fake runner drives every path: success, retry, failure, reuse, and bare topics.

- [ ] T017 [P] [US3] Write `tests/understand/test_jobs.py` for the runner's command: no tools, no settings, no MCP servers, and JSON output. Check: the tests fail.
- [ ] T018 [US3] Implement `src/unfold/jobs.py` with the runner, saved results, and job records. Check: `tests/understand/test_jobs.py` passes.
- [ ] T019 [P] [US3] Write `tests/understand/test_checks.py` for the knowledge-map and study-note checks. Check: the tests fail.
- [ ] T020 [US3] Implement `src/unfold/understand/checks.py`. Check: `tests/understand/test_checks.py` passes.
- [ ] T021 [US3] Write `tests/understand/test_understand.py`, which uses a fake runner for every path. Check: the tests fail.
- [ ] T022 [US3] Implement `src/unfold/understand/__init__.py` and `unfold understand`. Check: `tests/understand/test_understand.py` passes.

## Phase 5: User Story 4, the gate (Priority: P2)

- [ ] T023 [US4] Download the four golden sources into `../content/sources/`, then ingest them and the bare topic. Check: five source documents exist.
- [ ] T024 [US4] Run understand on all five, within 15 model jobs. Check: every output passes its checks, and a second run makes no calls.

## Phase 6: Polish

- [ ] T025 Lint the study notes with the written profile, and record the results. Check: `docs/studies/` holds the counts per source.
- [ ] T026 Converge: compare the result with the spec, record the M2 gates, and tag `m2-done`. Check: every M2 gate has evidence.

## Dependencies & Execution Order

- Setup comes first, then Foundational, which blocks every story.
- The adapters in Phase 3 are independent of each other.
- Phase 4 needs the SourceDocument type, but not the adapters.
- The gate needs Phases 3 and 4.

## Parallel Example: Phase 3

```text
Task: "T006 Write tests/sources/test_pdf.py"
Task: "T008 Write tests/sources/test_deck.py"
Task: "T010 Write tests/sources/test_web.py"
```

## Implementation Strategy

1. Setup and Foundational: the shared format.
2. The PDF and web adapters first, because three golden sources need them.
3. The understand step, driven by a fake runner, so no model call happens until the gate.
4. The gate, which makes the real model calls.

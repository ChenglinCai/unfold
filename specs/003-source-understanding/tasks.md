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
- [X] T014 [P] [US1] Write `tests/sources/test_recording.py`, which speaks a sentence and skips without the audio extra. Check: the tests fail.
- [X] T015 [US1] Implement `src/unfold/sources/recording.py`. Check: `tests/sources/test_recording.py` passes.
- [X] T016 [US1] Implement `src/unfold/sources/topic.py` and `unfold ingest` in `src/unfold/sources/command.py`, test first. Check: `tests/sources/test_command.py` passes.

## Phase 4: User Story 3, understand (Priority: P1)

**Goal**: a validated knowledge map and study notes, from one job with no tools.

**Independent Test**: a fake runner drives every path: success, retry, failure, reuse, and bare topics.

- [X] T017 [P] [US3] Write `tests/understand/test_jobs.py` for the runner's command: no tools, no settings, no MCP servers, and JSON output. Check: the tests fail.
- [X] T018 [US3] Implement `src/unfold/jobs.py` with the runner, saved results, and job records. Check: `tests/understand/test_jobs.py` passes.
- [X] T019 [P] [US3] Write `tests/understand/test_checks.py` for the knowledge-map and study-note checks. Check: the tests fail.
- [X] T020 [US3] Implement `src/unfold/understand/checks.py`. Check: `tests/understand/test_checks.py` passes.
- [X] T021 [US3] Write `tests/understand/test_understand.py`, which uses a fake runner for every path. Check: the tests fail.
- [X] T022 [US3] Implement `src/unfold/understand/__init__.py` and `unfold understand`. Check: `tests/understand/test_understand.py` passes.

## Phase 5: User Story 4, the gate (Priority: P2)

- [X] T023 [US4] Download the four golden sources into `../content/sources/`, then ingest them and the bare topic. The CUNY deck sits behind a bot wall, so MIT 18.05's Class 10 slides take its place, under CC BY-NC-SA 4.0. Check: five source documents exist.
- [X] T024 [US4] Run understand on all five, within 15 model jobs. Check: every output passes its checks, and a second run makes no calls. Result: 5 jobs, each passing on its first try. A second run reused all five results.

## Phase 6: Polish

- [X] T025 Lint the study notes with the written profile, and record the results. Check: `docs/studies/` holds the counts per source. Result: `docs/studies/study-notes-lint.md`.
- [X] T026 Converge: compare the result with the spec, record the M2 gates, and tag `m2-done`. Check: every M2 gate has evidence.

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

## Phase 7: Convergence

- [X] T027 CRITICAL: Ask the maintainer to resolve the one-output rule. The understand job writes two files, a knowledge map and study notes. Record the question in `docs/progress.md`, with the recommendation to split the job in M4, per Constitution II (contradicts)
- [X] T028 CRITICAL: Ask the maintainer which versions a key must cover. The understand key leaves out the manim and component-library versions, which its outputs never use. Record proposed wording in `docs/progress.md`, per Constitution II (contradicts)
- [X] T029 CRITICAL: Add a finance source to the golden set, then ingest and understand it with one model job. Check: six outputs pass their checks, per Constitution IV (missing)
- [X] T030 State the safety implications of downloads and parsing libraries in `docs/dependencies.md`. Say what they allow, what could go wrong, and how to undo them, per Constitution IX (partial)
- [X] T031 Add a hint to the profile of a PDF with almost no text, which suggests the scan reader. Check: a test in `tests/sources/test_pdf.py`, per Edge Cases (partial)
- [X] T032 Add a slow test that a recording with a long silence keeps correct timestamps, in `tests/sources/test_recording.py`, per Edge Cases (missing)
- [X] T033 Add `files` to the manifest, naming the text file and any original, in `src/unfold/sources/__init__.py`, per data-model source/v1 (partial)
- [X] T034 Add `family` to the profile, so the profile states every fact that FR-004 names, per FR-004 (partial)
- [X] T035 Record the formula-keeping web reader and the citation-skipping linter as decisions in `research.md`, per plan research decisions (unrequested)
- [X] T036 Make `unfold understand` say "1 try", not "1 tries", per contracts/cli.md (partial)

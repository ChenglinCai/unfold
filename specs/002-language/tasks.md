# Tasks: The Narration Standard linter

**Input**: Design documents from `specs/002-language/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: requested. Every story writes its tests first, and runs them to see them fail, before writing code.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel, because it touches different files and depends on nothing unfinished.
- **[Story]**: the user story the task serves, such as US1.
- Each task ends with its check: the command or result that proves it is done.

## Phase 1: Setup

- [X] T001 Create `src/unfold/lint/__init__.py` and `src/unfold/cli.py`, and add `unfold = "unfold.cli:main"` under `[project.scripts]` in `pyproject.toml`. Check: `uv run unfold --help` prints the usage.
- [X] T002 [P] Write `docs/terms.yaml`, mapping each term to avoid to its preferred term and a reason, starting with "bookmark" to "cue". Check: it loads as a YAML mapping.

## Phase 2: Foundational

**Purpose**: units of prose, which every rule reads. No story can start before this phase ends.

- [X] T003 Write `tests/lint/test_prose.py`. It covers removing front matter, code blocks, inline code, tables, link addresses, HTML comments, and cue markers. It also covers splitting at sentence ends but not at decimals, versions, or "e.g.", list items as sentences, breath groups, and line numbers. Check: the tests fail, because the module is missing.
- [X] T004 Implement `src/unfold/lint/prose.py`, with paragraphs, sentences, and breath groups that keep their line numbers. Check: `uv run pytest tests/lint/test_prose.py` passes.

## Phase 3: User Story 1, lint a doc with the written profile (Priority: P1) MVP

**Goal**: `unfold lint` reports written-profile findings, and fails only on errors.

**Independent Test**: a file with a 30-word sentence and an arrow gives two errors and exit code 1.

### Tests for User Story 1

- [X] T005 [P] [US1] Write `tests/lint/test_rules_written.py` for N101, N102, N104, N201, N202, and N301. Use the limits in `data-model.md`: 25 words per sentence, 20 per numbered step, and a warning above 6 sentences per paragraph. Check: the tests fail.
- [X] T006 [P] [US1] Write `tests/lint/test_cli.py` for exit codes 0, 1, and 2, and for both output formats in `contracts/cli.md`. It also covers directories, and N900 for unreadable files. Check: the tests fail.

### Implementation for User Story 1

- [X] T007 [US1] Implement `Finding`, `Rule`, and `Profile`, and the written rules, in `src/unfold/lint/rules.py`, and `lint_text()` in `src/unfold/lint/__init__.py`. Check: `tests/lint/test_rules_written.py` passes.
- [X] T008 [US1] Implement the `lint` subcommand in `src/unfold/cli.py`, as `contracts/cli.md` describes. Check: `tests/lint/test_cli.py` passes.

## Phase 4: User Story 2, lint narration with the spoken profile (Priority: P1)

**Goal**: the spoken profile checks breath groups and the rules for speech.

**Independent Test**: a beat with a parenthesis, "e.g.", an equals sign, and "see Figure 3" gets four errors.

### Tests for User Story 2

- [X] T009 [US2] Write `tests/lint/test_rules_spoken.py` for rules N101 to N206 in the spoken profile. It also covers N206 at "more than 15 words after the cue", and cue markers that do not count as words. Check: the tests fail.

### Implementation for User Story 2

- [X] T010 [US2] Implement the spoken and strict profiles, and rules N103 to N206, in `src/unfold/lint/rules.py`. Start with a provisional breath-group limit of 20 words. Check: `tests/lint/test_rules_spoken.py` passes.

## Phase 5: User Story 3, AI writing habits and replaced terms (Priority: P2)

**Goal**: warnings for AI habits and replaced terms, and a safe fixer.

**Independent Test**: every paragraph in the AI-style set gets a finding.

### Tests for User Story 3

- [X] T011 [P] [US3] Write `tests/lint/sets/ai_style.md` with at least 10 paragraphs written in AI style, `tests/lint/sets/clean.md` with at least 5 clean paragraphs, and `tests/lint/test_sets.py`. Check: the tests fail.
- [X] T012 [P] [US3] Write `tests/lint/test_fix.py`. The fixer expands "e.g." and replaces avoided terms, changes nothing else, and is stable when run twice. Check: the tests fail.

### Implementation for User Story 3

- [X] T013 [US3] Write `src/unfold/lint/words.py` with three lists. They hold the AI vocabulary and phrases from Wikipedia's "Signs of AI writing", abbreviations with their spoken forms, and irregular past participles. Check: the module imports.
- [X] T014 [US3] Implement N302, N303, N304, and N305 in `src/unfold/lint/rules.py`. Check: `tests/lint/test_sets.py` passes.
- [X] T015 [US3] Implement `src/unfold/lint/fix.py`, and the `--fix` option in `src/unfold/cli.py`. Check: `tests/lint/test_fix.py` passes.

## Phase 6: User Story 4, evidence for the spoken limits (Priority: P2)

**Goal**: a report that tests the hypothesis and sets the spoken limit.

**Independent Test**: the study writes `docs/studies/breath-groups.md` from at least 50 transcripts.

### Tests for User Story 4

- [X] T016 [US4] Write `tests/lint/test_study.py`, using a small invented transcript and word timings, not real 3Blue1Brown text. It covers breath-group lengths, percentiles, pause agreement, and speaking rate. Check: the tests fail.

### Implementation for User Story 4

- [X] T017 [P] [US4] Write `corpus/README.md` with the download command and the rights note. Check: the writing check passes.
- [X] T018 [US4] Implement `corpus/breath_groups.py`, which reads transcripts by path and writes numbers only. Check: `tests/lint/test_study.py` passes.
- [X] T019 [US4] Run the study on the 144 private transcripts, write `docs/studies/breath-groups.md`, and set the spoken limit in `src/unfold/lint/rules.py` from it. Check: the report covers at least 50 transcripts, and its firing rate meets SC-002.

## Phase 7: Polish

- [X] T020 Add two local hooks to `.pre-commit-config.yaml`: the written profile on Markdown docs, and the spoken profile on `script.md` files. Check: `uv run pre-commit run --all-files` passes.
- [X] T021 Fix every error that the linter finds in the repo's docs. Check: `uv run unfold lint README.md CLAUDE.md docs specs` exits 0.
- [X] T022 [P] Replace the scratch measurement script with `unfold lint` in `.specify/memory/constitution.md` and `CLAUDE.md`. Check: both name `unfold lint`.
- [X] T023 Time a lint of the whole repo. Check: under 5 seconds, as SC-005 requires.
- [ ] T024 Converge: compare the result with the spec, record the M3 gates in `docs/milestones.json`, and tag `m3-done`. Check: every M3 gate has evidence or a stated reason.

## Dependencies & Execution Order

### Phase Dependencies

- Setup comes first. Foundational depends on Setup, and blocks every story.
- US1 builds the rule framework, so US2 and US3 start after it.
- US2 and US3 do not depend on each other.
- US4 depends on US2, because the study uses the spoken breath groups.
- Polish comes last.

### Within Each User Story

- Tests come first, and must fail before the code.
- Word lists come before the rules that use them.
- Each story ends with its independent test passing.

### Parallel Opportunities

- T002 can run beside T001.
- T005 and T006 touch different files.
- T011 and T012 can run beside US2, because they only write tests and test sets.
- T017 can run at any time.

## Parallel Example: User Story 1

```text
Task: "T005 Write tests/lint/test_rules_written.py"
Task: "T006 Write tests/lint/test_cli.py"
```

## Implementation Strategy

### MVP First

Finish Setup, Foundational, and US1. The written profile alone can then lint the repo's docs, which replaces the scratch script.

### Incremental Delivery

1. Setup and Foundational, then US1: the written linter works.
2. US2: narration can be linted.
3. US3: AI habits and the fixer.
4. US4: the study sets the spoken limit with evidence.
5. Polish: CI runs the linter, and the docs pass it.

## Notes

- Commit after each task or each pair of test and code, and keep each commit under 300 changed lines.
- The transcripts never enter the repo. Tests use invented text only.

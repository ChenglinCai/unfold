# Tasks: Chinese subtitles

**Input**: Design documents from `specs/009-chinese-subtitles/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, and quickstart.md

**Tests**: requested. Each test runs and fails before its code exists. Each task names its check.

**Organization**: the pure functions come first, because the job needs them. Then one phase per user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel, because it touches other files and waits on no open task.
- **[Story]**: the user story from spec.md, such as US1.

## Phase 1: Foundational

The feature adds no dependency, so it needs no setup phase.

- [X] T001 Write tests in `tests/episodes/test_stitch.py` for `episode_beats`, which lists each beat's id, text, and spoken start and end in episode time. Then add beat names to `Part`, and `episode_beats` and `read_parts` to `src/unfold/episodes/stitch.py`, and use them in `stitch_episode`. Check: the tests pass.
- [X] T002 Rebuild the English cues of the seven golden episodes from `read_parts`, and compare each with its saved `episode.srt`. Check: all seven match byte for byte.
- [X] T003 Write tests for `zh_cues` in `tests/episodes/test_translate.py`, then implement it in `src/unfold/episodes/translate.py`. A cue holds "at most two lines of 16 characters", with the shorter line on top. Breaks fall at spaces when they can, and time follows each cue's share of characters. Check: the tests pass.
- [ ] T004 Write tests for `check_translation` in `tests/episodes/test_translate.py`, then implement it. It rejects each case in data-model.md. A missing or extra beat fails, and so do a comma, a period that is not a decimal point, and a full-width digit. It also rejects a beat with no Chinese, a run of four or more lowercase Latin letters, and a beat over its budget. Check: the tests pass.

## Phase 2: User Story 1, translate an episode (Priority: P1) 🎯 MVP

**Goal**: one command gives every rendered episode Chinese subtitles.

**Independent test**: translate a small rendered episode with a fake runner, then read the subtitle file.

- [ ] T005 [US1] Write tests with a fake runner. The job writes `episode.zh.srt`, a second run calls no runner, and an unrendered episode gets a note. Then add the reply model, the job, and `src/unfold/prompts/translate-zh.md`. Check: the tests pass.
- [ ] T006 [US1] Write tests for `unfold translate` and the exit codes in `contracts/cli.md`. Then implement the command with a RUNNER global, and register it in `src/unfold/cli.py`. Check: the tests pass.

## Phase 3: User Story 2, follow the style guide (Priority: P1)

**Goal**: every cue follows the guide, and a reply that breaks a rule gets its errors back.

**Independent test**: a fake runner first returns a reply with a comma, then a clean one.

- [ ] T007 [US2] Write a test where the fake runner first breaks a rule, and check that the second request carries the error. Add a test that a reply that never passes fails after 3 retries. Check: the tests pass.

## Phase 4: User Story 3, share the subtitles (Priority: P2)

**Goal**: the gallery and Claude Code both reach the Chinese subtitles.

**Independent test**: build a gallery from a public series with Chinese subtitles, and list the server's tools.

- [ ] T008 [P] [US3] Write a test in `tests/test_pages.py` that the gallery copies `episode.zh.srt` for a public series, then implement it in `src/unfold/pages.py`. Check: the test passes.
- [ ] T009 [P] [US3] Write a test in `tests/test_mcp_server.py` that the server offers a translate tool. Then add the tool to `src/unfold/mcp_server.py` and the plugin's skill. Check: the test passes.

## Phase 5: User Story 4, translate the golden set (Priority: P1)

**Goal**: the seven golden episodes gain Chinese subtitles that pass every check.

**Independent test**: translate the golden set, then run it again.

- [ ] T010 [US4] Run `unfold translate SERIES --to zh` on each of the six golden series. Check: seven episodes written, and none failed.
- [ ] T011 [US4] Run the same commands again. Check: every episode reused, and no new line in any `calls.jsonl`.
- [ ] T012 [US4] Read every cue of one public episode beside its video. Then write `docs/evals/M8-subtitles-report.md`, with the run's numbers and each fix the reading found. Check: the report quotes only sources that allow public outputs.

## Phase 6: Polish

- [ ] T013 [P] Add `episode.zh.srt` to `docs/formats.md`. Check: the written-profile lint passes.
- [ ] T014 Converge, update `docs/progress.md` and `docs/journal.md`, mark the pull request ready, and merge after CI passes. Check: the converge pass appends no task, and every CI job passes.

## Dependencies and execution order

- Phase 1 comes first. T002 needs T001, and T003 and T004 share files, so they run in order.
- User story 1 needs the foundation. User story 2 tests the job that user story 1 builds.
- User story 3 can start once user story 1 ends. T008 and T009 touch different files, so they can run in parallel.
- User story 4 needs every story before it, because it uses the finished command.

## Parallel example

```text
Task: "T008 the gallery copies episode.zh.srt, in src/unfold/pages.py"
Task: "T009 the MCP server's translate tool, in src/unfold/mcp_server.py"
```

## Implementation strategy

1. MVP: the foundation and user story 1. One command then translates an episode with every check in place.
2. Add the retry tests, the gallery, and the MCP tool, each test first.
3. Run the golden set last, so it costs about 8 model calls once.

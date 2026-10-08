# Implementation Plan: Chinese subtitles

**Branch**: `m8-subtitles` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/009-chinese-subtitles/spec.md`

## Summary

`unfold translate SERIES --to zh` writes Simplified Chinese subtitles beside each rendered episode. One model job per episode translates whole beats, and code splits them into cues that follow Netflix's style guide. Code checks each reply, retries with feedback, and reuses saved results. Stitching and translation share one timing source, so the two languages line up. [research.md](research.md) records each design decision.

## Technical Context

**Language/Version**: Python 3.12, in the existing unfold package.

**Primary Dependencies**: none new. Pydantic defines the reply, and the build package runs the job.

**Storage**: files. `episode.zh.srt` sits beside `episode.srt`, and the job's record sits under the series' `records/` folder.

**Testing**: pytest, test first, with a fake runner, so no test calls a model.

**Target Platform**: macOS and Linux, as before.

**Project Type**: a library with a command-line interface.

**Performance Goals**: one model call per episode, plus retries. A second run makes none.

**Constraints**: no model call in any test, and commits near 300 changed lines.

**Scale/Scope**: seven golden episodes, about 8 model calls with the canary.

## Constitution Check

*Gate: checked before research, and again after design.*

| Principle | Result |
|---|---|
| I. Own model access | Passes. Translation runs on the maintainer's access, and tests use a fake runner. |
| II. Code keeps track | Passes. Translation is a job with one output file, and its key covers its inputs, prompt, model, and schema. |
| III. Evidence | Passes. Each task names its test first. The evidence is test output and the golden run. |
| IV. Evals from failures | Passes. The checks come from the published style guide, and a person reads one episode before any new check. |
| V. Two families | Passes. The golden episodes come from five source families. |
| VI. Plain language | Passes. Docs use the written profile. The style guide governs the Chinese text. |
| VII. Rights | Passes. Subtitles of private sources stay private, and the gallery copies only public series. |
| VIII. The human decides | Deviation, recorded. Claude made the design calls in research.md, and each waits for the gate. |
| IX. Safety | Passes. No new dependency or permission. The new MCP tool runs one unfold command, like the others. |

The check after design found no new issue.

## Project Structure

### Documentation (this feature)

```text
specs/009-chinese-subtitles/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/cli.md
└── tasks.md          written by the tasks step
```

### Source Code (repository root)

```text
src/unfold/episodes/stitch.py       parts read from the rendered files, and beats with ids and times
src/unfold/episodes/translate.py    the Chinese cue splitter, the checks, the job, and the command
src/unfold/prompts/translate-zh.md  the translation prompt
src/unfold/cli.py                   registers `unfold translate`
src/unfold/pages.py                 the gallery copies episode.zh.srt
src/unfold/mcp_server.py            a translate tool
tests/episodes/test_translate.py    splitter, checks, job, and command tests
tests/episodes/test_stitch.py       beats with ids and times
docs/formats.md                     episode.zh.srt
```

**Structure Decision**: translation joins the episodes package, beside stitching and subtitles, because it reads the same rendered files.

## Delivery order

1. The shared timing source, with a regression check on the golden English subtitles.
2. The Chinese cue splitter, then the checks, each test first.
3. The job and the command, with a fake runner.
4. The gallery, the MCP tool, and the docs.
5. The golden run, one person's reading, and the converge pass.

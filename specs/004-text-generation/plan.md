# Implementation Plan: Text generation

**Branch**: `dev`, for the overnight run in decision record 0006 | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-text-generation/spec.md`

## Summary

Pydantic models become the schema of every file format, and `unfold check` validates files with them. A build graph runs five steps for a series: understand, series plan, outline, script, and storyboard. Each new step asks the runner for structured output that matches its schema. Code then checks meaning, retries with the errors, and saves the result under a key. A Haiku canary runs before the first real job, and every call lands in a call log. Error analysis on the golden outputs then yields binary checks and the first eval report.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: pydantic 2, the only new runtime dependency, for the schemas. PyYAML writes the files. The headless Claude runner gains `--json-schema`. `research.md` gives the reasons.

**Storage**: files. Series folders live in the private content folder.

**Testing**: pytest with fake runners. No test or CI run calls a model.

**Target Platform**: macOS and Linux

**Project Type**: library and command-line tool

**Performance Goals**: a build with nothing to run finishes in under 2 seconds per series.

**Constraints**: at most 60 model calls for the gate, no tools for the model, and one output file for each new step.

**Scale/Scope**: 10 schemas, 4 new steps, and 6 golden series

## Constitution Check

*Checked before research, and again after design.*

| Principle | Before research | After design |
|---|---|---|
| I. Users bring their own model access | Passes. Jobs run on the maintainer's subscription. | Passes |
| II. Code keeps track, and agents write | Partly. Each new step writes one file, and its key covers inputs, prompt, model, and schema. Items 13 and 14 wait for the maintainer. | Same |
| III. Every claim has evidence | Passes. Tests come first, and each job record keeps every try's errors. | Passes |
| IV. Evals come from real failures | Passes. Error analysis comes before any check, and checks pass or fail. | Passes. The golden set covers every family and subject. |
| V. Two source families | Passes. Six golden series span five families. Each beat lists its anchors. | Passes |
| VI. Plain language | Passes. Narration must pass the spoken profile. | Passes |
| VII. Rights and privacy | Passes. Series stay private, and the report quotes only public outputs. | Passes |
| VIII. The human decides | Changed for the overnight run, as in M1. | Same |
| IX. Safety | Passes. The model has no tools, and pydantic goes into `docs/dependencies.md`. | Passes. Structured output adds no tool with side effects. |

## Project Structure

### Documentation (this feature)

```text
specs/004-text-generation/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── contracts/cli.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
schemas/                  exported JSON Schema files, one per format and version
src/unfold/
├── formats/
│   ├── __init__.py       the registry from format name to model, and load_any()
│   ├── sources.py        source/v0, source/v1, knowledge-map/v0, and job/v0
│   ├── series.py         series/v0 and series-plan/v0
│   ├── episode.py        outline/v0, script/v0, script/v1, and storyboard/v0
│   └── export.py         writes schemas/
├── check.py              unfold check
├── jobs.py               adds structured output, every try's errors, and the canary
├── build/
│   ├── __init__.py       Job, the job loop, keys, records, and the call log
│   ├── steps.py          series plan, outline, script, and storyboard
│   ├── checks.py         meaning checks for each step
│   ├── write.py          output files from validated data
│   └── command.py        unfold build
├── prompts/              series-plan.md, outline.md, narration.md, and storyboard.md
└── evals/
    ├── __init__.py       binary checks from error analysis
    └── command.py        unfold eval
tests/formats/, tests/build/, tests/evals/
```

**Structure Decision**: `formats` holds the schemas, so the name matches `docs/formats.md`. `build` holds the graph and its steps. `evals` stays apart, because its checks come from error analysis and change as failures change.

## Complexity Tracking

| Item | Why it is needed | Simpler choice rejected because |
|---|---|---|
| Legacy schemas for source/v0 and script/v0 | Hand-written M1 files still use them | Migrating every M1 file now would touch the private episode too |

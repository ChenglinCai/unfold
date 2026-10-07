# Implementation Plan: Source understanding

**Branch**: `dev`, for the overnight run in decision record 0006 | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-source-understanding/spec.md`

## Summary

Each adapter reads one format and writes a source document: a manifest in the source/v1 format and the clean text with anchor markers. A profile module fills in the facts and the rights. The understand step builds a prompt from the document and runs one headless Claude job with no tools. Code then validates the knowledge map and study notes it returns. It retries with the errors, at most 3 times, and saves the result under a key, so unchanged inputs cost nothing.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: pypdfium2 for PDFs, python-pptx for decks, trafilatura for web pages, and faster-whisper as the optional `audio` extra. Apple's Vision framework reads scans through a Swift script. `research.md` gives the reasons.

**Storage**: files. Source documents live in the private content folder.

**Testing**: pytest. Tests make their own small PDFs, decks, images, and HTML, and use a fake runner instead of the model. Scan and recording tests skip where their tools are missing.

**Target Platform**: macOS and Linux. Scans need macOS.

**Project Type**: library and command-line tool

**Performance Goals**: ingest each golden source in under 2 minutes

**Constraints**: no model calls in tests or CI, no tools for the model, and at most 15 model jobs for the gate

**Scale/Scope**: five adapters, one job type, and five golden sources

## Constitution Check

*Checked before research, and again after design.*

| Principle | Before research | After design |
|---|---|---|
| I. Users bring their own model access | Passes. Jobs run on the maintainer's subscription. | Passes |
| II. Code keeps track, and agents write | Passes. Code builds the prompt, validates the output, and writes the files. | Passes |
| III. Every claim has evidence | Passes. Tests come first, and each job leaves a record. | Passes |
| IV. Evals come from real failures | Partly. The gate's outputs feed the first error analysis in M4. | Same |
| V. Two source families | Passes. All four families share one format. | Passes |
| VI. Plain language | Passes. The prompt asks for plain language, and study notes go through the linter. | Passes |
| VII. Rights and privacy | Passes. Downloads go to the private folder, and the profile decides what may be public. | Passes |
| VIII. The human decides | Changed for the overnight run, as in M1. | Same |
| IX. Safety | Passes. The model has no tools, and each new dependency goes into `docs/dependencies.md`. | Passes. The Swift script only reads images. |

## Project Structure

### Documentation (this feature)

```text
specs/003-source-understanding/
├── spec.md, plan.md, research.md, data-model.md, quickstart.md
├── contracts/cli.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/unfold/
├── sources/
│   ├── __init__.py       SourceDocument: load and save the manifest and the text
│   ├── profile.py        rights and quality facts
│   ├── pdf.py            PDFs as textbooks or slides
│   ├── pptx.py           PowerPoint decks
│   ├── scan.py           images, through vision.swift
│   ├── vision.swift      Apple Vision text recognition
│   ├── web.py            web pages and Markdown
│   ├── recording.py      audio, through faster-whisper
│   ├── topic.py          bare topics
│   └── command.py        unfold ingest
├── jobs.py               the headless Claude runner, saved results, and job records
└── understand/
    ├── __init__.py       prompt, parse, validate, retry
    ├── checks.py         knowledge-map and study-note checks
    └── command.py        unfold understand

tests/sources/            one test file per adapter, plus the profile
tests/understand/         the runner's command, the checks, and the retry loop
```

**Structure Decision**: two subpackages, `sources` and `understand`, as the pipeline's first two steps. `jobs.py` stays separate, because M4 grows it into the build graph.

## Complexity Tracking

None.

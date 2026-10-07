# Implementation Plan: The Narration Standard linter

**Branch**: `dev`, for the overnight run in decision record 0006 | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-language/spec.md`

## Summary

Build `unfold lint`, a linter for the Narration Standard with written, spoken, and strict profiles. A preprocessor strips Markdown that is not prose. A splitter cuts prose into paragraphs, sentences, and breath groups. Rules check each unit and return findings. A study script reads the private 3Blue1Brown transcripts, tests the breath-group hypothesis, and sets the spoken limit. Pre-commit runs the linter on the repo's docs, so CI does too.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: none new. PyYAML reads the replacement list, and `argparse` builds the command.

**Storage**: files. Rules live in code, replacements in `docs/terms.yaml`, and the study's numbers in `docs/studies/breath-groups.md`.

**Testing**: pytest, with test sets in `tests/lint/`

**Target Platform**: macOS and Linux

**Project Type**: library and command-line tool

**Performance Goals**: lint the whole repo in under 5 seconds

**Constraints**: no model calls, no new dependencies, and no transcripts in the repo. Ruff lets strings and comments run to 100 characters, because the formatter cannot wrap them. `words.py` is exempt from rule SIM905, because word lists read better as one split string.

**Scale/Scope**: about 15 rules, and 144 transcripts in the study

## Constitution Check

*Checked before research, and again after design.*

| Principle | Before research | After design |
|---|---|---|
| I. Users bring their own model access | Passes. The linter makes no model calls. | Passes |
| II. Code keeps track | Passes. Rules are deterministic code. | Passes |
| III. Every claim has evidence | Passes. Each rule has a test, written before its code. | Passes |
| IV. Evals come from real failures | Passes. The AI-style test set comes from the habits on Wikipedia's list, and the calibration comes from real transcripts. | Passes |
| V. Two source families | Passes. The tests cover docs and narration, and the study uses transcripts. | Passes |
| VI. Plain language | This feature puts the standard into code. | Passes. Every rule maps to a line of principle VI. |
| VII. Rights and privacy | Passes. Transcripts stay private, and only numbers reach the repo. | Passes |
| VIII. The human decides | Changed for the overnight run, as in M1. | Same |
| IX. Safety | Passes. No new dependency, and the hooks run no code that Claude wrote. | Passes. The pre-commit hooks run our linter, which only reads files. |

## Project Structure

### Documentation (this feature)

```text
specs/002-language/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/cli.md
├── checklists/requirements.md
└── tasks.md            written by /speckit-tasks
```

### Source Code (repository root)

```text
src/unfold/
├── cli.py              the unfold command and its lint subcommand
└── lint/
    ├── __init__.py     lint_text()
    ├── command.py      the lint subcommand, which cli.py registers
    ├── prose.py        preprocessing, and splitting into units
    ├── rules.py        the rules and the profiles
    ├── words.py        word lists: AI habits, abbreviations, irregular participles
    └── fix.py          the safe fixer

corpus/
├── README.md           how to download the transcripts into the private folder
└── breath_groups.py    the study

docs/terms.yaml
docs/studies/breath-groups.md

tests/lint/
├── test_prose.py
├── test_rules.py
├── test_cli.py
├── test_fix.py
└── test_sets.py        AI-style and clean paragraphs
```

**Structure Decision**: one package, as in M0 and M1. The linter is a subpackage, so `unfold.lint` can grow without crowding the package root.

## Complexity Tracking

None.

# Implementation Plan: Domain packs

**Branch**: `m8-packs` | **Date**: 2026-10-08 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/008-domain-packs/spec.md`

## Summary

Four new components replace the custom visuals that recur most in the golden set: `complex-plane`, `histogram`, `present-value`, and `flow-diagram`. Each one has a parameter model that never loads manim, and a drawing function that fits its region. Code computes every present value. The scene prompt learns the components, and the component version rises from 3 to 4. A golden rebuild then measures the custom share, the layout failures, and the eval pass rates before and after. [research.md](research.md) records each design decision.

## Technical Context

**Language/Version**: Python 3.12, in the existing unfold package.

**Primary Dependencies**: manim 0.21 and Pydantic 2, both present. Hypothesis joins the dev group only, for property tests. No runtime dependency is new.

**Storage**: files. Scenes stay `scene/v0` YAML, and `schemas/scene.v0.json` gains the new components.

**Testing**: pytest, test first. Parameter tests and present-value tests run without manim. Drawing tests check layout, property tests use random parameters, and one slow test renders each component.

**Target Platform**: macOS and Linux, as before.

**Project Type**: a library with a command-line interface.

**Performance Goals**: one drawing in under a second. The property tests add at most about 20 seconds to the suite.

**Constraints**: no LaTeX in the new components, no model call in any test, and commits near 300 changed lines.

**Scale/Scope**: six golden series, 12 segments, and 96 beats.

## Constitution Check

*Gate: checked before research, and again after design.*

| Principle | Result |
|---|---|
| I. Own model access | Passes. The rebuild runs on the maintainer's access, and tests call no model. |
| II. Code keeps track | Passes. The scene step stays a job, and its key covers the new component version. |
| III. Evidence | Passes. Each task names its test first. The evidence is test output, the eval report, and contact sheets. |
| IV. Evals from failures | Passes. The four components come from reading the golden custom visuals. The change stays only if SC-004 holds. |
| V. Two families | Passes. The scene prompt and format serve all six golden series, across five source families. |
| VI. Plain language | Passes. Docs use the written profile, and on-screen labels stay short. |
| VII. Rights | Passes. The report quotes only sources that allow public outputs. The components use our own code, with nothing from 3Blue1Brown's repositories. |
| VIII. The human decides | Deviation, recorded. The maintainer is away, so Claude made the design calls in research.md, and each waits for the gate. |
| IX. Safety | Passes. Hypothesis is a new dev dependency, so `docs/dependencies.md` states what it allows and how to remove it. |

The check after design found no new issue.

## Project Structure

### Documentation (this feature)

```text
specs/008-domain-packs/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md          written by the tasks step
```

The exported `schemas/scene.v0.json` is the contract for scene files, and data-model.md describes what it gains. So the feature needs no separate contracts folder.

### Source Code (repository root)

```text
src/unfold/visuals/params.py       four parameter models, and VERSION 4
src/unfold/visuals/components.py   four drawing functions
src/unfold/visuals/finance.py      present values and number formats, with no manim
src/unfold/prompts/scene.md        the new components, and when to use each
src/unfold/evals/__init__.py       the custom share, and grounded numbers for the new components
src/unfold/evals/command.py        the custom share in text and JSON
schemas/scene.v0.json              regenerated
tests/visuals/test_packs.py        parameter, drawing, and render tests
tests/visuals/test_pack_props.py   property tests with Hypothesis
tests/visuals/test_finance.py      present-value tests
tests/evals/                       custom share and grounded-number tests
docs/evals/M8-packs-report.md      before and after
docs/dependencies.md               the Hypothesis row
```

**Structure Decision**: the components join the existing visuals package, because the scene format already lists every component in one union. The finance module stays free of manim, so its tests run fast.

## Delivery order

1. Present value first: its pure functions, then the component, which also raises the version.
2. The complex plane, the histogram, and the flow diagram, each test first.
3. Property tests across all four components.
4. The scene prompt, the eval changes, and the exported schemas.
5. The golden rebuild, the report, and the converge pass.

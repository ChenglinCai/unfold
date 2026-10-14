# Implementation Plan: Neighborhood circle

**Branch**: `claude/local-folder-cloud-access-jlus4i` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/010-neighborhood-circle/spec.md`

## Summary

The scatter-plot component gains two optional parameters, a query point and k. Code finds the k nearest points, refuses ties, and computes the vote. The drawing adds the query point, a ring on each neighbor, and a shaded boundary around the neighborhood. With similar spans, both axes share one scale, so the boundary is a circle. The scene prompt learns the parameters, and the component version rises from 4 to 5. [research.md](research.md) records each design decision.

## Technical Context

**Language/Version**: Python 3.12, in the existing unfold package.

**Primary Dependencies**: manim 0.21 and Pydantic 2, both present. No dependency is new.

**Storage**: files. Scenes stay `scene/v0` YAML, and `schemas/scene.v0.json` gains the two parameters.

**Testing**: pytest, test first. Neighbor tests and parameter tests run without manim. Drawing tests check the layout, and a property test draws random plots.

**Target Platform**: macOS and Linux, as before.

**Project Type**: a library with a command-line interface.

**Performance Goals**: one drawing in under a second. The property test adds at most about 10 seconds to the suite.

**Constraints**: no LaTeX in the drawing, no model call in any test, and one pull request under about 300 changed lines.

**Scale/Scope**: a scatter plot holds at most 60 points, so a direct sort of distances costs nothing.

## Constitution Check

*Gate: checked before research, and again after design.*

| Principle | Result |
|---|---|
| I. Own model access | Passes. Tests call no model, and the golden rebuild runs on the maintainer's access. |
| II. Code keeps track | Passes. Code computes every neighbor and the vote. The scene step's key covers the new component version. |
| III. Evidence | Passes. Each task names its test first. The evidence is test output and a contact sheet of a sample plot. |
| IV. Evals from failures | Passes. The feature comes from three requests in the golden set. The custom share is measured at the next golden rebuild, which needs the content folder. |
| V. Two families | Passes. The prompt and the format serve every golden series. A k-nearest-neighbors lesson can come from a textbook, slides, or a recording. |
| VI. Plain language | Passes. Docs use the written profile, and the drawing adds no text. |
| VII. Rights | Passes. Tests use made-up points, and the code is our own. |
| VIII. The human decides | Deviation, recorded. The maintainer asked Claude to keep working, so Claude made the design calls in research.md, and each waits for the gate. |
| IX. Safety | Passes. The change adds no permission, hook, dependency, or public content. |

The check after design found no new issue.

## Project Structure

### Documentation (this feature)

```text
specs/010-neighborhood-circle/
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
src/unfold/visuals/neighbors.py    nearest points, ties, and the vote, with no manim
src/unfold/visuals/params.py       the query and k parameters, and VERSION 5
src/unfold/visuals/components.py   the query point, the rings, and the boundary
src/unfold/prompts/scene.md        the new parameters, and when to use them
schemas/scene.v0.json              regenerated
tests/visuals/test_neighbors.py    neighbor, tie, vote, parameter, and drawing tests
tests/visuals/test_pack_props.py   a property test with random plots
```

**Structure Decision**: the neighbor module stays free of manim, like `finance.py`, so its tests run fast. The drawing joins the existing scatter plot, because a neighborhood never appears without its points.

## Delivery order

1. The neighbor functions, test first.
2. The parameters and their checks, which also raise the version.
3. The drawing, then the property test.
4. The scene prompt and the exported schema.
5. The converge pass. The golden rebuild waits for the maintainer.

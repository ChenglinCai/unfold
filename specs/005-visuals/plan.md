# Implementation Plan: Visuals

**Branch**: `m5` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

## Summary

A theme and a grid of named regions frame every visual. Five components draw what the golden storyboards ask for, each from parameters that a Pydantic schema checks. A layout check measures built objects before any render. A scene step maps storyboard entries to components through one structured-output job per segment. `unfold render` checks, renders in parallel, and makes contact sheets.

## Technical Context

**Language/Version**: Python 3.12, ManimCE 0.21

**Primary Dependencies**: manim, pydantic, PyAV for reading frames, and Pillow, which manim installs, for contact sheets. No new dependency.

**Storage**: files in each segment's folder: `scene.yaml`, `segment.mp4`, and `contact-sheet.png`.

**Testing**: pytest. Component and layout tests build objects without rendering. One slow test renders a small scene.

**Constraints**: the model writes data, not code. At most 30 model calls for the golden set.

**Scale/Scope**: 5 components, 6 regions, and 12 golden segments

## Constitution Check

| Principle | Result |
|---|---|
| I. Own model access | Passes. The scene step uses the subscription runner. |
| II. Code keeps track | Passes. The scene step writes one file, and its key covers the component-library and manim versions. |
| III. Evidence | Passes. Tests first, and a contact sheet for every render. |
| IV. Evals from failures | Passes. Layout failures are checks, not scores. |
| V. Two families | Passes. Golden segments come from six sources. |
| VI. Plain language | Passes. Docs follow the written profile. |
| VII. Rights | Passes. Renders stay in the private content folder. |
| VIII. The human decides | The maintainer asked to keep going and merge. |
| IX. Safety | Passes. No model-written code runs, so no sandbox is needed yet. |

## Project Structure

```text
src/unfold/visuals/
├── theme.py          colors, sizes, and the manim settings
├── layout.py         regions, and the layout check
├── components.py     the five components and their parameter schemas
├── scene.py          the scene/v0 format, beat timing, and the manim scene
├── render.py         parallel renders, and contact sheets
└── command.py        unfold render
src/unfold/build/     gains the scene step
src/unfold/prompts/   gains scene.md
tests/visuals/
```

**Structure Decision**: `visuals` holds everything that draws. The scene step joins the build graph, because it is a model job like the others.

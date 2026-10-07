# Implementation Plan: Walking skeleton, by hand

**Branch**: `dev` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

## Summary

Write every M1 file by hand, so the formats come from real use rather than guesses. Two segments on k-NN get scripts, storyboards, and manim scenes. A small voice helper in the package turns each beat into audio with the macOS `say` command. It returns the audio's length, so each animation can last as long as its narration. The economics section gets a source manifest, a knowledge map, and an outline, with a test that its anchors resolve.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: manim 0.21, PyAV through manim, macOS `say`, and ffmpeg for joining segments

**Storage**: YAML and Markdown files. Private files live in `3B1B/content/`, and public examples in `examples/`.

**Testing**: pytest. The voice test skips on machines without `say`, such as Linux CI.

**Target Platform**: macOS for the voice. Rendering works on Linux too.

**Performance Goals**: each segment renders at low quality in under 5 minutes.

**Constraints**: no new dependencies, and no course material in the public repo.

## Constitution Check

| Principle | Check |
|---|---|
| I. Users bring their own model access | Passes. M1 makes no model calls. |
| II. Code keeps track | Not yet. M1 is by hand on purpose, and M4 adds the build graph. |
| III. Every claim has evidence | Passes. Each gate cites a file or a command. |
| IV. Evals come from real failures | Not yet. The retro collects the first failures. |
| V. Two source families | Passes. Every format gets a lecture example and a textbook example. |
| VI. Plain language | Passes. Scripts follow the spoken profile. |
| VII. Rights and privacy | Passes. CIS 5200 files stay private, and the economics source is CC BY 4.0. |
| VIII. The human decides | Changed for the overnight run. Claude writes the scenes, and the maintainer reviews in the morning. |
| IX. Safety | Passes. M1 adds no dependency, permission, or hook. |

## Project Structure

```text
unfold/
├── src/unfold/voice.py                     stand-in voice: text to audio, and its length
├── tests/test_voice.py
├── tests/test_examples.py                  anchors in the examples resolve
├── examples/econ-supply-demand/
│   ├── source.yaml                         manifest, license, and anchors
│   ├── knowledge-map.yaml
│   └── outline.yaml
├── docs/formats.md
└── docs/retros/M1.md

content/cis5200/episodes/E01-knn/           private
├── outline.yaml
├── s1-neighbours-vote/script.md, storyboard.yaml, scene.py
├── s2-choosing-k/script.md, storyboard.yaml, scene.py
└── render.sh                               renders both segments and joins them
```

## Complexity Tracking

None.

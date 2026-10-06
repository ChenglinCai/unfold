---
status: accepted
date: 2026-10-06
decision-makers: the maintainer
---

# Use Manim Community Edition 0.21 for animation

## Context and Problem Statement

unfold draws every visual with code, and agents write much of that code. Which animation engine should it use? The choice affects how reliably models write scenes, how we check layouts, and how we tie narration to animation.

## Considered Options

* Manim Community Edition 0.21, called ManimCE
* ManimGL, the engine that Grant Sanderson maintains for his own videos

## Decision Outcome

Chosen option: "ManimCE 0.21", because it has fuller documentation and works with manim-voiceover. We also expect models to write ManimCE more reliably, because more public code uses it. That expectation is a hypothesis, and M5 tests it.

### Consequences

* Good, because manim-voiceover ties each cue in a script to an animation.
* Good, because a larger community maintains ManimCE and its documentation.
* Bad, because ManimGL sometimes gets new features first.
* Neutral, because the version pins Python. ManimCE 0.21 needs Python 3.11 or later, and the Kokoro voice needs a version below 3.13. So we use Python 3.12.
* Neutral, because we use our own visual theme. We copy no code from the 3Blue1Brown repositories, because their license forbids commercial use.

## Revisit when

* ManimCE blocks a visual that the golden set needs.

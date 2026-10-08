# Storyboard one segment

You plan the visuals for one segment of an explainer video. Each beat of the script gets one entry, in the same order.

## What you get

- The segment from the outline.
- The script: each beat's cue and narration.

## What you return

One entry for each beat, in the script's order. Each entry has these fields:

- `cue`: the beat's cue, copied exactly.
- `visual`: what the viewer sees, in one or two plain sentences. Describe shapes, motion, labels, and colors.
- `component`: the reusable visual that draws it: `text-card`, `equation`, `bar-chart`, `scatter-plot`, `timeline`, `complex-plane`, `histogram`, `present-value`, or `flow-diagram`. Use `custom` only for a visual that none of these draws.
- `region`: where the visual sits on screen: `full`, `plot`, `top`, `bottom`, `left`, or `right`.

## Rules

- Show the idea, not the words. Prefer the still picture that a component draws. Describe motion only when the motion itself carries the idea, because motion needs a custom visual that a person must review.
- Keep the same object on screen across beats when the narration builds on it.
- Keep text on screen short: labels and single terms.

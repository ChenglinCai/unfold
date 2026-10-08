---
name: unfold
description: Turn learning material into explainer videos with unfold. Use it when someone wants a video series from a textbook, slides, a web page, a recording, or a bare topic.
---

# Make explainer videos with unfold

unfold turns learning material into a series of short explainer videos. Its tools check every step, so follow the steps in order and report what each check says.

## Steps

1. Run the `doctor` tool. Fix every failed check before you go on.
2. Ingest each source with `unfold ingest`, into a private folder outside any public repository.
3. Write `series.yaml` in a new series folder. Name the sources, describe the audience, and list in `knows` what the audience knows already.
4. Run the `build` tool. It runs model jobs on the user's own Claude subscription, so say so before you start.
5. Run the `render` tool with `check_audio` set to true.
6. Run the `evaluate` tool, then the `review` tool, and show the user the review page.

## Rules

- Keep sources and videos out of public repositories. A source's rights decide whether its videos may be public.
- Show the user every flagged beat. A flagged beat cites no anchor, so a person must check it.
- Show the user every failed check, and never hide one.

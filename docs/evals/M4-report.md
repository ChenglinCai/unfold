# Eval report: M4, text generation

This is the first eval report. It covers the plans, outlines, scripts, and storyboards that unfold wrote for the six golden series.

Claude read every output overnight on 2026-10-07, before writing any check. Principle IV prefers a domain expert for this step, so the maintainer should review the open notes in the private content folder.

## Method

- Each golden series uses one M2 source and builds one episode with two segments. That yields 6 plans, 6 outlines, 12 scripts, and 12 storyboards.
- The build made 42 model calls: 6 canaries and 36 generation jobs. Every job passed its checks on the first try.
- Claude wrote open notes on every output, then grouped the notes into 9 failure types. Seven types have a binary check, which passes or fails.
- Caveat: 36 outputs is a small sample. Current guides suggest 100 or more.

## Failure types and checks

| Failure type | Check | Unit | Passes | Rate |
|---|---|---|---|---|
| Over-planning | `plan-fits-source` | plan | 2 of 6 | 33% |
| The core topic arrives late | `first-episode-reaches-title` | plan | 2 of 6 | 33% |
| Plan boundaries ignored | `episode-stays-in-plan` | outline | 2 of 6 | 33% |
| Overlong narration | `narration-fits-target` | script | 8 of 12 | 67% |
| Thin grounding | `beats-are-grounded` | script | 10 of 12 | 83% |
| Source framing | `no-source-framing` | script | 11 of 12 | 92% |
| Custom-heavy storyboards | `storyboard-reuses-components` | storyboard | 8 of 12 | 67% |
| Paraphrase drift | none yet | beat | 1 case found | |
| An undefined field | none, because the format needs a fix | outline | 4 of 6 outlines | |

`uv run unfold eval ../content/series/*/` reproduces every rate in the table. `src/unfold/evals/__init__.py` defines each check in a few lines.

## What each failure looks like

These examples quote only sources that allow public outputs. The Wikipedia articles use CC BY-SA 4.0, and the spoken Wikipedia recording uses CC BY-SA 3.0.

- **Paraphrase drift.** A script for Euler's identity credits "a poll of mathematicians" in 1990, and adds "beating out every rival". The cited Wikipedia section says that a 1990 poll of readers of *The Mathematical Intelligencer* named it "the most beautiful theorem in mathematics". The beat cites the right anchor, so every code check passes.
- **Thin grounding.** A velocity-of-money script says that velocity "is shaped by habits, like how often people use cash versus cards, and how quickly banks move money around." The recording does tie velocity to "bank accounts and credit cards" at 2:32. The segment's anchors miss that block, so the beat cites nothing.
- **The core topic arrives late.** The plan for the central limit theorem opens with "What Does 'Random' Really Mean?". The theorem first appears in episode 5, so the one episode the build writes never reaches it.
- **Plan boundaries ignored.** Net present value's first episode asks why a dollar today is worth more than a dollar tomorrow. Its second segment still teaches the discount rate and present value, which the plan gives to episodes 2 and 3.

## Causes, and what to change

| Failure type | Likely cause | Change to try |
|---|---|---|
| Over-planning, and a late core topic | The plan prompt names a cap of 8 episodes, but not the source's size | Send the source's word count, ask for one episode per 500 words, and put the core topic in episode 1 or 2 |
| Plan boundaries ignored | The outline job sees the whole knowledge map | Send only the episode's concepts and the concepts of earlier episodes |
| Overlong narration | The prompt states a rate, not a number of words | Send each segment's word target as a number, and fail scripts more than 30 percent over |
| Thin grounding | A segment cites one or two anchors, and its script sees only those blocks | Add the anchors of every concept that the segment establishes |
| Custom-heavy storyboards | No component library exists yet | Start M5's components with the visuals that custom entries describe most |
| Paraphrase drift | Code cannot compare a claim with its source | Add a model check later, after these code checks, as principle III orders |
| An undefined field | `setups` in outline/v0 has no definition | Define `setups`, or remove it, in the next outline version |

## Cost

| Item | Amount |
|---|---|
| Model calls | 42, with no retries |
| Input tokens | 300,652 |
| Output tokens | 99,116 |
| Model time | about 18 minutes |
| A second build of all six series | 0 calls, in 0.7 seconds |

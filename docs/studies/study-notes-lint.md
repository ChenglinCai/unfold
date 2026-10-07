# Study notes and the written profile

This study checks the study notes from the M2 gate against the written profile of the Narration Standard. It reports numbers only, because notes from private sources stay private.

## Method

- Sources: the six golden sources of M2, after convergence added a finance article. One Sonnet job wrote each set of notes, with the prompt in `src/unfold/understand/prompt.md`.
- Command: `uv run unfold lint --format json ../content/sources/*/understand/study-notes.md`, with the findings counted per file and per rule.
- Words counts every token between spaces, including headings and citations.
- The linter now skips citations such as `[§p-3]`. Before that fix, citations pushed 4 more sentences over the limit.

## Results

| Source | Words | Errors | Warnings | Errors per 100 words |
|---|---|---|---|---|
| central-limit-theorem | 848 | 8 | 13 | 0.9 |
| cis5200-lecture-03 | 830 | 9 | 9 | 1.1 |
| mit-1805-class-10 | 928 | 5 | 19 | 0.5 |
| spoken-velocity-of-money | 822 | 4 | 8 | 0.5 |
| wikipedia-eulers-identity | 735 | 8 | 12 | 1.1 |
| wikipedia-net-present-value | 740 | 0 | 12 | 0.0 |

| Rule | Findings |
|---|---|
| N301 passive-voice | 36 |
| N202 parentheses | 35 |
| N101 sentence-length | 34 |
| N304 em-dash | 2 |

## Findings

- Every error is a long sentence. The prompt asks for at most 25 words, yet 34 sentences run longer. That is about one in every 144 words.
- The passive voice and parentheses cause most warnings, with 36 and 35 findings.
- The notes write formulas in words, such as "e raised to i times pi, plus 1, equals 0". Words suit narration. A hypothesis to test: learners read notation faster in notes.

## What to do next

- M4: run the linter inside the understand step, and send long sentences back as feedback. Measure how many extra tries that costs.
- M4: decide whether study notes may use notation for formulas.

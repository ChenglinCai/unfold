# Research: The Narration Standard linter

Each decision lists what we chose, why, and what else we considered.

## Sentence splitting

- Decision: a rule-based splitter in our own code. It ends sentences at `.`, `?`, and `!` before a space and a capital letter, or before the end of the text. It protects decimals, version numbers, initials, and a list of abbreviations such as "e.g." and "Dr.".
- Rationale: the text is our own docs and narration, which are short and regular. The splitter adds no dependency, and tests pin its edge cases.
- Alternatives: pysbd, NLTK's Punkt, and spaCy. Each adds a dependency, and the last two add large models.

## Breath groups

- Decision: a breath group is the run of words between two pauses, at a comma, semicolon, colon, or sentence end, as the glossary defines it.
- Rationale: punctuation is all a script has before it is spoken. The study measures how often punctuation falls at a real pause.
- Alternatives: count em dashes and parentheses as pauses too. The glossary's definition stays, and the AI-habits rule handles em dashes.

## Pause threshold for the study

- Decision: a gap of at least 0.25 seconds between two words counts as a pause. The study also reports 0.15 and 0.4 seconds, so its conclusion does not depend on one value.
- Rationale: Goldman-Eisler's 250-millisecond criterion is widely used, though researchers call it a convention rather than a gold standard. Source: https://pmc.ncbi.nlm.nih.gov/articles/11119743
- Alternatives: 0.2 seconds, which other studies use. It falls inside the range we report.

## Calibrating the spoken limit

- Decision: the spoken breath-group limit is the smallest whole number that keeps the 3Blue1Brown transcripts under 1 breath-group error per 1,000 words. The study reports the percentiles behind it.
- Rationale: the plan requires the linter to fire rarely on 3Blue1Brown. A limit read off the data avoids a number fitted to three transcripts.
- Alternatives: keep 20 words from the written profile. The study shows how often that limit would fire.

## AI writing habits

- Decision: a word list and a phrase list from Wikipedia's "Signs of AI writing", and a warning for each em dash. Source: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- Rationale: the page is public, maintained, and specific. Warnings never fail the command, so a false alarm costs little.
- Alternatives: a model that scores AI style. It would need model calls, which CI must not make.

## Passive voice

- Decision: a warning when a form of "be" comes before a past participle. A past participle is a word ending in "-ed", or one from a list of irregular forms, with an optional adverb in between.
- Rationale: the rule is a warning, so its misses and false alarms cost little. It needs no part-of-speech tagger.
- Alternatives: spaCy's dependency parse, which is more accurate but adds a large dependency.

## Command-line interface

- Decision: an `unfold` command built on `argparse`, with `lint` as its first subcommand.
- Rationale: it ships with Python, so the command adds no dependency.
- Alternatives: Click and Typer, which read better but add dependencies.

## CI

- Decision: two local pre-commit hooks. One lints Markdown docs with the written profile, and one lints `script.md` files with the spoken profile. CI already runs pre-commit on every pull request.
- Rationale: the same check runs before each commit and in CI, with no new workflow.
- Alternatives: a separate CI step, which would let local commits skip the check.

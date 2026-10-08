# Research: Chinese subtitles

Each entry records a decision, why we chose it, and what else we weighed. The maintainer is away, so Claude made these calls under principle VIII, and each waits for review at the gate.

## D1. Translate whole beats, then let code split them

- **Decision**: one model job per episode translates each beat whole. Code then splits each Chinese beat into cues.
- **Rationale**: English cues often break a sentence, and Chinese word order differs. A whole beat keeps the meaning intact. Code can then guarantee the line limits, so the model only has to keep each beat short enough.
- **Alternatives**: translating each English cue, which breaks sentences. Asking the model for finished cues, which moves the line limits into the model's hands.

## D2. How code splits a beat

- **Decision**: a cue holds at most 32 characters, in at most two lines of 16. Code breaks a beat into cues at spaces when it can, and into even pieces when it cannot. A two-line cue puts the shorter line on top, breaking at a space near the middle when one exists.
- **Rationale**: the style guide asks for two lines of 16 and a bottom-heavy shape. Spaces mark the pauses that replace commas and periods, so they make the best breaks.
- **Timing**: each cue's share of the beat's time follows its share of the characters, as the English cues follow their share of the words.

## D3. The reading budget

- **Decision**: a beat may hold at most 9 characters for each second of its spoken time, rounded down. Spaces do not count toward the budget.
- **Rationale**: the guide allows 9 characters per second for adult programs. Every cue in a beat then reads at the beat's own rate, because time follows characters.

## D4. The checks

- **Decision**: a reply fails when it misses a beat or adds one, or uses a comma or a period that is not a decimal point. It also fails on a full-width digit, or a beat with no Chinese character. Any run of four or more lowercase Latin letters fails, and so does a beat over its budget. Each error names its beat.
- **Rationale**: these are the guide's rules that code can decide. Capital acronyms such as NPV, and short variables such as x, still pass.
- **Alternatives**: a model that grades fluency, which principle IV allows only after it agrees with the maintainer's labels. The spec asks a person to read one episode instead.

## D5. One timing source for both languages

- **Decision**: `stitch.py` gains a function that reads each segment's parts from the rendered files. A pure function then lists every beat with its id, and its spoken start and end. Stitching and translation both use them.
- **Rationale**: Chinese cues then share their beats' times with the English cues. A regression check confirms that the golden English subtitles stay byte for byte the same.

## D6. Reuse the build graph's machinery

- **Decision**: the translate job is a `Job` that `run_job` runs, behind `Guarded`, which runs the canary first. Its record lives under the series' `records/` folder, and each call adds a line to `calls.jsonl`.
- **Rationale**: the job inherits saved-result reuse, retries with feedback, and the call log, all tested already. The key covers the request, which holds every beat's text and budget, so a changed narration or timing triggers a new translation.

## D7. Where the subtitles go

- **Decision**: `episode.zh.srt` sits beside `episode.srt`. The gallery copies it for public series, and the MCP server gains a translate tool.
- **Rationale**: video players find a sidecar file by its name, and the language code before `.srt` is the common convention.

## D8. A space at least every 16 characters

- **Decision**: added after the first golden round. A reply fails when a run of more than 16 characters has no space, and code packs whole phrases into lines.
- **Rationale**: Chinese has no spaces between words, so a long run had to break inside a word, such as 商品. Spaces already mark the guide's pauses, so they make the line breaks too.
- **Alternatives**: a word-segmentation library, which would add a dependency for one rule.

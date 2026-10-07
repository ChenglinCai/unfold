# Research: Text generation

Each decision lists what we chose, why, and what else we considered.

## Schemas

- Decision: one Pydantic 2 model per format. Each model exports JSON Schema, and the files live in `schemas/`, named such as `outline.v0.json`.
- Rationale: one definition serves three uses. Code validates files with it, jobs send its JSON Schema to the model, and readers browse the exported files. Pydantic uses the MIT license.
- Alternatives: hand-written JSON Schema with the jsonschema package, which keeps two definitions in step by hand. msgspec, which is fast but exports less complete schemas.

## Structured output

- Decision: each job passes its schema to `claude -p --json-schema`, and reads `structured_output` from the reply.
- Rationale: the model's reply then matches the schema, so retries go to meaning, not syntax. A test with Haiku and no tools worked with nested `$defs` and `$ref`, `pattern`, `enum`, `const`, and item limits.
- Alternatives: YAML parsed from free text, as M2 does, which fails on syntax more often. A fixed tool for the reply, which the runner does not offer with tools off.

## The build graph

- Decision: a small graph in Python. Each node has a key that hashes its prompt, its request, its model, and its JSON Schema. The request holds the input files' contents.
- Rationale: model output costs tokens, so reuse must follow content, not file times. The graph has five steps, which a short loop handles.
- Alternatives: doit, Snakemake, or Make, which decide by file times or need their own languages. Prefect or Dagster, which add servers.

## The canary

- Decision: before the first real job, a Haiku job answers "What is 2 plus 3?" through structured output, and the build checks for 5.
- Rationale: one cheap call proves the login, the usage limit, and structured output. A build with nothing to run skips it.
- Alternatives: `claude --version`, which proves neither the login nor the limit.

## The call log

- Decision: `calls.jsonl` in the series folder, with one JSON line per model call.
- Rationale: a line per call is easy to append, read, and count. The gate's budget of 60 calls needs that count.
- Alternatives: SQLite, which is harder to read by eye. OpenTelemetry, which needs a collector.

## Anchors in scripts

- Decision: script/v1 adds an `anchors` map to the front matter, from each cue to its anchor list.
- Rationale: the narration stays clean for the spoken profile, and each beat still lists its support, as principle V requires.
- Alternatives: markers inside the narration, which the voice would read. A second file, which could drift from the script.

## Context for each job

- Decision: a script job gets its segment from the outline, the knowledge map, and only the source blocks that the segment cites.
- Rationale: the whole source would cost more tokens and dilute the segment's focus.
- Alternatives: the whole source for every job, which multiplies input tokens by the number of segments.

## Limits for the gate

- Decision: by default, a build writes one episode with at most two segments.
- Rationale: six series then need about 36 generation calls, plus canaries and retries, under the budget of 60.
- Alternatives: whole series, which would need hundreds of calls before anyone has read one output.

## Error analysis

- Decision: read every output and write open notes, then group the notes into failure types. Researchers call that grouping axial coding. Then write a pass-or-fail check for each common type.
- Rationale: current practice puts error analysis before any eval, and prefers binary checks to rating scales. A check that always passes measures nothing, so pass rates near 70 percent show that a check has teeth. Sources: [Hamel Husain's evals FAQ](https://hamel.dev/blog/posts/evals-faq/) and [a 2026 practitioner's guide](https://tianpan.co/blog/2026-02-20-llm-evals-practitioners-guide).
- Alternatives: 1-to-5 scores, which principle IV forbids. A model judge first, which principle III orders after code checks.
- Caveat: the guides suggest 100 outputs or more, and the gate gives about 30. The report says so.

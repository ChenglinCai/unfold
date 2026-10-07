# Quickstart: validate the linter

## Prerequisites

`uv sync` in the repo. For the study, the 3Blue1Brown transcripts must sit in the private content folder at `content/corpus/3b1b-captions`. The download command is in `corpus/README.md`.

## Scenarios

1. Lint the repo's docs. Expected: exit code 0, and no errors.

   ```sh
   uv run unfold lint --profile written README.md CLAUDE.md docs specs
   ```

2. Lint the test sets. Expected: every AI-style paragraph has a finding, and the clean paragraphs have no errors.

   ```sh
   uv run pytest tests/lint -q
   ```

3. Lint a narration script with the spoken profile. Expected: no errors.

   ```sh
   uv run unfold lint --profile spoken examples/econ-supply-demand/s3-equilibrium/script.md
   ```

4. Fix mechanical findings. Expected: "e.g." becomes "for example", and nothing else changes.

   ```sh
   uv run unfold lint --fix --profile written some-file.md
   ```

5. Run the study on the private transcripts. Expected: `docs/studies/breath-groups.md` is rewritten with numbers only.

   ```sh
   uv run python corpus/breath_groups.py ../content/corpus/3b1b-captions
   ```

## Data contracts

See [contracts/cli.md](contracts/cli.md) for options, exit codes, output, and rule ids, and [data-model.md](data-model.md) for units, rules, and findings.

# unfold

unfold turns learning material into explainer videos. This file lists the commands, conventions, and rules for this repo.

## Commands

- Set up: `uv sync`, then `uv run pre-commit install`.
- Run every check: `uv run pre-commit run --all-files`.
- Run the tests: `uv run pytest`. Add `-m "not slow"` to skip the render tests.
- Render the test scene: `uv run manim -ql examples/hello.py Hello`.
- Add a package with `uv add <name>`. Never edit `uv.lock` by hand.

## Conventions

- Write the test first. Show its output as evidence that a change works.
- Keep each pull request under about 300 changed lines, not counting generated files.
- Docs, plans, and pull-request descriptions use plain English. Write one idea per sentence, with at most 25 words and in active voice. Define each term at first use, and use no arrows in prose.
- A hook in `.claude/hooks/` formats each Python file that Claude edits.

## Never

- Never commit PDFs, videos, audio, transcripts, or course material. They belong in the private content folder.
- Never call a language model from CI or from tests.
- Never copy code from the 3Blue1Brown repositories, because their license forbids commercial use.
- Never put "3Blue1Brown", "3B1B", or "STE" in a public name.

# Contributing to unfold

Thank you for helping. This guide covers how changes move through the repo, the rules every change keeps, and how to add a component.

## Start here

1. Follow the [quickstart](docs/quickstart.md) to render a segment on your machine.
2. Set up the checks from the [README](README.md), then run `uv run pre-commit install`.
3. Read the [constitution](.specify/memory/constitution.md), which every spec and pull request follows.
4. Use the terms in [the glossary](docs/glossary.md), with the meanings given there.

## How a change moves

- A change that one sentence can describe goes straight to a test and a pull request.
- A larger feature goes through [Spec Kit](https://github.com/github/spec-kit): a spec, a plan, and tasks under `specs/`, then the code.
- Write the test first, and show that it fails before the code that makes it pass.
- Keep each pull request near 300 changed lines, not counting generated files.
- Open a draft pull request with your first commit. CI runs only on pull requests, and it checks Linux, whose fonts run wider than macOS fonts.

## Rules that every change keeps

- Never commit PDFs, videos, audio, transcripts, or course material. Keep them in a private folder outside the repo.
- Never call a language model from CI or from a test. Model jobs run only on each user's own access.
- Never copy code from the 3Blue1Brown repositories, because their license forbids commercial use.
- Docs and pull-request descriptions follow the written profile of the Narration Standard. `uv run unfold lint` checks it, and pre-commit runs it on every commit.
- State the safety implications of a change to dependencies, permissions, hooks, or public content. Say what it allows, what could go wrong, and how to undo it.

## Add a component

A component is a tested, reusable animation, and a domain pack is a set of components for one subject. Add one when a custom visual recurs a third time in the golden set. `uv run unfold eval` reports the custom share.

1. Write the parameter model in `src/unfold/visuals/params.py`. That file never imports manim.
2. Add the model to `Visual` and its name to `NAMES` in the same file.
3. Write tests in `tests/visuals/` for rejected parameters, the drawing, and a slow render.
4. Add a sample to `tests/visuals/test_components.py`, which checks it in every region.
5. Add a random-parameter strategy to `tests/visuals/test_pack_props.py`.
6. Write the drawing in `src/unfold/visuals/components.py`, and give parts names that tests can find.
7. Keep labels apart with `Row` or `_keep_apart`, and print plain text, never TeX.
8. Describe the component in `src/unfold/prompts/scene.md`, where a test looks for its name.
9. If the model supplies numbers, extend `chart_values` in `src/unfold/evals/__init__.py`.
10. Raise `VERSION` in `params.py`, then run `uv run python -m unfold.formats.export`.
11. Render a sample, read its contact sheet, and draw it once with a wide font.

`specs/008-domain-packs/` shows four components built this way, from the spec to the eval report.

## Report a bug or suggest an idea

Use the issue forms. For a bug, include the output of `uv run unfold doctor`, so we can see your machine.

# Implementation Plan: Natural voice

**Branch**: `claude/local-folder-cloud-access-jlus4i` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

## Summary

A new module, `unfold.kokoro`, fills the existing `Voice` interface with Kokoro. It downloads and checks the model, turns text into phonemes with misaki, speaks each beat, then trims and levels the clip. `default_voice()` reads `UNFOLD_VOICE` and prefers Kokoro when the extra is installed. [research.md](research.md) records each design call.

## Technical Context

**Language/Version**: Python 3.12, in the existing unfold package.

**Primary Dependencies**: a new `voice` extra with kokoro-onnx, misaki, num2words, spaCy, and spaCy's small English model. They bring ONNX Runtime, phonemizer, and espeakng-loader.

**Storage**: the model files live in the user's cache folder. Clips stay in each series' `.voice-cache` folder.

**Testing**: pytest, test first. A fake engine and a fake download stand in for Kokoro, so no test downloads a model.

**Target Platform**: macOS and Linux.

**Constraints**: no PyTorch, no model call in tests, and a pull request near 300 changed lines, not counting the lock file.

## Constitution Check

| Principle | Result |
|---|---|
| I. Own model access | Passes. The voice runs on the user's machine, and tests use fakes. |
| II. Code keeps track | Passes. The voice name, with model version and speed, goes into the render key. |
| III. Evidence | Passes. Tests come first. Samples in six voices go to the maintainer for listening. |
| IV. Evals from failures | Passes. The Whisper audio check measures intelligibility on the maintainer's machine. |
| V. Two families | Passes. The voice reads narration from every source family alike. |
| VI. Plain language | Passes. Docs use the written profile. |
| VII. Rights | Passes. The weights use Apache-2.0. espeak-ng comes from PyPI, so unfold never redistributes it. |
| VIII. The human decides | Passes. The maintainer chose Kokoro, and picks the default voice by ear. |
| IX. Safety | Passes, with notes. The extra downloads code and a 350 MB model. A pinned hash guards each download, and `docs/dependencies.md` says how to remove each one. |

## Project Structure

```text
src/unfold/kokoro.py            model download, G2P, speech, trimming, and leveling
src/unfold/voice.py             UNFOLD_VOICE, and Kokoro first in default_voice()
src/unfold/doctor.py            the voice finding
pyproject.toml, uv.lock         the voice extra
plugin/.claude-plugin/plugin.json   the voice extra for plugin users
tests/test_kokoro.py            fakes for the engine and the download
docs/dependencies.md, docs/quickstart.md, docs/decisions/0007   the new packages and setup
```

## Delivery order

1. Trimming and leveling, as pure functions.
2. The checked download.
3. The Kokoro voice with a fake engine, then the voice setting.
4. The extra, the doctor finding, the plugin, and the docs.
5. A real render of the bundled example on Linux.

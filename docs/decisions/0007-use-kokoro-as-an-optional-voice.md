---
status: accepted
date: 2026-10-14
decision-makers: the maintainer, on Claude's recommendation
---

# Use Kokoro as an optional voice, with espeak-ng installed from PyPI

## Context and Problem Statement

M6 needs a voice that runs on macOS and Linux. Kokoro is the plan's default voice. For words outside its dictionary, it can fall back to espeak-ng through phonemizer, and both use the GPL. unfold uses the MIT license, so it must not ship GPL code inside its own package. Until now, unfold has used the macOS `say` command, which limits voiced renders to Macs.

## Considered Options

* Kokoro as an optional extra, with espeak-ng installed from PyPI
* The macOS `say` command only
* Kokoro with no espeak-ng fallback

## Decision Outcome

Chosen option: "Kokoro as an optional extra", because voiced renders then work on Linux too, and unfold never redistributes GPL code. The `voice` extra installs espeakng-loader from PyPI, and that package bundles espeak-ng. So the user's installer fetches the GPL code, as it does for PyAV in item 9 of `docs/progress.md`. The maintainer chose it on 2026-10-14. `specs/011-natural-voice/` holds the design.

### Consequences

* Good, because voiced renders no longer need a Mac.
* Good, because the voice interface from M6 already lets Kokoro replace `say` with no change to scenes.
* Bad, because the extra and its model add about 730 MB, and the first render waits for the download.
* Bad, because a packaged app that bundles espeak-ng would need a license review first, as item 9 says for FFmpeg.

## Revisit when

* Kokoro drops its espeak-ng fallback, or a permissive fallback appears.
* Someone builds a packaged app that bundles the voice.

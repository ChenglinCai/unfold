# Implementation Plan: ElevenLabs voice

**Branch**: `claude/local-folder-cloud-access-jlus4i` | **Date**: 2026-10-14 | **Spec**: [spec.md](spec.md)

## Summary

A new module, `unfold.elevenlabs`, fills the `Voice` interface with ElevenLabs' text-to-speech endpoint. Every voice now takes the text before and after its beat, and only ElevenLabs uses it. Clips reuse the trimming and leveling from `unfold.kokoro`. [research.md](research.md) records each design call.

## Technical Context

**Language/Version**: Python 3.12. **Dependencies**: none new, because `urllib` sends the requests.

**Testing**: pytest, test first. A fake transport stands in for ElevenLabs, and a guard in `tests/conftest.py` refuses any real request.

## Constitution Check

| Principle | Result |
|---|---|
| I. Own model access | Passes. Each user pays with their own key, and tests never reach ElevenLabs. |
| II. Code keeps track | Passes. The clip name covers every input that changes the sound. |
| III. Evidence | Partial. Tests use a fake server. A live check waits for the key and network access. |
| VII. Rights | Deviation, recorded. Narration from private sources leaves the machine. The maintainer chose this, and the docs say so. |
| VIII. The human decides | Passes. The maintainer asked for ElevenLabs. |
| IX. Safety | Passes, with notes. ElevenLabs runs only when the setting names it. The key stays in the environment. Unset the setting to undo it. |

The scope's non-goal of "model providers other than Anthropic" covers language models. A voice service is not one, so the feature keeps to the scope.

## Project Structure

```text
src/unfold/elevenlabs.py     the request, the clip, and the setting
src/unfold/voice.py          before and after for every voice, and the elevenlabs setting
src/unfold/kokoro.py         accepts before and after
src/unfold/visuals/render.py passes each beat's neighbors
src/unfold/doctor.py         reports ElevenLabs
tests/test_elevenlabs.py     a fake transport
docs/decisions/0008          why, and what it costs
```

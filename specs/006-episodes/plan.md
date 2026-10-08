# Implementation Plan: Episodes

**Branch**: `m6` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

## Summary

The voice module gains an interface, and `say` stays its only voice for now. Segments render with their clips, and each beat lasts as long as its clip. Whisper checks each segment's audio against its script. ffmpeg stitches each episode, with a title card before each segment. A ledger records what each episode teaches, the next outline sees it, and an idea-link check proves that every needed idea was taught or known.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: manim, which mixes each clip into the video. faster-whisper from the `audio` extra, for the audio check. The ffmpeg program, which Homebrew installs, for stitching. No new Python dependency.

**Storage**: files: `segment.srt` beside each segment, and `episode.mp4` with `episode.srt` in each episode folder. `ledger.yaml` sits in the series folder.

**Testing**: pytest. Voice and Whisper tests are slow, and skip without `say` or the audio extra.

**Constraints**: the voice needs macOS until the maintainer chooses another.

## Constitution Check

| Principle | Result |
|---|---|
| I. Own model access | Passes. No new model step. Episode 2 reuses the existing steps. |
| II. Code keeps track | Passes. Code writes the ledger and checks the links. |
| III. Evidence | Passes. The audio check and the idea-link check give evidence. |
| VII. Rights | Passes. Episodes stay in the private content folder. |
| IX. Safety | Passes. ffmpeg runs only on our own files. |

## Project Structure

```text
src/unfold/voice.py              gains the Voice interface
src/unfold/visuals/scene.py      times beats by their clips, and adds the sound
src/unfold/visuals/render.py     voices each segment, and writes its subtitles
src/unfold/episodes/
├── subtitles.py                 SRT cues from beats and clip times
├── audio.py                     the Whisper check and the word error rate
├── stitch.py                    title cards, and ffmpeg concatenation
├── ledger.py                    ledger/v0, written after each episode
└── links.py                     the idea-link check
```

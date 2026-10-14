# Feature Specification: Natural voice

**Feature Branch**: `claude/local-folder-cloud-access-jlus4i`

**Created**: 2026-10-14

**Status**: Draft

**Input**: decision record 0007, from `/speckit-specify`. Replace the macOS `say` voice with Kokoro, an open voice model, on macOS and Linux. The maintainer asked that the voice sound natural above all.

## Background

A voice turns each beat's narration into a clip. A beat is one short piece of narration and its visual. The render times each animation to its clip, and adds a short pause between beats.

Today the only voice is the macOS `say` command. It sounds robotic, and Linux renders come out silent. Kokoro is a voice model with 82 million parameters, released under Apache-2.0. Its American voice `af_heart` ranks highest among its voices.

Kokoro reads phonemes, the sounds of speech. A G2P step turns text into phonemes. Misaki, Kokoro's own G2P, tags each word's part of speech, so "read" in the past tense sounds like "red".

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hear a natural voice (Priority: P1)

A maintainer renders a segment, and the narration sounds like a person explaining an idea.

**Why this priority**: viewers leave a video whose voice grates, however good its pictures are.

**Independent Test**: render the bundled example with the voice, and listen to it.

**Acceptance Scenarios**:

1. **Given** the voice extra, **When** a segment renders, **Then** each beat speaks in the chosen Kokoro voice.
2. **Given** a past-tense "read", **When** it speaks, **Then** it sounds like "red".
3. **Given** beats in several voices, **When** they play in turn, **Then** each one plays at the same loudness.

---

### User Story 2 - Render with a voice on Linux (Priority: P1)

A maintainer on Linux renders a segment with sound.

**Why this priority**: a cloud session or a Linux laptop can then make finished videos.

**Independent Test**: on Linux, render the bundled example, and check that the video has audio.

**Acceptance Scenarios**:

1. **Given** Linux and the voice extra, **When** a segment renders, **Then** its video has narration.
2. **Given** no voice extra on macOS, **When** a segment renders, **Then** it falls back to `say`, as before.

---

### User Story 3 - Choose the voice (Priority: P2)

A maintainer picks another Kokoro voice, or the speed, for a render.

**Why this priority**: one voice will not suit every subject or audience.

**Independent Test**: set a voice, render, and read the voice name in the timing file.

**Acceptance Scenarios**:

1. **Given** a voice name in the setting, **When** a segment renders, **Then** it uses that voice.
2. **Given** an unknown voice name, **When** a segment renders, **Then** it stops and lists the voices.

---

### User Story 4 - Trust the downloads (Priority: P1)

The voice model downloads once, and unfold checks it before use.

**Why this priority**: the model runs on the maintainer's machine, so a swapped file must never load.

**Independent Test**: point the download at a file with the wrong checksum.

**Acceptance Scenarios**:

1. **Given** no model on disk, **When** the voice first speaks, **Then** it downloads the model and checks its SHA-256.
2. **Given** a download with a wrong checksum, **When** checked, **Then** it deletes the file and stops.

### Edge Cases

- A beat longer than one Kokoro call splits at punctuation, never inside a word.
- Silence at the start and end of a clip is trimmed, so pauses between beats stay even.
- A loud voice must not clip after leveling.
- The same text in the same voice is never spoken twice, because clips are saved.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An optional `voice` extra MUST install Kokoro's runtime and misaki, with no PyTorch.
- **FR-002**: With the extra, the default voice MUST be Kokoro `af_heart` at speed 1.0. Without it, macOS falls back to `say`, and Linux renders silent.
- **FR-003**: A setting MUST choose the voice and the speed, and an unknown voice MUST stop with the list of voices.
- **FR-004**: Text MUST pass through misaki's G2P. British voices use its British G2P.
- **FR-005**: Each clip MUST lose its edge silence, and reach one loudness with peaks below full scale.
- **FR-006**: The model files MUST download once into a user cache, and pass a pinned SHA-256 check before use.
- **FR-007**: The voice name MUST include the model version, voice, and speed, so a change rerenders each segment.
- **FR-008**: `unfold doctor` MUST report the voice that renders will use.
- **FR-009**: No test may download a model or call a language model.

### Key Entities

- **Kokoro voice**: a model version, a voice name, and a speed.
- **Clip**: a WAV file and its length in seconds.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The maintainer listens to sample beats in six voices, and picks a default that sounds natural.
- **SC-002**: Every clip lands within 1 dB of the target loudness, and no sample clips.
- **SC-003**: The bundled example renders with narration on Linux.
- **SC-004**: Whisper transcribes Kokoro narration of the golden set with a word error rate under 5 percent, on the maintainer's machine.

## Assumptions

- The model files come from the kokoro-onnx project's GitHub release, because they match Kokoro's own weights in a format that needs no PyTorch.
- The extra installs espeak-ng from PyPI, inside espeakng-loader, for words that misaki does not know. espeak-ng uses the GPL, and unfold never redistributes it.
- English narration only, as the constitution's scope says.
- Out of scope: voice cloning, custom pronunciation lists, and voices for other languages.

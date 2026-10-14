# Feature Specification: ElevenLabs voice

**Feature Branch**: `claude/local-folder-cloud-access-jlus4i`

**Created**: 2026-10-14

**Status**: Draft

**Input**: the maintainer listened to six Kokoro voices, and found none of them good enough. They asked for ElevenLabs, a paid voice service.

## Background

A voice turns each beat's narration into a clip. A beat is one short piece of narration and its visual. Kokoro, the free voice, runs on the user's machine. ElevenLabs runs on its own servers, and each user pays for it with their own API key.

ElevenLabs speaks a beat more naturally when it knows the text before and after it. This is called request stitching, and it keeps the intonation flowing from beat to beat.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Narrate with ElevenLabs (Priority: P1)

A maintainer sets an ElevenLabs key and voice, renders a segment, and hears ElevenLabs narration.

**Why this priority**: the maintainer found the free voices too robotic for viewers.

**Independent Test**: render with a fake ElevenLabs server, and read the requests and the clips.

**Acceptance Scenarios**:

1. **Given** a key and the setting, **When** a segment renders, **Then** each beat speaks in the chosen voice.
2. **Given** three beats, **When** they render, **Then** each request carries the text before and after its beat.
3. **Given** a rendered segment, **When** it renders again, **Then** it sends no request.

---

### User Story 2 - Spend money only on purpose (Priority: P1)

ElevenLabs runs only when the maintainer asks for it, and tests never reach it.

**Why this priority**: each request costs money and sends narration to another company.

**Independent Test**: set a key with no voice setting, and check that the render uses the free voice.

**Acceptance Scenarios**:

1. **Given** a key and no setting, **When** a segment renders, **Then** it uses Kokoro or `say`, not ElevenLabs.
2. **Given** the setting and no key, **When** a segment renders, **Then** it stops and names the missing key.
3. **Given** any test, **When** it runs, **Then** it cannot reach ElevenLabs.

### Edge Cases

- A refused request, such as a bad key or an empty balance, stops the render with ElevenLabs' own message, and never shows the key.
- A clip from ElevenLabs gets the same trimming and leveling as a Kokoro clip.
- The text before and after a beat changes its sound, so it belongs in the clip's saved name.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `UNFOLD_VOICE=elevenlabs:VOICE@MODEL` MUST choose ElevenLabs. The voice and the model are optional.
- **FR-002**: The key MUST come from `ELEVENLABS_API_KEY`, and no file or message may contain it.
- **FR-003**: Each request MUST carry the narration before and after its beat, within the same segment.
- **FR-004**: Clips MUST be saved by voice, model, settings, text, and neighbors, so unchanged beats cost nothing.
- **FR-005**: Each clip MUST get the trimming and leveling of feature 011.
- **FR-006**: `unfold doctor` MUST report ElevenLabs when the setting chooses it, and warn when its key is missing.
- **FR-007**: No test may reach ElevenLabs.
- **FR-008**: The docs MUST say that narration goes to ElevenLabs, and what that costs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The maintainer listens to the bundled example in ElevenLabs, and finds it natural.
- **SC-002**: A second render of an unchanged segment sends no request.
- **SC-003**: Whisper hears each golden segment with under 5 percent word errors.

## Assumptions

- The maintainer has an ElevenLabs plan, and their plan's terms allow the use they intend.
- The default model is `eleven_multilingual_v2`, which ElevenLabs recommends for long narration and which supports request stitching.
- No SDK is needed. One HTTPS request per beat uses Python's standard library.
- Narration comes from private course material. Sending it to ElevenLabs is the maintainer's choice, and the docs say so.
- Kokoro stays the free default.

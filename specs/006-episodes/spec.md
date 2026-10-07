# Feature Specification: Episodes

**Feature Branch**: `m6`

**Created**: 2026-10-07

**Status**: Draft

**Input**: Plan milestone M6. Add the voice, the audio check, transitions, stitching, subtitles, and ledger updates. Make two consecutive episodes from one series, with callbacks, and one episode from a second source family. Done when all three episodes play correctly, and the idea-link check passes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Hear each segment, timed to its voice (Priority: P1)

Each beat gets a voice clip, and the beat lasts as long as its clip. A segment renders with its narration, and an audio check compares what Whisper hears with the script.

**Why this priority**: a video without a voice is not an episode, and a garbled voice must fail before anyone watches it.

**Independent Test**: render a short segment with a voice, then transcribe it and compare.

**Acceptance Scenarios**:

1. **Given** a scene and its script, **When** the segment renders, **Then** each beat lasts as long as its voice clip.
2. **Given** a rendered segment, **When** the audio check runs, **Then** it reports the word error rate against the script.
3. **Given** a word error rate above 15 percent, **When** the check runs, **Then** the segment fails it.

---

### User Story 2 - Stitch episodes with subtitles (Priority: P1)

`unfold render` stitches an episode's segments into one video, with a title card between segments, and writes subtitles for the whole episode.

**Why this priority**: viewers watch episodes, not segments.

**Independent Test**: stitch two short segments, and check the length and the subtitle times.

**Acceptance Scenarios**:

1. **Given** rendered segments, **When** the episode stitches, **Then** one video holds them in order.
2. **Given** an episode, **When** its subtitles are written, **Then** each beat has a cue that starts when its narration starts.

---

### User Story 3 - Link ideas across episodes (Priority: P1)

A ledger records what each episode teaches. The next episode's outline sees the ledger, so it can call back to earlier visuals. The idea-link check proves that every idea a segment needs comes from an earlier segment, an earlier episode, or what the audience already knows.

**Why this priority**: a series must build, and a check must catch a segment that needs an idea no one taught.

**Independent Test**: run the check on outlines with a missing idea, and on outlines where every idea links.

**Acceptance Scenarios**:

1. **Given** a finished episode, **When** the build ends, **Then** the ledger lists what the episode established.
2. **Given** a segment that needs an untaught idea, **When** the check runs, **Then** it names the idea and the segment.
3. **Given** episode 2, **When** the outline step runs, **Then** it may call back to a visual from episode 1.

### Edge Cases

- `say` is missing, as on Linux. The render reports that the voice needs macOS, until another voice exists.
- The audio extra is missing. The audio check reports that it was skipped.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A voice interface MUST turn one beat's text into a clip and its length. The first voice MUST be the macOS `say` command.
- **FR-002**: Each beat MUST last as long as its clip, plus a short pause.
- **FR-003**: The audio check MUST compute the word error rate of each segment, and MUST fail a rate above 15 percent.
- **FR-004**: `unfold render` MUST stitch each episode into one video, with a title card before each segment.
- **FR-005**: Subtitles MUST cover every beat, with times from the clips.
- **FR-006**: A ledger MUST record, for each episode, what it establishes.
- **FR-007**: The outline step MUST see the ledger of earlier episodes.
- **FR-008**: The idea-link check MUST accept a required idea only when an earlier segment, an earlier episode, or the series' `knows` list supplies it.

### Key Entities

- **Voice**: what turns text into a clip.
- **Clip**: one beat's audio, and its length.
- **Ledger**: what each episode of a series established.
- **Episode video** and **subtitles**: the stitched result.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Three episodes play: two consecutive ones from one series, and one from a second source family.
- **SC-002**: Every segment of those episodes passes the audio check.
- **SC-003**: Every outline of those episodes passes the idea-link check.
- **SC-004**: Episode 2 calls back to a visual from episode 1.

## Assumptions

- The voice is macOS `say` until the maintainer answers progress item 18 about Kokoro.
- The two consecutive episodes come from net-present-value, which uses a web source. The third comes from velocity-of-money, a recording.
- Renders stay at low quality for review.

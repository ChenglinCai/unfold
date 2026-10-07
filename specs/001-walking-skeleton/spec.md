# Feature Specification: Walking skeleton, by hand

**Feature Branch**: `dev`, for the overnight run in decision record 0006

**Created**: 2026-10-06

**Status**: Draft

**Input**: Plan milestone M1. Make a 2-minute CIS 5200 episode about k-NN, in two segments. Write the knowledge map and outline for the economics source by hand, without rendering. Done when the video plays, `docs/formats.md` describes the formats, and a retro lists what was hard.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Watch a first episode (Priority: P1)

The maintainer plays a video of about two minutes on k-nearest neighbors, in two segments. Narration plays in step with the animation.

**Why this priority**: it proves the whole path from source to video before anything is automated. A path this thin is called a tracer bullet.

**Independent Test**: play the episode file in the content folder. It has two segments, a voice, and no silent gap.

**Acceptance Scenarios**:

1. **Given** an outline, two scripts, and two storyboards, **When** the maintainer runs the render command, **Then** each segment renders to a video with sound.
2. **Given** both segment videos, **When** the join command runs, **Then** one episode file plays from start to end.
3. **Given** a script, **When** its beat starts, **Then** the matching animation starts within half a second.

### User Story 2 - The formats fit a different source (Priority: P2)

The same formats hold a knowledge map and an outline for an economics textbook section, written by hand.

**Why this priority**: a format designed from one source fits only that source. The constitution requires two source families.

**Independent Test**: both economics files load as YAML. Every anchor in them names a heading or table in the source.

**Acceptance Scenarios**:

1. **Given** the economics source manifest, **When** the anchor test runs, **Then** every anchor resolves.

### User Story 3 - The formats are written down (Priority: P2)

`docs/formats.md` describes each file format, with its fields and two examples.

**Independent Test**: each format in the document links to one CIS 5200 example and one economics example.

### User Story 4 - Lessons for automation (Priority: P3)

A retro in `docs/retros/M1.md` lists what was hard, and which steps later milestones should automate first.

### Edge Cases

- A beat's narration runs longer than its animation. The scene then waits for the audio to end.
- An idea has no figure in the source. Its storyboard entry marks the visual as custom.
- A claim has no anchor. The knowledge map flags it for review.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The episode files MUST follow `docs/formats.md`.
- **FR-002**: The CIS 5200 outline, scripts, storyboards, scenes, audio, and video MUST stay in the private content folder.
- **FR-003**: The economics example MUST live in `examples/`, with the attribution that its CC BY 4.0 license requires.
- **FR-004**: Each beat in a script MUST have a cue, and each cue MUST have a storyboard entry.
- **FR-005**: Narration MUST follow the spoken profile: breath groups of at most 20 words, no parentheses, no abbreviations, and math in words.
- **FR-006**: The voice MUST use the macOS `say` command as a stand-in, so M1 adds no dependency.
- **FR-007**: A test MUST check that every economics anchor resolves.

### Key Entities

- **Source manifest**: where a source came from, its license, and its anchors.
- **Knowledge map**: concepts, prerequisites, claims, and gaps, each tied to anchors.
- **Outline**: the segments of one episode, with what each requires and establishes.
- **Script**: the narration of one segment, split into beats, each with a cue.
- **Storyboard**: one visual event for each cue.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The episode lasts between 90 and 150 seconds.
- **SC-002**: Each segment renders at low quality in under 5 minutes on the maintainer's Mac.
- **SC-003**: The economics knowledge map holds at least 10 concepts, and each has an anchor.
- **SC-004**: `docs/formats.md` gives two examples for each format, one from each source.

## Assumptions

- The macOS voice is good enough as a stand-in. M6 replaces it with Kokoro.
- The maintainer is asleep, so Claude writes the scenes, which the plan reserved for the maintainer.
- Out of scope: schemas and automation, which come in M4, layout checks, which come in M5, and the final voice, which comes in M6.

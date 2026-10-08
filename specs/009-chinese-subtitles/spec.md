# Feature Specification: Chinese subtitles

**Feature Branch**: `m8-subtitles`

**Created**: 2026-10-08

**Status**: Draft

**Input**: M8's second feature, from `/speckit-specify`. Write Simplified Chinese subtitles for each rendered episode, in the style that Netflix asks of its subtitlers.

## Background

Each stitched episode already has English subtitles in `episode.srt`. A beat is one short piece of narration and its visual, and the English subtitles split each beat into cues. A cue is one subtitle on screen, with a start and an end. English cues often break a sentence in two, so a cue is the wrong unit to translate. A beat keeps its sentences whole.

Netflix's [Simplified Chinese style guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215986007-Chinese-Simplified-Timed-Text-Style-Guide) sets these rules for adult programs:

- At most two lines in a cue, and at most 16 characters in a line.
- At most 9 characters per second.
- No commas or periods. A single space takes their place.
- Half-width digits, such as 1, 2, and 3.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Translate an episode's subtitles (Priority: P1)

A maintainer runs one command, and every rendered episode in a series gains Chinese subtitles beside its English ones.

**Why this priority**: Chinese viewers can then follow the episodes, and the plan names Chinese subtitles for M8.

**Independent Test**: translate a small rendered episode with a fake translator, then read the subtitle file.

**Acceptance Scenarios**:

1. **Given** a rendered episode, **When** the command runs, **Then** each beat gets Chinese cues inside its own time.
2. **Given** an unchanged episode, **When** the command runs again, **Then** it reuses the saved translation and calls no model.

---

### User Story 2 - Follow the style guide (Priority: P1)

Every Chinese cue follows the style guide, so the subtitles read the way Chinese viewers expect.

**Why this priority**: viewers cannot read subtitles that run too long or too fast.

**Independent Test**: split long beats into cues, and run the checks on replies that break each rule.

**Acceptance Scenarios**:

1. **Given** a beat of 40 characters, **When** code splits it, **Then** no cue has more than two lines of 16.
2. **Given** a reply with a comma, **When** the check runs, **Then** it fails and names the beat.
3. **Given** a beat over its reading budget, **When** the check runs, **Then** it fails and states the budget.
4. **Given** a reply that keeps an English word, **When** the check runs, **Then** it fails and names the word.

---

### User Story 3 - Share the subtitles (Priority: P2)

The gallery and Claude Code both reach the Chinese subtitles.

**Why this priority**: a public episode should carry its Chinese subtitles wherever it goes.

**Independent Test**: build a gallery from a public series with Chinese subtitles, and list the server's tools.

**Acceptance Scenarios**:

1. **Given** a public series with Chinese subtitles, **When** the gallery builds, **Then** it copies them beside the video.
2. **Given** the server, **When** a client lists its tools, **Then** it sees a translate tool.

---

### User Story 4 - Translate the golden set (Priority: P1)

The seven golden episodes gain Chinese subtitles that pass every check.

**Why this priority**: the golden set shows whether the checks and the prompt work on real narration.

**Independent Test**: translate the golden set, then run every check on every cue.

**Acceptance Scenarios**:

1. **Given** the seven rendered golden episodes, **When** translation runs, **Then** each one gets subtitles that pass every check.

### Edge Cases

- An episode with no render yet gets a note, and the command moves on.
- A decimal point between digits, such as 3.5, is not a period.
- Full-width question marks and exclamation marks stay, because the guide allows them.
- Capital acronyms, such as NPV, and one-letter variables, such as x, are not untranslated words.
- A reply that misses a beat, or adds one, fails and names each beat.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `unfold translate SERIES --to zh` MUST write `episode.zh.srt` beside each rendered episode, and skip unrendered ones with a note.
- **FR-002**: One model job per episode MUST translate every beat's narration, with one translation for each beat.
- **FR-003**: Code MUST split each translated beat into cues of at most two lines of 16 characters. Each cue's time inside the beat follows its share of characters.
- **FR-004**: A check MUST reject a missing or extra beat, a comma, a period that is not a decimal point, and a full-width digit.
- **FR-005**: A check MUST reject an untranslated English word, and a beat over its reading budget of 9 characters per second.
- **FR-006**: A failed check MUST retry with its errors as feedback, at most 3 times, and then report the episode as failed.
- **FR-007**: The command MUST reuse a saved translation when the narration, timing, prompt, model, and reply schema are all unchanged.
- **FR-008**: A passing canary MUST come before the first model call of a run. Every model call MUST add a line to the series' call log.
- **FR-009**: The gallery MUST copy `episode.zh.srt` for each public series that has one.
- **FR-010**: The MCP server MUST offer a translate tool.
- **FR-011**: No test may call a language model.

### Key Entities

- **Translated beat**: a beat's id, made of its segment and its cue name, and its Chinese text.
- **Reading budget**: the most characters a beat may hold. It is 9 times the beat's spoken seconds, rounded down.
- **Chinese cue**: a start, an end, and one or two lines.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All seven golden episodes have Chinese subtitles, and every cue passes every check.
- **SC-002**: A second run over the golden set makes no model call.
- **SC-003**: Every cue shows at most two lines of 16 characters, at no more than 9 characters per second.
- **SC-004**: A reader of Chinese finds every beat of one public episode accurate, and records each fix it needs.

## Assumptions

- The audience reads Simplified Chinese, and the episodes are adult programs, so the limit is 9 characters per second.
- A beat's spoken time runs from its start to its end, less the pause after it. The English subtitles use the same time.
- Every character counts as one, including digits and letters. Spaces count toward a line's length, but not toward reading speed.
- An untranslated word is a run of four or more lowercase Latin letters. Capital acronyms and short variables pass.
- Translation uses the series' model, on the maintainer's own access. The golden set needs about 8 model calls, plus retries.
- The maintainer is away and asked Claude to keep going. So Claude makes the design calls that principle VIII leaves to the maintainer, and records them for the gate.
- Out of scope: Chinese narration, subtitles burned into the video, and other languages.

# Feature Specification: The Narration Standard linter

**Feature Branch**: `dev`, for the overnight run in decision record 0006

**Created**: 2026-10-07

**Status**: Draft

**Input**: Plan milestone M3. Build `unfold lint` with written, spoken, and strict profiles. Test the breath-group hypothesis on at least 50 3Blue1Brown transcripts, calibrate the spoken limits on them, and check that the linter flags AI writing habits.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lint a doc against the written profile (Priority: P1)

A contributor runs `unfold lint` on a plan, doc, or pull-request description. Each problem appears with its rule, file, line, and the words involved. The command fails only when a rule of severity "error" fires.

**Why this priority**: every plan and doc in this repo must follow the written profile, and today a scratch script checks it by hand.

**Independent Test**: lint a file with a 30-word sentence and an arrow in prose. Both appear as errors, and the command exits with a failure.

**Acceptance Scenarios**:

1. **Given** a doc whose sentences all have 25 words or fewer, **When** it is linted, **Then** no sentence-length error appears.
2. **Given** a sentence of 26 words, **When** it is linted with the written profile, **Then** one error names that sentence and its length.
3. **Given** a numbered step of 21 words, **When** it is linted, **Then** one error says that procedure steps allow 20 words.
4. **Given** a paragraph of 7 sentences, **When** it is linted, **Then** one warning says that paragraphs allow 6 sentences.
5. **Given** code blocks, inline code, tables, and link addresses, **When** a doc is linted, **Then** no rule fires on them.

### User Story 2 - Lint narration against the spoken profile (Priority: P1)

A script writer lints a narration script. The limits apply to breath groups, and the rules catch things a voice cannot read well.

**Why this priority**: every episode's narration passes through this check before it is spoken.

**Independent Test**: lint a script beat that holds a parenthesis, the abbreviation "e.g.", an equals sign, and "see Figure 3". Each gets an error.

**Acceptance Scenarios**:

1. **Given** a breath group longer than the calibrated spoken limit, **When** it is linted, **Then** one error names it.
2. **Given** a long sentence whose breath groups are all short, **When** it is linted, **Then** only a warning appears.
3. **Given** "this" or "here" more than 15 words after the cue that starts its beat, **When** it is linted, **Then** one warning appears.
4. **Given** a cue marker, **When** a script is linted, **Then** the marker itself is not counted as words.

### User Story 3 - Catch AI writing habits and inconsistent terms (Priority: P2)

Any text gets warnings for the vocabulary, phrases, and punctuation habits that mark AI writing, and for terms the project has replaced.

**Why this priority**: the constitution limits AI writing habits and requires one word for one meaning.

**Independent Test**: lint each paragraph in the AI-style test set. Each one gets at least one finding.

**Acceptance Scenarios**:

1. **Given** "delve" or "a testament to", **When** it is linted, **Then** a warning cites the AI-habits rule.
2. **Given** "bookmark", which the glossary replaces with "cue", **When** it is linted, **Then** a warning names the preferred term.
3. **Given** the `--fix` option, **When** an abbreviation or an avoided term is found, **Then** the file is rewritten with the replacement, and nothing else changes.

### User Story 4 - Evidence for the spoken limits (Priority: P2)

The maintainer reads a report that tests the breath-group hypothesis on real transcripts and shows how often the linter fires on them.

**Why this priority**: the plan stated the hypothesis from three transcripts. The constitution requires evidence before a number becomes a rule.

**Independent Test**: run the study command on the local corpus, which writes a report. The report gives the share of breath groups at 19 words or fewer, the agreement between punctuation and real pauses, and the firing rate.

**Acceptance Scenarios**:

1. **Given** at least 50 transcripts, **When** the study runs, **Then** the report states whether 90 percent of breath groups have 19 words or fewer.
2. **Given** word timings, **When** the study runs, **Then** the report states how often punctuation marks fall at real pauses.
3. **Given** the calibrated limits, **When** the spoken profile runs on every transcript, **Then** the report gives errors per 1,000 words.

### Edge Cases

- A decimal number, a version number, or an abbreviation such as "Dr." must not end a sentence.
- A Markdown list item without a final period still counts as one sentence.
- YAML front matter, HTML comments, and cue markers are not prose.
- A file that cannot be read produces an error finding, not a crash.
- An empty file produces no findings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The linter MUST offer three profiles: written, spoken, and strict.
- **FR-002**: Each finding MUST give the rule id, the severity, the file, the line, and the excerpt.
- **FR-003**: The command MUST exit with a failure when at least one error appears, and succeed otherwise.
- **FR-004**: The command MUST print findings as text by default, and as JSON on request.
- **FR-005**: The written and strict profiles MUST limit sentences to 25 words, and numbered steps to 20 words.
- **FR-006**: The written profile MUST warn about paragraphs of more than 6 sentences, about passive voice, and about parentheses.
- **FR-007**: The written profile MUST report arrows and symbol shorthand in prose as errors.
- **FR-008**: The spoken profile MUST limit breath groups to a calibrated number of words, and only warn about long sentences.
- **FR-009**: The spoken profile MUST report parentheses, abbreviations, math symbols, and references to source layout as errors.
- **FR-010**: The spoken profile MUST warn when "this" or "here" appears more than 15 words after the cue that starts its beat.
- **FR-011**: Every profile MUST warn about AI writing habits, citing Wikipedia's "Signs of AI writing" as the source of the word list.
- **FR-012**: Every profile MUST warn about terms that the project has replaced, and name the preferred term. A file in the repo lists the replacements.
- **FR-013**: The `--fix` option MUST rewrite only abbreviations and replaced terms.
- **FR-014**: A study command MUST test the breath-group hypothesis, compare punctuation with real pauses, and measure the firing rate on the local transcripts.
- **FR-015**: The transcripts MUST stay outside the public repo. Only the study's numbers may appear in it.
- **FR-016**: CI MUST lint the repo's own Markdown docs with the written profile.

### Key Entities

- **Profile**: a named set of rules and limits.
- **Rule**: a check with an id, a severity, the profiles it applies to, and a message.
- **Finding**: one rule firing at one place in one file.
- **Breath group**: the words between two pauses, at a comma, semicolon, colon, or sentence end.
- **Replacement list**: terms to avoid, each with its preferred term.
- **Study report**: the numbers from the transcript study, with the method used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every Markdown doc in the repo passes the written profile with no errors.
- **SC-002**: The spoken profile reports fewer than 2 errors per 1,000 words on the 3Blue1Brown transcripts.
- **SC-003**: Every paragraph in the AI-style test set gets at least one finding, and every paragraph in the clean test set gets no errors.
- **SC-004**: The study covers at least 50 transcripts, and the report states the hypothesis's result with its numbers.
- **SC-005**: Linting the whole repo takes under 5 seconds.

## Assumptions

- The maintainer is asleep, so these choices stand until the morning review: the spoken breath-group limit comes from the study, and warnings never fail the command.
- Punctuation stands in for pauses in breath groups. The study measures how well it does.
- The 3Blue1Brown captions repository has no license, so its transcripts stay in the private content folder.
- The AI-style test set is written for this purpose and lives in the repo.
- Out of scope: noun-stack detection, checks that terms are defined before use, labeling teaching moves with models, rewriting long sentences, and the visual style guide.

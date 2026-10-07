# Feature Specification: Source understanding

**Feature Branch**: `dev`, for the overnight run in decision record 0006

**Created**: 2026-10-07

**Status**: Draft

**Input**: Plan milestone M2. Build adapters for the four source families, the source profile, and the understand step. Done when one source from each family yields a valid knowledge map and study notes, and every anchor resolves.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest any source into one format (Priority: P1)

A user points `unfold ingest` at a source of any family. It writes a source document: a manifest and the clean text, with anchor markers that later files can cite.

**Why this priority**: every later step reads source documents. One format means the later steps never care where a source came from.

**Independent Test**: ingest one small sample of each format, and check that each manifest lists anchors that the text marks.

**Acceptance Scenarios**:

1. **Given** a PDF, **When** it is ingested, **Then** each page becomes an anchor.
2. **Given** a slide deck, **When** it is ingested, **Then** each slide becomes an anchor.
3. **Given** a scan, **When** it is ingested, **Then** its recognized text and confidence are saved.
4. **Given** a web page or Markdown file, **When** it is ingested, **Then** each section becomes an anchor.
5. **Given** a recording, **When** it is ingested, **Then** each transcript segment gets a timestamp anchor.
6. **Given** a bare topic, **When** it is ingested, **Then** the manifest has no text and no anchors.

### User Story 2 - Profile each source (Priority: P1)

The manifest holds a profile: facts that decide how later steps treat the source.

**Why this priority**: slides need gaps filled, textbooks need cutting, and bare topics need fact checks. Rights decide what may become public.

**Independent Test**: read the profile of each ingested sample.

**Acceptance Scenarios**:

1. **Given** an ingested source, **When** its profile is read, **Then** it states family, format, size, quality, subject, and rights.
2. **Given** a non-commercial or unknown license, **When** a source is profiled, **Then** its outputs are marked private.
3. **Given** a PDF with almost no text, **When** it is profiled, **Then** the profile flags low quality.

### User Story 3 - Understand a source (Priority: P1)

`unfold understand` turns a source document into a knowledge map and study notes, using one language-model job with every tool disabled.

**Why this priority**: the knowledge map is what outlines and scripts build on.

**Independent Test**: run the step on one source, then check both outputs with the validators.

**Acceptance Scenarios**:

1. **Given** a source document, **When** the step runs, **Then** it writes a valid knowledge map and study notes.
2. **Given** an output with a broken anchor, **When** it is checked, **Then** the job retries with the errors as feedback.
3. **Given** three failed retries, **When** the job stops, **Then** it reports the failure and writes no output.
4. **Given** unchanged inputs, **When** the step runs again, **Then** it reuses the saved result without a model call.
5. **Given** a bare topic, **When** the step runs, **Then** every claim is flagged as unsupported.

### User Story 4 - Pass the gate on every family (Priority: P2)

The maintainer sees one golden source from each family go from source to study notes.

**Independent Test**: run ingest and understand on the five golden sources, and check every anchor.

**Acceptance Scenarios**:

1. **Given** the five golden sources, **When** ingest and understand run, **Then** every output passes its checks.

### Edge Cases

- A scanned PDF has no text layer. Its profile flags low quality and suggests the scan adapter.
- A web page yields no main text. Ingest reports the failure and writes nothing.
- A recording has long silences. Segments still carry correct timestamps.
- The model returns text that is not YAML. The validator reports it, and the job retries.
- A download fails. Ingest reports the failure and leaves no partial files.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every adapter MUST write the same source document: a manifest and the clean text.
- **FR-002**: Anchors MUST mark pages for PDFs, slides for decks, sections for web pages and Markdown, and timestamps for recordings.
- **FR-003**: The manifest MUST record the origin, the retrieval date, the rights, the profile, and the anchors.
- **FR-004**: The profile MUST record the family, format, size, quality signals, and subject.
- **FR-005**: A source under a non-commercial or unknown license MUST mark its outputs private.
- **FR-006**: The understand job MUST run with every tool disabled and no project settings.
- **FR-007**: Code MUST check each output: the YAML parses, required fields exist, anchors resolve, and required concepts exist.
- **FR-008**: A failed check MUST retry with the errors as feedback, at most 3 times, then report failure.
- **FR-009**: A saved result MUST be reused when its inputs, prompt version, and model are unchanged.
- **FR-010**: For a bare topic, every claim MUST start flagged as unsupported.
- **FR-011**: Downloads MUST land in the private content folder, never in the repo.
- **FR-012**: Each model job MUST leave a record of its model, tokens, time, and outcome.

### Key Entities

- **Source document**: a manifest and the clean text, in one folder.
- **Manifest**: origin, rights, profile, and anchors, in the source/v1 format.
- **Profile**: the facts that decide how to treat a source.
- **Job**: one model task with fixed inputs, one output, and a record.
- **Knowledge map** and **study notes**: the outputs of the understand step.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One golden source from each family yields a valid knowledge map and study notes.
- **SC-002**: Every anchor in those outputs resolves.
- **SC-003**: A second run on unchanged sources makes no model calls.
- **SC-004**: The whole gate uses at most 15 model jobs.
- **SC-005**: Ingesting each golden source takes under 2 minutes on the maintainer's Mac.

## Assumptions

- Model jobs run on the maintainer's Claude subscription through headless Claude Code, as the plan's default runner.
- Scans work on macOS only, because they use Apple's Vision framework.
- The speech model downloads once, and then runs offline.
- The maintainer's own handwritten page arrives later. Until then, a printed test image stands in.
- Out of scope: figure extraction, math recognition beyond the text tools, and the full build graph, which comes in M4.

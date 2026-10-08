# Feature Specification: Product and release

**Feature Branch**: `m7`

**Created**: 2026-10-07

**Status**: Draft

**Input**: Plan milestone M7. Build the MCP server, the plugin, `unfold doctor`, the review page, and the gallery. Write a five-minute quickstart. Done when, on a clean machine, the quickstart produces a rendered segment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find out what this machine lacks (Priority: P1)

`unfold doctor` checks every program and package that unfold needs, and says how to fix each gap.

**Why this priority**: M5 and M6 showed that machines differ, in fonts, voices, and programs.

**Independent Test**: run the doctor with programs hidden, and check its advice.

**Acceptance Scenarios**:

1. **Given** a machine without ffmpeg, **When** the doctor runs, **Then** it names ffmpeg and says how to install it.
2. **Given** a complete machine, **When** the doctor runs, **Then** every check passes and it exits 0.

---

### User Story 2 - Review a series in one page (Priority: P1)

`unfold review` writes one local page for a series. It shows each episode's video, its contact sheets, the eval checks, and the flagged beats.

**Why this priority**: review time is the bottleneck, and one page makes review fast.

**Independent Test**: build a page for a small series, and check what it links.

**Acceptance Scenarios**:

1. **Given** a rendered series, **When** the review page builds, **Then** it shows every episode, contact sheet, and failing check.

---

### User Story 3 - Show public work in a gallery (Priority: P2)

`unfold gallery` builds a static site from series whose sources allow public outputs, and leaves out every other series.

**Why this priority**: open examples show what unfold can do, and rights must decide what goes public.

**Independent Test**: build a gallery from one public series and one private series.

**Acceptance Scenarios**:

1. **Given** a private series, **When** the gallery builds, **Then** it leaves that series out, and says why.

---

### User Story 4 - Use unfold from Claude Code (Priority: P1)

An MCP server gives Claude Code tools to check, build, render, and review a series. A plugin bundles the server with a skill that explains the workflow.

**Why this priority**: the plan ships unfold as a Claude Code plugin.

**Independent Test**: list the server's tools, and call the check tool.

**Acceptance Scenarios**:

1. **Given** the server, **When** a client lists its tools, **Then** it sees check, build, render, review, and doctor.

---

### User Story 5 - Start in five minutes (Priority: P1)

A quickstart takes a new user from install to a rendered segment, with a bundled example scene that needs no model call.

**Why this priority**: a tool that people cannot start is not a product.

**Independent Test**: a CI job on a clean macOS machine runs the quickstart.

**Acceptance Scenarios**:

1. **Given** a clean machine, **When** the quickstart runs, **Then** it produces a rendered segment with a contact sheet.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `unfold doctor` MUST check Python, ffmpeg, LaTeX, manim, the voice, the audio extra, and the claude command, with a fix for each gap.
- **FR-002**: `unfold review` MUST write one HTML page per series, with relative links that open from disk.
- **FR-003**: `unfold gallery` MUST include only series whose every source allows public outputs.
- **FR-004**: The MCP server MUST offer tools for doctor, check, build, render, and review.
- **FR-005**: The plugin MUST bundle the MCP server and a skill.
- **FR-006**: The quickstart MUST render a bundled example scene with no model call, and CI MUST run it on a clean macOS machine.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a clean macOS runner, the quickstart produces a segment and a contact sheet.
- **SC-002**: The MCP server, the plugin, `unfold doctor`, the review page, and the gallery all exist and have tests.

## Assumptions

- The gallery builds a local site. Publishing videos is an outside action, so the maintainer decides where and when.
- The clean-machine test renders the bundled example, because CI may not call a model.
- Cowork support waits for a later release.

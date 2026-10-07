# Feature Specification: Visuals

**Feature Branch**: `m5`

**Created**: 2026-10-07

**Status**: Draft

**Input**: Plan milestone M5. Build the theme, the layout grid, the layout check, and the components that the golden set needs. Then build scene generation, parallel renders, and contact sheets. Done when the golden-set segments render with no layout failures, and each render produces a contact sheet.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Place visuals on a checked grid (Priority: P1)

Each visual comes from a component, which draws it inside a named region of the screen. A layout check then proves that every object stays inside its region and the frame, and that no two regions collide.

**Why this priority**: code can check a layout, but only when every visual comes from a known part.

**Independent Test**: build each component in each region, and run the layout check on good and bad layouts.

**Acceptance Scenarios**:

1. **Given** a component and a region, **When** it is built, **Then** it fits inside that region.
2. **Given** an object outside its region, **When** the check runs, **Then** it names the object and the region.
3. **Given** two regions in use at once, **When** they overlap, **Then** the check reports the collision.

---

### User Story 2 - Turn a storyboard into a scene (Priority: P1)

A scene step maps each storyboard entry to a component with typed parameters, through one model job per segment. An entry that no component can draw becomes a custom visual, which renders as a labeled card and stays flagged for review.

**Why this priority**: the model writes data that tested code draws, so no model-written code runs.

**Independent Test**: drive the step with a fake runner, and check every entry against its component's schema.

**Acceptance Scenarios**:

1. **Given** a storyboard, **When** the scene step runs, **Then** each cue gets one entry with a known component.
2. **Given** a component name that does not exist, **When** the reply is checked, **Then** the step retries with the error.
3. **Given** a custom entry, **When** the scene renders, **Then** a labeled card shows the visual's description.

---

### User Story 3 - Render segments with contact sheets (Priority: P1)

`unfold render` checks each scene's layout, renders its segments in parallel, and makes a contact sheet for each one. A contact sheet is one image with a frame from the end of every beat.

**Why this priority**: contact sheets caught most M1 bugs, and they make review fast.

**Independent Test**: render one small scene, and check the video and the contact sheet.

**Acceptance Scenarios**:

1. **Given** a scene, **When** it renders, **Then** a video and a contact sheet exist.
2. **Given** a scene with a layout failure, **When** the render starts, **Then** it stops before rendering and names the failure.
3. **Given** a finished render, **When** it runs again with no change, **Then** it reuses the video.

### Edge Cases

- A beat's narration is short. The beat still lasts at least 2 seconds.
- A text is too long for its region. The component shrinks it, down to a minimum size, and the check fails below that.
- A bar chart gets more than 12 bars. The schema rejects it, and the step retries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A theme MUST set the background, the colors, and the text sizes of every visual.
- **FR-002**: A layout grid MUST name the regions `full`, `plot`, `top`, `bottom`, `left`, and `right`.
- **FR-003**: Each component MUST take parameters that a schema checks, and MUST draw inside its region.
- **FR-004**: The layout check MUST find objects outside their region or the frame, colliding regions, and text below the minimum size.
- **FR-005**: The scene step MUST be a job with one output file, scene/v0, and its key MUST cover the component-library and manim versions.
- **FR-006**: A custom entry MUST render as a labeled card, and MUST count as flagged for review.
- **FR-007**: `unfold render` MUST run the layout check before rendering, and MUST render segments in parallel.
- **FR-008**: Each render MUST produce a contact sheet with one frame per beat.
- **FR-009**: Each beat MUST last as long as its narration needs, at 165 words a minute, and at least 2 seconds.

### Key Entities

- **Theme**: colors and sizes.
- **Region**: a named box on the screen.
- **Component**: a tested part that draws one kind of visual from typed parameters.
- **Scene**: one segment's entries, each a cue with a region and a component's parameters.
- **Contact sheet**: one image with a frame from the end of every beat.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 12 golden segments render with no layout failures.
- **SC-002**: Each render produces a contact sheet.
- **SC-003**: Every component passes its tests in every region where it fits.
- **SC-004**: The scene step uses at most 30 model calls for the golden set, counting retries and canaries.

## Assumptions

- The model writes data, never code, in this feature. Model-written manim code and its sandbox come in the next feature, so custom entries render as cards for now.
- Beat timing comes from the narration's length. M6 replaces it with the real voice.
- Renders use low quality for review. Final quality comes in M6.
- The components are the ones that the golden storyboards ask for most: text cards, equations, bar charts, scatter plots, and timelines.

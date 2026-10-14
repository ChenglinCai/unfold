# Feature Specification: Neighborhood circle

**Feature Branch**: `claude/local-folder-cloud-access-jlus4i`

**Created**: 2026-10-14

**Status**: Draft

**Input**: M8's machine-learning pack, from `/speckit-specify`. A scatter plot can show the k nearest neighbors of a query point, inside a circle.

## Background

A scatter plot is a component that draws points on two axes, colored by group. A component is a picture that code draws from a scene's parameters. A beat with no component draws a custom visual, which renders as a labeled card for review.

The k-nearest-neighbors method labels a new point by its closest examples. The query point is the new point. Its k nearest points vote, and the largest group wins.

`docs/evals/M8-packs-report.md` found that round 1 asked for a neighborhood circle on a scatter plot three times. Two custom beats still ask for it. Three requests meet the plan's rule for a new component.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show a query point's nearest neighbors (Priority: P1)

A scene names a query point and a number k on a scatter plot. Viewers see the query point, a circle around it, and its k nearest points stand out.

**Why this priority**: the circle is the picture that k-nearest-neighbors lessons need most, and no component draws it today.

**Independent Test**: draw a scatter plot with a query point and k, then check which points stand out and where the circle falls.

**Acceptance Scenarios**:

1. **Given** ten points and k of 3, **When** the plot draws, **Then** exactly the 3 nearest points stand out.
2. **Given** the same plot, **When** it draws, **Then** the circle passes through the third-nearest point.
3. **Given** a distant query point, **When** the plot draws, **Then** the circle stays inside the region.

---

### User Story 2 - Show the vote (Priority: P2)

The query point takes the color of the group that wins the vote among its neighbors.

**Why this priority**: the vote is the method's answer, and code can compute it without error.

**Independent Test**: draw plots whose neighbors have a clear winner, and plots whose neighbors tie.

**Acceptance Scenarios**:

1. **Given** neighbors from groups 0, 0, and 1, **When** it draws, **Then** the query takes group 0's color.
2. **Given** neighbors from groups 0 and 1, **When** it draws, **Then** the query point stays neutral.

---

### User Story 3 - Reject a circle that would mislead (Priority: P1)

A scene that asks for an impossible or unclear circle fails its check, with a message that the scene step can fix on retry.

**Why this priority**: a wrong picture teaches a wrong idea, so code must refuse it before render.

**Independent Test**: check scenes that break each rule, and read each message.

**Acceptance Scenarios**:

1. **Given** k larger than the number of points, **When** the check runs, **Then** it fails and states both numbers.
2. **Given** two points tied for k-th nearest, **When** the check runs, **Then** it fails and asks for another k.
3. **Given** k with no query point, **When** the check runs, **Then** it fails.

### Edge Cases

- A query point may sit on one of the points. That point counts as its nearest neighbor.
- The two axes may use different scales. The neighborhood must still show the points within one distance, so it may draw as an oval.
- A scatter plot with no query point draws exactly as before.
- A plot with a fitted line and a query point draws both.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A scatter plot MUST accept an optional query point and an optional k. Each needs the other.
- **FR-002**: k MUST be a whole number from 1 to the number of points.
- **FR-003**: Code MUST find the k nearest points by straight-line distance in the data's own units.
- **FR-004**: A check MUST reject a plot whose k-th nearest point ties with the next one.
- **FR-005**: The plot MUST draw the query point, mark its k nearest points, and draw the boundary of every point within the k-th distance.
- **FR-006**: The query point MUST take the color of the group with the most neighbors, or a neutral color on a tie.
- **FR-007**: The query point, the circle, and every label MUST fit inside the region, as for every component.
- **FR-008**: The scene prompt MUST describe the query point and k, so the scene step can use them.
- **FR-009**: The component version MUST rise, so saved scenes and renders rebuild.
- **FR-010**: No test may call a language model.

### Key Entities

- **Query point**: an x and a y, in the data's own units.
- **k**: how many nearest points vote.
- **Neighborhood**: every point within the k-th nearest distance of the query point.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 50 random plots, the marked points always match a direct count of the k nearest points.
- **SC-002**: In the same plots, every marked point lies on or inside the boundary, and every other point lies outside it.
- **SC-003**: No random plot breaks the layout check.
- **SC-004**: Every scatter plot without a query point draws the same picture as before.

## Assumptions

- Straight-line distance is the one the golden lessons use. Other distances wait for a later feature.
- Groups keep their five palette colors. The neutral color is the theme's text color.
- Tied neighborhoods are rare in real data, and a retry with another k fixes them. So the check refuses ties instead of drawing them.
- The golden k-nearest-neighbors source is private, so this spec gives no public example from it. The tests use made-up points.
- A golden rebuild needs model calls on the maintainer's access, and this cloud session has no content folder. So the eval measures wait for the maintainer.
- The maintainer asked Claude to keep working. So Claude makes the design calls that principle VIII leaves to the maintainer, and records them for the gate.
- Out of scope: motion, such as a growing circle, and decision boundaries.

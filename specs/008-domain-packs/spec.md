# Feature Specification: Domain packs

**Feature Branch**: `m8-packs`

**Created**: 2026-10-08

**Status**: Draft

**Input**: M8's first feature, from `/speckit-specify`. Add the four components that the golden set asks for most, then measure how many custom visuals remain.

## Background

A component is a tested, reusable animation, and a domain pack is a set of components for one subject. A custom visual is a beat's visual that no component can draw. It renders as a labeled card, and a person must review it.

Today 27 of the 96 golden beats use custom visuals, which is 28 percent. The plan makes a custom visual into a component the third time the golden set needs it. Four kinds of custom visual have passed that mark:

| Kind | Times | Pack |
|---|---|---|
| A complex plane with a unit circle and points at angles | 5 | math |
| A histogram with a mean line, a spread, and a bell curve | 5 | statistics |
| Cash flows that shrink to their present value at a discount rate | 6 | economics and finance |
| Labeled boxes joined by arrows | 5 | core |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Show what future money is worth today (Priority: P1)

A finance segment shows a stream of cash flows, and what each one is worth today at a discount rate. Code computes every discounted number, so no model can invent one.

**Why this priority**: it is the most common custom visual, and it ends invented numbers in finance charts, which progress item 17 raised.

**Independent Test**: draw a known stream of cash flows, and compare each number on screen with the discount formula.

**Acceptance Scenarios**:

1. **Given** yearly flows of 10,000 at 8 percent, **When** it draws, **Then** each shown value matches the formula.
2. **Given** an investment today and returns later, **When** it draws, **Then** the total nets the investment against the returns.

---

### User Story 2 - Show points on a complex plane (Priority: P1)

A math segment shows a complex plane with a unit circle. It marks points by their distance from zero and their angle, with optional guide lines.

**Why this priority**: five Euler's identity beats needed it, and no component draws a plane today.

**Independent Test**: draw points at known angles, and check where each lands.

**Acceptance Scenarios**:

1. **Given** a point at radius 1 and 60 degrees, **When** it draws, **Then** it sits on the unit circle.
2. **Given** a point at radius 3, **When** it draws, **Then** the plane grows to hold it and still fits.
3. **Given** guide lines for a point, **When** the visual draws, **Then** dashed lines drop to both axes, with their labels.

---

### User Story 3 - Show a distribution as a histogram (Priority: P1)

A statistics segment shows counts in bins, with an optional mean line, a spread, and a bell curve. The spread is the standard deviation, which measures how far values fall from the mean.

**Why this priority**: five central limit theorem beats needed it, and bar charts cannot show a mean or a curve.

**Independent Test**: draw a histogram of six dice faces with a mean of 3.5, and check the bars, the line, and the curve.

**Acceptance Scenarios**:

1. **Given** six equal bins and a mean of 3.5, **When** it draws, **Then** the mean line sits at 3.5.
2. **Given** a bell curve without a spread, **When** `unfold check` reads the scene, **Then** it names the missing field.

---

### User Story 4 - Show a process as boxes and arrows (Priority: P2)

A segment shows a few labeled boxes joined by arrows, such as data flowing into a method, or a dollar passing between people.

**Why this priority**: three source families needed it, but a text card can stand in for it today.

**Independent Test**: draw a cycle of three boxes, and check that every arrow joins the right boxes.

**Acceptance Scenarios**:

1. **Given** three boxes in a row, **When** the last links to the first, **Then** that arrow curves past the middle.
2. **Given** an arrow to a missing box, **When** `unfold check` reads the scene, **Then** it names that box.

---

### User Story 5 - Use the new components on the golden set (Priority: P1)

The scene step learns the four components. The maintainer rebuilds the golden scenes, renders them, and compares the results with the scenes from before.

**Why this priority**: the components only help once the scene step uses them.

**Independent Test**: rebuild and render the golden set, then count custom beats, layout failures, and eval results.

**Acceptance Scenarios**:

1. **Given** the saved golden scenes, **When** the component library changes, **Then** only the scene step calls a model.
2. **Given** the rebuilt scenes, **When** they render, **Then** no segment has a layout failure.

### Edge Cases

- A discount rate of zero keeps each present value equal to its face value.
- An investment today is a negative flow, so it sits below the axis.
- A stream of twelve flows drops labels that would overlap, as the timeline does.
- An angle above 360 degrees, or below zero, lands where the same turn would end.
- Histogram counts that do not match the bins fail the scene check with a clear message.
- A box label too long for its box wraps. If it still shrinks too far, the layout check fails it.
- Two arrows between the same pair of boxes, in opposite directions, curve apart so both stay visible.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The scene format MUST accept four new components: `complex-plane`, `histogram`, `present-value`, and `flow-diagram`. A schema MUST check the parameters of each.
- **FR-002**: Each new component MUST draw inside every layout region and pass the layout check on the golden examples.
- **FR-003**: `present-value` MUST compute every present value, and their total, from the amounts, the times, and the rate. The model supplies no discounted number.
- **FR-004**: `histogram` MUST reject counts that do not match its bins, and a bell curve without a mean and a spread.
- **FR-005**: `flow-diagram` MUST reject an arrow whose end names no box.
- **FR-006**: `complex-plane` MUST place each point by its radius and angle, and grow the plane to hold every point.
- **FR-007**: No new component may show overlapping labels. A label that would overlap a kept neighbor MUST drop out.
- **FR-008**: The scene prompt MUST describe each new component and when it beats a custom visual.
- **FR-009**: The component-library version MUST rise, so every saved scene and render rebuilds.
- **FR-010**: The published scene schema MUST describe the new components.
- **FR-011**: An eval report MUST compare the golden set before and after: the custom share, the layout failures, and each scene check's pass rate.

### Key Entities

- **Complex plane visual**: points, each with a label, a radius, and an angle in degrees. Options add the unit circle, guide lines to the axes, and an arc that marks the first point's angle.
- **Histogram visual**: bin edges and a count for each bin. Options add a mean line, a spread, a bell curve, a title, and an axis label.
- **Present-value visual**: a yearly discount rate in percent, and flows that each have a time and an amount. An option shows the total present value.
- **Flow diagram visual**: boxes, each with a short name and a label, and arrows between boxes, each with an optional label. The boxes run left to right or top to bottom.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Custom beats in the golden set fall from 28 percent to at most 10 percent.
- **SC-002**: No golden segment has a layout failure after the rebuild.
- **SC-003**: Every number that a present-value visual shows matches the discount formula, as rounded on screen.
- **SC-004**: Each scene check in the eval passes at least as often as before the rebuild.
- **SC-005**: A person who reads the contact sheets finds no clipped, overlapping, or unreadable text in a new component.

## Assumptions

- Components draw still pictures. The fade-in of each beat is the only motion, so motion inside a component waits for a later feature.
- Angles count in degrees, counterclockwise from the positive real axis, because storyboards name angles that way.
- The discount rate compounds once per period, and times count in periods, such as years.
- The bell curve is the normal curve with the given mean and spread, scaled to the histogram's area.
- The golden set stays the six M2 sources, with 7 episodes, 14 segments, and 96 beats.
- The rebuild makes about 14 model calls on the maintainer's own access, plus any retries.
- The machine-learning pack waits, because its visuals recur only twice.
- Custom visuals still render as cards for review. Model-written manim code for them stays out of scope.
- The maintainer is away and asked Claude to keep going. So Claude makes the design calls that principle VIII leaves to the maintainer, and records them for the gate.

# Feature Specification: Text generation

**Feature Branch**: `dev`, for the overnight run in decision record 0006

**Created**: 2026-10-07

**Status**: Draft

**Input**: Plan milestone M4. Build the schemas, the build graph, saved results, and canary jobs. Generate series plans, outlines, scripts, and storyboards for the golden set, then do the first error analysis. Done when a second build run reuses every saved result, and the first eval report exists.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check any file against its schema (Priority: P1)

A user runs `unfold check` on any file that unfold reads or writes. The command finds the file's format and reports every way the file breaks that format's schema. A schema is a typed description of one file format.

**Why this priority**: every later step trusts its inputs. Schemas turn that trust into a check.

**Independent Test**: run the check on every example file, then on files with one deliberate error each.

**Acceptance Scenarios**:

1. **Given** a valid outline, **When** the check runs, **Then** it reports no errors.
2. **Given** an outline with no core question, **When** the check runs, **Then** it names the missing field and its place.
3. **Given** a file in an unknown format, **When** the check runs, **Then** it says that no schema exists.

---

### User Story 2 - Build a series up to a chosen step (Priority: P1)

A user writes a short series file that names the sources and the audience. `unfold build` then runs each step in order, up to the step the user names. Each step writes one file, and a second run reuses every saved result.

**Why this priority**: the build graph is how unfold avoids repeated work and resumes after a crash.

**Independent Test**: build a series with a fake runner, change one input, and check that only the steps after it run again.

**Acceptance Scenarios**:

1. **Given** understood sources, **When** the build runs until storyboards, **Then** it writes a series plan, an outline, scripts, and storyboards.
2. **Given** a finished build, **When** it runs again, **Then** it makes no model calls.
3. **Given** a changed knowledge map, **When** the build reruns, **Then** every later step reruns, and no earlier step does.
4. **Given** a plan with five episodes, **When** the build runs, **Then** it writes one episode, with at most two segments.

---

### User Story 3 - Generate checked text at each step (Priority: P1)

Each step asks the model for data that matches the step's schema. Code then checks what a schema cannot see: anchors resolve, required concepts exist, cue names are unique, and narration follows the spoken profile.

**Why this priority**: a script with a broken anchor or an unspeakable sentence fails later, where it costs more.

**Independent Test**: drive every step with a fake runner that returns good data, bad data, and data that is good on the second try.

**Acceptance Scenarios**:

1. **Given** a reply that fails a check, **When** the step retries, **Then** the next request includes the errors.
2. **Given** four failed tries, **When** the step stops, **Then** it writes no output, and its record keeps every try's errors.
3. **Given** a beat with no anchor, **When** the check runs, **Then** the beat counts as a flagged claim.
4. **Given** a bare topic, **When** the script step runs, **Then** it flags every beat.

---

### User Story 4 - Stop early when the runner fails (Priority: P2)

Before the first model job of a build, a tiny canary job checks that the runner works. Every model call appends one line to a call log.

**Why this priority**: a broken login or a usage limit should cost one small call, not a failed batch.

**Independent Test**: run a build whose canary fails, and check that no other job ran.

**Acceptance Scenarios**:

1. **Given** a failing canary, **When** a build starts, **Then** it stops before any other model call.
2. **Given** a build with nothing to run, **When** it starts, **Then** it makes no canary call.
3. **Given** any model call, **When** it ends, **Then** the call log gains a line with its step, tokens, and outcome.

---

### User Story 5 - Learn from the first outputs (Priority: P2)

The maintainer reads an eval report built on error analysis. Someone reads every output, writes open notes, and groups them into failure types. Binary checks then measure the most common types.

**Why this priority**: evals must come from real failures, as principle IV requires.

**Independent Test**: run the checks on the golden outputs and compare the pass rates with the report.

**Acceptance Scenarios**:

1. **Given** the golden outputs, **When** analysis ends, **Then** each failure type has a name, a count, and a binary check.
2. **Given** the report, **When** the maintainer reads it, **Then** every quoted output comes from a source that allows public outputs.

### Edge Cases

- A usage limit arrives in the middle of a build. The build stops, finished steps keep their saved results, and the next run resumes.
- The model returns data that breaks the schema. The step counts it as a failed try and retries.
- An outline proposes more segments than the limit. The build writes only the first ones, and it says so.
- A script beat breaks the spoken profile. The lint findings go back as feedback.
- A series names a source that has no knowledge map yet. The build runs the understand step first.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every file format MUST have a versioned schema. The understand formats are source/v1, knowledge-map/v0, and the job record. The new formats are series/v0, series-plan/v0, outline/v0, script/v1, and storyboard/v0.
- **FR-002**: `unfold check` MUST validate a file against the schema that its format field names, and report each error with its place.
- **FR-003**: script/v1 MUST list the anchors of each beat. A beat with no anchor MUST count as a flagged claim.
- **FR-004**: `unfold build SERIES --until STEP` MUST run understand, series plan, outline, script, and storyboard, in that order.
- **FR-005**: Each new step MUST be a job with declared inputs and one output file.
- **FR-006**: The build MUST reuse a saved result when its inputs, prompt, model, and schema have not changed.
- **FR-007**: Each job MUST ask for data that matches its schema. Code MUST then check that anchors resolve, required concepts exist, cue names are unique, and narration has no spoken-profile errors.
- **FR-008**: A failed check MUST retry with the errors as feedback, at most 3 times, then report failure.
- **FR-009**: Each job record MUST keep the errors of every try.
- **FR-010**: Before the first model job of a build, a canary job MUST check the runner. A build with nothing to run MUST make no canary call.
- **FR-011**: Every model call MUST append one line to a call log, with the step, key, model, tokens, time, and outcome.
- **FR-012**: By default, the build MUST write only the first episode of a series, with at most two segments.
- **FR-013**: Eval checks MUST pass or fail. They MUST NOT use 1-to-5 scores.
- **FR-014**: The eval report MUST give each check's pass rate, and MUST quote only outputs whose sources allow public outputs.

### Key Entities

- **Schema**: a typed description of one file format, with a version.
- **Series**: a file that the user writes. It names the sources, the audience, and the limits.
- **Series plan**: the episodes that a series could hold, each with its concepts and anchors.
- **Outline**, **script**, and **storyboard**: one episode's plan, narration, and visual plan.
- **Step**: one kind of job in the build graph, with its inputs, prompt, schema, and checks.
- **Call log**: one line for each model call.
- **Canary**: a tiny job with a known answer, which proves that the runner works.
- **Failure type** and **binary check**: a named kind of error, and a pass-or-fail test for it.
- **Eval report**: the failure types, their counts, and each check's pass rate.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every format in `docs/formats.md` has a schema, and every example file passes its check.
- **SC-002**: All six golden series build to storyboards, and every output passes its checks.
- **SC-003**: A second build run on unchanged inputs makes no model calls.
- **SC-004**: The whole gate uses at most 60 model calls, counting retries and canaries.
- **SC-005**: The eval report names at least 3 failure types, each with a binary check and its pass rate.

## Assumptions

- Series folders live in the private content folder, because outputs from private sources must stay private.
- The user writes `series.yaml`, and the series-plan job writes `plan.yaml`. Keeping them apart means no job rewrites a user's file.
- Generation uses Sonnet, and the canary uses Haiku, the smallest model.
- The understand step keeps writing two files until the maintainer answers progress item 13. Every new step writes one.
- Claude does the first error analysis overnight, and the maintainer reviews it. Principle IV prefers a domain expert, so the report says who read the outputs.
- This first report uses code checks only. Model-based checks come later, after these code checks, as principle III orders them.
- Out of scope: rendering, voice, the review page, and callbacks between episodes.

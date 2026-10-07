# Tasks: Walking skeleton, by hand

Each task names its check. Tasks marked [P] can run in parallel.

## Phase 1: Setup

- [x] T001 Write the spec, plan, and tasks. Check: the writing check passes.

## Phase 2: Voice, which every segment needs

- [x] T002 Write `tests/test_voice.py`, then `src/unfold/voice.py`. Check: the test fails first, then passes, and it skips without `say`.

## Phase 3: User Story 1, the k-NN episode

- [x] T003 Write the episode outline. Check: each segment lists what it requires and establishes.
- [x] T004 [P] Write segment 1's script and storyboard. Check: every cue has a storyboard entry.
- [x] T005 [P] Write segment 2's script and storyboard. Check: every cue has a storyboard entry.
- [x] T006 Write segment 1's scene, and render it. Check: the video has sound, and its frames look right.
- [x] T007 Write segment 2's scene, and render it. Check: the video has sound, and its frames look right.
- [x] T008 Join the segments into the episode. Check: the episode lasts 90 to 150 seconds.

## Phase 4: User Story 2, the economics source

- [x] T009 Write the source manifest, with the license and anchors. Check: the attribution matches CC BY 4.0.
- [x] T010 Write the knowledge map and outline by hand. Check: `tests/test_examples.py` passes, and at least 10 concepts exist.

## Phase 5: User Stories 3 and 4

- [x] T011 Write `docs/formats.md`. Check: each format has two examples.
- [x] T012 Write the retro. Check: it lists what was hard and what to automate first.

## Phase 6: Converge

- [x] T013 Compare the result with the spec, update `docs/milestones.json`, and tag `m1-done`. Check: every M1 gate has evidence.

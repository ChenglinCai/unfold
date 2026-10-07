---
status: accepted
date: 2026-10-06
decision-makers: the maintainer, who asked Claude to finish the milestones overnight
---

# Run overnight work on a dev branch, with the maintainer's gate on main

## Context and Problem Statement

The maintainer asked Claude to work through the milestones overnight, checking in between them, while the maintainer sleeps. Claude cannot ask questions or wait for merges during that time. The maintainer also chose settings that ask before every merge and every dependency change. How can Claude make progress without taking those decisions away?

## Considered Options

* Claude merges each pull request into `main` after CI passes
* Claude opens a stack of pull requests and waits for the maintainer
* Claude commits to a `dev` branch, with a draft pull request into `main` that runs CI on every push

## Decision Outcome

Chosen option: "a dev branch", because `main` keeps the maintainer's approval gate, and the work still moves overnight. Each commit stays small and does one task. A tag marks the end of each milestone, so the maintainer can review one milestone at a time.

Rules for the run:

* Claude never merges into `main`, and never changes repository settings, rulesets, or Claude's own settings.
* Claude never commits course material, transcripts, or other files without an open license.
* Each new dependency goes into `docs/dependencies.md`, with its license, its reason, and how to remove it.
* Language-model jobs run with no tools, so text from a downloaded source cannot make them act. They stay small, and `docs/progress.md` records them.
* Claude sends no notifications at night, and asks no questions that would block the session.
* Claude records every choice that the maintainer would normally make in `docs/progress.md`, under "Decisions for the maintainer to confirm".

### Consequences

* Good, because `main` changes only after the maintainer reviews.
* Good, because a crash loses at most one small commit, since Claude pushes after each task.
* Bad, because the maintainer faces a large review in the morning. Small commits, milestone tags, and check-in notes reduce that.
* Bad, because Claude writes code that the plan reserved for the maintainer, which costs learning. Walkthroughs at each check-in make up part of that.

## Revisit when

* The overnight run ends. The maintainer then decides which milestones reach `main`.

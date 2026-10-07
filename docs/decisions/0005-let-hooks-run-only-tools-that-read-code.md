---
status: accepted
date: 2026-10-06
decision-makers: the maintainer
---

# Let hooks run only tools that read code

## Context and Problem Statement

Claude Code hooks run on their own, with the maintainer's full access. They run outside the sandbox, and the auto-mode classifier does not review them. Claude's edits to ordinary files, such as tests, skip the classifier too. unfold reads sources written by strangers, and a source can hide instructions for Claude. What may a hook run?

## Considered Options

* Ruff, pyright, and the fast tests, as the plan first said
* Only ruff and pyright, which read code but never run it
* No hooks at all

## Decision Outcome

Chosen option: "Only ruff and pyright", because then no hook runs code that Claude wrote. Tests still run, but only as commands that the classifier reviews, and in CI on every pull request. The maintainer chose this on 2026-10-06.

The same review dropped every allow rule from the proposed settings, because in auto mode those rules skip the classifier.

### Consequences

* Good, because an injected instruction cannot reach code execution through a hook.
* Good, because the Stop hook stays fast, at about 5 seconds.
* Good, because a test in `tests/hooks/test_stop_checks.py` fails if a hook ever runs another tool.
* Bad, because Claude can end a turn while a test fails. CI catches the failure later.
* Bad, because this conflicts with the plan's later idea of a Stop hook that runs `unfold check`. That command runs project code, so it needs a new decision.

## Revisit when

* Hooks can run inside the sandbox, or Claude Code itself runs in a container or virtual machine.
* `unfold check` exists, and we want it to run before Claude stops.

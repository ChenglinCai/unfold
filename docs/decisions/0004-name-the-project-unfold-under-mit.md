---
status: accepted
date: 2026-10-06
decision-makers: the maintainer
---

# Name the project unfold, under the MIT license

## Context and Problem Statement

The public name appears in the GitHub repo, the Python package, and the command. It must not contain "3Blue1Brown", "3B1B", or "STE", because those names belong to others. The license decides how others may use the code.

## Considered Options

* unfold, the working name
* explicable, which is free on PyPI and GitHub
* ideafold, which is free on PyPI and unused on GitHub

## Decision Outcome

Chosen option: "unfold", because it describes the product, and renaming stays cheap until the first release. The maintainer chose it on 2026-10-06. The license is MIT, which is short and lets anyone reuse the code.

### Consequences

* Good, because the repo `ChenglinCai/unfold` and the command `unfold` were both free.
* Bad, because an unrelated tool already owns the name `unfold` on PyPI. We cannot publish under that name.
* Bad, because django-unfold, a project with about 3,700 stars, crowds the search results.

## Revisit when

* Before the first PyPI release in M7. Then choose a package name such as `unfold-video`, or rename the project.

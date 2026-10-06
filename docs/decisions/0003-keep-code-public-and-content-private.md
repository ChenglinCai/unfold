---
status: accepted
date: 2026-10-06
decision-makers: the maintainer
---

# Keep code public and content private, in separate folders

## Context and Problem Statement

The code is open source. Many sources belong to others, such as the CIS 5200 lecture notes, and videos made from them cannot be public. Where should private sources and outputs live?

## Considered Options

* One public repo, with a gitignored content folder inside it
* A public repo for code, and a separate private folder for content, with its own local git history
* One private repo for everything

## Decision Outcome

Chosen option: "A public repo and a separate private folder", because private files then live outside the public repo. No command run inside the public repo can stage them.

The layout is `3B1B/unfold/` for the public code and `3B1B/content/` for private content. The content folder is a git repo with no remote.

### Consequences

* Good, because a careless `git add -A` in the public repo cannot reach private files.
* Good, because the content folder keeps a history of the maintainer's edits. The plan uses those edits as examples for prompts later.
* Good, because the public repo still blocks PDFs, videos, and audio with `.gitignore` and a pre-commit hook.
* Bad, because there are two folders to keep in step. Each command takes the content folder's path as input.

## Revisit when

* A collaborator needs the private content. Then add a private remote to the content repo.

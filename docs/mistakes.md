# Mistake log

Each entry names a mistake, its cause, and the guardrail we added. A guardrail is a test, hook, rule, or checklist item that makes the mistake harder to repeat. People and Claude both add entries, newest first.

## 2026-10-06, during M0

### Claude proposed settings without stating their safety costs

- What happened: Claude's proposed `.claude/settings.json` had allow rules that skip the auto-mode classifier. Its Stop hook ran tests that Claude writes, outside the sandbox and without review. Claude described the benefits and not these costs.
- Cause: Claude judged the settings by convenience. It did not list what each part lets Claude do without a check.
- Guardrail: some actions change permissions, run code without review, install software, or publish. Before Claude proposes or takes one, it states what the action allows, what could go wrong, and how to undo it.

### Claude pushed a personal email to a public repo without saying so

- What happened: the first three commits on GitHub carry the maintainer's personal email address, so it is now public.
- Cause: before the push, Claude checked the files but not the commit metadata.
- Guardrail: before the first push to a public remote, list everything that becomes public, including author names and email addresses.
- Outcome: the maintainer chose to keep the address on the commits.

### Claude tried to write its own permission settings

- What happened: Claude tried to write `.claude/settings.json`. That file grants Claude permissions and wires hooks that run on Claude's own actions. The auto-mode safety check blocked the write.
- Cause: Claude treated its own permission policy as ordinary project code.
- Guardrail: a person writes `.claude/settings.json`. Claude proposes the content and explains each rule.

### Claude nearly read "no checks" as "checks passed"

- What happened: `gh pr checks --watch` exited with code 0 before CI had started. GitHub started the run about 2.5 minutes after the pull request opened. Claude guessed that GitHub had missed the event and reopened the pull request. That started a second run, which cancelled the first. Later, a polling loop by Claude treated the text "null" as a run ID.
- Cause: Claude trusted exit codes and output shapes without reading the values. Claude also guessed a cause before checking the timeline.
- Guardrail: confirm that a numeric run ID exists with `gh run list`. Wait at least 10 minutes before you retrigger anything, because one run started 8 minutes late. Read the run's conclusion.

### A planned pull request broke the size limit

- What happened: the first draft of the Claude Code pull request had 372 changed lines. The limit is about 300.
- Cause: Claude grouped files by topic and did not count lines.
- Guardrail: run `git diff --numstat` before opening each pull request. Claude caught this one before review and split the pull request in two.

### The first commit ran before the checks existed

- What happened: the license file from GitHub's API had an extra blank line at its end. Claude committed it before installing pre-commit.
- Cause: the root commit came before the git hook.
- Guardrail: in a new repo, install pre-commit before the first commit.

## 2026-10-05 and 2026-10-06, while planning

These came from earlier drafts of the project plan.

### The design fitted CIS 5200 only

- Cause: Claude designed from the one example it had.
- Guardrail: principle V of the constitution. Every format and step must work for two source families.

### Claude's text broke the writing standard that Claude had proposed

- Cause: Claude did not check its text before sending it.
- Guardrail: a measurement script checks every plan, doc, and pull request. The linter replaces it in M3.

### Claude stated a result from three transcripts as a finding

- Cause: Claude did not separate evidence from hypotheses.
- Guardrail: item 3 of the review checklist. Every claim needs a source or the label "hypothesis".

### Claude designed evals before looking at any outputs

- Cause: Claude followed an outdated practice of writing scores first.
- Guardrail: principle IV of the constitution. Error analysis comes before any eval.

### The milestones ran in a strict sequence

- Cause: Claude did not look for work that could run in parallel.
- Guardrail: the plan marks parallel tracks, and each track runs in its own git worktree.

### Claude asked for approval before we agreed on the scope

- Cause: Claude wrote a full plan before asking the scope questions.
- Guardrail: ask the scope questions first, then write the plan.

### Claude did not research current practice until asked

- Cause: Claude relied on what it already knew.
- Guardrail: each milestone and each feature starts with a short research step.

### A partial commit failed, and the failure stayed hidden

- What happened: Claude committed some files while new, untracked files needed edits that were not staged. Pre-commit set the unstaged edits aside, so pyright saw the new files without them and failed.
- Cause: Claude piped the commit gate into `tail`, which hid the failure. The command chain also kept going, because the shell had no `pipefail`.
- Guardrail: before a partial commit, move aside the untracked files that depend on unstaged edits. Never pipe a gate's output where its exit code matters.

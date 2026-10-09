# Mistake log

Each entry names a mistake, its cause, and the guardrail we added. A guardrail is a test, hook, rule, or checklist item that makes the mistake harder to repeat. People and Claude both add entries, newest first.

## 2026-10-07 and 2026-10-08, during M2 to M8

### A line break looked like the start of a formula

- What happened: the LaTeX reader took `\\[2mm]`, a line break with space, for the display-math opener `\[`. One such break in the OpenIntro book swallowed 550,060 characters as a formula.
- Cause: the math pattern ignored the backslash before the opener. Claude's real files did not include a whole book until PR 32.
- Guardrail: a math opener after a backslash no longer counts, and a test puts line breaks with space beside real formulas. Each reader's real files now include one whole book.

### A lint failure reached a pull request body, twice

- What happened: PR 11 and PR 29 opened with a description that failed `unfold lint`. Each command piped the lint through `tail`, which always succeeds, so the next step ran anyway.
- Cause: the check lived in how Claude chained commands, so one careless chain skipped it.
- Guardrail: Claude now opens and edits pull requests through a script that lints the body first, and sends nothing on any finding.

### A token budget rested on one run

- What happened: Claude set understand's word limit from one run, and read its 74,631 input tokens as mostly fixed overhead. A second run and a probe call showed about 500 tokens of overhead. The limit held, but its stated reason was wrong in the code, the docs, and PR 25.
- Cause: one data point, and an inference stated as a fact. Job records kept no turn count, so nothing could show where the extra tokens came from.
- Guardrail: a claim about token budgets needs two runs of different sources, or a direct count. Job records and call logs now keep each call's turns.

### Code that shows LaTeX cut a deck short

- What happened: the first LaTeX reader looked for `\end{document}` before it set code aside. A Beamer course deck shows that line in a code sample, so the reader kept 3 words of about 2,000.
- Cause: Claude tried the reader on an article and a book, but not on a document that teaches LaTeX. No unit test put document markers inside code.
- Guardrail: the reader now sets code aside before every other step, and a test puts both markers inside code. Before a new reader's pull request merges, it runs on a real file of every kind it claims. For LaTeX, that means an article, a book, and a deck.

### A loop variable broke every gallery video

- What happened: PR 11 copied subtitles in a loop over `name`, inside a function that already used `name` for the series. Every gallery video then linked to a wrong path. The next feature's test caught it.
- Cause: Claude reused a short, common name in a long function. The PR 11 test checked that the file was copied, not the link that the page renders.
- Guardrail: a page test now asserts the video link itself. A loop variable gets a name that says what it holds, such as `subtitles`.

### A Linux font failure waited until the pull request

- What happened: twenty commits of the domain packs ran no Linux check, because CI runs only on pull requests. When the pull request opened, Linux's wider font shrank a flow diagram below 18 points.
- Cause: Claude opened the pull request at the end of the feature. M5 had already shown that Linux fonts run wider, but no local test drew with a wide font.
- Guardrail: open a draft pull request with a feature's first commit, so CI checks every push on Linux. A test now draws flow diagrams with Verdana on macOS, which runs about as wide as Linux's font.

### iCloud made 90 conflict copies after a pull

- What happened: Claude switched to an old local main and pulled, which deleted and rewrote many files at once. iCloud then saved 80 file copies, such as `pages 2.py`, and 10 empty folder copies.
- Cause: the repo sits on the iCloud-synced Desktop, as progress item 5 notes. Claude also let local main fall far behind, so one pull rewrote about 270 files.
- Guardrail: a pre-commit hook now rejects any conflict copy. After a checkout or pull, search for names that end in a space and a number. Moving the repo out of iCloud would end the problem.

### A hook failure looked like a quiet commit

- What happened: a commit stopped on a task line of 27 words, but Claude read only the last two lines of the gate's output. Those lines showed skipped hooks, so the failure looked like success.
- Cause: the gate stopped without a message of its own, and Claude trimmed its output. This is the third failure that a pipe or filter hid.
- Guardrail: the gate now prints "COMMIT FAILED" when a hook fails. After each gate run, look for "pushed" on its last line.

### The commit gate said pushed when the push failed

- What happened: GitHub returned server errors, and two commits and a tag stayed local. The commit script still printed "pushed".
- Cause: the script piped the push through a filter and ignored its exit code.
- Guardrail: the script now stops with "PUSH FAILED" when a push fails. Check `git status -sb` before opening a pull request.

### A loop ran one build instead of three, for the second time

- What happened: a loop over a variable that held three series names ran one build, with all three names as one path. It failed at once.
- Cause: zsh, unlike bash, does not split an unquoted variable into words. Claude hit the same trap on the first night, and did not record it then.
- Guardrail: in zsh, write each list out in full, or use an array. Check that a batch started as many jobs as it should.

### The build tests never ran in the full suite

- What happened: pytest skips folders named build by default, so the 28 tests in `tests/build` ran only when named. The full suite, CI, and the commit gate all missed them.
- Cause: Claude trusted the passing count without checking that it grew.
- Guardrail: after adding a test folder, compare the full suite's count with the new folder's count. `pyproject.toml` now lists the folders that pytest skips.

### CI stayed red for about 40 minutes

- What happened: the recording reader imports faster-whisper, an optional extra. CI skips the extra, so CI's pyright failed, and nobody looked.
- Cause: Claude trusted local checks, and the local environment has every extra. Claude also stopped checking CI after each push.
- Guardrail: check the CI run after any push that changes dependencies or imports. Type-check once without the extras before such a push.

### A partial commit failed, and the failure stayed hidden

- What happened: Claude committed some files while new, untracked files needed edits that were not staged. Pre-commit set the unstaged edits aside, so pyright saw the new files without them and failed.
- Cause: Claude piped the commit gate into `tail`, which hid the failure. The command chain also kept going, because the shell had no `pipefail`.
- Guardrail: before a partial commit, move aside the untracked files that depend on unstaged edits. Never pipe a gate's output where its exit code matters.

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

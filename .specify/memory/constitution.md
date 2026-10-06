# unfold Constitution

These principles govern every spec, plan, and pull request in this repo. Terms follow `docs/glossary.md`.

## Core Principles

### I. Users Bring Their Own Model Access

- Every language-model job MUST run on the user's own access. That means their Claude subscription through the headless runner, or their own API key.
- The project MUST NOT run a hosted service that spends the maintainer's money on other people's runs.
- CI and tests MUST NOT call a language model.

Rationale: contributors cost nothing, secrets stay out of CI, and nobody pays for anyone else's runs.

### II. Code Keeps Track, and Agents Write

- Python owns the build graph, the saved results, and every file write.
- Each language-model step MUST be a job. Python builds its input files, and the runner returns text. Python then checks the text before it writes the one output file.
- The key of a saved result MUST cover the inputs, the prompt version, the model, the component-library version, and the manim version.

Rationale: runs are repeatable, a crash resumes where it stopped, and unchanged work costs no tokens.

### III. Every Claim Has Evidence

- Each task MUST name its check before work starts. The test MUST exist and fail before the code that makes it pass.
- Each claim of success MUST show its evidence, such as test output, a check report, or a contact sheet.
- Automatic checks run first, LLM checks second, and human review last.
- A job MAY retry with feedback from its checks at most 3 times. After that, it MUST report failure.

Rationale: review time is the bottleneck, and evidence makes review fast.

### IV. Evals Come From Real Failures

- Error analysis MUST come before evals. Generate outputs for the golden set, read them, and list the types of failure.
- Each type of failure gets one pass/fail check. Use code where possible. Use an LLM check only where code cannot decide, and only after it agrees with the maintainer's own labels.
- Evals MUST NOT use 1-to-5 scores.
- The golden set MUST cover every source family and every subject.
- A change made to improve the evals stays only if the results improve. The journal records each such change.

Rationale: checks written before anyone reads the outputs measure the wrong things.

### V. Every Design Works for Two Source Families

- Each file format, prompt, and pipeline step MUST work for at least two different source families before we accept it. CIS 5200 is a test case, not the model for the design.
- Every beat MUST list the anchors that support it. A check flags each claim without an anchor, and the maintainer reviews the flagged claims. For a bare topic, every claim starts flagged.

Rationale: a design fitted to one source fails on the next one.

### VI. Plain Language Through the Narration Standard

The Narration Standard is our own set of writing rules, adapted from ASD-STE100. We cite the standard, but we do not copy it. It has three profiles:

- Written, for docs, plans, pull-request descriptions, and agent messages. A sentence MUST have at most 25 words, or 20 in a procedure. Each sentence carries one idea, in active voice. A paragraph has at most 6 sentences. Prose MUST NOT use arrows or symbol shorthand.
- Spoken, for narration. The word limits apply to breath groups, and very long sentences get a warning. Narration MUST NOT use parentheses, abbreviations, or references to the source layout, such as "slide 12". Narration says math in words. "This" and "here" appear only near a cue.
- Strict, for audiences that need maximum clarity. It applies the written limits to every sentence.

Every profile uses one word for one meaning, as the glossary defines it. Every profile defines each term before its first use.

Rationale: clear words make clear videos, and the same rules keep our own docs easy to review.

### VII. Rights and Privacy Come First

- The public repo MUST NOT contain PDFs, videos, audio, transcripts, or course material. They live in the private content folder.
- Each source records its rights. Outputs are private by default, and public examples use only openly licensed sources.
- We MUST NOT copy code from the 3Blue1Brown repositories, because their license forbids commercial use.
- Public names MUST NOT contain "3Blue1Brown", "3B1B", or "STE".

Rationale: course notes, textbooks, and transcripts belong to others.

### VIII. The Human Decides, and Learns

- The maintainer approves each big decision at a Spec Kit gate: the spec, the plan, the tasks, and the converged result. Agents do the bulk work between gates.
- Core modules use the Learning output style. In this style, Claude leaves the design decisions for the maintainer to write.
- At each milestone gate, the maintainer explains one module back, and Claude checks the explanation.

Rationale: the project is also how the maintainer learns agentic engineering. In a 2026 Anthropic study, developers who handed code writing to AI understood their code worst.

### IX. Safety Comes Before Convenience

- Every change to permissions, hooks, installed software, or public content MUST state its safety implications. That means what it allows, what could go wrong, and how to undo it.
- Hooks run with the maintainer's full access, outside the sandbox and without classifier review. So hooks MUST run only tools that read code, such as ruff and pyright. They MUST NOT run tests or other code that Claude wrote.
- Claude MUST NOT write its own permission settings. The maintainer writes `.claude/settings.json`.
- When safety and convenience conflict, choose the option that keeps the maintainer or the classifier in the loop.

Rationale: unfold reads sources written by strangers, and a source can hide instructions for Claude. Each rule above closes one path from such text to harm.

## Scope of Version 0.1

Goals:

1. Turn a source from any of the four source families into a planned series.
2. Turn any planned episode into a narrated video.
3. Keep episodes coherent across a series.
4. Measure narration clarity with the Narration Standard.
5. Let each user run everything on their own model access.

The four source families are textbooks and papers, slides and handwritten notes, web pages and Markdown, and recordings or bare topics. Subjects are math, computer science, statistics, economics, and finance. Narration is in English.

Non-goals:

- A hosted web service.
- Narration in other languages.
- Subjects outside the five above.
- Fine-tuning models.
- Model providers other than Anthropic.
- Cloud or GPU rendering.
- Public videos made from material we have no right to publish.

The stack is Python 3.12, ManimCE 0.21, and uv. Kokoro is the default voice, and headless `claude -p` processes are the default runner.

## Development Workflow

- Every feature goes through Spec Kit: `/speckit-specify`, `/speckit-plan`, and `/speckit-tasks`. Then `/speckit-implement` and `/speckit-converge` repeat until the result matches the spec.
- Bugs go through `/speckit-bug-assess`, `/speckit-bug-fix`, and `/speckit-bug-test`. Each bug also gets an entry in `docs/mistakes.md`.
- New ideas go through the assessment flow, from `/speckit-assess-intake` to `/speckit-assess-decide`, before they become features.
- A change that fits in one sentence skips Spec Kit. Write a test, then open a pull request.
- A pull request changes at most about 300 lines, not counting generated files. Its automatic checks pass before the maintainer reviews it. It merges into the protected `main` branch as one squashed commit.
- Each feature's implementation starts in a fresh session that reads only its spec files.
- A Stop hook keeps Claude working while ruff or pyright fails. A reviewer subagent with fresh context checks each diff against its spec. It reports only failures against requirements.
- Each hard-to-reverse decision gets a decision record in `docs/decisions/`, with a condition for revisiting it.
- Each milestone starts with research on current practice and a pre-mortem. It ends with a retro. About 20% of each milestone goes to cleanup.

Review Checklist. Before anyone presents a plan, doc, or pull request, they check that:

1. The terms match the glossary.
2. The text defines every technical term or drops it.
3. Every claim has a source or carries the label "hypothesis".
4. The design works for at least two different source families.
5. A reviewer can read it in 10 minutes.
6. It passes the written profile of the linter. Until the linter exists, a measurement script checks it.
7. It includes evidence of verification.
8. It states the safety implications of each change, as principle IX requires.

## Governance

- This constitution overrides every other practice document. CLAUDE.md holds only commands, conventions, and the "never" list.
- To amend this constitution, open a pull request that changes this file and states the reason. The maintainer approves each amendment.
- Version numbers have three parts: major, minor, and patch. Removing or redefining a principle is a major change. A new principle or section is a minor change, and a wording fix is a patch.
- Each `/speckit-plan` checks its plan against these principles, and each `/speckit-converge` checks its result.
- The maintainer reviews this constitution at each milestone retro.

**Version**: 1.0.0 | **Ratified**: 2026-10-06 | **Last Amended**: 2026-10-06

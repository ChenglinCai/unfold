# Glossary

Every document in this project uses these terms with these meanings only.

| Term | Meaning |
|---|---|
| source | Material a user gives the tool: a PDF, slides, a scan, a web page, Markdown, a recording, or a bare topic |
| source family | One of four groups of sources: textbooks and papers, slides and handwritten notes, web pages and Markdown, and recordings or bare topics |
| source document | A source after ingestion: clean text, math, figures, structure, and anchors |
| anchor | A pointer to one place in a source: a page, section, slide, or timestamp |
| source profile | Facts that decide how to treat a source: type, size, quality, subject, and rights |
| knowledge map | The concepts, prerequisites, claims, derivation steps, gaps, and suspected errors in a source |
| study notes | A complete written explanation that fills the gaps in a source |
| series | All videos made from one source or one set of sources |
| episode | One long video of 10 to 25 minutes, made of segments |
| segment | One idea, 2 to 5 minutes long |
| scene | One unit that manim renders |
| beat | One short piece of narration and its visual action |
| cue | A marker in a script that ties a word to a visual event. manim-voiceover calls it a bookmark |
| outline | The plan of one episode: segments, order, transitions, and callbacks |
| script | The narration of one segment, with cues |
| storyboard | The visual plan of one segment, with one entry per cue |
| series bible | Shared facts for a series: audience, glossary, notation, colors, and recurring visuals |
| ledger | The record of what each finished episode taught. Later episodes read it |
| component | A tested, reusable animation, such as a supply-and-demand chart |
| domain pack | A set of components for one subject |
| contact sheet | One image grid of key frames from a segment, for quick review |
| job | One LLM task with fixed input files and one output file |
| runner | The part of the tool that executes jobs |
| build graph | The record of which file is made from which, so unchanged results can be reused |
| check | An automatic pass/fail test of an output |
| idea-link check | A check that every idea a segment requires was established earlier |
| LLM check | A pass/fail check that a model performs, for questions code cannot answer |
| eval | A measurement of quality across the golden set |
| error analysis | Reading generated outputs and listing their types of failure, before writing any eval |
| golden set | Fixed example sources with approved outputs, used for evals and tests |
| breath group | The words between two pauses: a comma, semicolon, colon, or sentence end |
| Narration Standard | Our writing rules, adapted from ASD-STE100, with three profiles: written, spoken, and strict |
| constitution | The project's fixed principles, in `.specify/memory/constitution.md`. Every spec and plan must follow them |
| feature | One unit of work in Spec Kit, with its own spec, plan, and tasks |
| spec | The "what and why" of one feature: user stories, acceptance criteria, and what is out of scope |
| decision record | A one-page note of a hard-to-reverse decision, its reasons, and when to revisit it |

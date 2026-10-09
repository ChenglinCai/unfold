# Eval report: M8, LaTeX and EPUB readers

`unfold ingest` gained two readers in M8: one for LaTeX files and one for EPUB books. This report covers five real files, the bugs that they found, and one run of the understand step on a LaTeX source. Examples quote only sources that allow public outputs.

## Real files

| Reader | File | License | Anchors | Words | Seconds |
|---|---|---|---|---|---|
| LaTeX | OpenIntro Statistics, chapter 4 | CC BY-SA 3.0 | 16 | 9,124 | 0.01 |
| LaTeX | OpenIntro Statistics, whole book | CC BY-SA 3.0 | 9 | 23,749 | 0.06 |
| LaTeX | arXiv 2107.07511, a tutorial on conformal prediction | Not checked, so no quotes | 48 | 19,142 | 0.02 |
| LaTeX, Beamer | The learnlatex beginners' course deck | None stated, so no quotes | 47 | 2,010 | under 0.01 |
| EPUB | *The Wealth of Nations*, from Project Gutenberg | Public domain | 66 | 383,485 | 0.04 |

- The paper defines 41 macros. After expansion, none of their names stays in the output.
- The deck gets the slides family, and each titled frame starts an anchor.
- The whole OpenIntro book yields only its front and back matter. A macro, `\includechapter`, pulls in each chapter, and the reader does not expand macros before it follows includes.

## What the real files found

Each finding became a fix and a test before its pull request merged.

| Finding | Fix |
|---|---|
| A code sample that shows `\end{document}` cut a deck to 3 words | The reader sets code aside before every other step, in PR 18 |
| Two braced arguments ran together, as in "normal curvenormal distribution" | A space now separates them, in PR 18 |
| Style commands in the body, such as `\titleformat`, leaked their arguments | Style commands lose every argument, in PR 18 |
| A chapter named its includes from the book's folder, and ingest skipped them in silence | Ingest names each missing include, in PR 22 |
| trafilatura dropped the headings and short chapters of EPUB books | The EPUB reader converts every block itself, in PR 23 |
| A long heading made a 170-character anchor id | Ids stop at 60 characters, in PR 24 |
| A whole book would overflow one understand call | Understand stops before any call over 60,000 words, in PR 25 |

## End to end: understand on a LaTeX source

`unfold understand` read the OpenIntro chapter in one try. The call used 74,631 input tokens and 7,019 output tokens, and took 167 seconds.

- The knowledge map holds 7 concepts, 10 claims, and 2 gaps. Six of the seven concepts cite an anchor.
- The study notes cite anchors 38 times, and the check found each cited anchor in the source.
- The notes cover the normal distribution and leave out the later sections. A textbook has the "cut" need, so understand narrows it to one topic.
- One gap notes that the chapter never says why so many variables come out close to normal, and never mentions the Central Limit Theorem.

## Known limits

- A macro that hides an include, such as `\includechapter`, stays unread. Ingest each chapter's file instead.
- A chapter whose includes name paths from the book's folder loses those files. Ingest names them, so the loss is visible.
- An EPUB formula in MathML without TeX keeps only its plain text.
- An EPUB with encrypted chapters fails with a message, because unfold cannot read them.
- Understand reads at most 60,000 words, so a whole book needs one chapter at a time.

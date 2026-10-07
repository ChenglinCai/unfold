# Research: Source understanding

Each decision lists what we chose, why, and what else we considered.

## PDF text

- Decision: pypdfium2, which reads each page's text with Google's PDFium library.
- Rationale: it is fast, has no other dependencies, and uses the BSD-3 and Apache-2.0 licenses.
- Alternatives: PyMuPDF, which reads PDFs well but uses the AGPL-3.0 license, which would bind every user of this MIT project. pdfplumber and pypdf, which are slower on long files.

## Slides

- Decision: slides as PDF go through the PDF reader, with one anchor per page. PowerPoint files go through python-pptx, which uses the MIT license.
- Rationale: most decks circulate as PDFs. The two readers share the slide anchor format.
- Alternatives: converting PowerPoint to PDF with LibreOffice, which adds a large program.

## Scans

- Decision: Apple's Vision framework, called from a short Swift script. It returns each line of text with a confidence score.
- Rationale: it ships with macOS, reads print and handwriting, and needs no download.
- Alternatives: Tesseract, which is not installed here and reads handwriting poorly.

## Web pages and Markdown

- Decision: trafilatura extracts the main text of a web page as Markdown, under the Apache-2.0 license. Markdown files need no extraction. Both get one anchor per heading.
- Rationale: trafilatura drops menus and footers, and keeps headings.
- Alternatives: Pandoc on raw HTML, which keeps the page's clutter.

## Recordings

- Decision: faster-whisper with the English base model, as an optional `audio` extra. Each transcript segment gets a timestamp anchor.
- Rationale: it is MIT-licensed, runs on the CPU, and needs no PyTorch. The model is about 145 MB, and it downloads once.
- Alternatives: mlx-whisper, which needs PyTorch, numba, and SciPy, and runs only on Apple silicon.

## The model runner

- Decision: headless Claude Code, with `--tools ""` so the model has no tools. `--setting-sources ""` loads no settings or hooks, and `--strict-mcp-config` loads no MCP servers. Each job runs in an empty temporary folder and prints JSON.
- Rationale: it runs on the maintainer's subscription, as the plan requires. With no tools, text inside a source can only change the job's own output, which the validators check.
- Alternatives: `--bare`, which skips settings too, but needs an API key and cannot use a subscription.

## Saved results

- Decision: a result's key is a hash of the source text, the anchors, the prompt version, and the model. Results live next to the source document.
- Rationale: a second run then makes no model calls. M4 replaces this with the build graph.
- Alternatives: no saving, which would spend the subscription on repeated work.

## Anchor citations in study notes

- Decision: study notes cite anchors as `[§anchor-id]`. The validator checks that each one resolves.
- Rationale: the marker is short, unusual in prose, and easy to find with a pattern.
- Alternatives: Markdown links, which would point at files that do not exist yet.

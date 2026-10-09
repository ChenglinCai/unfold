# File formats

These are the formats that unfold reads and writes. Each file names its format and version in a `format` field, such as `outline/v0`. Since M4, each format and version has a schema in `src/unfold/formats/`. `schemas/` holds each schema as a JSON Schema file, and `unfold check` validates any file against its schema.

Every format has two examples from different source families:

- Public: the economics textbook example in `examples/econ-supply-demand/`.
- Private: the CIS 5200 lecture notes in the maintainer's content folder, under `content/cis5200/`. They stay private because they come from copyrighted course notes.

## Anchors

An anchor is a pointer to one place in a source, such as a heading, table, figure, slide, or timestamp. A source manifest lists the anchors its source offers. Other files point at them as `<source-id>#<anchor-id>`, in a list under a key named `anchors`. `unfold.anchors.unresolved()` reports every reference that names nothing.

## Source manifest: `source.yaml`, format `source/v0`

| Field | Meaning |
|---|---|
| `id` | A short name, unique across a series |
| `title`, `work`, `authors`, `published`, `url` | Where the source came from |
| `family` | The source family, such as `textbook` or `lecture-notes` |
| `subject` | One of the five subjects |
| `rights` | The license or owner, the attribution text, and `public_outputs`, which says whether videos made from it may be public |
| `anchors` | Each place the source offers: `id`, `kind`, and `title` |

Examples: `examples/econ-supply-demand/source.yaml`, and `content/cis5200/manifests/lecture-03.yaml`.

## Source document: format `source/v1`

`unfold ingest` writes one folder per source. M1's hand-written manifests use source/v0, and every ingested source uses source/v1. It reads PDF files, PowerPoint decks, images of slides, web pages, Markdown, Jupyter notebooks, LaTeX files, EPUB books, Word files, and recordings. A notebook keeps its Markdown, its code as fenced blocks, and the first 20 lines of each cell's printed output. An EPUB book keeps every chapter in reading order, and each heading starts an anchor. A web page or an EPUB book keeps each formula as TeX, from its own TeX or from its MathML.

A Word file's styled headings start anchors. When no style marks a heading, a short paragraph that is bold throughout and larger than the body text counts as one.

A LaTeX file keeps its sections as anchors and its formulas as TeX. Its own macros expand, so each formula stands alone. Theorems, lists, tables, and figure captions become Markdown. A Beamer deck gets the slides family, and each frame's title starts an anchor. Ingest follows `\input`, `\include`, and `\subfile` only to `.tex` files inside the main file's folder. It also follows an include that a macro hides, such as `\includechapter`, so a whole book reads from its main file.

| File | What it holds |
|---|---|
| `source.yaml` | The manifest, described below |
| `document.md` | The clean text. A line such as `<!-- anchor: p-3 -->` starts each anchored block |
| `original.<ext>` | The downloaded file, when the source came from a URL |
| `understand/` | The outputs of `unfold understand`, described below |

The manifest has these fields:

| Field | Meaning |
|---|---|
| `id`, `title`, `family`, `origin` | What the source is, and the URL or path it came from |
| `retrieved` | The date of ingestion |
| `rights` | `license`, `owner`, `attribution`, and `public_outputs` |
| `profile` | `format`, `size`, `quality`, `subject`, and `needs`. A LaTeX file adds `missing`, the includes that ingest could not find, and `--part` adds `part`, the span of anchors that it kept |
| `anchors` | Each block: `id`, `kind`, and `title` |

`public_outputs` is true only under CC0, CC BY, CC BY-SA, or the public domain, and for a bare topic. `needs` names what the source needs most: `cut`, `fill-gaps`, `clean-up`, or `fact-check`.

Anchor ids follow the family. Pages are `p-1`, slides are `s-1`, sections use heading slugs, timestamps are `t-0042`, and scans are `scan-1`. A bare topic has no anchors.

Examples: the five golden sources in `content/sources/`, which stay private.

## Knowledge map: format `knowledge-map/v0`

| Field | Meaning |
|---|---|
| `source` | The source manifest's id |
| `concepts` | Each idea: `id`, `name`, `meaning` in our own words, the ids it `requires`, and its `anchors` |
| `claims` | Each statement a video may make, with the anchors that support it |
| `gaps` | What the source leaves unexplained, which a video must fill |
| `suspected_errors` | Places where the source may be wrong |
| `written_by` | Who wrote the map: a person, or `unfold understand` with its model |

Examples: `examples/econ-supply-demand/knowledge-map.yaml`, and `content/cis5200/knowledge/lecture-03.yaml`.

A claim with no anchor needs `unsupported: true`, and so does every claim about a bare topic. `unfold.understand.checks.check_map()` checks every rule in this section.

## Study notes: `study-notes.md`

Study notes are Markdown for a learner. They cite the source as `[§p-3]`, or `[§p-3, §p-4]` for several anchors. `unfold.understand.checks.check_notes()` checks that each citation names an anchor of the source.

## Job record: `job.json`

Each model job writes a record next to its outputs.

| Field | Meaning |
|---|---|
| `key` | A hash of the prompt, the request, and the model. A matching key means the saved outputs are reused |
| `model` | The model that ran |
| `attempts` | How many tries the job took |
| `turns` | The model turns inside those tries. The tokens add up over turns, so more turns cost more |
| `input_tokens`, `output_tokens` | The tokens of every try, summed |
| `seconds` | The total time |
| `outcome`, `errors` | `ok` or `failed`, and the last errors |
| `tries` | The errors of each failed try, in order |
| `format` | `job/v0`. Records from M2 have no format field, and still load |

A build keeps its records under `records/` in the series folder, and appends one line per model call to `calls.jsonl`.

## Series: `series.yaml`, format `series/v0`

The user writes this file to ask for a series.

| Field | Meaning |
|---|---|
| `id` | The series name |
| `audience` | Who watches, and what they already know |
| `sources` | Source document folders, as paths relative to the series folder |
| `episodes`, `segments` | How many episodes, and segments of each, to write. The defaults are 1 and 2 |
| `model` | The model for generation. The default is `sonnet` |

`knows` lists what the audience knows already, as items such as `term:interest`. The idea-link check accepts these items without a segment that teaches them.

## Ledger: `ledger.yaml`, format `ledger/v0`

The build writes the ledger after each episode. For each built episode, it lists the segment ids and every item the segments establish. A later episode's outline step sees the ledger, so it can build on earlier ideas and call back to earlier segments.

## Series plan: `plan.yaml`, format `series-plan/v0`

The series-plan step writes this file. Each episode has an `id` such as `E01-equation-of-exchange`, a `title`, a `core_question`, the knowledge-map `concepts` it teaches, and its `anchors`.

## Outline: `outline.yaml`, format `outline/v0`

| Field | Meaning |
|---|---|
| `series`, `episode`, `title` | Where the episode belongs |
| `core_question` | The one question the episode answers |
| `audience` | What viewers already know |
| `previously` | Earlier episodes whose ideas this one uses |
| `segments` | Each segment: `id`, `title`, `target_seconds`, what it `requires` and `establishes`, `anchors`, and optional `callbacks` and `setups` |
| `transitions` | The idea that carries viewers from one segment to the next |

Items in `requires` and `establishes` have a kind and a name, such as `term:demand`, `idea:law-of-demand`, or `visual:demand-curve`. The idea-link check in M6 uses them.

Examples: `examples/econ-supply-demand/outline.yaml`, and `content/cis5200/episodes/E01-knn/outline.yaml`.

## Script: `script.md`, format `script/v0`

A script is Markdown with YAML front matter. The front matter names the `episode`, the `segment`, and the `voice`. Each beat is one paragraph that starts with its cue in double square brackets:

```markdown
[[cross]] They cross at one point: one dollar and forty cents a gallon.
```

Cue names use lower-case letters, digits, and hyphens, and each appears once per script. Narration follows the spoken profile of the Narration Standard. `unfold.script.parse_script()` reads the format.

Examples: `examples/econ-supply-demand/s3-equilibrium/script.md`, and `content/cis5200/episodes/E01-knn/s1-neighbours-vote/script.md`.

## Script: format `script/v1`

script/v1 adds an `anchors` map to the front matter. It lists, for each cue, the anchors that support its beat, as principle V requires. A cue with an empty list is a flagged claim. The script step writes this version, and `Script.anchors()` reads it.

```yaml
anchors:
  cross: [openstax-econ-2e-3-1#table-3-3]
  settle: []
```

## Storyboard: `storyboard.yaml`, format `storyboard/v0`

| Field | Meaning |
|---|---|
| `episode`, `segment` | The segment the storyboard belongs to |
| `entries` | One entry for each cue, in script order: `cue`, `visual` in plain words, `component` or `custom`, and `region` |

A region is where the visual goes on screen, such as `plot`, `top`, or `right`. M5 replaces these names with a layout grid.

Examples: `examples/econ-supply-demand/s3-equilibrium/storyboard.yaml`, and `content/cis5200/episodes/E01-knn/s2-choosing-k/storyboard.yaml`.

## Scene: `scene.yaml`, format `scene/v0`

The scene step writes this file after each storyboard. Each entry gives one cue a region and a component, with that component's parameters. Tested code draws every component, so the model writes data and never code.

```yaml
entries:
  - cue: growth
    region: plot
    visual: {component: bar-chart, labels: [Now, Later], values: [100, 105]}
```

The regions are `full`, `top`, `bottom`, `plot`, `left`, and `right`. The components are `text-card`, `equation`, `bar-chart`, `scatter-plot`, `timeline`, `complex-plane`, `histogram`, `present-value`, `flow-diagram`, and `custom`. A `custom` entry draws as a labeled card, which a person reviews. `src/unfold/visuals/params.py` defines each component's parameters.

`unfold render` turns each scene into `segment.mp4`, `contact-sheet.png`, and `segment.srt`. `timing.json` records when each beat starts and ends, and `render.json` records the render's key. The render then stitches each episode into `episode.mp4` and `episode.srt`, with a title card before each segment.

`unfold translate SERIES --to zh` then writes `episode.zh.srt` beside each rendered episode. A model translates each beat whole, and code splits the Chinese into cues of at most two lines of 16 characters. The cues follow Netflix's Simplified Chinese style guide, and share each beat's time with the English cues.

## Scene code

M1 writes scenes by hand. One Python file holds every segment of an episode, with one manim `Scene` class per segment. Each scene reads its narration from the script, and wraps each beat in `unfold.voice.voiced()`, so the animation lasts as long as the speech. Checks at the top of the file fail the render when the data stops matching the narration. M5 replaces hand-written scenes with tested components.

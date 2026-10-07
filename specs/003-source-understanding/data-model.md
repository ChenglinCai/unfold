# Data model: Source understanding

## Source document

A folder with two files, plus the understand step's outputs:

```text
<source-id>/
├── source.yaml          the manifest, format source/v1
├── document.md          the clean text, with anchor markers
└── understand/
    ├── knowledge-map.yaml
    ├── study-notes.md
    └── job.json         the job's record: key, model, tokens, time, and outcome
```

## Manifest, format source/v1

source/v1 adds `retrieved`, `profile`, and `files` to source/v0.

| Field | Meaning |
|---|---|
| `id` | A short name, unique across a series |
| `title` | The source's title |
| `family` | `textbook`, `slides`, `web`, `recording`, or `topic` |
| `origin` | The URL or file path it came from |
| `retrieved` | The date of ingestion |
| `rights` | `license`, `owner`, `attribution`, and `public_outputs` |
| `profile` | The facts below |
| `anchors` | Each place in the text: `id`, `kind`, and `title` |

## Profile

| Field | Meaning |
|---|---|
| `format` | The file type, such as `pdf`, `pptx`, `png`, `html`, `md`, or `ogg` |
| `size` | Pages, slides, words, or minutes |
| `quality` | Words per page, recognition confidence, or speech confidence, with a `low` flag |
| `subject` | One of the five subjects |
| `needs` | What the source needs most, such as `fill-gaps`, `cut`, or `fact-check` |

`public_outputs` is true only for these licenses: CC0, CC-BY, CC-BY-SA, and public domain. Every other license, and every unknown one, makes it false.

## Anchor markers in `document.md`

Each anchor starts a block with a line such as `<!-- anchor: p-3 -->`. The markers are HTML comments, so they stay invisible when the Markdown renders.

| Family | Anchor ids |
|---|---|
| textbook | `p-1`, `p-2`, and so on, one per page |
| slides | `s-1`, `s-2`, and so on, one per slide |
| web and Markdown | heading slugs, such as `euler-s-formula` |
| recording | `t-0000`, `t-0042`, and so on, the segment's start in seconds |
| scan | `scan-1`, one per image |

## Knowledge map

The knowledge-map/v0 format from `docs/formats.md`, with one rule added. Every claim of a bare topic has `unsupported: true`.

## Job record

| Field | Meaning |
|---|---|
| `key` | The hash of the inputs, the prompt version, and the model |
| `model` | The model that ran |
| `attempts` | How many tries it took |
| `input_tokens`, `output_tokens` | The tokens each try used, summed |
| `seconds` | The total time |
| `outcome` | `ok` or `failed`, with the last errors if it failed |

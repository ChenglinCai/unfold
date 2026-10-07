# Data model: Text generation

## A series folder

A series folder lives in the private content folder. The user writes `series.yaml`, and the build writes everything else.

```text
<series-id>/
├── series.yaml                     the user's request, format series/v0
├── plan.yaml                       the series plan, format series-plan/v0
├── calls.jsonl                     one line per model call
├── records/                        one job record per output, mirroring the paths below
└── E01-<slug>/
    ├── outline.yaml                format outline/v0
    └── s1-<slug>/
        ├── script.md               format script/v1
        └── storyboard.yaml         format storyboard/v0
```

## series/v0, written by the user

| Field | Meaning |
|---|---|
| `id` | The series name, in lower-case letters, digits, and hyphens |
| `audience` | Who watches, and what they already know |
| `sources` | Source document folders, as paths relative to the series folder |
| `episodes` | How many episodes to write. The default is 1 |
| `segments` | How many segments of each episode to write. The default is 2 |
| `model` | The model for generation. The default is `sonnet` |

## series-plan/v0, written by the series-plan step

| Field | Meaning |
|---|---|
| `series` | The series id |
| `written_by` | The step and model that wrote the plan |
| `episodes` | Each episode: `id` such as `E01-equation-of-exchange`, `title`, `core_question`, `concepts`, and `anchors` |

Checks: episode ids are unique, each concept exists in a knowledge map of the series, and each anchor resolves.

## outline/v0, written by the outline step

The format from `docs/formats.md`. Segment ids look like `s1-demand`, and each item in `requires` and `establishes` has the kind `term`, `idea`, or `visual`.

Checks: segment ids are unique, transitions name real segments, anchors resolve, and each target lasts 30 to 300 seconds.

## script/v1, written by the script step

script/v0 plus one field in the front matter. `anchors` maps each cue to the anchors that support its beat.

```markdown
---
format: script/v1
episode: E01-supply-demand
segment: s3-equilibrium
voice: default
anchors:
  cross: [openstax-econ-2e-3-1#table-3-3]
  settle: []
---

[[cross]] They cross at one point: one dollar and forty cents a gallon.

[[settle]] Either way, the price moves toward the crossing point.
```

Checks: cue names are unique, every cue has an entry in `anchors`, anchors resolve, and the narration has no spoken-profile errors. A cue with an empty list is a flagged claim. For a bare topic, every cue is flagged.

## storyboard/v0, written by the storyboard step

The format from `docs/formats.md`. Each entry has `cue`, `visual`, `region`, and either `component` or `custom`.

Checks: the cues match the script's cues, in order.

## job/v0, the job record

The M2 record, plus two fields. `format` names the record's version, and `tries` lists the errors of every try.

## The call log

| Field | Meaning |
|---|---|
| `time` | When the call ended |
| `step`, `output` | The step, and the file it serves |
| `key`, `model`, `attempt` | The job's key, the model, and the try number |
| `input_tokens`, `output_tokens`, `seconds` | What the call cost |
| `outcome`, `errors` | `ok`, `retry`, or `failed`, and any errors |

## Keys

A key hashes four parts: the step's prompt, the request, the model, and the JSON Schema. The request holds the contents of every input file, so a changed input changes the key.

## The eval report

`docs/evals/M4-report.md` lists each failure type with its count, the binary check that measures it, and the check's pass rate. It quotes only outputs whose sources allow public outputs.

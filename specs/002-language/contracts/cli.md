# Contract: `unfold lint`

```text
unfold lint [--profile {written,spoken,strict}] [--format {text,json}]
            [--fix] [--terms PATH] PATH [PATH ...]
```

| Option | Default | Meaning |
|---|---|---|
| `--profile` | `written` | The profile to apply to every path |
| `--format` | `text` | `text` prints one finding per line, and `json` prints one JSON document |
| `--fix` | off | Rewrites abbreviations and replaced terms in place, then lints again |
| `--terms` | `docs/terms.yaml` if it exists | The replacement list |
| `PATH` | | Files to lint. A directory means every `.md` file inside it |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | No errors. Warnings may appear |
| 1 | At least one error |
| 2 | Bad options, or a path that does not exist |

## Text output

One line per finding, then a summary line:

```text
docs/plan.md:12: error N101 sentence-length: 27 words; the limit is 25. "Every claim of success MUST show..."
1 error, 0 warnings in 1 file
```

## JSON output

```json
{
  "profile": "written",
  "findings": [
    {
      "rule": "N101",
      "name": "sentence-length",
      "severity": "error",
      "path": "docs/plan.md",
      "line": 12,
      "excerpt": "Every claim of success MUST show...",
      "message": "27 words; the limit is 25."
    }
  ],
  "errors": 1,
  "warnings": 0
}
```

## Rule ids

| Id | Name | written | spoken | strict |
|---|---|---|---|---|
| N101 | sentence-length | error | warning | error |
| N102 | step-length | error | error | error |
| N103 | breath-group-length | none | error | error |
| N104 | paragraph-length | warning | none | error |
| N201 | symbol-shorthand | error | error | error |
| N202 | parentheses | warning | error | warning |
| N203 | abbreviation | warning | error | error |
| N204 | math-symbols | none | error | none |
| N205 | source-layout | none | error | none |
| N206 | far-deixis | none | warning | none |
| N301 | passive-voice | warning | none | warning |
| N302 | ai-vocabulary | warning | warning | warning |
| N303 | ai-phrase | warning | warning | warning |
| N304 | em-dash | warning | warning | warning |
| N305 | avoided-term | warning | warning | warning |
| N900 | unreadable-file | error | error | error |

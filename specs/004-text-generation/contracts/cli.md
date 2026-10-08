# Contract: `unfold check`, `unfold build`, and `unfold eval`

## `unfold check`

```text
unfold check PATH [PATH ...] [--format text|json]
```

Each `PATH` is a file or a folder. In a folder, the command checks every YAML file and every `script.md`. It finds each file's format from its `format` field, or from a script's front matter, and validates the file against that format's schema.

| Exit code | Meaning |
|---|---|
| 0 | Every file passes |
| 1 | At least one file breaks its schema |
| 2 | Bad options, or a file with no known format |

## `unfold build`

```text
unfold build SERIES [--until STEP] [--model MODEL] [--retries N]
```

`SERIES` is a series folder with a `series.yaml`. `STEP` is `understand`, `plan`, `outline`, `script`, or `storyboard`, and the default is `storyboard`. The command prints one line per output: written, reused, or failed.

- A canary job runs before the first model call. A build with nothing to run makes no call at all.
- `--model` overrides the series file's model. The default number of retries is 3.

| Exit code | Meaning |
|---|---|
| 0 | Every output was written or reused |
| 1 | A step failed after every retry. Earlier outputs stay saved |
| 2 | Bad options, or a series file that breaks its schema |
| 3 | The canary failed, so no other job ran |

## `unfold eval`

```text
unfold eval SERIES [SERIES ...] [--format text|json]
```

The command runs every binary check on the outputs of each series. It prints each check's passes, failures, and pass rate. It also counts the flagged beats, and the custom visuals out of all scene beats.

| Exit code | Meaning |
|---|---|
| 0 | The checks ran. Failed checks are findings, not errors |
| 2 | Bad options, or a folder that is not a series |

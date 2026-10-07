# Contract: `unfold ingest` and `unfold understand`

## `unfold ingest`

```text
unfold ingest SOURCE --out DIR [--id ID] [--family FAMILY] [--title TITLE]
              [--license LICENSE] [--owner OWNER] [--subject SUBJECT]
```

`SOURCE` is a file path, a URL, or, with `--family topic`, a phrase such as "the central limit theorem". The command writes `DIR/<id>/source.yaml` and `DIR/<id>/document.md`, and prints the folder.

| Exit code | Meaning |
|---|---|
| 0 | The source document was written |
| 1 | The source could not be read, and nothing was written |
| 2 | Bad options |

## `unfold understand`

```text
unfold understand DIR [--model MODEL] [--retries N]
```

`DIR` is a source document folder. The command writes the knowledge map, the study notes, and the job record into `DIR/understand/`. It reuses saved results when nothing changed. The default model is `sonnet`, and the default number of retries is 3.

| Exit code | Meaning |
|---|---|
| 0 | Valid outputs were written or reused |
| 1 | The job failed its checks after every retry, and nothing was written |
| 2 | Bad options, or a folder that is not a source document |

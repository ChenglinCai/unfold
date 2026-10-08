# Validation guide: Chinese subtitles

These steps prove the feature works. The formats live in [data-model.md](data-model.md), and the command in [contracts/cli.md](contracts/cli.md).

## 1. Run the tests

```sh
uv run pytest tests/episodes -q
```

Expected: every test passes. The translation tests use a fake runner, so they call no model.

## 2. Confirm the English subtitles stay the same

Render a golden episode again, then compare its `episode.srt` with the saved copy. Expected: the files match byte for byte.

## 3. Translate the golden set

```sh
uv run unfold translate ../content/series/net-present-value --to zh
```

Run it for each of the six golden series. Expected: seven episodes written, none failed.

## 4. Run it again

Expected: every episode reused, and no new line in any `calls.jsonl`.

## 5. Read one public episode

Open one `episode.zh.srt` beside its video, and read every cue. Record each fix it needs in the feature's notes.

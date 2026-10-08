# Contract: `unfold translate`

```text
unfold translate SERIES --to zh [--model MODEL] [--retries N]
```

The command writes `episode.zh.srt` beside each rendered episode of a series. It prints one line for each episode: `written`, `reused`, `failed`, or `skipped`, then a count of each.

| Exit code | Meaning |
|---|---|
| 0 | Every rendered episode has Chinese subtitles |
| 1 | At least one episode failed its checks after every retry |
| 2 | Bad options, or a folder that is not a series |
| 3 | The canary failed, so no translation ran |

A skipped episode has no render yet, so the command notes it and moves on.

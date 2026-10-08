# Data model: Chinese subtitles

## The request

The job sends one line for each beat, in episode order. Each line gives the beat's id, its reading budget, and its English narration:

```text
[s1-growth/title] (at most 42 characters) Put one hundred dollars in a savings account that pays five percent a year.
```

A beat's id joins its segment and its cue name with a slash. The budget is 9 times the beat's spoken seconds, rounded down.

## The reply

| Field | Type | Rule |
|---|---|---|
| `beats` | list of translated beats | one for each beat in the request |

A translated beat has two fields:

| Field | Type | Rule |
|---|---|---|
| `id` | text | a segment id, a slash, and a cue name |
| `text` | text | not empty |

## Checks on the reply

Each failure names its beat, so a retry can fix it:

- "s1-growth/title: missing" and "s1-growth/extra: not a beat in this episode"
- "s1-growth/title: uses a comma or a period. Put a space in its place"
- "s1-growth/title: uses a full-width digit. Use half-width digits, such as 3"
- "s1-growth/title: holds no Chinese"
- "s1-growth/title: keeps the English word interest"
- "s1-growth/title: 45 characters, but its time allows 42"
- "s1-growth/title: runs 17 characters without a space. Put a space at a pause, at least every 16 characters"

## The output

`episode.zh.srt` follows the SubRip format of `episode.srt`. Each cue has a number, a start and an end, and one or two lines of at most 16 characters.

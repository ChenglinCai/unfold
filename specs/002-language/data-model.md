# Data model: The Narration Standard linter

## Unit

A piece of prose that rules check. Each unit keeps the line where it starts, so findings can point at it.

| Kind | Made from |
|---|---|
| paragraph | Lines of prose between blank lines, after preprocessing |
| sentence | A paragraph split by the sentence splitter. A list item is one sentence, even without a final period |
| breath group | A sentence split at commas, semicolons, and colons |
| beat | In a script, one paragraph that starts with a cue |

Preprocessing removes YAML front matter, fenced code blocks, HTML comments, tables, and image tags. It replaces inline code with the word "code", replaces each link with its text, and removes cue markers. Headings are kept for word rules but are not sentences.

## Rule

| Field | Meaning |
|---|---|
| `id` | A stable code, such as `N101` |
| `name` | A short name, such as `sentence-length` |
| `severity` | `error` fails the command, and `warning` does not |
| `profiles` | The profiles the rule applies to, with a severity for each |
| `check` | The function that returns findings for one unit |

## Profile

A name, the rules it runs, and its limits. `lint_text()` takes a profile's name or a Profile object, so the study can test a limit before the code adopts it:

| Limit | written | spoken | strict |
|---|---|---|---|
| words per sentence | 25 | warning above 40 | 25 |
| words per numbered step | 20 | 20 | 20 |
| words per breath group | none | calibrated | 20 |
| sentences per paragraph | 6, warning | none | 6, error |

## Finding

| Field | Meaning |
|---|---|
| `rule` | The rule id |
| `name` | The rule's short name |
| `severity` | `error` or `warning` |
| `path` | The file |
| `line` | The line where the unit starts |
| `excerpt` | Up to 80 characters of the unit or the matched words |
| `message` | What is wrong and what to do |
| `fix` | For mechanical findings only: the text to replace and its replacement |

## Replacement list

`docs/terms.yaml` maps each term to avoid to its preferred term and the reason. The fixer applies only these replacements and the abbreviation expansions.

## Study report

`docs/studies/breath-groups.md` holds numbers only:

- the number of transcripts and words;
- the percentiles of breath-group length, and the share at 19 words or fewer;
- the agreement between punctuation and pauses, at three thresholds;
- the speaking rate;
- the firing rate per 1,000 words.

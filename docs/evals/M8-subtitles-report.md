# Eval report: M8, Chinese subtitles

`unfold translate` gave all seven golden episodes Simplified Chinese subtitles. This report covers two translation rounds and one person's reading. Examples come only from sources that allow public outputs.

## What the checks hold

Netflix's Simplified Chinese style guide sets the rules, and code checks each one:

- At most two lines in a cue, and at most 16 characters in a line. Code splits the beats, so the model cannot break this rule.
- At most 9 characters per second. Each beat gets a budget from its spoken time.
- No commas, no periods outside numbers, and no full-width digits.
- No leftover English words, and a space at least every 16 characters.

## Results

| Measure | Round 1 | Round 2 |
|---|---|---|
| Episodes written | 7 of 7 | 7 of 7 |
| Translate calls | 7 | 8, with 1 retry |
| Cues | 216 | 242 |
| Lines over 16 characters | 0 | 0 |
| Cues faster than 9 characters per second | 0 | 0 |
| Fastest cue | 5.23 per second | 5.38 per second |

- A second run reused every episode, and no call log grew by a line.
- The reading budget never bound. Chinese runs short, so the fastest cue used about 60 percent of the limit.
- Each round also made one canary call per series, so the two rounds cost 27 calls in all.

## What the reading found

Claude read every beat of the velocity-of-money episode, from a Spoken Wikipedia recording, beside its English narration.

- **Accurate.** Every beat keeps its facts, numbers, and names. The equation reads 交易方程, M乘以V等于P乘以Q.
- **Natural.** The economics terms are the standard ones, such as 货币供应量 for money supply and 价格水平 for price level.
- **Words split across lines, in round 1.** A phrase longer than 16 characters had to break somewhere, so 商品 became 商 and 品 on two lines. Round 2 fixed it. Code now packs whole phrases into lines, and a check asks for a space at least every 16 characters.

## Known limits

- The English-word check can flag math notation. Round 2's one retry came from `cosx` in the Euler's identity episode, and the retry wrote `cos x` instead.
- A Chinese speaker on the maintainer's side should still read one episode, as the spec asks. Claude's reading is a first pass.
- The subtitles are sidecar files. The gallery copies them, but its video player does not show them yet.

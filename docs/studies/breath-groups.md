# Study: breath groups in 3Blue1Brown narration

`corpus/breath_groups.py` wrote this report on 2026-10-07. It read the 3Blue1Brown captions from the maintainer's private folder. The captions have no license, so this report holds numbers only.

## Hypothesis

The plan stated, from three transcripts, that 90 percent of breath groups have 19 words or fewer. A breath group is the run of words between two pauses, at a comma, semicolon, colon, or sentence end.

## Results

- Transcripts: 144. The study set aside 5 of them, which have fewer than 0.054 punctuation marks per word, half the median. They look like unpunctuated captions: 2018/basel-problem, 2019/fourier-series-montage, 2020/ldm-logarithms, 2022/some2, 2023/ego-and-math.
- Words in the transcripts studied: 508,020
- Breath groups: 53,762
- Breath groups with 19 words or fewer: 92.4%. The hypothesis holds.
- Breath-group length, in words: median 8, 90th percentile 18, 95th 22, 99th 31, longest 241.
- Sentences with more than 25 words: 38.0%.
- Speaking rate: median 181 words per minute, over 137 transcripts with word timings.

## Punctuation and real pauses

A pause is a silence of at least the threshold between two words. Goldman-Eisler's 0.25-second criterion is common, though not a gold standard, so the table also shows a shorter and a longer threshold. Source: https://pmc.ncbi.nlm.nih.gov/articles/11119743

| Pause threshold | Punctuation marks followed by a pause | Pauses that follow punctuation |
|---|---|---|
| 0.15 s | 83% | 98% |
| 0.25 s | 70% | 98% |
| 0.40 s | 50% | 98% |

## Calibration

- At a limit of 20 words, the spoken profile reports 6.71 errors per 1,000 words.
- The smallest limit with fewer than 1 breath-group error per 1,000 words is 31 words.
- At that limit, the spoken profile reports 1.03 errors per 1,000 words in total. By rule: N103 494, N203 22, N202 2, N205 2, N204 1.

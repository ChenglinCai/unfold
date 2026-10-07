# Corpus scripts

These scripts download and study third-party transcripts. The transcripts stay in the maintainer's private content folder, because they have no license. Only numbers reach this repo.

## 3Blue1Brown captions

The captions repository at https://github.com/3b1b/captions has no license. Download only the English files, into the private folder that sits next to this repo:

```sh
git clone --filter=blob:none --no-checkout --depth 1 \
  https://github.com/3b1b/captions.git ../content/corpus/3b1b-captions
git -C ../content/corpus/3b1b-captions sparse-checkout set --no-cone \
  '/*/*/english/transcript.txt' '/*/*/english/word_timings.json'
git -C ../content/corpus/3b1b-captions checkout main
```

The content folder's `.gitignore` keeps `corpus/` out of its history too.

## The breath-group study

```sh
uv run python corpus/breath_groups.py ../content/corpus/3b1b-captions
```

It rewrites `docs/studies/breath-groups.md`, which holds numbers only. A test checks that the report contains no transcript text.

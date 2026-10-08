# Validation guide: Domain packs

These steps prove the feature works, from the unit tests to the golden rebuild. The parameters live in [data-model.md](data-model.md).

## Prerequisites

- The unfold repo with `uv sync` done, and the private content folder next to it.
- The `claude` command, signed in, for step 4 only. Steps 1 to 3 make no model call.

## 1. Run the component tests

```sh
uv run pytest tests/visuals -q
```

Expected: every test passes, including the property tests and one render test for each new component.

## 2. Record the numbers before the rebuild

```sh
uv run unfold eval ../content/series/*/ --format json > ../content/series/before-packs.json
```

Expected: the output includes the custom share, 27 of 96 beats, and each check's pass rate. The file stays in the private content folder.

## 3. Check the scene schema

```sh
uv run pytest tests/formats -q
uv run unfold check ../content/series
```

Expected: the exported schemas are current, and the old scenes still pass.

## 4. Rebuild and render the golden scenes

```sh
uv run unfold build ../content/series/net-present-value --until scene
uv run unfold render ../content/series/net-present-value
```

Run both commands for each of the six golden series. Expected: each build reruns only its scene jobs, and each render reports 0 layout failures.

## 5. Compare

```sh
uv run unfold eval ../content/series/*/ --format json > ../content/series/after-packs.json
```

Expected: the custom share is at most 10 percent, and no scene check passes less often than before. Then read every contact sheet that holds a new component.

# Validation guide: Neighborhood circle

These steps prove the feature works, from the unit tests to the golden rebuild. The parameters live in [data-model.md](data-model.md).

## Prerequisites

- The unfold repo with `uv sync` done, and LaTeX for the render tests.
- For step 4 only: the private content folder next to the repo, and the `claude` command, signed in.

## 1. Run the tests

```sh
uv run pytest tests/visuals -q
```

Expected: every test passes, including the neighbor tests and the property test.

## 2. Check the scene schema

```sh
uv run pytest tests/formats -q
```

Expected: the exported schemas match the models.

## 3. Look at a drawing

Render the example in data-model.md as a still, and open the picture. Expected: three ringed neighbors, a round boundary through the third one, and a query point in group 0's color.

## 4. Rebuild the golden scenes

```sh
uv run unfold build ../content/series/cis5200-knn --until scene
uv run unfold render ../content/series/cis5200-knn
uv run unfold eval ../content/series/*/
```

Expected: the custom share falls, and no scene check passes less often than before. The series name may differ in the content folder.

# Quickstart: validate text generation

## Prerequisites

The six golden sources from M2 sit in `../content/sources/`, with their knowledge maps. Each golden series gets a folder in `../content/series/`.

## Scenarios

1. Check the example files. Expected: every file passes.

   ```sh
   uv run unfold check examples/econ-supply-demand
   ```

2. Write a series file, then build it. Expected: a plan, an outline, two scripts, and two storyboards, each written once.

   ```yaml
   format: series/v0
   id: velocity-of-money
   audience: Adults who know what money and prices are, with no economics background.
   sources: [../../sources/spoken-velocity-of-money]
   ```

   ```sh
   uv run unfold build ../content/series/velocity-of-money
   ```

3. Build it again. Expected: every line says reused, and `calls.jsonl` gains no line.

4. Check the outputs. Expected: every file passes.

   ```sh
   uv run unfold check ../content/series/velocity-of-money
   ```

5. Run the binary checks on all six series. Expected: one pass rate per check.

   ```sh
   uv run unfold eval ../content/series/*
   ```

## Data contracts

See [contracts/cli.md](contracts/cli.md) and [data-model.md](data-model.md).

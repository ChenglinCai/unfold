# Quickstart: validate source understanding

## Prerequisites

`uv sync --extra audio` for recordings, and macOS for scans. The golden sources download into the private content folder, `../content/sources/`.

## Scenarios

1. Ingest a PDF. Expected: one anchor per page.

   ```sh
   uv run unfold ingest "../CIS 5200 - training example/Lecture 3 - KNN.pdf" --out ../content/sources --id cis5200-lecture-03 --family textbook --license "all rights reserved" --subject computer-science
   ```

2. Understand it. Expected: a valid knowledge map and study notes, with every anchor resolved.

   ```sh
   uv run unfold understand ../content/sources/cis5200-lecture-03
   ```

3. Run it again. Expected: it prints "reused the saved result" and makes no model call.

   ```sh
   uv run unfold understand ../content/sources/cis5200-lecture-03
   ```

4. Ingest a bare topic. Expected: no text and no anchors, and every claim flagged after understanding.

   ```sh
   uv run unfold ingest "the central limit theorem" --family topic --out ../content/sources --id clt --subject statistics
   ```

## Data contracts

See [contracts/cli.md](contracts/cli.md) and [data-model.md](data-model.md).

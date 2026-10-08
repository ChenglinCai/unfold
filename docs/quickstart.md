# Quickstart

This guide takes a Mac from a fresh install to a rendered explainer video in about five minutes. A person wrote the example by hand, so it makes no model call and needs no Claude account.

## What you need

- macOS with [Homebrew](https://brew.sh/).
- [uv](https://docs.astral.sh/uv/), which installs Python and every Python package.

You don't need LaTeX for this example. LaTeX draws equations, and the example has none.

## Run it

1. Install the programs that manim and the episode stitcher use:

   ```sh
   brew install ffmpeg cairo pkg-config
   ```

2. Get the code, and install its Python packages:

   ```sh
   git clone https://github.com/ChenglinCai/unfold.git
   cd unfold
   uv sync
   ```

3. Check the machine. Each failed check names its fix:

   ```sh
   uv run unfold doctor
   ```

4. Copy the example out of the repo, so the render leaves the repo clean:

   ```sh
   cp -R examples/quickstart /tmp/quickstart
   ```

5. Render the copy:

   ```sh
   uv run unfold render /tmp/quickstart
   ```

When the render finishes, it prints `stitched` and the path of the episode video.

## What you get

A segment is one idea, and this one runs about 20 seconds. A beat is one short piece of narration and its visual. The render writes these files in `/tmp/quickstart/E01-compound-growth/`:

| File | What it holds |
|---|---|
| `s1-growth/segment.mp4` | The segment's video, with the voice |
| `s1-growth/contact-sheet.png` | One frame from each beat, so you can check the layout at a glance |
| `s1-growth/timing.json` | When each beat starts and ends |
| `episode.mp4` | The episode: a title card, then the segment |
| `episode.srt` | Subtitles for the episode |

The voice uses the macOS `say` command. On Linux, the render still works, but the video is silent.

## How the example works

The example holds three files. In a real series, `unfold build` writes them with Claude, from your source.

- `E01-compound-growth/outline.yaml` plans the episode. It lists one segment.
- `s1-growth/script.md` holds the narration. Each paragraph is one beat, and it starts with a cue, such as `[[growth]]`.
- `s1-growth/scene.yaml` gives each cue a component and a place on the screen. A component is a tested, reusable animation, such as a bar chart.

Try a change. Edit a value in `scene.yaml`, then render again. The render checks the layout first. When text runs off the frame or labels overlap, it stops and says what to fix.

## Next steps

- Run `uv run unfold check PATH` to check any unfold file against its format.
- To make a series from your own material, install the `claude` command and sign in. Then `unfold ingest`, `unfold understand`, and `unfold build` turn a source into scripts and scenes.
- To use unfold from Claude Code, add the plugin:

  ```sh
  claude plugin marketplace add ChenglinCai/unfold
  claude plugin install unfold@unfold
  ```

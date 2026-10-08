# unfold

unfold turns learning material into a series of explainer videos. Each video has a script, a visual plan, animations made with manim, and a voice.

The project is in early development. To see it work, follow the [quickstart](docs/quickstart.md). It renders a bundled example in about five minutes, with no model call.

## Set up a development machine

You need macOS or Linux, [uv](https://docs.astral.sh/uv/), and LaTeX.

1. Install the system libraries that manim needs. On macOS:

   ```sh
   brew install cairo pkg-config
   ```

   On Ubuntu or Debian:

   ```sh
   sudo apt-get install libcairo2-dev libpango1.0-dev pkg-config
   ```

2. Install LaTeX, which manim uses for equations. [MacTeX](https://www.tug.org/mactex/) works on macOS. Manim's [installation guide](https://docs.manim.community/en/stable/installation/uv.html) lists a smaller set of packages.

3. Install the Python packages and the git hook:

   ```sh
   uv sync
   uv run pre-commit install
   ```

4. Check the setup:

   ```sh
   uv run manim checkhealth
   uv run manim -ql examples/hello.py Hello
   uv run pytest
   ```

   The second command writes a short video to `media/videos/hello/480p15/Hello.mp4`.

## Troubleshooting

If the repo sits in a folder that iCloud Drive syncs, such as the Desktop, iCloud marks `.venv` as hidden. Recent Python versions then skip the `.pth` file that makes `unfold` importable, and `python -v` reports "Skipping hidden .pth file". iCloud also uploads the whole environment. Keep the environment out of iCloud instead:

```sh
rm -rf .venv
UV_PROJECT_ENVIRONMENT=.venv.nosync uv sync
ln -s .venv.nosync .venv
```

iCloud skips any name that ends in `.nosync`, and the `.venv` link lets every command work as before.

## Checks

Every pull request runs the same checks as the git hook, and then the tests. The checks make no calls to language models.

| Command | What it checks |
|---|---|
| `uv run pre-commit run --all-files` | Formatting, lint, types, the lock file, and that no PDFs or media files are committed |
| `uv run pytest` | All tests, including a test render |
| `uv run unfold lint docs` | Prose against the Narration Standard. Use `--profile spoken` for narration |

## License

MIT. See [LICENSE](LICENSE).

# Dependencies

Every dependency, with its license, the reason we need it, and how to remove it. Remove a Python package with `uv remove <name>`.

| Package | Kind | License | Added | Reason |
|---|---|---|---|---|
| manim | runtime | MIT | M0 | Renders every scene |
| pyyaml | runtime | MIT | M1 | Reads the YAML front matter of scripts, and the YAML formats |
| pypdfium2 | runtime | BSD-3-Clause and Apache-2.0 | M2 | Reads text from PDF pages. PyMuPDF was rejected for its AGPL license |
| python-pptx | runtime | MIT | M2 | Reads PowerPoint decks |
| trafilatura | runtime | Apache-2.0 | M2 | Extracts the main text of web pages |
| av | runtime | BSD-3-Clause | M2 | Decodes recordings for Whisper. manim already installs it. Its wheels bundle FFmpeg with the x264 and x265 encoders, which use the GPL |
| numpy | runtime | BSD-3-Clause, with parts under 0BSD, MIT, Zlib, and CC0 | M2 | Holds the decoded audio samples. manim already installs it |
| faster-whisper | `audio` extra | MIT | M2 | Transcribes recordings. Its English base model, about 145 MB, downloads once from Hugging Face |
| pytest | dev | MIT | M0 | Runs the tests |
| ruff | dev | MIT | M0 | Lints and formats Python |
| pyright | dev | MIT | M0 | Checks types |
| pre-commit | dev | MIT | M0 | Runs the checks before each commit |

System tools: cairo and pkg-config from Homebrew, which manim needs on macOS, and a LaTeX distribution for equations. Scans use Apple's Vision framework, which ships with macOS. Install the audio extra with `uv sync --extra audio`.

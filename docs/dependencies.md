# Dependencies

Every dependency, with its license, the reason we need it, and how to remove it. Remove a Python package with `uv remove <name>`.

| Package | Kind | License | Added | Reason |
|---|---|---|---|---|
| manim | runtime | MIT | M0 | Renders every scene |
| pyyaml | runtime | MIT | M1 | Reads the YAML front matter of scripts, and the YAML formats |
| pypdfium2 | runtime | BSD-3-Clause and Apache-2.0 | M2 | Reads text from PDF pages. PyMuPDF was rejected for its AGPL license |
| python-pptx | runtime | MIT | M2 | Reads PowerPoint decks |
| trafilatura | runtime | Apache-2.0 | M2 | Extracts the main text of web pages |
| lxml | runtime | BSD-3-Clause | M2 | Keeps each formula's TeX and drops wiki clutter before extraction. trafilatura already installs it |
| pydantic | runtime | MIT | M4 | Defines the schema of every file format, and validates files and model replies. It brings pydantic-core, annotated-types, and typing-inspection, all MIT |
| av | runtime | BSD-3-Clause | M2 | Decodes recordings for Whisper. manim already installs it. Its wheels bundle FFmpeg with the x264 and x265 encoders, which use the GPL |
| numpy | runtime | BSD-3-Clause, with parts under 0BSD, MIT, Zlib, and CC0 | M2 | Holds the decoded audio samples. manim already installs it |
| faster-whisper | `audio` extra | MIT | M2 | Transcribes recordings. Its English base model, about 145 MB, downloads once from Hugging Face |
| mcp | `mcp` extra | MIT | M7 | Serves unfold's commands as tools to Claude Code. Each tool runs its command in a subprocess |
| pytest | dev | MIT | M0 | Runs the tests |
| ruff | dev | MIT | M0 | Lints and formats Python |
| pyright | dev | MIT | M0 | Checks types |
| pre-commit | dev | MIT | M0 | Runs the checks before each commit |

System tools: cairo and pkg-config from Homebrew, which manim needs on macOS, and a LaTeX distribution for equations. Scans use Apple's Vision framework, which ships with macOS. Install the audio extra with `uv sync --extra audio`.

## Safety

`unfold ingest` downloads files and reads them with the libraries above. Each item says what it allows, what could go wrong, and how to undo it.

- Downloads: ingest fetches any http or https URL you give it, up to 500 MB. The file lands in a temporary folder, then in your private content folder. Delete the source's folder to undo it.
- Parsers: pypdfium2, python-pptx, lxml, and PyAV read files that strangers made. A crafted file could exploit a bug in one of them. Ingest only files you would open on your own computer, and let Dependabot keep these packages current.
- Speech model: faster-whisper downloads its model from Hugging Face once, into `~/.cache/huggingface`. Delete that folder to remove it.
- Schemas: pydantic only validates data in memory. It reads no files and opens no network connections.
- The MCP server: `unfold mcp` exposes only unfold's own commands, and each runs in a subprocess. It never runs other programs or code.
- Model jobs: `unfold understand` sends each source's text to Claude under your own account. The job has no tools, so text in a source can change only the job's reply. Code checks every reply before it writes a file.

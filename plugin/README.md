# The unfold plugin for Claude Code

This plugin lets Claude Code make explainer videos with unfold. It bundles two parts:

- An MCP server, which offers unfold's commands as tools. MCP is the protocol that Claude Code uses to call outside tools.
- A skill, which tells Claude the order of the steps and the rules to follow.

## Install

You need [uv](https://docs.astral.sh/uv/), plus the programs from the [quickstart](../docs/quickstart.md): ffmpeg, cairo, and pkg-config.

```sh
claude plugin marketplace add ChenglinCai/unfold
claude plugin install unfold@unfold
```

Then ask Claude to run the unfold doctor, and fix each gap that it names.

## What it installs and runs

- When Claude Code starts the server, `uvx` installs unfold from the main branch of this repository. It also installs the `audio` and `mcp` extras from PyPI, into uv's cache.
- The first audio check downloads a Whisper speech model from Hugging Face, into `~/.cache/huggingface`.
- Each tool runs one unfold command on your machine, with your account's access. The tools save their outputs inside the folders you give them, and they also use temporary folders and caches.
- The `ingest` tool downloads a web page or file when you give it a URL.
- The `build` tool calls Claude through the `claude` command, so it spends your own Claude usage.
- Claude Code's permission settings decide whether it asks before each tool call.

## What could go wrong

- The plugin runs whatever the main branch held when uv installed it. So anyone who can push to main can change the code that runs on your machine.
- A source's license decides whether its videos may be public. An unknown license keeps them private, so check each license before you ingest.
- Your sources and videos can be private course material. Keep them in a folder outside any public repository, as the skill tells Claude.
- A long build spends a lot of Claude usage, and a render keeps the processor busy for minutes.

## Remove it

```sh
claude plugin uninstall unfold@unfold
claude plugin marketplace remove unfold
```

uv keeps the downloaded packages in a cache that other projects share. To free that space, run `uv cache clean`, and uv downloads again what other projects need. You can also delete the Whisper model from `~/.cache/huggingface/hub`.

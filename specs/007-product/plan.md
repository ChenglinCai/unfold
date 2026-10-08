# Implementation Plan: Product and release

**Branch**: `m7` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

## Summary

`unfold doctor` checks the machine. `unfold review` and `unfold gallery` write static HTML from built series, and the gallery keeps only public series. An MCP server wraps the commands as tools, and a plugin bundles it with a skill. A quickstart renders a bundled example scene, and a CI job runs it on a clean macOS runner.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: the official MCP Python SDK, as the `mcp` extra, for the server. The pages use plain HTML that Python writes, with no new package.

**Testing**: pytest. The MCP test lists the server's tools in process, with no model call.

**Constraints**: CI never calls a model, and the gallery never publishes on its own.

## Constitution Check

| Principle | Result |
|---|---|
| I. Own model access | Passes. The server runs jobs on the user's own runner. |
| VII. Rights | Passes. The gallery checks every source's `public_outputs`. |
| IX. Safety | Passes. The new dependency goes into `docs/dependencies.md`, and the server exposes only unfold's own commands. |

## Project Structure

```text
src/unfold/doctor.py          unfold doctor
src/unfold/pages.py           unfold review and unfold gallery
src/unfold/mcp_server.py      the MCP server, behind the mcp extra
plugin/                       the Claude Code plugin: manifest, skill, and server config
examples/quickstart/          a series with a hand-written scene, for the quickstart
docs/quickstart.md            the five-minute path
.github/workflows/quickstart.yml   the clean-machine job on macOS
```

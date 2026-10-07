---
status: accepted
date: 2026-10-06
decision-makers: the maintainer
---

# Ship local tools, with no hosted service

## Context and Problem Statement

Making a video takes many language-model calls. Someone has to pay for them, and the maintainer will not pay for other people's runs. How should users reach the tool?

## Considered Options

* Local tools: a Python library and command-line tool, a Claude Code plugin with an MCP server, a local review page, and a static gallery
* A hosted web app that calls models with the maintainer's key
* A hosted web app where each user pastes their own API key

## Decision Outcome

Chosen option: "Local tools", because every run uses the user's own model access, and nothing costs the maintainer money.

### Consequences

* Good, because there is no server to pay for, and no user secrets to hold.
* Good, because users keep their sources on their own machines.
* Bad, because each user needs Claude Code or an API key, plus a local install with LaTeX.
* Bad, because the only demo without an install is the static gallery of finished videos.

## Revisit when

* Users ask for a hosted interface. Then consider one that uses each user's own key.

---
status: accepted
date: 2026-10-14
decision-makers: the maintainer
---

# Offer ElevenLabs as a paid voice, chosen on purpose

## Context and Problem Statement

The maintainer listened to six Kokoro voices on 2026-10-14, and found none of them good enough for viewers. ElevenLabs sells voices that sound closer to a person. It runs on its own servers, so each request costs money and sends the narration to ElevenLabs. The narration often comes from private course material.

## Considered Options

* ElevenLabs as an optional voice, on each user's own key
* Other free voice models
* Kokoro only

## Decision Outcome

Chosen option: "ElevenLabs as an optional voice", because the maintainer judged the voice the most important part of a video. It runs only when `UNFOLD_VOICE` names it, and each user pays with their own `ELEVENLABS_API_KEY`, as principle I asks. Kokoro stays the free default. `specs/012-elevenlabs-voice/` holds the design.

### Consequences

* Good, because narration can sound like a person.
* Good, because unchanged beats reuse their saved clips, so a second render costs nothing.
* Bad, because each beat's narration, and its neighbors, leave the machine. That follows principle VII only because the maintainer chose it. Check each plan's terms before you publish a video.
* Bad, because tests use a fake server. A live check waits for the key and network access.

## Revisit when

* A free voice model sounds as natural to the maintainer.
* ElevenLabs changes its terms, prices, or API.

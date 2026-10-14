# Research: ElevenLabs voice

Claude wrote these from its knowledge of ElevenLabs' public API. This environment cannot reach ElevenLabs, so each call waits for a live check.

## The endpoint

- **Decision**: send `POST /v1/text-to-speech/{voice_id}` with `output_format=pcm_24000`. The body holds `text`, `model_id`, `voice_settings`, `previous_text`, and `next_text`. The key goes in the `xi-api-key` header.
- **Rationale**: raw 16-bit audio at 24 kHz needs no decoder, and every plan can request it.
- **Alternatives considered**: MP3, which needs decoding, and the official SDK, which adds a dependency for one request.

## The model

- **Decision**: `eleven_multilingual_v2` by default, and any model through the setting.
- **Rationale**: ElevenLabs recommends it for long narration, and it supports request stitching.
- **Alternatives considered**: `eleven_v3`, which sounds more expressive but, as far as Claude knows, lacks request stitching. The maintainer can try it with `elevenlabs:VOICE@eleven_v3`.

## The default voice

- **Decision**: George, `JBFqnCBsd6RMkjVDRZzb`, a warm narrator from ElevenLabs' default voices.
- **Rationale**: ElevenLabs' own quickstart uses it. The maintainer will likely pick a voice from their own library.

## Voice settings

- **Decision**: stability 0.5, similarity 0.75, style 0, and speaker boost on.
- **Rationale**: these are ElevenLabs' defaults. Style above 0 adds drama, and it can make long narration unsteady.

## Opt-in only

- **Decision**: ElevenLabs runs only when `UNFOLD_VOICE` names it. A key alone does nothing.
- **Rationale**: each request costs money and sends text to another company. Principle IX keeps the maintainer in the loop.

## Neighbors

- **Decision**: every voice's `speak` takes optional `before` and `after` texts. Render passes the neighboring beats of the same segment.
- **Rationale**: request stitching needs them, and the other voices can ignore them.

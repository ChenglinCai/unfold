# Research: Natural voice

Each entry records one design call. Claude made each call on 2026-10-14 after testing Kokoro in a Linux container.

## Kokoro through ONNX, not PyTorch

- **Decision**: run Kokoro with kokoro-onnx and ONNX Runtime.
- **Rationale**: the same weights run without PyTorch. A test install took about 380 MB, against 1.6 GB with PyTorch. Ten seconds of speech took 3.6 seconds on a container's CPU.
- **Alternatives considered**: the `kokoro` package, which needs PyTorch and downloads from Hugging Face.

## Misaki for G2P

- **Decision**: turn text into phonemes with misaki, then pass the phonemes to Kokoro.
- **Rationale**: misaki is the G2P that Kokoro trained with. It tags parts of speech, so a past-tense "read" sounds like "red". In a test, it said Euler, Gaussian, Poisson, and $1.40 correctly.
- **Alternatives considered**: kokoro-onnx's own espeak-ng phonemes. They miss parts of speech, and they come from the GPL library alone.

## No PyTorch through misaki

- **Decision**: depend on plain `misaki`, plus num2words, spaCy, and spaCy's small English model.
- **Rationale**: `misaki[en]` also installs spacy-curated-transformers, which brings PyTorch. Only the transformer G2P needs it, and unfold uses the small model.
- **Alternatives considered**: `misaki[en]`, which works but adds about 1.2 GB.

## spaCy's model as a pinned wheel

- **Decision**: the extra names `en_core_web_sm` 3.8.0 by its GitHub URL and SHA-256.
- **Rationale**: misaki tries to download it at first use with pip, which uv environments lack. A pinned URL installs it with the extra, and the hash guards the file.
- **Alternatives considered**: a download at first use. It failed in a uv environment.
- **Cost**: PyPI refuses packages with URL dependencies. The first PyPI release must move the model elsewhere.

## Model files from GitHub, checked by hash

- **Decision**: download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from kokoro-onnx's release `model-files-v1.0`. Check each against a pinned SHA-256, and keep them in the user's cache folder.
- **Rationale**: the hash stops a changed file from loading. The cache keeps the 350 MB out of every project.
- **Alternatives considered**: Hugging Face, which this cloud environment blocks, and the int8 model, which is smaller but sounds worse.

## The default voice

- **Decision**: `af_heart` at speed 1.0, until the maintainer picks from the samples.
- **Rationale**: Kokoro's voice list rates it highest. At speed 1.0 it spoke 27 words in 10.2 seconds, about 158 words a minute. That pace suits explanation.
- **Alternatives considered**: speeds below 1.0, which drag, and blends of two voices, which need listening tests first.

## Leveling and trimming

- **Decision**: trim silence quieter than 1 percent of full scale from each end, keeping 50 milliseconds. Then scale the clip to an RMS level of minus 20 dBFS, and cap peaks at minus 1 dBFS.
- **Rationale**: in a test, the six voices differed in loudness by 4.5 dB, and one clipped. Even edges keep the render's pause between beats even.
- **Alternatives considered**: a full loudness meter, which needs another dependency for little gain on speech.

## Choosing the voice

- **Decision**: the `UNFOLD_VOICE` setting takes `kokoro:VOICE@SPEED`, `say:VOICE@RATE`, or `none`. With no setting, unfold picks Kokoro when the extra is installed, then `say`.
- **Rationale**: one setting works for renders, the plugin, and CI. Each voice name already goes into the render key.
- **Alternatives considered**: a field in each series file. It can come later, once the maintainer settles on voices.

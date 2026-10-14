# Tasks: ElevenLabs voice

**Tests**: requested. Each test runs and fails before its code exists. Each task names its check.

- [X] T001 [US1] Write tests in `tests/test_elevenlabs.py` with a fake transport, then implement `src/unfold/elevenlabs.py`. Check: the request has the right path, header, and body, the clip is leveled, and a second call sends nothing.
- [X] T002 [US1] Write a render test that each beat gets its neighbors, then pass them in `src/unfold/visuals/render.py`. Add `before` and `after` to every voice. Check: the tests pass.
- [X] T003 [US2] Write tests for the setting, a missing key, a refused request, and the conftest guard. Check: a key alone keeps the free voice, and no message shows the key.
- [X] T004 [US2] Report ElevenLabs in `unfold doctor`, with a test. Check: the doctor tests pass.
- [X] T005 Write decision record 0008, and update `docs/quickstart.md`, `plugin/README.md`, `docs/progress.md`, and `docs/journal.md`. Check: lint passes.
- [X] T006 Run every check and the whole suite. Check: `uv run pre-commit run --all-files` and `uv run pytest` pass.

A live render waits for the maintainer to add the key and allow `api.elevenlabs.io`.

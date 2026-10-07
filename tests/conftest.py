"""Guards for every test."""

import pytest

from unfold import jobs
from unfold.build import command as build_command
from unfold.understand import command as understand_command


def refuse(
    prompt: str, *, system: str, model: str, schema: object = None
) -> jobs.Reply:
    raise AssertionError("tests must not call a language model")


@pytest.fixture(autouse=True)
def no_model_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any test that reaches the real runner through a command."""
    monkeypatch.setattr(understand_command, "RUNNER", refuse)
    monkeypatch.setattr(build_command, "RUNNER", refuse)

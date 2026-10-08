"""unfold doctor names every missing program, with its fix."""

import pytest

from unfold import doctor
from unfold.cli import main


def hide(monkeypatch: pytest.MonkeyPatch, *names: str) -> None:
    real = doctor.which

    def fake(name: str) -> str | None:
        return None if name in names else real(name) or f"/usr/bin/{name}"

    monkeypatch.setattr(doctor, "which", fake)
    monkeypatch.setattr(doctor, "has_module", lambda name: True)
    monkeypatch.setattr(doctor, "draws_text", lambda: True)


def test_a_complete_machine_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    hide(monkeypatch)

    assert main(["doctor"]) == 0
    assert "fail" not in capsys.readouterr().out


def test_a_missing_ffmpeg_fails_and_names_its_fix(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    hide(monkeypatch, "ffmpeg")

    assert main(["doctor"]) == 1
    out = capsys.readouterr().out
    assert "fail ffmpeg" in out
    assert "ffmpeg" in out.split("fail ffmpeg", 1)[1].splitlines()[0]


def test_a_missing_voice_only_warns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    hide(monkeypatch, "say")

    assert main(["doctor"]) == 0
    assert "warn voice" in capsys.readouterr().out


def test_a_missing_latex_only_warns_because_only_equations_need_it(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    hide(monkeypatch, "latex", "dvisvgm")

    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "warn latex" in out and "equations" in out

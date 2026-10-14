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


def test_kokoro_is_the_voice_when_its_extra_is_installed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    hide(monkeypatch, "say")

    assert main(["doctor"]) == 0
    assert "ok   voice: kokoro" in capsys.readouterr().out


@pytest.mark.parametrize(("say", "detail"), [(True, "say"), (False, "silent")])
def test_without_kokoro_the_voice_warns_and_names_the_extra(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    say: bool,
    detail: str,
) -> None:
    hide(monkeypatch, *([] if say else ["say"]))
    monkeypatch.setattr(doctor, "has_module", lambda name: name != "kokoro_onnx")

    assert main(["doctor"]) == 0
    line = next(x for x in capsys.readouterr().out.splitlines() if "voice" in x)
    assert line.startswith("warn") and detail in line and "--extra voice" in line


def test_a_missing_latex_only_warns_because_only_equations_need_it(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    hide(monkeypatch, "latex", "dvisvgm")

    assert main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "warn latex" in out and "equations" in out

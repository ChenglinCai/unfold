"""unfold doctor: check every program and package that unfold needs.

A required gap fails the run, and an optional gap only warns. Each finding
says how to fix it, because machines differ in fonts, voices, and programs.
"""

import argparse
import importlib.util
import shutil
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    name: str
    ok: bool
    detail: str
    fix: str
    required: bool = True


def which(name: str) -> str | None:
    return shutil.which(name)


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def draws_text() -> bool:
    """Whether manim can draw text, which needs cairo and pango."""
    try:
        from manim import Text

        Text("ok")
    except Exception:  # cairo and pango fail in many ways
        return False
    return True


def program(name: str, fix: str, required: bool = True, label: str = "") -> Finding:
    found = which(name)
    return Finding(
        label or name, found is not None, found or "not found", fix, required
    )


def checks() -> list[Finding]:
    version = ".".join(map(str, sys.version_info[:2]))
    text, whisper = draws_text(), has_module("faster_whisper")
    return [
        Finding(
            "python",
            sys.version_info[:2] == (3, 12),
            version,
            "Use Python 3.12, which uv installs: uv python install 3.12",
        ),
        program("ffmpeg", "Install ffmpeg, such as with: brew install ffmpeg"),
        program("latex", "Install a TeX distribution, such as MacTeX or TeX Live"),
        program("dvisvgm", "Install dvisvgm, which comes with most TeX distributions"),
        Finding(
            "manim",
            text,
            "draws text" if text else "cannot draw text",
            "Install cairo and pango, such as with: brew install cairo pango pkg-config",
        ),
        program(
            "say",
            "Use macOS for a voice. Without one, segments render silent",
            required=False,
            label="voice",
        ),
        Finding(
            "audio",
            whisper,
            "faster-whisper" if whisper else "missing",
            "Add the audio extra, for recordings and audio checks: uv sync --extra audio",
            required=False,
        ),
        program(
            "claude",
            "Install Claude Code and log in, so build and understand can run jobs",
            required=False,
        ),
    ]


def add_doctor_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    command = commands.add_parser("doctor", help="Check what this machine needs.")
    command.set_defaults(run=run_doctor)


def run_doctor(args: argparse.Namespace) -> int:
    failed = False
    for finding in checks():
        status = "ok" if finding.ok else "fail" if finding.required else "warn"
        failed |= not finding.ok and finding.required
        line = f"{status:4} {finding.name}: {finding.detail}"
        print(line if finding.ok else f"{line}. Fix: {finding.fix}")
    return 1 if failed else 0

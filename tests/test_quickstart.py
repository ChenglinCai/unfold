"""The quickstart example passes its checks and renders with no model call."""

import shutil
from pathlib import Path

import pytest

from unfold.cli import main

EXAMPLE = Path(__file__).parent.parent / "examples" / "quickstart"
EPISODE = Path("E01-compound-growth")
SEGMENT = EPISODE / "s1-growth"


def test_the_example_passes_its_checks() -> None:
    script = EXAMPLE / SEGMENT / "script.md"

    assert main(["check", str(EXAMPLE)]) == 0
    assert main(["lint", "--profile", "spoken", str(script)]) == 0


@pytest.mark.slow
@pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="the quickstart needs ffmpeg"
)
def test_the_example_renders_a_segment_and_an_episode(tmp_path: Path) -> None:
    copy = shutil.copytree(EXAMPLE, tmp_path / "quickstart")

    assert main(["render", str(copy)]) == 0

    assert (copy / SEGMENT / "segment.mp4").stat().st_size > 0
    assert (copy / SEGMENT / "contact-sheet.png").stat().st_size > 0
    assert (copy / EPISODE / "episode.mp4").stat().st_size > 0
    assert "Put one hundred dollars" in (copy / EPISODE / "episode.srt").read_text()

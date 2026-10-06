"""The hello scene renders to a real video."""

import subprocess
import sys
from pathlib import Path

import av
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.slow
def test_hello_scene_renders_a_video(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "manim",
            "-ql",
            "--disable_caching",
            "--media_dir",
            str(tmp_path),
            str(REPO_ROOT / "examples" / "hello.py"),
            "Hello",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    videos = list(tmp_path.rglob("Hello.mp4"))
    assert len(videos) == 1

    with av.open(str(videos[0])) as container:
        assert container.streams.video, "the file has no video stream"
        assert container.duration is not None
        assert container.duration > 0

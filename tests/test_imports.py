"""Each module imports on its own, in a fresh process, so no import cycle hides."""

import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "unfold.visuals.params",
        "unfold.visuals.components",
        "unfold.formats.episode",
        "unfold.formats.series",
        "unfold.build.replies",
    ],
)
def test_a_module_imports_first(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}"], capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr.splitlines()[-1:]

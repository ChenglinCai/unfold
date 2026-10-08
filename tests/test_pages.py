"""The review page shows one series, and the gallery shows only public ones."""

from pathlib import Path

import pytest
import yaml
from PIL import Image

from unfold.cli import main
from unfold.sources import Anchor, SourceDocument

SCRIPT = """---
format: script/v1
episode: E01-growth
segment: s1-interest
voice: default
anchors:
  start: [demo#p-1]
  aside: []
---

[[start]] Money grows when it earns interest.

[[aside]] Nobody knows why people love round numbers.
"""


def make_series(root: Path, name: str, public: bool | str) -> Path:
    doc = SourceDocument(
        f"demo-{name}",
        "Demo",
        "textbook",
        "demo.pdf",
        {},
        {},
        [Anchor("p-1", "page", "P1")],
    )
    rights = {
        "license": "CC BY 4.0" if public else "all rights reserved",
        "owner": "Someone",
        "attribution": f"Demo source for {name}, CC BY 4.0",
        "public_outputs": public,
    }
    doc.rights = rights
    doc.save(root / "sources")
    folder = root / "series" / name
    segment = folder / "E01-growth" / "s1-interest"
    segment.mkdir(parents=True)
    series: dict[str, object] = {
        "format": "series/v0",
        "id": name,
        "audience": "Adults.",
    }
    series["sources"] = [f"../../sources/demo-{name}"]
    (folder / "series.yaml").write_text(yaml.safe_dump(series))
    episode: dict[str, object] = {
        "id": "E01-growth",
        "title": "Growth",
        "core_question": "Why?",
    }
    episode["concepts"] = ["interest"]
    plan = {"format": "series-plan/v0", "series": name, "episodes": [episode]}
    (folder / "plan.yaml").write_text(yaml.safe_dump(plan))
    outline = {
        "format": "outline/v0",
        "series": name,
        "episode": "E01-growth",
        "title": "Growth",
        "core_question": "Why does money grow?",
        "audience": "Adults.",
        "segments": [{"id": "s1-interest", "title": "Interest", "target_seconds": 30}],
    }
    (folder / "E01-growth" / "outline.yaml").write_text(yaml.safe_dump(outline))
    (segment / "script.md").write_text(SCRIPT)
    Image.new("RGB", (8, 8), "black").save(segment / "contact-sheet.png")
    (folder / "E01-growth" / "episode.mp4").write_bytes(b"not a real video")
    return folder


def test_the_review_page_links_videos_sheets_and_flags(tmp_path: Path) -> None:
    folder = make_series(tmp_path, "growth", public=False)

    assert main(["review", str(folder)]) == 0

    page = (folder / "review.html").read_text()
    assert 'src="E01-growth/episode.mp4"' in page
    assert 'src="E01-growth/s1-interest/contact-sheet.png"' in page
    assert "flagged" in page and "Nobody knows why" in page
    assert "plan-fits-source" in page


def test_the_gallery_keeps_only_public_series(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    public = make_series(tmp_path, "open", public=True)
    private = make_series(tmp_path, "closed", public=False)
    out = tmp_path / "site"

    assert main(["gallery", str(public), str(private), "--out", str(out)]) == 0

    index = (out / "index.html").read_text()
    assert "open" in index and "Demo source for open, CC BY 4.0" in index
    assert (out / "open" / "E01-growth" / "episode.mp4").exists()
    assert not (out / "closed").exists()
    assert "skipped closed" in capsys.readouterr().out


def test_the_gallery_fails_closed_on_missing_or_unclear_rights(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    empty = make_series(tmp_path, "empty", public=True)
    series = yaml.safe_load((empty / "series.yaml").read_text())
    series["sources"] = []
    (empty / "series.yaml").write_text(yaml.safe_dump(series))
    unclear = make_series(tmp_path, "unclear", public="yes")
    out = tmp_path / "site"

    assert main(["gallery", str(empty), str(unclear), "--out", str(out)]) == 0

    printed = capsys.readouterr().out
    assert "skipped empty: the series lists no sources" in printed
    assert "skipped unclear: source demo-unclear keeps its outputs private" in printed
    assert not (out / "empty").exists() and not (out / "unclear").exists()

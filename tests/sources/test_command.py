"""`unfold ingest` writes one source document folder, or nothing at all."""

from pathlib import Path

import pytest

from unfold.cli import main
from unfold.sources import command, load

MARKDOWN = "Intro.\n\n## Demand\n\nPrices rise, and buyers buy less.\n"
REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def notes(tmp_path: Path) -> Path:
    path = tmp_path / "notes.md"
    path.write_text(MARKDOWN)
    return path


def nothing_in(folder: Path) -> bool:
    return not folder.exists() or not any(folder.iterdir())


def test_ingests_a_markdown_file(
    notes: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "sources"

    code = main(["ingest", str(notes), "--out", str(out), "--license", "CC BY 4.0"])

    assert code == 0
    assert capsys.readouterr().out.strip() == str(out / "notes")
    doc = load(out / "notes")
    assert (doc.family, doc.title) == ("web", "notes")
    assert [a.id for a in doc.anchors] == ["intro", "demand"]
    assert doc.rights["public_outputs"] is True
    assert doc.profile["subject"] == "unknown"


def test_a_bare_topic_has_no_text_and_no_anchors(tmp_path: Path) -> None:
    out = tmp_path / "sources"
    phrase = "the central limit theorem"

    assert main(["ingest", phrase, "--family", "topic", "--out", str(out)]) == 0

    folder = out / "the-central-limit-theorem"
    doc = load(folder)
    assert (doc.title, doc.anchors) == (phrase, [])
    assert (folder / "document.md").read_text() == ""
    assert doc.profile["needs"] == "fact-check"


def test_refuses_to_write_inside_the_repo(
    notes: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = REPO / "ingest-test-output"

    assert main(["ingest", str(notes), "--out", str(target)]) == 2

    assert not target.exists()
    assert "inside the unfold repo" in capsys.readouterr().err


def test_refuses_an_id_that_could_escape_the_folder(
    notes: Path, tmp_path: Path
) -> None:
    out = tmp_path / "sources"

    assert main(["ingest", str(notes), "--out", str(out), "--id", "../x"]) == 2
    assert nothing_in(out)


def test_an_unknown_file_type_needs_a_reader(tmp_path: Path) -> None:
    source = tmp_path / "data.xyz"
    source.write_text("x")

    assert main(["ingest", str(source), "--out", str(tmp_path / "out")]) == 2


def test_an_unreadable_source_writes_nothing(tmp_path: Path) -> None:
    page = tmp_path / "empty.html"
    page.write_text("<html><body><nav>Home</nav></body></html>")
    out = tmp_path / "sources"

    assert main(["ingest", str(page), "--out", str(out)]) == 1
    assert nothing_in(out)


def test_a_download_keeps_the_original_beside_the_document(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        command, "download", lambda url: (MARKDOWN.encode(), "text/plain")
    )
    out = tmp_path / "sources"
    url = "https://example.org/files/notes.md"

    assert main(["ingest", url, "--out", str(out)]) == 0

    assert (out / "notes" / "original.md").read_bytes() == MARKDOWN.encode()
    assert load(out / "notes").origin == url


def test_a_download_without_a_suffix_uses_its_content_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    page = "<html><body><article><h1>Velocity</h1><p>" + "Money moves. " * 20
    page += "</p></article></body></html>"
    monkeypatch.setattr(command, "download", lambda url: (page.encode(), "text/html"))
    out = tmp_path / "sources"

    code = main(
        ["ingest", "https://example.org/wiki/Velocity_of_money", "--out", str(out)]
    )

    assert code == 0
    assert (out / "velocity-of-money" / "original.html").exists()


def test_a_failed_download_leaves_no_partial_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(url: str) -> tuple[bytes, str]:
        raise OSError("the network is down")

    monkeypatch.setattr(command, "download", fail)
    out = tmp_path / "sources"

    assert main(["ingest", "https://example.org/book.pdf", "--out", str(out)]) == 1
    assert nothing_in(out)

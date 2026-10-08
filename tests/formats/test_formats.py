"""Every file format has a schema, and every example file passes it."""

from pathlib import Path

import pytest
import yaml

from unfold import jobs
from unfold.formats import FORMATS, FormatError, load_any, problems
from unfold.formats.episode import ScriptV1
from unfold.sources import Anchor, SourceDocument

EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "econ-supply-demand"
SCRIPT_V1 = """---
format: script/v1
episode: E01-supply-demand
segment: s3-equilibrium
voice: default
anchors:
  cross: [openstax-econ-2e-3-1#table-3-3]
  settle: []
---

[[cross]] They cross at one point.

[[settle]] The price moves toward the crossing point.
"""


def write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text)
    return path


@pytest.mark.parametrize(
    "name",
    [
        "source.yaml",
        "knowledge-map.yaml",
        "outline.yaml",
        "s3-equilibrium/script.md",
        "s3-equilibrium/storyboard.yaml",
    ],
)
def test_every_example_file_passes(name: str) -> None:
    assert problems(EXAMPLES / name) == []


def test_every_format_has_a_versioned_schema() -> None:
    assert set(FORMATS) == {
        "source/v0",
        "source/v1",
        "knowledge-map/v0",
        "job/v0",
        "series/v0",
        "series-plan/v0",
        "outline/v0",
        "script/v0",
        "script/v1",
        "storyboard/v0",
        "scene/v0",
        "ledger/v0",
    }


def test_a_missing_field_is_named_with_its_place(tmp_path: Path) -> None:
    outline = yaml.safe_load((EXAMPLES / "outline.yaml").read_text())
    del outline["segments"][1]["title"]

    errors = problems(write(tmp_path, "outline.yaml", yaml.safe_dump(outline)))

    assert errors == ["segments.1.title: Field required"]


def test_a_bad_value_is_named_with_its_place(tmp_path: Path) -> None:
    outline = yaml.safe_load((EXAMPLES / "outline.yaml").read_text())
    outline["segments"][0]["requires"] = ["price"]

    [error] = problems(write(tmp_path, "outline.yaml", yaml.safe_dump(outline)))

    assert error.startswith("segments.0.requires.0:")


def test_an_unknown_format_fails(tmp_path: Path) -> None:
    with pytest.raises(FormatError, match="poem/v9"):
        load_any(write(tmp_path, "poem.yaml", "format: poem/v9\n"))


def test_a_file_without_a_format_fails(tmp_path: Path) -> None:
    with pytest.raises(FormatError, match="no format"):
        load_any(write(tmp_path, "notes.yaml", "title: no format here\n"))


def test_a_script_v1_passes_and_reads_its_anchors(tmp_path: Path) -> None:
    script = load_any(write(tmp_path, "script.md", SCRIPT_V1))

    assert isinstance(script, ScriptV1)
    assert script.anchors == {
        "cross": ["openstax-econ-2e-3-1#table-3-3"],
        "settle": [],
    }


def test_a_script_v1_needs_an_anchor_entry_for_every_cue(tmp_path: Path) -> None:
    text = SCRIPT_V1.replace("  settle: []\n", "")

    [error] = problems(write(tmp_path, "script.md", text))

    assert "settle" in error


def test_an_ingested_source_document_passes(tmp_path: Path) -> None:
    doc = SourceDocument(
        "demo",
        "Demo",
        "textbook",
        "demo.pdf",
        {},
        {},
        [Anchor("p-1", "page", "Page 1")],
    )
    doc.rights = {
        "license": "CC BY 4.0",
        "owner": "",
        "attribution": "",
        "public_outputs": True,
    }
    doc.profile = {"format": "pdf", "size": {"pages": 1}, "quality": {"low": True}}
    doc.profile |= {"subject": "math", "needs": "cut"}

    assert problems(doc.save(tmp_path) / "source.yaml") == []


def test_job_records_pass_including_those_from_m2(tmp_path: Path) -> None:
    record = jobs.Record(key="k", model="sonnet", outcome="ok")
    record.save(tmp_path / "new.json")
    (tmp_path / "job.json").write_text(
        '{"key": "k", "model": "sonnet", "outcome": "ok"}'
    )

    assert problems(tmp_path / "new.json") == []
    assert problems(tmp_path / "job.json") == []


def test_a_series_file_and_a_plan(tmp_path: Path) -> None:
    series = "format: series/v0\nid: money\naudience: Adults.\nsources: [../s]\n"
    plan = """format: series-plan/v0
series: money
episodes:
  - id: episode-one
    title: One
    core_question: Why?
    concepts: [velocity]
"""

    assert problems(write(tmp_path, "series.yaml", series)) == []
    [error] = problems(write(tmp_path, "plan.yaml", plan))
    assert error.startswith("episodes.0.id:")

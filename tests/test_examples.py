"""The example files follow docs/formats.md, and their anchors resolve."""

from pathlib import Path

import pytest
import yaml

from unfold.anchors import unresolved
from unfold.script import load_script

EXAMPLES = sorted(
    (Path(__file__).resolve().parents[1] / "examples").glob("*/source.yaml")
)


def load(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


@pytest.fixture(params=EXAMPLES, ids=lambda p: p.parent.name)
def example(request: pytest.FixtureRequest) -> Path:
    return request.param.parent


def test_every_anchor_resolves(example: Path) -> None:
    manifest = load(example / "source.yaml")
    for name in ("knowledge-map.yaml", "outline.yaml"):
        assert unresolved(load(example / name), [manifest]) == [], name


def test_concepts_require_only_known_concepts(example: Path) -> None:
    concepts = load(example / "knowledge-map.yaml")["concepts"]
    assert isinstance(concepts, list)
    known = {concept["id"] for concept in concepts}
    for concept in concepts:
        assert set(concept["requires"]) <= known, concept["id"]


def test_the_knowledge_map_is_substantial(example: Path) -> None:
    concepts = load(example / "knowledge-map.yaml")["concepts"]
    assert isinstance(concepts, list)
    assert len(concepts) >= 10


def test_every_cue_has_a_storyboard_entry(example: Path) -> None:
    for script_path in example.glob("*/script.md"):
        cues = [beat.cue for beat in load_script(script_path).beats]
        entries = load(script_path.parent / "storyboard.yaml")["entries"]
        assert isinstance(entries, list)
        assert cues == [entry["cue"] for entry in entries], script_path.parent.name

"""Source documents: one format for every source family.

A source document is a folder with two files. `source.yaml` is the manifest, in
the source/v1 format. `document.md` holds the clean text, where a line such as
`<!-- anchor: p-3 -->` starts each anchored block. `docs/formats.md` and
`specs/003-source-understanding/data-model.md` describe both.
"""

import datetime
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

FORMAT = "source/v1"
MANIFEST = "source.yaml"
TEXT = "document.md"
ANCHOR_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MARKER = re.compile(r"^<!-- anchor: ([a-z0-9][a-z0-9-]*) -->$", re.MULTILINE)


@dataclass(frozen=True)
class Anchor:
    """One place in a source: a page, slide, section, timestamp, or scan."""

    id: str
    kind: str
    title: str
    text: str = ""

    def __post_init__(self) -> None:
        if not ANCHOR_ID.match(self.id):
            raise ValueError(
                f"bad anchor id {self.id!r}: use lower-case letters, digits, and -"
            )


def _today() -> str:
    return datetime.date.today().isoformat()


@dataclass
class SourceDocument:
    """A source after ingestion: its manifest and its anchored text."""

    id: str
    title: str
    family: str
    origin: str
    rights: dict[str, object]
    profile: dict[str, object] = field(default_factory=dict)
    anchors: list[Anchor] = field(default_factory=list)
    retrieved: str = field(default_factory=_today)

    def manifest(self) -> dict[str, object]:
        return {
            "format": FORMAT,
            "id": self.id,
            "title": self.title,
            "family": self.family,
            "origin": self.origin,
            "retrieved": self.retrieved,
            "rights": self.rights,
            "profile": self.profile,
            "anchors": [
                {"id": a.id, "kind": a.kind, "title": a.title} for a in self.anchors
            ],
        }

    def text(self) -> str:
        """The document text, with a marker before each anchored block."""
        blocks = [
            f"<!-- anchor: {a.id} -->\n## {a.title}\n\n{a.text.strip()}\n"
            for a in self.anchors
        ]
        return "\n".join(blocks)

    def save(self, root: Path) -> Path:
        """Write the folder root/<id>, and return it. Each file is written whole."""
        folder = root / self.id
        folder.mkdir(parents=True, exist_ok=True)
        manifest = yaml.safe_dump(self.manifest(), sort_keys=False, allow_unicode=True)
        for name, content in ((MANIFEST, manifest), (TEXT, self.text())):
            partial = folder / f".{name}.partial"
            partial.write_text(content, encoding="utf-8")
            partial.replace(folder / name)
        return folder


def load(folder: Path) -> SourceDocument:
    """Read a source document folder."""
    manifest = yaml.safe_load((folder / MANIFEST).read_text(encoding="utf-8"))
    if manifest.get("format") != FORMAT:
        raise ValueError(f"{folder} is not a {FORMAT} source document")
    texts = _blocks((folder / TEXT).read_text(encoding="utf-8"))
    anchors = [
        Anchor(a["id"], a["kind"], a["title"], texts.get(a["id"], ""))
        for a in manifest.get("anchors") or []
    ]
    return SourceDocument(
        id=manifest["id"],
        title=manifest["title"],
        family=manifest["family"],
        origin=manifest["origin"],
        rights=manifest.get("rights") or {},
        profile=manifest.get("profile") or {},
        anchors=anchors,
        retrieved=str(manifest["retrieved"]),
    )


def _blocks(text: str) -> dict[str, str]:
    """Map each anchor id to its block's text, without the block's heading."""
    found: dict[str, str] = {}
    marks = list(MARKER.finditer(text))
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        block = text[mark.end() : end].strip("\n")
        lines = block.split("\n")
        if lines and lines[0].startswith("## "):
            lines = lines[1:]
        found[mark.group(1)] = "\n".join(lines).strip()
    return found

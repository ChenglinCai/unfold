"""Scripts: the narration of one segment, split into beats at cues.

A script is Markdown with YAML front matter. Each beat is a paragraph that
starts with a cue in double square brackets:

    [[query]] A new point arrives. How would you label it?

`docs/formats.md` describes the format in full.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

CUE = re.compile(r"^\[\[([a-z0-9][a-z0-9-]*)\]\]\s*(.*)$", re.DOTALL)


class ScriptError(ValueError):
    """A script does not follow the format in docs/formats.md."""


@dataclass(frozen=True)
class Beat:
    """One short piece of narration, with the cue that starts its visual."""

    cue: str
    text: str


@dataclass(frozen=True)
class Script:
    """The front matter and the beats of one segment's narration."""

    meta: dict[str, object]
    beats: list[Beat]

    def anchors(self) -> dict[str, list[str]]:
        """Each cue's anchors, from script/v1 front matter. script/v0 lists none."""
        found = self.meta.get("anchors")
        mapping = found if isinstance(found, dict) else {}
        return {beat.cue: list(mapping.get(beat.cue) or []) for beat in self.beats}

    def __getitem__(self, cue: str) -> Beat:
        for beat in self.beats:
            if beat.cue == cue:
                return beat
        raise KeyError(cue)


def parse_script(text: str) -> Script:
    """Split a script into its front matter and its beats."""
    meta, body = _split_front_matter(text)
    beats: list[Beat] = []
    for paragraph in re.split(r"\n\s*\n", body.strip()):
        match = CUE.match(paragraph.strip())
        if match is None:
            raise ScriptError(f"beat has no cue: {paragraph.strip()[:60]!r}")
        cue, narration = match.groups()
        if any(beat.cue == cue for beat in beats):
            raise ScriptError(f"cue {cue!r} appears twice")
        beats.append(Beat(cue, " ".join(narration.split())))
    return Script(meta, beats)


def load_script(path: Path) -> Script:
    """Read and parse a script file."""
    return parse_script(path.read_text(encoding="utf-8"))


def _split_front_matter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        raise ScriptError("a script must start with YAML front matter")
    _, front, body = text.split("---\n", 2)
    meta = yaml.safe_load(front) or {}
    if not isinstance(meta, dict):
        raise ScriptError("the front matter must be a mapping")
    return meta, body

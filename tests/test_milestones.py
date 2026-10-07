"""Every milestone gate is well formed, and no gate passes without evidence."""

import json
from pathlib import Path

MILESTONES = Path(__file__).resolve().parents[1] / "docs" / "milestones.json"


def test_every_passing_gate_has_evidence() -> None:
    data = json.loads(MILESTONES.read_text())
    seen: set[str] = set()
    for milestone in data["milestones"]:
        for gate in milestone["gates"]:
            assert gate["id"] not in seen, f"duplicate gate {gate['id']}"
            seen.add(gate["id"])
            assert gate["id"].startswith(milestone["id"] + ".")
            assert gate["check"].strip()
            if gate["passes"]:
                assert gate.get("evidence", "").strip(), f"{gate['id']} has no evidence"

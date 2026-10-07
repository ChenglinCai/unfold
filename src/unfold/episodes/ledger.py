"""The ledger: what each built episode of a series establishes.

Code writes it after each episode. The next episode's outline step sees it,
so it can build on earlier ideas and call back to earlier visuals.
"""

from pathlib import Path

import yaml

from unfold.formats.episode import OutlineV0
from unfold.formats.series import LedgerEntry, LedgerV0

LEDGER = "ledger.yaml"


def build_ledger(series: str, outlines: list[OutlineV0]) -> LedgerV0:
    entries = [
        LedgerEntry(
            episode=outline.episode,
            title=outline.title,
            segments=[segment.id for segment in outline.segments],
            establishes=[
                i for segment in outline.segments for i in segment.establishes
            ],
        )
        for outline in outlines
    ]
    return LedgerV0(format="ledger/v0", series=series, episodes=entries)


def ledger_text(ledger: LedgerV0) -> str:
    return yaml.safe_dump(
        ledger.model_dump(mode="json"), sort_keys=False, allow_unicode=True, width=100
    )


def write_ledger(folder: Path, ledger: LedgerV0) -> Path:
    path = folder / LEDGER
    path.write_text(ledger_text(ledger), encoding="utf-8")
    return path

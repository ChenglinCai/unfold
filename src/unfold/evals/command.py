"""The `unfold eval` subcommand.

`specs/004-text-generation/contracts/cli.md` describes its contract.
"""

import argparse
import json
import sys
from pathlib import Path

from unfold.evals import (
    CHECKS,
    Verdict,
    count_flags,
    custom_share,
    evaluate,
    share_line,
)


def add_eval_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    command = commands.add_parser("eval", help="Run the binary checks on built series.")
    command.add_argument("--format", choices=["text", "json"], default="text")
    command.add_argument(
        "--failures", action="store_true", help="List each failing file."
    )
    command.add_argument("series", nargs="+", metavar="SERIES")
    command.set_defaults(run=run_eval)


def run_eval(args: argparse.Namespace) -> int:
    verdicts: list[Verdict] = []
    flagged = beats = custom = entries = 0
    for raw in args.series:
        folder = Path(raw)
        if not (folder / "plan.yaml").is_file():
            print(f"unfold eval: {folder} is not a built series", file=sys.stderr)
            return 2
        verdicts += evaluate(folder)
        found, total = count_flags(folder)
        flagged, beats = flagged + found, beats + total
        extra, scene_beats = custom_share(folder)
        custom, entries = custom + extra, entries + scene_beats
    rows = []
    for check in CHECKS:
        mine = [v for v in verdicts if v.check == check]
        passed = sum(v.passed for v in mine)
        rate = round(100 * passed / len(mine)) if mine else None
        rows.append(
            {"check": check, "passed": passed, "total": len(mine), "rate": rate}
        )
    failures = [
        {"check": v.check, "path": str(v.subject)} for v in verdicts if not v.passed
    ]
    if args.format == "json":
        flags = {"flagged_beats": flagged, "beats": beats}
        flags |= {"custom_beats": custom, "scene_beats": entries}
        print(json.dumps({"checks": rows, "failures": failures, **flags}, indent=2))
        return 0
    for row in rows:
        rate = "n/a" if row["rate"] is None else f"{row['rate']}%"
        print(f"{row['check']:30} {row['passed']:>3}/{row['total']:<3} {rate}")
    print(f"flagged beats, for the maintainer to review: {flagged} of {beats}")
    print(share_line(custom, entries))
    if args.failures:
        for failure in failures:
            print(f"  fails {failure['check']}: {failure['path']}")
    return 0

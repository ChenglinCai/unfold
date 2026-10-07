"""The `unfold check` subcommand.

`specs/004-text-generation/contracts/cli.md` describes its contract.
"""

import argparse
import json
from pathlib import Path

import yaml

from unfold.formats import FormatError, problems

# Folders that hold renders or caches, never files with a format.
SKIP = {"media", "__pycache__", ".voice-cache"}


def add_check_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    check = commands.add_parser("check", help="Check files against their schemas.")
    check.add_argument("--format", choices=["text", "json"], default="text")
    check.add_argument("paths", nargs="+", metavar="PATH")
    check.set_defaults(run=run_check)


def wanted(path: Path) -> bool:
    if path.suffix in {".yaml", ".yml"} or path.name in {"script.md", "job.json"}:
        return True
    return path.suffix == ".json" and "records" in path.parts


def files_in(path: Path) -> list[Path]:
    if not path.is_dir():
        return [path]
    return sorted(
        found
        for found in path.rglob("*")
        if found.is_file()
        and wanted(found)
        and not any(
            part in SKIP or part.startswith(".")
            for part in found.relative_to(path).parts
        )
    )


def run_check(args: argparse.Namespace) -> int:
    files = [found for raw in args.paths for found in files_in(Path(raw))]
    found: list[dict[str, str]] = []
    unknown: list[dict[str, str]] = []
    for path in files:
        try:
            found += [{"path": str(path), "problem": p} for p in problems(path)]
        except (yaml.YAMLError, json.JSONDecodeError) as error:
            found.append({"path": str(path), "problem": f"cannot parse: {error}"})
        except (FormatError, OSError) as error:
            unknown.append({"path": str(path), "problem": str(error)})
    if args.format == "json":
        print(json.dumps({"files": len(files), "problems": found, "unknown": unknown}))
    else:
        for item in [*unknown, *found]:
            print(f"{item['path']}: {item['problem']}")
        print(f"{count(len(files), 'file')}, {count(len(found), 'problem')}")
    return 2 if unknown else 1 if found else 0


def count(number: int, noun: str) -> str:
    return f"{number} {noun}" if number == 1 else f"{number} {noun}s"

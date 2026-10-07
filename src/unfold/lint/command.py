"""The `unfold lint` subcommand, as `specs/002-language/contracts/cli.md` describes."""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import yaml

from unfold.lint import lint_text
from unfold.lint.rules import ERROR, Finding

DEFAULT_TERMS = Path("docs/terms.yaml")


def add_lint_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    lint = commands.add_parser(
        "lint", help="Check prose against the Narration Standard."
    )
    lint.add_argument(
        "--profile", choices=["written", "spoken", "strict"], default="written"
    )
    lint.add_argument("--format", choices=["text", "json"], default="text")
    lint.add_argument(
        "--fix", action="store_true", help="Rewrite mechanical findings in place."
    )
    lint.add_argument("--terms", help="The replacement list. Default: docs/terms.yaml.")
    lint.add_argument("paths", nargs="+", metavar="PATH")
    lint.set_defaults(run=run_lint)


def load_terms(path: Path | None) -> dict[str, str]:
    """Read the replacement list: each term to avoid, and the term to use."""
    if path is None:
        if not DEFAULT_TERMS.is_file():
            return {}
        path = DEFAULT_TERMS
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {
        str(avoid): str(entry["prefer"] if isinstance(entry, dict) else entry)
        for avoid, entry in data.items()
    }


def expand(paths: list[str]) -> list[Path]:
    """Turn each directory into the Markdown files inside it."""
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        files.extend(sorted(path.rglob("*.md")) if path.is_dir() else [path])
    return files


def lint_file(path: Path, profile: str, terms: dict[str, str]) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        message = f"Cannot read the file: {error}."
        return [Finding("N900", "unreadable-file", ERROR, str(path), 1, "", message)]
    return lint_text(text, profile, str(path), terms)


def plural(count: int, noun: str) -> str:
    return f"{count} {noun}" + ("" if count == 1 else "s")


def run_lint(args: argparse.Namespace) -> int:
    missing = [raw for raw in args.paths if not Path(raw).exists()]
    if missing:
        print(f"unfold lint: no such path: {', '.join(missing)}", file=sys.stderr)
        return 2
    if args.fix:
        print("unfold lint: --fix is not available yet.", file=sys.stderr)
        return 2
    terms = load_terms(Path(args.terms) if args.terms else None)
    files = expand(args.paths)
    findings = [f for path in files for f in lint_file(path, args.profile, terms)]
    errors = sum(f.severity == ERROR for f in findings)
    warnings = len(findings) - errors
    if args.format == "json":
        report = {
            "profile": args.profile,
            "findings": [asdict(f) for f in findings],
            "errors": errors,
            "warnings": warnings,
        }
        print(json.dumps(report, indent=2))
    else:
        for f in findings:
            where = f"{f.path}:{f.line}: {f.severity} {f.rule} {f.name}"
            print(f'{where}: {f.message} "{f.excerpt}"')
        summary = f"{plural(errors, 'error')}, {plural(warnings, 'warning')}"
        print(f"{summary} in {plural(len(files), 'file')}")
    return 1 if errors else 0

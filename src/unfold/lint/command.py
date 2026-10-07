"""The `unfold lint` subcommand, as `specs/002-language/contracts/cli.md` describes."""

import argparse


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


def run_lint(args: argparse.Namespace) -> int:
    raise NotImplementedError("T008 implements this")

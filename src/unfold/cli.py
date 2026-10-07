"""The `unfold` command. `docs/` describes each subcommand's contract."""

import argparse
import sys
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="unfold",
        description="Turn learning material into explainer videos.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    from unfold.build.command import add_build_command
    from unfold.check import add_check_command
    from unfold.lint.command import add_lint_command
    from unfold.sources.command import add_ingest_command
    from unfold.understand.command import add_understand_command

    add_build_command(commands)
    add_check_command(commands)
    add_lint_command(commands)
    add_ingest_command(commands)
    add_understand_command(commands)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())

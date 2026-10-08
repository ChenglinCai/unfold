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
    from unfold.doctor import add_doctor_command
    from unfold.evals.command import add_eval_command
    from unfold.lint.command import add_lint_command
    from unfold.pages import add_page_commands
    from unfold.sources.command import add_ingest_command
    from unfold.understand.command import add_understand_command
    from unfold.visuals.command import add_render_command

    add_build_command(commands)
    add_check_command(commands)
    add_doctor_command(commands)
    add_eval_command(commands)
    add_lint_command(commands)
    add_page_commands(commands)
    add_render_command(commands)
    add_ingest_command(commands)
    add_understand_command(commands)
    serve = commands.add_parser(
        "mcp", help="Serve unfold's tools to Claude Code over MCP."
    )
    serve.set_defaults(run=run_mcp)
    return parser


def run_mcp(args: argparse.Namespace) -> int:
    try:
        from unfold.mcp_server import serve
    except ImportError:
        print(
            "unfold mcp: add the mcp extra first: uv sync --extra mcp", file=sys.stderr
        )
        return 2
    serve()
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())

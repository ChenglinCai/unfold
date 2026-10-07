"""The `unfold build` subcommand.

`specs/004-text-generation/contracts/cli.md` describes its contract.
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from unfold import jobs
from unfold.build import RETRIES
from unfold.build.graph import STEPS, SeriesError, build

# Tests replace the runner, so that no test calls a model.
RUNNER: jobs.Runner | None = None


def add_build_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    command = commands.add_parser(
        "build", help="Write a series' plan, outlines, scripts, and storyboards."
    )
    command.add_argument("series", metavar="SERIES", help="A folder with series.yaml.")
    command.add_argument("--until", choices=STEPS, default="storyboard")
    command.add_argument("--model", help="Override the series file's model.")
    command.add_argument("--retries", type=int, default=RETRIES)
    command.set_defaults(run=run_build)


def run_build(args: argparse.Namespace) -> int:
    if args.retries < 0:
        return fail("--retries must be 0 or more", 2)
    runner = RUNNER or jobs.run_claude
    try:
        result = build(Path(args.series), runner, args.until, args.model, args.retries)
    except SeriesError as error:
        return fail(str(error), 2)
    except jobs.CanaryError as error:
        return fail(f"{error}. No other job ran.", 3)
    for line in result.lines:
        print(f"{line.status:8} {line.output}")
    counts = Counter(line.status for line in result.lines)
    print(
        f"{counts['written']} written, {counts['reused']} reused, {counts['failed']} failed"
    )
    return 1 if result.failed else 0


def fail(message: str, code: int) -> int:
    print(f"unfold build: {message}", file=sys.stderr)
    return code

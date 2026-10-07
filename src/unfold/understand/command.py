"""The `unfold understand` subcommand.

`specs/003-source-understanding/contracts/cli.md` describes its contract.
"""

import argparse
import sys
from pathlib import Path

from unfold import jobs
from unfold.sources import load
from unfold.understand import DEFAULT_MODEL, RETRIES, understand

# Tests replace the runner, so that no test calls a model.
RUNNER: jobs.Runner | None = None


def add_understand_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    command = commands.add_parser(
        "understand", help="Write a knowledge map and study notes for a source."
    )
    command.add_argument("folder", metavar="DIR", help="A folder from unfold ingest.")
    command.add_argument("--model", default=DEFAULT_MODEL)
    command.add_argument("--retries", type=int, default=RETRIES)
    command.set_defaults(run=run_understand)


def run_understand(args: argparse.Namespace) -> int:
    folder = Path(args.folder)
    if args.retries < 0:
        return fail("--retries must be 0 or more", 2)
    try:
        load(folder)
    except (OSError, ValueError, KeyError) as problem:
        return fail(f"{folder} is not a source document: {problem}", 2)
    runner = RUNNER or jobs.run_claude
    result = understand(folder, runner=runner, model=args.model, retries=args.retries)
    record = result.record
    if result.reused:
        print(f"{result.folder}: reused the saved result")
        return 0
    if record.outcome == "ok":
        print(
            f"{result.folder}: written in {record.attempts} tries, with "
            f"{record.input_tokens} input and {record.output_tokens} output tokens, "
            f"in {record.seconds} seconds"
        )
        return 0
    problems = "\n".join(f"  {error}" for error in record.errors)
    return fail(f"{folder}: failed after {record.attempts} tries:\n{problems}", 1)


def fail(message: str, code: int) -> int:
    print(f"unfold understand: {message}", file=sys.stderr)
    return code

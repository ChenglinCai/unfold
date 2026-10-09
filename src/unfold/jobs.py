"""Model jobs: headless Claude runs with no tools, saved under a key, with a record.

A job runs `claude -p` in an empty temporary folder. It gets no tools, no
settings, and no MCP servers, so text inside a source can change only the job's
own reply, and code checks every reply. `specs/003-source-understanding/research.md`
gives the reasons. M4 grows this module into the build graph.
"""

import dataclasses
import hashlib
import json
import os
import subprocess
import tempfile
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

TIMEOUT_SECONDS = 900
# These variables choose how to reach the model, so a job keeps them.
KEEP = ("CLAUDE_CODE_USE_", "CLAUDE_CODE_OAUTH_TOKEN")


class JobError(RuntimeError):
    """The job itself failed, before any check could read its reply."""


class CanaryError(RuntimeError):
    """The runner failed its canary, so the build stops before any real job.

    It is not a JobError, so no job loop mistakes it for one failed job.
    """


# The canary: a tiny job with a known answer, which proves the login, the usage
# limit, and structured output before a build spends anything.
CANARY_MODEL = "haiku"
CANARY_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {"answer": {"type": "integer"}},
    "required": ["answer"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Reply:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    # The structured output, when the job asked for a schema.
    data: dict[str, object] | None = None
    # The model turns inside one call. Usage sums over them, so more turns cost more.
    turns: int = 1


class Runner(Protocol):
    def __call__(
        self,
        prompt: str,
        *,
        system: str,
        model: str,
        schema: Mapping[str, object] | None = None,
    ) -> Reply: ...


def command(
    model: str, system: str, schema: Mapping[str, object] | None = None
) -> list[str]:
    """The `claude -p` command. A schema asks for output that matches it."""
    structured = (
        ["--json-schema", json.dumps(schema, sort_keys=True, separators=(",", ":"))]
        if schema is not None
        else []
    )
    return [
        "claude",
        "-p",
        "--model",
        model,
        "--tools",
        "",
        "--setting-sources",
        "",
        "--strict-mcp-config",
        "--no-session-persistence",
        "--output-format",
        "json",
        "--system-prompt",
        system,
        *structured,
    ]


def environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Drop the variables that tie a process to a running Claude Code session."""
    return {
        name: value
        for name, value in environ.items()
        if name != "CLAUDECODE"
        and (not name.startswith("CLAUDE_CODE_") or name.startswith(KEEP))
    }


def parse(stdout: str, seconds: float) -> Reply:
    """Read the JSON that `claude -p --output-format json` prints."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise JobError(f"the job printed no JSON: {stdout[:200]!r}") from error
    if data.get("is_error") or data.get("subtype") != "success":
        raise JobError(f"the job failed: {str(data.get('result'))[:200]}")
    usage = data.get("usage") or {}
    input_tokens = sum(
        int(usage.get(name) or 0)
        for name in (
            "input_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
        )
    )
    structured = data.get("structured_output")
    return Reply(
        str(data["result"]),
        input_tokens,
        int(usage.get("output_tokens") or 0),
        seconds,
        structured if isinstance(structured, dict) else None,
        int(data.get("num_turns") or 1),
    )


def run_claude(
    prompt: str,
    *,
    system: str,
    model: str,
    schema: Mapping[str, object] | None = None,
) -> Reply:
    """Run one job, with the prompt on stdin, in a new empty folder."""
    with tempfile.TemporaryDirectory(prefix="unfold-job-") as empty:
        started = time.monotonic()
        try:
            result = subprocess.run(
                command(model, system, schema),
                input=prompt,
                capture_output=True,
                text=True,
                cwd=empty,
                env=environment(os.environ),
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise JobError(f"could not run claude: {error}") from error
    if result.returncode != 0 and not result.stdout.strip():
        raise JobError(f"claude exited with {result.returncode}: {result.stderr[:200]}")
    return parse(result.stdout, round(time.monotonic() - started, 1))


def key(*parts: str) -> str:
    """Hash the parts, so a saved result is reused only when every part matches."""
    digest = hashlib.sha256()
    for part in parts:
        encoded = part.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big") + encoded)
    return digest.hexdigest()


@dataclass
class Record:
    """What one job did: its model, tries, tokens, time, and outcome."""

    key: str
    model: str
    attempts: int = 0
    turns: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0
    outcome: str = "running"
    errors: list[str] = field(default_factory=list)
    # The errors of each failed try, in order.
    tries: list[list[str]] = field(default_factory=list)
    # The data of the last reply, kept when every try fails, to show what went wrong.
    last_reply: dict[str, object] | None = None
    format: str = "job/v0"

    def add(self, reply: Reply) -> None:
        self.attempts += 1
        self.turns += reply.turns
        self.input_tokens += reply.input_tokens
        self.output_tokens += reply.output_tokens
        self.seconds = round(self.seconds + reply.seconds, 1)

    def save(self, path: Path) -> None:
        partial = path.with_name(f".{path.name}.partial")
        fields = dataclasses.asdict(self)
        ordered = {"format": fields.pop("format"), **fields}
        partial.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
        partial.replace(path)

    @classmethod
    def load(cls, path: Path) -> "Record | None":
        if not path.is_file():
            return None
        return cls(**json.loads(path.read_text(encoding="utf-8")))


def canary(runner: Runner) -> Reply:
    """Ask "What is 2 plus 3?" and expect 5. Raise CanaryError otherwise."""
    try:
        reply = runner(
            "What is 2 plus 3?",
            system="Answer with the number only.",
            model=CANARY_MODEL,
            schema=CANARY_SCHEMA,
        )
    except JobError as error:
        raise CanaryError(f"the canary job failed: {error}") from error
    answer = (reply.data or {}).get("answer")
    if answer != 5:
        raise CanaryError(f"the canary expected 5, and got {answer!r}")
    return reply

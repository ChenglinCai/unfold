"""The build graph's jobs: ask for data, check it, retry, save, and log each call.

Each job writes one output file. Its key hashes the step's prompt, the request,
the model, and the reply's JSON Schema. The request holds the contents of every
input, so a changed input changes the key, and a matching key means reuse.
"""

import datetime
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ValidationError

from unfold import jobs
from unfold.formats import describe

RETRIES = 3


@dataclass(frozen=True)
class Job:
    step: str
    output: Path
    record: Path
    system: str
    request: str
    reply: type[BaseModel]
    model: str
    check: Callable[[BaseModel], list[str]]
    render: Callable[[BaseModel], str]

    @property
    def schema(self) -> dict[str, object]:
        return portable(self.reply.model_json_schema())

    @property
    def key(self) -> str:
        schema = json.dumps(self.schema, sort_keys=True)
        return jobs.key(self.system, self.request, self.model, schema)


# Keywords that Pydantic writes but JSON Schema lacks. The runner checks schemas
# strictly, so a job's schema drops them. The union still holds, because each
# variant pins its own `component` value.
NONSTANDARD = {"discriminator"}


def portable(schema: object) -> dict[str, object]:
    """A copy of a schema without the keywords that JSON Schema lacks."""

    def clean(node: object) -> object:
        if isinstance(node, dict):
            return {k: clean(v) for k, v in node.items() if k not in NONSTANDARD}
        if isinstance(node, list):
            return [clean(item) for item in node]
        return node

    cleaned = clean(schema)
    assert isinstance(cleaned, dict)
    return cleaned


@dataclass(frozen=True)
class Outcome:
    job: Job
    record: jobs.Record
    reused: bool


def run_job(
    job: Job, runner: jobs.Runner, retries: int = RETRIES, log: Path | None = None
) -> Outcome:
    """Reuse the saved result, or ask until the reply passes, at most retries + 1 times."""
    saved = jobs.Record.load(job.record)
    if (
        saved
        and saved.key == job.key
        and saved.outcome == "ok"
        and job.output.is_file()
    ):
        return Outcome(job, saved, reused=True)
    record = jobs.Record(key=job.key, model=job.model)
    ask = job.request
    last: jobs.Reply | None = None
    for attempt in range(1, retries + 2):
        try:
            reply = runner(ask, system=job.system, model=job.model, schema=job.schema)
        except jobs.JobError as error:
            record.errors = [str(error)]
            log_call(log, job, record, attempt, None, final=True)
            break
        record.add(reply)
        last = reply
        errors, text = evaluate(job, reply)
        record.errors = errors
        if not errors:
            record.outcome = "ok"
            write_file(job.output, text)
            log_call(log, job, record, attempt, reply)
            break
        record.tries.append(errors)
        log_call(log, job, record, attempt, reply, final=attempt == retries + 1)
        ask = retry_request(job.request, reply, errors)
    if record.outcome != "ok":
        record.outcome = "failed"
        record.last_reply = last.data if last is not None else None
    job.record.parent.mkdir(parents=True, exist_ok=True)
    record.save(job.record)
    return Outcome(job, record, reused=False)


def evaluate(job: Job, reply: jobs.Reply) -> tuple[list[str], str]:
    """Validate a reply against its schema, then check its meaning."""
    if reply.data is None:
        return ["the reply held no structured output"], ""
    try:
        parsed = job.reply.model_validate(reply.data)
    except ValidationError as error:
        return [describe(detail) for detail in error.errors()], ""
    errors = job.check(parsed)
    return errors, "" if errors else job.render(parsed)


def retry_request(request: str, reply: jobs.Reply, errors: list[str]) -> str:
    answer = json.dumps(reply.data, indent=1) if reply.data is not None else reply.text
    problems = "\n".join(f"- {error}" for error in errors)
    return (
        f"{request}\n\n<last-answer>\n{answer}\n</last-answer>\n\n"
        f"Your last answer failed these checks:\n{problems}\n\n"
        "Answer again in full, with every problem fixed."
    )


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f".{path.name}.partial")
    partial.write_text(text, encoding="utf-8")
    partial.replace(path)


def log_call(
    log: Path | None,
    job: Job,
    record: jobs.Record,
    attempt: int,
    reply: jobs.Reply | None,
    final: bool = False,
) -> None:
    """Append one line about one model call to the call log."""
    if log is None:
        return
    outcome = "ok" if record.outcome == "ok" else "failed" if final else "retry"
    line = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "step": job.step,
        "output": str(job.output),
        "key": job.key,
        "model": job.model,
        "attempt": attempt,
        "input_tokens": reply.input_tokens if reply else 0,
        "output_tokens": reply.output_tokens if reply else 0,
        "seconds": reply.seconds if reply else 0,
        "outcome": outcome,
        "errors": record.errors,
    }
    append_log(log, line)


def append_log(log: Path | None, line: dict[str, object]) -> None:
    if log is None:
        return
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(line) + "\n")

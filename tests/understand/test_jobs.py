"""The job runner gives the model no tools and keeps a record of each job."""

import json
import subprocess
from pathlib import Path

import pytest

from unfold import jobs

REPLY = {
    "type": "result",
    "subtype": "success",
    "is_error": False,
    "result": "<knowledge-map>\nformat: knowledge-map/v0\n</knowledge-map>",
    "usage": {
        "input_tokens": 12,
        "cache_creation_input_tokens": 1000,
        "cache_read_input_tokens": 300,
        "output_tokens": 450,
    },
}


def test_the_command_gives_the_model_no_tools_settings_or_servers() -> None:
    command = jobs.command("sonnet", "Be exact.")

    assert command[:2] == ["claude", "-p"]
    pairs = dict(zip(command, [*command[1:], None], strict=True))
    assert pairs["--tools"] == ""
    assert pairs["--setting-sources"] == ""
    assert pairs["--model"] == "sonnet"
    assert pairs["--output-format"] == "json"
    assert pairs["--system-prompt"] == "Be exact."
    assert "--strict-mcp-config" in command
    assert "--no-session-persistence" in command


def test_a_job_does_not_join_the_session_that_started_it() -> None:
    environment = jobs.environment(
        {
            "PATH": "/usr/bin",
            "CLAUDECODE": "1",
            "CLAUDE_CODE_SESSION_ID": "abc",
            "CLAUDE_CODE_MESSAGING_SOCKET": "/tmp/s.sock",
            "CLAUDE_CODE_USE_BEDROCK": "1",
            "CLAUDE_CODE_OAUTH_TOKEN": "token",
        }
    )

    assert environment == {
        "PATH": "/usr/bin",
        "CLAUDE_CODE_USE_BEDROCK": "1",
        "CLAUDE_CODE_OAUTH_TOKEN": "token",
    }


def test_parse_reads_the_text_and_every_kind_of_token() -> None:
    reply = jobs.parse(json.dumps(REPLY), seconds=2.5)

    assert reply.text.startswith("<knowledge-map>")
    assert (reply.input_tokens, reply.output_tokens) == (1312, 450)
    assert reply.seconds == 2.5


@pytest.mark.parametrize(
    "stdout", ["not json", json.dumps({**REPLY, "is_error": True, "result": "limit"})]
)
def test_parse_raises_on_a_failed_job(stdout: str) -> None:
    with pytest.raises(jobs.JobError):
        jobs.parse(stdout, seconds=1.0)


def test_run_claude_runs_in_an_empty_folder_with_the_prompt_on_stdin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    def fake_run(
        command: list[str], **options: object
    ) -> subprocess.CompletedProcess[str]:
        cwd = Path(str(options["cwd"]))
        seen.update(options, empty=not any(cwd.iterdir()), command=command)
        return subprocess.CompletedProcess(command, 0, json.dumps(REPLY), "")

    monkeypatch.setattr(jobs.subprocess, "run", fake_run)
    monkeypatch.setenv("CLAUDECODE", "1")

    reply = jobs.run_claude("Read this.", system="Be exact.", model="sonnet")

    assert reply.output_tokens == 450
    assert seen["input"] == "Read this."
    assert seen["empty"] is True
    environment = seen["env"]
    assert isinstance(environment, dict)
    assert "CLAUDECODE" not in environment


def test_the_key_changes_when_any_part_changes() -> None:
    base = jobs.key("prompt", "text", "sonnet")

    assert jobs.key("prompt", "text", "sonnet") == base
    assert jobs.key("prompt 2", "text", "sonnet") != base
    assert jobs.key("prompt", "text", "opus") != base
    assert jobs.key("prompttext", "", "sonnet") != jobs.key("prompt", "text", "sonnet")


def test_a_record_sums_its_attempts_and_round_trips(tmp_path: Path) -> None:
    record = jobs.Record(key="k", model="sonnet")
    record.add(jobs.Reply("a", 100, 10, 1.5))
    record.add(jobs.Reply("b", 200, 20, 2.0))
    record.outcome = "ok"
    path = tmp_path / "job.json"

    record.save(path)

    assert jobs.Record.load(path) == record
    assert (record.attempts, record.input_tokens, record.output_tokens) == (2, 300, 30)
    assert jobs.Record.load(tmp_path / "missing.json") is None

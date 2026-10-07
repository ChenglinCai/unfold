"""The job loop: ask for data, check it, retry with the errors, and save the result."""

import json
from pathlib import Path

from pydantic import BaseModel

from unfold import jobs
from unfold.build import Job, run_job


class Answer(BaseModel):
    words: list[str]


def check(reply: BaseModel) -> list[str]:
    assert isinstance(reply, Answer)
    return [f"unknown word: {w}" for w in reply.words if w not in {"alpha", "beta"}]


def render(reply: BaseModel) -> str:
    assert isinstance(reply, Answer)
    return "\n".join(reply.words) + "\n"


GOOD: dict[str, object] = {"words": ["alpha", "beta"]}
BAD: dict[str, object] = {"words": ["alpha", "gamma"]}


class FakeRunner:
    """Returns its replies in order as structured output."""

    def __init__(self, *replies: dict[str, object] | None) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[str, object]] = []

    def __call__(
        self, prompt: str, *, system: str, model: str, schema: object = None
    ) -> jobs.Reply:
        self.calls.append((prompt, schema))
        assert self.replies, "the job called the model more often than expected"
        data = self.replies.pop(0)
        return jobs.Reply(json.dumps(data), 10, 5, 0.5, data)


def make_job(tmp_path: Path, request: str = "Name two words.") -> Job:
    return Job(
        step="demo",
        output=tmp_path / "out.txt",
        record=tmp_path / "records" / "out.txt.json",
        system="Be exact.",
        request=request,
        reply=Answer,
        model="sonnet",
        check=check,
        render=render,
    )


def test_a_good_reply_writes_the_output_and_a_record(tmp_path: Path) -> None:
    runner = FakeRunner(GOOD)

    outcome = run_job(make_job(tmp_path), runner)

    assert (outcome.record.outcome, outcome.reused) == ("ok", False)
    assert (tmp_path / "out.txt").read_text() == "alpha\nbeta\n"
    assert jobs.Record.load(tmp_path / "records" / "out.txt.json") == outcome.record
    assert runner.calls[0][1] == Answer.model_json_schema()


def test_a_failed_check_retries_with_its_errors(tmp_path: Path) -> None:
    runner = FakeRunner(BAD, GOOD)

    outcome = run_job(make_job(tmp_path), runner)

    assert (outcome.record.outcome, outcome.record.attempts) == ("ok", 2)
    assert outcome.record.tries == [["unknown word: gamma"]]
    assert "unknown word: gamma" in runner.calls[1][0]


def test_four_failures_write_nothing_and_keep_every_try(tmp_path: Path) -> None:
    outcome = run_job(make_job(tmp_path), FakeRunner(BAD, BAD, BAD, BAD))

    assert (outcome.record.outcome, outcome.record.attempts) == ("failed", 4)
    assert len(outcome.record.tries) == 4
    assert outcome.record.last_reply == BAD
    assert not (tmp_path / "out.txt").exists()


def test_data_that_breaks_the_schema_is_a_failed_try(tmp_path: Path) -> None:
    outcome = run_job(make_job(tmp_path), FakeRunner({"words": "alpha"}, None, GOOD))

    assert (outcome.record.outcome, outcome.record.attempts) == ("ok", 3)
    assert outcome.record.tries[0][0].startswith("words:")
    assert "no structured output" in outcome.record.tries[1][0]


def test_a_matching_key_reuses_the_saved_result(tmp_path: Path) -> None:
    run_job(make_job(tmp_path), FakeRunner(GOOD))

    assert run_job(make_job(tmp_path), FakeRunner()).reused


def test_a_changed_request_runs_again(tmp_path: Path) -> None:
    run_job(make_job(tmp_path), FakeRunner(GOOD))

    changed = make_job(tmp_path, "Name two other words.")
    assert not run_job(changed, FakeRunner(GOOD)).reused


def test_a_job_error_stops_without_a_retry(tmp_path: Path) -> None:
    def broken(
        prompt: str, *, system: str, model: str, schema: object = None
    ) -> jobs.Reply:
        raise jobs.JobError("the usage limit was reached")

    outcome = run_job(make_job(tmp_path), broken)

    assert outcome.record.outcome == "failed"
    assert outcome.record.errors == ["the usage limit was reached"]


def test_job_schemas_use_only_standard_keywords() -> None:
    from unfold.build.replies import SceneReply

    job = make_job(Path("/tmp"))
    scene = Job(**{**job.__dict__, "reply": SceneReply})

    assert "discriminator" not in json.dumps(scene.schema)
    assert "prefixItems" not in json.dumps(scene.schema)
    assert "oneOf" in json.dumps(scene.schema)

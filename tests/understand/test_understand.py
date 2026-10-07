"""The understand step, driven by a fake runner, so no test calls a model."""

from pathlib import Path

import pytest
import yaml

from unfold import jobs
from unfold.cli import main
from unfold.sources import Anchor, SourceDocument
from unfold.understand import MAP_FILE, NOTES_FILE, RECORD_FILE, understand
from unfold.understand import command as understand_command

ANCHORS = [
    Anchor("p-1", "page", "Page 1", "The mean is the sum over the count."),
    Anchor("p-2", "page", "Page 2", "Variance is the mean squared distance."),
]
GOOD_MAP = """format: knowledge-map/v0
source: demo
concepts:
  - id: mean
    name: mean
    meaning: The sum divided by the count.
    anchors: [demo#p-1]
  - id: variance
    name: variance
    meaning: The mean squared distance from the mean.
    requires: [mean]
    anchors: [demo#p-2]
claims:
  - text: Variance is never negative.
    anchors: [demo#p-2]
gaps: []
suspected_errors: []
"""
GOOD_NOTES = "# Spread\n\nThe mean is the center [§p-1]. Variance is spread [§p-2].\n"
GOOD = f"<knowledge-map>\n{GOOD_MAP}</knowledge-map>\n<study-notes>\n{GOOD_NOTES}</study-notes>"
BAD = GOOD.replace("demo#p-2]", "demo#p-9]")


class FakeRunner:
    """Replies in order, and fails the test if it runs out of replies."""

    def __init__(self, *replies: str) -> None:
        self.replies = list(replies)
        self.prompts: list[str] = []

    def __call__(self, prompt: str, *, system: str, model: str) -> jobs.Reply:
        self.prompts.append(prompt)
        assert self.replies, "the step called the model more often than expected"
        return jobs.Reply(self.replies.pop(0), 100, 40, 1.0)


@pytest.fixture
def source(tmp_path: Path) -> Path:
    doc = SourceDocument(
        "demo", "Spread", "textbook", "demo.pdf", {}, {"needs": "cut"}, ANCHORS
    )
    return doc.save(tmp_path)


def outputs(folder: Path) -> Path:
    return folder / "understand"


def test_writes_both_outputs_and_a_record(source: Path) -> None:
    result = understand(source, runner=FakeRunner(GOOD))

    assert (result.record.outcome, result.record.attempts, result.reused) == (
        "ok",
        1,
        False,
    )
    saved = yaml.safe_load((outputs(source) / MAP_FILE).read_text())
    assert saved["written_by"] == "unfold understand, model sonnet"
    assert saved["concepts"][0]["requires"] == []
    assert (outputs(source) / NOTES_FILE).read_text() == GOOD_NOTES
    record = jobs.Record.load(outputs(source) / RECORD_FILE)
    assert record is not None
    assert (record.input_tokens, record.output_tokens) == (100, 40)


def test_the_prompt_holds_the_source_text_and_its_needs(source: Path) -> None:
    runner = FakeRunner(GOOD)

    understand(source, runner=runner)

    assert "<!-- anchor: p-2 -->" in runner.prompts[0]
    assert "Variance is the mean squared distance." in runner.prompts[0]
    assert "Needs: cut" in runner.prompts[0]


def test_a_failed_check_retries_with_the_errors(source: Path) -> None:
    runner = FakeRunner(BAD, GOOD)

    result = understand(source, runner=runner)

    assert (result.record.outcome, result.record.attempts) == ("ok", 2)
    assert "unknown anchor: demo#p-9" in runner.prompts[1]
    assert "demo#p-9" in runner.prompts[1].split("<last-answer>")[1]


def test_gives_up_after_three_retries_and_writes_no_output(source: Path) -> None:
    result = understand(source, runner=FakeRunner(BAD, BAD, BAD, BAD))

    assert (result.record.outcome, result.record.attempts) == ("failed", 4)
    assert result.record.errors == ["unknown anchor: demo#p-9"]
    assert not (outputs(source) / MAP_FILE).exists()
    assert jobs.Record.load(outputs(source) / RECORD_FILE) == result.record


def test_a_reply_without_its_parts_fails_the_check(source: Path) -> None:
    result = understand(source, runner=FakeRunner(*["Sure!"] * 4))

    assert any("<knowledge-map>" in error for error in result.record.errors)


def test_fences_inside_the_parts_are_dropped(source: Path) -> None:
    fenced = GOOD.replace(GOOD_MAP, f"```yaml\n{GOOD_MAP}```\n")

    assert understand(source, runner=FakeRunner(fenced)).record.outcome == "ok"


def test_a_saved_result_is_reused_without_a_call(source: Path) -> None:
    understand(source, runner=FakeRunner(GOOD))

    assert understand(source, runner=FakeRunner()).reused


def test_a_new_model_or_source_text_runs_again(source: Path) -> None:
    understand(source, runner=FakeRunner(GOOD))
    assert not understand(source, runner=FakeRunner(GOOD), model="opus").reused

    text = source / "document.md"
    text.write_text(text.read_text().replace("sum over", "total over"))

    assert not understand(source, runner=FakeRunner(GOOD), model="opus").reused


def test_a_job_error_is_recorded_without_a_retry(source: Path) -> None:
    def broken(prompt: str, *, system: str, model: str) -> jobs.Reply:
        raise jobs.JobError("the usage limit was reached")

    result = understand(source, runner=broken)

    assert result.record.outcome == "failed"
    assert result.record.errors == ["the usage limit was reached"]


def test_every_claim_of_a_bare_topic_is_flagged(tmp_path: Path) -> None:
    phrase = "the central limit theorem"
    topic = SourceDocument("clt", phrase, "topic", phrase, {}).save(tmp_path)
    reply = (
        GOOD.replace("source: demo", "source: clt")
        .replace("[demo#p-1]", "[]")
        .replace("[demo#p-2]", "[]")
        .replace(GOOD_NOTES, "# The theorem\n\nSample means settle down.\n")
    )
    runner = FakeRunner(reply)

    assert understand(topic, runner=runner).record.outcome == "ok"

    saved = yaml.safe_load((outputs(topic) / MAP_FILE).read_text())
    assert [claim["unsupported"] for claim in saved["claims"]] == [True]
    assert "no source text" in runner.prompts[0]


def test_the_command_reports_each_outcome(
    source: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(understand_command, "RUNNER", FakeRunner(GOOD))

    assert main(["understand", str(source)]) == 0
    assert main(["understand", str(source)]) == 0
    assert "reused" in capsys.readouterr().out
    assert main(["understand", str(source.parent / "missing")]) == 2
    assert main(["understand", str(source), "--retries", "-1"]) == 2


def test_the_command_exits_1_when_every_try_fails(
    source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(understand_command, "RUNNER", FakeRunner(BAD, BAD))

    assert main(["understand", str(source), "--retries", "1"]) == 1

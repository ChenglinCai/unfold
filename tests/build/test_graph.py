"""The build graph runs every step in order, and reuses what has not changed."""

import copy
import json
from pathlib import Path

import pytest

from unfold import jobs
from unfold.build import command as build_command
from unfold.build.graph import build
from unfold.cli import main
from unfold.formats import problems
from unfold.jobs import CanaryError
from unfold.sources import Anchor, SourceDocument

MAP = """format: knowledge-map/v0
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
NOTES = "# Spread\n\nThe mean is the center [§p-1]. Variance is spread [§p-2].\n"
UNDERSTOOD = (
    f"<knowledge-map>\n{MAP}</knowledge-map>\n<study-notes>\n{NOTES}</study-notes>"
)


def segment(number: int, slug: str, anchor: str) -> dict[str, object]:
    return {
        "id": f"s{number}-{slug}",
        "title": slug.title(),
        "target_seconds": 60,
        "anchors": [anchor],
    }


BEATS = ["one", "two", "three"]
REPLIES: dict[str, dict[str, object]] = {
    "PlanReply": {
        "episodes": [
            {
                "id": "E01-center",
                "title": "Center",
                "core_question": "Where?",
                "concepts": ["mean"],
            },
            {
                "id": "E02-spread",
                "title": "Spread",
                "core_question": "How far?",
                "concepts": ["variance"],
            },
        ]
    },
    "OutlineReply": {
        "title": "Center",
        "core_question": "Where is the middle?",
        "segments": [
            segment(1, "mean", "demo#p-1"),
            segment(2, "variance", "demo#p-2"),
            segment(3, "extra", "demo#p-1"),
        ],
    },
    "ScriptReply": {
        "beats": [
            {"cue": cue, "text": f"Beat {cue} makes one point.", "anchors": []}
            for cue in BEATS
        ]
    },
    "StoryboardReply": {
        "entries": [
            {
                "cue": cue,
                "visual": "A dot moves.",
                "component": "custom",
                "region": "plot",
            }
            for cue in BEATS
        ]
    },
}


class StepRunner:
    """Answers each step by the title of the schema it receives."""

    def __init__(self, refuse: bool = False, bad: str = "", canary: int = 5) -> None:
        self.refuse, self.bad, self.canary = refuse, bad, canary
        self.calls: list[str] = []

    def __call__(
        self, prompt: str, *, system: str, model: str, schema: object = None
    ) -> jobs.Reply:
        step = "understand"
        if isinstance(schema, dict):
            step = str(schema.get("title", "canary"))
        self.calls.append(step)
        assert not self.refuse, f"the build called the model for {step}"
        if step == "canary":
            data: dict[str, object] = {"answer": self.canary}
            return jobs.Reply(json.dumps(data), 3, 1, 0.1, data)
        if step == "understand":
            return jobs.Reply(UNDERSTOOD, 10, 5, 0.1)
        data = {} if step == self.bad else copy.deepcopy(REPLIES[step])
        return jobs.Reply(json.dumps(data), 10, 5, 0.1, data)


@pytest.fixture
def series(tmp_path: Path) -> Path:
    anchors = [
        Anchor("p-1", "page", "Page 1", "The mean is the sum over the count."),
        Anchor("p-2", "page", "Page 2", "Variance squares each distance."),
    ]
    SourceDocument(
        "demo", "Demo", "textbook", "demo.pdf", {}, {"needs": "cut"}, anchors
    ).save(tmp_path / "sources")
    folder = tmp_path / "series"
    folder.mkdir()
    (folder / "series.yaml").write_text(
        "format: series/v0\nid: spread\naudience: Adults.\nsources: [../sources/demo]\n"
    )
    return folder


def test_a_build_writes_the_first_episode_with_two_segments(series: Path) -> None:
    runner = StepRunner()

    result = build(series, runner)

    assert not result.failed
    episode = series / "E01-center"
    written = [
        series / "plan.yaml",
        episode / "outline.yaml",
        episode / "s1-mean" / "script.md",
        episode / "s1-mean" / "storyboard.yaml",
        episode / "s2-variance" / "script.md",
        episode / "s2-variance" / "storyboard.yaml",
    ]
    for path in written:
        assert problems(path) == [], path
    assert not (episode / "s3-extra").exists()
    assert not (series / "E02-spread").exists()
    assert result.notes == [
        "plan.yaml: building 1 of 2 episodes",
        "E01-center/outline.yaml: building 2 of 3 segments",
    ]
    expected = ["canary", "understand", "PlanReply", "OutlineReply"]
    assert runner.calls == expected + ["ScriptReply", "StoryboardReply"] * 2


def test_a_second_build_calls_nothing(series: Path) -> None:
    build(series, StepRunner())

    result = build(series, StepRunner(refuse=True))

    assert {line.status for line in result.lines} == {"reused"}


def test_until_stops_after_the_chosen_step(series: Path) -> None:
    build(series, StepRunner(), until="outline")

    assert (series / "E01-center" / "outline.yaml").exists()
    assert not (series / "E01-center" / "s1-mean").exists()


def test_a_changed_knowledge_map_reruns_only_later_steps(series: Path) -> None:
    build(series, StepRunner())
    knowledge_map = (
        series.parent / "sources" / "demo" / "understand" / "knowledge-map.yaml"
    )
    knowledge_map.write_text(
        knowledge_map.read_text().replace("gaps: []", "gaps:\n- Why squares?")
    )
    runner = StepRunner()

    result = build(series, runner)

    status = {line.output.name: line.status for line in result.lines}
    assert status["understand"] == "reused"
    assert status["plan.yaml"] == "written"
    assert "understand" not in runner.calls


def test_a_failed_step_stops_the_build(series: Path) -> None:
    result = build(series, StepRunner(bad="OutlineReply"))

    assert result.failed
    assert result.lines[-1].status == "failed"
    assert not (series / "E01-center" / "s1-mean").exists()


def test_the_command_reports_each_output(
    series: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(build_command, "RUNNER", StepRunner())
    assert main(["build", str(series)]) == 0
    assert "written" in capsys.readouterr().out

    monkeypatch.setattr(build_command, "RUNNER", StepRunner(refuse=True))
    assert main(["build", str(series)]) == 0
    out = capsys.readouterr().out
    assert not any(line.startswith("written") for line in out.splitlines())
    assert out.strip().endswith("0 written, 7 reused, 0 failed")


def test_the_command_exits_1_when_a_step_fails(
    series: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build_command, "RUNNER", StepRunner(bad="PlanReply"))

    assert main(["build", str(series), "--retries", "0"]) == 1


def test_the_command_exits_2_on_a_bad_series(tmp_path: Path) -> None:
    (tmp_path / "series.yaml").write_text("format: series/v0\nid: x\n")

    assert main(["build", str(tmp_path)]) == 2
    assert main(["build", str(tmp_path / "missing")]) == 2


def test_a_failing_canary_stops_the_build_before_any_real_call(series: Path) -> None:
    runner = StepRunner(canary=4)

    with pytest.raises(CanaryError, match="expected 5"):
        build(series, runner)

    assert runner.calls == ["canary"]
    assert not (series.parent / "sources" / "demo" / "understand").exists()


def test_a_build_with_nothing_to_run_makes_no_canary_call(series: Path) -> None:
    build(series, StepRunner())
    runner = StepRunner()

    build(series, runner)

    assert runner.calls == []


def test_every_call_adds_one_line_to_the_call_log(series: Path) -> None:
    build(series, StepRunner(bad="ScriptReply"), retries=1)

    log = (series / "calls.jsonl").read_text().splitlines()
    lines = [json.loads(line) for line in log]
    steps = [line["step"] for line in lines]
    assert steps == ["canary", "understand", "plan", "outline", "script", "script"]
    assert [line["outcome"] for line in lines][-2:] == ["retry", "failed"]
    assert all(line["model"] for line in lines)
    assert all(line["key"] for line in lines)


def test_the_command_exits_3_when_the_canary_fails(
    series: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(build_command, "RUNNER", StepRunner(canary=4))

    assert main(["build", str(series)]) == 3

"""Writers turn a checked reply into a file that passes its own schema."""

from pathlib import Path

from unfold.build.replies import OutlineReply, PlanReply, ScriptReply, StoryboardReply
from unfold.build.write import outline_text, plan_text, script_text, storyboard_text
from unfold.formats import problems
from unfold.script import parse_script

BEATS = [
    {"cue": "start", "text": "Every list\nhas a center.", "anchors": ["demo#p-1"]},
    {"cue": "spread", "text": "Some lists spread out.", "anchors": []},
    {"cue": "end", "text": "Next, we measure it.", "anchors": ["demo#p-1", "demo#p-2"]},
]


def save(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_text(text)
    return path


def test_a_written_script_passes_and_reads_back(tmp_path: Path) -> None:
    reply = ScriptReply.model_validate({"beats": BEATS})

    text = script_text(reply, "E01-spread", "s1-center", "sonnet")

    assert problems(save(tmp_path, "script.md", text)) == []
    script = parse_script(text)
    assert [beat.cue for beat in script.beats] == ["start", "spread", "end"]
    assert script.beats[0].text == "Every list has a center."
    assert script.anchors() == {
        "start": ["demo#p-1"],
        "spread": [],
        "end": ["demo#p-1", "demo#p-2"],
    }
    assert "  start: [demo#p-1]\n" in text


def test_the_yaml_outputs_pass_their_schemas(tmp_path: Path) -> None:
    plan = PlanReply.model_validate(
        {
            "episodes": [
                {
                    "id": "E01-spread",
                    "title": "Spread",
                    "core_question": "Why?",
                    "concepts": ["mean"],
                }
            ]
        }
    )
    segments = [
        {"id": f"s{n}-part", "title": "Part", "target_seconds": 90} for n in (1, 2)
    ]
    outline = OutlineReply.model_validate(
        {
            "title": "Spread",
            "core_question": "Why?",
            "segments": segments,
            "transitions": [{"from": "s1-part", "to": "s2-part", "idea": "Next."}],
        }
    )
    entry = {"cue": "start", "visual": "Dots.", "component": "custom", "region": "plot"}
    board = StoryboardReply.model_validate({"entries": [entry]})

    texts = {
        "plan.yaml": plan_text(plan, "spread-series", "sonnet"),
        "outline.yaml": outline_text(
            outline, "spread-series", "E01-spread", "Adults.", "sonnet"
        ),
        "storyboard.yaml": storyboard_text(board, "E01-spread", "s1-part", "sonnet"),
    }

    for name, text in texts.items():
        assert problems(save(tmp_path, name, text)) == [], name
    assert "from: s1-part" in texts["outline.yaml"]

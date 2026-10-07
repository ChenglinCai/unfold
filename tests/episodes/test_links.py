"""The ledger records what each episode teaches, and the idea-link check uses it."""

from unfold.episodes.ledger import build_ledger, ledger_text
from unfold.episodes.links import check_links
from unfold.formats.episode import OutlineV0


def outline(
    episode: str, segments: list[tuple[str, list[str], list[str]]]
) -> OutlineV0:
    return OutlineV0.model_validate(
        {
            "format": "outline/v0",
            "series": "money",
            "episode": episode,
            "title": episode,
            "core_question": "Why?",
            "audience": "Adults.",
            "segments": [
                {
                    "id": sid,
                    "title": sid,
                    "target_seconds": 60,
                    "requires": requires,
                    "establishes": establishes,
                }
                for sid, requires, establishes in segments
            ],
        }
    )


FIRST = outline("E01-value", [("s1-today", ["term:money"], ["idea:time-value"])])
SECOND = outline(
    "E02-discount",
    [("s1-rate", ["idea:time-value"], ["term:discount-rate", "visual:timeline"])],
)


def test_ideas_link_when_each_comes_from_earlier_or_the_audience() -> None:
    assert check_links([FIRST, SECOND], knows={"term:money"}) == []


def test_an_untaught_idea_is_named_with_its_segment() -> None:
    assert check_links([SECOND], knows=set()) == [
        "E02-discount/s1-rate requires idea:time-value, which nothing earlier establishes"
    ]


def test_the_ledger_lists_each_episodes_teaching_and_segments() -> None:
    ledger = build_ledger("money", [FIRST, SECOND])

    assert [entry.episode for entry in ledger.episodes] == ["E01-value", "E02-discount"]
    assert ledger.episodes[1].establishes == ["term:discount-rate", "visual:timeline"]
    assert ledger.episodes[0].segments == ["s1-today"]
    assert "E01-value" in ledger_text(ledger)

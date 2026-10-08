"""Binary checks from the M4 error analysis. Each one passes or fails, never a score."""

from pathlib import Path

from unfold.cli import main
from unfold.evals import (
    beats_are_grounded,
    chart_numbers_grounded,
    episode_stays_in_plan,
    first_episode_reaches_title,
    flagged_beats,
    links_by_episode,
    narration_fits_target,
    no_source_framing,
    numbers_in,
    plan_fits_source,
    scene_uses_components,
    storyboard_reuses_components,
)


def test_a_plan_fits_its_source() -> None:
    assert plan_fits_source(episodes=2, words=1114, topic=False)
    assert not plan_fits_source(episodes=6, words=571, topic=False)
    assert plan_fits_source(episodes=3, words=0, topic=True)
    assert not plan_fits_source(episodes=5, words=0, topic=True)


def test_an_episode_stays_inside_its_plan() -> None:
    later = {"velocity-of-money", "real-gdp"}

    assert episode_stays_in_plan(
        ["term:money-supply", "idea:equation-of-exchange"], later
    )
    assert not episode_stays_in_plan(["term:velocity-of-money"], later)


def test_narration_fits_its_target_length() -> None:
    assert narration_fits_target(words=170, target_seconds=60)
    assert not narration_fits_target(words=219, target_seconds=45)
    assert not narration_fits_target(words=40, target_seconds=60)


def test_most_beats_are_grounded() -> None:
    assert beats_are_grounded({"a": ["s#p-1"], "b": []}, topic=False)
    assert not beats_are_grounded({"a": [], "b": [], "c": ["s#p-1"]}, topic=False)
    assert beats_are_grounded({"a": [], "b": []}, topic=True)


def test_narration_does_not_borrow_the_sources_framing() -> None:
    assert not no_source_framing("This is the branch this whole course cares about.")
    assert not no_source_framing("As the slides show, the mean moves.")
    assert no_source_framing("Over the course of one month, a dollar moves.")
    assert no_source_framing("In this video, you will see why.")


def test_a_storyboard_reuses_components() -> None:
    assert storyboard_reuses_components(["custom", "axes"])
    assert not storyboard_reuses_components(["custom", "custom", "axes"])


def test_eval_needs_a_series_folder(tmp_path: Path) -> None:
    assert main(["eval", str(tmp_path / "missing")]) == 2


def test_the_first_episode_reaches_the_title() -> None:
    clt = "the central limit theorem"
    assert first_episode_reaches_title(clt, ["central-limit-theorem"])
    assert not first_episode_reaches_title(clt, ["random-variable", "variance"])
    assert first_episode_reaches_title("Euler's identity", ["eulers-identity"])
    knn = "CIS 5200 Lecture 3: k-nearest neighbors"
    assert first_episode_reaches_title(knn, ["nearest-neighbor-set"])
    money = "Velocity of money (spoken Wikipedia)"
    assert not first_episode_reaches_title(money, ["money-supply", "price-level"])


def test_flagged_beats_are_those_with_no_anchor() -> None:
    assert flagged_beats({"a": [], "b": ["s#p-1"], "c": []}) == 2


def test_numbers_come_from_digits_and_words() -> None:
    text = "One hundred five dollars, then 1,200 more, and ten thousand later."

    assert {105, 1200, 10000} <= numbers_in(text)
    assert 55 in numbers_in("Fifty five heads came up.")


def test_chart_numbers_must_come_from_the_narration_or_storyboard() -> None:
    said = "Growth takes one hundred dollars to one hundred five."

    assert chart_numbers_grounded([100, 105], said)
    assert not chart_numbers_grounded([100, 72], said)


def test_a_scene_mostly_uses_components() -> None:
    assert scene_uses_components(["custom", "bar-chart"])
    assert not scene_uses_components(["custom", "custom", "text-card"])


def test_ideas_link_by_episode() -> None:
    from unfold.formats.episode import OutlineV0

    def outline(episode: str, requires: list[str], establishes: list[str]) -> OutlineV0:
        segment = {"id": "s1-a", "title": "A", "target_seconds": 60}
        segment |= {"requires": requires, "establishes": establishes}
        head = {"format": "outline/v0", "series": "x", "episode": episode, "title": "T"}
        head |= {"core_question": "Q?", "audience": "A."}
        return OutlineV0.model_validate({**head, "segments": [segment]})

    first = outline("E01-a", ["term:money"], ["idea:value"])
    second = outline("E02-b", ["idea:value", "idea:rate"], [])

    assert links_by_episode([first, second], {"term:money"}) == {
        "E01-a": True,
        "E02-b": False,
    }

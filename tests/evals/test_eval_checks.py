"""Binary checks from the M4 error analysis. Each one passes or fails, never a score."""

from pathlib import Path

from unfold.cli import main
from unfold.evals import (
    beats_are_grounded,
    episode_stays_in_plan,
    first_episode_reaches_title,
    narration_fits_target,
    no_source_framing,
    plan_fits_source,
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

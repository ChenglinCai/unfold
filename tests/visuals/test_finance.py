"""Present values and their labels come from code, so no model invents them."""

import subprocess
import sys

import pytest

from unfold.visuals.finance import present_value, shown


def test_a_future_amount_is_worth_less_today() -> None:
    assert present_value(10_000, 8, 1) == pytest.approx(9259.259, abs=0.001)
    assert present_value(10_000, 8, 12) == pytest.approx(3971.138, abs=0.001)


def test_a_zero_rate_or_a_flow_today_keeps_its_amount() -> None:
    assert present_value(100, 0, 5) == 100
    assert present_value(-100, 8, 0) == -100


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (9259.259, "9,259"),
        (92.5926, "92.59"),
        (100.0, "100"),
        (5.25, "5.25"),
        (0.5, "0.5"),
        (999.999, "1,000"),
        (-0.001, "0"),
    ],
)
def test_shown_values_round_as_the_screen_shows_them(value: float, text: str) -> None:
    assert shown(value) == text


def test_a_prefix_follows_the_sign() -> None:
    assert shown(10_000, "$") == "$10,000"
    assert shown(-100, "$") == "-$100"


def test_finance_loads_without_manim() -> None:
    code = "import sys, unfold.visuals.finance; print('manim' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "False"

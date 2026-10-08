"""Present values, and numbers as the screen shows them. No manim, so tests run fast.

The present-value component draws only what these functions compute, so a
model never supplies a discounted number.
"""


def present_value(amount: float, rate: float, at: float) -> float:
    """What an amount paid at a time is worth today, at a rate in percent per period."""
    return amount / (1 + rate / 100) ** at


def shown(value: float, prefix: str = "") -> str:
    """Whole units with separators from 1,000, else at most two decimals."""
    value = round(value, 2) or 0.0  # turns -0.0 into 0.0
    sign = "-" if value < 0 else ""
    size = abs(value)
    digits = f"{size:,.0f}" if size >= 1000 else f"{size:.2f}".rstrip("0").rstrip(".")
    return f"{sign}{prefix}{digits}"

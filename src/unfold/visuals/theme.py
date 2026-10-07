"""The theme: one background, a small palette, and fixed text sizes."""

from manim import config

BACKGROUND = "#101318"
TEXT = "#ECE7DD"
MUTED = "#8A8F98"
BLUE = "#5FB3E4"
YELLOW = "#F2C14E"
GREEN = "#7CC47F"
RED = "#E8665A"
PURPLE = "#A88BD8"
PALETTE = [BLUE, YELLOW, GREEN, RED, PURPLE]

TITLE_SIZE = 44
BODY_SIZE = 32
LABEL_SIZE = 26
# Text smaller than this is hard to read on a phone.
MIN_FONT = 18


def apply() -> None:
    """Set manim's background for every scene that unfold renders."""
    config.background_color = BACKGROUND

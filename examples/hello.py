"""A tiny scene that shows manim, LaTeX, and video encoding all work.

Render it with:

    uv run manim -ql examples/hello.py Hello
"""

from manim import UP, FadeIn, MathTex, Scene, Text, Write


class Hello(Scene):
    """Shows the project name, then writes one equation in the center."""

    def construct(self) -> None:
        title = Text("unfold").to_edge(UP)
        equation = MathTex(r"e^{i\pi} + 1 = 0")
        self.play(FadeIn(title))
        self.play(Write(equation))
        self.wait(0.5)

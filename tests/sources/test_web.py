"""Web pages and Markdown become one anchor per section."""

from pathlib import Path

import pytest

from unfold.sources import Meta
from unfold.sources.web import read_html, read_markdown

META = Meta(
    id="w",
    title="Euler",
    family="web",
    origin="https://example.org",
    license="CC BY-SA 4.0",
)

PAGE = """<html><head><title>Euler's identity</title></head><body>
<nav><a href="/">Home</a> <a href="/about">About us</a></nav>
<article>
<h1>Euler's identity</h1>
<p>Euler's identity links five constants in one short equation. It joins
e, i, pi, one, and zero, and many people call it the most beautiful formula.</p>
<h2>Explanations</h2>
<p>The identity is a special case of Euler's formula, which relates the complex
exponential to sine and cosine. Setting the angle to pi gives the identity.</p>
<h2>Generalizations</h2>
<p>The identity also follows from the roots of unity. Summing all the n-th roots
of unity gives zero for every n greater than one.</p>
</article>
<footer>Copyright notice and privacy policy.</footer>
</body></html>"""


def test_markdown_headings_become_anchors(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text(
        "Intro text.\n\n## The law of demand\n\nPrices up.\n\n## Supply\n\nMore.\n"
    )

    doc = read_markdown(path, META)

    assert [(a.id, a.title) for a in doc.anchors] == [
        ("intro", "Introduction"),
        ("the-law-of-demand", "The law of demand"),
        ("supply", "Supply"),
    ]
    assert doc.anchors[1].text == "Prices up."


def test_repeated_headings_get_distinct_ids(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text("## Example\n\nOne.\n\n## Example\n\nTwo.\n")

    assert [a.id for a in read_markdown(path, META).anchors] == ["example", "example-2"]


def test_long_headings_get_short_ids(tmp_path: Path) -> None:
    title = "Book I. Of the causes of improvement in the productive powers of labour"
    path = tmp_path / "notes.md"
    path.write_text(f"## {title}\n\nOne.\n\n## {title}\n\nTwo.\n")

    first, second = [a.id for a in read_markdown(path, META).anchors]

    assert len(first) <= 60 and first.startswith("book-i-of-the-causes")
    assert "book-i-of-the-causes-of-improvement-in-the-productive-powers-of-labour".startswith(
        f"{first}-"
    )
    assert second == f"{first}-2"


def test_a_web_page_keeps_its_article_and_drops_its_clutter() -> None:
    doc = read_html(PAGE, META)
    text = " ".join(a.text for a in doc.anchors)

    assert "five constants" in text
    assert "About us" not in text
    assert "privacy policy" not in text
    assert [a.id for a in doc.anchors][-2:] == ["explanations", "generalizations"]
    assert doc.profile["format"] == "html"


def test_a_page_with_only_a_menu_has_no_main_text() -> None:
    with pytest.raises(ValueError, match="no main text"):
        read_html("<html><body><nav>Home</nav></body></html>", META)


MATH_PAGE = r"""<html><body><article><h1>Euler's identity</h1>
<table class="sidebar"><tr><td>Part of a series of articles</td></tr></table>
<p>Euler's identity is the equality
<span class="mwe-math-element"><span style="display: none;"><math
alttext="{\displaystyle e^{i\pi }+1=0}"><mi>e</mi></math></span><img
class="mwe-math-fallback-image-display" alt="{\displaystyle e^{i\pi }+1=0}"></span>
where e is Euler's number.<sup class="reference"><a href="#n1">[1]</a></sup>
It links five constants in one short line, and many people call it beautiful.</p>
<h2>History<span class="mw-editsection">[edit]</span></h2>
<p>Euler never wrote the identity in this form, but it follows from his formula.</p>
</article></body></html>"""


def test_formulas_keep_their_tex_and_wiki_clutter_goes() -> None:
    doc = read_html(MATH_PAGE, META)
    text = " ".join(a.text for a in doc.anchors)

    assert "$e^{i\\pi }+1=0$" in text
    assert "[1]" not in text
    assert "[edit]" not in [a.title for a in doc.anchors][-1]
    assert "Part of a series" not in text


def test_a_hash_inside_a_code_fence_is_not_a_heading(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    fence = "```"
    path.write_text(
        f"## Setup\n\n{fence}sh\n# install it\nuv sync\n{fence}\n\n## Use\n\nRun it.\n"
    )

    doc = read_markdown(path, META)

    assert [a.id for a in doc.anchors] == ["setup", "use"]
    assert "# install it" in doc.anchors[0].text


def test_formulas_keep_their_underscores_and_stars() -> None:
    page = (
        "<html><body><article><h1>Present value</h1><p>Each future amount counts for "
        'less today, and the formula <math alttext="R_{t} x^{*}"><mi>R</mi></math> '
        "shows one term of the sum.</p><p>Many pages write the formula as text, such as "
        "$$PV = \\sum_{t=1}^{n} R_{t}$$ for the whole stream of amounts.</p>"
        "</article></body></html>"
    )

    text = read_html(page, META).text()

    assert "$R_{t} x^{*}$" in text and "$$PV = \\sum_{t=1}^{n} R_{t}$$" in text

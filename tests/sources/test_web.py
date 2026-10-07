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

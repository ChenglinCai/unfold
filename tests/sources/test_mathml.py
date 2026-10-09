"""MathML becomes TeX, so a formula without its TeX source keeps its meaning."""

import pytest
from lxml import html as lxml_html

from unfold.sources import Meta
from unfold.sources.mathml import mathml_tex
from unfold.sources.web import read_html

MINUS, MU, SIGMA, SUM = (chr(code) for code in (0x2212, 0x3BC, 0x3C3, 0x2211))
MACRON = chr(0xAF)


def tex(markup: str) -> str:
    return mathml_tex(lxml_html.fragment_fromstring(f"<math>{markup}</math>"))


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        (
            f"<mfrac><mrow><mi>x</mi><mo>{MINUS}</mo><mi>{MU}</mi></mrow>"
            f"<mi>{SIGMA}</mi></mfrac>",
            r"\frac{x - \mu}{\sigma}",
        ),
        ("<msup><mi>x</mi><mn>2</mn></msup>", "{x}^{2}"),
        ("<msub><mi>x</mi><mi>i</mi></msub>", "{x}_{i}"),
        ("<msqrt><mi>n</mi></msqrt>", r"\sqrt{n}"),
        ("<mi>log</mi><mi>p</mi>", r"\log p"),
        (
            f"<munderover><mo>{SUM}</mo><mrow><mi>i</mi><mo>=</mo><mn>1</mn></mrow>"
            "<mi>n</mi></munderover>",
            r"\sum_{i = 1}^{n}",
        ),
        (f"<mover><mi>x</mi><mo>{MACRON}</mo></mover>", r"\bar{x}"),
        (
            '<mfenced open="[" close="]"><mi>a</mi><mi>b</mi></mfenced>',
            r"\left[ a , b \right]",
        ),
        ("<mtext>if</mtext>", r"\text{if}"),
    ],
)
def test_presentation_mathml_becomes_tex(markup: str, expected: str) -> None:
    assert tex(markup) == expected


def test_a_tex_annotation_wins() -> None:
    markup = (
        "<semantics><mi>x</mi>"
        '<annotation encoding="application/x-tex">\\bar{x}</annotation></semantics>'
    )

    assert tex(markup) == r"\bar{x}"


def test_a_page_keeps_formulas_that_have_no_alttext() -> None:
    formula = (
        f"<math display='block'><semantics><mfrac><mrow><mi>x</mi><mo>{MINUS}</mo>"
        f"<mi>{MU}</mi></mrow><mi>{SIGMA}</mi></mfrac>"
        "<annotation-xml encoding='MathML-Content'><ci>x</ci></annotation-xml>"
        "</semantics></math>"
    )
    page = (
        "<html><body><article><h1>Z-scores</h1><p>A z-score counts standard deviations "
        "from the mean, and many tables list them for each value.</p><p>The z-score is:</p>"
        f"<div data-type='equation'>{formula}</div><p>Here x is one value of the variable, "
        "and the formula holds for each value.</p></article></body></html>"
    )
    meta = Meta(id="z", title="Z", family="web", origin="x", license="CC BY 4.0")

    text = read_html(page, meta).text()

    assert r"$$\frac{x - \mu}{\sigma}$$" in text

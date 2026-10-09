"""Word's equations, written in OMML, become TeX."""

import pytest
from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]

from unfold.sources.omml import omml_tex

M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
SUM, MINUS, SIGMA, OVERLINE = (chr(code) for code in (0x2211, 0x2212, 0x3C3, 0x305))


def tex(inside: str) -> str:
    return omml_tex(etree.fromstring(f'<m:oMath xmlns:m="{M}">{inside}</m:oMath>'))


def run(text: str) -> str:
    return f"<m:r><m:t>{text}</m:t></m:r>"


@pytest.mark.parametrize(
    ("inside", "expected"),
    [
        (
            f"<m:f><m:num>{run('a')}</m:num><m:den>{run('b')}</m:den></m:f>",
            r"\frac{a}{b}",
        ),
        (f"<m:sSup><m:e>{run('x')}</m:e><m:sup>{run('2')}</m:sup></m:sSup>", "{x}^{2}"),
        (f"<m:sSub><m:e>{run('x')}</m:e><m:sub>{run('i')}</m:sub></m:sSub>", "{x}_{i}"),
        (
            f"<m:rad><m:radPr><m:degHide m:val='1'/></m:radPr><m:deg/>"
            f"<m:e>{run('n')}</m:e></m:rad>",
            r"\sqrt{n}",
        ),
        (
            f"<m:rad><m:deg>{run('3')}</m:deg><m:e>{run('x')}</m:e></m:rad>",
            r"\sqrt[3]{x}",
        ),
        (
            f"<m:nary><m:naryPr><m:chr m:val='{SUM}'/></m:naryPr><m:sub>{run('i=1')}</m:sub>"
            f"<m:sup>{run('n')}</m:sup><m:e>{run('x')}</m:e></m:nary>",
            r"\sum_{i=1}^{n} x",
        ),
        (
            f"<m:d><m:e>{run('a')}</m:e><m:e>{run('b')}</m:e></m:d>",
            r"\left( a | b \right)",
        ),
        (
            "<m:d><m:dPr><m:begChr m:val='['/><m:endChr m:val=']'/></m:dPr>"
            f"<m:e>{run('x')}</m:e></m:d>",
            r"\left[ x \right]",
        ),
        (
            f"<m:func><m:fName>{run('sin')}</m:fName><m:e>{run('x')}</m:e></m:func>",
            r"\sin x",
        ),
        (
            f"<m:acc><m:accPr><m:chr m:val='{OVERLINE}'/></m:accPr><m:e>{run('x')}</m:e></m:acc>",
            r"\bar{x}",
        ),
        (f"{run('x')}{run(MINUS)}{run(SIGMA)}", r"x - \sigma"),
    ],
)
def test_omml_becomes_tex(inside: str, expected: str) -> None:
    assert tex(inside) == expected

"""Word files become Markdown: styled headings become anchors, and equations become TeX."""

import zipfile
from pathlib import Path

import pytest
from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]

from unfold.cli import main
from unfold.sources import Meta, docx, load
from unfold.sources.docx import read_docx

META = Meta(
    id="ig", title="Interest", family="textbook", origin="ig.docx", license=None
)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
RELS = """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Target="word/document.xml"
 Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"/>
</Relationships>"""
STYLES = f"""<w:styles xmlns:w="{W}">
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>
<w:style w:type="paragraph" w:styleId="Chapter"><w:name w:val="Chapter"/>
 <w:basedOn w:val="Heading1"/></w:style>
<w:style w:type="paragraph" w:styleId="Rates"><w:name w:val="Rates"/>
 <w:pPr><w:outlineLvl w:val="1"/></w:pPr></w:style>
</w:styles>"""


def para(text: str, style: str = "", extra: str = "") -> str:
    styled = (
        f'<w:pPr><w:pStyle w:val="{style}"/>{extra}</w:pPr>' if style or extra else ""
    )
    return f"<w:p>{styled}<w:r><w:t xml:space='preserve'>{text}</w:t></w:r></w:p>"


def item(text: str, level: int) -> str:
    numbered = f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="1"/></w:numPr>'
    return f"<w:p><w:pPr>{numbered}</w:pPr><w:r><w:t>{text}</w:t></w:r></w:p>"


def run(text: str) -> str:
    return f"<m:r><m:t>{text}</m:t></m:r>"


FRACTION = (
    f"<m:oMath><m:f><m:num>{run('a')}</m:num><m:den>{run('b')}</m:den></m:f></m:oMath>"
)
SQUARE = f"<m:sSup><m:e>{run('x')}</m:e><m:sup>{run('2')}</m:sup></m:sSup>"
CELLS = "".join(f"<w:tc>{para(text)}</w:tc>" for text in ("Years", "Balance"))
VALUES = "".join(f"<w:tc>{para(text)}</w:tc>" for text in ("1", "105"))
TOC = (
    '<w:sdt><w:sdtPr><w:docPartObj><w:docPartGallery w:val="Table of Contents"/>'
    f"</w:docPartObj></w:sdtPr><w:sdtContent>{para('Contents line')}</w:sdtContent></w:sdt>"
)
BODY = "".join(
    [
        TOC,
        para("Interest and Growth", "Title"),
        para("Money grows when it earns interest."),
        para("Simple interest", "Heading1"),
        "<w:p><w:r><w:t xml:space='preserve'>The rate is </w:t></w:r>"
        f"{FRACTION}<w:r><w:t xml:space='preserve'> each year.</w:t></w:r></w:p>",
        f"<w:p><m:oMathPara><m:oMath>{SQUARE}</m:oMath></m:oMathPara></w:p>",
        item("First point", 0),
        item("Nested point", 1),
        f"<w:tbl><w:tr>{CELLS}</w:tr><w:tr>{VALUES}</w:tr></w:tbl>",
        para("Compound interest", "Chapter"),
        "<w:p><w:r><w:t xml:space='preserve'>Kept </w:t></w:r><w:del><w:r>"
        "<w:delText>gone </w:delText></w:r></w:del><w:r><w:instrText> PAGE </w:instrText>"
        "</w:r><w:r><w:t>text.</w:t><w:tab/><w:t>More.</w:t></w:r></w:p>",
        para("Rates", "Rates"),
        para("Rates change over time."),
    ]
)


def make(folder: Path, body: str = BODY, prolog: str = "") -> Path:
    path = folder / "ig.docx"
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("_rels/.rels", RELS)
        package.writestr("word/styles.xml", STYLES)
        document = f'{prolog}<w:document xmlns:w="{W}" xmlns:m="{M}"><w:body>{body}'
        package.writestr("word/document.xml", document + "</w:body></w:document>")
    return path


def test_styled_headings_become_anchors_and_equations_become_tex(
    tmp_path: Path,
) -> None:
    doc = read_docx(make(tmp_path), META)

    assert [a.id for a in doc.anchors] == [
        "interest-and-growth",
        "simple-interest",
        "compound-interest",
        "rates",
    ]
    text = doc.text()
    assert r"The rate is $\frac{a}{b}$ each year." in text
    assert "$${x}^{2}$$" in text
    assert "- First point\n  - Nested point" in text
    assert "| Years | Balance |\n| --- | --- |\n| 1 | 105 |" in text
    assert "Kept text. More." in text
    for gone in ("Contents line", "gone", "PAGE"):
        assert gone not in text
    assert doc.profile["format"] == "docx"


def test_an_entity_cannot_read_local_files(tmp_path: Path) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("The secret.\n")
    prolog = f'<!DOCTYPE w:document [<!ENTITY leak SYSTEM "file://{secret}">]>'
    body = para("Leak &leak; here.") + para("Plain text stays.")

    text = read_docx(make(tmp_path, body, prolog), META).text()

    assert "secret" not in text.lower() and "Plain text stays." in text


def test_a_file_that_unpacks_too_large_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(docx, "MAX_BYTES", 1000)

    with pytest.raises(ValueError, match="MB"):
        read_docx(make(tmp_path, BODY * 3), META)


def test_ingest_reads_a_word_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "sources"

    assert main(["ingest", str(make(tmp_path)), "--out", str(out)]) == 0

    doc = load(out / "ig")
    assert doc.family == "textbook"
    assert doc.anchors[1].id == "simple-interest"


def bold(text: str, size: int) -> str:
    look = f'<w:rPr><w:b/><w:sz w:val="{size}"/></w:rPr>'
    return f"<w:p><w:r>{look}<w:t>{text}</w:t></w:r></w:p>"


def plain(text: str, size: int = 24) -> str:
    return (
        f'<w:p><w:r><w:rPr><w:sz w:val="{size}"/></w:rPr><w:t>{text}</w:t></w:r></w:p>'
    )


def test_bold_large_paragraphs_are_headings_when_no_style_marks_any(
    tmp_path: Path,
) -> None:
    bullet = chr(0x2022)
    body = "".join(
        [
            bold("Present value", 48),
            plain("A dollar today is worth more than a dollar next year."),
            bold("Discounting", 36),
            plain("Divide each amount by one plus the rate."),
            plain(f"{bullet}\tPick a rate"),
            plain(f"{bullet}\tDiscount each cash flow"),
            bold(
                "A bold sentence that runs far too long to be any kind of heading.", 24
            ),
        ]
    )

    doc = read_docx(make(tmp_path, body), META)

    assert [a.id for a in doc.anchors] == ["present-value", "discounting"]
    assert "- Pick a rate\n- Discount each cash flow" in doc.text()
    document = f'<w:document xmlns:w="{W}"><w:body>{body}</w:body></w:document>'
    lines = docx.document_markdown(etree.fromstring(document), {}).splitlines()
    assert "# Present value" in lines and "## Discounting" in lines


def test_a_nested_table_stays_inside_its_cell(tmp_path: Path) -> None:
    inner = (
        f"<w:tbl><w:tr><w:tc>{para('inner one')}</w:tc><w:tc>{para('inner two')}</w:tc>"
    )
    inner += "</w:tr></w:tbl>"
    cell = f"<w:tc>{para('Before')}{inner}{para('After')}</w:tc>"
    body = f"<w:tbl><w:tr>{cell}<w:tc>{para('Right')}</w:tc></w:tr></w:tbl>"

    text = read_docx(make(tmp_path, body), META).text()

    assert "| Before inner one inner two After | Right |" in text

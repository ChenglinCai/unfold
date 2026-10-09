"""MathML as TeX, so that a formula without its TeX source keeps its meaning.

Pages such as OpenStax's hold MathML and no TeX, and the web reader's extractor
drops MathML. The converter covers the presentation elements that textbooks
use. A TeX annotation wins when a formula has one, and any other element keeps
its text.
"""

from lxml import html as lxml_html

# Built from code points, so that no confusable character sits in this file.
OPERATORS = {
    chr(code): tex
    for code, tex in [
        (0x2212, "-"),
        (0x2013, "-"),
        (0xD7, r"\times"),
        (0xB7, r"\cdot"),
        (0x22C5, r"\cdot"),
        (0xB1, r"\pm"),
        (0x2264, r"\le"),
        (0x2265, r"\ge"),
        (0x2260, r"\ne"),
        (0x2248, r"\approx"),
        (0x221E, r"\infty"),
        (0x2211, r"\sum"),
        (0x220F, r"\prod"),
        (0x222B, r"\int"),
        (0x2192, r"\to"),
        (0x2208, r"\in"),
        (0x2202, r"\partial"),
        (0x2026, r"\ldots"),
        (0x22EF, r"\cdots"),
        (0x2032, "'"),
        (0x2223, "|"),
        (0x2016, r"\|"),
        (0x27E8, r"\langle"),
        (0x27E9, r"\rangle"),
    ]
}
GREEK = {
    chr(0x3B1 + index): "\\" + name
    for index, name in enumerate(
        "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi o pi "
        "rho varsigma sigma tau upsilon phi chi psi omega".split()
    )
} | {chr(0x3BF): "o", chr(0x3D5): r"\phi", chr(0x3F5): r"\epsilon"}
CAPITALS = {
    chr(code): "\\" + name
    for code, name in [
        (0x393, "Gamma"),
        (0x394, "Delta"),
        (0x398, "Theta"),
        (0x39B, "Lambda"),
        (0x39E, "Xi"),
        (0x3A0, "Pi"),
        (0x3A3, "Sigma"),
        (0x3A5, "Upsilon"),
        (0x3A6, "Phi"),
        (0x3A8, "Psi"),
        (0x3A9, "Omega"),
    ]
}
SYMBOLS = OPERATORS | GREEK | CAPITALS | {c: "\\" + c for c in "{}%#&$_"}
# Function application, invisible times and commas, and spaces that carry no meaning.
INVISIBLE = {chr(code) for code in (0x2061, 0x2062, 0x2063, 0x2064, 0xA0, 0x200B)}
FUNCTIONS = set(
    "sin cos tan sec csc cot arcsin arccos arctan sinh cosh tanh log ln exp lim max "
    "min sup inf det gcd Pr arg dim ker".split()
)
ACCENTS = {
    chr(code): name for code, name in [(0xAF, "bar"), (0x2C9, "bar"), (0x203E, "bar")]
}
ACCENTS |= {
    "_": "bar",
    "^": "hat",
    chr(0x2C6): "hat",
    "~": "tilde",
    chr(0x2DC): "tilde",
}
ACCENTS |= {chr(0x2192): "vec", ".": "dot", chr(0x2D9): "dot", chr(0xA8): "ddot"}
LIMITS = (r"\sum", r"\prod", r"\int", r"\lim", r"\max", r"\min", r"\sup", r"\inf")
TEX = {"application/x-tex", "application/x-latex", "tex", "latex"}


def _name(element: lxml_html.HtmlElement) -> str:
    tag = element.tag if isinstance(element.tag, str) else ""
    return tag.rsplit("}", 1)[-1].lower()


def chars_tex(text: str) -> str:
    """Each character as TeX, with a space after a command so that it stays whole."""
    out = ""
    for char in text:
        if char in INVISIBLE:
            continue
        mapped = SYMBOLS.get(char, char)
        out += mapped + (" " if mapped[:1] == "\\" and mapped[1:].isalpha() else "")
    return out.strip()


def _identifier(text: str) -> str:
    if text in FUNCTIONS:
        return "\\" + text
    if len(text) > 1 and text.isascii() and text.isalpha():
        return r"\mathrm{" + text + "}"
    return chars_tex(text)


def fence_tex(char: str) -> str:
    return {"": ".", "{": r"\{", "}": r"\}"}.get(char, SYMBOLS.get(char, char))


def _annotation(element: lxml_html.HtmlElement) -> str:
    """The TeX that a formula carries as an annotation, if any."""
    for note in element.iter():
        encoding = (note.get("encoding") or "").lower()
        if (
            _name(note) == "annotation"
            and encoding in TEX
            and (note.text or "").strip()
        ):
            return (note.text or "").strip()
    return ""


def mathml_tex(element: lxml_html.HtmlElement) -> str:
    """The TeX for one MathML element, such as a whole <math>."""
    name = _name(element)
    if name in ("annotation", "annotation-xml"):
        return ""
    if name in ("math", "semantics") and (tex := _annotation(element)):
        return tex
    kids = [mathml_tex(child) for child in element if _name(child)]
    kids = [kid for kid in kids if kid]
    text = (element.text or "").strip()
    count = len(kids)
    if name == "mi":
        return _identifier(text)
    if name in ("mn", "mo"):
        return chars_tex(text)
    if name == "mtext":
        return (
            r"\text{" + text.replace("{", r"\{").replace("}", r"\}") + "}"
            if text
            else ""
        )
    if name == "msup" and count == 2:
        return f"{{{kids[0]}}}^{{{kids[1]}}}"
    if name == "msub" and count == 2:
        return f"{{{kids[0]}}}_{{{kids[1]}}}"
    if name == "msubsup" and count == 3:
        return f"{{{kids[0]}}}_{{{kids[1]}}}^{{{kids[2]}}}"
    if name == "mfrac" and count == 2:
        return rf"\frac{{{kids[0]}}}{{{kids[1]}}}"
    if name == "msqrt":
        return rf"\sqrt{{{' '.join(kids)}}}"
    if name == "mroot" and count == 2:
        return rf"\sqrt[{kids[1]}]{{{kids[0]}}}"
    if name == "mover" and count == 2:
        accent = ACCENTS.get((element[1].text or "").strip())
        return (
            rf"\{accent}{{{kids[0]}}}"
            if accent
            else rf"\overset{{{kids[1]}}}{{{kids[0]}}}"
        )
    if name == "munder" and count == 2:
        if kids[0].startswith(LIMITS):
            return f"{kids[0]}_{{{kids[1]}}}"
        return rf"\underset{{{kids[1]}}}{{{kids[0]}}}"
    if name == "munderover" and count == 3:
        return f"{kids[0]}_{{{kids[1]}}}^{{{kids[2]}}}"
    if name == "mfenced":
        separator = (element.get("separators") or ",").strip()[:1] or ","
        opening, closing = element.get("open", "("), element.get("close", ")")
        inside = f" {separator} ".join(kids)
        return rf"\left{fence_tex(opening)} {inside} \right{fence_tex(closing)}"
    if name == "mtable":
        return r"\begin{matrix} " + r" \\ ".join(kids) + r" \end{matrix}"
    if name in ("mtr", "mlabeledtr"):
        return " & ".join(kids)
    return " ".join(kids) or chars_tex(text)

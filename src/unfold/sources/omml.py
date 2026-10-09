"""Word's equations, written in OMML, as TeX.

OMML is the XML that Word keeps for each equation. The converter covers the
structures that course notes use, and shares its symbol tables with the MathML
converter. Any other element keeps the TeX of its parts.
"""

from lxml import etree  # pyright: ignore[reportAttributeAccessIssue]

from unfold.sources.mathml import ACCENTS, FUNCTIONS, LIMITS, chars_tex, fence_tex

# OMML marks accents with combining characters, so these join the shared table.
MARKS = ACCENTS | {
    chr(code): name
    for code, name in [
        (0x305, "bar"),
        (0x302, "hat"),
        (0x303, "tilde"),
        (0x307, "dot"),
        (0x308, "ddot"),
        (0x20D7, "vec"),
    ]
}


def _name(element: etree._Element) -> str:
    tag = element.tag if isinstance(element.tag, str) else ""
    return tag.rsplit("}", 1)[-1]


def _option(element: etree._Element, properties: str, option: str) -> str | None:
    """The value of an option, such as the character in <m:naryPr><m:chr m:val=…/>."""
    for child in element:
        if _name(child) == properties:
            for setting in child:
                if _name(setting) == option:
                    return next(iter(setting.attrib.values()), "")
    return None


def _part(element: etree._Element, name: str) -> str:
    """The TeX of a named part, such as the numerator <m:num>."""
    return next((omml_tex(child) for child in element if _name(child) == name), "")


def omml_tex(element: etree._Element) -> str:
    """The TeX for one OMML element, such as a whole <m:oMath>."""
    name = _name(element)
    if name.endswith("Pr"):
        return ""
    if name == "r":
        text = "".join(t.text or "" for t in element if _name(t) == "t")
        return "\\" + text if text in FUNCTIONS else chars_tex(text)
    if name == "f":
        return rf"\frac{{{_part(element, 'num')}}}{{{_part(element, 'den')}}}"
    if name == "sSup":
        return f"{{{_part(element, 'e')}}}^{{{_part(element, 'sup')}}}"
    if name == "sSub":
        return f"{{{_part(element, 'e')}}}_{{{_part(element, 'sub')}}}"
    if name == "sSubSup":
        base, low, high = (_part(element, part) for part in ("e", "sub", "sup"))
        return f"{{{base}}}_{{{low}}}^{{{high}}}"
    if name == "rad":
        degree = _part(element, "deg")
        root = rf"\sqrt[{degree}]" if degree else r"\sqrt"
        return f"{root}{{{_part(element, 'e')}}}"
    if name == "nary":
        operator = chars_tex(_option(element, "naryPr", "chr") or chr(0x222B))
        low, high = _part(element, "sub"), _part(element, "sup")
        bounds = (f"_{{{low}}}" if low else "") + (f"^{{{high}}}" if high else "")
        return f"{operator}{bounds} {_part(element, 'e')}".strip()
    if name == "d":
        opening = _option(element, "dPr", "begChr")
        closing = _option(element, "dPr", "endChr")
        separator = chars_tex(_option(element, "dPr", "sepChr") or "|")
        inside = f" {separator} ".join(omml_tex(e) for e in element if _name(e) == "e")
        left = fence_tex("(" if opening is None else opening)
        right = fence_tex(")" if closing is None else closing)
        return rf"\left{left} {inside} \right{right}"
    if name == "func":
        return f"{_part(element, 'fName')} {_part(element, 'e')}".strip()
    if name == "limLow":
        base, low = _part(element, "e"), _part(element, "lim")
        if base.startswith(LIMITS):
            return f"{base}_{{{low}}}"
        return rf"\underset{{{low}}}{{{base}}}"
    if name == "limUpp":
        return rf"\overset{{{_part(element, 'lim')}}}{{{_part(element, 'e')}}}"
    if name == "acc":
        mark = MARKS.get(_option(element, "accPr", "chr") or chr(0x302), "hat")
        return rf"\{mark}{{{_part(element, 'e')}}}"
    if name == "bar":
        position = _option(element, "barPr", "pos") or "bot"
        line = r"\overline" if position == "top" else r"\underline"
        return f"{line}{{{_part(element, 'e')}}}"
    if name == "eqArr":
        rows = [omml_tex(e) for e in element if _name(e) == "e"]
        return r"\begin{aligned} " + r" \\ ".join(rows) + r" \end{aligned}"
    if name == "m":
        rows = [omml_tex(row) for row in element if _name(row) == "mr"]
        return r"\begin{matrix} " + r" \\ ".join(rows) + r" \end{matrix}"
    if name == "mr":
        return " & ".join(omml_tex(e) for e in element if _name(e) == "e")
    parts = [omml_tex(child) for child in element]
    return " ".join(part for part in parts if part)

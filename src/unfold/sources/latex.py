"""LaTeX files: each section becomes an anchor, and formulas keep their TeX.

The reader never runs TeX. It follows `\\input`, `\\include`, and `\\subfile` only
to `.tex` files inside the main file's folder, because a stranger's file could
otherwise pull private files into the source, and from there to the model. It
expands the document's own macros, so that each formula stands alone. Commands
that it does not know keep only their text.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from unfold.sources import Meta, SourceDocument
from unfold.sources.web import _document

DEPTH = 10  # how deep includes may nest
READS = 500  # how many files one document may include
PASSES = 50  # how many rounds of macro expansion
CODE = re.compile(
    r"\\begin\{(verbatim\*?|Verbatim|BVerbatim|semiverbatim|lstlisting|minted)\}(.*?)\\end\{\1\}",
    re.DOTALL,
)
VERB = re.compile(r"\\verb\*?([^\sA-Za-z*])(.*?)\1")
# A comment also ends its line, unless a blank line follows, as in TeX.
COMMENT = re.compile(r"(?<!\\)((?:\\\\)*)%.*(?:\n(?![ \t]*\n)[ \t]*)?")
SKIPPED = re.compile(
    r"\\begin\{comment\}.*?\\end\{comment\}|\\iffalse(?![A-Za-z@]).*?\\fi(?![A-Za-z@])",
    re.DOTALL,
)
INCLUDE = re.compile(r"\\(?:input|include|subfile)\{([^{}]*)\}")
DOCUMENT = re.compile(r"\\begin\{document\}(.*?)(?:\\end\{document\}|$)", re.DOTALL)
WORD = re.compile(r"\\[A-Za-z@]+")
CONTROL = re.compile(r"\\(?:[A-Za-z@]+|.)", re.DOTALL)
DEFINE = re.compile(
    r"\\(newcommand|renewcommand|providecommand|DeclareRobustCommand"
    r"|DeclareMathOperator|[gex]?def)(?![A-Za-z@])(\*?)"
)
PARAMETERS = re.compile(r"(?:#\d)*")
DISPLAY = {
    "equation": "",
    "displaymath": "",
    "align": "aligned",
    "flalign": "aligned",
    "eqnarray": "aligned",
    "alignat": "alignedat",
    "gather": "gathered",
    "multline": "gathered",
}
MATH = re.compile(
    r"\\begin\{(" + "|".join(DISPLAY) + r")(\*?)\}(.*?)\\end\{\1\2\}"
    r"|\$\$(.+?)\$\$|\\\[(.+?)\\\]|(?<!\\)\$(.+?)(?<!\\)\$|\\\((.+?)\\\)",
    re.DOTALL,
)
NUMBERING = re.compile(
    r"\\(?:label\{[^{}]*\}|nonumber(?![A-Za-z@])|notag(?![A-Za-z@]))"
)
LINEBREAK = re.compile(r"\\\\\*?(?:\[[^\]]*\])?|\\(?:newline|linebreak)(?![A-Za-z@])")
ESCAPED = re.compile(r"\\([%&_{}$#])")
PLAIN = {"%": "%", "&": "&", "_": "_", "{": "{", "}": "}"}
SECTIONS = {
    "part": "#",
    "chapter": "#",
    "section": "##",
    "subsection": "###",
    "subsubsection": "####",
}
Render = Callable[[list[str]], str]
INLINE: dict[str, tuple[int, Render]] = {
    "footnote": (1, lambda v: f" ({v[0]})"),
    **dict.fromkeys(
        ["cite", "citep", "citet", "citealp", "parencite", "textcite", "autocite"],
        (1, lambda v: f"[{v[0]}]"),
    ),
    "eqref": (1, lambda v: f"({v[0]})"),
    **dict.fromkeys(
        ["ref", "autoref", "cref", "Cref", "pageref", "nameref"], (1, lambda v: v[0])
    ),
    **dict.fromkeys(
        "label index vspace hspace includegraphics bibliography bibliographystyle "
        "pagestyle thispagestyle color title author date thanks documentclass "
        "usepackage".split(),
        (1, lambda v: ""),
    ),
    **dict.fromkeys(["setlength", "setcounter", "addtocounter"], (2, lambda v: "")),
}
ENVIRONMENT = re.compile(r"\\(begin|end)\{([A-Za-z]+\*?)\}")
SYMBOLS = [
    (re.compile(r"\\(?:ldots|dots|textellipsis)(?![A-Za-z@])"), "..."),
    (re.compile(r"\\(La)?TeX(?![A-Za-z@])"), r"\1TeX"),
    (re.compile(r"``|''"), '"'),
    (re.compile(r"\\par(?![A-Za-z@])"), "\n\n"),
    (re.compile(r"~|\\[,;: ]"), " "),
]
LEFTOVER = re.compile(r"\\(?:[A-Za-z@]+\*?(?:\[[^\]\n]*\])?|[^A-Za-z\s\0])")
KEPT = re.compile("\0(\\d+)\0")
SPACE = re.compile(r"[ \t]*(?:\n[ \t]*)?")
# Commands that set up layout or style: each loses all its arguments.
STYLE = re.compile(
    r"\\(?:newenvironment|renewenvironment|definecolor|colorlet|newcounter|newlength"
    r"|addtolength|titleformat|titlespacing|fancyhead|fancyfoot|fancyhf|mdfdefinestyle"
    r"|hypersetup|geometry|captionsetup|lstset|tcbset|usetikzlibrary|pgfplotsset"
    r"|graphicspath|theoremstyle|newtheoremstyle|numberwithin)\*?(?![A-Za-z@])"
)


@dataclass(frozen=True)
class Macro:
    """A macro that the document defines."""

    arguments: int
    default: str | None  # the first argument's default, when it is optional
    body: str


class _Kept:
    """Text set aside, such as formulas and code, so that later edits leave it alone."""

    def __init__(self) -> None:
        self.parts: list[str] = []

    def __call__(self, text: str) -> str:
        self.parts.append(text)
        return f"\0{len(self.parts) - 1}\0"

    def restore(self, text: str) -> str:
        while KEPT.search(text):
            text = KEPT.sub(lambda match: self.parts[int(match.group(1))], text)
        return text


def _shield(text: str, keep: _Kept) -> str:
    """Set code aside, so that no later step reads the commands that it shows."""
    return VERB.sub(
        lambda m: keep(m.group(0)), CODE.sub(lambda m: keep(m.group(0)), text)
    )


def _body(text: str) -> str:
    """The text inside the document environment, or all of it when there is none."""
    match = DOCUMENT.search(text)
    return match.group(1) if match else text


def _target(root: Path, name: str) -> Path | None:
    """The .tex file that an include names, or None when it does not exist."""
    if not name:
        return None
    path = root / name
    if path.suffix != ".tex":
        path = path.with_name(f"{path.name}.tex")
    path = path.resolve()
    if not path.is_relative_to(root) or any(
        part.startswith(".") for part in path.relative_to(root).parts
    ):
        raise ValueError(
            f"{name} lies outside the main file's folder, or in a hidden folder. "
            "Copy it into that folder, and run ingest again"
        )
    return path if path.is_file() else None


def gather(main: Path) -> str:
    """The main file's text without comments, with each include replaced by its file."""
    root = main.resolve().parent
    reads = 0

    def read(chain: tuple[Path, ...]) -> str:
        nonlocal reads
        reads += 1
        if reads > READS or len(chain) > DEPTH:
            raise ValueError(f"includes go past {READS} files or {DEPTH} levels")
        keep = _Kept()
        text = chain[-1].read_text(encoding="utf-8", errors="replace").replace("\0", "")
        text = SKIPPED.sub("", COMMENT.sub(r"\1", _shield(text, keep)))
        if len(chain) > 1:
            text = _body(text)

        def include(match: re.Match[str]) -> str:
            target = _target(root, match.group(1).strip())
            if target is None:
                return ""
            if target in chain:
                raise ValueError(f"{target.name} includes itself")
            return read((*chain, target))

        return keep.restore(INCLUDE.sub(include, text))

    return read((main.resolve(),))


def _skip(text: str, at: int) -> int:
    """The index after spaces and at most one line break, as TeX reads arguments."""
    space = SPACE.match(text, at)
    return space.end() if space else at


def _group(text: str, at: int) -> tuple[str, int] | None:
    """The {braced} group at `at`, after spaces: its inside and the index after it."""
    start = _skip(text, at)
    if not text.startswith("{", start):
        return None
    depth, index = 0, start
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        depth += {"{": 1, "}": -1}.get(char, 0)
        if depth == 0:
            return text[start + 1 : index], index + 1
        index += 1
    return None


def _optional(text: str, at: int) -> tuple[str, int] | None:
    """The [bracketed] argument at `at`, after spaces: its inside and the index after it."""
    start = _skip(text, at)
    if not text.startswith("[", start):
        return None
    depth = 0
    for index in range(start + 1, len(text)):
        depth += {"{": 1, "}": -1}.get(text[index], 0)
        if text[index] == "]" and depth == 0:
            return text[start + 1 : index], index + 1
    return None


def _argument(text: str, at: int) -> tuple[str, int] | None:
    """One macro argument: a braced group, a control sequence, or one character."""
    group = _group(text, at)
    if group is not None:
        return group
    start = _skip(text, at)
    if start >= len(text) or text[start] in "{}":
        return None
    control = CONTROL.match(text, start)
    return (control.group(0), control.end()) if control else (text[start], start + 1)


def _name(text: str, at: int) -> tuple[str, int] | None:
    """The macro that a definition names, written {\\name} or \\name."""
    group = _group(text, at)
    if group is not None:
        inside = group[0].strip()
        return (inside[1:], group[1]) if WORD.fullmatch(inside) else None
    word = WORD.match(text, _skip(text, at))
    return (word.group(0)[1:], word.end()) if word else None


def _macro(text: str, at: int, kind: str, star: str) -> tuple[str, Macro, int] | None:
    """One definition from `at`: the macro's name, the macro, and where it ends."""
    named = _name(text, at)
    if named is None:
        return None
    name, at = named
    arguments, default = 0, None
    if kind.endswith("def"):
        parameters = PARAMETERS.match(text, at)
        if parameters is not None:
            arguments, at = parameters.group(0).count("#"), parameters.end()
    elif kind != "DeclareMathOperator" and (count := _optional(text, at)) is not None:
        if not count[0].strip().isdigit():
            return None
        arguments, at = int(count[0]), count[1]
        if (optional := _optional(text, at)) is not None:
            default, at = optional
    body = _group(text, at)
    if body is None:
        return None
    if kind == "DeclareMathOperator":
        return name, Macro(0, None, f"\\operatorname{star}{{{body[0]}}}"), body[1]
    return name, Macro(arguments, default, body[0]), body[1]


def definitions(text: str) -> tuple[str, dict[str, Macro]]:
    """The text without its macro definitions, and the macros it defines."""
    macros: dict[str, Macro] = {}
    parts: list[str] = []
    index = 0
    while (match := DEFINE.search(text, index)) is not None:
        found = _macro(text, match.end(), match.group(1), match.group(2))
        if found is None:  # a form this reader does not know, so it stays as written
            parts.append(text[index : match.end()])
            index = match.end()
            continue
        name, macro, end = found
        if match.group(1) != "providecommand" or name not in macros:
            macros[name] = macro
        parts.append(text[index : match.start()])
        index = end
    parts.append(text[index:])
    return "".join(parts), macros


def _substitute(body: str, values: list[str]) -> str:
    """The body with #1, #2, and so on replaced by the argument values."""

    def value(number: re.Match[str]) -> str:
        position = int(number.group(1))
        return values[position - 1] if 0 < position <= len(values) else ""

    return re.sub(r"#(\d)", value, body)


def _expand_once(text: str, use: re.Pattern[str], macros: dict[str, Macro]) -> str:
    parts: list[str] = []
    index = 0
    while (match := use.search(text, index)) is not None:
        macro, at = macros[match.group(1)], match.end()
        values: list[str] = []
        if macro.default is not None:
            optional = _optional(text, at)
            value, at = optional if optional is not None else (macro.default, at)
            values.append(value)
        while len(values) < macro.arguments and (argument := _argument(text, at)):
            value, at = argument
            values.append(value)
        if len(values) < macro.arguments:  # too few arguments, so it stays as written
            parts.append(text[index : match.end()])
            index = match.end()
            continue
        parts.append(text[index : match.start()] + _substitute(macro.body, values))
        index = at
    parts.append(text[index:])
    return "".join(parts)


def expand(text: str, macros: dict[str, Macro]) -> str:
    """Replace each use of the document's macros with its body, round after round."""
    if not macros:
        return text
    names = "|".join(sorted(map(re.escape, macros), key=len, reverse=True))
    use = re.compile(rf"\\({names})(?![A-Za-z@])")
    limit = 4 * len(text) + 100_000
    for _ in range(PASSES):
        expanded = _expand_once(text, use, macros)
        if expanded == text:
            return text
        if len(expanded) > limit:
            break
        text = expanded
    raise ValueError("the document's macros expand without end")


def _fence(environment: str, body: str) -> str:
    """A verbatim block as fenced code, with its language when the block names one."""
    language = ""
    options = _optional(body, 0) if body.startswith("[") else None
    if environment not in ("verbatim", "verbatim*", "semiverbatim") and options:
        found = re.search(r"language=\{?(\w+)", options[0])
        language, body = (found.group(1).lower() if found else ""), body[options[1] :]
    if environment == "minted" and body.startswith("{") and (name := _group(body, 0)):
        language, body = name[0].strip().lower(), body[name[1] :]
    code = body.strip("\n")
    return f"```{language}\n{code}\n```"


def _formula(match: re.Match[str], keep: _Kept) -> str:
    environment, _, body, double, bracket, single, paren = match.groups()
    if single is not None or paren is not None:
        return keep(f"${(single if single is not None else paren).strip()}$")
    inside = NUMBERING.sub("", body if environment else double or bracket).strip()
    if wrapper := DISPLAY.get(environment or "", ""):
        inside = f"\\begin{{{wrapper}}}\n{inside}\n\\end{{{wrapper}}}"
    return "\n\n" + keep(f"$$\n{inside}\n$$") + "\n\n"


def _replace(text: str, name: str, count: int, render: Render) -> str:
    """Replace each `\\name[...]{a}{b}` with render(["a", "b"]), skipping [options]."""
    use = re.compile(rf"\\{name}\*?(?![A-Za-z@])")
    parts: list[str] = []
    index = 0
    while (match := use.search(text, index)) is not None:
        at = match.end()
        while (optional := _optional(text, at)) is not None:
            at = optional[1]
        values: list[str] = []
        while len(values) < count and (group := _group(text, at)) is not None:
            values.append(group[0])
            at = group[1]
        if len(values) < count:
            parts.append(text[index : match.end()])
            index = match.end()
            continue
        parts.append(text[index : match.start()] + render(values))
        index = at
    parts.append(text[index:])
    return "".join(parts)


def _heading(marks: str, title: str) -> str:
    title = " ".join(title.split())
    return f"\n\n{marks} {title}\n\n" if title else "\n\n"


def _style(text: str) -> str:
    """Drop each style command with every argument that follows it."""
    parts: list[str] = []
    index = 0
    while (match := STYLE.search(text, index)) is not None:
        at = match.end()
        while (found := _group(text, at) or _optional(text, at)) is not None:
            at = found[1]
        parts.append(text[index : match.start()])
        index = at
    parts.append(text[index:])
    return "".join(parts)


def _commands(text: str) -> str:
    """Sections become headings, and references become text, inner ones too."""
    for _ in range(3):
        before = text
        for name, marks in SECTIONS.items():
            text = _replace(text, name, 1, lambda v, marks=marks: _heading(marks, v[0]))
        for name, (count, render) in INLINE.items():
            text = _replace(text, name, count, render)
        if text == before:
            break
    return text


def latex_markdown(text: str) -> str:
    """A LaTeX document, with its includes already in place, as Markdown."""
    keep = _Kept()
    text = text.replace("\0", "")
    text = CODE.sub(
        lambda m: "\n\n" + keep(_fence(m.group(1), m.group(2))) + "\n\n", text
    )
    text = VERB.sub(lambda m: keep(f"`{m.group(2)}`"), text)
    text, macros = definitions(SKIPPED.sub("", COMMENT.sub(r"\1", text)))
    text = expand(_body(text), macros)
    text = MATH.sub(lambda m: _formula(m, keep), text)
    text = _replace(text, "ensuremath", 1, lambda v: keep(f"${v[0]}$"))
    text = LINEBREAK.sub("\n", text)
    text = ESCAPED.sub(lambda m: keep(PLAIN.get(m.group(1), "\\" + m.group(1))), text)
    text = ENVIRONMENT.sub("\n\n", _commands(_style(text)))
    for pattern, replacement in SYMBOLS:
        text = pattern.sub(replacement, text)
    text = LEFTOVER.sub("", re.sub(r"\}\s*\{", "} {", text))
    text = text.replace("{", "").replace("}", "")
    lines = (" ".join(line.split()) for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    return keep.restore(text) + "\n"


def read_latex(path: Path, meta: Meta) -> SourceDocument:
    return _document(latex_markdown(gather(path)), meta, "tex")

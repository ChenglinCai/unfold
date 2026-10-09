"""LaTeX files become Markdown: sections become anchors, and formulas keep their TeX."""

from pathlib import Path

import pytest

from unfold.cli import main
from unfold.sources import Meta, load
from unfold.sources.latex import latex_markdown, read_latex

META = Meta(
    id="ls", title="Least squares", family="textbook", origin="ls.tex", license=None
)
FENCE = "```"
DOCUMENT = r"""\documentclass{article}
\usepackage{amsmath}
\title{Least squares}
\begin{document}
\maketitle
We fit a line. % a private note
\section{The model}
Each $y_i \in \mathbb{R}$ is a noisy linear function of $x_i$.
\begin{equation}\label{eq:model}
  y = X\beta + \varepsilon
\end{equation}
\subsection*{Residuals}
A gap of 5\% is small.\\% a second note
The rest is noise.
\iffalse An old draft. \fi
\end{document}
"""


def test_sections_and_formulas_survive_and_the_rest_goes() -> None:
    text = latex_markdown(DOCUMENT)

    assert "We fit a line." in text
    assert "## The model" in text and "### Residuals" in text
    assert r"$y_i \in \mathbb{R}$" in text
    assert "$$\ny = X\\beta + \\varepsilon\n$$" in text
    assert "A gap of 5% is small." in text and "The rest is noise." in text
    for gone in ("private note", "second note", "old draft", "usepackage", "label"):
        assert gone not in text


def test_unknown_commands_keep_only_their_text() -> None:
    text = latex_markdown(
        "Called the \\termsub{bell curve}{normal curve}\\index{normal}%\n"
        ", or \\chaptertitle[30]{Gauss}.\n"
        "\\definecolor{sea}{rgb}{0,0,1}\\titleformat{\\chapter}[display]{\\large}{#1}\n"
        "\\chapter*{}\n\n{Braces} stay text.\n"
    )

    assert (
        text == "Called the bell curve normal curve, or Gauss.\n\nBraces stay text.\n"
    )


def test_the_documents_own_macros_expand() -> None:
    text = latex_markdown(
        r"""\newcommand{\norm}[1]{\lVert #1 \rVert}
\newcommand{\inner}[2][x]{\langle #1, #2 \rangle}
\renewcommand\vec[1]{\mathbf{#1}}
\DeclareMathOperator*{\argmin}{arg\,min}
\def\E{\mathbb{E}}
\newcommand{\Rn}{\ensuremath{\mathbb{R}^n}}
Fit $\argmin_w \E\norm{\vec w}$ with $\inner{y}$ and $\inner[a]{b}$ in \Rn{} here.
"""
    )

    assert r"$\operatorname*{arg\,min}_w \mathbb{E}\lVert \mathbf{w} \rVert$" in text
    assert r"$\langle x, y \rangle$" in text and r"$\langle a, b \rangle$" in text
    assert r"in $\mathbb{R}^n$ here." in text
    assert "newcommand" not in text and "def" not in text


def test_macros_that_expand_forever_fail() -> None:
    with pytest.raises(ValueError, match="expand"):
        latex_markdown("\\newcommand{\\twice}{\\twice\\twice}\n$\\twice$")


def test_code_stays_as_written() -> None:
    text = latex_markdown(
        "\\begin{lstlisting}[language=Python]\nx = 50 % 7  {not a group}\n"
        "\\end{lstlisting}\nRun \\verb|f(x) % 2| once.\n"
    )

    assert f"{FENCE}python\nx = 50 % 7  {{not a group}}\n{FENCE}" in text
    assert "Run `f(x) % 2` once." in text


def test_includes_inside_the_folder_are_followed(tmp_path: Path) -> None:
    (tmp_path / "chapters").mkdir()
    (tmp_path / "main.tex").write_text(
        "\\begin{document}\n\\input{means}\n\\include{chapters/spread}\n"
        "\\input{missing}\n% \\input{commented}\n\\end{document}\n"
    )
    (tmp_path / "means.tex").write_text("\\section{Means}\nThe average of draws.\n")
    (tmp_path / "commented.tex").write_text("\\section{Commented}\n")
    (tmp_path / "chapters" / "spread.tex").write_text(
        "\\documentclass[../main.tex]{subfiles}\n\\begin{document}\n"
        "\\section{Spread}\nHow far draws fall.\n\\end{document}\n"
    )

    doc = read_latex(tmp_path / "main.tex", META)

    assert [a.id for a in doc.anchors] == ["means", "spread"]
    assert doc.profile["format"] == "tex"


def test_code_that_shows_latex_stays_code(tmp_path: Path) -> None:
    (tmp_path / "main.tex").write_text(
        "\\begin{document}\n\\section{Start}\nPut \\verb|\\begin{document}| first.\n"
        "\\begin{semiverbatim}\n\\begin{document}\n\\end{semiverbatim}\n"
        "\\input{more}\n\\end{document}\n"
    )
    (tmp_path / "more.tex").write_text(
        "\\documentclass{beamer}\n\\begin{document}\n\\section{More}\n"
        "\\begin{Verbatim}\n\\end{document}\n\\end{Verbatim}\n"
        "A second part.\n\\end{document}\n"
    )

    doc = read_latex(tmp_path / "main.tex", META)

    assert [a.id for a in doc.anchors] == ["start", "more"]
    assert "Put `\\begin{document}` first." in doc.text()
    assert "A second part." in doc.text()


@pytest.mark.parametrize("kind", ["parent", "absolute", "link", "hidden"])
def test_includes_cannot_leave_the_folder(tmp_path: Path, kind: str) -> None:
    folder = tmp_path / "notes"
    (folder / ".private").mkdir(parents=True)
    secret = tmp_path / "secret.tex"
    secret.write_text("The secret.\n")
    (folder / ".private" / "keys.tex").write_text("The keys.\n")
    (folder / "link.tex").symlink_to(secret)
    name = {
        "parent": "../secret",
        "absolute": str(secret),
        "link": "link",
        "hidden": ".private/keys",
    }[kind]
    (folder / "main.tex").write_text(f"\\input{{{name}}}\n")

    with pytest.raises(ValueError, match="outside"):
        read_latex(folder / "main.tex", META)


def test_includes_follow_only_tex_files(tmp_path: Path) -> None:
    (tmp_path / "key").write_text("The key.\n")
    (tmp_path / "main.tex").write_text("Notes.\n\\input{key}\n")

    doc = read_latex(tmp_path / "main.tex", META)

    assert "key" not in doc.text().lower()


def test_a_file_that_includes_itself_fails(tmp_path: Path) -> None:
    (tmp_path / "main.tex").write_text("\\input{main}\n")

    with pytest.raises(ValueError, match="includes itself"):
        read_latex(tmp_path / "main.tex", META)


def test_ingest_reads_a_latex_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "ls.tex"
    path.write_text(DOCUMENT)
    out = tmp_path / "sources"

    assert main(["ingest", str(path), "--out", str(out), "--license", "CC BY 4.0"]) == 0

    doc = load(out / "ls")
    assert doc.family == "textbook"
    assert [a.id for a in doc.anchors] == ["intro", "the-model", "residuals"]

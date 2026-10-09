"""The `unfold ingest` subcommand, as `specs/003-source-understanding/contracts/cli.md` describes.

The readers load only when ingest runs, so `unfold lint` still starts fast.
"""

import argparse
import re
import shutil
import sys
import tempfile
import tomllib
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path

from unfold.sources import ANCHOR_ID, Meta, SourceDocument
from unfold.sources.scan import IMAGES

FAMILIES = ["textbook", "slides", "web", "recording", "topic"]
SUBJECTS = ["math", "computer-science", "statistics", "economics", "finance"]
TEXT = {".md", ".markdown", ".txt"}
NOTEBOOKS = {".ipynb"}
LATEX = {".tex"}
BOOKS = {".epub"}
PAGES = {".html", ".htm"}
AUDIO = {".ogg", ".oga", ".mp3", ".wav", ".m4a", ".aiff", ".flac", ".mp4", ".webm"}
KNOWN = {".pdf", ".pptx"} | TEXT | NOTEBOOKS | LATEX | BOOKS | PAGES | AUDIO | IMAGES
CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "text/html": ".html",
    "text/markdown": ".md",
    "text/plain": ".txt",
    "application/x-tex": ".tex",
    "text/x-tex": ".tex",
    "application/epub+zip": ".epub",
    "audio/ogg": ".ogg",
    "audio/mpeg": ".mp3",
    "audio/wav": ".wav",
}
USER_AGENT = "unfold/0.1 (+https://github.com/ChenglinCai/unfold)"
MAX_BYTES = 500 * 2**20

Reader = Callable[[Path, Meta], SourceDocument]


class UsageError(Exception):
    """A problem with the options, not with the source."""


def add_ingest_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    ingest = commands.add_parser("ingest", help="Turn a source into a source document.")
    ingest.add_argument(
        "source",
        metavar="SOURCE",
        help="A file, a URL, or a phrase with --family topic.",
    )
    ingest.add_argument(
        "--out", required=True, metavar="DIR", help="A private folder for sources."
    )
    ingest.add_argument("--id", help="The folder name. Default: the source's name.")
    ingest.add_argument("--family", choices=FAMILIES)
    ingest.add_argument("--title")
    ingest.add_argument(
        "--license",
        help="Such as 'CC BY-SA 4.0'. Unknown licenses keep outputs private.",
    )
    ingest.add_argument("--owner", default="")
    ingest.add_argument("--attribution", default="")
    ingest.add_argument("--subject", choices=SUBJECTS)
    ingest.set_defaults(run=run_ingest)


def run_ingest(args: argparse.Namespace) -> int:
    out = Path(args.out).resolve()
    repo = unfold_checkout(out)
    if repo is not None:
        return fail(
            f"{out} is inside the unfold repo at {repo}. Use a private folder.", 2
        )
    if args.id is not None and not ANCHOR_ID.match(args.id):
        return fail(f"bad --id {args.id!r}: use lower-case letters, digits, and -", 2)
    with tempfile.TemporaryDirectory() as scratch:
        try:
            doc, original = ingest(args, Path(scratch))
        except UsageError as problem:
            return fail(str(problem), 2)
        except Exception as problem:  # each reader fails in its own way
            return fail(f"could not read {args.source}: {problem}", 1)
        if original is not None:
            doc.files["original"] = original.name
        folder = doc.save(out)
        if original is not None:
            shutil.move(original, folder / original.name)
    missing = doc.profile.get("missing")
    if isinstance(missing, list) and missing:
        print(
            f"unfold ingest: skipped {len(missing)} includes that are not in the file's "
            f"folder: {', '.join(map(str, missing))}. If the file belongs to a larger "
            "project, ingest the project's main file.",
            file=sys.stderr,
        )
    print(folder)
    return 0


def ingest(
    args: argparse.Namespace, scratch: Path
) -> tuple[SourceDocument, Path | None]:
    """Read the source. A download lands in scratch, and is returned as the original."""
    if args.family == "topic":
        from unfold.sources import topic

        return topic.read(describe(args, args.source, "topic")), None
    original = None
    if args.source.startswith(("http://", "https://")):
        stem, suffix = url_name(args.source)
        data, content_type = download(args.source)
        if suffix.lower() not in KNOWN:
            suffix = CONTENT_TYPES.get(content_type, "")
        path = original = scratch / f"original{suffix}"
        path.write_bytes(data)
    else:
        path = Path(args.source)
        if not path.is_file():
            raise FileNotFoundError(f"{path} is not a file")
        stem, suffix = path.stem, path.suffix
    family, reader = choose(suffix, args.family, path)
    return reader(path, describe(args, stem, family)), original


def choose(suffix: str, family: str | None, path: Path) -> tuple[str, Reader]:
    """Pick the reader for a file type, and the family that the type implies."""
    from unfold.sources import deck, epub, latex, notebook, pdf, recording, scan, web

    suffix = suffix.lower()
    if suffix == ".pdf":
        return family or "textbook", pdf.read
    if suffix == ".pptx":
        return family or "slides", deck.read
    if suffix in IMAGES:
        return family or "slides", scan.read
    if suffix in TEXT:
        return family or "web", web.read_markdown
    if suffix in NOTEBOOKS:
        return family or "web", notebook.read_notebook
    if suffix in BOOKS:
        return family or "textbook", epub.read_epub
    if suffix in LATEX:
        return family or latex.family(path), latex.read_latex
    if suffix in PAGES:
        return family or "web", web.read_page
    if suffix in AUDIO:
        return family or "recording", recording.read
    raise UsageError(f"unfold has no reader for {suffix or 'files without a suffix'}")


def describe(args: argparse.Namespace, name: str, family: str) -> Meta:
    return Meta(
        id=args.id or slug(name),
        title=args.title or name.replace("_", " "),
        family=family,
        origin=args.source,
        license=args.license,
        owner=args.owner,
        attribution=args.attribution,
        subject=args.subject or "unknown",
    )


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "source"


def url_name(url: str) -> tuple[str, str]:
    """Split the last part of a URL's path into its stem and suffix."""
    last = urllib.parse.urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1]
    path = Path(urllib.parse.unquote(last))
    return path.stem, path.suffix


def download(url: str) -> tuple[bytes, str]:
    """Fetch a URL, and return its bytes and its content type."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
        content_type = response.headers.get_content_type()
    if len(data) > MAX_BYTES:
        raise ValueError(f"the download is larger than {MAX_BYTES // 2**20} MB")
    return data, content_type


def unfold_checkout(path: Path) -> Path | None:
    """The unfold source tree that holds path, if any. Sources never go there."""
    for folder in (path, *path.parents):
        project = folder / "pyproject.toml"
        if project.is_file():
            with project.open("rb") as handle:
                name = tomllib.load(handle).get("project", {}).get("name")
            if name == "unfold":
                return folder
    return None


def fail(message: str, code: int) -> int:
    print(f"unfold ingest: {message}", file=sys.stderr)
    return code

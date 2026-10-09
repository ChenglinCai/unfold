"""Pages: a review page for one series, and a gallery of public series.

Both are static HTML with relative links, so they open straight from disk.
The gallery only ever copies series whose every source allows public outputs.
"""

import argparse
import re
import shutil
from html import escape
from pathlib import Path

import yaml

from unfold.episodes.subtitles import vtt_text
from unfold.evals import CHECKS, count_flags, custom_share, evaluate, share_line
from unfold.script import load_script
from unfold.sources import load

STYLE = """<style>
body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2em auto;
       padding: 0 1em; background: #101318; color: #ece7dd; }
a { color: #5fb3e4; } img, video { max-width: 100%; }
.flag { color: #f2c14e; } td, th { padding: 4px 10px; text-align: left; }
</style>"""


PLAIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*")
# Each subtitle file beside an episode, with its language code and menu label.
TRACKS = (("episode.srt", "en", "English"), ("episode.zh.srt", "zh-Hans", "中文"))


def plain(name: object) -> bool:
    """Whether an id is safe in a path and in HTML: letters, digits, and dashes."""
    return isinstance(name, str) and PLAIN.fullmatch(name) is not None


def _yaml(path: Path) -> dict[str, object]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None
    return data if isinstance(data, dict) else {}


def _episodes(folder: Path) -> list[dict[str, str]]:
    listed = _yaml(folder / "plan.yaml").get("episodes")
    if not isinstance(listed, list):
        return []
    return [
        e
        for e in listed
        if isinstance(e, dict) and plain(e.get("id")) and (folder / e["id"]).is_dir()
    ]


def _tracks(folder: Path, base: str) -> str:
    """Write each subtitle file as WebVTT, which browsers play, and link it to a player."""
    tracks = []
    for name, language, label in TRACKS:
        srt = folder / name
        if not srt.is_file():
            continue
        vtt = srt.with_suffix(".vtt")
        vtt.write_text(vtt_text(srt.read_text(encoding="utf-8")), encoding="utf-8")
        default = "" if tracks else " default"
        tracks.append(
            f'<track kind="subtitles" srclang="{language}" label="{label}" '
            f'src="{base}/{vtt.name}"{default}>'
        )
    return "".join(tracks)


def _page(title: str, body: list[str]) -> str:
    head = f'<meta charset="utf-8"><title>{escape(title)}</title>{STYLE}'
    text = "\n".join(body)
    return f"<!doctype html>\n<html><head>{head}</head><body>\n{text}\n</body></html>\n"


def _heading(series: dict[str, object], folder: Path) -> str:
    """A series' title, or its id when it has no title."""
    return str(series.get("title") or series.get("id", folder.name))


def review_html(folder: Path) -> str:
    series = _yaml(folder / "series.yaml")
    body = [f"<h1>{escape(_heading(series, folder))}</h1>"]
    body.append(f"<p>Audience: {escape(str(series.get('audience', '')))}</p>")
    try:
        verdicts = evaluate(folder)
    except Exception as error:  # a half-built series still gets a page
        verdicts = []
        body.append(f"<p>The checks could not run: {escape(str(error))}</p>")
    rows = []
    for check in CHECKS:
        mine = [v for v in verdicts if v.check == check]
        if mine:
            passed = sum(v.passed for v in mine)
            rows.append(f"<tr><td>{check}</td><td>{passed} of {len(mine)}</td></tr>")
    if rows:
        body.append("<h2>Checks</h2><table>" + "".join(rows) + "</table>")
    failing = [v for v in verdicts if not v.passed]
    if failing:
        items = "".join(
            f"<li>{v.check}: {escape(str(v.subject.relative_to(folder)))}</li>"
            for v in failing
        )
        body.append(f"<ul>{items}</ul>")
    flagged, beats = count_flags(folder)
    body.append(
        f'<p class="flag">{flagged} of {beats} beats are flagged: they cite no anchor, '
        "so a person should check them.</p>"
    )
    body.append(
        f"<p>{escape(share_line(*custom_share(folder)))}, for a person to review.</p>"
    )
    for episode in _episodes(folder):
        body += _episode_html(folder, episode)
    return _page(f"Review: {series.get('id', folder.name)}", body)


def _episode_html(folder: Path, episode: dict[str, str]) -> list[str]:
    name = episode["id"]
    part = [f"<h2>{escape(name)}: {escape(episode.get('title', ''))}</h2>"]
    if (folder / name / "episode.mp4").is_file():
        tracks = _tracks(folder / name, name)
        part.append(f'<video controls src="{name}/episode.mp4">{tracks}</video>')
    if (folder / name / "episode-sheet.png").is_file():
        part.append(f'<img src="{name}/episode-sheet.png" alt="Episode contact sheet">')
    outline = _yaml(folder / name / "outline.yaml")
    segments = outline.get("segments")
    for segment in segments if isinstance(segments, list) else []:
        sid = segment.get("id")
        if not plain(sid) or not (folder / name / sid).is_dir():
            continue
        here = folder / name / sid
        part.append(f"<h3>{escape(sid)}: {escape(str(segment.get('title', '')))}</h3>")
        if (here / "contact-sheet.png").is_file():
            part.append(
                f'<img src="{name}/{sid}/contact-sheet.png" alt="Contact sheet">'
            )
        if (here / "script.md").is_file():
            script = load_script(here / "script.md")
            anchors = script.anchors()
            items = [
                _beat_html(b.cue, b.text, not anchors[b.cue]) for b in script.beats
            ]
            part.append("<ul>" + "".join(items) + "</ul>")
    return part


def _beat_html(cue: str, text: str, flagged: bool) -> str:
    mark = ' class="flag"' if flagged else ""
    note = " (flagged)" if flagged else ""
    return f"<li{mark}><b>{escape(cue)}</b> {escape(text)}{note}</li>"


def public(folder: Path) -> tuple[bool, list[str]]:
    """Whether every source allows public outputs, with each source's attribution.

    It fails closed: a series with no sources, or a right other than true, stays private.
    """
    sources = _yaml(folder / "series.yaml").get("sources")
    if not isinstance(sources, list) or not sources:
        return False, ["the series lists no sources"]
    credits = []
    for name in sources:
        doc = load((folder / str(name)).resolve())
        if doc.rights.get("public_outputs") is not True:
            return False, [f"source {doc.id} keeps its outputs private"]
        fallback = f"{doc.title}, {doc.rights.get('license')}"
        credits.append(str(doc.rights.get("attribution") or fallback))
    return True, credits


def gallery(folders: list[Path], out: Path) -> list[str]:
    """Copy each public series' episodes into a static site, and report each choice."""
    lines, sections = [], []
    for folder in folders:
        spec = _yaml(folder / "series.yaml")
        name = str(spec.get("id", folder.name))
        if not plain(name):
            lines.append(f"skipped {name}: its id is not a plain name")
            continue
        allowed, notes = public(folder)
        if not allowed:
            lines.append(f"skipped {name}: {notes[0]}")
            continue
        heading = f"<h2>{escape(_heading(spec, folder))}</h2>"
        section = [heading] + [f"<p>{escape(n)}</p>" for n in notes]
        for episode in _episodes(folder):
            video = folder / episode["id"] / "episode.mp4"
            if not video.is_file():
                continue
            target = out / name / episode["id"]
            target.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(video, target / "episode.mp4")
            for subtitles, _, _ in TRACKS:
                if (srt := video.with_name(subtitles)).is_file():
                    shutil.copyfile(srt, target / subtitles)
            section.append(f"<h3>{escape(episode.get('title', episode['id']))}</h3>")
            base = f"{name}/{episode['id']}"
            tracks = _tracks(target, base)
            section.append(f'<video controls src="{base}/episode.mp4">{tracks}</video>')
        sections += section
        lines.append(f"included {name}")
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        _page("unfold gallery", ["<h1>Gallery</h1>", *sections])
    )
    return lines


def add_page_commands(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    review = commands.add_parser("review", help="Write a review page for a series.")
    review.add_argument("series", metavar="SERIES")
    review.set_defaults(run=run_review)
    pages = commands.add_parser("gallery", help="Build a static site of public series.")
    pages.add_argument("series", nargs="+", metavar="SERIES")
    pages.add_argument("--out", required=True, metavar="DIR")
    pages.set_defaults(run=run_gallery)


def run_review(args: argparse.Namespace) -> int:
    folder = Path(args.series)
    if not (folder / "series.yaml").is_file():
        print(f"unfold review: {folder} is not a series")
        return 2
    (folder / "review.html").write_text(review_html(folder), encoding="utf-8")
    print(folder / "review.html")
    return 0


def run_gallery(args: argparse.Namespace) -> int:
    for line in gallery([Path(s) for s in args.series], Path(args.out)):
        print(line)
    return 0

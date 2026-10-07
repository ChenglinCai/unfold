"""The `unfold render` subcommand: check every scene, then render in parallel."""

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from unfold.formats import read_data
from unfold.formats.episode import SceneV0
from unfold.script import load_script
from unfold.visuals.render import QUALITIES, current, render_segment, segments


def add_render_command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]",
) -> None:
    command = commands.add_parser(
        "render", help="Render a series' scenes into videos with contact sheets."
    )
    command.add_argument("series", metavar="SERIES")
    command.add_argument("--jobs", type=int, default=3, help="Renders at once.")
    command.add_argument("--quality", choices=sorted(QUALITIES), default="low")
    command.set_defaults(run=run_render)


def run_render(args: argparse.Namespace) -> int:
    from unfold.visuals.scene import check_scene

    found = segments(Path(args.series))
    if not found:
        print(f"unfold render: {args.series} holds no scenes", file=sys.stderr)
        return 2
    failures = []
    for folder in found:
        scene = SceneV0.model_validate(read_data(folder / "scene.yaml"))
        cues = [beat.cue for beat in load_script(folder / "script.md").beats]
        failures += [f"{folder}: {error}" for error in check_scene(scene, cues)]
    if failures:
        print("\n".join(failures))
        print(f"{len(failures)} layout failures, so nothing was rendered")
        return 1
    todo = [folder for folder in found if not current(folder, args.quality)]
    with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        list(pool.map(render_segment, todo, [args.quality] * len(todo)))
    for folder in found:
        print(f"{'rendered' if folder in todo else 'reused':8} {folder}")
    print(f"{len(todo)} rendered, {len(found) - len(todo)} reused, 0 layout failures")
    return 0

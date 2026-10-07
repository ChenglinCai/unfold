"""The `unfold render` subcommand: check every scene, then render in parallel."""

import argparse
import multiprocessing
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
    command.add_argument(
        "--check-audio",
        action="store_true",
        help="Transcribe each voiced segment with Whisper, and compare it with its script.",
    )
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
    # Fresh worker processes: a fork after manim and cairo load can crash on Linux.
    spawn = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=max(1, args.jobs), mp_context=spawn) as pool:
        list(pool.map(render_segment, todo, [args.quality] * len(todo)))
    for folder in found:
        print(f"{'rendered' if folder in todo else 'reused':8} {folder}")
    print(f"{len(todo)} rendered, {len(found) - len(todo)} reused, 0 layout failures")
    stitch(found, todo, args.quality)
    if args.check_audio:
        return check_audio(found)
    return 0


def stitch(found: list[Path], todo: list[Path], quality: str) -> None:
    """Stitch each episode whose segments changed, or that has no video yet."""
    from unfold.episodes.stitch import EPISODE, stitch_episode

    for episode in sorted({folder.parent for folder in found}):
        changed = any(folder.parent == episode for folder in todo)
        if (episode / "outline.yaml").is_file() and (
            changed or not (episode / EPISODE).is_file()
        ):
            print(f"stitched {stitch_episode(episode, quality)}")


def check_audio(found: list[Path]) -> int:
    """Fail when any voiced segment's word error rate passes the limit."""
    import json

    from unfold.episodes.audio import LIMIT
    from unfold.episodes.audio import check_audio as heard

    failures = 0
    for folder in found:
        timing = json.loads((folder / "timing.json").read_text(encoding="utf-8"))
        if timing.get("voice") is None:
            print(f"silent   {folder}: no voice, so no audio check")
            continue
        text = " ".join(b.text for b in load_script(folder / "script.md").beats)
        rate = heard(folder / "segment.mp4", text)
        verdict = "passes" if rate <= LIMIT else "fails"
        failures += rate > LIMIT
        print(f"{verdict:8} {folder}: word error rate {100 * rate:.1f} percent")
    return 1 if failures else 0

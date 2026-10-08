"""The plugin bundles the MCP server and a skill, and the marketplace lists it."""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_the_manifest_names_the_plugin_and_starts_the_server() -> None:
    manifest = json.loads(
        (ROOT / "plugin" / ".claude-plugin" / "plugin.json").read_text()
    )

    assert manifest["name"] == "unfold"
    server = manifest["mcpServers"]["unfold"]
    assert server["args"][-2:] == ["unfold", "mcp"]


def test_the_skill_has_a_name_and_a_description() -> None:
    text = (ROOT / "plugin" / "skills" / "unfold" / "SKILL.md").read_text()
    front = yaml.safe_load(text.split("---\n")[1])

    assert front["name"] == "unfold"
    assert len(front["description"]) > 40


def test_the_marketplace_points_at_the_plugin() -> None:
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())

    [entry] = market["plugins"]
    assert (ROOT / entry["source"] / ".claude-plugin" / "plugin.json").is_file()


def test_the_server_installs_the_extras_that_the_skill_uses() -> None:
    manifest = json.loads(
        (ROOT / "plugin" / ".claude-plugin" / "plugin.json").read_text()
    )
    args = manifest["mcpServers"]["unfold"]["args"]

    package = args[args.index("--from") + 1]

    assert package.startswith("unfold[audio,mcp] @ git+https://")

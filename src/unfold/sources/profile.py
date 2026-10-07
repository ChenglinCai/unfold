"""The source profile: facts that decide how later steps treat a source."""

import re

# Licenses that let anyone publish what we make from the source.
OPEN_LICENSES = {"cc0", "cc-by", "cc-by-sa", "public-domain"}
LOW_WORDS_PER_PAGE = 30
NEEDS = {
    "textbook": "cut",
    "slides": "fill-gaps",
    "scan": "fill-gaps",
    "web": "cut",
    "recording": "clean-up",
    "topic": "fact-check",
}


def license_family(name: str | None) -> str:
    """Reduce a license name to its family, such as 'cc-by-sa' for 'CC BY-SA 3.0'."""
    text = re.sub(r"[\s_]+", "-", (name or "").strip().lower())
    if text.startswith("cc0"):
        return "cc0"
    text = re.sub(r"-?\d+(\.\d+)*$", "", text)
    if text in {"public-domain", "pd"}:
        return "public-domain"
    return text


def public_outputs(name: str | None) -> bool:
    """Whether videos made from the source may be public. Unknown means no."""
    return license_family(name) in OPEN_LICENSES


def rights(
    name: str | None, owner: str = "", attribution: str = ""
) -> dict[str, object]:
    return {
        "license": name or "unknown",
        "owner": owner,
        "attribution": attribution,
        "public_outputs": public_outputs(name),
    }


def quality(words: int, units: int, unit: str) -> dict[str, object]:
    """Words per unit, with a flag when a page holds almost no text."""
    per_unit = round(words / units) if units else 0
    low = unit == "page" and per_unit < LOW_WORDS_PER_PAGE
    return {f"words_per_{unit}": per_unit, "low": low}


def needs(family: str) -> str:
    return NEEDS.get(family, "fill-gaps")

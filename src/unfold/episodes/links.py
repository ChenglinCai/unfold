"""The idea-link check: every idea a segment needs was taught earlier, or is known."""

from unfold.formats.episode import OutlineV0


def check_links(outlines: list[OutlineV0], knows: set[str]) -> list[str]:
    """Walk the episodes in order, and name each required idea that nothing supplies."""
    taught = set(knows)
    errors: list[str] = []
    for outline in outlines:
        for segment in outline.segments:
            errors += [
                f"{outline.episode}/{segment.id} requires {item}, "
                "which nothing earlier establishes"
                for item in segment.requires
                if item not in taught
            ]
            taught |= set(segment.establishes)
    return errors

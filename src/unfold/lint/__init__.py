"""The Narration Standard linter: written, spoken, and strict profiles.

`specs/002-language/` holds the spec, the plan, and the command's contract.
"""

from unfold.lint.prose import paragraphs
from unfold.lint.rules import PROFILES, RULES, Context, Finding

__all__ = ["PROFILES", "Finding", "lint_text"]


def lint_text(
    text: str,
    profile: str = "written",
    path: str = "<text>",
    terms: dict[str, str] | None = None,
) -> list[Finding]:
    """Check text against one profile, and return its findings in line order."""
    chosen = PROFILES[profile]
    context = Context(paragraphs(text), chosen, terms or {})
    findings = [
        Finding(
            rule_id,
            name,
            chosen.severities[rule_id],
            path,
            hit.line,
            hit.excerpt,
            hit.message,
            hit.fix,
        )
        for rule_id, (name, check) in RULES.items()
        if rule_id in chosen.severities
        for hit in check(context)
    ]
    return sorted(findings, key=lambda f: (f.line, f.rule))

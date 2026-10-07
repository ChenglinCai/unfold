# Dependencies

Every dependency, with its license, the reason we need it, and how to remove it. Remove a Python package with `uv remove <name>`.

| Package | Kind | License | Added | Reason |
|---|---|---|---|---|
| manim | runtime | MIT | M0 | Renders every scene |
| pyyaml | runtime | MIT | M1 | Reads the YAML front matter of scripts, and the YAML formats |
| pytest | dev | MIT | M0 | Runs the tests |
| ruff | dev | MIT | M0 | Lints and formats Python |
| pyright | dev | MIT | M0 | Checks types |
| pre-commit | dev | MIT | M0 | Runs the checks before each commit |

System tools: cairo and pkg-config from Homebrew, which manim needs on macOS, and a LaTeX distribution for equations.

# Legacy Pygame Codebase (Archived)

**Status:** Archived / not maintained. Do not run, import, or lint.

This directory holds the original **pygame-era** implementation of P(Doom).
The live game is now **Godot/GDScript** under `godot/` (real tests live in
`godot/tests/`). The Python that remains in the repo is **automation only**
(under `scripts/`, `tools/`, `docs/shared/`) and targets a **Python 3.11
baseline** (see `pyproject.toml`).

## Why these files are here

The files under this directory are pygame-migration debris. Many of them have
**genuine Python syntax errors that fail to compile on every Python version**
(verified on 3.10 and 3.13) — they are not version-only issues, they are simply
broken. Keeping them in the live `tests/` and `tools/` trees made the CI syntax
gate noisy and unactionable, so they were moved out of the linted/compiled tree.

The repo's `.flake8` and `.pre-commit-config.yaml` already exclude `archive/`
and `legacy/`, so nothing under here is linted or compiled by CI.

## Most recent archival batch

28 broken legacy files were relocated from `tests/` and `tools/` into this
directory, preserving their original relative subpath
(e.g. `tests/foo.py` -> `archive/legacy-pygame/tests/foo.py`). Before moving,
the live tree (`godot/`, `scripts/`, remaining `tools/`) was grepped to confirm
none of these modules are imported by active code.

These are kept for historical reference only.

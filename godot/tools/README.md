# Godot-side tools (`godot/tools/`)

GDScript entry points that CI and the Python tooling invoke headlessly. Both of
them are **driven by a script in the repo-root `scripts/` or `tools/` dir** --
neither is meant to be run by hand as part of normal development.

Anything you add here ships inside the `.pck` (Godot packs the entire `godot/`
tree whether referenced or not), so keep this directory to things that actually
run.

## `syntax_walk.gd` + `syntax_walk.tscn` -- the GDScript compile gate

Compile-coverage walker for the syntax gate (issue #1082). It enumerates and
`load()`s every `.gd` in the project, then prints a `SYNTAX_WALK_COMPLETE`
manifest with a file count.

Invoked by **`scripts/run_godot_tests.py`** (`check_syntax()`), which greps the
output for `SCRIPT ERROR` / `Parse Error` and requires the completion marker to
match its own disk glob. The pass/fail decision lives in Python, outside GUT.

It is a **scene**, not a `--script`, on purpose: booting a scene boots the
project normally, so autoloads are initialised and the `class_name` cache is
live. Per-file `--check-only` cannot do this -- it false-failed 186 of 260 files
with "Identifier not found: <autoload>".

```
godot --headless --path godot res://tools/syntax_walk.tscn
```

## `validate_assets_probe.gd` -- asset-import validation

Walks `res://assets`, `load()`s every importable resource, and asserts each one
resolves to a non-null resource of a sane type. Catches a corrupt or undecodable
asset that imports "successfully" but fails to load.

Invoked by **`tools/validate_assets.py`**; run that rather than the probe
directly.

Headless-safe checks only: textures are validated by metadata (`get_width()` /
`get_height()` > 0), **not** by `get_image()` -- VRAM-compressed textures
legitimately discard their CPU image under the headless dummy renderer. So this
proves a resource is structurally loadable; it does not GPU-decode. That last
mile is the human release-build playtest
(`docs/LEADERBOARD_CRASH_DIAGNOSIS.md`).

## Running Godot headless on this project

Read the "Godot writes to Pip's REAL player profile" section of the root
`CLAUDE.md` **before** any headless invocation. The user-data dir derives from
`config/name` in `project.godot`, not from the worktree path, so every worktree
shares one profile and an unisolated run can overwrite live leaderboard data.
Isolation differs by OS (Windows: `APPDATA`; Linux: `XDG_DATA_HOME` -- see
`docs/LAPTOP_DEBIAN_SETUP.md` section 4).

## History

A family of Python-to-Godot port-verification scripts used to live here
(`dev_tool.gd`, `dev_tool_v2.gd`, `dev_tool_minimal.gd`, `quick_test.gd`,
`simple_test.gd`). They were removed in the 2026-08-14 dead-code sweep: they
validated `GameState` against the pygame-era API (`initialize()`,
`advance_turn()`, `end_turn()`, `.seed`, `.staff`), none of which still exists,
so the two that instantiated anything could not run at all. The Python bridge
they existed to cross-check is gone; `scripts/run_godot_tests.py` is the real
gate now.

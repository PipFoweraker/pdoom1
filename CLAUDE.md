# CLAUDE.md — P(Doom)1 agent cheat-sheet

Operational notes for Claude/LLM agents. Keep it short; update in place when a
convention changes. For the systems map read **`docs/ARCHITECTURE.md` FIRST**.

## What this is
Turn-based AI-safety strategy game. **Godot 4.5.1, pure GDScript** (no Python
runtime — the old Python bridge is gone). Python exists only for CI/tooling in
`scripts/` and `tools/`. Windows dev machine; CI is Ubuntu.

## Run the game
- `godot --path godot` (or `make run`). On Pip's machine Godot is
  `C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe`.

## Tests — two tiers, don't conflate them
- **Fast gate (this is what you run for scoped changes):**
  `python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300`
  (`tests/unit`, non-recursive). The runner does the `--import` pass itself.
- **Slow simulation tier:** `--simulation` (`tests/unit/simulation`, full-run /
  replay / determinism, ~3 min). **Non-blocking** in CI — do NOT wait on it for a
  scoped change. Run it only when you touched simulation/economy/replay code.
- **Fresh worktree gotcha:** GUT quits(0) before running anything if the class
  cache is cold. The runner's import pass fixes this; if you invoke Godot/GUT
  directly, run `godot --headless --path godot --import` first. Running headless
  Godot also floods stderr with SCRIPT ERROR class-cache lines on the first pass —
  expected noise, not a real failure.
- `make test` = fast gate; `make run` = game.

## `.import` / `.uid` files — the staging trap
- Both are **tracked on purpose** (Godot 4 convention: `.import` = import
  metadata, `.uid` = stable resource IDs). `godot/.godot/` and `godot/.import/`
  are correctly gitignored; the per-asset `*.import` / `*.uid` files are not.
- Running `--import` **rewrites/touches ~1200 `.import` files** and may emit new
  `.uid` files. **Do NOT stage that churn.** Never `git add -A` / `git add .`.
  Stage only the files you changed (`git add <path>`), or discard the churn with
  `git checkout -- godot/` before committing.

## Commit hooks & line endings
- Pre-commit runs `mixed-line-ending --fix=lf`, `enforce-standards` (ASCII-only,
  scans the whole tree — slowish), black/isort/ruff (Python only).
- **`.gitattributes` now forces `eol=lf`** repo-wide, so the old CRLF↔LF fight
  (every doc commit failing once on the line-ending hook under
  `core.autocrlf=true`) is fixed. If a NEW file was authored with CRLF the hook
  still rewrites it once — re-`git add` and re-commit is normal for that one file.
- **ASCII-only:** no non-ASCII chars in `.py/.md/.json/.yaml/.txt/.cfg/.sh`
  (no smart quotes, em-dashes as `--`, no emoji in source/docs). `enforce-standards`
  blocks the commit otherwise.

## Git workflow
- Branch from **freshly-fetched** `origin/main`, not a stale local ref:
  `git fetch origin main && git checkout -b <branch> origin/main`.
- **Never stage `.claude/settings.local.json`** (always shows modified; it's local).
- Merge to main via admin-merge (Pip reviews first for agent PRs). PR body ends
  with the Claude Code footer; commit trailer `Co-Authored-By: Claude ...`.

## Where things live
- `docs/ARCHITECTURE.md` — systems→code→ADR map. **READ FIRST.**
- `docs/game-design/` — `DESIGN_PHILOSOPHY.md` (the "why"), `decisions/`
  (ADR-0001…0016 — trust the files, the `decisions/README.md` index is stale),
  `WORKSHOP_2_BACKLOG.md`, `BUILD_BRIEF_*` build briefs.
- `godot/scripts/core/` — game logic (game_state, turn_manager, actions,
  doom_system, finance_engine, events, …). Deterministic, testable.
- `godot/scripts/ui/` — screens/panels (`main_ui.gd` is the 3k-line monolith).
- `godot/autoload/` — singletons (event_service, game_config, theme_manager, …).
- `godot/data/` — data-driven balance/events/actions/scenarios (JSON). Prefer
  editing data over hardcoding.
- `godot/tests/` — `unit/` (fast), `unit/simulation/` (slow), `integration/`.

## CI is honest now (#640)
Green CI means tests actually ran. Earlier the gate reported green while running
ZERO tests (cold class cache → GUT quit(0)); `run_godot_tests.py` now parses the
JUnit XML, enforces a min-test floor, and fails if any `test_*.gd` was silently
dropped. Trust green.

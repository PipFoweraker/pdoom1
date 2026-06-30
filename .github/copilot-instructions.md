<!--
status: canonical
applies-to-version: 0.11.0
last-verified: 2026-06-30
sources-of-truth: CONTRIBUTING.md, docs/developer/ARCHITECTURE.md, version.txt, docs/SCENARIOS.md, docs/mechanics/
note: This file was fully rewritten on 2026-06-30 to replace pre-migration (pygame/Python)
      instructions. If anything here conflicts with the sources-of-truth above, those win — and
      please fix this file.
-->

# P(Doom): AI Safety Strategy Game — Agent Instructions

P(Doom) is a turn-based **AI-safety strategy game built in Godot 4.5.1 (GDScript)**. You run an
underfunded AI safety lab trying to keep global P(Doom) low for as long as possible. Game content
(actions, events, upgrades, scenarios) is **data-driven via JSON**.

**Current version:** `0.11.0` — the single source of truth is `version.txt` (and `godot/project.godot`).

> **Always trust these instructions and the listed sources of truth first.** Fall back to searching
> the code only when something here looks wrong — and if it is wrong, fix it.

## ⚠️ This repo migrated from pygame/Python to Godot

The game **used** to be a Python/pygame app. That runtime is **retired and archived**. When you see
references to `src/`, `main.py`, `ui.py`, `python -m unittest`, `pip install pygame`, or
`src/services/version.py`, they describe the **dead** build — ignore them. The live game lives
entirely under `godot/`. Several older docs still under `docs/` (e.g. `docs/DEVELOPERGUIDE.md`, most of
`docs/game-design/*`) are mid-revision and may still describe the pygame build; prefer `CONTRIBUTING.md`
and `docs/developer/ARCHITECTURE.md`.

## Sources of truth (read these before acting)

| Topic | Authoritative file |
|------|--------|
| Setup, run, test, branch workflow | `CONTRIBUTING.md` |
| Architecture, autoloads, core systems | `docs/developer/ARCHITECTURE.md` |
| Version | `version.txt` |
| Starting resources / scenarios | `docs/SCENARIOS.md`, `godot/data/scenarios/` |
| Current mechanics numbers (auto-generated from code) | `docs/mechanics/*.md` |

## Technology stack

- **Engine:** Godot 4.5.1 (standard build, not .NET) — `godot/project.godot`
- **Language:** GDScript
- **Data:** JSON under `godot/data/`
- **Tests:** GUT (Godot Unit Testing)
- **Tooling scripts:** Python **3.11** baseline (see `pyproject.toml`) — for CI/dev scripts only, not the game

## Repository layout

```
pdoom1/
├── godot/                      # THE GAME (everything runtime lives here)
│   ├── autoload/               # Global singletons: GameManager, GameConfig, MusicManager, ThemeManager, ErrorHandler
│   ├── scripts/
│   │   ├── core/               # game_state.gd, turn_manager.gd, doom_system.gd, actions.gd, events.gd, researcher.gd
│   │   └── ui/                 # UI controllers (main_ui.gd, ...)
│   ├── scenes/                 # .tscn scene files
│   ├── data/                   # JSON content: actions.json, events.json, upgrades.json, scenarios/
│   └── tests/                  # GUT unit/integration tests (test_<system>.gd)
├── scripts/                    # Python tooling + CI helpers
├── docs/                       # Documentation
└── .github/                    # CI/CD workflows
```

## Running the game

- Open `godot/project.godot` in the Godot editor and press **F5**, or `godot godot/project.godot` from CLI.
- With `make`: `make run`.

## Running tests

```bash
# Syntax check (fast)
godot --headless --path godot --quit

# Unit tests via the Python runner
python scripts/run_godot_tests.py --quick
python scripts/run_godot_tests.py --quick --ci-mode   # CI: exits with status code

# Or directly through GUT
godot --headless --path godot -s res://addons/gut/gut_cmdln.gd -gexit
```

With `make`: `make test` (GUT), `make lint` (GDScript syntax), `make validate` (data files), `make health`.

> Note for fresh git worktrees: run an import pass (`godot --headless --path godot --import`) before
> GUT, or tests can fail with misleading `class_name` parse errors.

## Core game logic (ground truth, verified 2026-06-30)

- **Central state:** `godot/scripts/core/game_state.gd` (resources, doom, reputation, researchers, turn counter, queued actions).
- **Turn processing:** `godot/scripts/core/turn_manager.gd`.
- **Win/lose** is decided in `game_state.gd` `check_win_lose()` (called from `turn_manager.gd`):
  - **Victory:** `doom <= 0`
  - **Defeat:** `doom >= 100` **OR** `reputation <= 0`
  - There is **no turn limit / no "survive 100 turns" win** in this path. (A "best score in N turns" benchmark is a *leaderboard/achievement* idea, not the win condition.)
- Heads-up: `godot/scripts/game_controller.gd` contains a *second, divergent* win/lose implementation
  (loses on money/compute = 0). Treat `game_state.gd` as canonical; flag/confirm before relying on the other.

## Branching & commits

- **Trunk-based: everything flows through `main` via PRs.** The former `develop` branch was **retired
  (April 2026)** — do not create or target `develop`.
- Branch names: `feature/<name>`, `fix/<issue>-<desc>`.
- **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Commit messages must be **ASCII-only** (pre-commit enforces this).

## Adding content (the easy, data-driven path)

- New action → `godot/data/actions.json` (+ effect in `scripts/core/actions.gd` if non-trivial; test in `godot/tests/.../test_actions.gd`)
- New event → `godot/data/events.json` (+ `scripts/core/events.gd`)
- New upgrade → `godot/data/upgrades.json`

## In-game developer aids

- **`~`** (tilde) toggles the debug overlay (state, errors, performance, debug controls).
- **`\`** (backslash) opens the built-in bug reporter (auto-captures game state).

## Code style

- GDScript: follow the Godot style guide — `snake_case` functions/vars, `PascalCase` classes, type hints where practical.
- Python tooling: PEP 8, enforced by `ruff` + `black` via pre-commit.

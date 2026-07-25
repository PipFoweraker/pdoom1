# P(Doom) - Godot

**Engine**: Godot 4.5.1 stable
**Language**: pure GDScript -- there is NO Python runtime. The old Python bridge
(`shared_bridge/bridge_server.py`) is retired; all game logic runs in GDScript.
Python survives only for CI/tooling in the repo-root `scripts/` and `tools/`.

## Run

```bash
godot --path godot        # or: make run (from repo root)
```

On Pip's machine Godot is `C:/Program Files/Godot/Godot_v4.5.1-stable_win64.exe`.

## Layout

- `scripts/core/` -- deterministic game logic (game_state, turn_manager, actions,
  doom_system, finance_engine, events, ...). Testable, no engine UI deps.
- `scripts/ui/` -- screens and panels (`main_ui.gd` is the in-game controller).
- `autoload/` -- singletons (event_service, game_config, theme_manager,
  SceneTransition, ...).
- `data/` -- data-driven balance/events/actions/scenarios (JSON). Prefer editing
  data over hardcoding.
- `scenes/` -- Godot scene files (`.tscn`); `welcome.tscn` is the entry menu.
- `assets/` -- fonts, textures, audio.
- `tests/` -- `unit/` (fast gate), `unit/simulation/` (slow), `integration/`.

## Scene navigation

Change scenes ONLY through the `SceneTransition` autoload --
`SceneTransition.go_to("res://scenes/X.tscn")` / `SceneTransition.reload()`.
Never call `get_tree().change_scene_to_file()` directly (it segfaulted the release
build from inside input handlers; see `../docs/LEADERBOARD_CRASH_DIAGNOSIS.md`).

## Tests

Fast gate (repo root):

```bash
python scripts/run_godot_tests.py --quick --ci-mode --min-tests 300
```

The runner does the `--import` pass itself. See `../CLAUDE.md` and
`../docs/ARCHITECTURE.md` for the full systems map.

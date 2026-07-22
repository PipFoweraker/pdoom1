# P(Doom) Development Tool

A simple but extensible development tool for testing P(Doom) game functionality separately from the main game.

## Features

- **Modular Test System**: Easy to add new test scenarios
- **Command Line Interface**: Run specific tests or interactive menu
- **Dual Identity Testing**: Test player name vs lab name separation
- **Leaderboard Testing**: Test enhanced leaderboard functionality
- **Game State Testing**: Test core game mechanics
- **Session Simulation**: Test complete game session lifecycle
- **Seed Variation Testing**: Test how different seeds create different experiences

## Usage

### Command Line

```bash
# Interactive menu
python dev_tool.py

# Run specific test
python dev_tool.py --test dual
python dev_tool.py --test leaderboard
python dev_tool.py --test game
python dev_tool.py --test session
python dev_tool.py --test seeds

# List available tests
python dev_tool.py --list
```

### Interactive Menu

Run `python dev_tool.py` to see:

```
[DEV] P(Doom) Development Tool - v0.4.1
============================================================
Select a test to run:

  1. dual         - Test dual identity system (player_name + lab_name).
  2. leaderboard  - Test enhanced leaderboard functionality.
  3. game         - Test basic game state functionality.
  4. session      - Test complete game session simulation.
  5. seeds        - Test how different seeds create different experiences.
  6. Exit

Enter choice (1-6):
```

## Adding New Tests

The dev tool is designed for easy extension. To add a new test:

1. Add a method to the `DevTool` class:
```python
def test_my_feature(self):
    '''Test my new feature.'''
    print('[TEST] Testing My Feature')
    # Your test code here
    print('[OK] My feature working correctly')
```

2. Register it in `__init__`:
```python
self.tests['myfeature'] = self.test_my_feature
```

That's it! The test will automatically appear in the interactive menu and be available via `--test myfeature`.

## Example Test Output

```bash
$ python dev_tool.py --test dual

[TEST] Testing Dual Identity System - P(Doom) v0.4.1
============================================================
Default Player Name: Anonymous
Generated Lab Name: Cosmos Computing
Customized Player Name: DevTester
Lab Name (unchanged): Cosmos Computing
Different seed lab name: Pulsar AI
[OK] Dual identity system working correctly

[SUCCESS] Test completed successfully!
```

## Growth Potential

The dev tool architecture supports:

- **Performance Testing**: Add timing benchmarks
- **Integration Testing**: Test multiple systems together
- **Data Validation**: Test save/load functionality
- **Configuration Testing**: Test different game configurations
- **AI Testing**: Test opponent behavior
- **UI Testing**: Test user interface components (programmatically)
- **Regression Testing**: Test that changes don't break existing functionality

## Benefits

- **Separation of Concerns**: Test functionality without GUI overhead
- **Rapid Development**: Quick iteration on new features
- **Debugging**: Isolate and test specific components
- **CI/CD Integration**: Automated testing in continuous integration
- **Documentation**: Living examples of how systems work

---

## Build, Version, and Convention Tools

These live alongside `dev_tool.py` in `tools/`. The first three are also wired
into pre-commit and CI, so a violation fails the build rather than slipping in.

### `build_release.py`
Cuts a Windows release build. It nukes `godot/.godot` to defeat the
stale-export-cache trap, runs `write_build_stamp.py`, exports, and PROVES a
freshness marker is in the `.pck` before emitting.

- **Run it:** `python tools/build_release.py` for every Windows build. NEVER
  hand-run a raw `godot --export` (stale-cache risk -- it burned ~12 cycles in
  v0.11.0).

### `check_scene_nav.py`
Fails if any script calls `get_tree().change_scene_to_file()`,
`change_scene_to_packed()`, or `reload_current_scene()` directly instead of
going through the `SceneTransition` autoload. That deferral is what makes the
v0.11.0 release-build scene-change segfault structurally impossible (see
[`../docs/LEADERBOARD_CRASH_DIAGNOSIS.md`](../docs/LEADERBOARD_CRASH_DIAGNOSIS.md)).

- **Run it:** `python tools/check_scene_nav.py`. Runs in pre-commit (changed
  `.gd` files) and CI (full-tree scan). Annotate a genuine one-off exception with
  `# scene-nav-allow` on the line.

### `sync_version.py`
Stamps `version.txt` (the repo-root SINGLE SOURCE OF TRUTH for the game version)
into its derived copies: `game_config.gd` `CURRENT_VERSION`, `project.godot`,
`export_presets.cfg`, and `welcome.tscn`.

- **Run it:** `python tools/sync_version.py` after bumping `version.txt`. The
  `--check` mode writes nothing and exits 1 on drift; it gates pre-commit AND CI
  because a silent version drift forks the leaderboard board-key.

### `write_build_stamp.py`
Writes `godot/build_stamp.txt` (commit/date/branch), which the in-game DEV BUILD
overlay reads via `build_info.gd`; a missing stamp shows "unstamped".

- **Run it:** usually not by hand -- `build_release.py` runs it automatically
  before every export so builds always carry a real stamp.

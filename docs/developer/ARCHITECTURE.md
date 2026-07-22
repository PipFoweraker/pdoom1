# P(Doom) Architecture Overview

This document provides a high-level overview of the codebase for developers.

## Technology Stack

- **Game Engine:** Godot 4.5.1
- **Scripting:** GDScript
- **Data:** JSON files for game content
- **Testing:** GUT (Godot Unit Testing)

## Directory Structure

```
pdoom1/
|--- godot/                      # Main game project
|   |--- autoload/               # Singleton scripts (loaded globally)
|   |   |--- game_config.gd      # Game settings and configuration
|   |   |--- game_manager.gd     # Main game controller
|   |   |--- music_manager.gd    # Audio system
|   |   `--- ...
|   |--- scripts/
|   |   |--- core/               # Core game logic
|   |   |   |--- game_state.gd   # Central game state
|   |   |   |--- turn_manager.gd # Turn processing
|   |   |   |--- actions.gd      # Action definitions
|   |   |   |--- events.gd       # Event system
|   |   |   |--- doom_system.gd  # Doom calculation
|   |   |   `--- researcher.gd   # Researcher entities
|   |   `--- ui/                 # UI controllers
|   |       |--- main_ui.gd      # Main game screen
|   |       `--- ...
|   |--- scenes/                 # Godot scene files (.tscn)
|   |--- data/                   # JSON data files
|   |--- assets/                 # Art, audio, fonts
|   `--- tests/                  # Unit and integration tests
|--- docs/                       # Documentation
`--- .github/                    # CI/CD workflows
```

## Core Systems

### GameState (`scripts/core/game_state.gd`)

The central data model containing all game state:
- Resources (money, compute, reputation)
- Doom percentage
- Researchers and their properties
- Turn counter
- Queued actions

### TurnManager (`scripts/core/turn_manager.gd`)

Handles turn processing:
1. **Start Turn:** Initialize new turn, check for events
2. **Action Selection:** Player queues actions
3. **Execute Actions:** Process queued actions
4. **End Turn:** Apply effects, advance turn counter

### Actions (`scripts/core/actions.gd`)

Defines available player actions:
- Hiring researchers
- Publishing papers
- Acquiring compute
- Strategic decisions

Actions are data-driven dictionaries with:
- `id`: Unique identifier
- `name`: Display name
- `description`: Tooltip text
- `costs`: Resource costs
- `effects`: Resulting changes

### Events (`scripts/core/events.gd`)

Random and triggered events:
- Turn-based triggers
- Condition-based triggers
- Player choices with consequences

### DoomSystem (`scripts/core/doom_system.gd`)

Calculates and tracks doom percentage:
- Base doom changes from actions
- Modifiers from upgrades and events
- Clamping to 0-100 range

## Data Flow

```
User Input
    |
    v
+-------------------+
|    MainUI       | --- Captures clicks/keys
`---------+---------`
         |
         v
+-------------------+
|  GameManager    | --- Routes commands
`---------+---------`
         |
         v
+-------------------+
|   GameState     | --- Updates state
`---------+---------`
         |
         v
+-------------------+
|  TurnManager    | --- Processes turns
`---------+---------`
         |
         v
+-------------------+
|    MainUI       | --- Renders updated state
`-------------------`
```

## Signal Flow

Godot signals are used for decoupled communication:

```gdscript
# GameManager emits signals
signal game_state_updated(state: Dictionary)
signal turn_phase_changed(phase: String)
signal action_executed(result: Dictionary)
signal event_triggered(event: Dictionary)

# UI connects to signals
game_manager.game_state_updated.connect(_on_state_updated)
game_manager.event_triggered.connect(_on_event)
```

## Autoloads (Singletons)

These scripts are loaded globally and accessible anywhere:

| Autoload | Purpose |
|----------|---------|
| `GameConfig` | Settings, difficulty, player preferences |
| `GameManager` | Main game controller |
| `MusicManager` | Background music and audio |
| `ThemeManager` | UI theming |
| `ErrorHandler` | Error logging and reporting |
| `SceneTransition` | The scene-navigation chokepoint (see below) |

Access via: `GameConfig.setting_name` or `GameManager.method()`

## Scene Navigation

`SceneTransition` (`godot/autoload/scene_transition.gd`) is the single chokepoint
for changing scenes. Navigate ONLY through it:

```gdscript
SceneTransition.go_to("res://scenes/main.tscn")   # optional fade: go_to(path, true)
SceneTransition.reload()                            # reload current scene
```

Do NOT call `get_tree().change_scene_to_file()`, `change_scene_to_packed()`, or
`reload_current_scene()` from any other script. Those swap synchronously;
`SceneTransition` defers the swap onto a clean idle frame (`call_deferred`),
which is what fixed the v0.11.0 release-build segfault triggered by changing
scenes from inside an input handler (see
[`../LEADERBOARD_CRASH_DIAGNOSIS.md`](../LEADERBOARD_CRASH_DIAGNOSIS.md)).
`tools/check_scene_nav.py` enforces this in pre-commit and CI; annotate a genuine
exception with `# scene-nav-allow`.

## Testing

Tests use the GUT framework:

```bash
# Run all tests
godot --headless --path godot -s res://addons/gut/gut_cmdln.gd -gexit

# Run specific test file
godot --headless --path godot -s res://addons/gut/gut_cmdln.gd \
  -gtest=res://tests/unit/test_game_state.gd -gexit
```

Test files follow the pattern: `test_<system>.gd`

## Adding New Features

### New Action
1. Add definition to `scripts/core/actions.gd`
2. Implement effect in `_execute_action()` if needed
3. Add tests to `tests/unit/test_actions.gd`

### New Event
1. Add definition to `scripts/core/events.gd`
2. Define trigger condition and effects
3. Add tests to `tests/unit/test_events.gd`

### New UI Element
1. Create scene in `scenes/`
2. Add controller script in `scripts/ui/`
3. Connect to relevant signals

## Performance Considerations

- Use signals instead of polling
- Cache frequently accessed data
- Minimize per-frame allocations
- Profile with Godot's built-in profiler

## Further Reading

- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md) - Starter issues
- [../DEVELOPERGUIDE.md](../DEVELOPERGUIDE.md) - Detailed developer guide

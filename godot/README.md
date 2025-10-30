# P(Doom) - Godot Version

**Status**: Phase 4 MVP - Minimal Functional UI
**Godot Version**: 4.5 stable
**Python Version**: 3.13+

---

## Quick Start

### 1. Ensure Python is Available
The game logic runs in Python via `shared_bridge/bridge_server.py`:

```bash
python --version  # Should be 3.13 or higher
```

### 2. Run with Project-Local Godot

```bash
# From project root
cd godot
../tools/godot/Godot_v4.5-stable_win64.exe project.godot
```

Or double-click `tools/godot/Godot_v4.5-stable_win64.exe` and open the `godot/` folder.

### 3. Test the Game

Once the Godot editor opens:
1. Press **F5** or click the **Play** button (▶️)
2. The main scene should load with a minimal UI
3. Click "**Init Game**" to start
4. Click "**Hire Safety Researcher**" to test an action
5. Click "**End Turn**" to process the turn
6. Watch the message log and resource displays update

---

## Architecture Overview

```
Godot UI (GDScript)
    ↕ (PowerShell pipe: JSON over stdin/stdout)
Python Bridge (bridge_server.py)
    ↕ (Python imports)
Shared Game Logic (shared/)
```

### Key Files

- **`scripts/game_manager.gd`** - Singleton that spawns Python bridge and sends commands
- **`scripts/ui/main_ui.gd`** - UI controller that displays game state
- **`scenes/main.tscn`** - Main scene with minimal test UI
- **`../shared_bridge/bridge_server.py`** - Python bridge server (JSON protocol)
- **`../shared/core/game_logic.py`** - Core game logic (engine-agnostic)

---

## Current Features (Phase 4 MVP)

✅ **Working**:
- Python bridge communication (via PowerShell + pipe)
- Game initialization
- Action selection (queues actions)
- Turn processing (executes queued actions)
- Resource display (money, compute, safety)
- Message log with colored output
- Turn phase tracking

⏳ **Not Yet Implemented**:
- Action list UI (currently just one test button)
- Event popup dialogs
- Multiple screens/views
- Graphics/styling
- Sound
- Save/load
- Settings

---

## UI Design Philosophy

See [../docs/UI_DESIGN_VISION.md](../docs/UI_DESIGN_VISION.md) for full details.

**TL;DR**:
- Function over form - working buttons > pretty graphics
- Ugly is OK during development
- UI will upgrade through gameplay (planned feature)
- Modular screen system (like Civ IV)
- Future vision: X-COM/StarCraft 2 style command center

---

## Development Workflow

### Testing Python Bridge Directly

```bash
cd shared_bridge

# Test single command
echo '{"action": "init_game", "seed": "test"}' | python bridge_server.py

# Test full turn cycle
printf '%s\n%s\n%s\n' \
  '{"action": "init_game", "seed": "test"}' \
  '{"action": "select_action", "action_id": "hire_safety_researcher"}' \
  '{"action": "end_turn"}' \
  | python bridge_server.py
```

### Validating Godot Scripts

```bash
cd godot
../tools/godot/Godot_v4.5-stable_win64.exe --headless --check-only --path .
```

### Running Headless (for CI/testing)

```bash
cd godot
../tools/godot/Godot_v4.5-stable_win64.exe --headless --path . --quit-after 5
```

---

## Troubleshooting

### "Python not found" error
Make sure Python is in your PATH. Test with:
```bash
python --version
```

### Bridge not responding
The bridge uses PowerShell to pipe commands. Check:
1. PowerShell is available: `powershell -Command "echo test"`
2. Bridge runs manually: `python ../shared_bridge/bridge_server.py`

### Scene won't load
Check for GDScript errors:
```bash
../tools/godot/Godot_v4.5-stable_win64.exe --headless --script-check scripts/game_manager.gd
```

### UI not updating
Check the Godot console output for:
- `[GameManager]` messages (bridge communication)
- `[MainUI]` messages (UI updates)
- Error messages in red

---

## Next Steps (Phase 5)

See [../docs/SESSION_HANDOFF_2025-10-16_GODOT_MIGRATION_START.md](../docs/SESSION_HANDOFF_2025-10-16_GODOT_MIGRATION_START.md) for detailed roadmap.

**Immediate priorities**:
1. ✅ Minimal functional UI (DONE)
2. Load and display available actions dynamically
3. Implement event popup system
4. Add turn phase visual indicator
5. Test 10+ turn gameplay loop

**Future enhancements**:
- Multiple screens (research, employees, settings)
- Screen switching system
- UI upgrades as gameplay mechanics
- Polish and styling

---

## Contributing

When working on Godot features:
1. Keep Python bridge protocol stable (see `shared_bridge/bridge_server.py`)
2. Use signals for state updates (don't poll)
3. Function first, polish later
4. Document new screens in [UI_DESIGN_VISION.md](../docs/UI_DESIGN_VISION.md)

---

## Structure
- `scenes/` - Godot scene files (.tscn)
- `scripts/` - GDScript code
  - `scripts/game_manager.gd` - Main game controller
  - `scripts/ui/` - UI controllers
- `assets/` - Game assets (fonts, sounds, textures)

---

**Last Updated**: 2025-10-17
**Phase**: 4 (MVP - Minimal Functional UI)
**Status**: ✅ Bridge working, basic UI functional

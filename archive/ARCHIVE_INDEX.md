# PDoom Archive Index

This directory contains legacy code and historical artifacts from PDoom's development journey.

**Archived:** v0.10.2 (2025-11-08)
**Reason:** Migration from Pygame/Python to Godot/GDScript

## Directory Structure

### Legacy Game Implementations

**[legacy-pygame/](legacy-pygame/)**
- Complete Pygame implementation of PDoom
- ~19,000 lines of Python code
- Original game loop, UI, and game logic
- Status: Superseded by Godot implementation
- Last functional version: v0.9.0 (had syntax errors by v0.10.2)

**[legacy-python-src/](legacy-python-src/)**
- Python source code (`src/` directory)
- Core game systems (GameState, events, actions)
- Service layer (RNG, config, version management)
- UI systems (Pygame rendering)
- Status: Essential modules ported to `scripts/lib/`

**[legacy-ui/](legacy-ui/)**
- Experimental UI components (`ui_new/`)
- Modular UI architecture prototypes
- Never reached production
- Status: Deprecated, superseded by Godot UI

**[legacy-shared/](legacy-shared/)**
- Shared data structures and utilities
- Originally intended for Python↔Godot bridge
- Status: No longer needed with full Godot migration

**[legacy-shared-bridge/](legacy-shared-bridge/)**
- Bridge code between Python and Godot
- Used during hybrid implementation phase
- Status: Obsolete after full Godot migration

### Active Archives

**[docs/](docs/)**
- Historical documentation
- Development session notes
- Design documents from Pygame era
- Maintained for historical reference

**[python-root/](python-root/)**
- Python utility scripts from project root
- Development automation tools

**[releases/](releases/)**
- Historical release packages
- Build artifacts from Pygame era

**[session-docs/](session-docs/)**
- Development session documentation
- Pair programming notes
- Implementation planning documents

## Why These Were Archived

### Pygame → Godot Migration

The project migrated from Pygame (Python) to Godot (GDScript) for:

1. **Better Performance**: Native engine vs. Python interpretation
2. **Multi-Platform Support**: Windows, Linux, macOS builds
3. **Modern Tooling**: Godot's IDE, debugger, profiler
4. **Maintainability**: Purpose-built game engine vs. DIY framework

### What Was Preserved

Some Python modules were essential for build automation:
- **Version management** → `scripts/lib/services/version.py`
- **Leaderboard system** → `scripts/lib/scores/`
- **RNG utilities** → `scripts/lib/services/deterministic_rng.py`

See [scripts/lib/README.md](../scripts/lib/README.md) for details.

## Using Archived Code

### Game Logic Reference

If you need to understand how a game mechanic worked in Pygame:

1. Check `archive/legacy-python-src/core/game_state.py` for core logic
2. Review `archive/legacy-python-src/features/` for specific systems
3. Compare with current Godot implementation in `godot/scripts/`

### Extracting Algorithms

To port logic from Python to GDScript:

1. Find the relevant Python file in `archive/legacy-python-src/`
2. Extract the algorithm (not the UI/framework code)
3. Translate Python → GDScript syntax
4. Adapt to Godot's node/signal architecture

### Historical Context

For understanding design decisions:

1. Review `archive/docs/` for design documents
2. Check `archive/session-docs/` for implementation discussions
3. Read commit history for rationale

## What NOT to Do

❌ **Do not try to run archived Pygame code**
- Missing dependencies (pygame, numpy, etc.)
- Broken imports after restructuring
- Will fail with errors

❌ **Do not import from `archive/` in production code**
- Use `scripts/lib/` for needed functionality
- Port to GDScript for game logic
- Archived code is read-only reference

✅ **Do use archives for:**
- Understanding design decisions
- Extracting game balance data
- Historical research
- Learning from past mistakes

## Repository Cleanup Impact

### Before v0.10.2 (34 root directories)
```
pygame/, src/, ui_new/, shared/, shared_bridge/, ...
```

### After v0.10.2 (<15 root directories)
```
godot/, scripts/, docs/, tests/, archive/, ...
```

**Goal:** Clean, focused repository ready for public website integration.

## Maintenance

Archives are **frozen** - no new code added. Only documentation updates.

For questions about archived code, create an issue tagged `archaeology`.

---

**Last Updated:** 2025-11-08
**Migration Lead:** Documentation Cleanup Session v0.10.2

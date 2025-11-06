# Shared Game Logic

**Status:** Engine-agnostic game mechanics

This directory contains pure game logic with NO pygame or Godot dependencies.
Both pygame and Godot implementations use this shared code.

## Structure
- `core/` - Core game state, actions, events
- `features/` - Economic cycles, technical failures, etc.
- `data/` - JSON definitions for actions, events, upgrades
- `utils/` - Helper functions

## Testing
All shared logic is tested independently:
```bash
python -m pytest tests/test_shared_logic/ -v
```

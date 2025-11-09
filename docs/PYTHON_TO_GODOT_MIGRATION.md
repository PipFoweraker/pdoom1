# Python to Godot Migration

## Overview

PDoom1 has migrated from a Python/Pygame implementation to Godot Engine (GDScript). This document tracks the migration status and cleanup of legacy Python code.

## Migration Status

### Completed Migrations

- **Event System**: Migrated from `src.features.event_system` (Python) to `godot/scripts/core/events.gd` (GDScript)
  - Old: Python classes Event, EventType, EventAction, DeferredEventQueue
  - New: GameEvents static class with data-driven event definitions
  - Tests: Migrated from `tests/test_events.py` to `godot/tests/unit/test_events.gd`

- **Game Logic**: Migrated from `shared.core.game_logic` (Python) to Godot autoloads and scripts
  - Old: Python GameState, GameLogic classes
  - New: GameState.gd, ActionsEngine.gd, various Godot scripts

- **Actions Engine**: Migrated from `shared.core.actions_engine` (Python) to GDScript
  - Old: Python ActionsEngine
  - New: Godot action system in `godot/scripts/`

### Cleanup Actions (Issue #404)

**Date**: 2025-11-09
**Branch**: `fix/404-event-validation-error-handling`

Removed stale Python tests that referenced non-existent modules:
- `tests/test_events.py` - Removed (already archived in `archive/legacy-pygame/`)
- `tests/test_shared_logic/test_events_engine.py` - Removed
- `tests/test_shared_logic/test_actions_engine.py` - Removed
- `tests/test_shared_logic/test_game_logic.py` - Removed
- `tests/test_shared_logic/` directory - Removed entirely

These tests were attempting to import from modules that no longer exist after the Godot migration:
```python
from src.features.event_system import ...  # Module doesn't exist
from shared.core.events_engine import ...   # Module doesn't exist
from shared.core.actions_engine import ...  # Module doesn't exist
from shared.core.game_logic import ...      # Module doesn't exist
```

All Python test functionality has been replaced by Godot GUT tests in `godot/tests/unit/`.

## Testing Infrastructure

### Current (Godot)
- **Framework**: GUT (Godot Unit Testing)
- **Location**: `godot/tests/unit/`
- **Run tests**: Via Godot editor or headless mode
- **Example**: `godot/tests/unit/test_events.gd`

### Legacy (Python - Archived)
- **Framework**: pytest
- **Location**: `archive/legacy-pygame/tests/`
- **Status**: Preserved for historical reference only

## Related Issues

- **#404**: Event System Error Handling Issues - Removed stale Python tests
- **#440**: Add Shared Event Schemas - Will define schemas for data integration
- **#439**: Automate Validation in CI/CD - Will validate event data against schemas

## Next Steps

1. Ensure all Godot tests pass
2. Set up CI/CD for Godot testing (if not already done)
3. Implement data validation schemas (Issue #440)
4. Automate schema validation in CI pipeline (Issue #439)

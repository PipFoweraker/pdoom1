# Archived Python Files from Root

**Archived:** 2025-11-03
**From:** Project root directory
**Reason:** Root directory cleanup

## Files (15 total)

### Utility Scripts (7 files)
- `fix_quotes.py`
- `fix_all_smart_quotes.py`
- `fix_ascii.py`
- `fix_main_quotes.py`
- `fix_pygame_tests_quotes.py`
- `fix_quote_errors.py`
- `fix_rng_tests.py`

**Purpose:** Character encoding fixes (smart quotes → ASCII)
**Consolidation opportunity:** These could be merged into single tool

### Debug/Development (3 files)
- `debug_zabinga.py` - Debug utilities
- `dev_tool_testing.py` - Development tool testing
- `command_string_example.py` - Command examples

**Purpose:** Development support and examples

### Test Files (2 files)
- `test_pure_logic.py` - Logic tests
- `test_demo_hotfixes.py` - Demo testing

**Future:** Could move to main `tests/` directory

### Large Legacy Files (3 files - ~34K lines)

#### `core_game_logic.py` (12,634 lines)
- Bridge architecture implementation
- Game state management
- Business logic
- **Status:** Potentially obsolete - review before deletion

#### `engine_interface.py` (8,063 lines)
- Bridge pattern implementation
- Engine abstraction layer
- **Status:** Potentially obsolete - review before deletion

#### `pygame_adapter.py` (13,161 lines)
- Adapter pattern for Pygame
- UI rendering logic
- **Status:** Potentially obsolete - review before deletion

## Notes

These large files were part of an earlier architecture approach (bridge/adapter pattern) that was later superseded by more direct implementations. They are preserved here for:
- Logic reference
- Understanding architectural evolution
- Extracting any useful patterns or code

All files retain git history. Use `git log --follow` to trace their origins.

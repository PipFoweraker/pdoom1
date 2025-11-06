# Archive Directory

**Date Archived:** 2025-11-03
**Purpose:** Root directory cleanup for public presentation

This directory contains Python code and documentation moved out of the project root. **Nothing is deleted** - everything is preserved for reference and potential logic review.

## What's Here

### `python-root/` - Python Files from Project Root

15 files moved from root directory:

**Utility Scripts (7 files):**
- `fix_quotes.py` - Smart quote fixer
- `fix_all_smart_quotes.py` - Batch quote fixing
- `fix_ascii.py` - ASCII compliance tool
- `fix_main_quotes.py` - Main file quote fixer
- `fix_pygame_tests_quotes.py` - Test file quote fixer
- `fix_quote_errors.py` - Quote error resolver
- `fix_rng_tests.py` - RNG test fixer

**Debug/Dev Scripts (3 files):**
- `debug_zabinga.py` - Debug utility
- `dev_tool_testing.py` - Development tool tests
- `command_string_example.py` - Command string examples

**Test Files (2 files):**
- `test_pure_logic.py` - Pure logic tests
- `test_demo_hotfixes.py` - Demo hotfix tests

**Large Legacy Files (3 files - ~34,000 lines total):**
- `core_game_logic.py` - 12,634 lines (bridge architecture)
- `engine_interface.py` - 8,063 lines (bridge architecture)
- `pygame_adapter.py` - 13,161 lines (adapter pattern)

> **Note:** These large files were part of the old bridge architecture. They may be candidates for eventual deletion after thorough review, but are preserved here for logic reference.

### `session-docs/` - Session Documentation

15 session summary files moved from root:
- SESSION_COMPLETION_*.md (8 files)
- SESSION_HANDOFF_*.md (3 files)
- SESSION_SUMMARY_*.md (4 files)

## Why Archive?

Files were moved to:
1. **Clean root directory** - Makes project more approachable for new contributors
2. **Separate concerns** - Active code vs utility/legacy code
3. **Prepare for public push** - Professional directory structure
4. **Preserve all logic** - Nothing deleted, everything accessible

## What Stayed in Root

Only essential entry points remain:
- `main.py` - Main application entry point
- `ui.py` - UI implementation
- `dev.py` - Development convenience launcher
- `__init__.py` - Package marker
- `__main__.py` - Python -m entry point

## Accessing Archived Code

All files maintain full git history. To see the original location and history:

```bash
# View file history
git log --follow -- archive/python-root/filename.py

# See when file was moved
git log --all --full-history -- filename.py

# Compare with current code
git show HEAD:archive/python-root/filename.py
```

## Future Actions

**Potential Next Steps:**
1. **Review large legacy files** - Determine if bridge architecture code can be removed
2. **Consolidate utilities** - Merge multiple fix_*.py scripts into single tool
3. **Test organization** - Move archived tests to proper test directory structure
4. **Documentation** - Organize session docs chronologically

## Notes

- This is a **lift-and-shift** operation - no code logic was modified
- All moves preserve git history (tracked as deletes + adds)
- Archive can be moved elsewhere or removed after thorough review
- No functionality was lost - everything is still accessible

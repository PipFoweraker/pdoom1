# Good First Issues

These issues are specifically scoped for new contributors. Each one is self-contained, well-documented, and can be completed in a few hours.

---

## Issue 1: Centralize Game Version Constant

**Labels:** `good first issue`, `refactor`, `code quality`

**Problem:**
The game version is hardcoded as a string literal in `godot/scripts/game_manager.gd:40`:
```gdscript
var game_version = "0.11.0"  # TODO: Get from GameConfig or version constant
```

This makes version bumps error-prone and inconsistent.

**Solution:**
1. Add a `VERSION` constant to `godot/autoload/game_config.gd`
2. Update `game_manager.gd` to use `GameConfig.VERSION`
3. Search for any other hardcoded version strings and update them

**Files to modify:**
- `godot/autoload/game_config.gd`
- `godot/scripts/game_manager.gd`

**Acceptance criteria:**
- [ ] Version is defined in one place
- [ ] Game runs without errors
- [ ] Version displays correctly in-game

---

## Issue 2: Add Unit Tests for DoomSystem

**Labels:** `good first issue`, `testing`

**Problem:**
The `doom_system.gd` is a core game system but lacks dedicated unit tests. Other core systems like `game_state.gd` and `turn_manager.gd` have tests.

**Solution:**
1. Create `godot/tests/unit/test_doom_system.gd`
2. Follow the pattern from existing test files (e.g., `test_game_state.gd`)
3. Test key functions:
   - `calculate_doom_change()`
   - `apply_doom_modifier()`
   - Doom clamping (0-100 range)

**Files to create:**
- `godot/tests/unit/test_doom_system.gd`

**Reference files:**
- `godot/scripts/core/doom_system.gd` (the system to test)
- `godot/tests/unit/test_game_state.gd` (test pattern example)

**Acceptance criteria:**
- [ ] At least 5 test cases covering core doom functionality
- [ ] Tests pass when run with GUT framework
- [ ] Tests follow existing naming conventions

---

## Issue 3: Implement Save File Path in Bug Report Panel

**Labels:** `good first issue`, `enhancement`

**Problem:**
The bug report panel has a TODO for retrieving the save file path. Currently it's a stub:

```gdscript
# godot/scripts/ui/bug_report_panel.gd:130
# TODO: Implement actual save file path retrieval
pass
```

**Solution:**
1. Implement the save file path retrieval
2. Use Godot's `user://` path to find save files
3. Display the path or "No save found" in the bug report

**Files to modify:**
- `godot/scripts/ui/bug_report_panel.gd`

**Helpful resources:**
- [Godot File Paths Documentation](https://docs.godotengine.org/en/stable/tutorials/io/data_paths.html)
- `user://` resolves to the user data directory

**Acceptance criteria:**
- [ ] Bug report shows actual save file path when available
- [ ] Shows "No save file" when none exists
- [ ] No errors when opening bug report panel (F8)

---

## Issue 4: Add Keyboard Shortcut Documentation to In-Game Help

**Labels:** `good first issue`, `documentation`, `UX`

**Problem:**
The game has keyboard shortcuts (documented in `godot/KEYBOARD_SHORTCUTS_TESTING.md`) but they're not easily discoverable in-game.

**Solution:**
1. Add a "Keyboard Shortcuts" section to the settings or help screen
2. Display the most common shortcuts:
   - `F5` - Quick save
   - `F8` - Bug report
   - `F9` - Quick load
   - `Escape` - Menu
   - Number keys - Action selection

**Files to modify:**
- UI scene for settings/help (check `godot/scenes/`)
- Potentially `godot/scripts/ui/main_ui.gd`

**Reference:**
- `godot/KEYBOARD_SHORTCUTS_TESTING.md` - Full shortcut list

**Acceptance criteria:**
- [ ] Keyboard shortcuts visible somewhere in-game
- [ ] Information matches actual implemented shortcuts
- [ ] Easy to find for new players

---

## Issue 5: Add Colorblind-Friendly Mode

**Labels:** `good first issue`, `accessibility`, `enhancement`

**Problem:**
The game uses color to convey information (red for danger, green for safety) which may be difficult for colorblind players. A colorblind mode is mentioned in `godot/UI_MIGRATION_SUMMARY.md` as planned.

**Solution:**
1. Add a "Colorblind Mode" toggle to settings
2. When enabled, add patterns/symbols to color-coded elements:
   - Doom meter: Add warning icons at thresholds
   - Resource bars: Add distinct patterns
3. Store setting in GameConfig

**Files to modify:**
- `godot/autoload/game_config.gd` - Add setting
- `godot/scripts/ui/` - Update relevant UI components
- Settings scene

**Reference:**
- `godot/UI_STYLE_GUIDE.md` - Color definitions
- `godot/VISUAL_DOOM_METER.md` - Doom meter design

**Acceptance criteria:**
- [ ] Toggle exists in settings
- [ ] Visual distinction without relying solely on color
- [ ] Setting persists between sessions

---

## How to Claim an Issue

1. Comment on the GitHub issue saying you'd like to work on it
2. Fork the repository
3. Create a branch: `git checkout -b fix/issue-number-description`
4. Make your changes
5. Submit a PR referencing the issue

## Questions?

Open a [Discussion](https://github.com/PipFoweraker/pdoom1/discussions) or comment on the issue.

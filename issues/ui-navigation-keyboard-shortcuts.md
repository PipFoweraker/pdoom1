# UI Navigation and Keyboard Shortcuts Issues

## Description
Multiple UI navigation and keyboard shortcut systems are not functioning correctly.

## Affected Tests
- `test_keyboard_shortcuts_ui.py::TestKeyboardShortcutsUI::test_draw_main_menu_calls_shortcut_functions`
- `test_navigation_stack.py::TestBackButton::test_back_button_positioning`
- `test_issue_36_fixes.py::TestUIBoundaryChecking::test_multiple_upgrade_rows_when_needed`

## Error Details
```
AssertionError: Expected 'get_main_menu_shortcuts' to have been called once. Called 0 times.
AssertionError: 20 != 12
TypeError: cannot unpack non-iterable NoneType object
```

## Root Cause
1. Keyboard shortcut functions not being called when drawing menus
2. Back button positioning calculations incorrect
3. UI boundary checking returning None when tuple expected

## Expected Behavior
- Main menu should call keyboard shortcut functions during drawing
- Back button should be positioned correctly (expected 12, got 20)
- UI boundary checking should return valid tuple, not None

## Investigation Areas
1. Main menu drawing logic and shortcut integration
2. Back button positioning calculations
3. UI boundary checking function return values
4. Upgrade row layout when multiple rows needed

## Priority
Medium - Affects user interface usability

## Labels
- bug
- ui
- navigation
- keyboard-shortcuts
- positioning
- testing

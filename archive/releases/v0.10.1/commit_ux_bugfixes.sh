#!/bin/bash
# Commit UX bug fixes discovered during testing

cd "c:\Users\gday\Documents\A Local Code\pdoom1"

echo "=== Staging UX bug fixes ==="
git add godot/scenes/main.tscn godot/scripts/ui/main_ui.gd 7_HOUR_SPRINT_PLAN.md test_ux_fixes.md

echo ""
echo "=== Creating commit ==="
git commit -m "fix: UX bug fixes from playtesting

FIXES:
- Change Clear Queue shortcut: X → C (avoids conflicts)
- Disable Commit Actions button when queue is empty (prevents illegal turns)
- Better error message when trying to commit with empty queue
- Both Clear Queue and Commit buttons properly enable/disable based on queue state

ISSUE DISCOVERED:
- X key conflicted with potential future dialog shortcuts
- Players could click Commit with empty queue (confusing error state)
- Not obvious why commit wasn't working

TESTING DOCS:
- Added test_ux_fixes.md - Comprehensive UX testing checklist
- Added 7_HOUR_SPRINT_PLAN.md - Strategic issue prioritization for v0.10.1

Files changed:
- godot/scenes/main.tscn - Button text (X → C)
- godot/scripts/ui/main_ui.gd - Keyboard shortcut, button state management, error messages

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Commit complete! ==="
git log --oneline -1

echo ""
echo "Next: Re-export Godot build and test"

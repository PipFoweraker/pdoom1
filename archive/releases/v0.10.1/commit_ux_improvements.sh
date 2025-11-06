#!/bin/bash
# Commit UX improvements for v0.10.1

cd "c:\Users\gday\Documents\A Local Code\pdoom1"

echo "=== Staging changes ==="
git add -A

echo ""
echo "=== Creating commit ==="
git commit -m "feat: Major UX improvements for v0.10.1

CRITICAL FIXES:
- Fix action overcommitment bug - players can no longer queue more actions than they have AP
- Validates against remaining AP (total - committed) instead of total AP

UI IMPROVEMENTS:
- Rename 'End Turn' → 'Commit Actions (Space)' for clarity
- AP counter shows remaining AP: 'AP: 3 (1 free, 2 queued)'
- Color-coded AP display: Green (available), Yellow (low), Red (depleted)
- Added 'Clear Queue (X)' button with keyboard shortcut

TECHNICAL:
- Fixed GUT addon compatibility with Godot 4.5.1 (Logger → GutLogger)
- Added clear_action_queue() function to GameManager
- Enhanced error messages with AP breakdown

Files changed:
- godot/scripts/game_manager.gd - Overcommitment fix, clear queue function
- godot/scripts/ui/main_ui.gd - AP display, clear queue UI, keyboard shortcuts
- godot/scenes/main.tscn - Button renames, new Clear Queue button
- godot/addons/gut/utils.gd - Godot 4.5.1 compatibility fix
- CHANGELOG.md - Updated with all changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Commit complete! ==="
git log -1 --oneline

echo ""
echo "Next: Test the build at builds/windows/v0.10.1/P(Doom)1.exe"

#!/bin/bash
# Commit critical AP tracking fix

cd "c:\Users\gday\Documents\A Local Code\pdoom1"

echo "=== Staging AP tracking fixes ==="
git add godot/scripts/game_manager.gd godot/scripts/ui/main_ui.gd

echo ""
echo "=== Creating commit ==="
git commit -m "fix: Critical AP tracking and button state bugs

CRITICAL FIXES:
- Fix committed_ap not being incremented when queuing actions
- AP was being deducted immediately instead of tracked as committed
- Clear Queue button always disabled due to case-sensitive phase check
- Actions now properly queue with committed_ap tracking

HOW IT WORKS NOW:
- Queue action: committed_ap += cost (action_points unchanged)
- Clear queue: committed_ap = 0 (AP refunded)
- Commit turn: action_points -= committed_ap (AP actually spent)
- UI shows 'AP: 3 (1 free, 2 queued)' with color coding

BUG SYMPTOMS FIXED:
✅ AP counter now shows correct remaining AP
✅ Clear Queue button enables/disables properly
✅ Can't overcommit AP (validation works)
✅ C key clears queue successfully
✅ AP color coding works (green/yellow/red)

FILES CHANGED:
- game_manager.gd: Track committed_ap, convert to spent on turn end
- main_ui.gd: Case-insensitive phase check, debug logging

TESTING:
- Queue 2 actions → AP: 3 (1 free, 2 queued) ✅
- Press C → Queue clears, AP: 3 ✅
- Queue 3 actions → AP: 3 (0 free, 3 queued) RED ✅
- Try queue 4th → Error 'Not enough AP' ✅

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Commit complete! ==="
git log --oneline -1

echo ""
echo "=== TIER 1.3 COMPLETE - Moving to TIER 1.1 (GDScript warnings) ==="

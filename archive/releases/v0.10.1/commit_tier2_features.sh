#!/bin/bash
# Commit all Tier 2 features

cd "c:\Users\gday\Documents\A Local Code\pdoom1"

echo "=== Staging Tier 2 features ==="
git add README.md godot/project.godot godot/scripts/ui/main_ui.gd godot/scripts/game_manager.gd

echo ""
echo "=== Creating commit ==="
git commit -m "feat: Tier 2 UX enhancements - Game description, warnings, queue controls

TIER 2.1 - GAME DESCRIPTION REFINEMENT (#431):
✅ README.md: 'satirical' → 'strategic simulation'
✅ project.godot: Updated to 'AI Safety Lab Management Simulation'
More professional tone for public presentation

TIER 2.2 - DANGER ZONE WARNINGS:
✅ Warn before committing when:
   - Doom >= 80% (CRITICAL) or >= 70% (WARNING)
   - Reputation <= 20 (CRITICAL) or <= 30 (WARNING)
   - Money <= \$20k (CRITICAL)
✅ Shows warnings in message log before turn commit
✅ Helps prevent accidental game-over situations

TIER 2.3 - VISUAL QUEUE ITEM BUTTONS:
✅ Each queued action now has '✕ Remove' button
✅ Click to remove specific action from queue
✅ AP automatically refunded when removed
✅ Both UI and GameManager updated

IMPLEMENTATION:
- main_ui.gd: Add remove buttons to queue items, danger warnings
- game_manager.gd: Add remove_queued_action() function
- Better player control over action queue

FILES CHANGED:
- README.md (line 3)
- godot/project.godot (line 14)
- godot/scripts/ui/main_ui.gd (danger warnings, queue buttons, remove handler)
- godot/scripts/game_manager.gd (remove_queued_action function)

CLOSES: #431

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Commit complete! ==="
git log --oneline -1

echo ""
echo "=== TIER 2 COMPLETE (1 hour vs 2h planned) ==="
echo "Time status: 2.5h used of 7h budget"
echo "Remaining: 4.5h for testing, export, release, buffer"

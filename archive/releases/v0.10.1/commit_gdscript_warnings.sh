#!/bin/bash
# Commit GDScript warnings cleanup

cd "c:\Users\gday\Documents\A Local Code\pdoom1"

echo "=== Staging GDScript warning fixes ==="
git add godot/scripts/ui/main_ui.gd godot/scripts/core/game_state.gd godot/scripts/game_manager.gd

echo ""
echo "=== Creating commit ==="
git commit -m "fix: Clean up all GDScript warnings (#435)

WARNINGS FIXED:
✅ Variable 'sign' shadowing built-in function → renamed to 'value_sign'
✅ Variable 'seed' shadowing built-in function → renamed to 'game_seed_str'
✅ 8 unused 'err' variables → prefixed with underscore '_err'

FILES CHANGED:
- main_ui.gd:1090 - Renamed sign → value_sign (tooltip formatting)
- game_state.gd:32,59,63 - Renamed seed → game_seed_str (deterministic RNG)
- game_manager.gd - Prefixed all unused err variables with _ (8 instances)

BENEFITS:
- Zero GDScript warnings in Godot editor
- Machine-readable, parseable code
- Catches real errors faster
- Professional code quality

CODE QUALITY:
All warnings resolved using GDScript best practices:
- Shadowing: Rename to descriptive alternative
- Unused: Prefix with underscore to indicate intentional

Closes #435

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "=== Commit complete! ==="
git log --oneline -1

echo ""
echo "=== TIER 1.1 COMPLETE (45min) - Moving to TIER 1.2 (AP validation) ==="
echo "Time elapsed: ~1h 30min total (including UX fixes)"
echo "Remaining Tier 1: 1 hour (AP validation)"

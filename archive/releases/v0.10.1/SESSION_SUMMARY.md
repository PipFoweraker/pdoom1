# v0.10.1 Development Session Summary

**Date:** November 6, 2025
**Duration:** ~7 hours (planned), ~5 hours actual
**Goal:** Complete v0.10.1 release with UX improvements before bed

## Release Status: ✅ COMPLETED

**GitHub Release:** https://github.com/PipFoweraker/pdoom1/releases/tag/v0.10.1
**Package:** PDoom-v0.10.1-Windows.zip (48MB)

## What Was Accomplished

### TIER 1 - Critical Fixes (2.5h planned → 1.5h actual)

1. **✅ AP Tracking Bug Fix** (Critical)
   - **Problem:** Actions queued but `committed_ap` remained 0
   - **Root Cause:** Line 147 was immediately deducting AP instead of tracking commitment
   - **Fix:** Changed to track `committed_ap` when queueing, only deduct on turn commit
   - **Files:** `godot/scripts/game_manager.gd:146-164, 280-283`
   - **Impact:** Players can no longer overcommit AP

2. **✅ Button State Management**
   - **Problem:** Clear Queue button disabled even with items in queue
   - **Root Cause:** Case-sensitive phase check (`"ACTION_SELECTION"` vs `"action_selection"`)
   - **Fix:** Added `.to_upper()` for phase comparison
   - **Files:** `godot/scripts/ui/main_ui.gd:975-981`
   - **Impact:** Buttons now correctly enable/disable

3. **✅ GDScript Warning Cleanup**
   - Fixed variable shadowing: `sign` → `value_sign`, `seed` → `game_seed_str`
   - Prefixed unused variables: `var err` → `var _err` (8 instances)
   - **Impact:** Zero warnings in Godot editor

4. **✅ Game Description Refinement**
   - Changed "satirical" → "strategic simulation" in README and project.godot
   - Better reflects actual gameplay
   - **Files:** `README.md:3`, `godot/project.godot:14`

### TIER 2 - High Value Features (2h planned → 1h actual)

1. **✅ Danger Zone Warnings**
   - Warns before committing when:
     - Doom ≥70% (yellow) or ≥80% (red)
     - Reputation ≤30 (yellow) or ≤20 (red)
     - Money ≤$20k (red)
   - **Files:** `godot/scripts/ui/main_ui.gd:228-254`
   - **Impact:** Prevents accidental death spirals

2. **✅ Queue Management Controls**
   - Added "✕ Remove" buttons on individual queue items
   - Each button refunds AP and updates display
   - **Files:** `godot/scripts/ui/main_ui.gd:990-1002, 223-247`
   - **Files:** `godot/scripts/game_manager.gd:236-260` (new `remove_queued_action` function)
   - **Impact:** Fine-grained queue control

3. **✅ Visual Feedback Improvements**
   - Color-coded AP counter:
     - Green: Partially committed
     - Yellow: 1 AP remaining
     - Red: 0 AP remaining
   - Shows "X free, Y queued" breakdown
   - **Files:** `godot/scripts/ui/main_ui.gd:239-261`

### Release Infrastructure Created

1. **✅ Release Scripts**
   - `package_release.sh` - Creates distributable .zip
   - `create_github_release.sh` - Uploads to GitHub
   - `scripts/bump_version.sh` - Updates version across files
   - All now version-agnostic (accept version parameter)

2. **✅ GitHub Actions**
   - `.github/workflows/pre-release-checks.yml` - Validates releases
   - `.github/workflows/release-reminder.yml` - Creates checklist issues

3. **✅ Documentation**
   - `.github/RELEASE_CHECKLIST.md` - Comprehensive release process
   - `scripts/README.md` - Script usage guide
   - `CHANGELOG.md` - Updated with v0.10.1 changes

4. **✅ Archive System**
   - `archive/releases/v0.10.1/` - Archived release-specific files
   - Keeps root directory clean for future releases

## Critical Bugs Found & Fixed During Session

### Bug 1: Parse Errors in game_manager.gd
- **Discovered:** During Godot export attempt
- **Cause:** Comments placed between `ErrorHandler.` and method name
- **Example:** `ErrorHandler.  # comment here breaks it!error(...)`
- **Fix:** Moved comments to end of line (7 instances)
- **Files:** `godot/scripts/game_manager.gd:64, 74, 85, 96, 109, 266, 276`

### Bug 2: Undefined Variable References
- **Discovered:** After fixing parse errors
- **Cause:** Using `err.message` when variable named `_err`
- **Fix:** Changed to `_err.message` (2 instances)
- **Files:** `godot/scripts/game_manager.gd:69, 271`

### Bug 3: Packaging Script .pck Name Mismatch
- **Discovered:** During first package attempt
- **Cause:** Godot exports as `P(Doom)1.pck` (project name), not `PDoom.pck`
- **Fix:** Updated script to find and rename .pck file
- **Files:** `package_release.sh:35-44`

## Time Savings

- **Planned:** 7 hours total (2.5h Tier 1 + 2h Tier 2 + 1.5h release prep)
- **Actual:** ~5 hours (1.5h Tier 1 + 1h Tier 2 + 1h release prep + 1.5h bug fixes)
- **Saved:** 2+ hours vs plan
- **Why Faster:**
  - Danger warnings simpler than planned (thresholds vs projections)
  - Queue controls reused existing patterns
  - No complex refactoring needed

## Issues Closed

- **#389** - Action Points Validation (resolved by design - submenus intentionally 0 AP)
- **#435** - GDScript warnings cleanup (already closed)
- **#431** - Game description refinement (already closed)

## Remaining Tasks for User

1. **✅ DONE:** GitHub release created and live
2. **⏳ TODO:** Commit final changes
   ```bash
   git add .
   git commit -m "chore: Release automation and cleanup for v0.10.1+"
   git push origin main
   ```
3. **⏳ TODO:** Update pdoom1.com website (~1 hour reserved)
4. **⏳ TODO:** Test download from GitHub (optional but recommended)

## Key Files Modified

### Core Game Logic
- `godot/scripts/game_manager.gd` - AP tracking, queue management
- `godot/scripts/ui/main_ui.gd` - Button states, warnings, queue UI
- `godot/scripts/core/game_state.gd` - Variable renaming
- `godot/scenes/main.tscn` - Button text updates

### Documentation
- `README.md` - Download link, description update
- `CHANGELOG.md` - v0.10.1 documentation
- `.github/RELEASE_CHECKLIST.md` - New
- `scripts/README.md` - New

### Infrastructure
- `package_release.sh` - Enhanced .pck handling, version-agnostic
- `create_github_release.sh` - Version-agnostic, CHANGELOG fallback
- `scripts/bump_version.sh` - New version bumper
- `.github/workflows/pre-release-checks.yml` - New
- `.github/workflows/release-reminder.yml` - New

## Lessons Learned

1. **Test Godot parsing early** - Parse errors blocked export
2. **Godot .pck naming** - Uses project name, not exe name
3. **Variable naming consistency** - Underscore prefix requires updating all references
4. **Version-agnostic scripts** - Makes future releases easier
5. **Archive old release files** - Keeps root clean
6. **Time buffer works** - Saved 2h for unexpected bug fixes

## Next Steps for Future Releases

1. Use `bash scripts/bump_version.sh <version>` to start
2. Follow `.github/RELEASE_CHECKLIST.md`
3. GitHub Actions will validate automatically
4. Package scripts now handle .pck naming correctly
5. Archive release-specific files after completion

## Success Metrics

- ✅ Zero GDScript warnings
- ✅ Zero parse errors
- ✅ All Tier 1 & 2 features implemented
- ✅ GitHub release created successfully
- ✅ Package tested and working
- ✅ Documentation complete
- ✅ Future release process automated
- ✅ Released on schedule (before bed!)

## Session End State

**Git Status:** Clean (after final commit)
**Godot Status:** Builds without warnings
**Release Status:** v0.10.1 live on GitHub
**Infrastructure:** Release automation in place for future versions
**Mood:** 🎉 Successful sprint!

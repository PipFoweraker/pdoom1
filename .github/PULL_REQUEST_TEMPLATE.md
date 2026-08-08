## Summary
<!-- Brief description of what this PR does -->


## Changes
<!-- List the key changes made -->
-


## UI/Style Guide Checklist
<!-- If this PR modifies UI-related files, please review this checklist -->

### Does this PR modify any of the following?
- [ ] Theme colors or styling (`theme_manager.gd`)
- [ ] UI scenes (`godot/scenes/*.tscn`)
- [ ] Textures or visual assets (`godot/assets/textures/`, `godot/assets/ui/`)
- [ ] New `Color()` definitions in GDScript

### If yes, did you:
- [ ] Update `godot/UI_STYLE_GUIDE.md` with any new colors, textures, or patterns
- [ ] Follow the existing design system (spacing, typography, color palette)
- [ ] Maintain accessibility standards (contrast ratios, focus indicators)

**Note:** The pre-commit hook will remind you if UI files are modified without updating the style guide. You can skip this check with `git commit --no-verify` if the changes don't require documentation updates.


## Ladder impact
<!--
REQUIRED if this PR touches anything under godot/ that is not UI/scenes/assets/
theme/tests/docs -- the Ladder Bump Gate (quality-checks) fails without it.
Answer BUILD_VS_LADDER_VERSION_SPLIT.md Section 3.3: could this change a score,
a trajectory on a fixed seed, the seed schedule, the RNG stream, or the reachable
content? Any yes -> bump ladder_version.txt and run python tools/sync_version.py.

Uncomment ONE line (keep the exact prefix -- CI greps for it):
-->
<!-- Ladder-Impact: none -- <why this cannot change any run outcome> -->
<!-- Ladder-Impact: bump -- <what run outcome changes> -->


## Test Plan
<!-- How should reviewers test these changes? -->
- [ ]


## Screenshots
<!-- If UI changes, include before/after screenshots -->


---
Generated with [Claude Code](https://claude.com/claude-code)

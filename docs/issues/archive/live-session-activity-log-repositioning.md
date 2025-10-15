# LIVE SESSION: Activity Log Repositioning

## Issue Summary
Activity log needs to be repositioned to right-hand side of screen, with action buttons made smaller to accommodate this change.

## Current State
- Activity log is currently positioned in bottom-left of context area
- Action buttons take up significant horizontal space
- Layout could be optimized for better information display

## Proposed Changes
1. **Move activity log to right side**: Position activity log vertically on right side of screen
2. **Smaller action buttons**: Reduce action button size to make room for repositioned log
3. **Improved layout**: Better balance between actions and information display

## Implementation Points
- Update UI layout in `ui_new/screens/game.py` 
- Modify `draw_activity_log_3column()` positioning
- Adjust action button sizing in three-column layout
- Maintain readability while optimizing space usage

## Priority
**HIGH** - Live session enhancement

## Files to Modify
- `ui_new/screens/game.py`
- `ui_new/layouts/three_column.py`
- Layout calculation functions

## Acceptance Criteria
- [ ] Activity log appears on right side of screen
- [ ] Action buttons are appropriately sized
- [ ] Layout is visually balanced
- [ ] All text remains readable
- [ ] No UI overlap issues

## Labels
`enhancement`, `ui-ux`, `live-session`, `layout`

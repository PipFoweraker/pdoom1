# MONOLITH BREAKDOWN: Extract core draw_ui function (662 lines)\n\n## Overview
Continue the UI monolith breakdown by extracting the massive `draw_ui` function - the largest remaining function in ui.py.

## Target Function
- **Function**: `draw_ui` (lines 1178-1840, ~662 lines)
- **Impact**: 13% of entire ui.py file  
- **Current file size**: ~4,800 lines (down from 5,031)

## Breakdown Strategy
The massive `draw_ui` function should be broken into logical sub-functions:

1. **Resource display rendering** (money, staff, reputation, action points)
2. **Action button management** (filtered actions, compact/traditional modes)  
3. **Upgrade panel handling** (purchased upgrades, available upgrades)
4. **Activity log display** (scrollable log, minimize/expand)
5. **Context window rendering** (hover information, persistent display)
6. **UI transitions and overlays** (popup events, upgrade transitions)

## Implementation Approach
- Create `src/ui/game_ui.py` module
- Extract logical sub-functions from `draw_ui`
- Maintain existing function signature for compatibility
- Update main `draw_ui` to orchestrate sub-functions
- Add comprehensive type annotations following established patterns

## Previous Progress (Session 2025-09-15)  
✅ Tutorial functions extracted (486 lines)
✅ Critical hover bug fixed (Issue #263)
✅ Legacy function removed (151 lines)
✅ Modular architecture established

## Acceptance Criteria
- [ ] `draw_ui` function broken into 5-7 logical sub-functions
- [ ] Sub-functions moved to `src/ui/game_ui.py`
- [ ] Main `draw_ui` acts as orchestrator (< 100 lines)
- [ ] Game launches and renders correctly 
- [ ] All existing functionality preserved
- [ ] Type annotations maintained
- [ ] Comprehensive testing validated

## Expected Impact
- **Lines reduced**: ~500-600 lines from main function body
- **Maintainability**: Much easier to understand and modify game UI
- **Modularity**: Individual UI components can be tested/modified independently
- **Progress**: Will bring monolith breakdown to ~20-25% completion

## Next Session Priority
This should be the **primary focus** of the next monolith breakdown session as it provides the highest impact for effort invested.

**Estimated effort**: 2-3 hours of focused extraction work
**Priority**: HIGH - Maximum impact function\n\n<!-- GitHub Issue #303 -->
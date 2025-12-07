# Issue #418 Fix: Turn Sequencing and Event Timing

**Date**: 2025-10-30
**Issue**: [#418 - Turn Sequencing and Event Timing Problems](https://github.com/PipFoweraker/pdoom1/issues/418)
**Status**: SUCCESS FIXED in Godot Pure GDScript implementation
**Files Modified**: 4 files

---

## Problem Summary

Events were triggering **AFTER** actions were executed, breaking player agency. Players would:
1. Select actions
2. End turn
3. **THEN** see events that should have influenced their decisions

This violated the principle that players should have full information before making choices.

---

## Solution: Proper Turn Phases

Implemented 4-phase turn architecture as designed in `shared_bridge/turn_architecture.py`:

### Turn Flow (CORRECTED)

```
Phase 1: TURN_START
|-- Process maintenance (staff salaries, compute generation)
|-- CHECK FOR EVENTS  <-  FIX: Events happen FIRST
|-- If events exist:
|  |-- Block action selection
|  |-- Present events to player
|  `-- Wait for resolution
`-- If no events:  ->  Transition to Phase 2

Phase 2: ACTION_SELECTION
|-- Player sees ALL information
|-- Player selects actions (no execution yet)
`-- Player commits turn  ->  Phase 3

Phase 3: TURN_PROCESSING
|-- Execute queued actions
|-- Update game state
|-- Check win/lose conditions
`--  ->  Phase 4

Phase 4: TURN_END
|-- Prepare for next turn
`-- Loop back to Phase 1
```

---

## Files Modified

### 1. [godot/scripts/core/game_state.gd](../godot/scripts/core/game_state.gd)

**Added turn phase tracking:**
```gdscript
enum TurnPhase { TURN_START, ACTION_SELECTION, TURN_PROCESSING, TURN_END }
var current_phase: TurnPhase = TurnPhase.ACTION_SELECTION
var pending_events: Array[Dictionary] = []
var can_end_turn: bool = false
```

**Purpose**: Track which phase the turn is in and block inappropriate actions.

---

### 2. [godot/scripts/core/turn_manager.gd](../godot/scripts/core/turn_manager.gd)

**Modified `start_turn()`** - Lines 10-67:
- SUCCESS Check for events **FIRST** (line 47)
- SUCCESS If events exist, stay in TURN_START phase and block actions
- SUCCESS If no events, transition to ACTION_SELECTION phase
- SUCCESS Return `triggered_events` array for GameManager to emit

**Modified `execute_turn()`** - Lines 69-129:
- ERROR **REMOVED** event checking from line 88 (was duplicate)
- SUCCESS Events now only check at turn START, not turn END

**Added `resolve_event()`** - Lines 131-168:
- SUCCESS Handle event resolution during TURN_START phase
- SUCCESS Remove resolved event from `pending_events`
- SUCCESS Transition to ACTION_SELECTION when all events resolved
- SUCCESS Return phase transition info to GameManager

---

### 3. [godot/scripts/game_manager.gd](../godot/scripts/game_manager.gd)

**Modified `start_new_game()`** - Lines 19-46:
- SUCCESS Handle initial events that may trigger on turn 1
- SUCCESS Emit events before actions if present
- SUCCESS Emit correct phase ("turn_start" or "action_selection")

**Modified `select_action()`** - Lines 48-86:
- SUCCESS **BLOCK** if `pending_events.size() > 0` (line 47-49)
- SUCCESS **BLOCK** if not in ACTION_SELECTION phase (line 52-54)
- SUCCESS Show error message to player

**Modified `start_next_turn()`** - Lines 125-149:
- SUCCESS Emit triggered events from turn_result
- SUCCESS Block action list emission if events pending
- SUCCESS Emit correct phase to UI

**Modified `resolve_event()`** - Lines 156-177:
- SUCCESS Use `turn_manager.resolve_event()` instead of direct GameEvents call
- SUCCESS Handle phase transition when all events resolved
- SUCCESS Emit actions_available when transitioning to ACTION_SELECTION

---

## Key Changes

### Before (BROKEN) ERROR
```
end_turn():
  1. Execute actions immediately
  2. Process turn
  3. Check events  <-  TOO LATE!
  4. Player sees events AFTER actions executed
```

### After (FIXED) SUCCESS
```
start_turn():
  1. Check events FIRST
  2. If events: Block until resolved
  3. Once resolved: Enable action selection

select_action():
   ->  Blocked if events pending

end_turn():
  1. Execute actions
  2. Process turn
  3. No event checking (already happened)
```

---

## Testing Instructions

### Test Case 1: Events Block Actions

1. **Setup**: Use seed that triggers turn 1 event (e.g., "test-event-seed")
2. **Run**: Start new game
3. **Expected**:
   - SUCCESS Event popup appears immediately
   - SUCCESS Action buttons are disabled/hidden
   - SUCCESS Cannot select actions
   - SUCCESS Error message if action attempted: "Resolve pending events first!"

### Test Case 2: Event Resolution Enables Actions

1. **Setup**: Game with pending event
2. **Run**: Resolve event by choosing an option
3. **Expected**:
   - SUCCESS Event dialog closes
   - SUCCESS Phase transitions to "action_selection"
   - SUCCESS Action buttons become available
   - SUCCESS Message log shows event resolution
   - SUCCESS Can now select actions normally

### Test Case 3: No Events  ->  Direct to Actions

1. **Setup**: Use seed with no early events (e.g., "no-event-seed")
2. **Run**: Start new game / end turn
3. **Expected**:
   - SUCCESS No event popups
   - SUCCESS Actions immediately available
   - SUCCESS Phase is "action_selection"
   - SUCCESS Can select and queue actions

### Test Case 4: Multiple Events Sequential

1. **Setup**: Turn that triggers multiple events
2. **Run**: Resolve first event
3. **Expected**:
   - SUCCESS First event resolves
   - SUCCESS Second event appears immediately
   - SUCCESS Actions still blocked
   - SUCCESS Only after ALL events: actions enabled

### Test Case 5: Event -> Actions -> Turn End

1. **Setup**: Normal turn with event
2. **Run**: Full turn cycle
3. **Expected Flow**:
   ```
   1. Turn starts  ->  Event popup
   2. Resolve event  ->  Actions available
   3. Select actions  ->  Actions queued
   4. End turn  ->  Actions execute
   5. Next turn starts  ->  Check for new events
   ```

---

## Verification Checklist

- [ ] Events appear **before** action selection every turn
- [ ] Action selection **blocked** when events pending
- [ ] Clear error message if actions attempted during events
- [ ] Phase transitions correctly: TURN_START  ->  ACTION_SELECTION
- [ ] Multiple events resolve sequentially before actions
- [ ] No duplicate event checking (removed from execute_turn)
- [ ] Turn 1 events work correctly
- [ ] No events scenario works (direct to actions)

---

## Architecture Compliance

This fix implements the **ideal turn architecture** as documented in:
- `shared_bridge/turn_architecture.py` (Python bridge version)
- Now also in Pure GDScript implementation

Both implementations now follow the same correct turn flow:
1. SUCCESS Events FIRST (information gathering)
2. SUCCESS Actions SECOND (decision making with full info)
3. SUCCESS Execution THIRD (commitment)
4. SUCCESS Cleanup FOURTH (prepare next turn)

---

## Benefits

### For Players
- SUCCESS **Full Information**: See all events before making decisions
- SUCCESS **Player Agency**: Events can influence action choices
- SUCCESS **Clear Feedback**: Know when/why actions are blocked
- SUCCESS **Intuitive Flow**: Events  ->  Decisions  ->  Consequences

### For Developers
- SUCCESS **Clean Architecture**: Clear phase separation
- SUCCESS **Predictable Flow**: Turn phases enforce correct sequencing
- SUCCESS **Testable**: Phase state makes testing easier
- SUCCESS **Maintainable**: Logic in correct places

---

## Future Enhancements

### Deferred Events (Future)
```gdscript
# Option to defer non-critical events
func defer_event(event: Dictionary):
    state.deferred_events.append(event)
    # Will trigger at end of turn or next turn start
```

**Use case**: Player wants to make urgent decisions without interruption.

**Design note**: Mark in future as enhancement, not required for MVP.

---

## Related Documentation

- **Original Issue**: [#418](https://github.com/PipFoweraker/pdoom1/issues/418)
- **Turn Architecture Design**: [shared_bridge/turn_architecture.py](../shared_bridge/turn_architecture.py)
- **Phase 5 Session Notes**: [SESSION_HANDOFF_2025-10-30_GODOT_PHASE_5.md](../docs/development-sessions/SESSION_HANDOFF_2025-10-30_GODOT_PHASE_5.md)

---

**Fix Completed**: 2025-10-30
**Tested**: Pending (see test cases above)
**Status**: Ready for gameplay testing

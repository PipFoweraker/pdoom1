# Issue: Turn Sequencing and Event Timing Problems

## Problem Description

**Reported Issue**: Events are appearing out of sequence during turn processing. Specifically:
- Player takes actions and clicks "End Turn" 
- Events that should appear before action selection are showing up after actions are committed
- This breaks the intended game flow where players should see all available events/opportunities before making decisions

**Example Scenario**:
1. Player quickly advances through several turns using space bar
2. Player attempts to end turn by clicking
3. Click doesn't work initially (likely due to turn processing state)
4. Player takes an action and ends turn successfully  
5. "Industry networking event" popup appears - but should have appeared BEFORE action selection

## Root Cause Analysis

### Current Turn Flow (Problematic)
```
end_turn() method current sequence:
1. Clear messages
2. Execute selected actions (immediate commitment)
3. Process staff maintenance  
4. Process opponent actions
5. trigger_events() <- EVENTS HAPPEN AFTER ACTIONS!
6. Check milestones
7. Handle deferred events  
8. Increment turn counter
9. Reset action points
```

### Issues with Current Flow
1. **Events trigger after action commitment** - Players can't respond to events that should influence their decisions
2. **No pre-action event phase** - Events that unlock new actions or change strategy appear too late
3. **Poor player agency** - Players commit to actions without seeing all available information
4. **Confusing UX** - Events appear to "interrupt" the turn flow rather than guide it

## Proposed Solution: Proper Turn Sequencing

### Ideal Turn Flow Architecture
```
Turn Start Phase:
1. Process pending/deferred events from previous turn
2. trigger_events() - NEW EVENTS APPEAR FIRST
3. Update available actions based on new game state
4. Present all information to player for decision making

Action Selection Phase:  
5. Player selects actions (can see all current events/opportunities)
6. Player commits turn (clicks "End Turn")

Turn Processing Phase:
7. Execute committed actions
8. Process staff maintenance
9. Process opponent turns  
10. Update game state from opponent actions
11. Check milestone triggers
12. Increment turn counter
13. Reset action points for next turn

Turn End Phase:
14. Update UI to reflect all changes
15. Prepare for next turn cycle
```

## Implementation Strategy

### Option 1: Gradual Refactor (Recommended)
**Scope**: Medium complexity, preserves backward compatibility
**Approach**: 
- Create new `start_turn()` method for pre-action event processing
- Move `trigger_events()` to start of turn cycle
- Maintain current `end_turn()` for action execution
- Add turn state tracking (`turn_phase`: 'events', 'actions', 'processing')

### Option 2: Complete Architecture Redesign  
**Scope**: High complexity, breaks compatibility
**Approach**:
- Separate turn phases into distinct methods
- Implement state machine for turn flow
- Redesign event system for proper timing
- Extensive testing and migration required

### Option 3: Quick Fix (Temporary)
**Scope**: Low complexity, minimal changes
**Approach**:
- Move `trigger_events()` to very beginning of `end_turn()`
- Add event processing before action execution
- Risk: May introduce other timing issues

## Recommended Implementation

### Phase 1: Move Event Processing (Quick Win)
```python
def end_turn(self):
    # ... existing turn_processing guards ...
    
    # MOVE THIS TO THE BEGINNING
    self.trigger_events()  # Events happen BEFORE actions
    
    # Handle any pending popup events before continuing
    if hasattr(self, 'pending_popup_events') and self.pending_popup_events:
        # Don't process actions until events are resolved
        return False  # Indicate turn not complete
    
    # Now execute actions after player has seen all events
    for idx in self.selected_actions:
        # ... existing action execution ...
```

### Phase 2: Add Turn State Management
```python
# Add to GameState.__init__()
self.turn_phase = 'events'  # 'events', 'actions', 'processing', 'complete'

def process_turn_events(self):
    """Handle events at start of turn before action selection."""
    self.turn_phase = 'events'
    self.trigger_events()
    # If popup events exist, stay in events phase
    if not self.has_pending_popups():
        self.turn_phase = 'actions'
    
def end_turn(self):
    """Execute actions and process turn after events are handled."""
    if self.turn_phase != 'actions':
        return False  # Events must be resolved first
        
    self.turn_phase = 'processing'
    # ... existing action execution logic ...
```

### Phase 3: UI Integration
- Update UI to show turn phase clearly
- Disable "End Turn" button during events phase
- Add visual indicators for pending events
- Improve feedback for why actions might be blocked

## Testing Strategy

### Critical Test Cases
1. **Event Ordering**: Events appear before action selection
2. **Popup Blocking**: Turn can't advance until popups are resolved  
3. **Deferred Events**: Deferred events trigger at proper times
4. **Action Availability**: Actions update correctly after events
5. **Turn States**: Turn phases transition correctly
6. **Backward Compatibility**: Existing saves/games work correctly

### Test Scenarios
```python
def test_events_before_actions():
    # Setup game state to trigger event
    # Start new turn
    # Verify event triggers before action selection
    # Verify actions are unavailable until event resolved

def test_popup_blocks_turn():
    # Trigger popup event
    # Attempt to end turn
    # Verify turn doesn't advance
    # Resolve popup
    # Verify turn can now advance
```

## Files Requiring Changes

### Core Files
- `src/core/game_state.py` - Main turn logic refactor
- `src/features/event_system.py` - Event timing adjustments  
- `ui.py` - Turn phase indicators and feedback
- `main.py` - Turn processing in main game loop

### Test Files  
- `tests/test_end_turn_reliability.py` - Update turn sequencing tests
- `tests/test_events.py` - Add event timing tests
- New: `tests/test_turn_sequencing.py` - Comprehensive turn flow tests

## Risk Assessment

### High Risk
- **Save Compatibility**: Turn state changes may break existing saves
- **Event System Interactions**: Complex interactions between old/new event systems
- **Performance**: Additional turn processing phases may impact performance

### Medium Risk  
- **UI Complexity**: Turn phase management adds UI state complexity
- **Testing Burden**: Requires extensive regression testing
- **Player Confusion**: Changed turn flow may confuse existing players

### Mitigation Strategies
- **Feature Flags**: Implement behind feature flag for gradual rollout
- **Migration Path**: Provide save game migration utilities
- **Documentation**: Update player guide with new turn flow
- **Testing**: Comprehensive automated test suite before release

## Priority Assessment

**Impact**: High - Significantly improves game flow and player agency
**Complexity**: Medium - Requires careful refactoring but not complete rewrite  
**Risk**: Medium - Changes core game mechanics but preserves functionality
**Effort**: Medium - Estimated 1-2 weeks of focused development

**Recommendation**: Implement Phase 1 (Move Event Processing) immediately as it provides significant improvement with minimal risk, then evaluate need for Phase 2/3 based on player feedback.

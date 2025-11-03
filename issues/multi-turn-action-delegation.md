# Multi-Turn Action Delegation System

## Summary
**PRIORITY: MEDIUM** - Implement multi-turn action sequences that allow delegation of decision-making to staff/managers, creating more strategic AP management.

## Strategic Context
- **Goal**: Enable complex actions like 'advertise -> receive applicants -> interview -> hire'
- **Benefit**: Reduces micro-management while adding strategic depth
- **Timeline**: Beta phase enhancement (post-alpha)

## Vision
Players can initiate longer-term actions that unfold over multiple turns:
1. **Recruitment Process**: Advertise (1 AP) -> Get applicants (2 turns) -> Interview (1 AP) -> Decision
2. **Research Projects**: Start research (2 AP) -> Progress updates (3 turns) -> Results  
3. **Marketing Campaigns**: Launch campaign (1 AP) -> Market response (4 turns) -> Reputation effects

## Current State Analysis
- **Action system**: Single-turn immediate effects (`actions.py`)
- **Staff system**: Static productivity bonuses (`game_state.py`)  
- **Manager system**: Basic unproductivity prevention
- **AP system**: Turn-based allocation with staff bonuses

## Proposed Architecture

### Core Components
1. **ActionQueue System**: Track multi-turn action progression
2. **DelegationManager**: Handle staff-managed action decisions  
3. **ActionTemplate System**: Define multi-stage action patterns
4. **ProgressTracker**: Show player status of ongoing actions

### Implementation Plan

#### Phase 1: Action Queue Foundation
```python
class MultiTurnAction:
    def __init__(self, action_type, stages, delegated_to=None):
        self.stages = stages  # List of action stages
        self.current_stage = 0
        self.delegated_to = delegated_to  # Staff member handling
        
class ActionQueue:
    def __init__(self):
        self.active_actions = []
    
    def process_turn(self, game_state):
        # Advance all active multi-turn actions
        for action in self.active_actions:
            action.advance_stage(game_state)
```

#### Phase 2: Delegation System
```python
class DelegationManager:
    def can_delegate(self, action_type, staff_member):
        # Check if staff has skills for action
        
    def delegate_decision(self, action, options, staff_member):
        # Staff makes decision based on AI/rules
```

#### Phase 3: UI Integration
- **Action Queue Display**: Show progress of ongoing actions
- **Delegation Interface**: Assign actions to specific staff
- **Progress Notifications**: Turn-by-turn updates on action status

## Example Action Flows

### Recruitment (3-4 turns)
1. **T1**: Player spends 1 AP to 'Post Job Advertisement'
2. **T2-T3**: Applications arrive (automatic)  
3. **T4**: Manager reviews applications (if delegated) OR player chooses (1 AP)
4. **T5**: Hiring decision executed

### Research Project (5-7 turns)
1. **T1**: Player spends 2 AP to 'Start Research Project'
2. **T2-T5**: Research progresses (automatic updates)
3. **T6**: Results available, player decides on publication/secrecy (1 AP)
4. **T7**: Effects applied to game state

## Integration Points
- **File**: `src/core/game_state.py` - Add ActionQueue to GameState
- **File**: `actions.py` - Define multi-turn action templates  
- **File**: `ui.py` - Add action queue display components
- **File**: `src/systems/delegation.py` - New delegation management system

## Success Criteria
- [ ] Players can initiate multi-turn actions
- [ ] Actions progress automatically each turn  
- [ ] Staff can be assigned to handle action decisions
- [ ] UI clearly shows action queue status
- [ ] Delegated actions reduce player micro-management
- [ ] AP costs are front-loaded appropriately

## Technical Challenges
1. **Save/Load**: Persist action queue state
2. **Balance**: Ensure delegated actions aren't overpowered
3. **UI Space**: Display action progress without clutter
4. **AI Logic**: Smart delegation decisions by AI staff

## Dependencies
- **Staff Management System**: Requires improved staff skill system
- **Action Framework**: May need action system refactor
- **Manager System**: Enhanced manager capabilities

## Priority: MEDIUM
**Effort**: 1-2 weeks (significant system addition)
**Impact**: Major gameplay depth enhancement  
**Risk**: Medium (complex system with many interactions)
**Timeline**: Beta phase (after alpha stability)

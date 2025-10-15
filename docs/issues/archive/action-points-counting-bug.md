---
name: Action Points Counting Bug
about: Critical gameplay bug affecting action point system
title: 'Action Points Not Counting Correctly'
labels: bug, critical, gameplay, hotfix
assignees: ''

---

## ? Critical Issue: Action Points Counting Bug

**Version**: v0.3.0
**Priority**: Critical (affects core gameplay)
**Component**: Action Points System
**Type**: Logic/calculation bug

### Problem Description
Action points are not counting correctly, causing confusion about available actions and potentially breaking the core turn-based gameplay loop.

### Expected Behavior
- Action points should accurately reflect available actions
- Each action should properly consume the specified number of points
- UI should display current/maximum action points correctly
- Action point refresh should work properly between turns

### Current Behavior
- Action points counting incorrectly
- Possible discrepancy between UI display and actual game state
- May allow impossible actions or prevent valid ones

### Impact Assessment
- **Gameplay**: Breaks core turn mechanics
- **Balance**: Affects strategic decision-making
- **Player Experience**: Creates confusion and frustration
- **Tutorial**: May break learning flow

### Investigation Areas
1. **Game State Logic**: Check action point calculation in `game_state.py`
2. **Action System**: Verify action point consumption in `actions.py`
3. **UI Display**: Compare UI display with actual state values
4. **Turn Management**: Check action point refresh between turns

### Potential Root Causes
- UI display bug (visual only)
- Game state calculation error
- Action consumption logic bug
- Turn transition issue

### Acceptance Criteria
- [ ] Action points calculate correctly in all scenarios
- [ ] UI accurately displays current action points
- [ ] Actions consume correct number of points
- [ ] Action point refresh works between turns
- [ ] No phantom actions or blocked valid actions
- [ ] Pass all action point unit tests

### Implementation Investigation
```python
# Debug action points system
from src.core.game_state import GameState
gs = GameState('test-action-points')
print(f'Starting AP: {gs.action_points}')
# Test action execution and point consumption
```

### Testing Scenarios
1. Start new game, verify initial action points
2. Execute various actions, verify point consumption
3. End turn, verify action point refresh
4. Test edge cases (0 points, maximum actions)

### Related Systems
- Turn management
- Action execution system
- UI state synchronization
- Save/load functionality

**Target Release**: v0.3.1 (immediate hotfix)
**Estimated Effort**: 2-6 hours (depending on root cause)

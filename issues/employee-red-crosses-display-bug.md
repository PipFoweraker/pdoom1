---
name: Employee Red Crosses Not Displaying Correctly
about: Critical UI bug affecting employee status visualization
title: "[HOTFIX] Employee red crosses not showing properly in UI"
labels: bug, critical, ui, hotfix
assignees: ''

---

## 🔴 Critical Issue: Employee Red Crosses Display Bug

**Version**: v0.3.0
**Priority**: Critical (affects core UX)
**Component**: UI System
**Type**: Visual feedback bug

### Problem Description
Employee red crosses are not displaying properly in the user interface, making it difficult for players to understand employee status and make informed decisions.

### Expected Behavior
- Red crosses should clearly indicate employee status (fired, unavailable, etc.)
- Visual feedback should be consistent and immediately visible
- Status changes should update the display in real-time

### Current Behavior
- Red crosses not showing properly
- Employee status unclear to players
- Potential confusion about workforce management

### Impact Assessment
- **User Experience**: High negative impact
- **Gameplay**: Affects decision-making
- **Tutorial**: May confuse new players
- **Accessibility**: Reduces visual clarity

### Investigation Areas
1. **UI Rendering**: Check `ui.py` employee display functions
2. **State Management**: Verify employee status tracking in `game_state.py`
3. **Visual Assets**: Confirm red cross graphics loading correctly
4. **Update Logic**: Ensure status changes trigger UI updates

### Acceptance Criteria
- [ ] Red crosses display correctly for all employee states
- [ ] Visual feedback is immediate and clear
- [ ] Status changes update UI in real-time
- [ ] No regression in other UI elements
- [ ] Pass visual validation tests

### Implementation Notes
- Check employee rendering logic in UI system
- Verify sprite/icon loading and positioning
- Test status change triggers and updates
- Validate across different game states

### Related Issues
- May be related to general UI update system
- Could affect other status indicators

### Testing Protocol
```python
# Test employee status display
from src.core.game_state import GameState
gs = GameState('test-employee-ui')
# Test various employee status scenarios
```

**Target Release**: v0.3.1 (immediate hotfix)
**Estimated Effort**: 2-4 hours (UI debugging + testing)

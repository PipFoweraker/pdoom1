# Mouse Wheel Scrolling Breaks Game

## Summary
**CRITICAL BUG**: Mouse wheel scrolling causes game to break/crash, making the game unplayable for users with mouse wheels.

## Problem Description
- Mouse wheel input crashes or breaks the game
- Discovered during expanded testing (not caught in initial development)
- Affects any user with a standard mouse wheel
- Complete game failure when mouse wheel is used

## Expected Behavior
- Mouse wheel should either:
  - Be ignored safely (no crash)
  - Provide useful functionality (scroll through menus/lists)
  - Handle input gracefully without breaking game state

## Current Behavior (Critical)
- Game breaks/crashes when mouse wheel is used
- Complete failure of game functionality
- Unrecoverable state requiring restart

## Impact Assessment
- **Severity**: CRITICAL - Game breaking
- **Scope**: Affects all users with mouse wheels (majority of players)
- **User Experience**: Complete failure, game unplayable
- **Discovery**: Missed in testing due to no mouse wheel usage

## Root Cause Analysis
Likely causes:
- Unhandled pygame mouse wheel events
- Event handler not catching MOUSEWHEEL events
- Improper event processing causing state corruption
- Missing input validation for wheel events

## Investigation Steps
1. Check pygame event handling loop
2. Look for MOUSEWHEEL event processing
3. Test mouse wheel in different game states
4. Verify event handler robustness
5. Check for state corruption on wheel input

## Files Likely Involved
- `main.py` - Main event loop
- Input handling systems
- pygame event processing
- UI event handlers

## Immediate Fix Required
Priority fix approaches:
1. **Quick Fix**: Safely ignore mouse wheel events
2. **Proper Fix**: Handle mouse wheel events gracefully
3. **Enhancement**: Add useful mouse wheel functionality

## Code Investigation
Check for:
```python
# Missing in event loop:
elif event.type == pygame.MOUSEWHEEL:
    # Handle or ignore safely
    pass
```

## Priority
**CRITICAL** - Game breaking bug affecting majority of users

## Labels
- bug
- critical
- input-handling
- mouse-wheel
- game-breaking

## Acceptance Criteria
- [ ] Mouse wheel input does not crash game
- [ ] Game remains stable with mouse wheel usage
- [ ] Proper event handling for all mouse inputs
- [ ] No regression in existing mouse functionality
- [ ] Test across different game states/screens

## Testing Requirements
- Test with various mouse types and wheel configurations
- Test in all game screens (menu, gameplay, overlays)
- Verify no state corruption from wheel events
- Ensure smooth gameplay with wheel-equipped mice

## Assignee
@PipFoweraker

---
*CRITICAL BUG - Immediate fix required for game stability*

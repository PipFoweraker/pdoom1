# Seed Selection Screen: Up/Down Arrow Navigation Broken

## Summary
The up/down arrow keys do not function in the 'Select Seed' screen during new game setup, preventing keyboard navigation through seed options.

## Problem Description
When working through new game options and reaching the seed selection screen:
- Up/down arrow keys have no effect
- User cannot navigate seed options using keyboard
- May affect other menu screens with similar navigation patterns

## Expected Behavior
- Up arrow should move to previous seed option
- Down arrow should move to next seed option
- Arrow key navigation should be consistent across all menu screens

## Current Behavior
- Arrow keys are non-responsive in seed selection
- Navigation only works with mouse (if at all)
- Inconsistent user experience across menu system

## Root Cause Analysis
This appears to be a general menu navigation issue that could affect:
- Seed selection screen specifically
- Other menu screens with list navigation
- General keyboard input handling in menu contexts

## Suggested Solution Scope
Consider fixing at a higher level:
- **Menu screen level**: Fix navigation for all menu screens
- **Starting game screen level**: Ensure consistent keyboard navigation
- **Input handling**: Review keyboard event processing in menu contexts

## Impact
- **User Experience**: Poor keyboard accessibility
- **Consistency**: Breaks expected navigation patterns
- **Accessibility**: Limits input method options for users

## Files Likely Involved
- Menu screen handling code
- Input event processing for menus
- Seed selection screen implementation
- Keyboard shortcut system

## Priority
**Medium-High** - Core navigation functionality broken

## Labels
- bug
- ui-ux
- menu-navigation
- keyboard-input
- accessibility

## Acceptance Criteria
- [ ] Up/down arrows work in seed selection screen
- [ ] Navigation is consistent across all menu screens
- [ ] Keyboard input is properly handled in menu contexts
- [ ] No regression in existing menu functionality

---
*Reported during hotfix/menu-navigation-fixes session*

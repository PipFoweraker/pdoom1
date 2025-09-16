# Seed Selection Screen: Up/Down Arrow Navigation Broken

## ✅ RESOLVED (v0.7.3) - 2025-09-16

**RESOLUTION**: Fixed by implementing proper keyboard navigation in seed selection screen. Added `seed_selected_item` tracking variable and complete UP/DOWN arrow handling.

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

## ✅ IMPLEMENTATION COMPLETED

**Fixed in commit 446f96d**: 
- Added `seed_selected_item` global variable for selection tracking
- Implemented proper UP/DOWN arrow navigation logic in `handle_seed_selection_keyboard`
- Updated `draw_seed_selection` call to use actual selection state
- Added selection reset when entering seed selection screen
- Follows established menu navigation patterns from other screens

**Verification**: 
- UP/DOWN arrows now navigate between "Use Weekly Seed" and "Use Custom Seed"
- Selection stays within bounds (0-1)
- Visual feedback shows selected option
- ENTER key selects chosen option and transitions properly
- ESCAPE key returns to previous screen

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

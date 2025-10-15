# Premature Laboratory Upgrade Popup on Game Start

## Summary
The 'Your First Laboratory Upgrade' popup appears immediately upon starting a new game in default mode, before any upgrade conditions should be met.

## Problem Description
As shown in the attached screenshot:
- New game starts in default mode
- 'Your First Laboratory Upgrade' popup appears instantly in top-right
- This occurs before player has taken any actions
- Popup should only appear when upgrade conditions are actually met

## Expected Behavior
- New game should start without upgrade popups
- 'Your First Laboratory Upgrade' should only appear when:
  - Player has actually unlocked their first upgrade
  - Proper trigger conditions are met
  - Player has taken relevant actions

## Current Behavior (Bug)
- Popup appears immediately on game instantiation
- No player actions required to trigger
- Appears in default/regular game mode
- Premature popup display confuses new players

## Root Cause Analysis
Likely causes:
- Incorrect initialization trigger logic
- Default game state incorrectly flagging upgrade availability
- Popup trigger checking wrong conditions
- First-time help system firing prematurely

## Impact
- **New Player Experience**: Confusing popup before any context
- **Tutorial Flow**: Disrupts learning progression
- **UI Polish**: Makes game feel buggy or unfinished
- **Logic Integrity**: Indicates initialization logic issues

## Files Likely Involved
- Game initialization code
- Upgrade system triggers
- First-time help/popup system
- Default game state setup
- UI overlay management

## Investigation Steps
1. Check game initialization sequence
2. Review upgrade trigger conditions
3. Examine first-time help logic
4. Verify default game state setup
5. Test popup trigger timing

## Priority
**High** - Affects first impression for new players

## Labels
- bug
- ui-ux
- game-initialization
- popup-system
- new-player-experience

## Acceptance Criteria
- [ ] No premature popups on new game start
- [ ] 'Your First Laboratory Upgrade' only appears when earned
- [ ] Clean game initialization without unexpected UI
- [ ] Proper trigger conditions validated
- [ ] No regression in upgrade notification system

## Assignee
@PipFoweraker

## Screenshots
See attached screenshot showing premature popup on fresh game start.

---
*Reported during local testing session - hotfix/menu-navigation-fixes*

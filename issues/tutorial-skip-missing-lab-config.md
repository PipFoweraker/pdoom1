# Tutorial Skip: Missing Lab Configuration Screen

## Summary
When starting a new game, selecting 'No - Regular Mode' after the tutorial prompt bypasses the lab name configuration and other cosmetic setup options that should be available.

## Problem Description
The new game flow has a broken path:
1. Start new game
2. Tutorial screen appears: 'Would you like to do the tutorial?'
3. Select 'No - Regular Mode'
4. **PROBLEM**: Game starts immediately without lab configuration

## Missing Configuration Options
When skipping tutorial, users should still access:
- **Lab name configuration** (currently implemented)
- **Future cosmetic options** (planned):
  - Star sign selection
  - Animal types/mascots
  - Other personalization features

## Expected Behavior
Tutorial skip should lead to:
1. Tutorial prompt: 'Do tutorial?' -> 'No - Regular Mode'
2. **Lab Configuration Screen**: Set lab name, cosmetic options
3. Game starts with configured settings

## Current Behavior
Tutorial skip immediately starts game with default settings, bypassing all configuration.

## User Impact
- **Missing personalization**: No chance to set lab name
- **Future-proofing**: Will break when cosmetic options are added
- **User experience**: Inconsistent paths (tutorial vs non-tutorial)
- **Completeness**: Non-tutorial users get incomplete experience

## Technical Analysis
This suggests the game flow logic has:
- Missing screen transition after tutorial decline
- Direct jump to game start instead of configuration
- Need to separate tutorial flow from configuration flow

## Solution Requirements
1. **Immediate**: Fix tutorial skip to show lab configuration
2. **Architecture**: Separate tutorial decision from configuration screens
3. **Future-ready**: Ensure flow supports upcoming cosmetic features

## Flow Diagram (Desired)
```
New Game -> Tutorial Prompt -> No -> Lab Configuration -> Game Start
                            -> Yes -> Tutorial -> Lab Configuration -> Game Start
```

## Files Likely Involved
- Main menu/game start logic
- Tutorial system flow control
- Lab configuration screen
- Game initialization sequence

## Priority
**Medium** - Affects user personalization and future feature expansion

## Labels
- bug
- ui-ux
- game-flow
- tutorial
- configuration
- user-experience

## Acceptance Criteria
- [ ] Tutorial skip leads to lab configuration screen
- [ ] Lab name can be set regardless of tutorial choice
- [ ] Flow is ready for future cosmetic options
- [ ] Both tutorial and non-tutorial paths work correctly
- [ ] No regression in existing tutorial functionality

## Future Considerations
When adding cosmetic features (star signs, animals, etc.):
- This configuration screen should accommodate them
- All personalization should be in one place
- Tutorial choice should not affect configuration availability

---
*Reported during hotfix/menu-navigation-fixes session*

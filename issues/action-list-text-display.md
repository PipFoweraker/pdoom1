# Action List Text Display Issues

## Summary
Text display problems in the action list on the right-hand side of the screen affecting readability and user experience.

## Problem Description
From local testing, the action list (right side of screen) has text rendering or layout issues that impact usability during gameplay.

## Expected Behavior
- Action list text should be clearly readable
- Proper text alignment and spacing
- Consistent formatting across all action items
- No text overflow or truncation issues

## Current Behavior
- Text display issues in right-side action list
- Affects user ability to understand available actions
- May include alignment, spacing, or rendering problems

## Impact
- **User Experience**: Difficulty reading action information
- **Gameplay**: May prevent understanding of available actions
- **Accessibility**: Text readability is core functionality

## Investigation Required
- Check text rendering in action list component
- Verify font sizing and spacing calculations
- Test across different screen resolutions
- Validate text wrapping and overflow handling

## Files Likely Involved
- `ui.py` - Main UI rendering
- Action list rendering functions
- Text display and formatting code

## Priority
**High** - Core UI functionality affecting gameplay readability

## Labels
- bug
- ui-ux
- text-display
- action-list

## Acceptance Criteria
- [ ] Action list text is clearly readable
- [ ] Proper alignment and spacing maintained
- [ ] No text overflow or truncation
- [ ] Consistent formatting across all actions
- [ ] Works across different screen resolutions

## Assignee
@PipFoweraker

---
*Reported during local testing session - hotfix/menu-navigation-fixes*

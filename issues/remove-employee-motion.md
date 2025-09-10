# Remove Obsolete Employee Motion System

## Summary
The employee motion system is no longer needed and should be removed to simplify codebase and improve performance.

## Problem Description
Current system includes employee motion/animation functionality that is:
- No longer required for gameplay
- Adding unnecessary complexity
- Potentially impacting performance
- Creating maintenance overhead

## Background
The employee motion system was likely part of earlier game design but is now obsolete. Removing it will:
- Simplify the codebase
- Reduce computational overhead
- Eliminate unused code paths
- Make the system easier to maintain

## Expected Outcome
- Employee motion code removed
- No visual impact on core gameplay
- Improved performance
- Cleaner codebase

## Implementation Tasks
- [ ] Identify all employee motion-related code
- [ ] Remove motion/animation systems
- [ ] Clean up related assets if any
- [ ] Update any dependent systems
- [ ] Verify no regression in employee display/functionality

## Files Likely Involved
- Employee rendering code
- Animation/motion systems
- UI components showing employees
- Any employee-related assets

## Benefits
- **Performance**: Reduced computational overhead
- **Maintainability**: Less code to maintain
- **Clarity**: Simpler system architecture
- **Focus**: Remove distractions from core gameplay

## Priority
**Medium** - Code cleanup and optimization

## Labels
- technical-debt
- performance
- code-cleanup
- employee-system

## Acceptance Criteria
- [ ] Employee motion code completely removed
- [ ] No performance regression
- [ ] Employee display still functions correctly
- [ ] No broken dependencies
- [ ] Clean commit with clear documentation

## Assignee
@PipFoweraker

---
*Reported during local testing session - hotfix/menu-navigation-fixes*

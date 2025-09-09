# P(Doom) Change Attribution in Activity Log

## Summary
Ensure all p(Doom) increases and decreases show clear reasons in the activity log for better player understanding and debugging.

## Background
The game has verbose logging for resource changes, but p(Doom) changes in the activity log sometimes lack clear attribution. Players need to understand why p(Doom) increased or decreased to make informed decisions.

## Current State
- `GameState._add('doom', delta, reason)` logs to verbose logger when enabled
- Some doom changes have good reasons, others may show "unspecified"
- Verbose logs capture everything but may not be visible to average players

## Acceptance Criteria
- [ ] All `_add('doom', ...)` calls include descriptive reason strings
- [ ] Activity log shows: "p(Doom) +2: Research breakthrough risk" or "p(Doom) -1: Safety measures effective"
- [ ] Reasons are concise but informative (under 50 characters)
- [ ] Both positive and negative changes are clearly attributed
- [ ] Verbose logging captures detailed context for debugging

## Implementation Notes
- Audit existing `self._add('doom', ...)` calls for missing/weak reasons
- Add helper method `log_doom_change(reason, delta, source=None)` for consistency
- Ensure activity log messages are human-readable
- Consider doom change icons/formatting for visual clarity

## Files to Modify
- `src/core/game_state.py`: doom change call sites and helper method
- Any modules that modify doom directly

## Priority
Medium - improves player comprehension of a core game mechanic.

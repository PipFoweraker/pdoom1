# Expense Request Accept/Deny Label Consistency

## Summary
Standardize expense request popup labels and behavior to use 'Accept / Deny' consistently instead of the current 'Approve / Deny' text with ACCEPT/DISMISS actions.

## Background
The expense request system in `GameState._trigger_expense_request()` has inconsistent labeling:
- UI text says 'Approve the expense or deny the request?'
- Available actions are [ACCEPT, DISMISS] 
- Activity log messages use 'Approved' and 'Denied'

Players expect 'Accept / Deny' as the standard pattern throughout the UI.

## Acceptance Criteria
- [ ] Expense popup text updated to 'Accept the expense or deny the request?'
- [ ] Event actions align with UI labels (ACCEPT for accept, REDUCE for deny)
- [ ] Activity log messages use 'Accepted' and 'Denied' consistently
- [ ] Popup button labels display 'Accept' and 'Deny' (not 'Approve' and 'Dismiss')
- [ ] Behavior remains unchanged (accept spends money, deny triggers deny_effect)

## Implementation Notes
- Update `_trigger_expense_request()` event description text
- Change `available_actions` to [ACCEPT, REDUCE] with `reduce_effect=deny_expense`
- Add custom button labels to the Event system if needed
- Update activity log strings in approve_expense and deny_expense functions

## Files to Modify
- `src/core/game_state.py`: `_trigger_expense_request()` method
- Potentially `src/features/event_system.py`: custom button labels
- UI rendering: `draw_popup_events` in main UI system

## Priority
Low - cosmetic consistency fix that improves UX clarity.

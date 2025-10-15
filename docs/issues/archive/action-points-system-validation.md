# Action Points System Validation Issues

## Description
Action points system has validation issues where some actions have invalid AP costs.

## Affected Tests
- `test_action_points.py::TestActionPointsBackwardCompatibility::test_all_actions_have_ap_cost`

## Error Details
```
AssertionError: 0 not greater than 0
```

## Root Cause
Some actions in the game have AP costs of 0, which fails validation that expects all actions to have costs > 0.

## Expected Behavior
- All actions should have valid AP costs (> 0)
- OR: The test should account for legitimate 0-cost actions (meta-actions)
- Clear distinction between regular actions and meta-actions

## Investigation Areas
1. Action definitions and their AP costs
2. Meta-actions that legitimately cost 0 AP
3. Action validation logic
4. Backward compatibility requirements

## Priority
Medium - Affects game balance and action system integrity

## Labels
- bug
- action-points
- game-mechanics
- validation
- testing

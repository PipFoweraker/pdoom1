# Public Opinion System Logic Issues

## Description
Public opinion system has multiple logic and integration issues affecting game mechanics.

## Affected Tests
- `test_public_opinion_system.py::TestPublicOpinion::test_serialization`
- `test_public_opinion_system.py::TestMediaSystem::test_get_available_actions`
- `test_public_opinion_system.py::TestMediaSystem::test_press_release_action`

## Error Details
```
AssertionError: 67.0 != 65.0
TypeError: 'Mock' object is not iterable
AssertionError: expected call not found.
Expected: _add('money', -50000)
Actual: _add('reputation', 0)
```

## Root Cause
1. Public opinion serialization values don't match expected (67.0 vs 65.0)
2. Mock objects not properly configured for iteration
3. Press release action not calling correct resource modification (_add money vs reputation)

## Expected Behavior
- Public opinion should serialize to expected values
- Media system should return iterable actions list
- Press release should deduct money ($50,000) as expected

## Investigation Areas
1. Public opinion calculation and serialization logic
2. Media system action enumeration
3. Press release action implementation
4. Resource modification calls and parameters

## Priority
Medium - Affects public opinion game mechanics

## Labels
- bug
- public-opinion
- media-system
- game-mechanics
- serialization
- testing

# Event System Error Handling Issues

## Description
Event system has error handling and validation issues that cause test failures.

## Affected Tests
- `test_event_system.py::TestEventSystem::test_is_event_valid`
- `test_event_system.py::TestEventSystem::test_validate_event_config`

## Error Details
```
AssertionError: True is not false
Event validation should fail for invalid events but is returning True
```

## Root Cause
1. Event validation logic is too permissive
2. Invalid events are incorrectly marked as valid
3. Event configuration validation not catching malformed configs

## Expected Behavior
- `is_event_valid()` should return False for invalid events
- Event validation should catch configuration errors
- Malformed event configs should be rejected

## Investigation Areas
1. Event validation logic in event_system.py
2. Event configuration schema validation
3. Error handling for malformed events
4. Test cases for edge cases and invalid inputs

## Priority
Medium - Affects game stability and event processing

## Labels
- bug
- event-system
- validation
- error-handling
- testing

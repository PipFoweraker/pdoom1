# Tutorial System State Management Issues

## Description
Multiple tests are failing related to tutorial state management, specifically around `tutorial_enabled` state tracking.

## Affected Tests
- `test_tutorial_choice_improvements.py::TestTutorialChoiceNavigation::test_mouse_click_selection`
- `test_tutorial_choice_improvements.py::TestTutorialChoiceNavigation::test_keyboard_enter_selection` 
- `test_tutorial_choice_improvements.py::TestTutorialChoiceNavigation::test_keyboard_space_selection`
- `test_prelaunch_polish_integration.py::TestFullFeatureIntegration::test_complete_tutorial_choice_flow`

## Error Details
```
assert False == True
 +  where False = main.tutorial_enabled
```

## Root Cause
The `main.tutorial_enabled` state is not being properly set when tutorial choices are made through UI interactions.

## Expected Behavior
- Clicking 'Yes' in tutorial choice should set `tutorial_enabled = True`
- Clicking 'No' in tutorial choice should set `tutorial_enabled = False`
- Keyboard interactions should properly update the state

## Investigation Areas
1. `main.handle_tutorial_choice_click()` function
2. Tutorial choice state management in main loop
3. Integration between UI events and game state

## Priority
Medium - Affects new player onboarding experience

## Labels
- bug
- tutorial
- state-management
- testing

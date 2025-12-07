# Testing Strategy

## Overview

PDoom uses a comprehensive testing strategy to catch bugs early and prevent regressions. Tests run automatically on every push via GitHub Actions.

## Test Types

### 1. Unit Tests (`godot/tests/unit/`)

Test individual components in isolation:

- **test_actions.gd** - Action definitions and execution
- **test_events.gd** - Event system and triggers
- **test_game_state.gd** - Game state management
- **test_game_manager.gd** - Core game loop
- **test_turn_manager.gd** - Turn progression
- **test_upgrades.gd** - Upgrade system
- **test_bug_fixes.gd** - Regression tests for fixed bugs

### 2. Integration Tests (`godot/tests/integration/`)

Test component interactions and UI behavior:

- **test_ui_stability.gd** - UI element stability and keyboard handling

### 3. Smoke Tests (`godot/tests/smoke/`)

Quick sanity checks that the game boots and core features work.

## Running Tests

### Locally - Windows

```powershell
# Run all tests
.\godot\tests\run_all_tests.ps1

# Run specific test file
godot --headless --path .\godot --script res://addons/gut/gut_cmdln.gd -gtest=test_bug_fixes.gd
```

### Locally - Linux/Mac

```bash
# Run all tests
./godot/tests/run_all_tests.sh

# Run specific test file
godot --headless --path ./godot --script res://addons/gut/gut_cmdln.gd -gtest=test_bug_fixes.gd
```

### CI/CD

Tests run automatically on:
- Every push to main, develop, or feature branches
- Every pull request

See `.github/workflows/godot-tests.yml` for configuration.

## Writing Tests

### Test Structure

```gdscript
extends GutTest

func before_each():
    # Setup before each test
    state = GameState.new("test_seed")

func test_feature_name():
    # Arrange
    var expected = 42

    # Act
    var result = some_function()

    # Assert
    assert_eq(result, expected, "Result should match expected")
```

### Regression Test Pattern

When fixing a bug:

1. **Write a failing test first** - Reproduces the bug
2. **Fix the bug** - Implement the solution
3. **Verify test passes** - Confirms bug is fixed
4. **Document in test** - Add issue number and description

Example:

```gdscript
## Issue #449: Lobby Government action affordability
func test_lobby_government_no_reputation_cost():
    var lobby_action = _find_action("lobby_government")
    var costs = lobby_action.get("costs", {})

    # Should NOT have reputation cost (was bug in #449)
    assert_false(costs.has("reputation"),
        "lobby_government should NOT cost reputation (issue #449)")
```

## Test Categories

### Critical Path Tests

Tests that prevent game-breaking bugs:

- Event dialog soft-locks (#452)
- Game crashes (#447)
- Action affordability (#449)

### Stability Tests

Tests that ensure consistent behavior:

- UI element sizing and flickering (#450)
- Color coding and visual clarity (#451)
- Keyboard shortcut handling

### Validation Tests

Tests that enforce design rules:

- All actions have required fields
- No negative costs
- Valid category assignments
- Proper resource tracking

## Coverage Goals

- **Unit tests**: 80%+ coverage of core game logic
- **Integration tests**: All critical UI interactions
- **Regression tests**: Every fixed bug has a test

## Best Practices

### DO:
- SUCCESS Write tests for every bug fix
- SUCCESS Use descriptive test names
- SUCCESS Include issue numbers in comments
- SUCCESS Test both positive and negative cases
- SUCCESS Keep tests fast and focused

### DON'T:
- ERROR Test implementation details
- ERROR Create flaky tests
- ERROR Skip test documentation
- ERROR Forget to update tests when refactoring

## Continuous Improvement

### Adding New Tests

1. Create test file in appropriate directory
2. Follow naming convention: `test_<feature>.gd`
3. Use GUT assertions (assert_eq, assert_true, etc.)
4. Document test purpose and related issues
5. Run locally before committing
6. Verify CI passes

### Test Maintenance

- Review test failures immediately
- Update tests when features change
- Remove obsolete tests
- Keep test code clean and readable

## Tools

- **GUT** - Godot Unit Test framework
- **GitHub Actions** - Automated test execution
- **Godot headless mode** - Fast test execution

## Resources

- [GUT Documentation](https://github.com/bitwes/Gut)
- [Godot Testing Guide](https://docs.godotengine.org/en/stable/tutorials/scripting/unit_testing.html)
- [CI/CD Configuration](.github/workflows/godot-tests.yml)

## Test Metrics

Track these metrics to ensure quality:

- **Test count**: Growing with codebase
- **Pass rate**: Should be 100%
- **Execution time**: Keep under 2 minutes
- **Coverage**: Increasing over time

## Issue-to-Test Mapping

| Issue | Test File | Test Function |
|-------|-----------|---------------|
| #452 | test_ui_stability.gd | test_event_dialog_blocks_esc_key |
| #447 | test_bug_fixes.gd | test_difficulty_validation_handles_invalid_int |
| #449 | test_bug_fixes.gd | test_lobby_government_no_reputation_cost |
| #451 | test_ui_stability.gd | test_category_colors_are_prominent |
| #450 | test_ui_stability.gd | test_infobar_maintains_height |
| #448 | test_bug_fixes.gd | test_no_hire_office_cat_action |

## Future Improvements

- [ ] Add visual regression testing for UI
- [ ] Implement property-based testing
- [ ] Add performance benchmarks
- [ ] Create test data generators
- [ ] Add mutation testing
- [ ] Improve test reporting

---

**Last Updated**: 2025-11-15
**Test Framework**: GUT 9.x
**Godot Version**: 4.5.1

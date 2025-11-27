# Godot Testing Strategy
**Date:** October 30, 2025
**Status:** Design Phase

## Overview

This document outlines the testing strategy for the Godot migration, analyzing the 98 Python tests and determining which should be migrated, which can be eliminated, and how to structure the new test suite.

---

## Old Test Suite Analysis

### Test Count: 98 Python test files

### Categories:

**1. Core Game Logic Tests (HIGH PRIORITY - MUST MIGRATE)**
- `test_game_state.py` - Game state initialization and management
- `test_deterministic_rng.py` - RNG reproducibility
- `test_events.py` - Event system
- `test_shared_logic/test_events_engine.py` - Data-driven events
- `test_shared_logic/test_actions_engine.py` - Action execution
- `test_shared_logic/test_game_logic.py` - Core mechanics
- `test_action_points.py` - AP system
- `test_upgrades.py` - Upgrade system
- `test_economic_cycles.py` - Resource economics
- `test_public_opinion_system.py` - Reputation mechanics
- `test_scores.py` - Scoring system
- `test_leaderboard.py` - Leaderboard functionality

**Rationale:** These test the pure game logic that is now in GDScript. MUST verify correctness after migration.

---

**2. UI/Pygame-Specific Tests (LOW PRIORITY - MOST CAN BE ELIMINATED)**
- `test_menu_system_refactoring.py`
- `test_dialog_system_integration.py`
- `test_popup_improvements.py`
- `test_keyboard_shortcuts_ui.py`
- `test_ui_layout_utils.py`
- `test_ui_transitions.py`
- `test_ui_overlap_prevention.py`
- `test_pygame_mousewheel.py`
- `test_mouse_wheel_direct.py`
- `test_modal_dialog_integration.py`
- `test_overlay_manager.py`
- `test_end_game_menu.py`
- `test_loading_screen.py`
- `test_privacy_controls_ui.py`

**Rationale:** Godot handles UI differently with built-in nodes (Control, Button, Dialog, etc.). These tests verified pygame quirks that don't exist in Godot. **Replace with manual/visual testing.**

---

**3. Bug Fix Tests (MEDIUM PRIORITY - EXTRACT LOGIC, DISCARD REST)**
- `test_critical_bug_fixes.py`
- `test_critical_gameplay_bugs.py`
- `test_hotfix_batch.py`
- `test_issue_36_fixes.py`
- `test_hiring_dialog_fix.py`
- `test_turn6_spacebar_regression.py`
- `test_unbound_local_error_fix.py`
- `test_fixes.py`
- `test_navigation_fixes.py`

**Rationale:** These tests document specific bugs. **Review each** to extract underlying game logic that should still be tested, but don't migrate pygame-specific bug tests. The Godot version won't have the same bugs.

---

**4. Integration/Flow Tests (HIGH PRIORITY - MIGRATE PATTERNS)**
- `test_game_flow_improvements.py`
- `test_end_turn_reliability.py`
- `test_scenario_runner.py`
- `test_stepwise_tutorial.py`
- `test_tutorial_system.py`
- `test_new_player_experience.py`
- `test_onboarding.py`

**Rationale:** These test complete gameplay flows. **Migrate the test patterns** but adapt to Godot's architecture (signals, scenes, nodes).

---

**5. Feature-Specific Tests (VARIES - MIGRATE IF FEATURE EXISTS)**
- `test_research_quality.py` - WARNING Not yet in Godot
- `test_office_cat.py` - WARNING Not in Godot
- `test_opponents.py` - WARNING Not in Godot
- `test_achievements_endgame.py` - WARNING Not in Godot
- `test_lab_names.py` - WARNING Not in Godot
- `test_accounting_software.py` - WARNING Not in Godot

**Rationale:** Only migrate tests for features that exist in Godot. Add to TODO for future feature implementation.

---

**6. Infrastructure/Meta Tests (LOW PRIORITY - SOME UNNECESSARY)**
- `test_config_manager.py` - WARNING Godot uses project.godot, not Python config
- `test_settings.py` - Adapt to Godot settings system
- `test_version.py` - Adapt to Godot version tagging
- `test_bug_reporter.py` - WARNING May not need in Godot
- `test_error_tracker.py` - Adapt to Godot's error handling
- `test_game_logging.py` - Godot has built-in logging
- `test_verbose_logging.py` - Godot debugging tools

**Rationale:** Infrastructure changed. Some obsolete, some need Godot equivalents.

---

## Godot Testing Approach

### Option 1: GUT (Godot Unit Testing) Framework ⭐ RECOMMENDED

**Pros:**
- Native Godot integration
- Runs in Godot engine (access to all nodes/signals)
- CLI support for CI/CD
- Familiar unittest-style syntax
- Scene testing support

**Cons:**
- Another dependency to manage
- Learning curve for GUT-specific features

**Installation:**
```bash
# Install GUT via AssetLib or manual download
# https://github.com/bitwes/Gut
```

**Example GUT Test:**
```gdscript
# godot/tests/test_game_state.gd
extends GutTest

func test_game_state_initialization():
    var state = GameState.new("test_seed")
    assert_eq(state.money, 100000.0, "Should start with $100k")
    assert_eq(state.doom, 50.0, "Should start with doom=50")
    assert_eq(state.turn, 0, "Should start at turn 0")

func test_game_state_resource_deduction():
    var state = GameState.new("test_seed")
    state.spend_resources({"money": 10000})
    assert_eq(state.money, 90000.0, "Money should decrease")

func test_can_afford_check():
    var state = GameState.new("test_seed")
    assert_true(state.can_afford({"money": 50000}), "Should afford $50k")
    assert_false(state.can_afford({"money": 200000}), "Should not afford $200k")
```

---

### Option 2: Pure GDScript Tests (No Framework)

**Pros:**
- Zero dependencies
- Simple scripts
- Easy to understand

**Cons:**
- No test runner
- Manual assertion checking
- No CI/CD integration
- No test discovery

**Example:**
```gdscript
# godot/tests/manual_test_game_state.gd
extends Node

func _ready():
    test_game_state_initialization()
    test_resource_deduction()
    print("All tests passed!")

func test_game_state_initialization():
    var state = GameState.new("test_seed")
    assert(state.money == 100000.0, "Money should be $100k")
    assert(state.turn == 0, "Turn should be 0")

func test_resource_deduction():
    var state = GameState.new("test_seed")
    state.spend_resources({"money": 10000})
    assert(state.money == 90000.0, "Money should decrease")
```

---

### Option 3: Hybrid Approach (GUT + Manual)

**Strategy:**
- Use GUT for core game logic tests (game_state, actions, events, turns)
- Use manual testing for UI/visual tests
- Use scene-based tests for integration flows

---

## Recommended Testing Architecture

### Directory Structure:
```
godot/
|--- tests/
|   |--- unit/
|   |   |--- test_game_state.gd          # GameState tests
|   |   |--- test_turn_manager.gd        # TurnManager tests
|   |   |--- test_actions.gd             # GameActions tests
|   |   |--- test_events.gd              # GameEvents tests
|   |   `--- test_deterministic_rng.gd   # RNG tests
|   |--- integration/
|   |   |--- test_full_turn_cycle.gd     # Complete turn flow
|   |   |--- test_event_triggers.gd      # Event system integration
|   |   |--- test_hiring_flow.gd         # Hiring submenu flow
|   |   `--- test_win_lose_conditions.gd # Game over scenarios
|   |--- scenarios/
|   |   |--- test_funding_crisis.gd      # Specific event scenario
|   |   |--- test_paper_publication.gd   # Research  ->  papers flow
|   |   `--- test_staff_salary_cycle.gd  # Economic pressure
|   `--- visual/
|       `--- manual_testing_checklist.md # UI verification steps
`--- scripts/
    `--- core/
        `--- (production code)
```

---

## Priority Migration List

### Phase 1: Core Logic (IMMEDIATE - THIS AFTERNOON!)

**Tests to Migrate:**

1. **test_game_state.gd** - Highest priority
   - Initialization with correct defaults
   - Resource can_afford() checking
   - Resource spend_resources() deduction
   - Resource add_resources() addition
   - Win/lose condition checking
   - Staff counting
   - State serialization (to_dict())

2. **test_deterministic_rng.gd** - Critical for reproducibility
   - Same seed produces same sequence
   - Different seeds produce different sequences
   - RNG state persistence across turns
   - Hash function consistency

3. **test_turn_manager.gd** - Core gameplay loop
   - start_turn() increments turn, sets AP
   - execute_turn() processes queued actions
   - AP scaling with staff (base 3 + 0.5 per employee)
   - Staff salary deduction ($5k per employee)
   - Research generation from compute
   - Paper publication at research >= 100
   - Environmental doom increase
   - Event checking integration

4. **test_actions.gd** - Action system
   - All 15 actions defined correctly
   - Costs specified correctly
   - Effects applied correctly
   - Hiring submenu actions
   - Action execution modifies state as expected

5. **test_events.gd** - Events system
   - Event trigger conditions (random, threshold, turn+resource)
   - Event non-repeatable vs repeatable
   - Event choice costs checked
   - Event choice effects applied
   - Affordability checking
   - triggered_events tracking

---

### Phase 2: Integration Tests (NEXT SESSION)

6. **test_full_turn_cycle.gd**
   - Start turn  ->  select actions  ->  end turn  ->  verify results
   - Multiple turns in sequence
   - Action queueing and execution
   - State updates after each phase

7. **test_event_triggers.gd**
   - Events trigger at correct turns
   - Determinism: same seed = same events
   - Event popup data contains correct options
   - Event resolution applies effects

8. **test_hiring_flow.gd**
   - Hiring action opens submenu
   - Submenu contains 3 options
   - Each option costs correct resources
   - Staff count increases after hiring

---

### Phase 3: Scenario Tests (FUTURE)

9. **test_win_scenarios.gd**
   - Reduce doom to 0  ->  victory
   - High reputation + low doom  ->  victory (if applicable)

10. **test_lose_scenarios.gd**
    - Doom reaches 100  ->  game over
    - Reputation reaches 0  ->  game over

11. **test_economic_pressure.gd**
    - Hire many staff  ->  high salaries  ->  bankruptcy risk
    - Balance hiring vs sustainability

---

## Tests We Can SKIP (Eliminated by Godot Migration)

### UI/Pygame-Specific (35+ tests eliminated):
- All pygame menu/dialog tests
- Mouse wheel handling tests
- UI layout/overlap tests
- Keyboard shortcut UI tests (Godot handles this)
- Modal dialog tests (Godot's built-in dialogs)

### Bug-Specific Tests (15+ tests eliminated):
- Tests for pygame quirks that won't exist in Godot
- Python-specific error handling tests
- UI rendering bugs from pygame

### Infrastructure Tests (10+ tests eliminated):
- Python config manager tests (Godot uses project.godot)
- Python logging tests (Godot has print_debug())
- Python-specific version handling

**Total Eliminated: ~60 tests (60% reduction!)**

---

## Elegant Testing Patterns for Godot

### Pattern 1: Determinism Verification
```gdscript
func test_deterministic_gameplay():
    # Play same scenario twice with same seed
    var results1 = play_scenario("test_seed", 10)  # 10 turns
    var results2 = play_scenario("test_seed", 10)

    assert_eq(results1.final_doom, results2.final_doom)
    assert_eq(results1.final_money, results2.final_money)
    assert_eq(results1.events_triggered, results2.events_triggered)
```

### Pattern 2: Signal Testing
```gdscript
func test_event_triggered_signal():
    var game_manager = GameManager.new()
    game_manager.start_new_game("test_seed")

    # Set up signal watcher
    watch_signals(game_manager)

    # Trigger event conditions
    game_manager.state.money = 40000
    game_manager.state.turn = 10
    game_manager.end_turn()

    # Verify signal emitted
    assert_signal_emitted(game_manager, "event_triggered")
```

### Pattern 3: Scene Testing
```gdscript
func test_welcome_screen_navigation():
    var welcome = preload("res://scenes/welcome.tscn").instantiate()
    add_child(welcome)

    # Simulate key press
    var event = InputEventKey.new()
    event.keycode = KEY_1
    event.pressed = true
    welcome._input(event)

    # Verify scene transition initiated
    assert_true(welcome.is_transitioning)
```

---

## Testing Workflow

### Development Cycle:
1. Write production code in `godot/scripts/`
2. Write GUT test in `godot/tests/unit/`
3. Run tests: `godot --headless --script tests/run_tests.gd`
4. Fix failures, iterate
5. Commit with tests passing

### CI/CD Integration:
```yaml
# .github/workflows/godot-tests.yml
name: Godot Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Godot
        uses: chickensoft-games/setup-godot@v1
      - name: Run GUT Tests
        run: |
          godot --headless --script addons/gut/gut_cmdln.gd \
            -gdir=res://tests/unit/ \
            -gprefix=test_
```

---

## Metrics & Success Criteria

### Coverage Goals:
- **Core Logic:** 90%+ coverage (game_state, turn_manager, actions, events)
- **Integration:** 70%+ coverage (full turn cycles, event flows)
- **UI:** Manual testing checklist (not automated)

### Test Count Target:
- **Unit Tests:** 25-30 tests (down from 98!)
- **Integration Tests:** 10-15 tests
- **Scenario Tests:** 5-10 tests
- **Total:** ~40-55 automated tests

### Quality Bar:
- All tests must pass before merge
- New features require tests
- Determinism tests must verify RNG consistency
- No flaky tests (deterministic environment)

---

## Implementation Plan

### This Afternoon (2-3 hours):

**Step 1:** Install GUT (15 min)
- Download GUT from GitHub
- Add to `godot/addons/gut/`
- Configure test runner

**Step 2:** Write Core Tests (90 min)
- test_game_state.gd (8-10 tests)
- test_deterministic_rng.gd (5-6 tests)
- test_turn_manager.gd (8-10 tests)
- test_actions.gd (6-8 tests)

**Step 3:** Write Events Tests (45 min)
- test_events.gd (10-12 tests)
- Test all 5 event triggers
- Test event choice execution
- Test determinism

**Step 4:** Run & Iterate (30 min)
- Fix any failures
- Verify all tests pass
- Commit test suite

---

## Open Questions

1. **Do we want GUT or pure GDScript tests?**
   - Recommendation: GUT for better tooling

2. **Should we test UI interactions?**
   - Recommendation: Manual testing checklist, not automated

3. **How detailed should integration tests be?**
   - Recommendation: Focus on happy path + critical edge cases

4. **Do we need performance tests?**
   - Recommendation: Not yet, maybe later if performance issues arise

---

## Conclusion

**Testing Strategy Summary:**
- SUCCESS Use GUT framework for unit/integration tests
- SUCCESS Migrate ~40 tests (60% reduction from 98)
- SUCCESS Focus on core game logic (game state, turns, actions, events)
- SUCCESS Manual testing for UI/visual verification
- SUCCESS Eliminate pygame-specific and bug-fix tests
- SUCCESS Emphasize determinism verification
- SUCCESS Target 90%+ coverage for core logic

**This afternoon's goal:** Implement Phase 1 (core logic tests) with GUT framework.

**Expected outcome:** Robust, maintainable test suite that verifies game correctness without excessive test burden.

---

**Status:** Ready to begin implementation
**Next Step:** Install GUT and start writing test_game_state.gd

# Godot Test Suite Comprehensive Plan

**Date**: 2025-10-30
**Purpose**: Complete test coverage for Godot GDScript implementation
**Testing Framework**: GUT (Godot Unit Test)

---

## Executive Summary

### Current State
- **5 test files** with **86 total tests**
- **Good coverage**: GameState, Actions, Events, TurnManager, RNG
- **Critical gaps**: GameManager, integration tests, error handling, turn sequencing (#418)

### Target State
- **10+ test files** with **150+ tests**
- Complete coverage of all core systems
- Integration tests for full gameplay cycles
- Error handling and edge case coverage
- Regression tests for all fixed issues

---

## Current Test Coverage (86 tests)

### 1. test_game_state.gd (23 tests) SUCCESS COMPLETE
- [x] Initialization and defaults
- [x] Resource management (can_afford, spend, add)
- [x] Win/lose conditions
- [x] Staff tracking
- [x] Serialization (to_dict)
- [x] **NEW**: Reputation validation (#407 fix - 6 tests)

### 2. test_actions.gd (15 tests) SUCCESS GOOD
- [x] Action definitions and structure
- [x] Action execution
- [x] Categories and submenu
- [x] Hiring options
- [x] Resource effects
- **Missing**: Error cases, chaining, validation edge cases

### 3. test_events.gd (21 tests) SUCCESS GOOD
- [x] Event structure and definitions
- [x] Trigger conditions
- [x] Repeatability
- [x] Choice execution
- [x] Affordability checks
- [x] Deterministic behavior
- [x] Condition evaluation
- **Missing**: Event chaining, complex conditions, error handling

### 4. test_turn_manager.gd (17 tests) SUCCESS GOOD
- [x] Turn increment
- [x] Action point generation
- [x] Staff salaries
- [x] Research generation
- [x] Paper publication
- [x] Doom progression
- [x] Action processing
- **Missing**: Turn sequencing (#418), event blocking, phase management

### 5. test_deterministic_rng.gd (10 tests) SUCCESS COMPLETE
- [x] Seed reproducibility
- [x] Sequence determinism
- [x] Different RNG methods
- [x] Hash consistency
- [x] Time-based seeds

---

## Critical Missing Tests (Priority 1)

### A. GameManager Tests ERROR **MISSING ENTIRELY**
**File to create**: `godot/tests/unit/test_game_manager.gd`

**Required tests** (estimate: 20 tests):
1. `test_initialization_with_seed`
2. `test_start_new_game_initializes_state`
3. `test_start_new_game_emits_signals`
4. `test_select_action_queues_action`
5. `test_select_action_validates_affordability`
6. `test_select_action_blocks_during_events` (#418)
7. `test_select_action_blocks_wrong_phase` (#418)
8. `test_select_action_emits_error_signal`
9. `test_end_turn_starts_execution`
10. `test_end_turn_blocked_during_events` (#418)
11. `test_start_next_turn_increments_turn`
12. `test_start_next_turn_checks_events_first` (#418)
13. `test_start_next_turn_emits_events_signal` (#418)
14. `test_resolve_event_updates_state`
15. `test_resolve_event_transitions_phase` (#418)
16. `test_resolve_event_enables_action_selection` (#418)
17. `test_signal_emissions_complete_turn_cycle`
18. `test_game_over_detection_doom`
19. `test_game_over_detection_reputation`
20. `test_game_over_detection_victory`

**Why critical**: GameManager is the main coordinator; untested = high risk of integration bugs

---

### B. Turn Sequencing Tests (#418 Fix) ERROR **INCOMPLETE**
**File to enhance**: `godot/tests/unit/test_turn_manager.gd`

**Required new tests** (estimate: 12 tests):
1. `test_turn_phase_starts_at_action_selection`
2. `test_start_turn_with_no_events_allows_actions`
3. `test_start_turn_with_events_blocks_actions`
4. `test_start_turn_sets_pending_events`
5. `test_start_turn_sets_can_end_turn_false_when_events`
6. `test_resolve_event_removes_from_pending`
7. `test_resolve_event_transitions_to_action_selection`
8. `test_resolve_event_sets_can_end_turn_true`
9. `test_resolve_event_blocked_in_wrong_phase`
10. `test_execute_turn_blocked_during_turn_start_phase`
11. `test_multiple_events_all_must_resolve`
12. `test_phase_transitions_complete_cycle`

**Why critical**: Fix #418 is untested; regression risk is high

---

### C. Integration Tests ERROR **MISSING ENTIRELY**
**File to create**: `godot/tests/integration/test_gameplay_flow.gd`

**Required tests** (estimate: 15 tests):
1. `test_complete_turn_cycle_no_events`
2. `test_complete_turn_cycle_with_event`
3. `test_multiple_events_in_sequence`
4. `test_action_effects_persist_across_turns`
5. `test_resource_accumulation_multi_turn`
6. `test_staff_salary_depletion_leads_to_bankruptcy`
7. `test_doom_accumulation_leads_to_loss`
8. `test_reputation_loss_leads_to_loss`
9. `test_doom_reduction_leads_to_victory`
10. `test_paper_publication_multi_turn`
11. `test_hiring_increases_ap_next_turn`
12. `test_research_generation_scales_with_engineers`
13. `test_event_blocks_actions_until_resolved`
14. `test_non_repeatable_event_only_once_in_game`
15. `test_ten_turn_game_simulation`

**Why critical**: Unit tests don't catch integration failures; need end-to-end validation

---

### D. Error Handling Tests ERROR **MISSING**
**Files to enhance**: All test files

**Required tests across files** (estimate: 20 tests):

**test_game_state.gd additions** (5 tests):
1. `test_can_afford_with_malformed_costs_dict`
2. `test_spend_resources_with_negative_values`
3. `test_add_resources_with_invalid_keys`
4. `test_resource_overflow_protection`
5. `test_resource_underflow_protection`

**test_actions.gd additions** (5 tests):
1. `test_execute_action_with_invalid_id`
2. `test_execute_action_with_null_state`
3. `test_get_action_by_id_returns_empty_for_invalid`
4. `test_action_costs_never_negative`
5. `test_action_execution_atomic_on_failure`

**test_events.gd additions** (5 tests):
1. `test_execute_event_choice_with_invalid_choice_id`
2. `test_event_trigger_with_malformed_condition`
3. `test_event_effect_with_invalid_resource`
4. `test_event_non_repeatable_after_trigger`
5. `test_evaluate_condition_with_invalid_syntax`

**test_turn_manager.gd additions** (5 tests):
1. `test_start_turn_with_null_state`
2. `test_execute_turn_with_invalid_action_ids`
3. `test_negative_resource_generation_clamped`
4. `test_doom_overflow_at_max`
5. `test_action_execution_failure_handling`

**Why critical**: Godot games crash on unhandled errors; robust error handling essential

---

### E. Edge Case Tests ERROR **INCOMPLETE**
**Files to enhance**: Multiple

**Required tests** (estimate: 15 tests):

**Resource edge cases** (5 tests):
1. `test_exact_resource_match_affordability`
2. `test_zero_cost_actions_always_affordable`
3. `test_floating_point_resource_precision`
4. `test_very_large_resource_values`
5. `test_resource_costs_with_missing_keys`

**Turn flow edge cases** (5 tests):
1. `test_turn_zero_initial_state`
2. `test_very_long_game_turn_1000`
3. `test_multiple_papers_single_turn`
4. `test_bankruptcy_mid_turn_recovery`
5. `test_simultaneous_win_lose_conditions`

**Staff edge cases** (5 tests):
1. `test_zero_staff_no_research_generation`
2. `test_maximum_staff_count_limits`
3. `test_staff_types_independent`
4. `test_salary_calculation_precision`
5. `test_ap_generation_with_fractional_staff_bonus`

**Why important**: Edge cases cause most production bugs

---

## Secondary Missing Tests (Priority 2)

### F. Action Validation Tests (enhance test_actions.gd)
**Additional tests needed** (10 tests):
1. `test_fundraise_reputation_cost_validation` (related to #407)
2. `test_action_chaining_effects`
3. `test_action_undo_on_insufficient_resources`
4. `test_multiple_resource_type_validation`
5. `test_action_costs_evaluated_before_effects`
6. `test_submenu_action_no_cost`
7. `test_action_effects_commutative`
8. `test_action_message_generation`
9. `test_action_category_filtering`
10. `test_dynamic_action_availability`

### G. Event Complexity Tests (enhance test_events.gd)
**Additional tests needed** (8 tests):
1. `test_event_with_complex_and_conditions`
2. `test_event_with_or_conditions`
3. `test_event_timing_determinism`
4. `test_event_choice_effects_stack`
5. `test_event_minimum_turn_enforcement`
6. `test_event_probability_distribution`
7. `test_event_state_snapshot_on_trigger`
8. `test_event_message_formatting`

### H. Regression Tests (create test_regression.gd)
**Tests for fixed issues** (currently 2, more as issues fixed):
1. `test_issue_418_events_before_actions`
2. `test_issue_407_reputation_validation`
3. *(Add test for each future bug fix)*

---

## Test Organization Strategy

### Directory Structure
```
godot/tests/
|--- unit/                          # Unit tests for individual classes
|   |--- test_game_state.gd        SUCCESS (23 tests)
|   |--- test_actions.gd           SUCCESS (15 tests)  ->  Enhance (+15)
|   |--- test_events.gd            SUCCESS (21 tests)  ->  Enhance (+13)
|   |--- test_turn_manager.gd      SUCCESS (17 tests)  ->  Enhance (+17)
|   |--- test_deterministic_rng.gd SUCCESS (10 tests)
|   |--- test_game_manager.gd      ERROR CREATE (20 tests)
|   `--- test_regression.gd        ERROR CREATE (2+ tests)
|--- integration/                   # Integration tests
|   |--- test_gameplay_flow.gd     ERROR CREATE (15 tests)
|   |--- test_event_integration.gd ERROR CREATE (10 tests)
|   `--- test_multi_turn.gd        ERROR CREATE (12 tests)
|--- edge_cases/                    # Edge case tests
|   |--- test_resource_limits.gd   ERROR CREATE (10 tests)
|   `--- test_boundary_conditions.gd ERROR CREATE (8 tests)
`--- run_tests.gd                   SUCCESS Test runner
```

### Test Naming Convention
```gdscript
# Pattern: test_<system>_<scenario>_<expected_outcome>

# Good:
func test_can_afford_insufficient_money_returns_false()
func test_start_turn_with_events_blocks_actions()
func test_fundraise_without_reputation_fails()

# Bad:
func test_money()
func test_scenario_1()
func test_bug_fix()
```

---

## Implementation Priority

### Phase 1: Critical Gaps (Week 1)
1. SUCCESS **DONE**: Issue #407 tests (reputation validation)
2. **IN PROGRESS**: Issue #418 tests (turn sequencing)
3. **NEXT**: GameManager comprehensive test suite
4. **NEXT**: Basic integration tests

**Goal**: Cover all critical untested systems

### Phase 2: Error Handling (Week 2)
1. Add error handling tests to existing files
2. Create edge case test files
3. Add regression test file

**Goal**: Robust error coverage

### Phase 3: Integration & Advanced (Week 3)
1. Complete integration test suite
2. Multi-turn simulation tests
3. Performance/stress tests (1000 turns)

**Goal**: Full end-to-end confidence

---

## Test Coverage Metrics

### Current Metrics
- **Files with tests**: 5/7 core systems (71%)
- **Total tests**: 86
- **Estimated coverage**: ~60% of critical paths

### Target Metrics
- **Files with tests**: 7/7 core systems (100%)
- **Total tests**: 150+
- **Estimated coverage**: >85% of critical paths
- **Integration tests**: 30+
- **Regression tests**: 1 per fixed issue

---

## Running Tests

### Run All Tests
```gdscript
# Godot Editor  ->  GUT Panel  ->  "Run All"
# OR via command line:
godot --path godot/ --headless --script tests/run_tests.gd
```

### Run Specific Test File
```gdscript
# GUT Panel  ->  Select file  ->  "Run"
```

### Run Specific Test
```gdscript
# GUT Panel  ->  Expand file  ->  Click test name
```

### Continuous Integration
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
        uses: godot/setup-godot@v1
      - name: Run Tests
        run: godot --headless --script tests/run_tests.gd
```

---

## Test Quality Standards

### Every Test Must:
1. SUCCESS Have clear, descriptive name
2. SUCCESS Test ONE specific behavior
3. SUCCESS Include assertion with message
4. SUCCESS Clean up state (use `before_each`/`after_each`)
5. SUCCESS Be deterministic (no random failures)
6. SUCCESS Run in <1 second
7. SUCCESS Document WHY (for complex tests)

### Example Quality Test:
```gdscript
func test_start_turn_with_events_blocks_action_selection():
	# FIX #418: Events must be resolved before actions can be selected
	state.turn = 10
	state.money = 40000  # Triggers funding_crisis event

	var result = turn_manager.start_turn()

	assert_false(result.get("can_select_actions", true),
		"Action selection should be blocked when events are pending")
	assert_eq(state.current_phase, GameState.TurnPhase.TURN_START,
		"Phase should remain TURN_START until events resolved")
	assert_gt(state.pending_events.size(), 0,
		"Pending events should be recorded")
```

---

## Benefits of Comprehensive Testing

### For Development
- **Confidence**: Refactor without fear
- **Speed**: Catch bugs in seconds, not hours
- **Documentation**: Tests show how systems work
- **Design**: Tests reveal design issues early

### For Migration
- **Safety**: Verify Godot matches Python behavior
- **Validation**: Prove fixes work (#407, #418)
- **Regression**: Prevent fixed bugs from returning
- **Progress**: Track migration completeness

### For Users
- **Stability**: Fewer crashes and bugs
- **Quality**: Validated gameplay mechanics
- **Trust**: Professional development practices

---

## Next Steps

1. **Immediate**: Create `test_game_manager.gd` (20 tests)
2. **Next**: Enhance `test_turn_manager.gd` with #418 tests (12 tests)
3. **Then**: Create `test_gameplay_flow.gd` integration tests (15 tests)
4. **After**: Add error handling tests across all files (20 tests)
5. **Finally**: Create regression test file for all fixed issues

**Total new tests planned**: 64+ tests
**Total target**: 150+ tests (current 86 + planned 64+)

---

## Related Documentation

- **Testing Framework**: [GUT Documentation](https://github.com/bitwes/Gut)
- **Current Tests**: [godot/tests/](../godot/tests/)
- **Issue #418 Fix**: [docs/ISSUE_418_FIX_TURN_SEQUENCING.md](ISSUE_418_FIX_TURN_SEQUENCING.md)
- **Issue #407 Fix**: [docs/ISSUE_407_FIX_ACTION_VALIDATION.md](ISSUE_407_FIX_ACTION_VALIDATION.md)
- **Godot Phase 6 Docs**: [docs/GODOT_PHASE_6_DOCS.md](GODOT_PHASE_6_DOCS.md)

---

**Test Suite Plan Created**: 2025-10-30
**Status**: Planning complete, ready for implementation
**Priority**: Create test_game_manager.gd next

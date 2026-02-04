# Sample Bugs for Test Verification

This document contains intentional bugs that can be reintroduced to verify the test suite catches regressions. Useful for:
- Onboarding new developers to the testing workflow
- Verifying CI/CD pipeline catches failures
- Teaching TDD principles

## Bug 1: Missing Risk Pool Clamping

**File:** `scripts/core/risk_pool.gd`
**Test:** `test_add_risk_clamps_to_max`, `test_property_risk_always_in_range`

**How to reintroduce:**
In `add_risk()`, remove the clamping:
```gdscript
# BROKEN - allows values > 100
pools[pool_name] += amount

# CORRECT - clamps to valid range
pools[pool_name] = clampf(pools[pool_name] + amount, 0.0, 100.0)
```

**Expected failure:**
```
[150.0] expected to equal [100.0]: Pool should be clamped to 100
```

---

## Bug 2: Missing Risk Decay

**File:** `scripts/core/risk_pool.gd`
**Test:** `test_risk_decays_each_turn`

**How to reintroduce:**
In `process_turn()`, comment out or remove the decay logic:
```gdscript
# BROKEN - no decay
# for pool_name in pools:
#     pools[pool_name] = maxf(0.0, pools[pool_name] - decay_rate)

# CORRECT - risk decays each turn
for pool_name in pools:
    pools[pool_name] = maxf(0.0, pools[pool_name] - decay_rate)
```

**Expected failure:**
```
[50.0] expected to be < than [50.0]: Pool should decay after turn
```

---

## Bug 3: Serialization Key Mismatch

**File:** `scripts/core/risk_pool.gd`
**Test:** `test_risk_pool_to_dict`

**How to reintroduce:**
Use different key names in `to_dict()`:
```gdscript
# BROKEN - wrong key names
return {
    "pools": pools.duplicate(),
    "triggered_tiers": triggered_tiers.duplicate(),  # Should be "thresholds_triggered"
    "risk_history": risk_history.duplicate()         # Should be "history"
}

# CORRECT - matches test expectations
return {
    "pools": pools.duplicate(),
    "thresholds_triggered": thresholds_triggered.duplicate(),
    "history": history.duplicate()
}
```

**Expected failure:**
```
Expected ["history"] to contain value but got "risk_history"
Expected ["thresholds_triggered"] but got "triggered_tiers"
```

---

## Bug 4: from_dict Not Restoring State

**File:** `scripts/core/game_state.gd`
**Test:** `test_game_state_from_dict_restores_risk`

**How to reintroduce:**
Don't call `risk_system.from_dict()` in `GameState.from_dict()`:
```gdscript
# BROKEN - doesn't restore risk system
if data.has("risk_system"):
    pass  # Forgot to actually restore it

# CORRECT - restores risk system
if risk_system and data.has("risk_system"):
    risk_system.from_dict(data["risk_system"])
```

**Expected failure:**
```
[0.0] expected to equal [70.0]: risk_system should be restored from dict
```

---

## Bug 5: Action Not Contributing Risk

**File:** `scripts/core/actions.gd`
**Test:** `test_train_capabilities_adds_risk`

**How to reintroduce:**
Remove the action from the risk contribution mapping:
```gdscript
# BROKEN - missing from match statement
match action_id:
    "hire_capability_researcher":
        # ...
    # "train_capabilities" case is missing!

# CORRECT - includes train_capabilities
match action_id:
    "hire_capability_researcher":
        # ...
    "train_capabilities":
        state.risk_system.add_risk_multi({
            "capability_overhang": 5.0,
            "research_integrity": 2.0
        }, "train_capabilities", turn)
```

**Expected failure:**
```
[0.0] expected to be > than [0.0]: train_capabilities should increase capability_overhang
```

---

## Running Tests to Verify Bug Detection

```bash
# Run only risk system tests
make test-risk

# Or directly with Godot
godot --headless -s res://addons/gut/gut_cmdln.gd \
  -gtest=res://tests/unit/test_risk_system.gd -glog=1 -gexit
```

## Using These Bugs for Onboarding

1. New developer checks out the codebase
2. Mentor introduces one of these bugs
3. Developer runs tests, sees failure
4. Developer fixes the bug using the test output as guidance
5. Developer runs tests again, sees green
6. Repeat with next bug

This teaches:
- How to run the test suite
- How to read test failure output
- How tests guide implementation
- The red-green-refactor cycle

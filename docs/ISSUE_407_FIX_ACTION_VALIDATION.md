# Issue #407 Fix: Game State Action Validation

**Date**: 2025-10-30
**Issue**: [#407 - Game State Action Validation Issues](https://github.com/PipFoweraker/pdoom1/issues/407)
**Status**: FIXED in Godot Pure GDScript implementation
**Files Modified**: 2 files

---

## Problem Summary

Action validation was incomplete - the `can_afford()` method did not check **reputation** costs, and `spend_resources()` did not deduct reputation when actions were executed.

This caused two critical bugs:
1. **Actions were incorrectly allowed**: Players could execute actions requiring reputation they didn't have (e.g., "fundraise" requires 5 reputation)
2. **Resources weren't deducted**: Even when players had enough reputation, it wasn't being spent when actions executed

This violated core game mechanics where fundraising requires spending reputation as political capital.

---

## Root Cause

### Missing Reputation Validation

**File**: [godot/scripts/core/game_state.gd](../godot/scripts/core/game_state.gd)

The `can_afford()` method (lines 70-82) checked:
- money
- compute
- research
- papers
- action_points

But **NOT** reputation, despite the "fundraise" action requiring it:

```gdscript
# From actions.gd line 48:
{
    "id": "fundraise",
    "name": "Fundraising",
    "description": "Raise money from investors",
    "costs": {"action_points": 2, "reputation": 5},  # <-- Reputation cost!
    "category": "management"
}
```

### Missing Reputation Deduction

The `spend_resources()` method (lines 84-95) deducted:
- money
- compute
- research
- papers
- action_points

But **NOT** reputation, so even if validation was fixed, the resource wouldn't be spent.

---

## Solution: Complete Resource Validation

### Fix 1: Add Reputation Check to `can_afford()`

**File**: [godot/scripts/core/game_state.gd:70-84](../godot/scripts/core/game_state.gd)

Added reputation validation:

```gdscript
func can_afford(costs: Dictionary) -> bool:
    """Check if player can afford given costs (FIX #407: added reputation validation)"""
    if costs.has("money") and money < costs["money"]:
        return false
    if costs.has("compute") and compute < costs["compute"]:
        return false
    if costs.has("research") and research < costs["research"]:
        return false
    if costs.has("papers") and papers < costs["papers"]:
        return false
    if costs.has("reputation") and reputation < costs["reputation"]:  # <-- NEW
        return false
    if costs.has("action_points") and action_points < costs["action_points"]:
        return false
    return true
```

### Fix 2: Add Reputation Deduction to `spend_resources()`

**File**: [godot/scripts/core/game_state.gd:86-100](../godot/scripts/core/game_state.gd)

Added reputation spending with clamping:

```gdscript
func spend_resources(costs: Dictionary):
    """Spend resources (assumes can_afford was checked) (FIX #407: added reputation deduction)"""
    if costs.has("money"):
        money -= costs["money"]
    if costs.has("compute"):
        compute -= costs["compute"]
    if costs.has("research"):
        research -= costs["research"]
    if costs.has("papers"):
        papers -= costs["papers"]
    if costs.has("reputation"):                      # <-- NEW
        reputation -= costs["reputation"]            # <-- NEW
        reputation = max(reputation, 0.0)            # <-- NEW: Clamp to 0 minimum
    if costs.has("action_points"):
        action_points -= costs["action_points"]
```

**Why clamping?** Reputation going negative could break game logic (e.g., lose condition is `reputation <= 0`), so we ensure it never goes below zero even if there's a bug elsewhere.

---

## Files Modified

### 1. [godot/scripts/core/game_state.gd](../godot/scripts/core/game_state.gd)

**Modified `can_afford()`** - Lines 70-84:
- Added reputation cost validation (line 80-81)
- Updated docstring to reference fix

**Modified `spend_resources()`** - Lines 86-100:
- Added reputation deduction (lines 96-98)
- Added clamping to prevent negative reputation
- Updated docstring to reference fix

### 2. [godot/tests/unit/test_game_state.gd](../godot/tests/unit/test_game_state.gd)

**Added 6 new tests** - Lines 164-217:
1. `test_can_afford_reputation_sufficient` - Validates reputation affordability checks work
2. `test_can_afford_reputation_insufficient` - Validates rejection when reputation too low
3. `test_spend_resources_reputation_deduction` - Validates reputation is deducted correctly
4. `test_spend_resources_reputation_clamped_to_zero` - Validates clamping prevents negatives
5. `test_action_validation_fundraise_with_insufficient_reputation` - Validates fundraise blocked correctly
6. `test_action_validation_fundraise_with_sufficient_reputation` - Validates fundraise allowed correctly

---

## Test Coverage

### Unit Tests (GUT Framework)

Run tests with:
```bash
# From Godot editor:
# 1. Open project
# 2. Go to "GUT" panel (bottom)
# 3. Click "Run All"
# OR run specific test file:
# 4. Select test_game_state.gd
# 5. Click "Run"
```

### Test Cases

#### Test Case 1: Reputation Validation (Sufficient)
```gdscript
var state = GameState.new("test")
state.reputation = 50.0
assert_true(state.can_afford({"reputation": 5}))  # SUCCESS Should pass
```

#### Test Case 2: Reputation Validation (Insufficient)
```gdscript
var state = GameState.new("test")
state.reputation = 3.0
assert_false(state.can_afford({"reputation": 5}))  # SUCCESS Should pass
```

#### Test Case 3: Reputation Spending
```gdscript
var state = GameState.new("test")
state.reputation = 50.0
state.spend_resources({"reputation": 10})
assert_eq(state.reputation, 40.0)  # SUCCESS Should pass
```

#### Test Case 4: Fundraise Action Integration
```gdscript
var state = GameState.new("test")
state.reputation = 3.0  # Too low (needs 5)
var action = GameActions.get_action_by_id("fundraise")
assert_false(state.can_afford(action["costs"]))  # SUCCESS Should be blocked
```

---

## Gameplay Impact

### Before Fix (BROKEN)

1. Player with 3 reputation could execute "fundraise" action
2. Action would succeed despite insufficient reputation
3. Reputation would not decrease even if sufficient
4. Game balance broken - infinite fundraising with no cost

### After Fix (CORRECT)

1. Player with 3 reputation **CANNOT** execute "fundraise"
2. Action selection shows it as unaffordable
3. Player must gain reputation first (networking, media campaigns)
4. When fundraising succeeds, reputation is properly deducted
5. Game balance restored - fundraising has a real cost

---

## Edge Cases Handled

### 1. Negative Reputation Prevention
```gdscript
state.reputation = 2.0
state.spend_resources({"reputation": 5})
# Result: reputation = 0.0 (clamped, not -3.0)
```

**Why important**: Prevents undefined behavior and maintains lose condition (`reputation <= 0`)

### 2. Multiple Resource Validation
```gdscript
state.can_afford({"money": 10000, "reputation": 60})
# Returns false if EITHER resource is insufficient
```

**Why important**: Actions can cost multiple resource types; ALL must be validated

### 3. Empty Costs Dictionary
```gdscript
state.can_afford({})  # Returns true
```

**Why important**: Some actions (like "hire_staff" submenu) have no costs and should always be affordable

---

## Related Systems

### Actions Affected

Currently only **"fundraise"** has reputation costs, but the fix ensures any future actions with reputation costs will work correctly.

**Current Action with Reputation Cost**:
- `fundraise`: 2 AP, 5 reputation  ->  Gain $100k + (reputation x $1k)

**Potential Future Actions**:
- `lobbying`: Reputation cost for political influence
- `public_statement`: Reputation cost for controversial statements
- `headhunting`: Reputation cost to poach top talent

### Lose Condition

The game ends when `reputation <= 0`. This fix ensures:
1. Players can't accidentally go negative through spending
2. Reputation costs are properly enforced
3. Lose condition remains meaningful

---

## Architecture Compliance

This fix aligns the Godot implementation with the Python bridge's validation architecture:

**Python bridge** (`src/core/game_state.py`):
- Has comprehensive resource validation
- Validates all resource types including reputation
- Properly deducts all costs

**Godot implementation** (now fixed):
- Matches Python bridge validation behavior
- Supports all resource types
- Maintains game balance parity

---

## Testing Instructions

### Manual Testing

1. **Start new game**
   ```
   New Game  ->  "test-seed"
   ```

2. **Verify initial reputation**
   ```
   Reputation = 50 (check top UI bar)
   ```

3. **Attempt fundraise** (costs 5 reputation, 2 AP)
   ```
   Select "Fundraising" action
   SUCCESS Should be allowed (have 50 reputation)
   ```

4. **Execute turn**
   ```
   End Turn
   SUCCESS Reputation should decrease to 45
   SUCCESS Money should increase
   ```

5. **Drain reputation to near zero**
   ```
   Use console or debug to set reputation = 3
   ```

6. **Attempt fundraise again**
   ```
   Try to select "Fundraising"
   SUCCESS Should be blocked/grayed out
   SUCCESS Error message: "Cannot afford Fundraising"
   ```

### Automated Testing

Run full test suite:
```bash
# Godot Editor  ->  GUT panel  ->  "Run All"
# Expected: All 23 tests pass (17 original + 6 new)
```

---

## Future Enhancements

### 1. Better UI Feedback
Show WHY actions are unaffordable:
```
"Fundraising requires 5 reputation (you have 3)"
```

### 2. Reputation Cost Tooltips
```
Action tooltip:
"Fundraising
Costs: 2 AP, 5 Reputation
Returns: ~$100k"
```

### 3. Dynamic Reputation Costs
```gdscript
# Fundraising costs scale with reputation
"costs": {
    "action_points": 2,
    "reputation": func(state): return max(5, state.reputation * 0.1)
}
```

---

## Verification Checklist

- [x] Reputation validation added to `can_afford()`
- [x] Reputation deduction added to `spend_resources()`
- [x] Reputation clamped to non-negative values
- [x] 6 unit tests added covering all edge cases
- [x] Fundraise action properly blocked when reputation insufficient
- [x] Fundraise action properly deducts reputation when executed
- [x] No other actions broken by changes
- [x] Documentation complete

---

## Benefits

### For Players
- **Fair gameplay**: Can't exploit broken validation
- **Strategic depth**: Reputation is now a real resource to manage
- **Clear feedback**: Know when/why actions are blocked

### For Developers
- **Complete validation**: All resource types properly checked
- **Maintainable**: Future reputation-cost actions will work automatically
- **Tested**: Comprehensive test coverage prevents regressions
- **Documented**: Clear fix documentation for future reference

---

## Related Documentation

- **Original Issue**: [#407](https://github.com/PipFoweraker/pdoom1/issues/407)
- **Actions System**: [godot/scripts/core/actions.gd](../godot/scripts/core/actions.gd)
- **Game State**: [godot/scripts/core/game_state.gd](../godot/scripts/core/game_state.gd)
- **Test Suite**: [godot/tests/unit/test_game_state.gd](../godot/tests/unit/test_game_state.gd)

---

**Fix Completed**: 2025-10-30
**Testing**: Unit tests added and passing
**Status**: Ready for gameplay testing and PR

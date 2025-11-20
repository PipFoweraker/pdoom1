# PDoom Scoring System Proposal

**Date**: November 20, 2024
**Status**: 🟡 Proposal for Review
**Context**: Replacing simple "turns survived" with comprehensive scoring

---

## Current State

**Existing Formula** (game_controller.gd:192):
```gdscript
score = game_state["turn"]  # Just turns survived
```

**Problem**: Simplistic - doesn't reward strategic play, resource management, or safety-focused outcomes.

---

## Proposed Scoring System

### Design Goals

1. **Reward Safety**: Lower doom = higher score (core theme)
2. **Value Research Output**: Papers published demonstrate progress
3. **Recognize Longevity**: Turns survived matters (existing behavior)
4. **Encourage Team Building**: Researchers are valuable
5. **Balanced Resources**: Money/compute matter but don't dominate
6. **Victory Bonus**: Winning (doom < 20%) gets major reward
7. **Strategic Depth**: Multiple viable approaches (safety vs capability vs balanced)

### Scoring Formula v1.0

```gdscript
func calculate_final_score(state: Dictionary) -> int:
	"""
	Calculate final score from game state.

	Components:
	- Safety Achievement: (100 - doom) * 1000    [Max: 100,000]
	- Research Output:    papers * 5000          [~5-10 papers = 25k-50k]
	- Team Excellence:    researchers * 2000     [~5-10 researchers = 10k-20k]
	- Survival Duration:  turn * 500             [50 turns = 25k]
	- Financial Success:  money * 0.1            [125k money = 12.5k]
	- Victory Bonus:      +50000 if doom < 20%   [50k bonus]

	Typical Range: 50k-250k (good game), 300k+ (excellent)
	"""
	var score = 0

	# 1. Safety Achievement (40-50% of total score)
	var safety_score = (100 - state.doom) * 1000
	score += safety_score

	# 2. Research Output (20-30% of total score)
	var paper_score = state.papers * 5000
	score += paper_score

	# 3. Team Excellence (10-15% of total score)
	var team_score = state.researchers * 2000
	score += team_score

	# 4. Survival Duration (10-15% of total score)
	var survival_score = state.turn * 500
	score += survival_score

	# 5. Financial Success (5-10% of total score)
	var financial_score = state.money * 0.1
	score += financial_score

	# 6. Victory Bonus (unlocks at doom < 20%)
	if state.doom < 20.0:
		score += 50000  # Victory bonus

	return int(score)
```

---

## Example Scenarios

### Scenario 1: Safety-Focused Win
```
Turn: 50
Doom: 15% (victory!)
Papers: 8
Researchers: 6
Money: $150,000

Score Breakdown:
- Safety:    (100 - 15) * 1000 = 85,000
- Papers:    8 * 5000           = 40,000
- Team:      6 * 2000           = 12,000
- Survival:  50 * 500           = 25,000
- Financial: 150000 * 0.1       = 15,000
- Victory:   +50,000 bonus      = 50,000
Total: 227,000 points
```

### Scenario 2: Long Survival (No Victory)
```
Turn: 80
Doom: 55% (no victory)
Papers: 12
Researchers: 10
Money: $80,000

Score Breakdown:
- Safety:    (100 - 55) * 1000 = 45,000
- Papers:    12 * 5000          = 60,000
- Team:      10 * 2000          = 20,000
- Survival:  80 * 500           = 40,000
- Financial: 80000 * 0.1        =  8,000
- Victory:   (none)             =      0
Total: 173,000 points
```

### Scenario 3: Early Loss (Typical)
```
Turn: 20
Doom: 100% (defeat)
Papers: 3
Researchers: 4
Money: $50,000

Score Breakdown:
- Safety:    (100 - 100) * 1000 = 0
- Papers:    3 * 5000            = 15,000
- Team:      4 * 2000            =  8,000
- Survival:  20 * 500            = 10,000
- Financial: 50000 * 0.1         =  5,000
- Victory:   (none)              =      0
Total: 38,000 points
```

### Scenario 4: Capability Rush (Risky)
```
Turn: 35
Doom: 75% (risky, no victory)
Papers: 15
Researchers: 8
Money: $200,000

Score Breakdown:
- Safety:    (100 - 75) * 1000 = 25,000
- Papers:    15 * 5000          = 75,000
- Team:      8 * 2000           = 16,000
- Survival:  35 * 500           = 17,500
- Financial: 200000 * 0.1       = 20,000
- Victory:   (none)             =      0
Total: 153,500 points
```

---

## Score Distribution Analysis

### Expected Ranges

| Performance | Score Range | Description |
|-------------|-------------|-------------|
| Beginner | 10k - 50k | Early defeat, minimal progress |
| Competent | 50k - 100k | Mid-game survival, some safety work |
| Strong | 100k - 150k | Long survival or focused safety |
| Excellent | 150k - 200k | Well-balanced or strong specialization |
| Victory | 200k - 300k | Won game with good metrics |
| Optimal | 300k+ | Perfect safety victory with max research |

### Component Weight Distribution

- **Safety** (doom): ~40-50% of score (core theme)
- **Research** (papers): ~20-30% (demonstrates progress)
- **Team** (researchers): ~10-15% (strategy depth)
- **Survival** (turns): ~10-15% (time investment)
- **Financial** (money): ~5-10% (resource management)
- **Victory Bonus**: +50k (rewards winning)

---

## Strategic Implications

### Viable Strategies

**1. Safety-First Victory**
- Focus on safety researchers
- Minimize doom at all costs
- Aim for victory bonus
- **Expected Score**: 200k-280k

**2. Research Output**
- Maximize paper publication
- Balance doom to survive
- Long-term survival
- **Expected Score**: 150k-200k

**3. Balanced Approach**
- Moderate everything
- Adapt to events
- Avoid extremes
- **Expected Score**: 120k-180k

**4. Capability Rush** (Risky)
- High doom, high papers
- Race against time
- High risk/reward
- **Expected Score**: 80k-160k (if survive)

All strategies can achieve competitive scores, supporting diverse playstyles.

---

## Comparison to Current System

### Current (Turns Only)
```
Typical Win:  50 turns → 50 points
Long Game:    80 turns → 80 points
Early Loss:   20 turns → 20 points

Problems:
- No reward for safety focus
- Ignores resource management
- Doesn't distinguish victory from near-loss
- No incentive for research output
```

### Proposed (Comprehensive)
```
Typical Win:  227,000 points (safety-focused)
Long Game:    173,000 points (balanced survival)
Early Loss:    38,000 points (minimal progress)

Benefits:
✅ Rewards core safety theme
✅ Values research output
✅ Distinguishes quality of wins
✅ Multiple viable strategies
✅ Strategic depth
```

---

## Implementation Checklist

### Client-Side (Godot)

- [ ] Add `calculate_final_score()` function to GameState or GameManager
- [ ] Update score calculation in game_over flow
- [ ] Test formula with known game states
- [ ] Verify score ranges are reasonable
- [ ] Update leaderboard display (show score, not just turns)

**File to Modify**: `godot/scripts/game_controller.gd` or `godot/scripts/core/game_state.gd`

```gdscript
func calculate_final_score() -> int:
	"""Calculate final score from current game state."""
	var score = 0

	# Safety Achievement
	score += (100 - doom) * 1000

	# Research Output
	score += papers * 5000

	# Team Excellence
	score += researchers.size() * 2000

	# Survival Duration
	score += turn * 500

	# Financial Success
	score += money * 0.1

	# Victory Bonus
	if doom < 20.0:
		score += 50000

	return int(score)
```

### Server-Side (Python)

- [ ] Update `ScoreCalculator.calculate_score()` in `verification_logic.py`
- [ ] **CRITICAL**: Ensure formula matches Godot exactly
- [ ] Test with same game states as client
- [ ] Verify score differences are within tolerance (100 points)

**File to Modify**: `pdoom1-website/scripts/verification_logic.py`

```python
@staticmethod
def calculate_score(final_state: Dict[str, Any]) -> int:
    """
    CRITICAL: Must match godot/scripts/core/game_state.gd exactly!
    """
    doom = final_state.get('doom', 0)
    papers = final_state.get('papers', 0)
    researchers = final_state.get('researchers', 0)
    turn = final_state.get('turn', 0)
    money = final_state.get('money', 0)

    score = 0

    # Safety Achievement
    score += (100 - doom) * 1000

    # Research Output
    score += papers * 5000

    # Team Excellence
    score += researchers * 2000

    # Survival Duration
    score += turn * 500

    # Financial Success
    score += money * 0.1

    # Victory Bonus
    if doom < 20.0:
        score += 50000

    return int(score)
```

---

## Testing Plan

### Unit Tests

```gdscript
# Test known scenarios
func test_scoring_system():
	# Scenario 1: Safety-focused win
	var state1 = {
		"turn": 50, "doom": 15.0, "papers": 8,
		"researchers": 6, "money": 150000
	}
	assert(calculate_final_score(state1) == 227000)

	# Scenario 2: Long survival
	var state2 = {
		"turn": 80, "doom": 55.0, "papers": 12,
		"researchers": 10, "money": 80000
	}
	assert(calculate_final_score(state2) == 173000)

	# Scenario 3: Early loss
	var state3 = {
		"turn": 20, "doom": 100.0, "papers": 3,
		"researchers": 4, "money": 50000
	}
	assert(calculate_final_score(state3) == 38000)
```

### Cross-Platform Validation

```python
# Python unit test (server-side)
def test_score_calculation():
    # Same scenarios as Godot
    state1 = {
        "turn": 50, "doom": 15.0, "papers": 8,
        "researchers": 6, "money": 150000
    }
    assert calculate_score(state1) == 227000

    # Verify within tolerance
    godot_score = 227000
    python_score = calculate_score(state1)
    assert abs(godot_score - python_score) <= 100
```

---

## Balancing Considerations

### Potential Adjustments (Post-Launch)

If community feedback suggests:

**"Safety too dominant"**: Reduce doom multiplier (1000 → 800)
**"Papers undervalued"**: Increase paper multiplier (5000 → 6000)
**"Victory bonus too high"**: Reduce bonus (50000 → 30000)
**"Money irrelevant"**: Increase money multiplier (0.1 → 0.5)

### Monitoring Metrics

Track post-launch:
- Average score by strategy type
- Correlation: doom vs final score
- Victory rate at different score tiers
- Community sentiment (forums/Discord)

---

## Alternative Formulas (For Discussion)

### Option A: Simpler (Fewer Components)
```
score = (100 - doom) * 1000 + papers * 5000 + turn * 500
```
**Pros**: Easier to understand, fewer variables
**Cons**: Less strategic depth, ignores team/money

### Option B: Non-Linear (Exponential Safety)
```
score = pow(100 - doom, 1.5) * 100 + papers * 5000 + ...
```
**Pros**: Heavily rewards low doom (thematic)
**Cons**: May discourage risky strategies, harder to balance

### Option C: Weighted by Turn (Later = More Valuable)
```
score = (100 - doom) * turn * 20 + papers * turn * 100 + ...
```
**Pros**: Rewards sustained excellence
**Cons**: May overly favor long games

---

## Recommendation

**Use Proposed Formula v1.0** for initial launch because:

1. ✅ Balanced weight distribution (40% safety, 20% research, etc.)
2. ✅ Multiple viable strategies (safety, research, balanced, risky)
3. ✅ Clear component breakdown (easy to understand)
4. ✅ Reasonable score ranges (50k-300k)
5. ✅ Maintains existing "turns survived" importance
6. ✅ Easy to tune post-launch (adjust multipliers)

**Then**: Monitor community feedback and adjust multipliers in v1.1 if needed.

---

## Open Questions for Review

1. **Victory threshold**: Is 20% doom the right cutoff? (Consider: 15%, 25%, or dynamic)
2. **Victory bonus**: 50k points fair? (Consider: 30k-70k range)
3. **Money weight**: Too low at 0.1x? (Consider: 0.2x or 0.5x)
4. **Reputation**: Should it count? (Currently excluded, could add: `reputation * 100`)
5. **Compute**: Should it count? (Currently excluded, could add: `compute * 50`)
6. **Defeat types**: Should doom=100 defeat score differently than bankruptcy?

---

## References

- Current implementation: `godot/scripts/game_controller.gd:178-211`
- Game state definition: `godot/scripts/core/game_state.gd`
- Verification docs: `pdoom1/docs/VERIFICATION_INTEGRATION_COMPLETE.md`
- Server validation: `pdoom1-website/scripts/verification_logic.py`

---

**Status**: 🟡 Awaiting review and feedback
**Next Step**: Implement in Godot after approval
**Timeline**: Can deploy with Week 3 testing phase

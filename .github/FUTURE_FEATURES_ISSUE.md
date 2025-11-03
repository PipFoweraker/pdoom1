# Future Features: Research Quality, Technical Debt, Upgrades

**Priority**: Medium
**Category**: Game Mechanics Expansion
**Dependencies**: Doom Momentum System ✅, Researcher Specializations ✅

---

## Overview

Three interconnected systems from the Python prototype ready to port to Godot:

1. **Research Quality System** - Rushed/Standard/Thorough research choices
2. **Technical Debt** - Accumulates from rushed research, affects doom
3. **Upgrades System** - 7 purchasable upgrades with significant effects

All three work together to create mid-late game strategic depth.

---

## 1. Research Quality System

### Complexity
Low (1-2 hours)

### Features
Three quality levels for research actions:

**Rushed**:
- **Speed**: 2x research generation
- **Cost**: Accumulates technical debt (+2 per turn)
- **Doom**: +1 doom per turn
- **Use Case**: Desperate situations, final push

**Standard**:
- **Speed**: 1x research generation (baseline)
- **Cost**: No debt
- **Doom**: Baseline doom
- **Use Case**: Normal gameplay

**Thorough**:
- **Speed**: 0.5x research generation
- **Cost**: No debt
- **Doom**: -1 doom per turn (safer!)
- **Use Case**: Safety-focused builds, early game

### Implementation
```gdscript
# In actions.gd:
const RESEARCH_QUALITY = {
    "rushed": {
        "research_multiplier": 2.0,
        "debt_per_turn": 2,
        "doom_modifier": 1.0
    },
    "standard": {
        "research_multiplier": 1.0,
        "debt_per_turn": 0,
        "doom_modifier": 0.0
    },
    "thorough": {
        "research_multiplier": 0.5,
        "debt_per_turn": 0,
        "doom_modifier": -1.0
    }
}
```

### UI
- Radio buttons / dropdown on research actions
- Shows trade-offs clearly
- Default: Standard

---

## 2. Technical Debt System

### Complexity
Medium (2-3 hours)

### Features

**4 Debt Categories**:
1. **Validation** - Insufficient testing
2. **Architecture** - Shortcuts in design
3. **Documentation** - Poor code comments
4. **Performance** - Unoptimized code

**Effects**:
- **Research Speed**: -5% per debt point
- **Opponent Doom**: +5% per debt point (rivals benefit from your mess!)
- **Accident Chance**: Increases cascade event probability

**Accumulation**:
- Rushed research: +2 debt per turn
- Random events: +1-3 debt
- Capability research: +0.5 debt per researcher

**Reduction Actions** (4+):
1. **Code Review** ($30k, 1 AP): -3 validation debt
2. **Refactoring Sprint** ($50k, 2 AP): -5 architecture debt
3. **Documentation Drive** ($20k, 1 AP): -3 documentation debt
4. **Performance Optimization** ($40k, 2 AP): -4 performance debt

### Implementation
```gdscript
# In game_state.gd:
var technical_debt: Dictionary = {
    "validation": 0,
    "architecture": 0,
    "documentation": 0,
    "performance": 0
}

func get_total_debt() -> int:
    var total = 0
    for category in technical_debt.values():
        total += category
    return total

# In doom_system.gd:
func apply_technical_debt_effects(debt: int):
    var debt_multiplier = 1.0 + (debt * 0.05)
    set_doom_multiplier("rivals", debt_multiplier)
    doom_sources["technical_debt"] = debt * 0.2
```

### UI Needed
- Debt tracker in main UI
- Breakdown by category
- Warning at 10+ total debt

---

## 3. Upgrades System

### Complexity
Low-Medium (2-3 hours)

### 7 Upgrades

#### Computer System ($200k)
- **Effect**: +1 research per action
- **Unlock**: Turn 1
- **Value**: Early research boost

#### Comfy Chairs ($120k)
- **Effect**: -25% burnout accumulation (all researchers)
- **Unlock**: 3+ researchers
- **Value**: Long-term productivity

#### Secure Cloud ($160k) ⭐
- **Effect**: Reduces doom event spikes by 70% (6-13 → 1-2)
- **Unlock**: 5+ researchers
- **Value**: Critical for event mitigation

#### Accounting Software ($500k)
- **Effect**: Unlock advanced financial tracking
- **Unlock**: Turn 5
- **Value**: QoL improvement

#### Compact Display ($150k)
- **Effect**: UI optimization (show more info)
- **Unlock**: Turn 1
- **Value**: UX enhancement

#### HPC Cluster ($800k) ⭐
- **Effect**: +20 compute, +25% research speed
- **Unlock**: 10+ researchers
- **Value**: Late-game power spike

#### Automation Suite ($600k)
- **Effect**: Compute efficiency +30%
- **Unlock**: 5+ compute engineers
- **Value**: Scales with compute

### Implementation
```gdscript
# In game_state.gd:
var upgrades: Array[String] = []

func has_upgrade(upgrade_id: String) -> bool:
    return upgrade_id in upgrades

func purchase_upgrade(upgrade_id: String):
    if not has_upgrade(upgrade_id):
        upgrades.append(upgrade_id)

# In turn_manager.gd:
if state.has_upgrade("comfy_chairs"):
    burnout_rate *= 0.75  # 25% reduction

if state.has_upgrade("hpc_cluster"):
    research_generated *= 1.25  # 25% boost
    state.add_resources({"compute": 20})
```

### UI Needed
- Upgrades menu/dialog
- Show costs and unlock conditions
- Purchased upgrades visible in main UI

---

## Integration Notes

### Research Quality + Technical Debt
```
Player selects "Rushed" research:
1. Research generation: 2x
2. Doom modifier: +1/turn
3. Technical debt: +2/turn

After 5 turns of rushed research:
- Total debt: 10
- Opponent doom multiplier: 1.5x (50% worse!)
- Must use debt reduction actions
```

### Technical Debt + Upgrades
```
Player purchases "HPC Cluster":
- +20 compute (immediate)
- +25% research (ongoing)
- Can offset debt penalties with raw power
```

### All Three Together
```
Strategy: "Speed Run with Recovery"

Turns 1-5: Rushed research (build debt)
- Accumulate 10 debt
- Generate 2x research
- Accept higher doom

Turn 6-7: Purchase upgrades + reduce debt
- Buy Secure Cloud (reduce event spikes)
- Code Review actions (reduce debt)

Turns 8-12: Thorough research (clean finish)
- Slower but safer
- Debt under control
- Secure path to victory
```

---

## Prioritization

### Must-Have (v1.0)
1. **Research Quality** - Simple, high impact
2. **Technical Debt** - Core system for risk/reward

### Nice-to-Have (v1.1)
3. **Upgrades System** - Polish and power spikes

### Reasoning
- Research Quality is trivial to implement
- Technical Debt creates interesting trade-offs
- Upgrades are polish (can wait for UI polish pass)

---

## Testing Requirements

### Unit Tests Needed
- Research quality modifiers
- Technical debt accumulation
- Technical debt effects on doom
- Upgrade purchase and effects
- Integration: rushed research → debt → doom

### Balance Testing
- Is rushed research worth it?
- Can players recover from high debt?
- Are upgrades meaningful choices?

---

## Documentation Needed

1. **Research Quality Guide**
   - When to use each quality level
   - Trade-off analysis

2. **Technical Debt Guide**
   - How debt accumulates
   - When to prioritize reduction
   - Debt reduction strategies

3. **Upgrades Guide**
   - Purchase order recommendations
   - Unlock conditions
   - ROI analysis

---

## Estimated Effort

- **Research Quality**: 1-2 hours
- **Technical Debt**: 2-3 hours
- **Upgrades**: 2-3 hours
- **Testing**: 2 hours
- **Documentation**: 2 hours

**Total**: 9-12 hours (1-2 sessions)

---

## Success Metrics

✅ **Research Quality**:
- Players use all three quality levels
- Strategic choices (not always one dominant)

✅ **Technical Debt**:
- Debt accumulation creates tension
- Reduction actions feel meaningful
- Doom penalty noticeable but not overwhelming

✅ **Upgrades**:
- Players purchase 3-5 upgrades per game
- Choices feel impactful
- Unlock conditions make sense

---

## Notes

- All three systems have proven balance from Python prototype
- Clean extension points exist in doom system
- Can implement incrementally (Research Quality → Debt → Upgrades)
- UI can be basic initially (text-based dialogs)

---

## Related Issues

- #426 Godot Phase 5 (completed - this is follow-up)
- #424 Unmanaged Employee Productivity (partially addressed)
- #416 Technical Debt Visualization (part of this)

---

## Next Steps

1. Create this as GitHub issue
2. Implement Research Quality (quick win)
3. Build Technical Debt system
4. Add Upgrades when UI is ready

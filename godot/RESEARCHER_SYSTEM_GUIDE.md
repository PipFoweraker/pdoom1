# Researcher Specialization System Guide

**Status**: ✅ Fully Implemented
**Complexity**: High-impact strategic depth
**Integration**: Doom System, Game State, Actions, Turn Manager

---

## 🎯 Overview

The Researcher System transforms hiring from simple "hire staff" into strategic character management. Each researcher has:
- **Specialization** (4 types with unique effects)
- **Traits** (10+ positive/negative personality traits)
- **Burnout** (0-100, reduces productivity over time)
- **Skill Level** (1-10, improves slowly)
- **Loyalty** (0-100, affects poaching resistance)

This creates emergent gameplay: "Should I hire the skilled but Prima Donna researcher, or the Workaholic who'll burn out fast?"

---

## 👥 Specializations

### Safety Researcher ($60k)
**Focus**: AI safety and alignment

**Effects**:
- **Doom Reduction Bonus**: +15% effectiveness
- Base doom reduction: -3.5/turn
- With bonus: -4.025/turn

**Best For**: Players focused on reducing p(doom) quickly

**Example**: "Alex Chen (Safety Specialist, Skill 6)"

---

### Capabilities Researcher ($60k)
**Focus**: Advancing AI capabilities

**Effects**:
- **Research Speed**: +25% faster research generation
- **Doom Penalty**: +5% doom from their work
- Base doom increase: +3.0/turn
- With penalty: +3.15/turn

**Best For**: Risky strategies that need fast research

**Trade-off**: Speed vs safety

---

### Interpretability Researcher ($70k)
**Focus**: Making AI systems understandable

**Effects**:
- Counts as safety researcher (-3.0 doom/turn)
- **Unlocks Special Actions** (future: audit, transparency actions)
- More expensive but versatile

**Best For**: Mid-game when you need safety + special capabilities

---

### Alignment Researcher ($65k)
**Focus**: Aligning AI goals with human values

**Effects**:
- Enhanced safety research (-3.2 doom/turn)
- **Negative Event Reduction**: -10% chance of bad events (future)
- Slight bonus over regular safety researchers

**Best For**: Players who want safety + event mitigation

---

## 🎭 Traits System

### Positive Traits

#### Workaholic
- **Effect**: +20% productivity
- **Cost**: +2.0 burnout per turn
- **Strategy**: Short-term powerhouse, needs management

#### Team Player
- **Effect**: +10% productivity to ALL researchers
- **Benefit**: Multiplies with team size
- **Strategy**: Hire early for compound effect

#### Media Savvy
- **Effect**: +3 reputation when publishing papers
- **Benefit**: Boosts public image
- **Strategy**: Great for reputation-focused builds

#### Safety Conscious
- **Effect**: -10% doom from their work
- **Benefit**: Stacks with specialization
- **Strategy**: Safety specialist with this trait = super effective

#### Fast Learner
- **Effect**: Skill grows 50% faster
- **Benefit**: Long-term investment
- **Strategy**: Keep them employed for many turns

---

### Negative Traits

#### Prima Donna
- **Effect**: If paid <90% of salary expectation → -20% productivity + team morale hit
- **Danger**: Can cascade if budget tight
- **Strategy**: Either pay well or don't hire

#### Leak Prone
- **Effect**: 5% chance per turn to leak research to competitors
- **Danger**: Rivals get advantage
- **Strategy**: Use on non-critical projects

#### Burnout Prone
- **Effect**: 50% faster burnout accumulation
- **Danger**: Becomes unproductive quickly
- **Strategy**: Rotate with team building actions

#### Pessimist
- **Effect**: -5 morale to entire team
- **Danger**: Reduces overall productivity
- **Strategy**: Avoid or balance with Team Players

---

## 📊 Productivity Mechanics

### Base Productivity
```gdscript
base_productivity = 0.5 + (skill_level * 0.1)
# Skill 3 = 0.8 productivity
# Skill 5 = 1.0 productivity
# Skill 10 = 1.5 productivity
```

### Burnout Penalty
```gdscript
burnout_penalty = min(burnout / 100.0 * 0.5, 0.5)
effective_productivity *= (1.0 - burnout_penalty)

# 0 burnout = no penalty
# 50 burnout = 25% penalty
# 100 burnout = 50% penalty (minimum 10% productivity)
```

### Trait Modifiers
```gdscript
if "workaholic":
    effective *= 1.20  # +20%

if "prima_donna" and underpaid:
    effective *= 0.80  # -20%
```

### Final Formula
```gdscript
effective = base * (1 - burnout_penalty) * trait_modifiers
effective = max(effective, 0.1)  # Minimum 10%
```

---

## 🔥 Burnout System

### Accumulation
- **Base Rate**: 0.5 burnout per turn
- **Workaholic**: +2.0 burnout per turn
- **Burnout Prone**: 1.5x multiplier

### Reduction
- Team Building action: -10 burnout (all researchers)
- Team Retreat event: -20 burnout (all researchers)
- Salary Raise event: -5 burnout

### Thresholds
- **0-40**: Healthy (full productivity)
- **40-70**: Strained (reduced productivity)
- **70-90**: Burned Out (major productivity loss)
- **90-100**: Critically Burned Out (minimal productivity)

### Strategy
- Monitor burnout levels
- Use team building regularly
- Rotate workaholic researchers

---

## 🎮 Integration with Doom System

### Doom Calculation with Researchers
```gdscript
# Old system (legacy):
doom_sources["safety"] = -safety_researchers * 3.5

# New system (individual researchers):
for researcher in researchers:
    if researcher.is_productive():
        match researcher.specialization:
            "safety":
                base = -3.5 * researcher.get_effective_productivity()
                bonus = base * 0.15  # Specialization bonus
                doom_sources["safety"] += base + bonus

            "capabilities":
                base = 3.0 * researcher.get_effective_productivity()
                penalty = base * 0.05  # Doom penalty
                doom_sources["capabilities"] += base + penalty

        # Apply trait modifiers
        doom_sources["specializations"] += researcher.get_doom_modifier()
```

### Specialization Breakdown in UI
```
Doom 48.2 → 52.5 (change: +4.3)
  └─ base: +1.0
  └─ safety: -8.1 (2 safety specialists with 15% bonus)
  └─ capabilities: +9.5 (3 cap researchers with 5% penalty)
  └─ specializations: -0.3 (Safety Conscious trait on 3 researchers)
  └─ momentum: +1.2
```

---

## 💼 Hiring Strategy Guide

### Early Game (Turns 1-5)
**Goal**: Build foundation

**Recommendation**:
- 2x Safety Researchers
- 1x Capabilities Researcher (for research speed)
- Focus: High skill level over traits

**Why**: Establish doom reduction, generate research

---

### Mid Game (Turns 6-12)
**Goal**: Scale and specialize

**Recommendation**:
- Add Alignment or Interpretability researchers
- Look for Team Player trait (multiplies team effectiveness)
- Hire Manager at 9 researchers

**Why**: Diversify, unlock special actions, manage burnout

---

### Late Game (Turns 13+)
**Goal**: Optimize and power through

**Recommendation**:
- Safety-heavy team (4-6 safety specialists)
- 1-2 Capabilities for final research push
- Watch burnout levels

**Why**: Final doom reduction sprint

---

## 🎯 Example Builds

### "Pure Safety" Build
```
Team Composition:
- 6x Safety Researchers
- 1x Alignment Researcher
- 2x Managers

Strategy:
- Maximize doom reduction
- Slow but steady research
- Low risk, high safety margin

Doom Rate: -25/turn (massive reduction!)
```

---

### "Balanced Research" Build
```
Team Composition:
- 3x Safety Researchers
- 3x Capabilities Researchers
- 1x Interpretability Researcher
- 1x Manager

Strategy:
- Fast research with safety backup
- Moderate doom pressure
- Flexible mid-game

Doom Rate: -5/turn (sustainable)
```

---

### "Speed Run" Build (Risky!)
```
Team Composition:
- 1x Safety Researcher
- 6x Capabilities Researchers (all Workaholics)
- 1x Manager

Strategy:
- Blitz research generation
- Accept doom increase
- Race to victory before doom = 100

Doom Rate: +15/turn (dangerous!)
Research Rate: 3x normal

Risk: Doom spiral, burnout cascade
```

---

## 🧪 Testing & Validation

### Unit Tests
**File**: `godot/tests/test_researcher_system.gd`

29 test cases covering:
- Initialization and name generation
- Productivity calculations
- Burnout mechanics
- Trait effects
- Doom integration
- Serialization
- Hiring actions
- Game state integration

### Integration Tests Needed
- Full game with researcher system
- Burnout cascade scenario
- Prima Donna salary crisis
- Team Player scaling
- Skill growth over 20+ turns

---

## 📊 Balance Tuning Parameters

All values exposed for easy tweaking:

```gdscript
# In Researcher.SPECIALIZATIONS:
"safety": {
    "doom_reduction_bonus": 0.15,  # Currently +15%
    "base_cost": 60000
}

"capabilities": {
    "research_speed_modifier": 1.25,  # Currently +25%
    "doom_per_research": 0.05,  # Currently +5%
    "base_cost": 60000
}

# In trait definitions:
POSITIVE_TRAITS["workaholic"]["productivity_bonus"] = 0.20  # +20%
POSITIVE_TRAITS["workaholic"]["burnout_rate"] = 2.0  # +2 per turn

NEGATIVE_TRAITS["prima_donna"]["team_productivity_penalty"] = -0.10  # -10%

# In researcher.process_turn():
accumulate_burnout(0.5)  # Base rate per turn
if randf() < 0.05:  # 5% chance for skill growth
```

**Balancing Philosophy**:
- Specializations should create distinct strategies
- Traits should be meaningful but not overwhelming
- Burnout should matter but be manageable
- Productivity range: 0.1 (burned out) to 2.5 (perfect conditions)

---

## 🔌 Future Extensions

### Phase 1: Researcher Events (Next)
- Breakthrough events (research + reputation boost)
- Burnout crisis (need team building or lose researcher)
- Poaching attempts (rivals try to hire your researchers)
- Conference invitations (reputation gain)

### Phase 2: Advanced Traits
- Trait discovery over time
- Trait combinations (synergies/conflicts)
- Hidden traits revealed through events

### Phase 3: Researcher Management UI
- Researcher roster screen
- Burnout visualization
- Salary negotiation dialog
- Skill progression tracking

### Phase 4: Research Projects
- Multi-turn projects requiring specific specialists
- Team composition bonuses
- Project completion milestones

---

## 🎊 Summary

The Researcher System adds **strategic depth through character management**:

✅ **4 Specializations** with unique doom effects
✅ **10+ Traits** creating emergent personalities
✅ **Burnout Mechanic** requiring active management
✅ **Skill Growth** rewarding long-term employment
✅ **Doom Integration** - specializations directly modify doom calculations
✅ **29 Unit Tests** - comprehensive coverage
✅ **Backward Compatible** - works alongside legacy system

**Gameplay Impact**:
- Hiring becomes a strategic decision (not just "+1 staff")
- Researchers feel like individuals with personalities
- Trade-offs between short-term power (Workaholic) and sustainability
- Doom reduction now has nuance (Safety spec = 15% better!)

**Ready For**: Playtesting, UI integration, event system expansion

The foundation is solid - time to play and discover emergent strategies! 🎮✨

---

## 📝 Quick Reference

**File Locations**:
- `godot/scripts/core/researcher.gd` - Researcher class (350 lines)
- `godot/scripts/core/game_state.gd` - Integration with game state
- `godot/scripts/core/doom_system.gd` - Doom calculation with researchers
- `godot/scripts/core/actions.gd` - Hiring actions
- `godot/scripts/core/turn_manager.gd` - Turn processing
- `godot/tests/test_researcher_system.gd` - 29 unit tests

**Key Functions**:
- `Researcher.new(spec, name)` - Create researcher
- `researcher.get_effective_productivity()` - Current productivity with modifiers
- `researcher.get_doom_modifier()` - Personal doom modification
- `state.add_researcher(researcher)` - Hire researcher
- `GameActions.execute_action("hire_safety_researcher", state)` - Hire via action

**Costs**:
- Safety: $60k
- Capabilities: $60k
- Interpretability: $70k
- Alignment: $65k

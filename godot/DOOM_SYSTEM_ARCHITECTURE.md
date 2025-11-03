# Doom System Architecture

**Design Philosophy**: Path of Exile Approach - Start Simple, Add Layers

---

## 🎯 Overview

The Doom System is a **modular, extensible architecture** for calculating and managing p(doom) - the probability of AI-caused extinction. It's designed to start with simple mechanics (Phase 1) and progressively add complexity over time without breaking existing functionality.

## 📐 Architecture Layers

### Layer 1: Doom Momentum (✅ IMPLEMENTED)
**Status**: Complete
**Complexity**: Simple (5% added complexity)

Core mechanics:
- **Doom Velocity**: Smoothed rate of doom change
- **Doom Momentum**: Accumulated momentum that compounds over time
- **Momentum Decay**: Prevents permanent momentum (8% decay/turn)
- **Momentum Cap**: Prevents infinite spirals (±8.0 max)

**Formula**:
```gdscript
# Each turn:
raw_change = base + capabilities + safety + rivals + unproductive
momentum += raw_change * 0.15  # 15% accumulates
momentum *= 0.92  # 8% decay
momentum = clamp(momentum, -8.0, 8.0)  # Cap

total_change = raw_change + momentum
```

**Gameplay Effect**:
- Risky play → Doom spiral (positive momentum)
- Safety focus → Safety flywheel (negative momentum)
- Creates emergent narratives ("I'm in a doom spiral!")
- Recovery is possible but harder once momentum builds

---

### Layer 2: Source Tracking (✅ IMPLEMENTED)
**Status**: Complete
**Complexity**: Trivial (bookkeeping only)

Tracks where doom comes from:
- `base`: +1.0 organizational risk
- `capabilities`: +3.0 per capability researcher
- `safety`: -3.5 per safety researcher (if productive)
- `rivals`: Varies by rival actions (-10 to +20)
- `unproductive`: +0.5 per unproductive employee
- `events`: One-time doom spikes
- `momentum`: Compounded momentum
- **Future**: technical_debt, specializations, cascades, market_pressure

**UI Benefit**:
```
Doom 48.2 → 52.5 (change: +4.3)
  └─ base: +1.0, capabilities: +6.0, safety: -7.0,
     rivals: +3.2, momentum: +1.1
  └─ Momentum: doom spiral (1.1)
```

Players understand exactly why doom is changing.

---

### Layer 3: Multipliers & Modifiers (🔄 PARTIAL - Extension Point Ready)
**Status**: Architecture ready, awaiting content
**Complexity**: Medium (15% added complexity)

**Multipliers** (multiply doom sources):
```gdscript
# Example usage:
doom_system.set_doom_multiplier("rivals", 0.7)  # Intelligence reduces rival doom 30%
doom_system.set_doom_multiplier("events", 1.5)  # Market panic increases event doom 50%
```

**Modifiers** (add/subtract from sources):
```gdscript
# Example usage:
doom_system.apply_doom_modifier("capabilities", -0.5)  # Safety Conscious trait
doom_system.apply_doom_modifier("safety", 1.0)         # Specialization bonus
```

**Planned Content** (Phase 3):
- Researcher specializations modify doom
- Technical debt increases opponent doom (5% per debt point)
- Market cycles affect doom rates
- Upgrades provide doom bonuses (Secure Cloud = -70% event spikes!)

---

### Layer 4: Multi-Axis Doom (📋 PLANNED)
**Status**: Not yet implemented
**Complexity**: High (25% added complexity)

Split doom into strategic categories:
```gdscript
var doom_capability_risk: float = 50.0      # From capabilities research
var doom_safety_gap: float = 50.0           # From insufficient safety
var doom_competitive_pressure: float = 50.0  # From rivals
```

**Victory Condition**: All axes < threshold (e.g., 20%)
**Game Over**: Any axis reaches 100%

**Gameplay Effect**:
- Multiple victory paths (focus on one axis vs balance all)
- Specialist strategies (pure safety, pure competition)
- More strategic depth

**When to Implement**: After playtesting shows single-axis doom is too simplistic

---

## 🎮 Current Implementation Details

### Doom Sources (Layer 1)

#### Base Doom
- **Amount**: +1.0 per turn
- **Reason**: Organizational risk, time pressure
- **Modifier**: None currently

#### Capability Researchers
- **Amount**: +3.0 per researcher per turn
- **Reason**: Capabilities research increases AI risk
- **Productive Only**: No (always contributes)
- **From Python**: Matches Python's 3.0 rate

#### Safety Researchers
- **Amount**: -3.5 per **productive** researcher per turn
- **Reason**: Safety research reduces AI risk
- **Productive Check**: Needs compute + management
- **From Python**: Matches Python's 3.5 rate

#### Rivals
- **Amount**: Varies (-10 to +20 typical)
- **Reason**: Competitor actions affect global doom
- **Set Externally**: `doom_system.set_rival_doom_contribution(amount)`
- **Future**: Scale with opponent progress^1.5 + technical debt

#### Unproductive Employees
- **Amount**: +0.5 per unproductive employee
- **Reason**: Idle staff create organizational risk
- **Check**: No compute OR no manager = unproductive

#### Events
- **Amount**: One-time spikes
- **Reason**: Random events, breakthroughs, cascades
- **Usage**: `doom_system.add_event_doom(amount, "reason")`
- **Future**: Event spikes (2-4 doom), cascades (10-20 doom)

---

### Momentum Mechanics (Layer 1)

#### Accumulation
```gdscript
doom_momentum += raw_doom_change * momentum_accumulation_rate
# Default: 15% of each doom change becomes momentum
```

**Tunable**: `momentum_accumulation_rate` (0.0-1.0)
- Higher = faster spirals
- Lower = more stable

#### Decay
```gdscript
doom_momentum *= momentum_decay_rate
# Default: 92% retained (8% decay)
```

**Tunable**: `momentum_decay_rate` (0.0-1.0)
- Higher = momentum lasts longer
- Lower = faster decay

#### Cap
```gdscript
doom_momentum = clamp(doom_momentum, -momentum_cap, momentum_cap)
# Default: ±8.0
```

**Tunable**: `momentum_cap` (0.0-20.0)
- Higher = more extreme spirals
- Lower = more contained

#### Velocity (Smoothing)
```gdscript
doom_velocity = doom_velocity * 0.7 + raw_doom_change * 0.3
# 70% old, 30% new (smoothed moving average)
```

Used for trend detection:
- `< -2.0`: Strongly decreasing
- `-2.0 to -0.5`: Decreasing
- `-0.5 to 0.5`: Stable
- `0.5 to 2.0`: Increasing
- `> 2.0`: Strongly increasing

---

## 🎯 Tuning Parameters

All parameters exposed for easy balancing:

```gdscript
class DoomSystem:
    # Momentum tuning
    var momentum_accumulation_rate: float = 0.15  # 15% becomes momentum
    var momentum_decay_rate: float = 0.92         # 8% decay per turn
    var momentum_cap: float = 8.0                 # Max ±8.0 momentum

    # Source rates (in calculation functions)
    # Base: 1.0
    # Capabilities: 3.0 per researcher
    # Safety: 3.5 per productive researcher
    # Unproductive: 0.5 per employee
```

**Balancing Philosophy**:
- Start with Python values (proven playable)
- Adjust momentum rates based on playtesting
- Goal: 12-15 turn games (matching Python)

---

## 🔌 Extension Points (Future Phases)

### Phase 3: Researcher Specializations

```gdscript
# Example implementation (commented in doom_system.gd)
func apply_researcher_specialization_effects(researchers: Array):
    for researcher in researchers:
        match researcher.specialization:
            "safety":
                apply_doom_modifier("safety", 0.15)  # +15% effectiveness
            "capabilities":
                apply_doom_modifier("capabilities", 0.05)  # +5% doom
            "interpretability":
                set_doom_multiplier("events", 0.9)  # -10% event doom
            "alignment":
                apply_doom_modifier("rivals", -0.5)  # Reduce rival doom
```

### Phase 3: Technical Debt

```gdscript
# Example implementation
func apply_technical_debt_effects(debt: int):
    var debt_multiplier = 1.0 + (debt * 0.05)  # 5% per debt point
    set_doom_multiplier("rivals", debt_multiplier)
    doom_sources["technical_debt"] = debt * 0.2  # Direct doom
```

### Phase 4: Cascade Events

```gdscript
# Example implementation
func trigger_cascade_event(cascade_type: String, severity: float):
    var cascade_doom = severity * 5.0  # 10-20 doom for big cascades
    doom_sources["cascades"] = cascade_doom
    add_event_doom(cascade_doom, "cascade_%s" % cascade_type)
```

### Phase 4: Multi-Axis Doom

```gdscript
# Example implementation
func enable_doom_axes():
    doom_axes_enabled = true
    # Split current doom into axes
    doom_capability_risk = current_doom * 0.4
    doom_safety_gap = current_doom * 0.4
    doom_competitive_pressure = current_doom * 0.2
```

---

## 📊 Testing Strategy

### Unit Tests (✅ Implemented)
**File**: `godot/tests/test_doom_momentum.gd`

16 test cases covering:
- Basic calculation
- Momentum accumulation
- Momentum decay
- Safety/capability research
- Doom spiral scenario
- Safety flywheel scenario
- Source tracking
- Momentum capping
- Trend detection
- Status thresholds
- Game state integration
- Serialization

### Integration Tests (Needed)
- Full game playthrough (15 turns)
- Doom reaches 100 → Game over
- Doom reaches 0 → Victory
- Momentum affects game length
- Balance validation (12-15 turn target)

### Balance Testing (Ongoing)
- Track average game length
- Monitor doom progression curves
- Identify dominant strategies
- Adjust momentum rates if needed

---

## 🎮 Gameplay Examples

### Example 1: Doom Spiral
```
Turn 1: 5 capability researchers, 0 safety
  Doom: 50.0 → 54.0 (+4.0)
  Momentum: 0 → 0.6

Turn 2:
  Doom: 54.0 → 58.6 (+4.6)  # Momentum adds 0.6
  Momentum: 0.6 → 1.2

Turn 3:
  Doom: 58.6 → 63.8 (+5.2)  # Momentum adds 1.2
  Momentum: 1.2 → 1.9

Turn 5:
  Doom: 71.4 → 77.5 (+6.1)  # Accelerating!
  Status: CRITICAL
```

### Example 2: Safety Flywheel
```
Turn 1: 0 capability, 4 safety researchers
  Doom: 50.0 → 45.0 (-5.0)
  Momentum: 0 → -0.75

Turn 2:
  Doom: 45.0 → 39.2 (-5.8)  # Momentum adds -0.75
  Momentum: -0.75 → -1.5

Turn 3:
  Doom: 39.2 → 32.6 (-6.6)  # Accelerating reduction!
  Momentum: -1.5 → -2.3

Turn 8:
  Doom: 2.1 → 0.0 (VICTORY!)
  Status: SAFE
```

### Example 3: Recovery
```
Turn 1-5: Doom spiral (hit 75.0)
  Status: CRITICAL
  Momentum: +3.2

Turn 6: Emergency pivot! (convert 3 cap researchers to safety)
  Doom: 75.0 → 78.2 (+3.2)  # Momentum still positive
  New strategy: 5 safety, 2 capability

Turn 7:
  Doom: 78.2 → 79.5 (+1.3)  # Slowing
  Momentum: +3.2 → +2.1 (decaying)

Turn 8:
  Doom: 79.5 → 79.1 (-0.4)  # Turning around!
  Momentum: +2.1 → +0.8

Turn 12:
  Doom: 72.3 → 66.5 (-5.8)  # Recovery accelerating
  Momentum: -1.5
  Status: DANGER (improving!)
```

---

## 🚀 Implementation Roadmap

### ✅ Phase 1: Momentum (COMPLETE)
- Doom momentum mechanics
- Source tracking
- Integration with game state
- 16 unit tests

### 🔄 Phase 2: Balance Tuning (IN PROGRESS)
- Playtesting
- Momentum parameter tweaking
- Game length validation
- Feedback collection

### 📋 Phase 3: Modifiers (NEXT)
- Researcher specializations
- Technical debt system
- Upgrade effects (Secure Cloud!)
- Market cycle impacts

### 📋 Phase 4: Advanced Systems (FUTURE)
- Multi-axis doom (if needed)
- Cascade events
- Complex interactions

---

## 📝 Design Notes

### Why Momentum?
- Creates emergent narratives
- Rewards strategic consistency
- Punishes flip-flopping
- "Doom spiral" is visceral and understandable
- Small choices compound over time

### Why Not Multi-Axis Yet?
- Keep it simple first
- Validate single-axis is playable
- Add complexity only if needed
- Path of Exile approach: layers over time

### Why Source Tracking?
- Player feedback ("Why is doom changing?")
- Debugging and balance
- Foundation for future complexity
- Minimal overhead (just bookkeeping)

### Why Extensible Architecture?
- Add features without breaking existing systems
- Test incrementally
- Revert easily if features don't work
- Keep codebase maintainable

---

## 🎯 Success Metrics

### Phase 1 Success (Current)
- ✅ Momentum creates doom spirals
- ✅ Safety flywheel works
- ✅ Recovery is possible but harder
- ✅ Source tracking shows breakdown
- ✅ 16 unit tests pass

### Phase 2 Success (Target)
- Average game length: 12-15 turns
- Doom spiral games: 8-10 turns (lose)
- Safety flywheel games: 15-20 turns (win)
- Balanced games: 12-15 turns
- Player feedback: "Momentum feels impactful"

### Phase 3 Success (Future)
- Researcher specs create distinct strategies
- Technical debt matters
- Upgrades provide meaningful choices
- No dominant strategy

---

## 🔗 Related Files

**Core Implementation**:
- `godot/scripts/core/doom_system.gd` - Doom system class
- `godot/scripts/core/game_state.gd` - Integration with game state
- `godot/scripts/core/turn_manager.gd` - Integration with turn processing

**Testing**:
- `godot/tests/test_doom_momentum.gd` - 16 unit tests

**Documentation**:
- `GODOT_PHASE_5_SUMMARY.md` - Phase 5 overview
- `godot/PHASE_5_QUICK_REFERENCE.md` - Player guide
- `PHASE_6_SUGGESTIONS.md` - Future improvements

---

## 🎊 Summary

The Doom System is **production-ready** with modular architecture for future expansion. Start with simple momentum mechanics, add layers over time without breaking existing gameplay.

**Current Status**: Phase 1 complete, Phase 2 (balancing) in progress.

**Path Forward**: Playtest → Balance → Add Layers (researcher specs, tech debt, etc.)

The foundation is solid. Time to play and tune! 🎮✨

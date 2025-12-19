# Personnel & Hiring

> **Status**: Active - Core mechanic ([Issue #465](https://github.com/PipFoweraker/pdoom1/issues/465))

Your research team is your most valuable asset. Hiring the right mix of researchers, managing their productivity, and preventing burnout are essential to success.

## Current Mechanics (v0.11.0)

## Game Data (Auto-Generated)

> **Note**: This section is automatically generated from the game code. Do not edit manually.
> Last updated: 2025-12-19

| Variable | Default Value | Type | Source |
|----------|---------------|------|--------|
| `safety_researchers` | `0` | int | [godot/scripts/core/game_state.gd:21](../../godot/scripts/core/game_state.gd#L21) |
| `capability_researchers` | `0` | int | [godot/scripts/core/game_state.gd:22](../../godot/scripts/core/game_state.gd#L22) |
| `compute_engineers` | `0` | int | [godot/scripts/core/game_state.gd:23](../../godot/scripts/core/game_state.gd#L23) |
| `managers` | `0` | int | [godot/scripts/core/game_state.gd:24](../../godot/scripts/core/game_state.gd#L24) |
| `MAX_CANDIDATES` | `6` | int | [godot/scripts/core/game_state.gd:31](../../godot/scripts/core/game_state.gd#L31) |

*These values are extracted from the game source code and updated automatically.*

---

### Starting Staff
You begin with no staff. The candidate pool starts with 2-3 low-skill candidates.

### Staff Types Overview

| Type | Cost | Effect | Doom Impact |
|------|------|--------|-------------|
| Safety Researcher | $60,000 | Reduces doom | -3.5/turn |
| Capability Researcher | $60,000 | Generates research | +3.0/turn |
| Interpretability Researcher | $70,000 | Audit actions | -3.0/turn |
| Alignment Researcher | $65,000 | Event reduction | -3.2/turn |
| Compute Engineer | $50,000 | Compute efficiency | Neutral |
| Manager | $80,000 | Manages 8 staff | Neutral |
| AI Ethicist | $70,000 | +5 reputation | Neutral |

## Researcher Specializations

### Safety Researcher
- **Base Cost**: $60,000
- **Doom Reduction**: -3.5 per turn (with +15% specialization bonus)
- **Focus**: AI safety and alignment research
- **Best For**: Your core doom-fighting force

### Capability Researcher
- **Base Cost**: $60,000
- **Research Speed**: +25% faster
- **Doom Impact**: +3.0 per turn (+5% additional from specialization)
- **Focus**: Advancing AI capabilities
- **Risk**: Increases doom but generates research points

### Interpretability Researcher
- **Base Cost**: $70,000
- **Doom Reduction**: -3.0 per turn
- **Special**: Unlocks audit and transparency actions
- **Focus**: Making AI systems understandable

### Alignment Researcher
- **Base Cost**: $65,000
- **Doom Reduction**: -3.2 per turn
- **Special**: -10% chance of negative events
- **Focus**: Ensuring AI goals align with human values

## Candidate Pool System

Researchers don't appear instantly - they come from a candidate pool.

### How It Works
1. Pool holds up to 6 candidates
2. New candidates appear slowly over time
3. You hire from available candidates
4. Starting candidates have lower skill (1-3)
5. Later candidates may have higher skill

### Initial Candidates
At game start, you get 2-3 starting candidates:
- 1 guaranteed safety researcher
- 1 random (50% safety, 50% capabilities)
- 50% chance of a third random candidate

All starting candidates have skill level 1-3.

## Management System

### Management Capacity
- **Base Capacity**: 9 employees (before first manager)
- **Per Manager**: 8 additional employees
- **Formula**: `capacity = max(9, managers * 9)`

### Unmanaged Penalty
Staff exceeding management capacity become partially unproductive:
- Unmanaged staff add +0.5 doom per turn
- They don't contribute to research effectively

## Productivity System

### What Determines Productivity

A researcher's effective productivity is calculated from:

```
effective = base_productivity
          * (1 - burnout_penalty)
          * (1 - jet_lag_penalty)
          * trait_modifiers
          * salary_satisfaction
```

**Minimum**: 10% (even totally burned out)
**Maximum**: ~250% (perfect conditions + traits)

### Productivity Requirements

For a researcher to be productive:
1. Must be managed (within management capacity)
2. Must have compute available
3. `productive_count = min(managed_staff, available_compute)`

## Researcher Stats

### Skill Level
- **Range**: 1-10
- **New Hires**: 3-7 (random)
- **Growth**: 5% chance per turn to increase by 1
- **Effect**: `base_productivity = 0.5 + (skill * 0.1)`

### Loyalty
- **Range**: 0-100
- **New Hires**: 40-70
- **Increases**: +1/turn if paid at or above expectation
- **Decreases**: -2/turn if paid below 80% of expectation
- **Effect**: Affects poaching resistance (future feature)

### Burnout
- **Range**: 0-100
- **Accumulation**: +0.5 base per turn
- **Critical Threshold**: 80 (researcher is "burned out")
- **Penalty**: Up to 50% productivity reduction at 100 burnout

## Researcher Traits

### Positive Traits

| Trait | Effect | Notes |
|-------|--------|-------|
| Workaholic | +20% productivity | +2 burnout/turn |
| Team Player | +10% team productivity | Boosts everyone |
| Media Savvy | +3 reputation on publish | Great for papers |
| Safety Conscious | -10% doom from work | Reduces their doom contribution |
| Fast Learner | +50% skill growth rate | Improves over time |
| Road Warrior | -50% jet lag duration | For frequent travelers |

### Negative Traits

| Trait | Effect | Notes |
|-------|--------|-------|
| Prima Donna | -20% productivity if underpaid | Must pay 90%+ of expectation |
| Leak Prone | 5% leak chance per turn | Can cause reputation damage |
| Burnout Prone | +50% burnout rate | Burns out faster |
| Pessimist | -5 team morale | Brings down the team |

### Trait Assignment (New Hires)
- 40% chance of one positive trait
- 25% chance of one negative trait
- Some hires may have both or neither

## Jet Lag System (Issue #469)

Conference travel causes jet lag, reducing productivity.

### Travel Classes

| Class | Cost Multiplier | Recovery Time | Productivity Loss |
|-------|-----------------|---------------|-------------------|
| Economy | 1.0x | 10 turns | -40% |
| Business | 2.5x | 5 turns | -20% |
| First Class | 5.0x | 2 turns | -10% |

### Distance Scaling
- Local (tier 1): No jet lag
- Domestic (tier 2): 60% of base jet lag
- International (tier 3): 100% of base jet lag

## Actions for Personnel Management

| Action | Effect | Cost |
|--------|--------|------|
| Hire Staff | Opens hiring submenu | Free |
| Team Building | Reduces burnout, +2 rep | $10,000, 1 AP |
| Emergency Pivot | Convert cap to safety | $50,000, 2 AP |

## Strategic Considerations

### Early Game
- Hire safety researchers first (you start at 50 doom)
- Get a manager before hitting 9 staff
- Avoid capability researchers until doom is under control

### Team Composition
- Aim for 2:1 or 3:1 safety:capability ratio
- At least one interpretability for audits
- Managers scale with team size

### Burnout Management
- Run Team Building periodically
- Watch for 80+ burnout (critical)
- Workaholics are productive but burn out faster

### Trait Priorities
- **Best**: Team Player, Safety Conscious
- **Good**: Media Savvy, Fast Learner
- **Avoid**: Leak Prone, Prima Donna

## Related Game Systems

- **[P(Doom)](doom.md)** - Staff composition directly affects doom
- **[Funding](funding.md)** - Staff are your primary expense
- **[Reputation](reputation.md)** - Media savvy researchers boost papers

## Developer Notes

### Code References
- **Researcher Class**: [`godot/scripts/core/researcher.gd`](../../godot/scripts/core/researcher.gd) - Full researcher implementation
- **Game State**: [`godot/scripts/core/game_state.gd:21-32`](../../godot/scripts/core/game_state.gd#L21) - Staff variables
- **Hiring Actions**: [`godot/scripts/core/actions.gd:132-170`](../../godot/scripts/core/actions.gd#L132) - Hiring submenu
- **Doom Calculation**: [`godot/scripts/core/doom_system.gd:161`](../../godot/scripts/core/doom_system.gd#L161) - Researcher doom contribution

### Architecture Notes
The personnel system uses two models:
1. **Legacy counters**: `safety_researchers`, `capability_researchers`, etc.
2. **Individual researcher array**: Full Researcher objects with traits, burnout, etc.

The new system takes precedence when researchers exist; legacy counters are maintained for backward compatibility.

---

*Last updated: 2025-12-19 | [Edit this page](https://github.com/PipFoweraker/pdoom1/blob/main/docs/mechanics/personnel.md)*

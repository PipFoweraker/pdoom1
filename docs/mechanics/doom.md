# P(Doom) - The Doom System

> **Status**: Active - Core mechanic ([Issue #465](https://github.com/PipFoweraker/pdoom1/issues/465))

P(Doom) represents the probability of catastrophic AI outcomes. Your goal is to reduce it to zero while preventing it from reaching 100.

## Current Mechanics (v0.11.0)

## Game Data (Auto-Generated)

> **Note**: This section is automatically generated from the game code. Do not edit manually.
> Last updated: 2025-12-19

| Variable | Default Value | Type | Source |
|----------|---------------|------|--------|
| `doom` | `50.0` | float | [godot/scripts/core/game_state.gd:11](../../godot/scripts/core/game_state.gd#L11) |
| `current_doom` | `50.0` | float | [godot/scripts/core/doom_system.gd:11](../../godot/scripts/core/doom_system.gd#L11) |
| `doom_velocity` | `0.0` | float | [godot/scripts/core/doom_system.gd:14](../../godot/scripts/core/doom_system.gd#L14) |
| `doom_momentum` | `0.0` | float | [godot/scripts/core/doom_system.gd:15](../../godot/scripts/core/doom_system.gd#L15) |
| `momentum_cap` | `8.0` | float | [godot/scripts/core/doom_system.gd:20](../../godot/scripts/core/doom_system.gd#L20) |

*These values are extracted from the game source code and updated automatically.*

---

### Win/Lose Conditions
- **Victory**: Reduce doom to 0
- **Defeat**: Doom reaches 100 OR reputation reaches 0

### Doom Range
- **Starting Value**: 50.0
- **Range**: 0 - 100
- **Clamped**: Cannot go below 0 or above 100

## Doom Sources

The doom system tracks multiple sources of risk:

| Source | Effect | Description |
|--------|--------|-------------|
| Base | +1.0/turn | Inherent organizational risk |
| Capabilities | +3.0/researcher | Capability research increases doom |
| Safety | -3.5/researcher | Safety research reduces doom (base) |
| Rivals | Variable | Competitor actions add doom |
| Unproductive | +0.5/staff | Idle employees increase risk |
| Events | Variable | Random events can spike doom |
| Momentum | Compounds | Accumulated doom changes |

### Doom from Staff

**Capability Researchers**:
- Base: +3.0 doom per productive researcher
- +5% additional doom from capabilities specialization

**Safety Researchers**:
- Base: -3.5 doom per productive researcher
- +15% bonus reduction from safety specialization

**Other Specializations**:
- Interpretability: -3.0 doom (counts as safety)
- Alignment: -3.2 doom (slightly better than base safety)

### Unproductive Staff Penalty
Staff are unproductive if:
1. Not managed (no manager capacity)
2. No compute available

Each unproductive staff member adds +0.5 doom per turn.

## Momentum System

Doom has momentum - changes tend to compound over time.

### Momentum Mechanics
```
velocity = velocity * 0.7 + raw_change * 0.3  (30% new, 70% old)
momentum += raw_change * 0.15  (15% accumulation rate)
momentum = clamp(momentum, -8.0, 8.0)  (capped)
momentum *= 0.92  (8% decay per turn)
```

### Doom Trends
| Velocity | Trend |
|----------|-------|
| < -2.0 | Strongly Decreasing |
| < -0.5 | Decreasing |
| < 0.5 | Stable |
| < 2.0 | Increasing |
| >= 2.0 | Strongly Increasing |

### Doom Status Levels
| Doom | Status |
|------|--------|
| < 25 | Safe |
| < 50 | Warning |
| < 70 | Danger |
| < 90 | Critical |
| >= 90 | Catastrophic |

### Momentum Descriptions
- **Neutral**: |momentum| < 0.5
- **Doom Spiral**: momentum > 0 (things getting worse faster)
- **Safety Flywheel**: momentum < 0 (things getting better faster)

## Actions That Affect Doom

### Doom Reduction Actions
| Action | Effect | Cost |
|--------|--------|------|
| Safety Research | -1.0 x safety_researchers | 10 research, 1 AP |
| Publish Paper | -3 doom, +1 paper | 20 research, 1 AP |
| Safety Audit | -5 - safety_researchers | $40,000, 2 AP |
| Team Building | -1 doom | $10,000, 1 AP |
| Lobby Government | -8 - (rep x 0.1) | $80,000, 2 AP, -10 rep |
| Public Warning | -15 +/- random | 2 AP, 15 reputation |
| Open Source Release | -10 - (papers x 2) | 3 papers, 1 AP |
| Sabotage (success) | -20 doom | $100,000, 3 AP, 20 rep |

### Doom Increase Sources
| Source | Effect |
|--------|--------|
| Base per turn | +1.0 |
| Capability researchers | +3.0 each |
| Unproductive staff | +0.5 each |
| Sabotage (failure) | +10 doom, -25 reputation |
| Acquire capability startup | +3 doom |

## Strategic Considerations

### Doom Management Priorities
1. **Build safety team first** - Safety researchers provide ongoing doom reduction
2. **Avoid unproductive staff** - Ensure compute and management capacity
3. **Watch momentum** - A doom spiral can quickly become unrecoverable
4. **Balance capability research** - Sometimes needed but always risky

### When to Panic
- **Doom > 70**: Critical territory - focus all efforts on reduction
- **Positive momentum > 3**: Doom spiral forming - take aggressive action
- **No safety researchers**: Doom will only increase

### Recovery Strategies
- Stack safety researchers to reverse momentum
- Use Safety Audit for immediate large reductions
- Consider Emergency Pivot to convert capability researchers
- Open source releases for big one-time reductions (costs papers)

## Researcher Traits Affecting Doom

| Trait | Effect |
|-------|--------|
| Safety Conscious | -10% doom from their work |
| Workaholic | +20% productivity (more doom reduction) |

## Related Game Systems

- **[Personnel](personnel.md)** - Researcher types determine doom impact
- **[Funding](funding.md)** - Money enables doom-reducing actions
- **[Reputation](reputation.md)** - Some doom actions cost reputation

## Future Enhancements

**Phase 2**: Source tracking visualization in UI
**Phase 3**: Doom multipliers from researcher specializations, technical debt
**Phase 4**: Multi-axis doom (capability risk, safety gap, competitive pressure)

## Developer Notes

### Code References
- **Doom System**: [`godot/scripts/core/doom_system.gd`](../../godot/scripts/core/doom_system.gd) - Full doom calculation
- **State**: [`godot/scripts/core/game_state.gd:11`](../../godot/scripts/core/game_state.gd#L11) - Doom variable
- **Actions**: [`godot/scripts/core/actions.gd`](../../godot/scripts/core/actions.gd) - Actions affecting doom

### Architecture Notes
The doom system is designed to be modular and extensible:
- Phase 1: Basic sources + momentum (current)
- Phase 2: Source tracking and visualization
- Phase 3: Multipliers and modifiers
- Phase 4: Multi-dimensional doom axes

---

*Last updated: 2025-12-19 | [Edit this page](https://github.com/PipFoweraker/pdoom1/blob/main/docs/mechanics/doom.md)*

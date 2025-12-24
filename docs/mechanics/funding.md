# Funding & Resources

> **Status**: Active - Core mechanic ([Issue #465](https://github.com/PipFoweraker/pdoom1/issues/465))

Money is your lab's lifeblood. Managing funding is critical to hiring researchers, purchasing compute, and surviving long enough to reduce P(Doom).

## Current Mechanics (v0.11.0)

## Game Data (Auto-Generated)

> **Note**: This section is automatically generated from the game code. Do not edit manually.
> Last updated: 2025-12-19

| Variable | Default Value | Type | Source |
|----------|---------------|------|--------|
| `money` | `245000.0` | float | [godot/scripts/core/game_state.gd:6](../../godot/scripts/core/game_state.gd#L6) |
| `compute` | `100.0` | float | [godot/scripts/core/game_state.gd:7](../../godot/scripts/core/game_state.gd#L7) |
| `research` | `0.0` | float | [godot/scripts/core/game_state.gd:8](../../godot/scripts/core/game_state.gd#L8) |
| `papers` | `0.0` | float | [godot/scripts/core/game_state.gd:9](../../godot/scripts/core/game_state.gd#L9) |
| `stationery` | `100.0` | float | [godot/scripts/core/game_state.gd:13](../../godot/scripts/core/game_state.gd#L13) |

*These values are extracted from the game source code and updated automatically.*

---

### Starting Resources
- **Money**: $245,000 (updated from player feedback, Issue #436)
- **Compute**: 100 units
- **Research Points**: 0 (generated from researchers)
- **Papers**: 0
- **Stationery**: 100 units (consumed by staff each turn)

### Money Sinks

| Expense | Cost | Notes |
|---------|------|-------|
| Safety Researcher | $60,000 | Base hiring cost |
| Capability Researcher | $60,000 | Base hiring cost |
| Interpretability Researcher | $70,000 | Specialized hire |
| Alignment Researcher | $65,000 | Specialized hire |
| Compute Engineer | $50,000 | Improves compute efficiency |
| Manager | $80,000 | Handles up to 8 researchers |
| AI Ethicist | $70,000 | +5 reputation |
| Purchase Compute | $50,000 | +50 compute units |
| Team Building | $10,000 | Reduces burnout, +2 reputation |
| Safety Audit | $40,000 | Reduces doom, +3 reputation |
| Media Campaign | $30,000 | +10+ reputation |
| Lobby Government | $80,000 | Reduces doom significantly |
| Office Supplies | $2,000 | +50 stationery |
| Office Maintenance | $5,000 | Slight morale improvement |

## Fundraising Options

### Modest Funding Round
- **Cost**: 1 AP, 2 reputation
- **Returns**: $30,000 - $60,000 (random)
- **Risk**: Low - always available
- **Best For**: Steady income when reputation is low

### Major Funding Round
- **Cost**: 2 AP, 8 reputation
- **Returns**: $80,000 - $150,000 base + (reputation x $500 bonus)
- **Risk**: Medium - requires decent reputation
- **Best For**: Big pushes when reputation is high

### Business Loan
- **Cost**: 1 AP
- **Returns**: $75,000 immediate
- **Risk**: High - creates $90,000 debt obligation
- **Best For**: Emergency cash needs

### Research Grant
- **Cost**: 1 AP, 1 paper
- **Returns**: $50,000 - $100,000 base + (papers x $5,000 bonus)
- **Risk**: Low - requires published research
- **Best For**: Converting academic success to funding

### Grant Proposal (Strategic)
- **Cost**: 1 AP, 1 paper
- **Returns**: $80,000 base + (reputation x $1,500)
- **Best For**: High reputation labs with papers

## Compute System

Compute is required for researchers to be productive:

- Each productive researcher needs 1 compute
- Researchers without compute are unproductive
- Unproductive researchers add +0.5 doom per turn
- Buy compute at $50,000 for 50 units

### Productivity Formula
```
productive_count = min(managed_staff, available_compute)
```

## Office Operations

### Stationery System
- Staff consume stationery each turn
- Low stationery affects operations
- Restock: $2,000 for +50 supplies (max 100)

### Maintenance
- Office maintenance costs $5,000
- Improves team morale slightly

## Strategic Considerations

### When to Fundraise
- Before major hiring pushes
- When money drops below $100,000
- After reputation gains (maximize major round bonuses)

### Budget Planning
- Keep 2-3 months of operating expenses in reserve
- Account for ongoing salary costs (future feature)
- Balance growth vs. cash reserves

### Trade-offs
- **Speed vs. Safety**: More funding enables faster scaling but rushing can increase doom
- **Reputation vs. Cash**: Fundraising costs reputation; balance carefully
- **Debt vs. Equity**: Loans provide immediate cash but create future obligations

## Related Game Systems

- **[P(Doom)](doom.md)** - Unproductive staff increase doom
- **[Personnel](personnel.md)** - Staff are your main expense
- **[Reputation](reputation.md)** - Affects funding round returns

## Implementation Status

**Current State** (v0.11.0):
- Basic money tracking
- All fundraising options implemented
- Compute purchasing
- Stationery system

**Planned Future**:
- Ongoing salary costs (per-turn expenses)
- Investor relationships (different investor types)
- Burn rate tracking and warnings
- Loan repayment mechanics

## Developer Notes

### Code References
- **State**: [`godot/scripts/core/game_state.gd:6-13`](../../godot/scripts/core/game_state.gd#L6) - Resource variables
- **Actions**: [`godot/scripts/core/actions.gd:172-207`](../../godot/scripts/core/actions.gd#L172) - Fundraising options
- **Format**: [`godot/autoload/game_config.gd:254`](../../godot/autoload/game_config.gd#L254) - Money formatting (Issue #436)

---

*Last updated: 2025-12-19 | [Edit this page](https://github.com/PipFoweraker/pdoom1/blob/main/docs/mechanics/funding.md)*

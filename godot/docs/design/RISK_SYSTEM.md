# Risk System Design Document

> **Status**: In Development
> **Created**: 2025-12-25
> **Related Issues**: #500 (Research Quality), #512 (Doom Trend Graph)

## Executive Summary

The Risk System introduces hidden, accumulating consequences that manifest stochastically over time. Unlike the visible Doom meter, risk pools track latent dangers that convert to events (and ultimately doom) based on probability thresholds.

This creates a more realistic simulation where cutting corners doesn't immediately hurt you, but increases the probability of future problems - mirroring real-world dynamics in AI safety and research integrity.

---

## Decision Log

| Date | Decision | Options Considered | Rationale |
|------|----------|-------------------|-----------|
| 2025-12-25 | **Multi-pool architecture** | Single, Dual, Multi (4-6 pools) | Richer gameplay, captures distinct failure modes |
| 2025-12-25 | **Hybrid event triggering** | Threshold-only, Probabilistic-only, Hybrid | Natural feel - "always a risk, finally happened" |
| 2025-12-25 | **Active reduction only** | No decay, Slow decay, Active reduction | Creates interesting decisions about "paying down" risk |
| 2025-12-25 | **Other players can reduce risk** | Player-only, All actors | Opponents/allies can contribute to or mitigate shared risk pools |
| 2025-12-25 | **"Risk" naming** | Risk, Exposure, Technical Debt, Accumulated Consequences | Simple and direct; may revisit for player-facing |
| 2025-12-25 | **6 pools (added Financial)** | 5 pools, 6 pools | Financial risk captures funding lead-lag, planning fallacy, overhead blindness |
| 2025-12-25 | **Skill-gated insight** | Always show, Never show, Skill-gated | Player insight into risk/consequences scales with character skills (like Civ diplomacy) |
| 2025-12-25 | **Causal transparency: sometimes** | Always, Sometimes, Never | Causal explanations gated by "retrospective inference" skill; start with dev mode + simple model for playtesting |
| 2025-12-25 | **Character creation acknowledged** | N/A | Game will have point-allocation character creation; insight skills part of that system (future work) |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PLAYER/OPPONENT ACTIONS                      │
│  (publish paper, rush research, hire researcher, lobby, etc.)        │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          RISK POOLS (Hidden)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │ Capability  │ │  Research   │ │ Regulatory  │ │   Public    │   │
│  │  Overhang   │ │  Integrity  │ │  Attention  │ │  Awareness  │   │
│  │             │ │             │ │             │ │             │   │
│  │ Current: 45 │ │ Current: 12 │ │ Current: 67 │ │ Current: 23 │   │
│  │ Threshold:  │ │ Threshold:  │ │ Threshold:  │ │ Threshold:  │   │
│  │ 50/75/100   │ │ 50/75/100   │ │ 50/75/100   │ │ 50/75/100   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│  ┌─────────────┐ ┌─────────────┐                                    │
│  │  Insider    │ │  Financial  │                                    │
│  │   Threat    │ │  Exposure   │                                    │
│  │             │ │             │                                    │
│  │ Current: 8  │ │ Current: 31 │                                    │
│  │ Threshold:  │ │ Threshold:  │                                    │
│  │ 50/75/100   │ │ 50/75/100   │                                    │
│  └─────────────┘ └─────────────┘                                    │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EVENT TRIGGER SYSTEM (Hybrid)                     │
│                                                                      │
│  Each turn, for each pool:                                          │
│    1. Calculate trigger probability = pool_value / 100              │
│    2. Roll against probability (deterministic RNG)                  │
│    3. If roll succeeds OR pool >= threshold: trigger event          │
│    4. Thresholds (50, 75, 100) guarantee escalating events          │
│                                                                      │
│  Events are selected from pool-specific event tables                │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         CONSEQUENCES                                 │
│                                                                      │
│  Events can cause:                                                  │
│    - Direct doom changes (+5, +10, etc.)                            │
│    - Resource impacts (money, reputation, compute)                  │
│    - Researcher effects (burnout, departure, skill loss)            │
│    - Narrative moments (player choices with trade-offs)             │
│    - Risk pool changes (cascade effects between pools)              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Risk Pool Definitions

### 1. Capability Overhang

**Theme**: The gap between AI capabilities and safety understanding.

**Increased by**:
- Publishing capability-advancing research
- Rushing papers (low rigor)
- Hiring capabilities researchers without safety balance
- Opponent labs publishing capabilities work
- Ignoring safety milestones

**Reduced by**:
- Publishing safety research
- Thorough research practices
- Safety-focused hiring
- Industry-wide safety initiatives (opponent actions)
- Attending safety conferences

**Events when triggered**:
- "Capability Breakthrough" - Major AI advance, doom spike
- "Alignment Tax Debate" - Public discourse, reputation effects
- "Recursive Self-Improvement Scare" - Media panic, regulatory attention

---

### 2. Research Integrity

**Theme**: The quality and trustworthiness of your lab's work.

**Increased by**:
- Rushing papers
- Skipping peer review
- Not publishing negative results
- Overworking researchers (burnout)
- Ignoring replication failures

**Reduced by**:
- Thorough research practices
- Publishing negative results
- Replication studies
- Healthy researcher workload
- External audits

**Events when triggered**:
- "Retraction Notice" - Paper retracted, reputation damage
- "Reproducibility Crisis" - Field-wide credibility loss
- "Whistleblower" - Internal leak, public scandal

---

### 3. Regulatory Attention

**Theme**: Government and institutional scrutiny of AI development.

**Increased by**:
- High-profile publications
- Capability breakthroughs (yours or others)
- Public incidents
- Lobbying failures
- Media coverage

**Reduced by**:
- Proactive transparency
- Compliance investments
- Successful lobbying
- Safety-focused messaging
- Industry self-regulation

**Events when triggered**:
- "Congressional Hearing" - Resource drain, forced testimony
- "Regulatory Framework" - New constraints on research
- "Moratorium Proposal" - Potential research freeze

---

### 4. Public Awareness

**Theme**: General public attention to AI risks and your lab specifically.

**Increased by**:
- Media coverage (positive or negative)
- High-profile publications
- AI incidents in the news
- Competitor scandals
- Doom increases

**Reduced by**:
- Low-profile operations
- Positive community engagement
- Safety communications
- Time passing without incidents

**Events when triggered**:
- "Viral AI Panic" - Public fear, political pressure
- "Tech Backlash" - Hiring difficulties, funding challenges
- "Protest Movement" - Direct action against labs

---

### 5. Insider Threat

**Theme**: Risk from within your organization.

**Increased by**:
- Low researcher morale
- Salary disparities
- Overwork/burnout
- Hiring without vetting
- Toxic work culture

**Reduced by**:
- Fair compensation
- Healthy workload
- Strong culture
- Security investments
- Researcher satisfaction

**Events when triggered**:
- "Data Leak" - Research stolen, competitor advantage
- "Researcher Defection" - Key talent leaves for rival
- "Sabotage" - Internal damage to projects

---

### 6. Financial Exposure

**Theme**: Funding uncertainty and cash flow fragility.

**Increased by**:
- Over-optimistic budget planning
- Delayed grant/funding announcements
- Hiring ahead of confirmed funding
- Research timelines slipping (publication delays)
- Ignoring operational overheads
- Expensive compute purchases without runway buffer
- Salary increases without matching revenue

**Reduced by**:
- Conservative financial planning
- Maintaining cash reserves (runway buffer)
- Diversified funding sources
- On-time publication milestones
- Successful grant applications
- Overhead reduction initiatives

**Events when triggered**:
- "Funding Delay" - Expected grant delayed, cash crunch
- "Budget Shortfall" - Must cut staff or projects
- "Runway Crisis" - Emergency cost-cutting, morale damage
- "Grant Rejection" - Major funder passes, scramble for alternatives

**Design Notes**:
This pool captures the lead-lag dynamics of academic/research funding:
- Grants announced months before disbursement
- Publication timelines affect future funding eligibility
- Overhead costs (facilities, admin, equipment) often underestimated
- Planning fallacy: researchers chronically over-optimistic about timelines

---

## Event Triggering: Hybrid System

### Per-Turn Calculation

```gdscript
func process_risk_events(state: GameState, rng: RandomNumberGenerator) -> Array[Dictionary]:
    var triggered_events: Array[Dictionary] = []

    for pool_name in risk_pools.keys():
        var pool_value = risk_pools[pool_name]
        var probability = pool_value / 100.0  # 0.0 to 1.0+

        # Probabilistic check
        var roll = rng.randf()
        var triggered_by_roll = roll < probability

        # Threshold check (guaranteed triggers)
        var threshold_tier = _get_threshold_tier(pool_name, pool_value)
        var triggered_by_threshold = threshold_tier > _last_triggered_tier[pool_name]

        if triggered_by_roll or triggered_by_threshold:
            var event = _select_event_for_pool(pool_name, threshold_tier)
            triggered_events.append(event)

            # Record for verification
            VerificationTracker.record_rng_outcome(
                "risk_" + pool_name,
                roll,
                state.turn
            )

            # Update threshold tracking
            if triggered_by_threshold:
                _last_triggered_tier[pool_name] = threshold_tier

    return triggered_events

func _get_threshold_tier(pool_name: String, value: float) -> int:
    if value >= 100: return 3  # Catastrophic
    if value >= 75: return 2   # Severe
    if value >= 50: return 1   # Moderate
    return 0                    # None
```

### Threshold Tiers

| Tier | Pool Value | Event Severity | Guaranteed? |
|------|------------|----------------|-------------|
| 0 | 0-49 | Minor (if triggered by roll) | No |
| 1 | 50-74 | Moderate | Yes, once |
| 2 | 75-99 | Severe | Yes, once |
| 3 | 100+ | Catastrophic | Yes, once |

---

## Risk Reduction Mechanics

Risk pools do **not** decay automatically. They require active intervention:

### Reduction Actions

| Action | Pools Affected | Reduction Amount |
|--------|---------------|------------------|
| Publish safety paper | Capability Overhang | -5 to -15 based on quality |
| Publish negative results | Research Integrity | -3 to -8 |
| Thorough research mode | Research Integrity, Capability Overhang | -1 per turn |
| Compliance investment | Regulatory Attention | -5 to -10 |
| Public safety messaging | Public Awareness | -3 to -7 |
| Improve working conditions | Insider Threat | -2 to -5 |
| Industry safety coalition | All pools | -2 to -5 each |
| Maintain runway buffer | Financial Exposure | -3 to -8 |
| Successful grant application | Financial Exposure | -5 to -15 |
| Diversify funding sources | Financial Exposure | -5 to -10 |
| On-time publication | Financial Exposure, Research Integrity | -2 to -5 each |

### Opponent Contributions

Other players/AI labs can affect shared pools:

- **Positive**: Opponent publishes safety research → reduces Capability Overhang for all
- **Negative**: Opponent causes incident → increases Public Awareness for all
- **Competitive**: Opponent's integrity scandal → your Research Integrity relatively safer

---

## Integration Points

### Files to Modify

| File | Changes |
|------|---------|
| `godot/scripts/core/risk_pool.gd` | **NEW** - RiskPool class |
| `godot/scripts/core/game_state.gd` | Add `risk_system: RiskPool` property |
| `godot/scripts/core/turn_manager.gd` | Call `risk_system.process_turn()` during execution |
| `godot/scripts/core/actions.gd` | Add risk contributions to action effects |
| `godot/scripts/core/events.gd` | Add risk-triggered events to event tables |
| `godot/scripts/ui/dev_tools.gd` | Display risk pools in dev mode |

### Serialization

```gdscript
# In RiskPool.to_dict()
func to_dict() -> Dictionary:
    return {
        "pools": risk_pools.duplicate(),
        "last_triggered_tiers": _last_triggered_tier.duplicate(),
        "history": _risk_history.duplicate()  # For trend analysis
    }
```

### Dev Mode Display

Risk pools visible in dev mode as:
- Current values per pool
- Threshold proximity warnings
- Historical trend (last 10 turns)
- Trigger probability this turn

---

## Player Visibility

### Insight System (Skill-Gated)

Player visibility into risk and consequences scales with **Insight** skills. This creates a spectrum from "learn through experience" to "see the full decision tree."

| Insight Level | What Player Sees |
|---------------|------------------|
| **None (0)** | Outcomes only, no explanations |
| **Low (1-2)** | Vague hints: "Reaction will likely be mixed" |
| **Medium (3-4)** | Directional: "This will increase regulatory scrutiny" |
| **High (5-6)** | Specific: "OpenPhil dislikes this; Anthropic neutral" |
| **Expert (7+)** | Quantified: "Regulatory Attention +8, Financial Exposure +3" |

**Insight Domains** (future work):
- Political Insight → Regulatory Attention, Public Awareness visibility
- Financial Insight → Financial Exposure visibility
- Academic Insight → Research Integrity, Capability Overhang visibility
- Organizational Insight → Insider Threat visibility

**Implementation Note**: For initial release, implement as dev mode toggle (full visibility on/off). Skill-gating requires character creation system, which is future work.

### Default Visibility (No Insight Skills)
- Narrative hints: "Your lab's reputation for rigor is questioned"
- Event outcomes without causal chains
- Trend indicators (after #512): Doom graph shows spikes from risk events

### Dev Mode (Full Visibility)
- All pool values
- All calculations
- Trigger logs
- Risk contribution breakdown per action
- Causal chains for all events

---

## Future Extensions

### Planned
- Research Quality toggle (#500) feeds into Research Integrity pool
- Opponent AI contributes to shared pools
- Player-facing "Lab Health" summary (aggregates risk into single indicator)
- **Character Creation System**: Point allocation for starting resources, staff, and personality bonuses
- **Insight Skills**: Skill-gated visibility into risk mechanics (requires character system)
- **Upgrade Rework**: Make upgrades more subtle in effect, integrate with insight system

### Possible
- Risk trading between players (multiplayer)
- Insurance/hedging mechanics
- Risk specialization (some labs accept certain risks)
- Dynamic thresholds based on game difficulty
- Domain-specific insight skills (Political, Financial, Academic, Organizational)
- Retrospective causal inference skill (explains past events)

---

## Success Criteria

- [ ] RiskPool class implemented following DoomSystem patterns
- [ ] 6 risk pools tracking independently
- [ ] Hybrid event triggering (probabilistic + threshold)
- [ ] Active reduction via specific actions
- [ ] Stub for opponent contributions
- [ ] Dev mode visibility
- [ ] Serialization for save/load
- [ ] Integration with TurnManager
- [ ] Player-facing documentation complete
- [ ] At least 3 events per pool defined

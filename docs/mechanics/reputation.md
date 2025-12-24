# Reputation & Public Opinion

> **Status**: 🟡 Stub - Under active development ([Issue #186](https://github.com/PipFoweraker/pdoom1/issues/186))

Your lab's reputation affects funding opportunities, researcher recruitment, and regulatory pressure. Managing public opinion is key to long-term success.

## Current Mechanics (v0.10.2)

## Game Data (Auto-Generated)

> **Note**: This section is automatically generated from the game code. Do not edit manually.
> Last updated: 2025-12-19 15:23:19

| Variable | Default Value | Type | Source |
|----------|---------------|------|--------|
| `reputation` | `50.0` | float | [godot/scripts/core/game_state.gd:10](../../godot/scripts/core/game_state.gd#L10) |


*These values are extracted from the game source code and updated automatically.*

---

### Reputation Score
- **Range**: 0-100
- **Starting Value**: 50
- **Current Uses**: Limited (primarily affects funding and recruitment)

### How Reputation Changes

**Gains:**
- Publishing research papers
- Hiring media-savvy researchers
- Successful public milestones

**Losses:**
- Research leaks from leak-prone researchers
- Negative events (scandals, accidents)
- Rival lab competitive actions

## Planned Enhancements 🚧

The following features are planned for the **Public Opinion & Media System** enhancement:

### 1. Dynamic Public Sentiment Tracking
Track multiple dimensions of public opinion:
- **Safety Focus** - How seriously does the public think you take AI safety?
- **Competence** - Does the public believe you're capable of solving alignment?
- **Trustworthiness** - Do people trust your lab with powerful AI?
- **Media Presence** - How visible is your lab in public discourse?

### 2. Media Cycles & Events
- **News Cycles**: Positive/negative media attention that affects reputation
- **Public Scandals**: High-impact negative events requiring PR response
- **Breakthrough Announcements**: Opportunities to boost reputation via research milestones
- **Media Controversies**: Respond to public debates about AI safety

### 3. PR & Communications System
New actions to manage public opinion:
- **PR Campaign** - Proactive reputation management
- **Crisis Management** - Respond to negative events
- **Media Appearances** - Researcher visibility (requires media-savvy trait)
- **Transparency Reports** - Build trust through openness

### 4. Strategic Integration
Reputation affects:
- **Funding Access**: High reputation unlocks better funding terms
- **Recruitment**: Attracts higher-quality candidates
- **Regulatory Pressure**: Low reputation triggers government scrutiny
- **Rival Dynamics**: Reputation affects competitive interactions

## Strategic Considerations

### When to Prioritize Reputation
- Before major fundraising rounds
- When recruiting top-tier researchers
- After negative events or scandals
- In competitive races with rival labs

### Trade-offs
- **Speed vs. Transparency**: Fast research may sacrifice public trust
- **Safety vs. Capability**: Capability research improves competence perception but may reduce safety focus
- **Media Presence vs. Focus**: Media appearances build reputation but distract from research

## Related Game Systems

- **[Funding System](funding.md)** - Reputation affects investor confidence
- **[Personnel](personnel.md)** - Media-savvy researchers boost reputation
- **[Events](events.md)** - Many events affect public opinion
- **Doom System** - Public pressure can influence p(Doom)

## Implementation Status

**Current State** (v0.10.2):
- ✅ Basic reputation tracking (0-100 score)
- ✅ Reputation gains from papers
- ✅ Reputation loss from leaks/events
- ✅ Media-savvy researcher trait

**In Development** ([Issue #186](https://github.com/PipFoweraker/pdoom1/issues/186)):
- 🚧 Multi-dimensional public sentiment
- 🚧 Media cycle events
- 🚧 PR action system
- 🚧 Strategic integration with funding/recruitment

**Planned Future**:
- ⚪ International reputation (different regions)
- ⚪ Social media dynamics
- ⚪ Journalist relationships
- ⚪ Public debates & controversies

## Developer Notes

### Code References
- **State**: [`godot/scripts/core/game_state.gd:10`](../../godot/scripts/core/game_state.gd#L10) - `var reputation: float = 50.0`
- **Events**: [`godot/scripts/core/events.gd`](../../godot/scripts/core/events.gd) - Event system affecting reputation
- **Actions**: [`godot/scripts/core/actions.gd`](../../godot/scripts/core/actions.gd) - Actions that modify reputation

### Design Documents
- [Public Opinion System Design](../game-design/PUBLIC_OPINION_SYSTEM.md)
- [Issue #186: Public Opinion & Media System](https://github.com/PipFoweraker/pdoom1/issues/186)

---

*Last updated: 2025-11-26 | [Edit this page](https://github.com/PipFoweraker/pdoom1/blob/main/docs/mechanics/reputation.md)*

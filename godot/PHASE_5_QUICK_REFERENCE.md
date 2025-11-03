# Phase 5 Quick Reference Guide

## 🎯 New Player-Facing Features

### New Strategic Actions

#### High-Risk, High-Reward
- **Public Warning** (2 AP, -15 rep) - Random doom reduction 10-25, random rep change ±10
- **Corporate Espionage** ($100k, 3 AP, -20 rep) - 70% success = -20 doom, 30% caught = +10 doom, -25 rep

#### Influence & Lobbying
- **Lobby Government** ($80k, 2 AP, -10 rep) - Reduce doom 8-18 (scales with reputation)
- **Open Source Release** (3 papers, 1 AP) - Share research: -10-20 doom, +15 reputation

#### Economic
- **Grant Proposal** (1 paper, 1 AP) - Government funding: $80k-$250k (scales with reputation)
- **Acquire Startup** ($150k, 2 AP) - Random: +2 safety/cap/compute staff + 30 compute

#### Organizational
- **Emergency Pivot** ($50k, 2 AP) - Convert 1-3 capability researchers to safety
- **Hire AI Ethicist** ($70k, 1 AP) - Add ethicist: +5 reputation
- **Hire Manager** ($80k, 1 AP) - Manages 9 employees, prevents unproductivity

### Employee Productivity System

**Every employee needs TWO things to be productive:**
1. **Compute** (1 compute per employee)
2. **Manager** (1 manager per 9 employees)

**Without compute OR manager = UNPRODUCTIVE**
- No research generation
- +0.5 doom penalty per unproductive employee
- Warning messages each turn

**Example Scenarios:**

**Scenario 1: Sufficient Resources**
```
5 employees, 1 manager, 50 compute
→ All 5 productive ✅
→ Research generation: ~1-2 per turn
→ No doom penalties
```

**Scenario 2: Not Enough Compute**
```
10 employees, 2 managers, 5 compute
→ 5 productive ✅, 5 unproductive ❌
→ Research: ~0-2 per turn (from 5 productive)
→ Doom penalty: +2.5 per turn (5 × 0.5)
→ Need: More compute!
```

**Scenario 3: Not Enough Managers**
```
15 employees, 1 manager, 100 compute
→ 9 productive ✅, 6 unproductive ❌
→ Research: ~1-3 per turn
→ Doom penalty: +3.0 per turn (6 × 0.5)
→ Need: Hire manager! (1 manager only handles 9)
```

**Scenario 4: Both Problems**
```
20 employees, 1 manager, 5 compute
→ Only 5 can be productive (limited by compute AND management)
→ 15 unproductive!
→ Doom penalty: +7.5 per turn 💀
→ Need: Managers AND compute ASAP!
```

### Employee Types & Effects

**Safety Researcher** ($60k)
- Passive: -0.3 doom per turn (if productive)
- Research generation: 30% chance for 1-3 research

**Capability Researcher** ($60k)
- Passive: +0.5 doom per turn (always)
- Research generation: 30% chance for 1-3 research
- ⚠️ Risk/reward: Faster research but increases doom!

**Compute Engineer** ($50k)
- Passive: +10% research efficiency per engineer
- Research generation: 30% chance for 1-3 research

**Manager** ($80k)
- Oversees: 9 employees
- Always productive (doesn't need compute)
- Critical: Prevents unproductivity doom spiral

### New Random Events

**Employee Burnout** (5+ safety researchers)
- Team retreat: $30k → +5 rep, -2 doom
- Salary raises: $50k → +8 rep
- Push through: Free → +3 doom ⚠️

**Rival Poaching** (Random, 8%, turn 10+)
- Counter-offer: $80k → Keep staff
- Let go: -1 safety researcher, +$20k saved

**Media Scandal** (Random, 6%, turn 7+)
- PR campaign: $40k → +10 rep
- Ignore: -8 rep

**Government Regulation** (Doom ≥ 60, one-time)
- Support: $50k, 1 AP → -10 doom, +15 rep ✅
- Oppose: +5 doom, -5 rep
- Neutral: +2 doom

**Technical Failure** (Random, 5%, turn 12+)
- Emergency repair: $60k → +30 compute
- Basic fix: $20k → -20 compute

### Rival AI Labs

**3 Autonomous Competitors:**

**DeepSafety** - Safety-Focused
- Funding: $500k
- Strategy: Prioritizes safety research
- Effect: Helps reduce global doom 👍

**CapabiliCorp** - Aggressive
- Funding: $1M
- Strategy: Rushes capabilities
- Effect: Rapidly increases doom! ⚠️

**StealthAI** - Balanced
- Funding: $300k
- Strategy: Mixed approach
- Effect: Neutral impact

**Each turn, rivals take 1-3 actions:**
- hire_researcher
- buy_compute
- publish_paper
- fundraise
- capability_research (+5 doom!)
- safety_research (-3 doom)

**Strategic Implications:**
- Can't ignore global situation
- CapabiliCorp creates time pressure
- DeepSafety can help you
- Watch their progress in game state

---

## 🎮 Updated Gameplay Loop

### Turn Start
1. ✅ **Management check** - Who has managers?
2. ✅ **Compute distribution** - Who gets compute?
3. ✅ **Productivity evaluation** - Who can work?
4. ✅ **Research generation** - Productive employees contribute
5. ✅ **Passive effects** - Safety reduces doom, caps increase it
6. ✅ **Unproductivity penalties** - Doom from idle staff
7. ✅ **Staff salaries** - $5k per employee
8. ✅ **Random events** - 10 possible events

### Action Phase
1. Select from **18 actions** (10 original + 8 new)
2. Consider risks vs rewards
3. Manage resources (money, compute, AP, reputation)

### Turn End
1. Execute queued actions
2. Auto-publish papers (at 100 research)
3. **Rivals take 1-3 actions each** ⚡
4. Base doom +1.0
5. Capability doom +0.5 per cap researcher
6. Rival doom contribution (varies)
7. Check win/lose

---

## 💡 Strategy Tips

### Early Game (Turns 1-5)
- Hire 2-3 safety researchers
- Buy compute ($50k for 50)
- Keep staff under 9 (avoid manager need)
- Save money for salaries ($5k per employee per turn)

### Mid Game (Turns 6-12)
- **Critical**: Hire manager at 9-10 employees
- Expand to 15-18 employees (hire 2nd manager!)
- Balance safety vs capability researchers
- Buy compute as needed (1 per employee)
- React to events (fundraising opportunities!)

### Late Game (Turns 13+)
- Strategic actions (lobby, warnings, open source)
- Watch rival labs (respond to CapabiliCorp aggression!)
- Emergency pivots if needed
- Final push to doom = 0

### Resource Management
- **Money**: $5k salary per employee per turn
  - 10 employees = $50k/turn maintenance
  - Need steady income (grants, fundraising)

- **Compute**: 1 per productive employee
  - Buy in bulk ($50k for 50 compute)
  - Prioritize over other purchases

- **Action Points**: Base 3 + 0.5 per staff member
  - 10 staff = 8 AP
  - Use wisely (some actions cost 2-3 AP)

### Common Mistakes
❌ Hiring too fast without compute → Unproductivity doom spiral
❌ Ignoring managers past 9 staff → Massive doom penalties
❌ Too many capability researchers → Doom accelerates
❌ Running out of money → Can't pay salaries → Game over
❌ Ignoring rival labs → CapabiliCorp rushes you

### Winning Strategies
✅ Balanced team (60% safety, 20% caps, 20% compute engineers)
✅ Always have 1 compute per employee
✅ Hire managers proactively (at 8 staff, at 17 staff, etc.)
✅ Take calculated risks (warnings, open source releases)
✅ Use grants/fundraising to maintain cash flow
✅ React to events wisely (sometimes short-term pain is worth it)

---

## 🔧 Developer Notes

### File Structure
```
godot/scripts/core/
  ├── game_state.gd      (state + management capacity)
  ├── actions.gd         (18 actions, execution logic)
  ├── events.gd          (10 events, trigger conditions)
  ├── rivals.gd          (3 rival labs, autonomous actions)
  └── turn_manager.gd    (turn flow, productivity system)
```

### Key Functions

**GameState**:
- `get_management_capacity()` - How many employees can be managed
- `get_unmanaged_count()` - How many exceed capacity
- `to_dict()` - Includes rival lab summaries

**TurnManager**:
- `start_turn()` - Productivity evaluation, events
- `execute_turn()` - Player actions, rivals, doom updates

**GameActions**:
- `get_all_actions()` - All 18 actions
- `execute_action()` - Execute with state mutation

**GameEvents**:
- `check_triggered_events()` - Evaluate all triggers
- `evaluate_condition()` - Supports staff conditions now

**RivalLabs**:
- `get_rival_labs()` - Initialize 3 rivals
- `process_rival_turn()` - Autonomous decision-making

### Testing
Run tests with GUT framework:
```bash
godot --run-tests godot/tests/test_phase5_features.gd
```

9 test cases covering all Phase 5 features.

---

## 📈 Balance Tuning

Current values optimized for 15-20 turn games:

**Doom Rates**:
- Base: +1.0/turn
- Per capability researcher: +0.5/turn
- Per unproductive employee: +0.5/turn
- Per safety researcher: -0.3/turn (if productive)
- Rival contributions: -10 to +20/turn (varies by actions)

**Research Generation**:
- 30% chance per productive employee
- 1-3 points per contribution
- +10% per compute engineer
- Auto-publish at 100 research

**Costs**:
- Researchers: $50-80k
- Actions: $10-150k
- Maintenance: $5k per employee per turn

**If games too easy**: Increase rival aggression or base doom rate
**If games too hard**: Reduce unproductivity doom penalty or increase starting money

---

## 🎊 Phase 5 Complete!

**Total Additions**:
- 8 new actions
- 5 new events
- 3 rival labs
- Full productivity system
- Manager mechanics
- 9 test cases
- Comprehensive documentation

**Lines of Code**: ~1,500 lines of GDScript
**Development Time**: Single session (2025-10-31)
**Architecture**: Native Godot, no Python bridge

**Ready for**: UI integration, playtesting, balance refinement

🚀 **The game is now feature-complete for core gameplay!** 🚀

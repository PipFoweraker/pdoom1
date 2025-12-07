# Godot Phase 5: Native Game Logic Expansion

**Status**: SUCCESS Complete
**Date**: 2025-10-31
**Focus**: Native Godot/GDScript implementation, Python prototype archived

## TARGET Phase 5 Goals

Move away from Python bridge architecture and build all game logic natively in Godot for:
- Faster iteration cycles
- Simpler debugging
- Better performance
- Native Godot integration

## SUCCESS What Was Built

### 1. Python Prototype Archived
**Location**: `legacy/shared/`

The original Python game logic has been moved to `legacy/` as reference material. It served its purpose as a prototype but added unnecessary complexity.

**Why Archived**:
- Bridge architecture was over-engineered
- Godot is now the primary engine
- GDScript provides all needed functionality
- Simpler to maintain one codebase

### 2. Expanded Actions System (18 Actions)
**File**: `godot/scripts/core/actions.gd`

Added 8 new strategic actions for depth and variety:

**New Actions**:
1. **Lobby Government** ($80k, 2 AP) - Advocate for AI safety regulation
2. **Public Warning** (2 AP, -15 rep) - Risky but impactful doom reduction
3. **Acquire AI Startup** ($150k, 2 AP) - Buy struggling startup for talent/compute
4. **Corporate Espionage** ($100k, 3 AP, -20 rep) - Sabotage competitors (unethical!)
5. **Open Source Release** (3 papers, 1 AP) - Share research globally
6. **Emergency Pivot** ($50k, 2 AP) - Convert capability researchers to safety
7. **Grant Proposal** (1 paper, 1 AP) - Apply for government funding
8. **Hire AI Ethicist** ($70k, 1 AP) - Add philosophical perspective

**Total Actions**: 18 (10 original + 8 new)

**Key Features**:
- Risk/reward tradeoffs (sabotage can backfire!)
- Reputation management
- Strategic pivots
- Ethical dilemmas

### 3. Employee Productivity System
**Files**: `godot/scripts/core/turn_manager.gd`, `godot/scripts/core/game_state.gd`

Implemented full productivity system based on Python prototype (lines 1208-1372):

**Core Mechanics**:

1. **Management Capacity**
   - Base capacity: 9 employees (before first manager)
   - Each manager: handles 9 employees
   - Unmanaged employees: 0 productivity + doom penalty

2. **Compute Distribution**
   - Each productive employee needs 1 compute
   - Without compute: 0 productivity + doom penalty

3. **Research Generation**
   - 30% chance per productive employee per turn
   - Base research: 1-3 points (random)
   - Compute engineer bonus: +10% per engineer

4. **Safety Researcher Benefits**
   - Passive doom reduction: 0.3 per safety researcher per turn
   - Only applies if employee is productive (has compute + manager)

5. **Capability Researcher Penalties**
   - Increase doom: 0.5 per capability researcher per turn
   - Risk vs reward balance

6. **Unproductivity Doom Penalty**
   - 0.5 doom per unproductive employee
   - Encourages compute investment and manager hiring

**Example Turn**:
```gdscript
# 10 employees, 1 manager, 50 compute
# Managed: 9 employees (1 unmanaged)
# Productive: 9 employees (50 compute covers all 9)
# Unproductive: 1 (lacks manager)

# Research: ~2-3 per turn from 9 employees (30% chance each)
# Doom from unproductive: +0.5
# Need: 2nd manager to cover all 10!
```

### 4. Manager Hiring System
**Files**: `godot/scripts/core/actions.gd`, `godot/scripts/core/game_state.gd`

Added manager as 4th employee type:

**Manager Stats**:
- Cost: $80,000 + 1 AP
- Capacity: Oversees 9 employees
- Effect: Prevents unproductivity doom penalties

**New State Variables**:
```gdscript
var managers: int = 0

func get_management_capacity() -> int
func get_unmanaged_count() -> int
```

**Strategic Implications**:
- Must hire managers as team grows
- Timing decision: When to invest in management?
- Scales with team size (need more managers for larger teams)

### 5. Enhanced Random Events System
**File**: `godot/scripts/core/events.gd`

Added 5 new events for variety and strategic decisions:

**New Events**:

1. **Employee Burnout Crisis**
   - Trigger: 5+ safety researchers
   - Choices: Team retreat ($30k), raises ($50k), or push through (+3 doom)

2. **Rival Lab Poaching**
   - Trigger: Random (8% chance, turn 10+)
   - Choices: Counter-offer ($80k) or let them go (-1 researcher, +$20k)

3. **Media Scandal**
   - Trigger: Random (6% chance, turn 7+)
   - Choices: PR campaign ($40k, +10 rep) or ignore (-8 rep)

4. **Government Regulation**
   - Trigger: Doom >= 60 (one-time)
   - Choices: Support ($50k, -10 doom), oppose (+5 doom), or neutral (+2 doom)

5. **Technical Failure**
   - Trigger: Random (5% chance, turn 12+)
   - Choices: Emergency repair ($60k, +30 compute) or basic fix ($20k, -20 compute)

**Total Events**: 10 (5 original + 5 new)

**Event System Features**:
- Three trigger types: random, threshold, turn_and_resource
- Repeatable vs one-time events
- Multi-choice outcomes
- Staff condition evaluation (e.g., `safety_researchers >= 5`)

### 6. Rival AI Labs System
**File**: `godot/scripts/core/rivals.gd`

Built autonomous competitor simulation:

**The 3 Rival Labs**:

1. **DeepSafety**
   - Funding: $500k
   - Reputation: 70
   - Aggression: 0.3 (cautious, safety-focused)
   - Strategy: Prioritizes safety research

2. **CapabiliCorp**
   - Funding: $1M
   - Reputation: 60
   - Aggression: 0.9 (very aggressive)
   - Strategy: Rushes capabilities research (increases global doom!)

3. **StealthAI**
   - Funding: $300k
   - Reputation: 40
   - Aggression: 0.5 (balanced)
   - Strategy: Mixed approach

**Rival Actions Per Turn**:
- 1-3 actions based on funding level
- Actions: hire_researcher, buy_compute, publish_paper, fundraise, capability_research, safety_research
- Each action affects global doom counter
- Deterministic (seeded RNG for reproducibility)

**Doom Contributions**:
- Capability research: +5 doom (dangerous!)
- Safety research: -3 doom (helpful!)
- Aggressive rivals push doom up
- Safety-focused rivals help reduce doom

**Strategic Implications**:
- Can't ignore global AI landscape
- Aggressive rivals create time pressure
- Must balance your own research with global situation
- Emergent narratives (e.g., "CapabiliCorp is rushing ahead!")

### 7. Comprehensive Test Suite
**File**: `godot/tests/test_phase5_features.gd`

Created 9 test cases covering:
- Expanded actions verification
- Manager system capacity calculations
- Employee productivity mechanics
- Rival lab initialization
- Event system with staff conditions
- Full turn integration

## METRICS Game Balance Summary

**Starting Resources**:
- Money: $100,000
- Compute: 100
- Doom: 50%
- Base AP: 3

**Key Costs**:
- Safety Researcher: $60,000
- Capability Researcher: $60,000
- Compute Engineer: $50,000
- Manager: $80,000
- Compute Purchase: $50,000 for 50 compute

**Maintenance Costs**:
- Staff salary: $5,000 per employee per turn
- Management capacity: 9 employees per manager

**Win Condition**: Doom reaches 0%
**Lose Conditions**: Doom reaches 100% OR Reputation reaches 0%

## 🎮 Gameplay Loop (Phase 5)

**Turn Start**:
1. Employee productivity evaluated (compute + management)
2. Research generated from productive employees
3. Safety researchers reduce doom passively
4. Unproductive employees increase doom
5. Staff salaries paid
6. Random events may trigger (10 possible events)

**Action Phase**:
1. Player selects from 18 actions
2. Strategic decisions (hire, research, influence)
3. Risk management (sabotage? warnings?)

**Turn End**:
1. Queued actions execute
2. Papers auto-publish at 100 research
3. **Rival labs take 1-3 actions each**
4. Base doom increase (+1.0)
5. Capability doom increase (+0.5 per capability researcher)
6. Rival doom contribution (varies by rival actions)
7. Win/lose check

## REFRESH Changes from Python Prototype

**Removed**:
- ERROR Python bridge architecture
- ERROR IGameEngine interface
- ERROR ActionsEngine / EventsEngine classes
- ERROR Complex employee blob system
- ERROR Productive actions effectiveness bonuses
- ERROR Specialist researcher traits

**Kept (Simplified)**:
- SUCCESS Core productivity formulas (30% chance, 1-3 research)
- SUCCESS Management capacity (9 per manager)
- SUCCESS Compute distribution (1 per employee)
- SUCCESS Unproductivity doom penalties (0.5 per employee)
- SUCCESS Random events system
- SUCCESS Rival labs concept

**Added (New)**:
- SUCCESS 8 strategic actions (lobby, sabotage, pivot, etc.)
- SUCCESS Rival labs with personalities and autonomous actions
- SUCCESS 5 new random events
- SUCCESS Manager as distinct employee type
- SUCCESS Simplified GDScript implementation

## LAUNCH What's Next (Phase 6 Ideas)

**Potential Improvements**:
1. **UI Polish** - Better visualization of:
   - Employee productivity status
   - Rival lab progress bars
   - Event notifications

2. **Advanced Employee System**:
   - Specialist traits (workaholic, prima donna, etc.)
   - Burnout mechanic
   - Individual productivity modifiers

3. **Tech Tree**:
   - Unlock actions based on progress
   - Research branches
   - Upgrade paths

4. **Scenario System**:
   - Different starting conditions
   - Custom challenge scenarios
   - Story mode

5. **Multiplayer Leaderboards**:
   - Integrate with pdoom1-website
   - Seed-based competition
   - Score tracking

## MEMO Design Notes

### Why Native Godot?

The Python bridge was architecturally interesting but practically problematic:
- Required maintaining two codebases (Python + GDScript)
- Complicated debugging (which layer has the bug?)
- Performance overhead from cross-language calls
- Over-engineered for actual needs

**Native Godot is better because**:
- Single source of truth
- Faster iteration (change code, test immediately)
- Better performance (no bridge overhead)
- Simpler mental model
- Full access to Godot features

### Balancing Philosophy

**Core Loop**: Hire staff  ->  Need compute  ->  Need managers  ->  Need money  ->  Make strategic choices

**Tension Sources**:
1. **Resource scarcity**: Limited money, compute, AP
2. **Time pressure**: Rivals advancing, base doom increase
3. **Risk/reward**: Unethical actions (sabotage) vs safe plays
4. **Staff management**: Productivity requires compute + management
5. **Global doom**: Can't ignore what rivals are doing

**Victory Strategy**:
- Hire balanced team (safety + support staff)
- Manage productivity (compute + managers)
- Take calculated risks (warnings, lobbying)
- React to events smartly
- Race against rivals

## TARGET Implementation Quality

**Code Quality**:
- SUCCESS Deterministic (seeded RNG for reproducibility)
- SUCCESS Well-documented (comments explain formulas)
- SUCCESS Modular (actions, events, rivals separate)
- SUCCESS Testable (comprehensive test suite)
- SUCCESS Based on Python prototype (proven design)

**Balance Quality**:
- SUCCESS Multiple viable strategies
- SUCCESS Meaningful choices
- SUCCESS Risk/reward tradeoffs
- SUCCESS Time pressure from rivals
- SUCCESS Recovery mechanisms (grants, fundraising)

**Architecture Quality**:
- SUCCESS Native Godot (no bridge complexity)
- SUCCESS Clean separation of concerns
- SUCCESS Easy to extend (add actions, events, rivals)
- SUCCESS Performance-friendly (no unnecessary abstractions)

---

## 🎊 Summary

Phase 5 successfully transformed P(Doom) from a Python prototype with bridge architecture into a **fully native Godot game** with:

- **18 strategic actions** with risk/reward decisions
- **Complete employee productivity system** (compute, management, research generation)
- **10 random events** with meaningful choices
- **3 autonomous rival labs** competing in real-time
- **Comprehensive test coverage**

The game is now **ready for rapid iteration** with a solid foundation for future features. The native Godot implementation makes development faster, debugging simpler, and the architecture cleaner.

**Next session**: Focus on UI polish, playtesting, and balance refinement! 🎮

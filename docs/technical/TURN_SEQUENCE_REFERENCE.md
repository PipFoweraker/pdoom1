# Turn Sequence Reference - Complete Technical Documentation

**Version:** 1.0 (Godot 4.5.1 Implementation)
**Last Updated:** 2025-11-17
**Status:** CURRENT - Reflects production implementation

---

## Turn Philosophy: The "Monday Planning" Metaphor

**Core Concept:** Each turn represents planning a week of work at your AI safety lab.

**The Weekly Cycle:**
1. **Monday Morning** (TURN_START): Survey the week ahead, events arrive, refresh resources
2. **Planning Phase** (ACTION_SELECTION): Decide what to accomplish this week, queue actions
3. **Reserve Slack**: Keep some Action Points available for chaos/opportunities that arise
4. **Commit Plan**: Lock in your strategy (Enter) or execute immediately (Space)
5. **Week Unfolds** (TURN_EXECUTION): Actions execute, events may occur, competitors act
6. **Next Monday**: Repeat with new information

**Strategic Implications:**
- **Empty queue is valid**: Reserving all AP for reactive responses is a legitimate strategy
- **Planned actions** (future): Will cost less AP than improvised responses to events
- **Slack management**: Like real planning, balancing structure vs. flexibility is key
- **Commitment timing**: Monday planning = low stress; mid-week improvisation = higher cost

---

## Quick Reference

### Turn Phases (Enum)
```gdscript
enum TurnPhase {
    TURN_START,         # Events trigger, resources refresh (Monday morning)
    ACTION_SELECTION,   # Player plans the week, queues actions
    TURN_EXECUTION      # Week unfolds, actions execute, doom calculated
}
```

### Complete Turn Cycle
```
MONDAY PLANNING  ->  [Events?]  ->  PLAN YOUR WEEK  ->  COMMIT & EXECUTE  ->  NEXT MONDAY
      v                v                v                    v 
  Phase 1        Resolve      Queue actions     Week unfolds
  (automatic)    (manual)      (manual)         (automatic)
```

---

## Phase 1: TURN_START (Automatic)

**Entry Point:** `TurnManager.start_turn()`
**File:** [turn_manager.gd:10-119](../godot/scripts/core/turn_manager.gd#L10-L119)

### 1.1 Initialization
```gdscript
state.turn += 1
state.current_phase = GameState.TurnPhase.TURN_START
state.pending_events.clear()
state.queued_actions.clear()
state.can_end_turn = false
```

**Logic:**
- Increment turn counter
- Reset phase to TURN_START
- Clear any stale events/actions from previous turn
- Block turn ending until events resolved or no events present

---

### 1.2 Action Points Calculation
```gdscript
var total_staff = state.get_total_staff()
var max_ap = 3 + int(total_staff * 0.5)
state.action_points = max_ap
state.reset_turn_ap()
```

**Formula:**
- Base AP: **3**
- Staff Bonus: **+0.5 AP per staff member** (rounded down)

**Examples:**
| Staff Count | Base | Bonus | Total AP |
|-------------|------|-------|----------|
| 0           | 3    | 0     | 3        |
| 2           | 3    | 1     | 4        |
| 6           | 3    | 3     | 6        |
| 10          | 3    | 5     | 8        |

**Reserve System (Future Feature):**
```gdscript
func reset_turn_ap():
    committed_ap = 0   # AP spent on queued actions
    reserved_ap = 0    # AP held for events
    used_event_ap = 0  # AP spent on event responses
```

---

### 1.3 Researcher Turn Processing
```gdscript
for researcher in state.researchers:
    researcher.process_turn()
```

**Per-Researcher Processing:** [researcher.gd:180-245](../godot/scripts/core/researcher.gd#L180-L245)

1. **Burnout Decay:**
   - Burnout decreases by 2-5 points per turn
   - Faster recovery if loyalty > 70

2. **Skill Growth:**
   - 10% chance to gain 1 skill point (max 10)
   - Based on productivity and base_productivity

3. **Loyalty Changes:**
   - Increases if well-paid (salary >= expectation)
   - Decreases if underpaid or burned out

4. **Turns Employed:**
   - Increment `turns_employed` counter
   - Used for poaching risk and promotion eligibility

---

### 1.4 Staff Salary Costs
```gdscript
var total_staff = state.get_total_staff()
var staff_salaries = total_staff * 5000  # $5k per employee per turn
if staff_salaries > 0:
    state.add_resources({"money": -staff_salaries})
```

**Salary Formula:**
- **$5,000 per employee per turn** (fixed rate)
- Applies to ALL staff: researchers, engineers, managers

**Budget Planning:**
| Staff | Salary/Turn | Salary/10 Turns |
|-------|-------------|-----------------|
| 5     | $25,000     | $250,000        |
| 10    | $50,000     | $500,000        |
| 20    | $100,000    | $1,000,000      |

---

### 1.5 Employee Productivity System

**Critical Constraint:** Employees need **both** management AND compute to be productive

#### 1.5.1 Management Capacity Check
```gdscript
var non_manager_staff = state.safety_researchers +
                        state.capability_researchers +
                        state.compute_engineers

var management_capacity = state.get_management_capacity()
var managed_employees = min(non_manager_staff, management_capacity)
var unmanaged_employees = state.get_unmanaged_count()
```

**Management Capacity Formula:**
```gdscript
func get_management_capacity() -> int:
    if managers == 0:
        return 9  # Base capacity before first manager
    return managers * 9  # Each manager handles 9 employees
```

**Example:**
| Managers | Capacity | With 15 Staff | Managed | Unmanaged |
|----------|----------|---------------|---------|-----------|
| 0        | 9        | 15            | 9       | 6         |
| 1        | 9        | 15            | 9       | 6         |
| 2        | 18       | 15            | 15      | 0         |

---

#### 1.5.2 Compute Distribution
```gdscript
var available_compute = int(state.compute)
var productive_employees = min(managed_employees, available_compute)
```

**Constraint:** Each productive employee requires **1 compute unit**

**Example Scenario:**
- 15 total staff
- 2 managers (capacity = 18)
- 10 compute units available

Result:
- 15 managed (all have management)
- 10 productive (limited by compute)
- 5 unproductive (no compute, despite having management)

---

#### 1.5.3 Research Generation
```gdscript
var research_from_employees = 0.0
for i in range(productive_employees):
    if state.rng.randf() < 0.30:  # 30% chance per employee
        var base_research = state.rng.randi_range(1, 3)
        research_from_employees += base_research
```

**Research Generation:**
- **30% chance** per productive employee
- **1-3 research points** per trigger (random)

**Expected Value:**
- Per productive employee: `0.30 x 2 = 0.6 research/turn`
- 10 productive employees: ~6 research/turn (average)

---

#### 1.5.4 Compute Engineer Bonus
```gdscript
var compute_efficiency_bonus = 1.0 + (state.compute_engineers * 0.1)
research_from_employees *= compute_efficiency_bonus
```

**Multiplier:** +10% effectiveness per compute engineer

**Example:**
- 3 compute engineers = 1.3x multiplier
- Base research: 6.0
- Final research: 6.0 x 1.3 = **7.8**

---

#### 1.5.5 Safety Researcher Doom Reduction
```gdscript
var productive_safety = min(state.safety_researchers, productive_employees)
var doom_reduction_from_safety = productive_safety * 0.3
state.add_resources({"doom": -doom_reduction_from_safety})
```

**Passive Doom Reduction:**
- **-0.3 doom per productive safety researcher** (automatic, every turn)
- Only productive safety researchers count

**Example:**
- 5 total safety researchers
- 3 are productive (have management + compute)
- Doom reduction: 3 x 0.3 = **-0.9 doom/turn**

---

#### 1.5.6 Unproductive Employee Doom Penalty
```gdscript
var total_unproductive = (non_manager_staff - productive_employees) + unmanaged_employees
if total_unproductive > 0:
    var doom_penalty = total_unproductive * 0.5
    state.add_resources({"doom": doom_penalty})
```

**Doom Penalty:**
- **+0.5 doom per unproductive employee**
- Unproductive = no compute OR no manager

**Scenario:**
- 15 staff total
- 0 managers  ->  6 unmanaged (9 capacity exceeded)
- 10 compute units  ->  5 without compute
- Total unproductive: 6 + 5 = 11
- Doom penalty: 11 x 0.5 = **+5.5 doom/turn** WARNING

**Key Insight:** Hiring staff without proper infrastructure is DANGEROUS!

---

### 1.6 Event Triggering
```gdscript
var triggered_events = GameEvents.check_triggered_events(state, state.rng)

if triggered_events.size() > 0:
    state.pending_events = triggered_events
    state.current_phase = GameState.TurnPhase.TURN_START  # Stay in TURN_START
    state.can_end_turn = false
else:
    state.current_phase = GameState.TurnPhase.ACTION_SELECTION
    state.can_end_turn = true
```

**Critical Design (FIX #418):**
- Events trigger **BEFORE** action selection
- Player sees events **before** committing AP to actions
- Turn phase remains TURN_START until all events resolved

**Event Flow:**
```
Events triggered?
    |-- YES  ->  Show events  ->  Block action selection  ->  Wait for player
    `-- NO   ->  Immediately allow action selection
```

---

## Phase 2: Event Resolution (Manual, if events present)

**Entry Point:** `TurnManager.resolve_event(event, choice_id)`
**File:** [turn_manager.gd:228-265](../godot/scripts/core/turn_manager.gd#L228-L265)

### 2.1 Event Choice Execution
```gdscript
var result = GameEvents.execute_event_choice(event, choice_id, state)
```

**Event Choice Processing:** [events.gd](../godot/scripts/core/events.gd)
- Apply costs (money, AP, resources)
- Apply effects (doom, reputation, etc.)
- Generate result message

---

### 2.2 Pending Events Management
```gdscript
# Remove resolved event from pending queue
var event_id = event.get("id", "")
var new_pending: Array[Dictionary] = []
for pending in state.pending_events:
    if pending.get("id", "") != event_id:
        new_pending.append(pending)
state.pending_events = new_pending
```

---

### 2.3 Phase Transition Check
```gdscript
if state.pending_events.size() == 0:
    state.current_phase = GameState.TurnPhase.ACTION_SELECTION
    state.can_end_turn = true
    result["phase_transitioned"] = true
    result["new_phase"] = "action_selection"
```

**Phase Transition:**
- **All events resolved**  ->  Transition to ACTION_SELECTION
- **Events remaining**  ->  Stay in TURN_START, show next event

---

## Phase 3: ACTION_SELECTION (Manual)

**Entry Point:** Player UI
**File:** [main_ui.gd](../godot/scripts/ui/main_ui.gd)

### 3.1 Available Actions Query
```gdscript
var available = TurnManager.get_available_actions()
```

**Action Filtering:**
```gdscript
for action in all_actions:
    var can_afford = state.can_afford(action["costs"])
    action_copy["affordable"] = can_afford
    available.append(action_copy)
```

---

### 3.2 Action Queueing
**UI Flow:**
1. Player clicks action button
2. Check affordability (AP + resources)
3. Add to `state.queued_actions`
4. Deduct `committed_ap`
5. Update UI

**AP Tracking:**
```gdscript
var available_ap = state.action_points - state.committed_ap - state.reserved_ap
```

---

### 3.3 Special Actions

#### Pass Turn (Virtual Action)
```gdscript
// Created by "Commit Plan (Enter)" button
{
    "id": "pass_turn",
    "name": "Reserve All AP",
    "description": "Commit plan with all AP reserved for reactive responses",
    "ap_cost": 0,
    "money_cost": 0
}
```

**Purpose:** Allows turn advancement with empty queue
**Implementation:** [actions.gd:225-227](../godot/scripts/core/actions.gd#L225-L227)

---

## Phase 4: TURN_EXECUTION (Automatic)

**Entry Point:** `GameManager.end_turn()`  ->  `TurnManager.execute_turn()`
**File:** [turn_manager.gd:121-226](../godot/scripts/core/turn_manager.gd#L121-L226)

### 4.1 Action Execution
```gdscript
for action_id in state.queued_actions:
    var result = GameActions.execute_action(action_id, state)
    results.append(result)
```

**Processing:**
- Execute actions in queue order (FIFO)
- Apply costs and effects
- Collect result messages

---

### 4.2 Paper Publication Check
```gdscript
if state.research >= 100:
    var papers_to_publish = int(state.research / 100)
    state.papers += papers_to_publish
    state.research = fmod(state.research, 100)  # Keep remainder
    state.add_resources({"reputation": papers_to_publish * 5})
```

**Paper Mechanics:**
- **100 research = 1 paper**
- Each paper grants **+5 reputation**
- Excess research carries over

**Example:**
- 245 research accumulated
- Publish 2 papers (200 research consumed)
- +10 reputation
- 45 research remains

---

### 4.3 Rival Lab Actions
```gdscript
for rival in state.rival_labs:
    var rival_result = RivalLabs.process_rival_turn(rival, state, state.rng)
    rival_doom_contribution += rival_result["doom_contribution"]
```

**Rival Processing:** [rival_labs.gd](../godot/scripts/core/rival_labs.gd)
- Each rival takes 1-3 actions
- Actions contribute to global doom
- Rival progress affects reputation and doom

---

### 4.4 Doom Calculation (Momentum System)
```gdscript
state.doom_system.set_rival_doom_contribution(rival_doom_contribution)
var doom_result = state.doom_system.calculate_doom_change(state)
state.doom = state.doom_system.current_doom
```

**Doom Calculation Flow:** [doom_system.gd:253-382](../godot/scripts/core/doom_system.gd#L253-L382)

#### 4.4.1 Collect Doom Sources
```gdscript
doom_sources = {
    "safety_research": -X,      # From player safety actions
    "capability_research": +Y,   # From player capability actions
    "rival_labs": +Z,            # From rival contributions
    "employee_productivity": +/-W, # From productive/unproductive staff
    "base_increase": +1.0,       # Constant pressure
    "momentum": +/-M               # Doom momentum effect
}
```

---

#### 4.4.2 Calculate Total Change
```gdscript
var total_change = 0.0
for source in doom_sources:
    total_change += doom_sources[source]
```

---

#### 4.4.3 Apply Doom Momentum
**Momentum System:** Doom has "inertia" - changes accelerate in the same direction

```gdscript
# Update velocity (rate of change)
doom_velocity = 0.7 * doom_velocity + 0.3 * total_change

# Momentum contribution
doom_momentum = doom_velocity * 0.3

# Add momentum to total change
total_change += doom_momentum
```

**Momentum Effect:**
- Doom increasing  ->  Momentum makes it increase faster
- Doom decreasing  ->  Momentum helps it decrease faster
- Creates strategic "turning points" where reversing trends is hard

**Example:**
| Turn | Action Effect | Velocity | Momentum | Total Change | Doom |
|------|---------------|----------|----------|--------------|------|
| 1    | +2.0          | +0.6     | +0.18    | +2.18        | 52.2 |
| 2    | +2.0          | +1.02    | +0.31    | +2.31        | 54.5 |
| 3    | +2.0          | +1.41    | +0.42    | +2.42        | 56.9 |
| 4    | -3.0 (pivot!) | +0.09    | +0.03    | -2.97        | 53.9 |
| 5    | -3.0          | -0.83    | -0.25    | -3.25        | 50.7 |

**Strategic Insight:** Early intervention is crucial - momentum makes late-game pivots harder!

---

#### 4.4.4 Doom Boundaries
```gdscript
current_doom = clamp(current_doom + total_change, 0.0, 100.0)
```

**Constraints:**
- Minimum: **0.0** (victory condition)
- Maximum: **100.0** (game over condition)

---

### 4.5 Win/Lose Check
```gdscript
state.check_win_lose()

if state.game_over:
    if state.victory:
        # Doom reached 0
    else:
        # Doom = 100 OR Reputation = 0
```

**Game Over Conditions:**
- **Victory:** doom <= 0
- **Defeat:** doom >= 100 OR reputation <= 0

---

## Action Point Reserve System (Future)

**Status:** Designed but not fully implemented
**Reference:** [TURN_STRUCTURE_AP_DESIGN.md](../godot/TURN_STRUCTURE_AP_DESIGN.md)

### Reserve Mechanic Overview
```gdscript
// Player can reserve AP for event responses
state.reserved_ap = 2       // Hold 2 AP for events
state.committed_ap = 1      // Use 1 AP for actions
// Total: 3 AP

// When event triggers:
event_option["costs"]["action_points"] = 2
if state.get_event_ap() >= 2:
    // Can afford powerful event option
```

**Strategic Trade-off:**
- Reserve AP  ->  Can take powerful event options
- Commit all AP  ->  Maximum guaranteed actions, but miss event opportunities

---

## Complete Turn Sequence Diagram

```
+---------------------------------------------------------------+
| TURN START (Phase 1 - Automatic)                            |
|---------------------------------------------------------------|
| 1. Increment turn counter                                   |
| 2. Calculate AP (3 + 0.5 per staff)                         |
| 3. Process researchers (burnout, skill, loyalty)            |
| 4. Pay staff salaries ($5k per employee)                    |
| 5. Employee productivity:                                   |
|    |-- Check management capacity                             |
|    |-- Distribute compute                                    |
|    |-- Generate research (30% chance per productive emp)     |
|    |-- Apply compute engineer bonus                          |
|    |-- Safety researchers reduce doom (-0.3 each)            |
|    `-- Unproductive employees increase doom (+0.5 each)      |
| 6. Check for triggered events                               |
|    |-- Events present?  ->  Stay in TURN_START                  |
|    `-- No events?  ->  Transition to ACTION_SELECTION           |
`---------------------------------------------------------------`
                           v 
+---------------------------------------------------------------+
| EVENT RESOLUTION (Phase 2 - Manual, if events triggered)    |
|---------------------------------------------------------------|
| FOR EACH pending event:                                     |
|   1. Show event to player                                   |
|   2. Player selects choice                                  |
|   3. Execute choice (apply costs and effects)               |
|   4. Remove from pending queue                              |
|                                                              |
| ALL events resolved?                                        |
|   `-- YES  ->  Transition to ACTION_SELECTION                   |
`---------------------------------------------------------------`
                           v 
+---------------------------------------------------------------+
| ACTION SELECTION (Phase 3 - Manual)                         |
|---------------------------------------------------------------|
| LOOP until player ends turn:                                |
|   1. Show available actions                                 |
|   2. Player queues action                                   |
|   3. Deduct committed_ap                                    |
|   4. Update UI (show queue, remaining AP)                   |
|                                                              |
| Player commits plan: "End Turn" or "Commit Plan & Reserve AP"|
|   |-- End Turn (Space): Execute queued actions               |
|   `-- Commit Plan (Enter): Queue "pass_turn" (reserve all AP)|
|                                                              |
| Transition to TURN_EXECUTION                                |
`---------------------------------------------------------------`
                           v 
+---------------------------------------------------------------+
| TURN EXECUTION (Phase 4 - Automatic)                        |
|---------------------------------------------------------------|
| 1. Execute queued actions (in order)                        |
|    `-- Apply costs, apply effects, record results            |
|                                                              |
| 2. Check for paper publication                              |
|    `-- Research >= 100  ->  Publish papers (+5 rep each)         |
|                                                              |
| 3. Process rival lab actions                                |
|    `-- Each rival takes 1-3 actions                          |
|    `-- Calculate rival doom contribution                     |
|                                                              |
| 4. Calculate doom change (Momentum System)                  |
|    |-- Collect sources (safety, capability, rivals, etc.)    |
|    |-- Calculate total change                                |
|    |-- Update doom velocity                                  |
|    |-- Calculate momentum contribution                       |
|    |-- Apply total change to doom                            |
|    `-- Clamp doom to [0, 100]                                |
|                                                              |
| 5. Check win/lose conditions                                |
|    |-- Victory: doom <= 0                                     |
|    `-- Defeat: doom >= 100 OR reputation <= 0                  |
|                                                              |
| Turn complete  ->  Loop back to TURN START (Phase 1)           |
`---------------------------------------------------------------`
```

---

## Key Implementation Files

| File | Purpose | Lines |
|------|---------|-------|
| [turn_manager.gd](../godot/scripts/core/turn_manager.gd) | Turn sequence orchestration | 279 |
| [game_state.gd](../godot/scripts/core/game_state.gd) | State management, AP tracking | 420+ |
| [actions.gd](../godot/scripts/core/actions.gd) | Action definitions and execution | 416 |
| [doom_system.gd](../godot/scripts/core/doom_system.gd) | Doom calculation with momentum | 440+ |
| [events.gd](../godot/scripts/core/events.gd) | Event triggering and resolution | 300+ |
| [researcher.gd](../godot/scripts/core/researcher.gd) | Individual researcher mechanics | 320+ |
| [rival_labs.gd](../godot/scripts/core/rival_labs.gd) | Rival lab behavior | 200+ |
| [main_ui.gd](../godot/scripts/ui/main_ui.gd) | Player interface for action selection | 1200+ |

---

## Testing Considerations

### Determinism Requirements
All turn processing must be deterministic given the same:
- Game state
- RNG seed
- Player actions

**Critical for:**
- Replay systems
- Multiplayer (future)
- Bug reproduction
- Balance testing

### Test Scenarios

#### 1. Employee Productivity Edge Cases
```gdscript
# Scenario: More staff than compute and management
# Expected: Only min(managed, compute) are productive
var state = GameState.new()
state.safety_researchers = 10
state.managers = 0  # Capacity = 9
state.compute = 5

# Expected productive: min(9, 5) = 5
# Expected unproductive: 10 - 5 = 5
# Doom penalty: 5 x 0.5 = +2.5
```

#### 2. Event-Action Phase Transition
```gdscript
# Scenario: Event triggers, must resolve before actions
# Expected: Phase stays TURN_START until event resolved

start_turn()
assert(state.current_phase == TurnPhase.TURN_START)
assert(state.pending_events.size() > 0)
assert(state.can_end_turn == false)

resolve_event(event, choice)
assert(state.current_phase == TurnPhase.ACTION_SELECTION)
assert(state.can_end_turn == true)
```

#### 3. Doom Momentum Acceleration
```gdscript
# Scenario: Sustained doom increase accelerates due to momentum
# Expected: Later turns have larger doom increases

var doom_changes = []
for turn in range(5):
    # Same action each turn (+2 doom base)
    execute_action("capability_research")
    doom_changes.append(state.doom - previous_doom)

# Verify momentum causes acceleration
assert(doom_changes[4] > doom_changes[0])
```

---

## Future Enhancements

### 1. Event AP Reserve System
**Status:** Designed, not implemented
**Priority:** Medium
**Complexity:** High

Add explicit AP reservation for event responses, creating strategic trade-offs.

### 2. Multi-Turn Action Queueing
**Status:** Not designed
**Priority:** Low
**Complexity:** Very High

Allow queueing actions across multiple turns (e.g., "Research project: 3 turns").

### 3. Action Cancellation/Reordering
**Status:** Not designed
**Priority:** Low
**Complexity:** Medium

Allow editing action queue before committing turn.

### 4. Conditional Actions
**Status:** Not designed
**Priority:** Low
**Complexity:** Very High

Execute actions based on conditions (e.g., "If doom > 60, do safety research").

---

## Appendix: Formulas Reference

### Action Points
```
AP = 3 + floor(total_staff x 0.5)
```

### Staff Salaries
```
Salary = total_staff x $5,000
```

### Management Capacity
```
Capacity = managers == 0 ? 9 : managers x 9
```

### Productive Employees
```
Productive = min(managed_employees, available_compute)
where managed_employees = min(non_manager_staff, management_capacity)
```

### Research Generation
```
Expected research = productive_employees x 0.3 x 2.0 x (1.0 + compute_engineers x 0.1)
```

### Doom from Safety Researchers
```
Doom reduction = productive_safety_researchers x 0.3 per turn
```

### Doom from Unproductive Employees
```
Doom penalty = unproductive_employees x 0.5 per turn
```

### Doom Momentum
```
velocity(t) = 0.7 x velocity(t-1) + 0.3 x change(t)
momentum(t) = velocity(t) x 0.3
total_doom_change(t) = base_change(t) + momentum(t)
```

### Paper Publication
```
Papers published = floor(research / 100)
Reputation gain = papers_published x 5
Remaining research = research mod 100
```

---

**End of Document**

*For questions or clarifications, see:*
- [TURN_STRUCTURE_AP_DESIGN.md](../godot/TURN_STRUCTURE_AP_DESIGN.md) - AP reserve system design
- [TURN_SEQUENCING_FIX.md](../docs/game-design/TURN_SEQUENCING_FIX.md) - Event ordering fix documentation
- [turn_manager.gd](../godot/scripts/core/turn_manager.gd) - Source of truth implementation

# Turn Structure & Action Point Design
## Strategic AP Management with Event Reserve System

_Created: 2025-10-31_
_Status: Design proposal - pending implementation_

---

## Current Turn Flow

### Phase 1: Turn Start
1. Refresh resources (research, compute)
2. Rival labs take actions
3. Doom system calculations
4. Random events trigger (if any)

### Phase 2: Action Selection
1. Player has full AP pool
2. Player queues actions (AP deducted immediately)
3. Queued actions shown in visual queue
4. Player can continue until AP exhausted or chooses to end turn

### Phase 3: Turn End
1. Execute all queued actions
2. Apply action effects
3. Check game over conditions
4. Advance to next turn

---

## Proposed Enhancement: Event AP Reserve

### Strategic Problem
**Currently**: Players must commit all AP during action selection phase
**Issue**: Events that occur mid-turn cannot be responded to with AP
**Result**: Missed strategic depth - no resource management tension

### Solution: Two-Phase AP System

#### AP Split
```gdscript
var total_ap: int = 3  # Base AP per turn
var committed_ap: int = 0  # Spent on queued actions
var reserved_ap: int = 0   # Held back for events

# Invariant: committed_ap + reserved_ap <= total_ap
```

#### Player Choice
When queuing actions, player can:
1. **Commit AP**: Queue action, deduct from available pool
2. **Reserve AP**: Explicitly save AP for potential events
3. **End Turn**: Lock in current split

---

## Architecture Changes

### 1. GameState Updates

```gdscript
# game_state.gd additions
class_name GameState

var action_points: int = 3        # Total AP for this turn
var committed_ap: int = 0         # AP spent on queued actions
var reserved_ap: int = 0          # AP held for events
var used_event_ap: int = 0        # AP spent on event responses

func get_available_ap() -> int:
	"""AP available for queuing actions"""
	return action_points - committed_ap - reserved_ap

func get_event_ap() -> int:
	"""AP available for event responses"""
	return reserved_ap - used_event_ap

func reserve_ap(amount: int) -> bool:
	"""Explicitly reserve AP for events"""
	if get_available_ap() >= amount:
		reserved_ap += amount
		return true
	return false

func commit_ap(amount: int) -> bool:
	"""Commit AP to queued action"""
	if get_available_ap() >= amount:
		committed_ap += amount
		return true
	return false

func spend_event_ap(amount: int) -> bool:
	"""Spend reserved AP on event response"""
	if get_event_ap() >= amount:
		used_event_ap += amount
		return true
	return false

func reset_turn_ap():
	"""Reset AP tracking for new turn"""
	committed_ap = 0
	reserved_ap = 0
	used_event_ap = 0
```

### 2. Event System Updates

```gdscript
# events.gd - add AP costs to event options
{
	"id": "safety_breakthrough_event",
	"name": "Safety Research Breakthrough",
	"options": [
		{
			"id": "accelerate",
			"text": "Accelerate research (costs 1 AP)",
			"costs": {"action_points": 1, "money": 50000},
			"effects": {"doom": -10, "research": 20}
		},
		{
			"id": "publish_immediately",
			"text": "Publish immediately (costs 2 AP)",
			"costs": {"action_points": 2},
			"effects": {"doom": -15, "papers": 1, "reputation": 10}
		},
		{
			"id": "defer",
			"text": "Defer to next turn (no AP cost)",
			"costs": {},
			"effects": {}
		}
	]
}
```

### 3. UI Updates

#### AP Display Enhancement
```gdscript
# Show split instead of just total
ap_label.text = "AP: %d (Available: %d | Reserved: %d)" % [
	state.action_points,
	state.get_available_ap(),
	state.reserved_ap
]
```

#### Reserve AP Button
Add UI control to reserve AP:
```gdscript
# New button in action selection phase
var reserve_button = Button.new()
reserve_button.text = "Reserve 1 AP for Events"
reserve_button.pressed.connect(_on_reserve_ap_pressed)

func _on_reserve_ap_pressed():
	if game_manager.reserve_ap(1):
		log_message("[color=cyan]Reserved 1 AP for event responses[/color]")
		update_ap_display()
```

#### Event Option Filtering
```gdscript
# In event dialog, show/disable options based on event AP
for option in event_options:
	var ap_cost = option.get("costs", {}).get("action_points", 0)
	var can_afford_ap = state.get_event_ap() >= ap_cost

	if not can_afford_ap:
		button.disabled = true
		button.tooltip_text += "\n[INSUFFICIENT EVENT AP]"
```

---

## Strategic Implications

### Risk/Reward Trade-off

**Commit All AP** (Current behavior):
- SUCCESS Maximum actions per turn
- SUCCESS Guaranteed progress
- ERROR Cannot respond to events optimally
- ERROR Forced to take "defer" options

**Reserve AP** (New strategy):
- SUCCESS Can take powerful event options
- SUCCESS Reactive capability
- ERROR Fewer guaranteed actions
- ERROR AP wasted if no events occur

### Example Scenarios

#### Scenario A: All-In Aggressive
```
Turn 5: 3 AP total
- Commit 3 AP: Hire researcher + Research safety + Publish paper
- Reserved: 0 AP
- Event occurs: "Safety breakthrough" - must defer (no AP)
- Result: 3 actions executed, missed event opportunity
```

#### Scenario B: Conservative Reserve
```
Turn 5: 3 AP total
- Commit 2 AP: Hire researcher + Research safety
- Reserved: 1 AP
- Event occurs: "Safety breakthrough" - can accelerate (1 AP)
- Result: 2 actions + powerful event response
```

#### Scenario C: Balanced
```
Turn 5: 3 AP total
- Commit 2 AP: Research safety + Publish
- Reserved: 1 AP
- No events occur
- Result: 2 actions, 1 AP wasted (opportunity cost)
```

---

## Implementation Phases

### Phase 1: Core Infrastructure SUCCESS (Done)
- [x] GameState tracks committed vs reserved AP
- [x] Visual queue shows committed actions
- [x] AP display shows split

### Phase 2: Reserve Mechanic (Next)
- [ ] Add "Reserve AP" button to UI
- [ ] Update action selection logic to respect reserves
- [ ] Visual indicator of reserved AP

### Phase 3: Event Integration
- [ ] Add AP costs to event options
- [ ] Event dialog shows event AP availability
- [ ] Disable unaffordable event options
- [ ] Spend event AP when option selected

### Phase 4: Balance & Polish
- [ ] Tune event frequency vs AP costs
- [ ] Add tutorial explaining reserve system
- [ ] Analytics: track reserve usage patterns
- [ ] AI opponents reserve AP intelligently

---

## Event AP Cost Guidelines

### Event Option Tiers

**Tier 0: Free Options** (Always available)
- Defer/ignore event
- Minimal response
- Example: "Do nothing" or "Acknowledge"

**Tier 1: Minor Response** (1 AP)
- Small boost/mitigation
- Low resource cost
- Example: "Quick review" or "Send email"

**Tier 2: Significant Response** (2 AP)
- Major effect
- Moderate resource cost
- Example: "Emergency meeting" or "Accelerate research"

**Tier 3: All-In Response** (3 AP)
- Game-changing effect
- High resource cost
- Rare, critical events only
- Example: "Pivot entire lab" or "Public announcement"

### Design Principles
1. **Always offer Tier 0 option** - No AP = viable choice
2. **AP cost scales with impact** - Bigger effects = more AP
3. **Resource + AP costs** - Most powerful options cost both
4. **Diminishing returns** - 3 AP option != 3x better than 1 AP

---

## Balance Considerations

### Event Frequency
- **Too frequent**: Reserving AP becomes mandatory
- **Too rare**: Reserving AP feels wasteful
- **Target**: ~40% of turns have events with AP options

### AP Reserve Value
```
Expected value of reserving 1 AP:
= P(event) x E(event_benefit | event) x P(have_AP | event)
= 0.4 x avg_benefit x 1.0
```

Should be competitive with:
```
Value of committing 1 AP to action:
= guaranteed_action_benefit
```

### Tuning Knobs
1. Event frequency (per turn)
2. AP option power level (effects)
3. Event AP costs (1-3 range)
4. Resource costs on AP options

---

## Documentation TODOs

### Files to Update
- [ ] `GAME_DESIGN.md` - Add AP reserve strategy section
- [ ] `PLAYERGUIDE.md` - Tutorial on AP management
- [ ] `ARCHITECTURE.md` - Document AP tracking system
- [ ] `TURN_MANAGER.md` - Update turn flow diagrams

### Architecture Review Needed
- [ ] How does this interact with doom momentum system?
- [ ] Can rivals reserve AP? Should they?
- [ ] What if player runs out of event AP mid-event?
- [ ] Save/load compatibility with new AP fields

---

## Open Questions

1. **UI Complexity**: Is explicit "Reserve" button too complex?
   - Alternative: Auto-reserve last AP?
   - Alternative: "Save 1 AP" checkbox on end turn?

2. **Commitment Timing**: Can players "unreserve" AP?
   - Once reserved, locked for turn?
   - Or flexible until turn end?

3. **Event Chaining**: What if multiple events in one turn?
   - Share event AP pool?
   - Each event has own reserve?

4. **Tutorial**: How to teach without overwhelming?
   - Introduce in turn 3-4?
   - Show example event first?

5. **Visual Design**: How to show reserved AP clearly?
   - Color-coded AP bar (blue = committed, green = reserved)?
   - Separate "Event AP" meter?

---

## Next Session: Architecture Doc Sweep

### Files to Review & Update
1. `GAME_DESIGN.md` - Core mechanics
2. `ARCHITECTURE.md` - System interactions
3. `TURN_MANAGER.md` - Turn flow
4. `PLAYERGUIDE.md` - Player-facing docs
5. `GODOT_PHASE_*.md` - Implementation roadmaps

### Questions to Answer
- Where does AP reserve system live in architecture?
- How does it integrate with existing systems?
- What are the testing requirements?
- What's the rollout strategy?

---

_This design document will be refined as we prototype and playtest the system._

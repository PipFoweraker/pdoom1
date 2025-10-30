extends Node
class_name TurnManager
## Manages turn execution order - fully deterministic

var state: GameState

func _init(game_state: GameState):
	state = game_state

func start_turn() -> Dictionary:
	"""
	Begin new turn - Phase 1: TURN_START
	FIX #418: Events trigger BEFORE action selection
	"""
	state.turn += 1
	state.current_phase = GameState.TurnPhase.TURN_START
	state.pending_events.clear()
	state.queued_actions.clear()
	state.can_end_turn = false

	# Calculate max AP based on staff (base 3 + 0.5 per staff member)
	var total_staff = state.get_total_staff()
	var max_ap = 3 + int(total_staff * 0.5)
	state.action_points = max_ap

	# === RESEARCHER TURN PROCESSING ===
	# Process individual researchers (burnout, skill growth, loyalty)
	for researcher in state.researchers:
		researcher.process_turn()

	# Staff maintenance costs (salary per employee per turn)
	var staff_salaries = total_staff * 5000  # $5k per employee per turn
	if staff_salaries > 0:
		state.add_resources({"money": -staff_salaries})

	# === EMPLOYEE PRODUCTIVITY SYSTEM ===
	# Based on Python implementation: src/core/game_state.py lines 1208-1372

	# 1. Management capacity check - unmanaged employees are unproductive
	var non_manager_staff = state.safety_researchers + state.capability_researchers + state.compute_engineers
	var management_capacity = state.get_management_capacity()
	var managed_employees = min(non_manager_staff, management_capacity)
	var unmanaged_employees = state.get_unmanaged_count()

	# 2. Compute distribution - each productive employee needs 1 compute
	var available_compute = int(state.compute)
	var productive_employees = min(managed_employees, available_compute)

	# 3. Research generation from employees (30% chance per productive employee)
	var research_from_employees = 0.0
	for i in range(productive_employees):
		if state.rng.randf() < 0.30:  # 30% chance per employee
			var base_research = state.rng.randi_range(1, 3)
			research_from_employees += base_research

	# 4. Compute engineer bonus (+10% effectiveness per engineer)
	var compute_efficiency_bonus = 1.0 + (state.compute_engineers * 0.1)
	research_from_employees *= compute_efficiency_bonus

	# 5. Safety researchers reduce doom passively (only if productive)
	var productive_safety = min(state.safety_researchers, productive_employees)
	var doom_reduction_from_safety = productive_safety * 0.3
	state.add_resources({"doom": -doom_reduction_from_safety})

	# 6. Unproductive employees (no compute OR no manager) cause doom
	var total_unproductive = (non_manager_staff - productive_employees) + unmanaged_employees
	if total_unproductive > 0:
		var doom_penalty = total_unproductive * 0.5
		state.add_resources({"doom": doom_penalty})

	# Apply research gains
	state.add_resources({"research": research_from_employees})

	var messages = [
		"Turn %d started" % state.turn,
		"Action Points: %d (base 3 + %d from %d staff)" % [max_ap, max_ap - 3, total_staff]
	]

	if staff_salaries > 0:
		messages.append("Paid $%d in staff salaries" % staff_salaries)

	if research_from_employees > 0:
		messages.append("Generated %.1f research from %d productive employees" % [research_from_employees, productive_employees])

	if doom_reduction_from_safety > 0:
		messages.append("Safety researchers reduced doom by %.1f" % doom_reduction_from_safety)

	if unmanaged_employees > 0:
		messages.append("WARNING: %d unmanaged employees (need more managers!)" % unmanaged_employees)

	if total_unproductive > 0:
		messages.append("WARNING: %d unproductive employees! (+%.1f doom)" % [total_unproductive, total_unproductive * 0.5])

	# CHECK FOR EVENTS FIRST (FIX #418)
	# Events must be presented and resolved BEFORE player selects actions
	var triggered_events = GameEvents.check_triggered_events(state, state.rng)

	if triggered_events.size() > 0:
		# Events block action selection until resolved
		state.pending_events = triggered_events
		state.current_phase = GameState.TurnPhase.TURN_START  # Stay in TURN_START
		state.can_end_turn = false
		messages.append("%d event(s) require attention!" % triggered_events.size())
	else:
		# No events, can proceed to action selection
		state.current_phase = GameState.TurnPhase.ACTION_SELECTION
		state.can_end_turn = true

	return {
		"success": true,
		"phase": "turn_start" if triggered_events.size() > 0 else "action_selection",
		"messages": messages,
		"triggered_events": triggered_events,
		"can_select_actions": triggered_events.size() == 0,
		"can_end_turn": state.can_end_turn
	}

func execute_turn() -> Dictionary:
	"""Execute queued actions - Phase 2"""
	var results = []
	var all_success = true

	# Execute each queued action in order
	for action_id in state.queued_actions:
		var result = GameActions.execute_action(action_id, state)
		results.append(result)
		if not result["success"]:
			all_success = false

	# Clear queued actions
	state.queued_actions.clear()

	# Check for paper publication (research threshold)
	if state.research >= 100:
		var papers_to_publish = int(state.research / 100)
		state.papers += papers_to_publish
		state.research = fmod(state.research, 100)  # Keep remainder
		state.add_resources({"reputation": papers_to_publish * 5})  # Papers boost reputation
		results.append({
			"success": true,
			"message": "Published %d paper%s! (+%d reputation)" % [
				papers_to_publish,
				"s" if papers_to_publish > 1 else "",
				papers_to_publish * 5
			]
		})

	# === RIVAL LABS TAKE ACTIONS ===
	var rival_doom_contribution = 0.0
	for rival in state.rival_labs:
		var rival_result = RivalLabs.process_rival_turn(rival, state, state.rng)
		rival_doom_contribution += rival_result["doom_contribution"]
		results.append({
			"success": true,
			"message": "%s: %s" % [rival_result["name"], ", ".join(rival_result["actions"])]
		})

	# === USE DOOM SYSTEM FOR CALCULATION ===
	if state.doom_system:
		# Set rival contribution (calculated externally)
		state.doom_system.set_rival_doom_contribution(rival_doom_contribution)

		# Calculate doom with momentum system
		var doom_result = state.doom_system.calculate_doom_change(state)

		# Create detailed message
		var doom_msg = "Doom %.1f → %.1f (change: %+.1f)" % [
			doom_result["new_doom"] - doom_result["total_change"],
			doom_result["new_doom"],
			doom_result["total_change"]
		]

		# Add breakdown if significant changes
		if abs(doom_result["total_change"]) > 0.1:
			var breakdown_parts = []
			for source in doom_result["sources"]:
				var value = doom_result["sources"][source]
				if abs(value) > 0.1:
					breakdown_parts.append("%s: %+.1f" % [source, value])
			if breakdown_parts.size() > 0:
				doom_msg += "\n  └─ " + ", ".join(breakdown_parts)

		# Add momentum info if significant
		if abs(doom_result["momentum"]) > 0.5:
			doom_msg += "\n  └─ Momentum: %s (%.1f)" % [
				state.doom_system.get_momentum_description(),
				doom_result["momentum"]
			]

		results.append({
			"success": true,
			"message": doom_msg
		})

		# Sync to state.doom for backward compatibility
		state.doom = state.doom_system.current_doom
	else:
		# Fallback if doom system not initialized
		var total_doom_increase = 1.0 + (state.capability_researchers * 0.5) + rival_doom_contribution
		state.add_resources({"doom": total_doom_increase})
		results.append({
			"success": true,
			"message": "Doom +%.1f (legacy calculation)" % total_doom_increase
		})

	# REMOVED: Event checking now happens in start_turn() (FIX #418)
	# Events are checked BEFORE actions, not after

	# Check win/lose
	state.check_win_lose()

	if state.game_over:
		if state.victory:
			results.append({"success": true, "message": "VICTORY! p(doom) reached 0!"})
		else:
			var reason = "p(doom) = 100" if state.doom >= 100 else "Reputation = 0"
			results.append({"success": false, "message": "GAME OVER: " + reason})

	return {
		"success": all_success,
		"action_results": results,
		"turn_complete": true
	}

func resolve_event(event: Dictionary, choice_id: String) -> Dictionary:
	"""
	Resolve player's event choice during TURN_START phase
	FIX #418: After all events resolved, transition to ACTION_SELECTION
	"""
	if state.current_phase != GameState.TurnPhase.TURN_START:
		return {
			"success": false,
			"error": "Cannot resolve events in phase %s" % state.current_phase
		}

	# Execute the event choice
	var result = GameEvents.execute_event_choice(event, choice_id, state)

	if not result["success"]:
		return result

	# Remove this event from pending
	var event_id = event.get("id", "")
	var new_pending: Array[Dictionary] = []
	for pending in state.pending_events:
		if pending.get("id", "") != event_id:
			new_pending.append(pending)
	state.pending_events = new_pending

	# If no more pending events, transition to ACTION_SELECTION
	if state.pending_events.size() == 0:
		state.current_phase = GameState.TurnPhase.ACTION_SELECTION
		state.can_end_turn = true
		result["phase_transitioned"] = true
		result["new_phase"] = "action_selection"
	else:
		result["pending_events"] = state.pending_events.size()

	result["can_select_actions"] = state.pending_events.size() == 0
	result["can_end_turn"] = state.can_end_turn

	return result

func get_available_actions() -> Array[Dictionary]:
	"""Get actions player can currently take"""
	var all_actions = GameActions.get_all_actions()
	var available: Array[Dictionary] = []

	for action in all_actions:
		var can_afford = state.can_afford(action["costs"])
		var action_copy = action.duplicate()
		action_copy["affordable"] = can_afford
		available.append(action_copy)

	return available

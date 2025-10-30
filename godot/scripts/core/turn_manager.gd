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

	# Staff maintenance costs (salary per employee per turn)
	var staff_salaries = total_staff * 5000  # $5k per employee per turn
	if staff_salaries > 0:
		state.add_resources({"money": -staff_salaries})

	# Generate research from compute (deterministic)
	var research_generated = state.compute * 0.05 * (1.0 + state.compute_engineers * 0.1)
	state.add_resources({"research": research_generated})

	var messages = [
		"Turn %d started" % state.turn,
		"Action Points: %d (base 3 + %d from %d staff)" % [max_ap, max_ap - 3, total_staff]
	]

	if staff_salaries > 0:
		messages.append("Paid $%d in staff salaries" % staff_salaries)

	messages.append("Generated %.1f research from compute" % research_generated)

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

	# Environmental doom increase (time pressure)
	var base_doom_increase = 1.0
	var capability_doom = state.capability_researchers * 0.5
	var total_doom_increase = base_doom_increase + capability_doom

	state.add_resources({"doom": total_doom_increase})
	results.append({
		"success": true,
		"message": "Environmental doom +%.1f (base %.1f, capabilities %.1f)" % [
			total_doom_increase, base_doom_increase, capability_doom
		]
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

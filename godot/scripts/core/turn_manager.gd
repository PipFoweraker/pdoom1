extends Node
class_name TurnManager
## Manages turn execution order - fully deterministic

var state: GameState

func _init(game_state: GameState):
	state = game_state

func start_turn() -> Dictionary:
	"""Begin new turn - Phase 1"""
	state.turn += 1
	state.action_points = 3  # Refresh AP each turn

	# Generate research from compute (deterministic)
	var research_generated = state.compute * 0.05 * (1.0 + state.compute_engineers * 0.1)
	state.add_resources({"research": research_generated})

	return {
		"success": true,
		"phase": "action_selection",
		"messages": [
			"Turn %d started" % state.turn,
			"Generated %.1f research from compute" % research_generated
		]
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

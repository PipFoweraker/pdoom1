extends Node
class_name RivalLabs
## Rival AI labs that compete with the player
## Issue #474: Organization discovery system

# Organization visibility states
enum VisibilityState {
	HIDDEN,      # Player does not know they exist
	RUMORED,     # Player has heard whispers (name only)
	DISCOVERED,  # Player knows about them (basic info visible)
	KNOWN        # Full intelligence gathered (all stats visible)
}

# Rival lab data structure
class RivalLab:
	var id: String = ""
	var name: String
	var safety_progress: float = 0.0
	var capability_progress: float = 0.0
	var funding: float = 200000.0
	var reputation: float = 50.0
	var aggression: float = 0.5

	# Discovery system (Issue #474)
	var visibility: int = VisibilityState.KNOWN
	var discovery_turn: int = -1
	var discovery_threshold: float = 0.0
	var is_starter: bool = true
	var description: String = ""
	var focus: String = "balanced"
	var estimated_funding: float = 0.0
	var estimated_reputation: float = 0.0

	func _init(lab_name: String, initial_aggression: float):
		name = lab_name
		id = lab_name.to_lower().replace(" ", "_")
		aggression = initial_aggression
		if initial_aggression > 0.7:
			focus = "capabilities"
		elif initial_aggression < 0.4:
			focus = "safety"

	func is_visible_to_player() -> bool:
		return visibility >= VisibilityState.RUMORED

	func get_visible_name() -> String:
		if visibility == VisibilityState.RUMORED:
			return name + " (rumored)"
		return name

static func get_rival_labs() -> Array[RivalLab]:
	var rivals: Array[RivalLab] = []

	var deep_safety = RivalLab.new("DeepSafety", 0.3)
	deep_safety.funding = 500000.0
	deep_safety.reputation = 70.0
	deep_safety.visibility = VisibilityState.KNOWN
	deep_safety.description = "A well-funded research lab focused on AI alignment and safety."
	rivals.append(deep_safety)

	var capabili = RivalLab.new("CapabiliCorp", 0.9)
	capabili.funding = 1000000.0
	capabili.reputation = 60.0
	capabili.visibility = VisibilityState.KNOWN
	capabili.description = "An aggressive AI capabilities lab backed by major tech investors."
	rivals.append(capabili)

	var stealth = RivalLab.new("StealthAI", 0.5)
	stealth.funding = 300000.0
	stealth.reputation = 40.0
	stealth.visibility = VisibilityState.RUMORED
	stealth.discovery_threshold = 45.0
	stealth.description = "A secretive AI lab with unknown backers."
	stealth.estimated_funding = 200000.0
	stealth.estimated_reputation = 30.0
	rivals.append(stealth)

	return rivals

static func check_discovery(rival: RivalLab, player_state: GameState, rng: RandomNumberGenerator) -> Dictionary:
	var result = {"discovered": false, "new_visibility": rival.visibility, "message": ""}
	if rival.visibility >= VisibilityState.KNOWN:
		return result
	var discovery_chance = 0.0
	if player_state.reputation >= rival.discovery_threshold:
		discovery_chance = 0.15 + (player_state.reputation - rival.discovery_threshold) * 0.005
	if rng.randf() < discovery_chance:
		result["discovered"] = true
		result["new_visibility"] = rival.visibility + 1
		if rival.discovery_turn == -1:
			rival.discovery_turn = player_state.turn
		match result["new_visibility"]:
			VisibilityState.DISCOVERED:
				result["message"] = "Intel on %s: %s-focused org." % [rival.name, rival.focus]
				rival.estimated_funding = rival.funding * rng.randf_range(0.7, 1.3)
				rival.estimated_reputation = rival.reputation * rng.randf_range(0.8, 1.2)
			VisibilityState.KNOWN:
				result["message"] = "Full intel on %s acquired." % rival.name
	return result

static func process_rival_turn(rival: RivalLab, player_state: GameState, rng: RandomNumberGenerator) -> Dictionary:
	var result = {"name": rival.name, "actions": [], "doom_contribution": 0.0, "visible": rival.is_visible_to_player()}
	var num_actions = 1 if rival.funding < 100000 else (2 if rival.funding < 500000 else 3)
	for i in range(num_actions):
		var action = _choose_rival_action(rival, player_state, rng)
		result["actions"].append(action)
		match action:
			"hire_researcher":
				rival.funding -= 60000
				if rival.aggression > 0.6:
					rival.capability_progress += 5.0
					result["doom_contribution"] += 2.0
				else:
					rival.safety_progress += 3.0
					result["doom_contribution"] -= 0.5
			"buy_compute":
				rival.funding -= 50000
				result["doom_contribution"] += 0.5
			"publish_paper":
				rival.reputation += 5.0
				if rival.aggression > 0.6:
					result["doom_contribution"] += 3.0
				else:
					result["doom_contribution"] -= 2.0
			"fundraise":
				rival.funding += 150000 + (rival.reputation * 1000)
			"capability_research":
				rival.capability_progress += 10.0
				result["doom_contribution"] += 5.0
			"safety_research":
				rival.safety_progress += 8.0
				result["doom_contribution"] -= 3.0
	return result

static func _choose_rival_action(rival: RivalLab, _player_state: GameState, rng: RandomNumberGenerator) -> String:
	if rival.funding < 50000:
		return "fundraise"
	var roll = rng.randf()
	if rival.aggression > 0.7:
		if roll < 0.4: return "capability_research"
		elif roll < 0.7: return "hire_researcher"
		elif roll < 0.85: return "publish_paper"
		else: return "buy_compute"
	elif rival.aggression < 0.4:
		if roll < 0.5: return "safety_research"
		elif roll < 0.75: return "hire_researcher"
		else: return "publish_paper"
	else:
		if roll < 0.3: return "safety_research"
		elif roll < 0.5: return "capability_research"
		elif roll < 0.7: return "hire_researcher"
		else: return "buy_compute"

static func get_rival_summary(rival: RivalLab) -> String:
	if not rival.is_visible_to_player():
		return ""
	if rival.visibility == VisibilityState.RUMORED:
		return "%s: Rumored to exist." % rival.name
	elif rival.visibility == VisibilityState.DISCOVERED:
		return "%s (%s): ~$%.0fk, ~%.0f rep" % [rival.name, rival.focus, rival.estimated_funding/1000.0, rival.estimated_reputation]
	else:
		return "%s (%s): $%.0fk, %.0f rep, %.1f safety, %.1f caps" % [rival.name, rival.focus, rival.funding/1000.0, rival.reputation, rival.safety_progress, rival.capability_progress]

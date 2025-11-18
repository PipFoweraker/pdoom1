extends Node
class_name RivalLabs
## Rival AI labs that compete with the player

# Rival lab data structure
class RivalLab:
	var name: String
	var safety_progress: float = 0.0
	var capability_progress: float = 0.0
	var funding: float = 200000.0
	var reputation: float = 50.0
	var aggression: float = 0.5  # 0.0 = cautious, 1.0 = aggressive

	func _init(lab_name: String, initial_aggression: float):
		name = lab_name
		aggression = initial_aggression

static func get_rival_labs() -> Array[RivalLab]:
	"""Initialize the 3 rival labs"""
	var rivals: Array[RivalLab] = []

	# DeepSafety - well-funded, safety-focused
	var deep_safety = RivalLab.new("DeepSafety", 0.3)
	deep_safety.funding = 500000.0
	deep_safety.reputation = 70.0
	rivals.append(deep_safety)

	# CapabiliCorp - aggressive capabilities research
	var capabili = RivalLab.new("CapabiliCorp", 0.9)
	capabili.funding = 1000000.0
	capabili.reputation = 60.0
	rivals.append(capabili)

	# StealthAI - mysterious, balanced approach
	var stealth = RivalLab.new("StealthAI", 0.5)
	stealth.funding = 300000.0
	stealth.reputation = 40.0
	rivals.append(stealth)

	return rivals

static func process_rival_turn(rival: RivalLab, player_state: GameState, rng: RandomNumberGenerator) -> Dictionary:
	"""Simulate one rival's turn actions"""
	var result = {
		"name": rival.name,
		"actions": [],
		"doom_contribution": 0.0
	}

	# Rivals take 1-3 actions per turn based on funding
	var num_actions = 1 if rival.funding < 100000 else (2 if rival.funding < 500000 else 3)

	for i in range(num_actions):
		var action = _choose_rival_action(rival, player_state, rng)
		result["actions"].append(action)

		# Execute action
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
				var raised = 150000 + (rival.reputation * 1000)
				rival.funding += raised

			"capability_research":
				rival.capability_progress += 10.0
				result["doom_contribution"] += 5.0  # Capabilities increase global doom

			"safety_research":
				rival.safety_progress += 8.0
				result["doom_contribution"] -= 3.0  # Safety reduces global doom

	return result

static func _choose_rival_action(rival: RivalLab, _player_state: GameState, rng: RandomNumberGenerator) -> String:
	"""Choose what action a rival takes based on their personality"""

	# Low funding? Fundraise
	if rival.funding < 50000:
		return "fundraise"

	# Random decision weighted by aggression
	var roll = rng.randf()

	if rival.aggression > 0.7:
		# Aggressive lab - focus on capabilities
		if roll < 0.4:
			return "capability_research"
		elif roll < 0.7:
			return "hire_researcher"
		elif roll < 0.85:
			return "publish_paper"
		else:
			return "buy_compute"

	elif rival.aggression < 0.4:
		# Safety-focused lab
		if roll < 0.5:
			return "safety_research"
		elif roll < 0.75:
			return "hire_researcher"
		else:
			return "publish_paper"

	else:
		# Balanced approach
		if roll < 0.3:
			return "safety_research"
		elif roll < 0.5:
			return "capability_research"
		elif roll < 0.7:
			return "hire_researcher"
		else:
			return "buy_compute"

static func get_rival_summary(rival: RivalLab) -> String:
	"""Get text summary of rival's status"""
	return "%s: $%.0fk funding, %.0f reputation, %.1f safety, %.1f capabilities" % [
		rival.name,
		rival.funding / 1000.0,
		rival.reputation,
		rival.safety_progress,
		rival.capability_progress
	]

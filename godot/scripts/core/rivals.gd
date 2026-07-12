extends Node
class_name RivalLabs
## Rival AI labs that compete with the player
## Issue #474: Organization discovery system

## Passive "capability-overhang" doom each rival applies per turn, scaling with its
## accumulated capability_progress — a GROWING pressure a fixed safety capacity cannot
## offset forever (the unbounded-mortality term for issue #562 / DQ-1).
## Placeholder magnitude — tuning is workshop #2.
const CAPABILITY_OVERHANG_DOOM_PER_PROGRESS: float = 0.025

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

	## L7 (#618): full-state serialization. Everything mutable during a run
	## (progress, funding, reputation, discovery state) must round-trip; identity
	## fields (name, aggression, description) travel too so a save is self-contained.
	func to_dict() -> Dictionary:
		return {
			"id": id,
			"name": name,
			"safety_progress": safety_progress,
			"capability_progress": capability_progress,
			"funding": funding,
			"reputation": reputation,
			"aggression": aggression,
			"visibility": visibility,
			"discovery_turn": discovery_turn,
			"discovery_threshold": discovery_threshold,
			"is_starter": is_starter,
			"description": description,
			"focus": focus,
			"estimated_funding": estimated_funding,
			"estimated_reputation": estimated_reputation,
		}

	static func from_dict(d: Dictionary) -> RivalLab:
		var lab := RivalLab.new(String(d.get("name", "")), float(d.get("aggression", 0.5)))
		lab.id = String(d.get("id", lab.id))
		lab.safety_progress = float(d.get("safety_progress", 0.0))
		lab.capability_progress = float(d.get("capability_progress", 0.0))
		lab.funding = float(d.get("funding", 200000.0))
		lab.reputation = float(d.get("reputation", 50.0))
		lab.visibility = int(d.get("visibility", VisibilityState.KNOWN))
		lab.discovery_turn = int(d.get("discovery_turn", -1))
		lab.discovery_threshold = float(d.get("discovery_threshold", 0.0))
		lab.is_starter = bool(d.get("is_starter", true))
		lab.description = String(d.get("description", ""))
		lab.focus = String(d.get("focus", lab.focus))
		lab.estimated_funding = float(d.get("estimated_funding", 0.0))
		lab.estimated_reputation = float(d.get("estimated_reputation", 0.0))
		return lab

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
		discovery_chance = Balance.num("rivals.discovery.base_chance", 0.15) \
			+ (player_state.reputation - rival.discovery_threshold) * Balance.num("rivals.discovery.chance_per_rep_above_threshold", 0.005)
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
	# Passive capability-overhang pressure: grows as this rival's capability_progress
	# accumulates, so advanced rivals apply doom a fixed safety capacity cannot fully
	# offset over time (issue #562 / DQ-1 mortality term). Scale from Balance (L9 #621).
	result["doom_contribution"] += rival.capability_progress \
		* Balance.num("rivals.capability_overhang_doom_per_progress", CAPABILITY_OVERHANG_DOOM_PER_PROGRESS)
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

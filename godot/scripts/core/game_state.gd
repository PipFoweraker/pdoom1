extends Node
class_name GameState
## Core game state - all resources and game status

# Resources
var money: float = 245000.0  # Updated from player feedback (issue #436)
var compute: float = 100.0
var research: float = 0.0  # Generated from compute
var papers: float = 0.0
var reputation: float = 50.0
var doom: float = 50.0  # 0-100, lose at 100
var action_points: int = 3
var stationery: float = 100.0  # Office supplies, depletes with staff usage

# AP Reserve System (for event responses)
var committed_ap: int = 0      # AP spent on queued actions
var reserved_ap: int = 0       # AP held back for events
var used_event_ap: int = 0     # AP spent on event responses

# Staff (legacy counts for backward compatibility)
var safety_researchers: int = 0
var capability_researchers: int = 0
var compute_engineers: int = 0
var managers: int = 0  # Each manager can handle 9 employees

# Individual researchers (new system)
var researchers: Array[Researcher] = []

# Candidate pool (available hires - populates slowly over time)
var candidate_pool: Array[Researcher] = []
const MAX_CANDIDATES: int = 6  # Maximum candidates in pool

# Purchased upgrades (one-time purchases)
var purchased_upgrades: Array[String] = []

# Game status
var turn: int = 0
var game_over: bool = false
var victory: bool = false
var game_seed_str: String = ""  # Renamed from 'seed' to avoid shadowing built-in function

# Lab mascot 🐱
var has_cat: bool = false

# Turn phase tracking (fixes #418 - proper event sequencing)
enum TurnPhase { TURN_START, ACTION_SELECTION, TURN_PROCESSING, TURN_END }
var current_phase: TurnPhase = TurnPhase.ACTION_SELECTION
var pending_events: Array[Dictionary] = []  # Events that must be resolved before actions
var can_end_turn: bool = false

# Deterministic RNG for events
var rng: RandomNumberGenerator

# Queued actions for this turn
var queued_actions: Array[String] = []

# Rival labs
var rival_labs: Array = []  # Array of RivalLabs.RivalLab

# Doom system (modular, extensible)
var doom_system: DoomSystem

func _init(game_seed: String = ""):
	game_seed_str = game_seed if game_seed != "" else str(Time.get_ticks_msec())

	# Initialize deterministic RNG from seed
	rng = RandomNumberGenerator.new()
	rng.seed = hash(game_seed_str)

	# Initialize doom system
	doom_system = DoomSystem.new()
	doom_system.current_doom = doom

	# Initialize rival labs
	rival_labs = RivalLabs.get_rival_labs()

	reset()

func reset():
	"""Reset to starting state"""
	money = 245000.0  # Updated from player feedback (issue #436)
	compute = 100.0
	research = 0.0
	papers = 0.0
	reputation = 50.0
	doom = 50.0
	action_points = 3
	stationery = 100.0

	safety_researchers = 0
	capability_researchers = 0
	compute_engineers = 0
	managers = 0

	purchased_upgrades.clear()
	candidate_pool.clear()
	researchers.clear()

	# Initialize with 2-3 starting candidates (low quality)
	_populate_initial_candidates()

	turn = 0
	game_over = false
	victory = false
	queued_actions.clear()

	# Reset phase tracking (#418 fix)
	current_phase = TurnPhase.ACTION_SELECTION
	pending_events.clear()
	can_end_turn = false

	# Reset doom system
	if doom_system:
		doom_system.current_doom = doom
		doom_system.doom_velocity = 0.0
		doom_system.doom_momentum = 0.0

func can_afford(costs: Dictionary) -> bool:
	"""Check if player can afford given costs (FIX #407: added reputation validation)"""
	if costs.has("money") and money < costs["money"]:
		return false
	if costs.has("compute") and compute < costs["compute"]:
		return false
	if costs.has("research") and research < costs["research"]:
		return false
	if costs.has("papers") and papers < costs["papers"]:
		return false
	if costs.has("reputation") and reputation < costs["reputation"]:
		return false
	if costs.has("action_points") and action_points < costs["action_points"]:
		return false
	return true

func spend_resources(costs: Dictionary):
	"""Spend resources (assumes can_afford was checked) (FIX #407: added reputation deduction)"""
	# Validate we can afford before spending
	if not can_afford(costs):
		ErrorHandler.report_err(
			ErrorHandler.Category.RESOURCES,
			"Attempted to spend unaffordable resources",
			{
				"costs": costs,
				"current": {
					"money": money,
					"compute": compute,
					"research": research,
					"papers": papers,
					"reputation": reputation,
					"action_points": action_points
				}
			}
		)
		return

	if costs.has("money"):
		money -= costs["money"]
		if money < 0:
			ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Money went negative", {"money": money})

	if costs.has("compute"):
		compute -= costs["compute"]
		if compute < 0:
			ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Compute went negative", {"compute": compute})

	if costs.has("research"):
		research -= costs["research"]
		if research < 0:
			ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Research went negative", {"research": research})

	if costs.has("papers"):
		papers -= costs["papers"]
		if papers < 0:
			ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Papers went negative", {"papers": papers})

	if costs.has("reputation"):
		reputation -= costs["reputation"]
		reputation = max(reputation, 0.0)  # Clamp to 0 minimum
		if reputation <= 0:
			ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Reputation reached zero", {})

	if costs.has("action_points"):
		action_points -= costs["action_points"]
		if action_points < 0:
			ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Action points went negative", {"action_points": action_points})

func add_resources(gains: Dictionary):
	"""Add resources"""
	if gains.has("money"):
		money += gains["money"]
	if gains.has("compute"):
		compute += gains["compute"]
	if gains.has("research"):
		research += gains["research"]
	if gains.has("papers"):
		papers += gains["papers"]
	if gains.has("reputation"):
		reputation += gains["reputation"]
	if gains.has("doom"):
		doom += gains["doom"]
		doom = clamp(doom, 0.0, 100.0)

func check_win_lose():
	"""Check victory/defeat conditions"""
	# Sync doom from doom system
	if doom_system:
		doom = doom_system.current_doom

	if doom >= 100.0:
		game_over = true
		victory = false
	elif reputation <= 0.0:
		game_over = true
		victory = false
	elif doom <= 0.0:
		game_over = true
		victory = true

func get_total_staff() -> int:
	# Count individual researchers if using new system
	if researchers.size() > 0:
		return researchers.size() + managers
	# Fallback to legacy counts
	return safety_researchers + capability_researchers + compute_engineers + managers

func get_researcher_count_by_spec(spec: String) -> int:
	"""Count researchers by specialization"""
	var count = 0
	for researcher in researchers:
		if researcher.specialization == spec:
			count += 1
	return count

func add_researcher(researcher: Researcher):
	"""Add a researcher to the team"""
	researchers.append(researcher)

	# Update legacy counts for backward compatibility
	match researcher.specialization:
		"safety":
			safety_researchers += 1
		"capabilities":
			capability_researchers += 1
		"interpretability", "alignment":
			safety_researchers += 1  # Count as safety for legacy systems

func remove_researcher(researcher: Researcher):
	"""Remove a researcher from the team"""
	var idx = researchers.find(researcher)
	if idx >= 0:
		researchers.remove_at(idx)

		# Update legacy counts
		match researcher.specialization:
			"safety":
				safety_researchers = max(0, safety_researchers - 1)
			"capabilities":
				capability_researchers = max(0, capability_researchers - 1)
			"interpretability", "alignment":
				safety_researchers = max(0, safety_researchers - 1)

func add_candidate(candidate: Researcher):
	"""Add a candidate to the hiring pool"""
	if candidate_pool.size() < MAX_CANDIDATES:
		candidate_pool.append(candidate)

func remove_candidate(candidate: Researcher):
	"""Remove a candidate from the pool (hired or expired)"""
	var idx = candidate_pool.find(candidate)
	if idx >= 0:
		candidate_pool.remove_at(idx)

func hire_candidate(candidate: Researcher):
	"""Hire a candidate from the pool"""
	remove_candidate(candidate)
	add_researcher(candidate)

func get_candidates_by_spec(spec: String) -> Array[Researcher]:
	"""Get all candidates with a specific specialization"""
	var matches: Array[Researcher] = []
	for candidate in candidate_pool:
		if candidate.specialization == spec:
			matches.append(candidate)
	return matches

func _populate_initial_candidates():
	"""Generate 2-3 starting candidates (lower quality for early game)"""
	# Always at least 1 safety researcher to start
	var safety_candidate = Researcher.new()
	safety_candidate.generate_random(rng)
	safety_candidate.specialization = "safety"
	# Lower skill for starting candidates
	safety_candidate.skill_level = rng.randi_range(1, 3)
	add_candidate(safety_candidate)

	# Second candidate - 50% safety, 50% capabilities
	var second = Researcher.new()
	second.generate_random(rng)
	second.specialization = "safety" if rng.randf() < 0.5 else "capabilities"
	second.skill_level = rng.randi_range(1, 3)
	add_candidate(second)

	# Third candidate (50% chance)
	if rng.randf() < 0.5:
		var third = Researcher.new()
		third.generate_random(rng)
		var specs = ["safety", "capabilities", "interpretability", "alignment"]
		third.specialization = specs[rng.randi() % specs.size()]
		third.skill_level = rng.randi_range(1, 3)
		add_candidate(third)

func get_management_capacity() -> int:
	"""How many employees can current managers handle?"""
	if managers == 0:
		return 9  # Base capacity before first manager
	return managers * 9

func get_unmanaged_count() -> int:
	"""How many employees exceed management capacity?"""
	var non_manager_staff = safety_researchers + capability_researchers + compute_engineers
	var capacity = get_management_capacity()
	return max(0, non_manager_staff - capacity)

func has_upgrade(upgrade_id: String) -> bool:
	"""Check if an upgrade has been purchased"""
	return purchased_upgrades.has(upgrade_id)

func add_upgrade(upgrade_id: String):
	"""Mark an upgrade as purchased"""
	if not purchased_upgrades.has(upgrade_id):
		purchased_upgrades.append(upgrade_id)

		# Handle special upgrade effects
		if upgrade_id == "cat_adoption":
			has_cat = true

# AP Reserve System Methods
func get_available_ap() -> int:
	"""AP available for queuing actions"""
	return action_points - committed_ap - reserved_ap

func get_event_ap() -> int:
	"""AP available for event responses"""
	return reserved_ap - used_event_ap

func reserve_ap_amount(amount: int) -> bool:
	"""Reserve AP for events"""
	if get_available_ap() >= amount:
		reserved_ap += amount
		return true
	return false

func commit_ap_amount(amount: int) -> bool:
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

func to_dict() -> Dictionary:
	"""Serialize state for UI"""
	var rival_summaries = []
	for rival in rival_labs:
		rival_summaries.append(RivalLabs.get_rival_summary(rival))

	# Sync doom from doom system
	if doom_system:
		doom = doom_system.current_doom

	# Get doom system data
	var doom_data = {}
	if doom_system:
		doom_data = {
			"doom": doom,
			"doom_velocity": doom_system.doom_velocity,
			"doom_momentum": doom_system.doom_momentum,
			"doom_trend": doom_system._get_doom_trend(),
			"doom_status": doom_system.get_doom_status(),
			"momentum_description": doom_system.get_momentum_description(),
			"doom_sources": doom_system.doom_sources.duplicate()
		}
	else:
		doom_data = {"doom": doom}

	# Serialize researchers array
	var researcher_dicts = []
	for researcher in researchers:
		researcher_dicts.append(researcher.to_dict())

	# Serialize candidate pool
	var candidate_dicts = []
	for candidate in candidate_pool:
		candidate_dicts.append(candidate.to_dict())

	return {
		"money": money,
		"compute": compute,
		"research": research,
		"papers": papers,
		"reputation": reputation,
		"doom": doom,
		"doom_system": doom_data,
		"action_points": action_points,
		"committed_ap": committed_ap,
		"reserved_ap": reserved_ap,
		"available_ap": get_available_ap(),
		"event_ap": get_event_ap(),
		"stationery": stationery,
		"safety_researchers": safety_researchers,
		"capability_researchers": capability_researchers,
		"compute_engineers": compute_engineers,
		"managers": managers,
		"total_staff": get_total_staff(),
		"management_capacity": get_management_capacity(),
		"unmanaged_count": get_unmanaged_count(),
		"turn": turn,
		"game_over": game_over,
		"victory": victory,
		"rival_labs": rival_summaries,
		"has_cat": has_cat,
		"purchased_upgrades": purchased_upgrades,
		"researchers": researcher_dicts,
		"candidate_pool": candidate_dicts
	}

extends Node
class_name GameState
## Core game state - all resources and game status

# Preload RiskPool to ensure it's available before class_name registration
const RiskPoolClass = preload("res://scripts/core/risk_pool.gd")

# Resources
var money: float = 245000.0  # Updated from player feedback (issue #436)
var compute: float = 100.0
var research: float = 0.0  # Generated from compute
var papers: float = 0.0
var reputation: float = 50.0
var doom: float = 50.0  # 0-100, lose at 100
var action_points: int = 3
var stationery: float = 100.0  # Office supplies, depletes with staff usage

# Technical Debt System (Issue #416)
# Accumulates from rushed research, increases failure risk, affects doom
var technical_debt: float = 0.0  # 0-100 scale
const MAX_TECHNICAL_DEBT: float = 100.0
const TECH_DEBT_DOOM_MULTIPLIER: float = 0.05  # 5% doom increase per debt point at high levels

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
var pending_hire_queue: Array[Researcher] = []  # Queue of candidates selected for hiring (FIFO)

# Purchased upgrades (one-time purchases)
var purchased_upgrades: Array[String] = []

# Game status
var turn: int = 0
var game_over: bool = false
var victory: bool = false
var game_seed_str: String = ""  # Renamed from 'seed' to avoid shadowing built-in function

# Lab mascot 🐱
var has_cat: bool = false

# Calendar system (Issue #472)
# Default: Game starts on Saturday, July 1st 2017 (configurable)
# Each turn = 1 day, 5 turns per work week (Mon-Fri)
# Note: July 1, 2017 was a Saturday, but we treat turn 0 as Monday
const DEFAULT_START_YEAR: int = 2017
const DEFAULT_START_MONTH: int = 7
const DEFAULT_START_DAY: int = 3  # Monday July 3rd, 2017 (first working day)
const TURNS_PER_WEEK: int = 5  # Work days per week

# Configurable start date (can be changed for scenarios/campaigns)
var start_year: int = DEFAULT_START_YEAR
var start_month: int = DEFAULT_START_MONTH
var start_day: int = DEFAULT_START_DAY

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

# Risk system (hidden accumulating consequences)
# See godot/docs/design/RISK_SYSTEM.md for design documentation
var risk_system  # Type is RiskPoolClass (preloaded)

# Academic travel system (Issue #468)
var paper_submissions: Array = []  # Array of PaperSubmissions.PaperSubmission
var attended_conferences: Array[String] = []  # Conference IDs attended this game year
var conference_year: int = 2017  # Track which year for conference attendance reset

func _init(game_seed: String = ""):
	game_seed_str = game_seed if game_seed != "" else str(Time.get_ticks_msec())

	# Initialize deterministic RNG from seed
	rng = RandomNumberGenerator.new()
	rng.seed = hash(game_seed_str)

	# Initialize doom system
	doom_system = DoomSystem.new()
	doom_system.current_doom = doom

	# Initialize risk system
	risk_system = RiskPoolClass.new()

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
	technical_debt = 0.0  # Reset tech debt (Issue #416)

	safety_researchers = 0
	capability_researchers = 0
	compute_engineers = 0
	managers = 0

	purchased_upgrades.clear()
	candidate_pool.clear()
	pending_hire_queue.clear()
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

	# Reset risk system
	if risk_system:
		risk_system.reset()

	# Reset academic travel system (Issue #468)
	paper_submissions.clear()
	attended_conferences.clear()
	conference_year = start_year

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
	if gains.has("technical_debt"):
		add_technical_debt(gains["technical_debt"])


# ============================================================================
# TECHNICAL DEBT SYSTEM (Issue #416)
# ============================================================================

func add_technical_debt(amount: float, reason: String = ""):
	"""Add technical debt (from rushed research, skipped reviews, etc.)"""
	var old_debt = technical_debt
	technical_debt = clamp(technical_debt + amount, 0.0, MAX_TECHNICAL_DEBT)

	if amount > 0 and reason != "":
		print("[TechDebt] +%.1f debt: %s (%.1f -> %.1f)" % [amount, reason, old_debt, technical_debt])

	# Update doom system's technical debt source if significant
	if doom_system and technical_debt >= 20.0:
		var debt_doom = (technical_debt - 20.0) * TECH_DEBT_DOOM_MULTIPLIER
		doom_system.doom_sources["technical_debt"] = debt_doom


func reduce_technical_debt(amount: float, reason: String = ""):
	"""Reduce technical debt (from audits, refactoring, etc.)"""
	var old_debt = technical_debt
	technical_debt = clamp(technical_debt - amount, 0.0, MAX_TECHNICAL_DEBT)

	if amount > 0 and reason != "":
		print("[TechDebt] -%.1f debt: %s (%.1f -> %.1f)" % [amount, reason, old_debt, technical_debt])

	# Update doom system
	if doom_system:
		if technical_debt < 20.0:
			doom_system.doom_sources["technical_debt"] = 0.0
		else:
			var debt_doom = (technical_debt - 20.0) * TECH_DEBT_DOOM_MULTIPLIER
			doom_system.doom_sources["technical_debt"] = debt_doom


func get_tech_debt_status() -> String:
	"""Get human-readable technical debt status"""
	if technical_debt < 10.0:
		return "minimal"
	elif technical_debt < 25.0:
		return "low"
	elif technical_debt < 50.0:
		return "moderate"
	elif technical_debt < 75.0:
		return "high"
	else:
		return "critical"


func get_tech_debt_color() -> Color:
	"""Get color representing technical debt severity"""
	if technical_debt < 10.0:
		return Color(0.3, 0.8, 0.3)  # Green
	elif technical_debt < 25.0:
		return Color(0.6, 0.8, 0.3)  # Yellow-green
	elif technical_debt < 50.0:
		return Color(0.9, 0.7, 0.2)  # Orange
	elif technical_debt < 75.0:
		return Color(0.9, 0.4, 0.2)  # Red-orange
	else:
		return Color(0.9, 0.2, 0.2)  # Red


func get_tech_debt_failure_chance() -> float:
	"""Get chance of technical failure based on debt level"""
	# No failure chance below 20 debt
	if technical_debt < 20.0:
		return 0.0
	# 2% chance per 10 debt above 20
	return (technical_debt - 20.0) * 0.002


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
	# Use researchers array if available (new system), otherwise use legacy counts
	var non_manager_staff: int
	if researchers.size() > 0:
		non_manager_staff = researchers.size()
	else:
		non_manager_staff = safety_researchers + capability_researchers + compute_engineers
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

# Paper Submission System Methods (Issue #468)
func add_paper_submission(paper: PaperSubmissions.PaperSubmission):
	"""Add a paper submission to tracking"""
	paper_submissions.append(paper)

func get_papers_by_status(status: int) -> Array:
	"""Get all papers with a specific status"""
	return PaperSubmissions.get_papers_by_status(paper_submissions, status)

func get_accepted_paper_for_conference(conf_id: String) -> PaperSubmissions.PaperSubmission:
	"""Get an accepted paper for a specific conference"""
	return PaperSubmissions.get_accepted_paper_for_conference(paper_submissions, conf_id)

func mark_conference_attended(conf_id: String):
	"""Mark a conference as attended this year"""
	if not attended_conferences.has(conf_id):
		attended_conferences.append(conf_id)

func has_attended_conference(conf_id: String) -> bool:
	"""Check if conference was already attended this year"""
	return attended_conferences.has(conf_id)

func check_conference_year_reset():
	"""Reset attended conferences when year changes"""
	var current_date = get_current_date()
	if current_date.year > conference_year:
		attended_conferences.clear()
		conference_year = current_date.year

# Calendar System Methods (Issue #472)
func get_current_week() -> int:
	"""Get the current week number (1-indexed)"""
	return (turn / TURNS_PER_WEEK) + 1

func get_day_of_week() -> int:
	"""Get day within the current week (1-5 for Mon-Fri)"""
	return (turn % TURNS_PER_WEEK) + 1

func get_weekday_name() -> String:
	"""Get the name of the current weekday"""
	var day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
	return day_names[turn % TURNS_PER_WEEK]

func get_current_date() -> Dictionary:
	"""Calculate the actual date from turn number
	Returns: {year, month, day, weekday, week_number, quarter}"""
	# Each turn = 1 weekday, so we need to account for weekends
	var weeks_elapsed = turn / TURNS_PER_WEEK
	var days_into_week = turn % TURNS_PER_WEEK

	# Total calendar days = weeks * 7 + days into current week
	var total_days = weeks_elapsed * 7 + days_into_week

	# Calculate date from start date (using configurable values)
	var year = start_year
	var month = start_month
	var day = start_day + total_days

	# Days in each month (non-leap year base, we'll handle leap years)
	var days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

	# Roll over months and years
	while day > days_in_month[month - 1]:
		# Check for leap year February
		var feb_days = 28
		if month == 2 and _is_leap_year(year):
			feb_days = 29

		var month_days = days_in_month[month - 1] if month != 2 else feb_days

		if day > month_days:
			day -= month_days
			month += 1
			if month > 12:
				month = 1
				year += 1

	var quarter = ((month - 1) / 3) + 1

	return {
		"year": year,
		"month": month,
		"day": day,
		"weekday": get_weekday_name(),
		"week_number": get_current_week(),
		"day_of_week": get_day_of_week(),
		"quarter": quarter
	}

func _is_leap_year(year: int) -> bool:
	"""Check if a year is a leap year"""
	return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

func get_formatted_date() -> String:
	"""Get a nicely formatted date string"""
	var date = get_current_date()
	var month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
					   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	return "%s %d, %d" % [month_names[date.month - 1], date.day, date.year]

func get_turn_display() -> String:
	"""Get the full turn display string for UI"""
	var date = get_current_date()
	var month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
					   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	# Format: "Week 12 | Wed Mar 20, 2024 | Day 3/5"
	return "Week %d | %s %s %d, %d | Day %d/%d" % [
		date.week_number,
		date.weekday.substr(0, 3),  # Mon, Tue, Wed, etc.
		month_names[date.month - 1],
		date.day,
		date.year,
		date.day_of_week,
		TURNS_PER_WEEK
	]

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

	# Get risk system data (for dev mode / save-load)
	var risk_data = {}
	if risk_system:
		risk_data = risk_system.to_dict()

	# Serialize researchers array
	var researcher_dicts = []
	for researcher in researchers:
		researcher_dicts.append(researcher.to_dict())

	# Serialize candidate pool
	var candidate_dicts = []
	for candidate in candidate_pool:
		candidate_dicts.append(candidate.to_dict())

	# Serialize paper submissions (Issue #468)
	var paper_dicts = []
	for paper in paper_submissions:
		paper_dicts.append(paper.to_dict())

	return {
		"money": money,
		"compute": compute,
		"research": research,
		"papers": papers,
		"reputation": reputation,
		"doom": doom,
		"doom_system": doom_data,
		"risk_system": risk_data,
		"action_points": action_points,
		"committed_ap": committed_ap,
		"reserved_ap": reserved_ap,
		"available_ap": get_available_ap(),
		"event_ap": get_event_ap(),
		"stationery": stationery,
		# Technical Debt System (Issue #416)
		"technical_debt": technical_debt,
		"tech_debt_status": get_tech_debt_status(),
		"tech_debt_color": get_tech_debt_color(),
		"tech_debt_failure_chance": get_tech_debt_failure_chance(),
		"safety_researchers": safety_researchers,
		"capability_researchers": capability_researchers,
		"compute_engineers": compute_engineers,
		"managers": managers,
		"total_staff": get_total_staff(),
		"management_capacity": get_management_capacity(),
		"unmanaged_count": get_unmanaged_count(),
		"turn": turn,
		"turn_display": get_turn_display(),
		"calendar": get_current_date(),
		"game_over": game_over,
		"victory": victory,
		"rival_labs": rival_summaries,
		"has_cat": has_cat,
		"purchased_upgrades": purchased_upgrades,
		"researchers": researcher_dicts,
		"candidate_pool": candidate_dicts,
		"paper_submissions": paper_dicts,
		"attended_conferences": attended_conferences
	}


func from_dict(data: Dictionary) -> void:
	"""Restore game state from serialized data (for save/load)"""
	# Core resources
	money = data.get("money", 100000)
	compute = data.get("compute", 0.0)
	research = data.get("research", 0.0)
	papers = data.get("papers", 0)
	reputation = data.get("reputation", 10.0)
	doom = data.get("doom", 50.0)
	action_points = data.get("action_points", 3)
	committed_ap = data.get("committed_ap", 0)
	reserved_ap = data.get("reserved_ap", 0)
	stationery = data.get("stationery", 100.0)
	technical_debt = data.get("technical_debt", 0.0)

	# Staff counts (legacy)
	safety_researchers = data.get("safety_researchers", 0)
	capability_researchers = data.get("capability_researchers", 0)
	compute_engineers = data.get("compute_engineers", 0)
	managers = data.get("managers", 0)

	# Game state
	turn = data.get("turn", 0)
	game_over = data.get("game_over", false)
	victory = data.get("victory", false)
	has_cat = data.get("has_cat", false)
	# Handle typed arrays properly
	purchased_upgrades.clear()
	for upgrade in data.get("purchased_upgrades", []):
		purchased_upgrades.append(upgrade)
	attended_conferences.clear()
	for conf in data.get("attended_conferences", []):
		attended_conferences.append(conf)

	# Restore doom system
	if doom_system and data.has("doom_system"):
		doom_system.from_dict(data["doom_system"])

	# Restore risk system
	if risk_system and data.has("risk_system"):
		risk_system.from_dict(data["risk_system"])

	# Restore researchers
	researchers.clear()
	if data.has("researchers"):
		for researcher_data in data["researchers"]:
			var researcher = Researcher.new()
			researcher.from_dict(researcher_data)
			researchers.append(researcher)

	# Restore candidate pool
	candidate_pool.clear()
	if data.has("candidate_pool"):
		for candidate_data in data["candidate_pool"]:
			var candidate = Researcher.new()
			candidate.from_dict(candidate_data)
			candidate_pool.append(candidate)

	# Restore paper submissions
	paper_submissions.clear()
	if data.has("paper_submissions"):
		for paper_data in data["paper_submissions"]:
			var paper = PaperSubmissions.PaperSubmission.from_dict(paper_data)
			paper_submissions.append(paper)

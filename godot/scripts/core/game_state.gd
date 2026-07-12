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
var doom_history: Array[float] = []  # Per-turn doom snapshots for the trend graph (#512)
# ADR-0002: area under the survival curve — sum of (100 - doom) over turns actually
# survived. The lexicographic score tiebreaker ("doom-years averted"); accrues in-engine.
var doom_integral: float = 0.0
var action_points: int = 3
var max_action_points: int = 3  # Per-turn AP cap; difficulty modifiers adjust this (game_manager._apply_difficulty_settings)
var stationery: float = 100.0  # Office supplies, depletes with staff usage

# Governance: institutional legitimacy the Liability Ledger bills against (ADR-0003).
# Added as an engine resource this lane; its full player-facing design is parked for
# workshop #2 (kickoff "governance is currently a name, not a system").
var governance: float = 50.0

# The Liability Ledger (ADR-0003): every mitigation is a loan. Instance state, rebuilt
# per game in reset(); compounding payables are the mortality guarantee (ADR-0002).
var ledger: Ledger

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
static var _empty_seed_counter: int = 0  # Keeps empty ("random") seeds unique within the same instant (#538)

# Lab mascot 🐱
var has_cat: bool = false

# Calendar system (Issue #472)
# Default: Game starts on Saturday, July 1st 2017 (configurable)
# Each turn = 1 day, 5 turns per work week (Mon-Fri)
# Note: July 1, 2017 was a Saturday, but we treat turn 0 as Monday
# L0 (#620): all turn<->calendar conversions live in Clock (scripts/core/clock.gd),
# the single time authority. The methods below are thin delegates.
const DEFAULT_START_YEAR: int = 2017
const DEFAULT_START_MONTH: int = 7
const DEFAULT_START_DAY: int = 3  # Monday July 3rd, 2017 (first working day)

# Configurable start date (can be changed for scenarios/campaigns)
var start_year: int = DEFAULT_START_YEAR
var start_month: int = DEFAULT_START_MONTH
var start_day: int = DEFAULT_START_DAY

# Research Quality System (Issue #500)
# Org-wide research stance. Feeds the RISK POOLS (not tech-debt/doom directly — see
# docs/design/RISK_SYSTEM.md & TWO_ACT_STRUCTURE.md). Risk magnitudes are per calendar-MONTH;
# turn_manager scales them by get_months_per_turn(). Speed multiplier is applied per-researcher.
# Sign convention: POSITIVE risk_per_month = adds risk to that pool (worse). Tune freely.
const RESEARCH_QUALITY := {
	"rushed":   {"research_multiplier": 2.0, "research_integrity_risk_per_month":  6.0, "capability_overhang_risk_per_month":  2.0},
	"standard": {"research_multiplier": 1.0, "research_integrity_risk_per_month":  0.0, "capability_overhang_risk_per_month":  0.0},
	"thorough": {"research_multiplier": 0.5, "research_integrity_risk_per_month": -3.0, "capability_overhang_risk_per_month": -3.0},
}
const DEFAULT_RESEARCH_QUALITY := "standard"
var research_quality_mode: String = DEFAULT_RESEARCH_QUALITY

# Turn phase tracking (fixes #418 - proper event sequencing)
enum TurnPhase { TURN_START, ACTION_SELECTION, TURN_PROCESSING, TURN_END }
var current_phase: TurnPhase = TurnPhase.ACTION_SELECTION
var pending_events: Array[Dictionary] = []  # Events that must be resolved before actions
var can_end_turn: bool = false

# Deterministic RNG for events
var rng: RandomNumberGenerator

# WS-0 determinism: per-game event-firing registry (was static in events.gd, which leaked
# across in-process games/replays and desynced state.rng). Fresh per GameState instance.
var triggered_events: Array[String] = []
var event_cooldowns: Dictionary = {}

# Queued actions for this turn
var queued_actions: Array[String] = []

# Rival labs
var rival_labs: Array = []  # Array of RivalLabs.RivalLab

# WS-C (ADR-0005): a seed = RNG seed + event schedule. Ordered list of scheduled causes
# ({turn, cause, target, magnitude}) applied per-turn by SeedSchedule. Causes touch sim
# INPUTS only, never doom. Part of the seed's identity, so it survives reset().
var event_schedule: Array = []

# Doom system (modular, extensible)
var doom_system: DoomSystem

# Risk system (hidden accumulating consequences)
# See godot/docs/design/RISK_SYSTEM.md for design documentation
var risk_system  # Type is RiskPoolClass (preloaded)

# Academic travel system (Issue #468)
var paper_submissions: Array = []  # Array of PaperSubmissions.PaperSubmission
var attended_conferences: Array[String] = []  # Conference IDs attended this game year
var conference_year: int = 2017  # Track which year for conference attendance reset

func _init(game_seed: String = "", schedule: Array = []):
	# WS-C (ADR-0005): schedule is part of seed identity; duplicated so external mutation
	# can't alias it, and deliberately NOT cleared by reset().
	event_schedule = schedule.duplicate(true)
	if game_seed != "":
		game_seed_str = game_seed
	else:
		# Empty = random new game. Combine high-res time with a static counter so two
		# games created in the same instant (tests, rapid restarts) get unique seeds (#538).
		_empty_seed_counter += 1
		game_seed_str = "%d-%d" % [Time.get_ticks_usec(), _empty_seed_counter]

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
	"""Reset to starting state. Starting resources come from the Balance surface
	("starting_resources.*", L9 #621); fallbacks are the pre-L9 literals.
	Money default 245000 is from player feedback (issue #436)."""
	money = Balance.num("starting_resources.money", 245000.0)
	compute = Balance.num("starting_resources.compute", 100.0)
	research = Balance.num("starting_resources.research", 0.0)
	papers = Balance.num("starting_resources.papers", 0.0)
	reputation = Balance.num("starting_resources.reputation", 50.0)
	doom = Balance.num("starting_resources.doom", 50.0)
	action_points = Balance.inum("starting_resources.action_points", 3)
	stationery = Balance.num("starting_resources.stationery", 100.0)
	governance = Balance.num("starting_resources.governance", 50.0)
	ledger = Ledger.new()  # ADR-0003: fresh ledger per game
	technical_debt = 0.0  # Reset tech debt (Issue #416)
	research_quality_mode = DEFAULT_RESEARCH_QUALITY  # Issue #500

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
	doom_integral = 0.0  # ADR-0002: reset the survival-curve accumulator
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

	# Seed doom trend history with the starting value, so the graph shows t=0 (#512)
	doom_history.clear()
	doom_history.append(doom)

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


# ============================================================================
# RESEARCH QUALITY SYSTEM (Issue #500)
# ============================================================================

func get_months_per_turn() -> float:
	"""Calendar months represented by one turn — delegates to Clock, the single
	time authority (L0 #620). Fixed at 1.0 until the variable game-length system
	lands (see docs/design/TWO_ACT_STRUCTURE.md)."""
	return Clock.months_per_turn()


func get_research_multiplier() -> float:
	"""Per-researcher research-speed multiplier for the current quality mode."""
	return RESEARCH_QUALITY.get(research_quality_mode, RESEARCH_QUALITY[DEFAULT_RESEARCH_QUALITY])["research_multiplier"]


func set_research_quality(mode: String) -> void:
	"""Set the org-wide research stance. Unknown modes are ignored (kept standard)."""
	if RESEARCH_QUALITY.has(mode):
		research_quality_mode = mode
	else:
		ErrorHandler.warning(ErrorHandler.Category.RESOURCES, "Unknown research quality mode", {"mode": mode})


func apply_research_quality_risk(current_turn: int) -> void:
	"""Apply this turn's research-quality contributions to the risk pools.
	Per-month magnitudes scaled to per-turn via get_months_per_turn() so total
	accrued risk is invariant across game length (see TWO_ACT_STRUCTURE.md)."""
	if risk_system == null:
		return
	var q = RESEARCH_QUALITY.get(research_quality_mode, RESEARCH_QUALITY[DEFAULT_RESEARCH_QUALITY])
	var mpt: float = get_months_per_turn()
	var integrity_delta: float = q["research_integrity_risk_per_month"] * mpt
	var overhang_delta: float = q["capability_overhang_risk_per_month"] * mpt
	var src: String = "research_quality:%s" % research_quality_mode
	if integrity_delta != 0.0:
		risk_system.add_risk("research_integrity", integrity_delta, src, current_turn)
	if overhang_delta != 0.0:
		risk_system.add_risk("capability_overhang", overhang_delta, src, current_turn)


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

# Calendar System Methods (Issue #472) — thin delegates to Clock, the single
# time authority (L0 #620). Values unchanged: turn = 1 workday.
func get_current_week() -> int:
	"""Get the current week number (1-indexed)"""
	return Clock.week_number(turn)

func get_day_of_week() -> int:
	"""Get day within the current week (1-5 for Mon-Fri)"""
	return Clock.day_of_week(turn)

func get_weekday_name() -> String:
	"""Get the name of the current weekday"""
	return Clock.weekday_name(turn)

func get_current_date() -> Dictionary:
	"""Calculate the actual date from turn number
	Returns: {year, month, day, weekday, week_number, quarter}"""
	return Clock.date_for_turn(turn, start_year, start_month, start_day)

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
		Clock.TURNS_PER_WEEK
	]

func record_doom_history() -> void:
	"""Append the current (post-resolution) doom to the per-turn history (#512 trend graph)."""
	doom_history.append(doom)


func accrue_survival_credit() -> void:
	"""ADR-0002: credit this survived turn to the doom-integral score tiebreaker.
	Call only for turns the player actually survived (game not over); a turn that
	ended the game earns no stewardship credit."""
	doom_integral += 100.0 - doom


# --- Scoring (ADR-0002) --------------------------------------------------------
# The engine is the sole scoring authority. Score is the tuple
# (turns_survived, doom_integral), compared lexicographically: turns strictly
# dominant, doom-integral as tiebreak. FLOWS ONLY — no stock the player holds at
# death (money, papers, staff, reputation) may ever affect the score.
static func score_tuple(state: Dictionary) -> Array:
	return [int(state.get("turn", 0)), int(round(state.get("doom_integral", 0.0)))]


static func compare_score(a_turns: int, a_integral: int, b_turns: int, b_integral: int) -> int:
	"""Lexicographic compare. Returns 1 if A ranks above B, -1 if below, 0 if equal."""
	if a_turns != b_turns:
		return 1 if a_turns > b_turns else -1
	if a_integral != b_integral:
		return 1 if a_integral > b_integral else -1
	return 0


static func format_score(turns: int, integral: int) -> String:
	return "Turn %d · %d" % [turns, integral]


# ============================================================================
# SERIALIZATION — SAVE/LOAD CONVENTION (L7, #618)
#
# to_dict() is BOTH the UI payload and the save-file state body; from_dict()
# must rebuild an equivalent GameState from it. The invariant the round-trip
# test enforces: from_dict(to_dict()) — including a JSON stringify/parse hop —
# yields a state whose to_dict() is deep-equal AND whose next turn is
# turn-for-turn identical (rng stream included).
#
# Rules for registering new state (L2 workstreams and later systems):
#   1. Every stateful subsystem owns its own to_dict()/from_dict() pair
#      (see Ledger, DoomSystem, RiskPool, Researcher, RivalLab, PaperSubmission).
#   2. GameState composes them under ONE stable top-level key per subsystem;
#      from_dict() restores under the same key. Add both sides in the same PR.
#   3. JSON-safe values only: String/float/int/bool/Array/Dictionary. No
#      Callables or object refs. int64s that can exceed 2^53 (e.g. rng state)
#      travel as Strings, because JSON parses every number back as float.
#   4. from_dict() casts explicitly (int()/float()/String()) and loop-appends
#      into typed arrays — JSON hands back untyped floats and untyped Arrays.
#   5. Derived/display values (turn_display, tech_debt_color, rival summaries,
#      available_ap, ...) are recomputed, never restored.
#   6. Extend tests/unit/test_save_load_roundtrip.gd so the new state is
#      exercised before the save point.
#
# Replay (ADR-0006) is unaffected: it rebuilds from turn 0. This is SNAPSHOT
# fidelity for mid-game save/load (and later DQ-11 fork/divergence).
# ============================================================================

func to_dict() -> Dictionary:
	"""Serialize state for UI + save/load (see convention block above)"""
	var rival_summaries = []
	var rival_full_dicts = []
	for rival in rival_labs:
		rival_summaries.append(RivalLabs.get_rival_summary(rival))
		rival_full_dicts.append(rival.to_dict())

	# Sync doom from doom system
	if doom_system:
		doom = doom_system.current_doom

	# Doom system data: the persistent core comes from doom_system.to_dict() (so
	# multipliers/modifiers round-trip — previously hand-rolled and lossy), plus
	# derived display strings the UI reads.
	var doom_data = {}
	if doom_system:
		doom_data = doom_system.to_dict()
		doom_data["doom"] = doom
		doom_data["doom_trend"] = doom_system._get_doom_trend()
		doom_data["doom_status"] = doom_system.get_doom_status()
		doom_data["momentum_description"] = doom_system.get_momentum_description()
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

	# Pending-hire queue (FIFO of selected candidates)
	var pending_hire_dicts = []
	for candidate in pending_hire_queue:
		pending_hire_dicts.append(candidate.to_dict())

	# Serialize paper submissions (Issue #468)
	var paper_dicts = []
	for paper in paper_submissions:
		paper_dicts.append(paper.to_dict())

	return {
		"money": money,
		"compute": compute,
		"research": research,
		"research_quality_mode": research_quality_mode,  # Issue #500
		"papers": papers,
		"reputation": reputation,
		"governance": governance,
		"ledger": ledger.to_dict() if ledger else {},
		"doom": doom,
		"doom_history": doom_history.duplicate(),  # #512 trend graph
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
		"doom_integral": doom_integral,
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
		"attended_conferences": attended_conferences,
		# --- Full-fidelity save/load fields (L7, #618) ---
		"game_seed": game_seed_str,
		"rng_state": str(rng.state) if rng else "",  # int64 as String (JSON floats lose precision past 2^53)
		"event_schedule": event_schedule.duplicate(true),  # WS-C: part of seed identity
		"triggered_events": triggered_events.duplicate(),  # WS-0 registry (was forgotten by from_dict)
		"event_cooldowns": event_cooldowns.duplicate(),    # WS-0 registry (was forgotten by from_dict)
		"queued_actions": queued_actions.duplicate(),
		"pending_events": pending_events.duplicate(true),  # event defs are pure-data dicts
		"current_phase": current_phase,
		"can_end_turn": can_end_turn,
		"used_event_ap": used_event_ap,
		"max_action_points": max_action_points,  # difficulty modifier — next-turn AP base
		"conference_year": conference_year,
		"start_year": start_year,
		"start_month": start_month,
		"start_day": start_day,
		"pending_hire_queue": pending_hire_dicts,
		"rival_labs_full": rival_full_dicts  # "rival_labs" stays display summaries for the UI
	}


func from_dict(data: Dictionary) -> void:
	"""Restore game state from serialized data (for save/load).
	L7 (#618): full-fidelity — see SERIALIZATION CONVENTION block above to_dict().
	Explicit int()/float()/String() casts throughout: JSON parses every number as float."""
	# Core resources
	money = float(data.get("money", 100000.0))
	compute = float(data.get("compute", 0.0))
	research = float(data.get("research", 0.0))
	research_quality_mode = String(data.get("research_quality_mode", DEFAULT_RESEARCH_QUALITY))  # Issue #500
	papers = float(data.get("papers", 0.0))
	reputation = float(data.get("reputation", 10.0))
	governance = float(data.get("governance", 50.0))  # was forgotten pre-L7
	doom = float(data.get("doom", 50.0))
	doom_history.clear()
	for d in data.get("doom_history", []):
		doom_history.append(float(d))
	action_points = int(data.get("action_points", 3))
	max_action_points = int(data.get("max_action_points", 3))
	committed_ap = int(data.get("committed_ap", 0))
	reserved_ap = int(data.get("reserved_ap", 0))
	used_event_ap = int(data.get("used_event_ap", 0))
	stationery = float(data.get("stationery", 100.0))
	technical_debt = float(data.get("technical_debt", 0.0))

	# Staff counts (legacy)
	safety_researchers = int(data.get("safety_researchers", 0))
	capability_researchers = int(data.get("capability_researchers", 0))
	compute_engineers = int(data.get("compute_engineers", 0))
	managers = int(data.get("managers", 0))

	# Game state
	turn = int(data.get("turn", 0))
	doom_integral = float(data.get("doom_integral", 0.0))
	game_over = bool(data.get("game_over", false))
	victory = bool(data.get("victory", false))
	has_cat = bool(data.get("has_cat", false))
	# Handle typed arrays properly
	purchased_upgrades.clear()
	for upgrade in data.get("purchased_upgrades", []):
		purchased_upgrades.append(String(upgrade))
	attended_conferences.clear()
	for conf in data.get("attended_conferences", []):
		attended_conferences.append(String(conf))

	# Calendar / conference-year (scenario start dates travel with the save)
	start_year = int(data.get("start_year", start_year))
	start_month = int(data.get("start_month", start_month))
	start_day = int(data.get("start_day", start_day))
	conference_year = int(data.get("conference_year", start_year))

	# Turn-phase / planning state (mid-turn snapshot fidelity)
	current_phase = int(data.get("current_phase", TurnPhase.ACTION_SELECTION)) as TurnPhase
	can_end_turn = bool(data.get("can_end_turn", false))
	queued_actions.clear()
	for a in data.get("queued_actions", []):
		queued_actions.append(String(a))
	pending_events.clear()
	for ev in data.get("pending_events", []):
		if ev is Dictionary:
			pending_events.append(ev.duplicate(true))

	# WS-0 event-firing registry (the known-forgotten pair this lane exists for)
	triggered_events.clear()
	for eid in data.get("triggered_events", []):
		triggered_events.append(String(eid))
	event_cooldowns.clear()
	var cooldown_data = data.get("event_cooldowns", {})
	if cooldown_data is Dictionary:
		for eid in cooldown_data.keys():
			event_cooldowns[String(eid)] = int(cooldown_data[eid])

	# WS-C scheduled causes (seed identity — survives reset(), must survive load too)
	var schedule_data = data.get("event_schedule", null)
	if schedule_data is Array:
		event_schedule = []
		for cause in schedule_data:
			if cause is Dictionary:
				var c = cause.duplicate(true)
				if c.has("turn"):
					c["turn"] = int(c["turn"])
				event_schedule.append(c)

	# Deterministic RNG: reseed from the seed string, then restore the exact
	# stream position. Without this, a loaded game diverges from an unsaved
	# continuation on the very next randf().
	var seed_str = String(data.get("game_seed", ""))
	if seed_str != "":
		game_seed_str = seed_str
		if rng == null:
			rng = RandomNumberGenerator.new()
		rng.seed = hash(game_seed_str)
	var rng_state_data = data.get("rng_state", "")
	if rng and rng_state_data is String and rng_state_data != "":
		rng.state = rng_state_data.to_int()
	elif rng and (rng_state_data is int or rng_state_data is float):
		rng.state = int(rng_state_data)

	# Restore the Liability Ledger (WS-1 — entries were forgotten pre-L7)
	if ledger == null:
		ledger = Ledger.new()
	ledger.from_dict(data.get("ledger", {}))

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

	# Restore pending-hire queue (FIFO)
	pending_hire_queue.clear()
	if data.has("pending_hire_queue"):
		for candidate_data in data["pending_hire_queue"]:
			var pending = Researcher.new()
			pending.from_dict(candidate_data)
			pending_hire_queue.append(pending)

	# Restore rival labs (full state; "rival_labs" key is display summaries only)
	if data.has("rival_labs_full"):
		rival_labs.clear()
		for rival_data in data["rival_labs_full"]:
			if rival_data is Dictionary:
				rival_labs.append(RivalLabs.RivalLab.from_dict(rival_data))

	# Restore paper submissions
	paper_submissions.clear()
	if data.has("paper_submissions"):
		for paper_data in data["paper_submissions"]:
			var paper = PaperSubmissions.PaperSubmission.from_dict(paper_data)
			paper_submissions.append(paper)

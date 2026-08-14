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

# ============================================================================
# TYPED REPUTATION (ADR-0010 R2 atoms B7/B8/B9) -- ADDITIVE, first pass.
#
# AUTHORITY RULE (do not "improve" this into a derived sum): the legacy scalar
# `reputation` above stays AUTHORITATIVE and writable. ~20 sites write it
# (spend_resources below, media_system.gd:244/416, ledger entries carrying
# currency "reputation"); a derived-sum shim breaks every one of them on write.
# The typed dimensions here are ADDITIVE modifiers read through rep_for(); no
# reader is wired yet (readers switch on one at a time, B9).
#
# Three bearers: ORG (the lab), OPERATOR (the founder, personally) and
# EMPLOYEE (per-person, stored on Researcher.rep -- see researcher.gd).
# Two kinds per bearer: safety / capability standing.
# ============================================================================
const REP_KIND_SAFETY := "safety"
const REP_KIND_CAPABILITY := "capability"
const REP_KINDS: Array = [REP_KIND_SAFETY, REP_KIND_CAPABILITY]

const REP_WHO_ORG := "org"
const REP_WHO_OPERATOR := "operator"
const REP_WHO_EMPLOYEE := "employee"  # `who` for an employee is their name/candidate_id

## COST ROUTING RULE -- ruled by Pip, 2026-07-27 (answers ADR-0010 R2 section 6
## question 1, "which pocket pays when something costs reputation?").
##   Reputation COSTS bill the ORG by default. They bill the FOUNDER (operator)
##   ONLY when the event/action EXPLICITLY names the founder.
## One constant + one helper (rep_cost_bearer) so the rule has a single home;
## every future rep-cost site routes through it rather than re-deciding.
const REP_COST_DEFAULT_BEARER := REP_WHO_ORG
const REP_BEARER_KEY := "rep_bearer"        # explicit override on an action/event def
const REP_FOUNDER_FLAG := "targets_founder"  # boolean flag form of the same intent

var rep_org: Dictionary = {REP_KIND_SAFETY: 0.0, REP_KIND_CAPABILITY: 0.0}
var rep_operator: Dictionary = {REP_KIND_SAFETY: 0.0, REP_KIND_CAPABILITY: 0.0}
var doom_history: Array[float] = []  # Per-turn doom snapshots for the trend graph (#512)
# ADR-0002: area under the survival curve -- sum of (100 - doom) over turns actually
# survived. The lexicographic score tiebreaker ("doom-years averted"); accrues in-engine.
var doom_integral: float = 0.0

# ADR-0015 / DQ-21 world-state intermediaries: doom is computed from THESE (never written
# directly). Actions/events/rivals write intermediaries; DoomSystem reads them each day tick
# and sums the named streams into the doom rate. Every one is L6-attributable (guard rule).
var ambient_risk: float = 0.0                  # baseline stream -- year-keyed background floor
var frontier_capability: Dictionary = {}       # actor_id -> capability level; "player" is the named slice
var general_capability: float = 0.0            # diffusion stream -- chronic commoditized floor (ratchet)
var global_compute: float = 0.0                # the slow ocean (schedule furniture; no own doom term)
var dedicated_ai_compute: float = 0.0          # compute stream -- the controllable fleet
var safety_absorption: float = 0.0             # offsets frontier in the overhang gap (accumulated safety)
var global_alarm: float = 0.0                  # alarm stream (small relief) + typed-damper gate
var global_panic: float = 0.0                  # panic stream -- social accelerant
var political_pressure: float = 0.0            # signed disposition; gate only (no stream of its own)
var doom_dampers: Array = []                   # typed dampers: {target, strength, expires_turn}
var doom_pulses: Array = []                    # ADR-0005 scheduled pulse envelopes (v1: none)
var sacred_chain_log: Array = []               # completed sacred-object chains (trend-invariant exemption)

## player_frontier -- the DQ-22-read alias for frontier_capability["player"].
var player_frontier: float:
	get:
		return float(frontier_capability.get("player", 0.0))

# T2 / ADR-0011 amendment (a): the per-turn ACTION POINT pool is DELETED. There is no
# `action_points` field, no per-turn grant, no AP in any cost dict. The founder currency is
# ATTENTION, granted per PLAN MONTH and held by month_plan (MonthPlan), typed 2-way into
# planning vs operating hours. `attention_per_month` is the grant size -- difficulty scales
# THIS now (it used to scale max_action_points).
#
# 2026-08-12 ruling: this field is an INPUT to the budget, not the budget. Do NOT read it
# to open a month -- call `capacity_for_month()` (-> Capacity.derive), which is the single
# derivation point. Difficulty, scenario packs and save/load still WRITE here: this is the
# grant modifier they set, and the derivation reads it back out as `modifiers.grant`. The
# two numbers are identical today by contract, and the point of the indirection is that the
# day they stop being identical, exactly one function changes.
var attention_per_month: int = 20
var stationery: float = 100.0  # Office supplies, depletes with staff usage

# Governance: institutional legitimacy the Liability Ledger bills against (ADR-0003).
# Added as an engine resource this lane; its full player-facing design is parked for
# workshop #2 (kickoff "governance is currently a name, not a system").
var governance: float = 50.0

# The Liability Ledger (ADR-0003): every mitigation is a loan. Instance state, rebuilt
# per game in reset(); compounding payables are the mortality guarantee (ADR-0002).
var ledger: Ledger

# Standing financing offers (ADR-0013 / L5 #616): the current menu minted by
# FinanceEngine.generate_offers when the player seeks debt/funding. TRANSIENT (not
# serialized): offers are cheap to regenerate and carry their own expiry_turn, so a
# save/load simply drops any pending menu (the player re-seeks). Kept off to_dict so
# the L7 save round-trip stays byte-stable.
var financing_offers: Array = []

# Standing LEASE offers (#791 / #811 item 1): the 3-option first-lease menu minted by
# FinanceEngine.generate_lease_offers. TRANSIENT, exactly like financing_offers -- they
# carry their own expiry_turn and are cheap to re-tour, so save/load drops a pending menu.
var lease_offers: Array = []

# --- Office economy (#791; see scripts/core/office.gd) -------------------------
# The office is the early game's shape-giver: tier 0 (bedroom/basement) hard-caps hires,
# so growing FORCES the first lease spend. Signing LOCKS the choice in v1 (no moving
# mechanic yet -- office_locked is the seam the future move instrument clears).
var office_id: String = "bedroom"
var office_name: String = "Bedroom / basement"
var office_tier: int = 0
var office_hire_cap: int = 2            # SIM number. The render layer's desk_slots is NOT read here (ADR-0018).
var office_rent_per_month: float = 0.0  # Charged on the payroll rail at the month boundary.
var office_locked: bool = false         # true once a lease is signed; nothing shipped flips it back.
var office_upgrades: Array = []         # ADDITIVE String ids (Office.apply_upgrade). Empty in v1 by design.

# Hype: the "loud on the internet" standing that FinanceEngine already prices against
# (finance_engine.gd:69 read it duck-typed with a 0.0 fallback; vc_equity gates on
# min_hype 25). Promoting it to a real field is behaviour-NEUTRAL at 0 and gives the
# scouting shitpost action somewhere honest to write (#811 item 1).
var hype: float = 0.0

# The month plan layer (L1 / ADR-0009): the founder currency Attention, the crisp reserve,
# and duration-bearing queued strategic actions. The plan cadence is monthly; the turn above
# is the day-grained resolution tick. Rebuilt per game in reset().
var month_plan: MonthPlan

# The hiring pipeline (Phase B / BUILD_BRIEF_HIRING_PIPELINE): source -> interview -> offer
# -> onboard. Instance state (campaigns, in-flight duration jobs), rebuilt per game in
# reset(). Deterministic; spends Attention through month_plan and mints promises on the ledger.
var hiring: HiringPipeline

# EE-8 (ADR-0012): chronological CONTRIBUTING-CAUSE log for root-cause death
# attribution. Ledger defaults, governance deficits, secret exposures, rep collapse
# and funding starvation are appended here with turn stamps, so a death can be traced
# to its causal chain (a doom/rep death downstream of a default is a LEDGER death --
# see DeathAttribution.classify). Recording only: nothing reads this during play,
# so it can never change run outcomes.
var cause_log: Array = []
var rep_collapse_noted: bool = false       # one-shot: first crossing below REP_COLLAPSE_THRESHOLD
var funding_starvation_noted: bool = false # one-shot per starvation episode (reset on recovery)
const REP_COLLAPSE_THRESHOLD: float = 10.0

# Technical Debt System (Issue #416)
# Accumulates from rushed research, increases failure risk, affects doom
var technical_debt: float = 0.0  # 0-100 scale
const MAX_TECHNICAL_DEBT: float = 100.0
const TECH_DEBT_DOOM_MULTIPLIER: float = 0.05  # 5% doom increase per debt point at high levels

# (T2: the per-turn AP reserve trio -- committed_ap / reserved_ap / used_event_ap -- is
# DELETED. Its job is done by MonthPlan's attention_spent / attention_reserved /
# reserve_used, which are per PLAN MONTH and survive the day tick.)

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

# ============================================================================
# WORKSTREAM SUBSTRATE (ADR-0011 s3/s4, lane T1 / issue #613)
# The directed-work layer the month plan was pointing at (month_plan.gd:21). Workstreams
# are started off the data-driven backlog (WorkstreamBacklog), researchers are committed
# to them at plan speed, and effort accrues per person per tick (turn_manager
# _step_workstream_accrual). Everything here is INERT until the player starts a
# workstream: with an empty list the accrual hook only records self-directed effort and
# bills no compute, so an untouched run is byte-identical to the pre-substrate build.
#
# NOT in this lane: manager shields. (AP-pool deletion / Attention migration and the 2-way
# founder-hour typing landed in T2; nothing below reads either -- workstream effort is a
# STAFF currency, never founder Attention.)
# ============================================================================
var workstreams: Array = []                          # Array[Workstream], live + finished
var workstream_backlog_taken: Array[String] = []     # backlog entry ids already started
var workstream_serial: int = 0                       # pure counter for workstream ids (no rng)
var researcher_id_serial: int = 0                    # pure counter for minted staff ids
# Self-directed effort tally by topic key -> {"actual": float, "reported": float}. The
# REPORTED half is the optimistic claim (Researcher.self_report_optimism); audits
# ground-truth reported vs actual in a later lane (ruled 2026-07-27, review-by
# 2026-08-31). Nothing consumes "reported" today -- it only serializes and displays.
var self_directed_progress: Dictionary = {}

# Purchased upgrades (one-time purchases)
var purchased_upgrades: Array[String] = []

# Game status
var turn: int = 0
var game_over: bool = false
var victory: bool = false
# Org form (early-game choice, part of DQ-19 char/org creation): "nonprofit" | "for_profit".
# Set from GameConfig at game start (game_manager); read by FinanceEngine.context_from_state
# to gate instruments (e.g. vc_equity is for_profit-only) and scale debt pricing.
var org_type: String = "nonprofit"
var game_seed_str: String = ""  # Renamed from 'seed' to avoid shadowing built-in function
static var _empty_seed_counter: int = 0  # Keeps empty ("random") seeds unique within the same instant (#538)

# Lab mascot
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
# Org-wide research stance. Feeds the RISK POOLS (not tech-debt/doom directly -- see
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
	# Typed dims start at zero: they are ADDITIVE modifiers on top of the
	# authoritative scalar, not a decomposition of it (ADR-0010 B9).
	rep_org = {REP_KIND_SAFETY: 0.0, REP_KIND_CAPABILITY: 0.0}
	rep_operator = {REP_KIND_SAFETY: 0.0, REP_KIND_CAPABILITY: 0.0}
	doom = Balance.num("starting_resources.doom", 50.0)
	attention_per_month = Balance.inum("attention.per_month", 20)
	stationery = Balance.num("starting_resources.stationery", 100.0)
	governance = Balance.num("starting_resources.governance", 50.0)
	hype = Balance.num("starting_resources.hype", 0.0)
	# Office economy (#791): back to the bedroom, cap and all. Clears any signed lease.
	financing_offers.clear()
	lease_offers.clear()
	Office.apply_start(self)
	ledger = Ledger.new()  # ADR-0003: fresh ledger per game
	# L1/ADR-0009: fresh month plan, opened with the first month's Attention grant. The plan
	# month ordinal is derived from the calendar (turn 0 -> ordinal 0).
	month_plan = MonthPlan.new()
	# Ordinal 0 is the run's START month by definition, so the derivation is asked about
	# turn 0's calendar month, not `turn` (reset() zeroes `turn` further down, and a
	# restart would otherwise ask about the month the previous run died in).
	var start_capacity: Dictionary = capacity_for_month(Clock.month_index(0, start_year, start_month, start_day))
	month_plan.begin_month(int(start_capacity["value"]), 0)
	hiring = HiringPipeline.new()  # Phase B: fresh pipeline per game (created BEFORE candidates
	                               # are populated so add_candidate can stamp their ids)
	cause_log.clear()      # EE-8: fresh attribution trail per game
	rep_collapse_noted = false
	funding_starvation_noted = false
	technical_debt = 0.0  # Reset tech debt (Issue #416)
	research_quality_mode = DEFAULT_RESEARCH_QUALITY  # Issue #500

	# ADR-0015 / DQ-21: fresh world-state intermediaries. 2017 spawn starts low and slow
	# (ambient_risk climbs with the schedule; frontier/absorption accumulate from play).
	ambient_risk = Balance.num("doom.base_per_turn", 0.06)
	frontier_capability = {"player": 0.0}
	general_capability = 0.0
	global_compute = 0.0
	dedicated_ai_compute = compute
	safety_absorption = 0.0
	global_alarm = 0.0
	global_panic = 0.0
	political_pressure = 0.0
	doom_dampers.clear()
	doom_pulses.clear()
	sacred_chain_log.clear()

	safety_researchers = 0
	capability_researchers = 0
	compute_engineers = 0
	managers = 0

	purchased_upgrades.clear()
	candidate_pool.clear()
	pending_hire_queue.clear()
	researchers.clear()

	# Workstream substrate: a new run starts with an empty board and the full backlog.
	workstreams.clear()
	workstream_backlog_taken.clear()
	workstream_serial = 0
	researcher_id_serial = 0
	self_directed_progress.clear()

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


# ============================================================================
# TYPED REPUTATION ACCESSORS (ADR-0010 B7/B9)
# Read side is total: an unknown kind or an unknown bearer reads 0.0 rather
# than erroring, matching ResourceAccessor.read's "unknown name reads 0.0"
# convention. Callers that need the distinction gate on has_rep_bearer().
# ============================================================================

func rep_for(kind: String, who: String = REP_WHO_ORG) -> float:
	"""Typed reputation for one kind ("safety"/"capability") held by one bearer
	("org", "operator", or an employee's name/candidate_id). 0.0 for unknowns.
	ADDITIVE only -- the legacy `reputation` scalar is unaffected by this read."""
	if not (kind in REP_KINDS):
		return 0.0
	match who:
		REP_WHO_ORG:
			return float(rep_org.get(kind, 0.0))
		REP_WHO_OPERATOR:
			return float(rep_operator.get(kind, 0.0))
	var person = _find_researcher_by_handle(who)
	if person == null:
		return 0.0
	return person.rep_for(kind)


func rep_dims(who: String = REP_WHO_ORG) -> Dictionary:
	"""All typed dims for one bearer, as a DETACHED COPY (callers must never get a
	live reference into state -- a mutated copy would silently rewrite the model)."""
	var out: Dictionary = {}
	for kind in REP_KINDS:
		out[kind] = rep_for(String(kind), who)
	return out


func has_rep_bearer(who: String) -> bool:
	"""True if `who` names a bearer this state knows (org, operator, or an
	employed researcher). Unknown bearers still READ as 0.0 via rep_for()."""
	if who == REP_WHO_ORG or who == REP_WHO_OPERATOR:
		return true
	return _find_researcher_by_handle(who) != null


func add_rep(kind: String, amount: float, who: String = REP_WHO_ORG) -> void:
	"""Additive typed-rep write. No-op for an unknown kind or unknown bearer --
	typed rep is a modifier layer, so a missed write can never corrupt the run."""
	if not (kind in REP_KINDS):
		return
	match who:
		REP_WHO_ORG:
			rep_org[kind] = float(rep_org.get(kind, 0.0)) + amount
			return
		REP_WHO_OPERATOR:
			rep_operator[kind] = float(rep_operator.get(kind, 0.0)) + amount
			return
	var person = _find_researcher_by_handle(who)
	if person != null:
		person.add_rep(kind, amount)


static func rep_cost_bearer(spec: Dictionary) -> String:
	"""WHICH POCKET PAYS a reputation cost. Pip's ruling, 2026-07-27 (ADR-0010 R2
	section 6 q1): the ORG pays by default; the FOUNDER pays only when the
	event/action explicitly names the founder. `spec` is the action/event
	definition dict; it opts in with either "rep_bearer": "operator"/"founder"
	or "targets_founder": true. Anything else -- including an empty dict -- is
	the org. Single home for the rule; do not re-decide it at call sites."""
	if spec == null or spec.is_empty():
		return REP_COST_DEFAULT_BEARER
	var explicit := String(spec.get(REP_BEARER_KEY, ""))
	if explicit == REP_WHO_OPERATOR or explicit == "founder":
		return REP_WHO_OPERATOR
	if explicit == REP_WHO_ORG:
		return REP_WHO_ORG
	if bool(spec.get(REP_FOUNDER_FLAG, false)):
		return REP_WHO_OPERATOR
	return REP_COST_DEFAULT_BEARER


func bill_reputation(kind: String, amount: float, spec: Dictionary = {}) -> String:
	"""Charge `amount` of typed reputation of `kind` to whichever pocket
	rep_cost_bearer(spec) names, and return that bearer. Deliberately does NOT
	touch the legacy `reputation` scalar -- that stays authoritative and is
	still deducted by spend_resources()/the ledger path."""
	var bearer := rep_cost_bearer(spec)
	add_rep(kind, -amount, bearer)
	return bearer


static func _load_rep_dims(raw) -> Dictionary:
	"""Deserialize one typed-rep bearer dict: every REP_KINDS key present, every
	value a re-snapped float, unknown keys dropped (JSON hands numbers back as
	floats; re-snapping is idempotent -- see the SERIALIZATION block)."""
	var out: Dictionary = {}
	for kind in REP_KINDS:
		var value := 0.0
		if raw is Dictionary and raw.has(kind):
			value = float(raw[kind])
		out[kind] = DoomSystem._snap(value)
	return out


func _find_researcher_by_handle(handle: String):
	"""Employed researcher matching a `who` handle (candidate_id first, then
	display name). null when nothing matches."""
	if handle == "":
		return null
	for r in researchers:
		if r.candidate_id != "" and r.candidate_id == handle:
			return r
	for r in researchers:
		if r.researcher_name == handle:
			return r
	return null


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
	# T2: `attention` is the founder currency and lives on the month plan, not on a per-turn
	# pool. An un-typed cost dict bills OPERATING hours (see MonthPlan.spend_attention).
	if costs.has("attention"):
		if month_plan == null:
			return false
		if not month_plan.can_spend_hours(int(costs["attention"]), _cost_hour_type(costs)):
			return false
	return true


func _cost_hour_type(costs: Dictionary) -> String:
	"""Which founder hour token a cost dict bills. Data may name it explicitly with an
	`hour_type` key -- either a 2-way FAMILY ("planning" | "operating") or a 4-way KIND
	("doors" | "approvals" | "audits" | "reserve"); MonthPlan.family_of/kind_of resolve
	either. Anything unrecognised is OPERATING (presence work).
	This is ONE of the two subdivision points the 4-way lane widened (the other is
	GameActions.hour_type); the 40 call sites stayed untouched.

	DEFAULT ASYMMETRY -- KEPT DELIBERATELY (T2 judgment call 4, re-examined by this lane and
	upheld). A bare cost dict handed to spend_resources defaults to OPERATING; a queued
	ACTION defaults to PLANNING. Rationale unchanged: queuing is deciding, whereas an
	un-typed subsystem charge (hiring, ledger, media) is somebody physically doing a thing.
	The alternative -- one default everywhere -- would silently re-type either every
	subsystem charge or every strategic card, i.e. a balance change disguised as a cleanup,
	on the eve of the 2026-08-31 review. Both defaults are now pinned by tests so the split
	cannot drift unnoticed; the real fix (every cost dict declares its type explicitly) is a
	data pass, not a code change, and is tracked for post-review."""
	var declared: String = String(costs.get("hour_type", MonthPlan.HOUR_OPERATING))
	if MonthPlan.KIND_FAMILY.has(declared):
		return declared
	if declared == MonthPlan.HOUR_PLANNING:
		return MonthPlan.HOUR_PLANNING
	return MonthPlan.HOUR_OPERATING

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
					"attention": get_available_attention()
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

	if costs.has("attention") and month_plan != null:
		if not month_plan.spend_attention(int(costs["attention"]), _cost_hour_type(costs)):
			ErrorHandler.warning(
				ErrorHandler.Category.RESOURCES,
				"Attention spend rejected by the month plan",
				{"cost": costs["attention"], "available": month_plan.available()}
			)

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
		# ADR-0015 REMAINDER (Legacy #15 / memo S7.1): this generic doom sink is the un-migrated
		# tail of the clobber-bug class -- event/scenario CONTENT (data/events/*.json) still carries
		# literal "doom" deltas that flow here. In the real turn loop this write is CLOBBERED by
		# `state.doom = doom_system.current_doom` at resolve, so it is an inert no-op (Finding A);
		# it survives only for the direct-state unit tests. The AUTHORITY is DoomSystem's streams.
		# The follow-up content lane re-authors each event to write an INTERMEDIARY (frontier /
		# panic / alarm / ...) instead of doom, at which point this branch is deleted.
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
	"""Calendar months represented by one turn -- delegates to Clock, the single
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


func note_cause(kind: String, source: String, effects: Dictionary = {}) -> void:
	"""EE-8: append a turn-stamped contributing-cause event to the attribution trail.
	`effects` holds the APPLIED damage by resource (e.g. {"doom": 3.5, "reputation": -2.0})
	so DeathAttribution can run counterfactual necessity tests at death. Recording only --
	never read during play."""
	cause_log.append({"turn": turn, "kind": kind, "source": source, "effects": effects.duplicate()})


func check_win_lose():
	"""Check victory/defeat conditions"""
	# Sync doom from doom system
	if doom_system:
		doom = doom_system.current_doom

	# EE-8: rep-collapse watermark -- a contributing cause on the ADR-0012 cascade
	# (default -> rep collapse -> funding starvation -> death), not the death itself.
	# One-shot: the FIRST crossing marks the chain.
	if reputation <= REP_COLLAPSE_THRESHOLD and not rep_collapse_noted:
		rep_collapse_noted = true
		note_cause("rep_collapse", "reputation", {"reputation_level": reputation})

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

func add_researcher(researcher: Researcher, full_reveal: bool = true):
	"""Add a researcher to the team.
	Phase A hiring model: a DIRECTLY-hired person is fully known on their card (skill,
	appetites, loyalty-risk all revealed) and marked EMPLOYED. The QUIRK deliberately
	stays hidden until an exposure event -- employing someone does not surface it (A2).
	Phase B: a PIPELINE hire passes full_reveal=false -- a blind hire (skipped interviews)
	keeps whatever stayed hidden (the scouting gamble). Ensure a stable candidate_id so the
	pipeline can reference the employee (onboarding, recruiter reads)."""
	if full_reveal:
		researcher.set_reveal_level(Researcher.MAX_REVEAL)
	researcher.hire_state = Researcher.HireState.EMPLOYED
	if researcher.candidate_id == "" and hiring != null:
		hiring.stamp_candidate(researcher)
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

		# A departing person stops accruing, but what they already contributed STAYS on the
		# workstream (contributions feed later authorship). Losing your lead is supposed to
		# hurt as a slowdown, not as a retroactive erasure.
		release_from_workstreams(researcher)

# ============================================================================
# WORKSTREAM SUBSTRATE -- BACKLOG, ASSIGNMENT, READOUT (ADR-0011 s3/s4, #613)
# Assignment is PLAYER INPUT, so it replays for free (ADR-0006); every function below is
# deterministic and rng-free. Single source of truth for "who is on what" is
# Workstream.assigned_ids -- the Researcher does NOT carry a back-pointer, so the two
# cannot drift.
# ============================================================================

func researcher_id(researcher: Researcher) -> String:
	"""The stable id used in workstream assignment lists, MINTING one if this person has
	none (direct/legacy hires are created without a pipeline id). Pure counter, no rng;
	the 'staff_' prefix cannot collide with the pipeline's 'cand_'/'job_' serials."""
	if researcher == null:
		return ""
	if researcher.candidate_id == "":
		researcher_id_serial += 1
		researcher.candidate_id = "staff_%d" % researcher_id_serial
	return researcher.candidate_id


func available_backlog() -> Array[Dictionary]:
	"""Backlog entries not yet started this run (id-sorted, like WorkstreamBacklog)."""
	var out: Array[Dictionary] = []
	for e in WorkstreamBacklog.entries():
		if not workstream_backlog_taken.has(String(e.get("id", ""))):
			out.append(e)
	return out


func start_workstream(backlog_id: String):
	"""Commit the lab to a backlog item. Returns the new Workstream, or null if the id is
	unknown or already running. Costs nothing here: pricing the START against founder
	Attention is the plan-screen lane's call, not the substrate's."""
	if not WorkstreamBacklog.has(backlog_id):
		return null
	if workstream_backlog_taken.has(backlog_id):
		return null
	var entry := WorkstreamBacklog.get_entry(backlog_id)
	workstream_serial += 1
	var ws := Workstream.make("ws_%d" % workstream_serial, entry, turn)
	workstreams.append(ws)
	workstream_backlog_taken.append(backlog_id)
	return ws


func get_workstream(workstream_id: String):
	for ws in workstreams:
		if ws.id == workstream_id:
			return ws
	return null


func active_workstreams() -> Array:
	var out: Array = []
	for ws in workstreams:
		if ws.status == Workstream.Status.ACTIVE:
			out.append(ws)
	return out


func workstream_for_researcher(researcher: Researcher):
	"""The ACTIVE workstream this person is committed to, or null if they self-direct.
	A researcher is on at most one workstream at a time (assign_to_workstream enforces it):
	splitting one person across bets is exactly the fungible-scalar move ADR-0011 kills."""
	if researcher == null or researcher.candidate_id == "":
		return null
	for ws in workstreams:
		if ws.status == Workstream.Status.ACTIVE and ws.is_assigned(researcher.candidate_id):
			return ws
	return null


func assign_to_workstream(researcher: Researcher, workstream_id: String) -> bool:
	"""Commit a researcher to a workstream at plan speed. Pulls them off any other one
	first. Returns false if the workstream is unknown/finished or they were already there."""
	var ws = get_workstream(workstream_id)
	if ws == null or ws.status != Workstream.Status.ACTIVE:
		return false
	var rid := researcher_id(researcher)
	if rid == "":
		return false
	if ws.is_assigned(rid):
		return false
	release_from_workstreams(researcher)
	return ws.assign(rid)


func release_from_workstreams(researcher: Researcher) -> bool:
	"""Take a person off whatever they are on (back to self-directing). Their accrued
	contribution stays recorded on the workstream."""
	if researcher == null or researcher.candidate_id == "":
		return false
	var released := false
	for ws in workstreams:
		if ws.unassign(researcher.candidate_id):
			released = true
	return released


func record_self_directed(topic_key: String, actual: float, reported: float) -> void:
	"""Tally self-directed work by topic. TWO figures by ruling (2026-07-27): `actual` is
	the deterministic truth, `reported` is what the unsupervised researcher claims.
	SEAM: audits ground-truth reported vs actual (a later lane) -- nothing reads
	`reported` yet. Review-by 2026-08-31."""
	var bucket: Dictionary = self_directed_progress.get(topic_key, {"actual": 0.0, "reported": 0.0})
	# Snapped at the accumulator so live == saved (DoomSystem.SAVE_QUANTUM; see the note in
	# Workstream.accrue -- an unsnapped live tally forks a loaded run from an unsaved one).
	bucket["actual"] = DoomSystem._snap(float(bucket.get("actual", 0.0)) + actual)
	bucket["reported"] = DoomSystem._snap(float(bucket.get("reported", 0.0)) + reported)
	self_directed_progress[topic_key] = bucket


func audit_self_directed(topic_key: String = "", charge: bool = true) -> Dictionary:
	"""Spend a founder AUDIT hour to ground-truth one topic's self-directed progress.

	This is the consumer the T1 substrate left a SEAM for at every touch point
	(researcher.gd:129, record_self_directed above): unassigned staff self-direct and report
	OPTIMISTICALLY, and until now nothing read `reported`. An audit is skip-level
	ground-truthing -- the founder goes and looks -- so it bills the `audits` kind, which
	sits in the OPERATING family and is therefore impossible while away (#980 falls out).

	`topic_key` empty audits the topic with the LARGEST claimed-vs-true gap, tie-broken by
	sorted key. Deterministic, no RNG source touched -- the optimism factor is already a
	per-person hash (researcher.gd:632) and this only reads it.

	EFFECT (the conservative S-cut answer to the ADR's open 'what do audits audit'): the
	audited topic's ORG-LEVEL books are corrected -- `reported` collapses onto `actual`, so
	the gap closes and cannot be double-counted by a later reader. Deliberately NOT taken:
	reputation/trust penalties or departure risk against the individual (needs a target
	system that does not exist pre-T4), and per-person `self_directed_reported` is left
	alone on purpose -- an audit corrects what the ORG believes, not what the person
	claimed. Returns {ok, topic, actual, reported, gap, message}."""
	if month_plan == null:
		return {"ok": false, "topic": "", "gap": 0.0, "message": "No month plan -- nothing to audit."}
	if self_directed_progress.is_empty():
		return {"ok": false, "topic": "", "gap": 0.0, "message": "Nobody is self-directing -- there is nothing to ground-truth."}
	var target: String = topic_key
	if target == "":
		var topics: Array = self_directed_progress.keys()
		topics.sort()  # order-stable pick regardless of Dictionary iteration order
		var best_gap: float = -1.0
		for t in topics:
			var b: Dictionary = self_directed_progress[t]
			var g: float = float(b.get("reported", 0.0)) - float(b.get("actual", 0.0))
			if g > best_gap:
				best_gap = g
				target = String(t)
	if not self_directed_progress.has(target):
		return {"ok": false, "topic": target, "gap": 0.0, "message": "No self-directed work recorded on that topic."}
	# `charge` false when the caller already paid at QUEUE time (the action path: GameManager
	# debits the month plan when the card is queued, execute_action only applies the effect).
	if charge and not month_plan.spend_attention(1, MonthPlan.KIND_AUDITS):
		return {"ok": false, "topic": target, "gap": 0.0, "message": "No founder hours left to audit with."}
	var bucket: Dictionary = self_directed_progress[target]
	var actual: float = float(bucket.get("actual", 0.0))
	var reported: float = float(bucket.get("reported", 0.0))
	var gap: float = DoomSystem._snap(reported - actual)
	bucket["reported"] = DoomSystem._snap(actual)
	self_directed_progress[target] = bucket
	return {
		"ok": true,
		"topic": target,
		"actual": actual,
		"reported": reported,
		"gap": gap,
		"message": "Audited %s: claimed %.1f, actually %.1f (overstated by %.1f). Books corrected." % [
			target, reported, actual, gap,
		],
	}


func workstream_readout() -> Array[String]:
	"""Minimal ASCII debug readout for this lane (the plan-screen assignment verb is a
	separate UI carve). Lists running workstreams, then the self-directed drift with the
	claimed-vs-true gap the audit hour will eventually reconcile."""
	var lines: Array[String] = []
	if workstreams.is_empty():
		lines.append("[workstreams] none started -- all staff self-directing")
	for ws in workstreams:
		lines.append("[workstreams] " + ws.readout_line())
	var topics: Array = self_directed_progress.keys()
	topics.sort()  # order-stable readout regardless of Dictionary iteration order
	for t in topics:
		var b: Dictionary = self_directed_progress[t]
		lines.append("[self-directed] %s: %.1f actual / %.1f reported (gap %.1f)" % [
			String(t), float(b.get("actual", 0.0)), float(b.get("reported", 0.0)),
			float(b.get("reported", 0.0)) - float(b.get("actual", 0.0)),
		])
	return lines

func add_candidate(candidate: Researcher):
	"""Add a candidate to the hiring pool"""
	# Phase B: stamp a stable id (+ deterministic visa flag) so the pipeline can reference
	# this candidate across save/load. Covers every creation path (initial pool, turn trickle,
	# sourcing channels).
	if hiring != null:
		hiring.stamp_candidate(candidate)
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

# Threshold at/above which an appetite counts as a "strong/notable" hidden rider. The
# guaranteed-rider assignment sets its chosen appetite at or above this, and tests key off it.
const STARTER_STRONG_APPETITE: float = 0.8

func _populate_initial_candidates():
	"""Seed the turn-0 founding team: EXACTLY 4 starter candidates, each GUARANTEED a hidden
	rider (Pip ruling). Framing (Pip): these are the "starter pokemon" -- they accrue the most
	experience and become the deepest in trust/seniority late-game, so a guaranteed latent rider
	creates long-term narrative drama. The rider is either a rare quirk OR a strong appetite; it
	starts HIDDEN (quirk_known stays false; a strong appetite only surfaces at the appetite
	reveal layer) and reveal_level stays REVEAL_UNINTERVIEWED. Deterministic from the seeded rng
	(replay-safe, ADR-0006). Normal sourced candidates keep their existing chance-based riders --
	only these four founders are guaranteed one."""
	var specs := ["safety", "capabilities", "interpretability", "alignment"]
	for i in range(4):
		var cand := Researcher.new()
		cand.generate_random(rng)
		# First starter is always a safety anchor; the others rotate the lanes.
		cand.specialization = "safety" if i == 0 else specs[rng.randi() % specs.size()]
		# Lower skill for early-game starting candidates.
		cand.skill_level = rng.randi_range(1, 3)
		cand.base_productivity = 0.5 + (cand.skill_level * 0.1)
		_assign_guaranteed_rider(cand)
		add_candidate(cand)

func _assign_guaranteed_rider(candidate: Researcher) -> void:
	"""Give a founding-team starter a GUARANTEED, still-HIDDEN rider, drawn from the seeded rng
	(deterministic). Coin-flip between the two rider kinds so the four founders vary:
	  - quirk rider: a rare quirk (hidden until an exposure event; quirk_known stays false)
	  - appetite rider: one appetite pushed to STARTER_STRONG_APPETITE+ (hidden until the
	    appetite reveal layer, revealed only by interviewing)
	Either way the card shows nothing extra at reveal 0 -- the depth is latent."""
	if rng.randf() < 0.5:
		candidate.quirk = QuirkCatalogue.pick_id(rng)  # from the data-driven catalogue
		candidate.quirk_known = false
	else:
		var key: String = Researcher.APPETITE_KEYS[rng.randi() % Researcher.APPETITE_KEYS.size()]
		candidate.appetites[key] = clampf(STARTER_STRONG_APPETITE + rng.randf() * 0.2, STARTER_STRONG_APPETITE, 1.0)

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

# --- Founder Attention capacity (2026-08-12 ruling: ONE derivation point) ------------
func current_month_index() -> int:
	"""Absolute month ordinal (Clock.month_index form) for the turn the run is on. The
	argument capacity_for_month() wants; also the month-boundary counter MonthController
	already uses, so both sides agree on what 'this month' means."""
	return Clock.month_index(turn, start_year, start_month, start_day)

func capacity_for_month(month_index: int) -> Dictionary:
	"""THE derivation point for this run's monthly Attention budget: {value, reason}.

	Every site that opens a plan month goes through here rather than reading
	`attention_per_month` directly (GameState.reset, MonthController._open_plan_month,
	GameManager._set_attention_grant). The seed is passed from the first line even though
	`value` ignores it -- see capacity.gd for why that is the whole point.

	Zero behaviour change today: `value` is exactly `attention_per_month`, for every seed
	and every month. Only the `reason` varies, and it varies by seed+month, never by an
	rng draw off the run stream."""
	return Capacity.derive(game_seed_str, month_index, {Capacity.MOD_GRANT: attention_per_month})

# --- Founder Attention accessors (T2: the AP reserve system is gone; these read the plan) ---
func get_available_attention() -> int:
	"""Founder Attention free to fund new commitments this PLAN MONTH (ADR-0011 / T2).
	Nets out what is already spent and what is explicitly reserved for response windows.
	Zero when there is no month plan -- there is no fallback pool any more."""
	if month_plan != null:
		return month_plan.available()
	return 0

func get_reserve_attention() -> int:
	"""Attention still held in the crisp reserve for response windows (ADR-0009 S3)."""
	if month_plan != null:
		return month_plan.reserve_remaining()
	return 0

func get_available_hours(hour_type: String) -> int:
	"""Founder hours of one TYPE still unspent this month (2-way floor: planning /
	operating). The 4-way refinement subdivides these; it does not replace them."""
	if month_plan != null:
		return month_plan.hours_available(hour_type)
	return 0

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

# Calendar System Methods (Issue #472) -- thin delegates to Clock, the single
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
	"""Badge/HUD string. ADR-0009 S1-2/S6: the plan cadence is the MONTH and the badge
	is the calendar date; the day is a resolution tick, not a decision unit. The old
	'Week 12 | ... | Day 3/5' framing hung the player's attention on the day tick and is
	retired -- routine decisions live at the month boundary now. Primary is the plan month;
	the calendar day rides along as playback progress, not a decision counter."""
	var date = get_current_date()
	# e.g. "March 2034  -  Mar 20"  -- month is the plan unit, date is the badge.
	return "%s %d  -  %s %d" % [
		Clock.MONTH_NAMES[date.month - 1],
		date.year,
		Clock.MONTH_ABBR[date.month - 1],
		date.day
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
# dominant, doom-integral as tiebreak. FLOWS ONLY -- no stock the player holds at
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
	return "Turn %d - %d" % [turns, integral]


# ============================================================================
# SERIALIZATION -- SAVE/LOAD CONVENTION (L7, #618)
#
# to_dict() is BOTH the UI payload and the save-file state body; from_dict()
# must rebuild an equivalent GameState from it. The invariant the round-trip
# test enforces: from_dict(to_dict()) -- including a JSON stringify/parse hop --
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
#      into typed arrays -- JSON hands back untyped floats and untyped Arrays.
#   5. Derived/display values (turn_display, tech_debt_color, rival summaries,
#      available_ap, ...) are recomputed, never restored.
#   6. Extend tests/unit/test_save_load_roundtrip.gd so the new state is
#      exercised before the save point.
#
# Replay (ADR-0006) is unaffected: it rebuilds from turn 0. This is SNAPSHOT
# fidelity for mid-game save/load (and later DQ-11 fork/divergence).
# ============================================================================

static func _snap_array(arr) -> Array:
	## Serialization-boundary float snap for arrays (see DoomSystem.SAVE_QUANTUM).
	var out: Array = []
	for v in arr:
		out.append(DoomSystem._snap(float(v)))
	return out


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
	# multipliers/modifiers round-trip -- previously hand-rolled and lossy), plus
	# derived display strings the UI reads.
	var doom_data = {}
	if doom_system:
		doom_data = doom_system.to_dict()
		doom_data["doom"] = DoomSystem._snap(doom)
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

	# Serialize workstreams (ADR-0011 substrate). Self-directed tallies are float pairs, so
	# they get the same serialization-boundary snap as every other sim float.
	var workstream_dicts = []
	for ws in workstreams:
		workstream_dicts.append(ws.to_dict())
	var self_directed_out := {}
	for t in self_directed_progress.keys():
		var b: Dictionary = self_directed_progress[t]
		self_directed_out[String(t)] = {
			"actual": DoomSystem._snap(float(b.get("actual", 0.0))),
			"reported": DoomSystem._snap(float(b.get("reported", 0.0))),
		}

	return {
		"money": money,
		"compute": compute,
		"research": research,
		"research_quality_mode": research_quality_mode,  # Issue #500
		"papers": papers,
		"reputation": reputation,
		# ADR-0010 B7/B9 typed reputation. NEW KEYS ONLY -- the authoritative
		# "reputation" scalar above is untouched, so this merges clean with the
		# other save-schema lanes landing this week. Snapped to the repo-wide
		# serialization grid (same reason as appetites in researcher.gd).
		"rep_org": DoomSystem._snap_dict(rep_org),
		"rep_operator": DoomSystem._snap_dict(rep_operator),
		"governance": governance,
		"ledger": ledger.to_dict() if ledger else {},
		"month_plan": month_plan.to_dict() if month_plan else {},  # L1/ADR-0009 Attention + reserve + WIP
		"hiring": hiring.to_dict() if hiring else {},  # Phase B pipeline: campaigns + in-flight jobs
		"cause_log": cause_log.duplicate(true),  # EE-8 attribution trail
		# Doom-adjacent floats are SNAPPED at the serialization boundary (both directions,
		# same quantum as DoomSystem.SAVE_QUANTUM): the stream model produces full-precision
		# doubles, and Godot's JSON parse is not correctly-rounded (calibration S7.2) -- a
		# 1-ulp corrupted parse re-snaps to the identical double, keeping save/load
		# deep-equality byte-stable. Live dynamics never see the quantum.
		"doom": DoomSystem._snap(doom),
		"doom_history": _snap_array(doom_history),  # #512 trend graph
		# ADR-0015 / DQ-21 world-state intermediaries (doom is computed from these)
		"ambient_risk": DoomSystem._snap(ambient_risk),
		"frontier_capability": DoomSystem._snap_dict(frontier_capability),
		"general_capability": DoomSystem._snap(general_capability),
		"global_compute": DoomSystem._snap(global_compute),
		"dedicated_ai_compute": DoomSystem._snap(dedicated_ai_compute),
		"safety_absorption": DoomSystem._snap(safety_absorption),
		"global_alarm": DoomSystem._snap(global_alarm),
		"global_panic": DoomSystem._snap(global_panic),
		"political_pressure": DoomSystem._snap(political_pressure),
		"doom_dampers": doom_dampers.duplicate(true),
		"doom_pulses": doom_pulses.duplicate(true),
		"sacred_chain_log": sacred_chain_log.duplicate(true),
		"doom_system": doom_data,
		"risk_system": risk_data,
		# T2: founder currency in the state dict is ATTENTION. "attention" is what the HUD
		# and every affordability readout wants (free-to-spend now); the pool breakdown
		# rides month_plan (already serialized below).
		"attention": get_available_attention(),
		"attention_total": month_plan.attention_total if month_plan != null else 0,
		"attention_reserved": get_reserve_attention(),
		"planning_hours_left": get_available_hours(MonthPlan.HOUR_PLANNING),
		"operating_hours_left": get_available_hours(MonthPlan.HOUR_OPERATING),
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
		# Office economy (#791). hire_cap is the SIM number the hiring paths enforce;
		# floorplan stays render-side and is deliberately NOT surfaced here (ADR-0018).
		"office_id": office_id,
		"office_name": office_name,
		"office_tier": office_tier,
		"office_hire_cap": office_hire_cap,
		"office_rent_per_month": office_rent_per_month,
		"office_locked": office_locked,
		"office_upgrades": office_upgrades.duplicate(),
		"desks_free": maxi(0, office_hire_cap - get_total_staff()),
		"hype": hype,
		"management_capacity": get_management_capacity(),
		"unmanaged_count": get_unmanaged_count(),
		"turn": turn,
		"doom_integral": DoomSystem._snap(doom_integral),
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
		"attention_per_month": attention_per_month,  # difficulty modifier -- next month's grant
		"conference_year": conference_year,
		"start_year": start_year,
		"start_month": start_month,
		"start_day": start_day,
		"pending_hire_queue": pending_hire_dicts,
		"rival_labs_full": rival_full_dicts,  # "rival_labs" stays display summaries for the UI
		# --- Workstream substrate (ADR-0011 s3/s4, #613). ADDITIVE top-level keys, one per
		# concern (convention rule 2); a pre-substrate save loads with an empty board. ---
		"workstreams": workstream_dicts,
		"workstream_backlog_taken": workstream_backlog_taken.duplicate(),
		"workstream_serial": workstream_serial,
		"researcher_id_serial": researcher_id_serial,
		"self_directed_progress": self_directed_out
	}


func from_dict(data: Dictionary) -> void:
	"""Restore game state from serialized data (for save/load).
	L7 (#618): full-fidelity -- see SERIALIZATION CONVENTION block above to_dict().
	Explicit int()/float()/String() casts throughout: JSON parses every number as float."""
	# Core resources
	money = float(data.get("money", 100000.0))
	compute = float(data.get("compute", 0.0))
	research = float(data.get("research", 0.0))
	research_quality_mode = String(data.get("research_quality_mode", DEFAULT_RESEARCH_QUALITY))  # Issue #500
	papers = float(data.get("papers", 0.0))
	reputation = float(data.get("reputation", 10.0))
	# ADR-0010 B7: typed dims default to zero, so pre-typing saves load as
	# "scalar only" -- exactly the state the game is in before any reader wires up.
	rep_org = _load_rep_dims(data.get("rep_org", {}))
	rep_operator = _load_rep_dims(data.get("rep_operator", {}))
	governance = float(data.get("governance", 50.0))  # was forgotten pre-L7
	hype = float(data.get("hype", 0.0))
	# Office economy (#791). Defaults are the tier-0 start, so a pre-office save loads
	# into the bedroom rather than into an undefined office.
	office_id = String(data.get("office_id", "bedroom"))
	office_name = String(data.get("office_name", "Bedroom / basement"))
	office_tier = int(data.get("office_tier", 0))
	office_hire_cap = int(data.get("office_hire_cap", int(Office.start_office().get("hire_cap", 2))))
	office_rent_per_month = float(data.get("office_rent_per_month", 0.0))
	office_locked = bool(data.get("office_locked", false))
	office_upgrades = (data.get("office_upgrades", []) as Array).duplicate()
	# Doom-adjacent floats re-snap on load (idempotent under the 1-ulp JSON parse
	# corruption -- see the to_dict comment + DoomSystem.SAVE_QUANTUM).
	doom = DoomSystem._snap(float(data.get("doom", 50.0)))
	doom_history.clear()
	for d in data.get("doom_history", []):
		doom_history.append(DoomSystem._snap(float(d)))
	# ADR-0015 / DQ-21 world-state intermediaries
	ambient_risk = DoomSystem._snap(float(data.get("ambient_risk", Balance.num("doom.base_per_turn", 0.06))))
	frontier_capability = DoomSystem._snap_dict(data.get("frontier_capability", {"player": 0.0}) as Dictionary)
	if not frontier_capability.has("player"):
		frontier_capability["player"] = 0.0
	general_capability = DoomSystem._snap(float(data.get("general_capability", 0.0)))
	global_compute = DoomSystem._snap(float(data.get("global_compute", 0.0)))
	dedicated_ai_compute = DoomSystem._snap(float(data.get("dedicated_ai_compute", 0.0)))
	safety_absorption = DoomSystem._snap(float(data.get("safety_absorption", 0.0)))
	global_alarm = DoomSystem._snap(float(data.get("global_alarm", 0.0)))
	global_panic = DoomSystem._snap(float(data.get("global_panic", 0.0)))
	political_pressure = DoomSystem._snap(float(data.get("political_pressure", 0.0)))
	doom_dampers = (data.get("doom_dampers", []) as Array).duplicate(true)
	doom_pulses = (data.get("doom_pulses", []) as Array).duplicate(true)
	sacred_chain_log = (data.get("sacred_chain_log", []) as Array).duplicate(true)
	# T2: pre-migration saves carry action_points / max_action_points / the *_ap trio. They
	# are read for NOTHING -- the fields no longer exist. The founder budget restores from
	# the serialized month_plan; only the grant size is carried here.
	attention_per_month = int(data.get("attention_per_month", Balance.inum("attention.per_month", 20)))
	stationery = float(data.get("stationery", 100.0))
	technical_debt = float(data.get("technical_debt", 0.0))

	# Staff counts (legacy)
	safety_researchers = int(data.get("safety_researchers", 0))
	capability_researchers = int(data.get("capability_researchers", 0))
	compute_engineers = int(data.get("compute_engineers", 0))
	managers = int(data.get("managers", 0))

	# Game state
	turn = int(data.get("turn", 0))
	doom_integral = DoomSystem._snap(float(data.get("doom_integral", 0.0)))
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

	# WS-C scheduled causes (seed identity -- survives reset(), must survive load too)
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

	# Restore the Liability Ledger (WS-1 -- entries were forgotten pre-L7)
	if ledger == null:
		ledger = Ledger.new()
	ledger.from_dict(data.get("ledger", {}))

	# Restore the month plan layer (L1/ADR-0009: Attention, reserve, in-flight strategic WIP)
	if month_plan == null:
		month_plan = MonthPlan.new()
	month_plan.from_dict(data.get("month_plan", {}))

	# Restore the hiring pipeline (Phase B: campaigns + in-flight duration jobs + id serial).
	# Candidate/employee onboarding + reveal state ride on the Researcher records themselves,
	# restored below; this restores the campaign/job bookkeeping and the id counter.
	if hiring == null:
		hiring = HiringPipeline.new()
	hiring.from_dict(data.get("hiring", {}))

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

	# Restore the workstream substrate (ADR-0011 s3/s4, #613). Every key is optional: a
	# pre-substrate save restores to an empty board with the full backlog available.
	workstreams.clear()
	for ws_data in data.get("workstreams", []):
		if ws_data is Dictionary:
			workstreams.append(Workstream.from_dict(ws_data))
	workstream_backlog_taken.clear()
	for bid in data.get("workstream_backlog_taken", []):
		workstream_backlog_taken.append(String(bid))
	workstream_serial = int(data.get("workstream_serial", 0))
	researcher_id_serial = int(data.get("researcher_id_serial", 0))
	self_directed_progress.clear()
	var sd_data = data.get("self_directed_progress", {})
	if sd_data is Dictionary:
		for t in sd_data.keys():
			var b = sd_data[t]
			if b is Dictionary:
				self_directed_progress[String(t)] = {
					"actual": DoomSystem._snap(float(b.get("actual", 0.0))),
					"reported": DoomSystem._snap(float(b.get("reported", 0.0))),
				}

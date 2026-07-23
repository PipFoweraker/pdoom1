extends Resource
class_name Researcher
## Individual researcher with specialization, hidden quirk, and burnout
## Based on Python src/core/researchers.py

# ============================================================================
# CORE PROPERTIES
# ============================================================================

@export var researcher_name: String = ""
@export var specialization: String = "safety"  # safety, capabilities, interpretability, alignment
@export var skill_level: int = 5  # 1-10
@export var salary_expectation: float = 60000.0
@export var current_salary: float = 60000.0

# Dynamic state
var base_productivity: float = 1.0  # 0.1 to 2.0
var loyalty: int = 50  # 0-100, affects poaching resistance
var burnout: float = 0.0  # 0-100, reduces productivity
var turns_employed: int = 0

# Travel fatigue system (Issue #469)
var jet_lag_turns: int = 0  # Turns remaining with jet lag
var jet_lag_severity: float = 0.0  # 0.0-1.0, productivity penalty during jet lag

# NOTE: the legacy positive/negative "trait" system (workaholic/leak_prone/...) has been
# RETIRED. Its shallow, hardcoded placeholders are replaced by the data-driven QUIRK
# catalogue (see `quirk` below + res://data/researchers/quirks.json). The good ones were
# reframed as quirks (runs_hot <- workaholic, loose_lips <- leak_prone, lab_parent <-
# team_player, sponge <- fast_learner, true_believer <- safety_conscious). See
# docs/game-design/RESEARCHER_QUIRKS.md.

# ============================================================================
# HIRING PIPELINE — IDENTITY + ONBOARDING (Phase B)
# Spec: docs/game-design/BUILD_BRIEF_HIRING_PIPELINE.md "Phase B". These ride ON the
# Phase-A hidden layer below. `candidate_id` is a stable handle the pipeline references
# across save/load (object identity doesn't survive a JSON hop). The onboarding flags gate
# productivity: a pipeline hire starts UN-onboarded and only becomes fully productive once
# the checklist clears (skimping mentoring leaves a lasting debuff + attrition risk).
# ============================================================================
var candidate_id: String = ""       # stable id assigned when the candidate is sourced
var needs_visa: bool = false        # foreign/remote hire -> a situational onboarding item
var onboarded: bool = true          # DEFAULT true: legacy/direct hires are productive at once
var laptop_done: bool = false       # hard checklist item
var visa_done: bool = false         # hard checklist item (only when needs_visa)
var systems_done: bool = false      # hard checklist item (#789): onboarded to systems; needs laptop first
var meet_people_done: bool = false  # hard checklist item (#789): introduced around the lab
var mentoring_done: bool = false    # soft item: skipping it debuffs + arms attrition
var mentoring_skipped: bool = false # player explicitly skimped mentoring (slack-as-insurance)

# ============================================================================
# HIRING PIPELINE — HIDDEN ABILITY LAYER (Phase A)
# Spec: docs/game-design/BUILD_BRIEF_HIRING_PIPELINE.md "Phase A" + WORKSHOP_2_BACKLOG
# "Hiring pipeline RULED" (A1/A2/A3); appetites/quirks per ADR-0011 section 8; pay-to-see
# per ADR-0004 ("Simulate everything; gate only the view").
#
# GUARD (ADR-0004): the MODEL stores the TRUE values below. Only the CARD VIEW hides
# them by reveal_level (get_card_data). The sim never lies -- interviewing REVEALS, it
# never fabricates. Physical identity (appearance_id, name) is DECOUPLED from ability.
# ============================================================================

# Hire lifecycle (WORKSHOP_2 "Hiring pipeline RULED"): pool -> offered -> employed ->
# departed. DEPARTED is terminal. Transitions are guarded (see can_transition_to).
enum HireState { CANDIDATE_IN_POOL, OFFERED, EMPLOYED, DEPARTED }

# The five appetites (ADR-0011 section 8) -- the negotiation/retention currency. Each is
# a 0..1 hunger strength; feeding it (or minting a ledger promise) retains, starving bites.
const APPETITE_KEYS := ["compute", "prestige", "mentees", "money", "mission_purity"]

# Reveal ladder (A1/A2). 0 = uninterviewed: only lane + rough seniority show. Each
# interview step (Phase B) peels back one layer. The card hides everything above the
# current level behind HIDDEN_PLACEHOLDER; the underlying values are always real.
const REVEAL_UNINTERVIEWED := 0   # name, lane (specialization), rough seniority band
const REVEAL_SKILL := 1           # + true skill, compensation expectation
const REVEAL_APPETITES := 2       # + the five appetites
const REVEAL_DEEP := 3            # + loyalty-risk
const MAX_REVEAL := 3

# Field -> minimum reveal_level at which the card shows the TRUE value.
const REVEAL_REQUIREMENTS := {
	"name": REVEAL_UNINTERVIEWED,
	"specialization": REVEAL_UNINTERVIEWED,
	"seniority_band": REVEAL_UNINTERVIEWED,
	"skill_level": REVEAL_SKILL,
	"salary_expectation": REVEAL_SKILL,
	"appetites": REVEAL_APPETITES,
	"loyalty_risk": REVEAL_DEEP,
}

const HIDDEN_PLACEHOLDER := "??? (interview to reveal)"

# Identity assets are combinatorial (WORKSHOP_2 "Character sprite system"): a base-body
# id drawn from a pool, deliberately UNCORRELATED with ability.
const IDENTITY_POOL_SIZE := 24

# Rare quirk riders (ADR-0011 section 8): thematically-grounded lab archetypes carrying a
# small, TRUE, hidden mechanical effect. They stay hidden until an EXPOSURE surfaces them
# (ADR-0003 machinery) -- NOT revealed by interviewing (A2). The catalogue is data-driven
# (res://data/researchers/quirks.json via QuirkCatalogue); see docs/game-design/RESEARCHER_QUIRKS.md.
const QUIRK_CHANCE := 0.15

# --- Identity (ability-UNCORRELATED) ---
@export var appearance_id: String = ""     # sprite/appearance handle; diverse, not a stat tell

# --- Hidden ability layer (TRUE values; the card gates their visibility) ---
var hire_state: int = HireState.CANDIDATE_IN_POOL
var reveal_level: int = REVEAL_UNINTERVIEWED
var appetites: Dictionary = {}             # appetite_key -> 0..1 strength (ADR-0011 section 8)
var quirk: String = ""                     # rare quirk rider ("" = none)
var quirk_known: bool = false              # true once an exposure event surfaces the quirk
var loyalty_risk: float = 0.0              # 0..1 hidden flight predisposition (NOT live loyalty)

# ============================================================================
# SPECIALIZATIONS
# ============================================================================

const SPECIALIZATIONS = {
	"safety": {
		"name": "Safety Researcher",
		"description": "Focused on AI safety and alignment",
		"doom_reduction_bonus": 0.15,  # +15% safety research effectiveness
		"base_cost": 60000
	},
	"capabilities": {
		"name": "Capabilities Researcher",
		"description": "Advances AI capabilities (risky!)",
		"research_speed_modifier": 1.25,  # +25% research speed
		"doom_per_research": 0.05,  # +5% doom from their research
		"base_cost": 60000
	},
	"interpretability": {
		"name": "Interpretability Researcher",
		"description": "Makes AI systems more understandable",
		"unlocks_special_actions": true,  # Audit, transparency actions
		"base_cost": 70000
	},
	"alignment": {
		"name": "Alignment Researcher",
		"description": "Ensures AI goals align with human values",
		"negative_event_reduction": 0.10,  # -10% chance of bad events
		"base_cost": 65000
	}
}

# ============================================================================
# QUIRK EFFECTS (data-driven; replaces the retired trait system)
# ============================================================================
# A quirk's mechanical effect is read through quirk_effect() from the JSON catalogue. The
# effect is TRUE from creation (hidden-but-real); play reveals it. Effect channels are a
# small fixed set (see docs/game-design/RESEARCHER_QUIRKS.md): self_productivity_mult,
# burnout_per_turn_add, doom_mod_add, leak_chance, team_productivity_add, skill_growth_mult,
# loyalty_per_turn_add.

func quirk_effect(key: String, default_value):
	"""This researcher's value for a quirk effect channel, or default_value if they carry no
	quirk (or the quirk does not touch that channel). Effect is live even while hidden."""
	if quirk == "":
		return default_value
	return QuirkCatalogue.effect(quirk, key, default_value)

# ============================================================================
# INITIALIZATION
# ============================================================================

func _init(spec: String = "safety", name: String = ""):
	specialization = spec
	# WS-0 determinism: no global RNG in _init. Seeded creation calls generate_random(rng);
	# deserialization calls from_dict. Both overwrite these deterministic defaults.
	researcher_name = name if name != "" else "New Researcher"

	# Set base salary from specialization
	if SPECIALIZATIONS.has(spec):
		salary_expectation = SPECIALIZATIONS[spec]["base_cost"]
		current_salary = salary_expectation

	# Deterministic mid-range defaults; variation is applied only via generate_random(rng)
	skill_level = 5
	base_productivity = 0.5 + (skill_level * 0.1)  # 1.0
	loyalty = 55

	# Hidden ability layer defaults: neutral appetites, no quirk, uninterviewed. Real
	# values are drawn only via generate_random(rng) or restored via from_dict.
	appetites = _neutral_appetites()

func generate_random(rng: RandomNumberGenerator):
	"""Generate random attributes using provided RNG for determinism"""
	researcher_name = _generate_name_with_rng(rng)

	# Random skill level (3-7 for new hires)
	skill_level = rng.randi_range(3, 7)

	# Base productivity from skill
	base_productivity = 0.5 + (skill_level * 0.1)

	# Random loyalty (40-70)
	loyalty = rng.randi_range(40, 70)

	# Salary variation (+/- 10%)
	var variation = 1.0 + (rng.randf() * 0.2 - 0.1)
	salary_expectation = SPECIALIZATIONS.get(specialization, {}).get("base_cost", 60000) * variation
	current_salary = salary_expectation

	# --- Hidden ability layer (Phase A). ADDITIVE by construction: the hidden layer is
	# drawn from a CHILD rng seeded off the main stream's CURRENT state, which reading
	# does NOT advance. So the main rng.state after generate_random is exactly what it
	# was before this feature -- the rest of the game's deterministic stream (rival
	# estimates, events, ...) is byte-unchanged. Deterministic + replay-safe because the
	# child seed is a pure function of the (reproducible) main state at this point. ---
	var hidden_rng := RandomNumberGenerator.new()
	hidden_rng.seed = hash(rng.state)
	# Identity: deliberately uncorrelated with skill (WORKSHOP_2 "Character sprite
	# system": diversity is identity, never a stat tell).
	appearance_id = "body_%02d" % (hidden_rng.randi() % IDENTITY_POOL_SIZE)
	# The five appetites (ADR-0011 section 8): independent 0..1 hungers.
	appetites = {}
	for k in APPETITE_KEYS:
		appetites[k] = hidden_rng.randf()
	# Loyalty-risk: hidden flight predisposition (revealed only at deep reveal).
	loyalty_risk = hidden_rng.randf()
	# Rare quirk rider: most candidates carry none; when present it stays hidden until
	# an exposure event (A2) -- interviewing never surfaces it. Drawn from the data-driven
	# catalogue (same two hidden_rng draws as before -> byte-identical stream, ADR-0006).
	if hidden_rng.randf() < QUIRK_CHANCE:
		quirk = QuirkCatalogue.pick_id(hidden_rng)
	else:
		quirk = ""
	quirk_known = false
	# Freshly-sourced people start uninterviewed, in the candidate pool.
	reveal_level = REVEAL_UNINTERVIEWED
	hire_state = HireState.CANDIDATE_IN_POOL

func _generate_name_with_rng(rng: RandomNumberGenerator) -> String:
	"""Generate a random researcher name using provided RNG"""
	const FIRST_NAMES = [
		"Alex", "Blake", "Casey", "Drew", "Ellis", "Finley", "Gray", "Harper",
		"Iris", "Jordan", "Kelly", "Lane", "Morgan", "Noel", "Owen", "Parker",
		"Quinn", "Riley", "Sage", "Taylor"
	]
	const LAST_NAMES = [
		"Chen", "Kumar", "O'Brien", "Patel", "Rodriguez", "Smith", "Williams",
		"Zhang", "Anderson", "Martinez", "Thompson", "Garcia", "Lee", "Wilson",
		"Moore", "Taylor", "Brown", "Davis", "Miller", "Johnson"
	]

	return FIRST_NAMES[rng.randi() % FIRST_NAMES.size()] + " " + LAST_NAMES[rng.randi() % LAST_NAMES.size()]

# ============================================================================
# PRODUCTIVITY CALCULATION
# ============================================================================

func get_effective_productivity() -> float:
	"""
	Calculate actual productivity considering all factors.
	Returns 0.1 to ~2.5 (with perfect conditions and traits)
	"""
	var effective = base_productivity

	# Burnout penalty (max 50% reduction at 100 burnout)
	var burnout_penalty = min(burnout / 100.0 * 0.5, 0.5)
	effective *= (1.0 - burnout_penalty)

	# Jet lag penalty (Issue #469)
	if jet_lag_turns > 0:
		effective *= (1.0 - jet_lag_severity)

	# Quirk self-effect (retired-trait replacement): a single legible productivity multiplier
	# drawn from the catalogue (runs_hot 1.20, quiet_quitter 0.85, ...). TRUE even while the
	# quirk is still hidden -- the player sees the output, not yet the cause.
	effective *= float(quirk_effect("self_productivity_mult", 1.0))

	# Hiring onboarding (Phase B): a not-yet-onboarded pipeline hire is barely productive
	# until their checklist clears; a hire whose mentoring was skimped carries a lasting
	# (smaller) debuff. Both default off (onboarded=true, mentoring_skipped=false), so legacy
	# and directly-hired staff are unaffected.
	if not onboarded:
		effective *= Balance.num("hiring.onboarding.unproductive_multiplier", 0.4)
	elif mentoring_skipped:
		effective *= Balance.num("hiring.onboarding.skimped_multiplier", 0.85)

	# Minimum 10% productivity (even totally burned out)
	return max(effective, 0.1)

func get_doom_modifier() -> float:
	"""Get doom modification from this researcher's specialization and quirk"""
	var modifier = 0.0

	# Specialization effects
	match specialization:
		"safety":
			modifier -= SPECIALIZATIONS["safety"]["doom_reduction_bonus"]
		"capabilities":
			modifier += SPECIALIZATIONS["capabilities"]["doom_per_research"]

	# Quirk effect (retired-trait replacement): true_believer/doom_absolutist lower doom,
	# e_acc_sympathizer/secret_successionist raise it. Live even while the quirk is hidden.
	modifier += float(quirk_effect("doom_mod_add", 0.0))

	return modifier

# ============================================================================
# BURNOUT MANAGEMENT
# ============================================================================

func accumulate_burnout(amount: float):
	"""Add burnout (typically called each turn). Quirk burnout drift is applied by the caller
	(process_turn) via quirk_effect('burnout_per_turn_add') so a negative-drift quirk like
	cat_whisperer can also relieve burnout."""
	burnout += amount
	burnout = clamp(burnout, 0.0, 100.0)

func reduce_burnout(amount: float):
	"""Reduce burnout (from team building, retreats, etc.)"""
	burnout -= amount
	burnout = max(burnout, 0.0)

func is_burned_out() -> bool:
	"""Check if researcher is critically burned out"""
	return burnout >= 80.0

# ============================================================================
# JET LAG MANAGEMENT (Issue #469)
# ============================================================================

# Travel class constants
const TRAVEL_CLASS = {
	"economy": {
		"name": "Economy",
		"cost_multiplier": 1.0,
		"jet_lag_turns": 10,  # ~2 weeks recovery
		"jet_lag_severity": 0.40  # 40% productivity loss
	},
	"business": {
		"name": "Business",
		"cost_multiplier": 2.5,
		"jet_lag_turns": 5,  # ~1 week recovery
		"jet_lag_severity": 0.20  # 20% productivity loss
	},
	"first": {
		"name": "First Class",
		"cost_multiplier": 5.0,
		"jet_lag_turns": 2,  # Minimal impact
		"jet_lag_severity": 0.10  # 10% productivity loss
	}
}

func apply_jet_lag(location_tier: int, travel_class: String = "economy"):
	"""Apply jet lag based on travel distance and class (Issue #469)"""
	# Local travel = no jet lag
	if location_tier <= 1:
		return

	var class_data = TRAVEL_CLASS.get(travel_class, TRAVEL_CLASS["economy"])

	# Base jet lag from class
	var base_turns = class_data["jet_lag_turns"]
	var base_severity = class_data["jet_lag_severity"]

	# Scale by distance (domestic = 60%, international = 100%)
	var distance_multiplier = 0.6 if location_tier == 2 else 1.0

	jet_lag_turns = int(base_turns * distance_multiplier)
	jet_lag_severity = base_severity * distance_multiplier

func recover_jet_lag():
	"""Called each turn to recover from jet lag"""
	if jet_lag_turns > 0:
		jet_lag_turns -= 1
		if jet_lag_turns == 0:
			jet_lag_severity = 0.0

func has_jet_lag() -> bool:
	"""Check if researcher is jet lagged"""
	return jet_lag_turns > 0

func get_jet_lag_status() -> String:
	"""Get human-readable jet lag status"""
	if jet_lag_turns == 0:
		return ""
	return "Jet lagged (%d turns, -%.0f%% productivity)" % [jet_lag_turns, jet_lag_severity * 100]

# ============================================================================
# QUIRK MANAGEMENT (replaces the retired trait system)
# ============================================================================

func quirk_display_name() -> String:
	"""Human-readable quirk name ('none' if the person carries no quirk)."""
	return QuirkCatalogue.display_name(quirk)

func maybe_reveal_quirk_by_tenure() -> bool:
	"""Deterministic tenure-based reveal: once employed long enough, the quirk surfaces (flips
	quirk_known). No-op if no quirk, already known, or not yet at the catalogue threshold.
	Returns true iff this call newly exposed the quirk."""
	if quirk == "" or quirk_known:
		return false
	if turns_employed >= QuirkCatalogue.reveal_after_turns(quirk):
		quirk_known = true
		return true
	return false

# ============================================================================
# TURN PROCESSING
# ============================================================================

func process_turn(rng: RandomNumberGenerator = null):
	"""Called each turn - handle burnout, skill growth, jet lag recovery, etc."""
	turns_employed += 1

	# Base burnout accumulation (working is stressful!) plus any quirk burnout drift
	# (runs_hot/empire_builder push it up; cat_whisperer relieves it). Kept as ONE call so the
	# net per-turn burnout is legible.
	accumulate_burnout(0.5 + float(quirk_effect("burnout_per_turn_add", 0.0)))

	# Jet lag recovery (Issue #469)
	recover_jet_lag()

	# Skill growth (very slow - 1 point per ~20 turns). The sponge quirk multiplies the roll
	# chance (skill_growth_mult).
	# WS-0 determinism: use provided seeded RNG only; no global-RNG fallback (1.0 => no growth)
	var skill_roll: float = rng.randf() if rng != null else 1.0
	if skill_roll < 0.05 * float(quirk_effect("skill_growth_mult", 1.0)):  # base 5% chance per turn
		skill_level = min(skill_level + 1, 10)
		base_productivity = 0.5 + (skill_level * 0.1)

	# Loyalty changes based on satisfaction, plus quirk loyalty drift (true_believer holds,
	# quiet_quitter drifts out).
	var salary_ratio = current_salary / salary_expectation
	if salary_ratio >= 1.0:
		loyalty = min(loyalty + 1, 100)
	elif salary_ratio < 0.8:
		loyalty = max(loyalty - 2, 0)
	loyalty = clampi(loyalty + int(quirk_effect("loyalty_per_turn_add", 0)), 0, 100)

	# Tenure reveal (deterministic fallback): time on the team eventually surfaces the quirk
	# even absent a bespoke incident, so a hidden rider never stays invisible forever (ADR-0006).
	maybe_reveal_quirk_by_tenure()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

func get_summary() -> String:
	"""Get one-line summary of researcher"""
	return "%s (%s, Skill %d, Productivity %.1f%%)" % [
		researcher_name,
		SPECIALIZATIONS[specialization]["name"],
		skill_level,
		get_effective_productivity() * 100.0
	]

func get_specialization_name() -> String:
	"""Get human-readable specialization name"""
	if SPECIALIZATIONS.has(specialization):
		return SPECIALIZATIONS[specialization]["name"]
	return specialization.capitalize()

# ============================================================================
# HIRING PIPELINE — REVEAL / HIRE-STATE / CANDIDATE CARD (Phase A)
# ============================================================================

static func _neutral_appetites() -> Dictionary:
	"""All five appetites at 0.0 (neutral). Used as the deterministic default so a
	Researcher.new() before generate_random still exposes every appetite key."""
	var d := {}
	for k in APPETITE_KEYS:
		d[k] = 0.0
	return d

func get_seniority_band() -> String:
	"""Rough seniority (A1): visible even uninterviewed. A coarse BAND, not the exact
	skill number, so lane + seniority read at reveal 0 without leaking true skill."""
	if skill_level <= 2:
		return "Junior"
	elif skill_level <= 4:
		return "Mid"
	elif skill_level <= 6:
		return "Senior"
	elif skill_level <= 8:
		return "Staff"
	return "Principal"

# --- Reveal ladder (interviewing is Phase B; this is the API surface it drives) ---

func reveal_more(amount: int = 1) -> int:
	"""Raise reveal_level by `amount` (an interview step, Phase B), clamped to
	[0, MAX_REVEAL]. Returns the new level. Reveals NEVER fabricate -- they only
	unhide values the model already holds (ADR-0004)."""
	reveal_level = clampi(reveal_level + amount, 0, MAX_REVEAL)
	return reveal_level

func set_reveal_level(level: int) -> void:
	"""Directly set the reveal level (clamped). Used by hire-on (fully revealed) and load."""
	reveal_level = clampi(level, 0, MAX_REVEAL)

func is_field_revealed(field: String) -> bool:
	"""True if the card should show `field`'s true value at the current reveal_level.
	Unknown fields are treated as never-revealed. (Quirk is exposure-gated, not here.)"""
	var req: int = REVEAL_REQUIREMENTS.get(field, MAX_REVEAL + 1)
	return reveal_level >= req

func expose_quirk() -> void:
	"""An exposure event (ADR-0003) surfaces the rare quirk rider. Independent of the
	interview reveal ladder: a fully-interviewed hire can still have a hidden quirk (A2)."""
	quirk_known = true

func has_quirk() -> bool:
	"""True if this person actually carries a quirk (regardless of whether it is known)."""
	return quirk != ""

# --- Hire-state lifecycle (guarded transitions) ---

func can_transition_to(new_state: int) -> bool:
	"""Guard the pool -> offered -> employed -> departed lifecycle. DEPARTED is terminal."""
	match hire_state:
		HireState.CANDIDATE_IN_POOL:
			return new_state == HireState.OFFERED or new_state == HireState.DEPARTED
		HireState.OFFERED:
			return new_state == HireState.EMPLOYED \
				or new_state == HireState.CANDIDATE_IN_POOL \
				or new_state == HireState.DEPARTED
		HireState.EMPLOYED:
			return new_state == HireState.DEPARTED
		_:  # DEPARTED (terminal) or unknown
			return false

func transition_hire_state(new_state: int) -> bool:
	"""Apply a guarded hire-state transition. Returns false (no-op) if disallowed."""
	if can_transition_to(new_state):
		hire_state = new_state
		return true
	return false

func hire_state_name() -> String:
	match hire_state:
		HireState.CANDIDATE_IN_POOL:
			return "Candidate"
		HireState.OFFERED:
			return "Offer out"
		HireState.EMPLOYED:
			return "Employed"
		HireState.DEPARTED:
			return "Departed"
		_:
			return "Unknown"

# --- Candidate card (the hire-as-scouting info model, ADR-0004) ---

func get_card_data() -> Dictionary:
	"""The candidate-card INFO MODEL. Revealed fields carry their TRUE value; hidden
	fields carry HIDDEN_PLACEHOLDER. Identity (name/appearance/lane/seniority) is always
	shown; skill/comp/appetites/loyalty-risk gate on reveal_level; the quirk gates on an
	exposure event (quirk_known), never on the interview ladder (A2)."""
	var card := {
		"name": researcher_name,
		"appearance_id": appearance_id,
		"lane": get_specialization_name(),
		"seniority_band": get_seniority_band(),
		"hire_state": hire_state_name(),
		"reveal_level": reveal_level,
	}
	card["skill_level"] = skill_level if is_field_revealed("skill_level") else HIDDEN_PLACEHOLDER
	card["salary_expectation"] = salary_expectation if is_field_revealed("salary_expectation") else HIDDEN_PLACEHOLDER
	card["appetites"] = appetites.duplicate() if is_field_revealed("appetites") else HIDDEN_PLACEHOLDER
	card["loyalty_risk"] = loyalty_risk if is_field_revealed("loyalty_risk") else HIDDEN_PLACEHOLDER
	# Quirk: exposure-gated. Once known, "" reads as an explicit "none" (a checked absence).
	if quirk_known:
		card["quirk"] = quirk if quirk != "" else "none"
	else:
		card["quirk"] = HIDDEN_PLACEHOLDER
	return card

func get_card_text() -> String:
	"""A minimal formatted candidate card (Phase A view). See get_card_data for the model."""
	var c := get_card_data()
	var lines: Array[String] = []
	lines.append("%s  [%s]" % [c["name"], c["hire_state"]])
	lines.append("Lane: %s    Seniority: %s" % [c["lane"], c["seniority_band"]])
	lines.append("Skill: %s" % str(c["skill_level"]))
	if c["salary_expectation"] is float:
		lines.append("Comp expectation: $%.0f" % c["salary_expectation"])
	else:
		lines.append("Comp expectation: %s" % str(c["salary_expectation"]))
	if c["appetites"] is Dictionary:
		var parts: Array[String] = []
		for k in APPETITE_KEYS:
			parts.append("%s %d%%" % [k, int(round(float(c["appetites"][k]) * 100.0))])
		lines.append("Appetites: %s" % ", ".join(parts))
	else:
		lines.append("Appetites: %s" % str(c["appetites"]))
	if c["loyalty_risk"] is float:
		lines.append("Loyalty risk: %d%%" % int(round(c["loyalty_risk"] * 100.0)))
	else:
		lines.append("Loyalty risk: %s" % str(c["loyalty_risk"]))
	lines.append("Quirk: %s" % str(c["quirk"]))
	return "\n".join(lines)

# ============================================================================
# SERIALIZATION
# ============================================================================

func to_dict() -> Dictionary:
	"""Serialize to dictionary for saving"""
	return {
		"name": researcher_name,
		"specialization": specialization,
		"skill_level": skill_level,
		"salary_expectation": salary_expectation,
		"current_salary": current_salary,
		"base_productivity": base_productivity,
		"loyalty": loyalty,
		"burnout": burnout,
		"turns_employed": turns_employed,
		"jet_lag_turns": jet_lag_turns,
		"jet_lag_severity": jet_lag_severity,
		# --- Hiring pipeline hidden-ability layer (Phase A) ---
		# Appetites / loyalty-risk are SNAPPED to the repo-wide serialization grid
		# (DoomSystem.SAVE_QUANTUM) so the save/load round-trip is JSON-parse-stable --
		# Godot's JSON parse is not correctly-rounded, so an un-snapped double drifts a
		# ULP and breaks deep-equality (see the SERIALIZATION block in game_state.gd).
		"appearance_id": appearance_id,
		"hire_state": hire_state,          # enum -> int
		"reveal_level": reveal_level,
		"appetites": DoomSystem._snap_dict(appetites),
		"quirk": quirk,
		"quirk_known": quirk_known,
		"loyalty_risk": DoomSystem._snap(loyalty_risk),
		# --- Hiring pipeline identity + onboarding (Phase B) ---
		"candidate_id": candidate_id,
		"needs_visa": needs_visa,
		"onboarded": onboarded,
		"laptop_done": laptop_done,
		"visa_done": visa_done,
		"systems_done": systems_done,
		"meet_people_done": meet_people_done,
		"mentoring_done": mentoring_done,
		"mentoring_skipped": mentoring_skipped,
	}

func from_dict(data: Dictionary):
	"""Deserialize from dictionary (L7 #618: explicit casts — JSON numbers arrive as float)"""
	researcher_name = String(data.get("name", ""))
	specialization = String(data.get("specialization", "safety"))
	skill_level = int(data.get("skill_level", 5))
	salary_expectation = float(data.get("salary_expectation", 60000.0))
	current_salary = float(data.get("current_salary", 60000.0))
	base_productivity = float(data.get("base_productivity", 1.0))
	loyalty = int(data.get("loyalty", 50))
	burnout = float(data.get("burnout", 0.0))
	turns_employed = int(data.get("turns_employed", 0))
	jet_lag_turns = int(data.get("jet_lag_turns", 0))
	jet_lag_severity = float(data.get("jet_lag_severity", 0.0))
	# NOTE: legacy "traits" key (retired system) is intentionally ignored on load -- old saves
	# carrying it drop it silently; the quirk layer below is the replacement.

	# --- Hiring pipeline hidden-ability layer (Phase A). Explicit casts: JSON hands
	# every number back as float and every enum as float. Missing keys fall back to the
	# uninterviewed/neutral defaults so pre-Phase-A saves still load. ---
	appearance_id = String(data.get("appearance_id", ""))
	hire_state = int(data.get("hire_state", HireState.CANDIDATE_IN_POOL))
	reveal_level = int(data.get("reveal_level", REVEAL_UNINTERVIEWED))
	quirk = String(data.get("quirk", ""))
	quirk_known = bool(data.get("quirk_known", false))
	# Re-snap on load (idempotent) so the live values sit exactly on the grid, matching
	# the doom-intermediary convention -- keeps any future sim use deterministic.
	loyalty_risk = DoomSystem._snap(float(data.get("loyalty_risk", 0.0)))
	appetites = _neutral_appetites()
	var appetite_data = data.get("appetites", {})
	if appetite_data is Dictionary:
		for k in appetite_data.keys():
			appetites[String(k)] = DoomSystem._snap(float(appetite_data[k]))

	# --- Hiring pipeline identity + onboarding (Phase B). Missing keys fall back to the
	# legacy defaults (onboarded=true) so pre-Phase-B saves load productive. ---
	candidate_id = String(data.get("candidate_id", ""))
	needs_visa = bool(data.get("needs_visa", false))
	onboarded = bool(data.get("onboarded", true))
	laptop_done = bool(data.get("laptop_done", false))
	visa_done = bool(data.get("visa_done", false))
	# #789 checklist steps: missing keys (pre-#789 saves) default false. A pre-#789 save
	# mid-onboard therefore owes the new steps -- acceptable; #789 is a gameplay change.
	systems_done = bool(data.get("systems_done", false))
	meet_people_done = bool(data.get("meet_people_done", false))
	mentoring_done = bool(data.get("mentoring_done", false))
	mentoring_skipped = bool(data.get("mentoring_skipped", false))

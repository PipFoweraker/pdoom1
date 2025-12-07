extends Resource
class_name Researcher
## Individual researcher with specialization, traits, and burnout
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

# Traits (positive and negative)
var traits: Array[String] = []

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
# TRAITS
# ============================================================================

const POSITIVE_TRAITS = {
	"workaholic": {
		"name": "Workaholic",
		"productivity_bonus": 0.20,  # +20% productivity
		"burnout_rate": 2.0  # +2 burnout per turn
	},
	"team_player": {
		"name": "Team Player",
		"team_productivity_bonus": 0.10,  # +10% to ALL researchers
		"description": "Boosts entire team morale"
	},
	"media_savvy": {
		"name": "Media Savvy",
		"reputation_on_publish": 3,  # +3 reputation when publishing
		"description": "Great at public communication"
	},
	"safety_conscious": {
		"name": "Safety Conscious",
		"doom_reduction": 0.10,  # -10% doom from their work
		"description": "Extra careful about AI risks"
	},
	"fast_learner": {
		"name": "Fast Learner",
		"skill_growth_rate": 1.5,  # Skill improves 50% faster
		"description": "Rapidly improves over time"
	},
	"road_warrior": {
		"name": "Road Warrior",
		"jet_lag_reduction": 0.5,  # 50% less jet lag duration
		"description": "Recovers quickly from travel"
	}
}

const NEGATIVE_TRAITS = {
	"prima_donna": {
		"name": "Prima Donna",
		"salary_penalty_threshold": 0.9,  # Must be paid 90%+ of expectation
		"team_productivity_penalty": -0.10,  # -10% team productivity if underpaid
		"description": "Demands high salary or causes problems"
	},
	"leak_prone": {
		"name": "Leak Prone",
		"leak_chance_per_turn": 0.05,  # 5% chance to leak research
		"description": "Sometimes shares confidential info"
	},
	"burnout_prone": {
		"name": "Burnout Prone",
		"burnout_accumulation_multiplier": 1.5,  # 50% faster burnout
		"description": "Burns out more easily"
	},
	"pessimist": {
		"name": "Pessimist",
		"morale_penalty": -5,  # Reduces team morale
		"description": "Brings down team mood"
	}
}

# ============================================================================
# INITIALIZATION
# ============================================================================

func _init(spec: String = "safety", name: String = ""):
	specialization = spec
	researcher_name = name if name != "" else _generate_name()

	# Set base salary from specialization
	if SPECIALIZATIONS.has(spec):
		salary_expectation = SPECIALIZATIONS[spec]["base_cost"]
		current_salary = salary_expectation

	# Random skill level (3-7 for new hires, can grow)
	skill_level = randi_range(3, 7)

	# Base productivity from skill
	base_productivity = 0.5 + (skill_level * 0.1)  # 0.8 to 1.2 for skill 3-7

	# Random loyalty (40-70 for new hires)
	loyalty = randi_range(40, 70)

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

	# Trait bonuses
	if "workaholic" in traits:
		effective *= 1.20

	# Salary satisfaction (prima donna trait)
	if "prima_donna" in traits:
		if current_salary < (salary_expectation * 0.9):
			effective *= 0.80  # -20% productivity if underpaid

	# Minimum 10% productivity (even totally burned out)
	return max(effective, 0.1)

func get_doom_modifier() -> float:
	"""Get doom modification from this researcher's specialization and traits"""
	var modifier = 0.0

	# Specialization effects
	match specialization:
		"safety":
			modifier -= SPECIALIZATIONS["safety"]["doom_reduction_bonus"]
		"capabilities":
			modifier += SPECIALIZATIONS["capabilities"]["doom_per_research"]

	# Trait effects
	if "safety_conscious" in traits:
		modifier -= POSITIVE_TRAITS["safety_conscious"]["doom_reduction"]

	return modifier

# ============================================================================
# BURNOUT MANAGEMENT
# ============================================================================

func accumulate_burnout(amount: float):
	"""Add burnout (typically called each turn)"""
	var multiplier = 1.0

	# Trait modifiers
	if "burnout_prone" in traits:
		multiplier = NEGATIVE_TRAITS["burnout_prone"]["burnout_accumulation_multiplier"]
	if "workaholic" in traits:
		amount += POSITIVE_TRAITS["workaholic"]["burnout_rate"]

	burnout += amount * multiplier
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

	# Road warrior trait reduces duration
	if "road_warrior" in traits:
		base_turns = int(base_turns * POSITIVE_TRAITS["road_warrior"]["jet_lag_reduction"])

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
# TRAIT MANAGEMENT
# ============================================================================

func add_trait(trait_id: String):
	"""Add a trait if not already present"""
	if trait_id not in traits:
		traits.append(trait_id)

func has_trait(trait_id: String) -> bool:
	"""Check if researcher has a trait"""
	return trait_id in traits

func get_trait_description() -> String:
	"""Get human-readable trait list"""
	if traits.size() == 0:
		return "No special traits"

	var descriptions = []
	for trait_id in traits:
		if POSITIVE_TRAITS.has(trait_id):
			descriptions.append(POSITIVE_TRAITS[trait_id]["name"])
		elif NEGATIVE_TRAITS.has(trait_id):
			descriptions.append(NEGATIVE_TRAITS[trait_id]["name"])

	return ", ".join(descriptions)

# ============================================================================
# TURN PROCESSING
# ============================================================================

func process_turn(rng: RandomNumberGenerator = null):
	"""Called each turn - handle burnout, skill growth, jet lag recovery, etc."""
	turns_employed += 1

	# Base burnout accumulation (working is stressful!)
	accumulate_burnout(0.5)

	# Jet lag recovery (Issue #469)
	recover_jet_lag()

	# Skill growth (very slow - 1 point per ~20 turns)
	# Use provided RNG for determinism, fallback to global for tests
	var skill_roll = rng.randf() if rng else randf()
	if skill_roll < 0.05:  # 5% chance per turn
		skill_level = min(skill_level + 1, 10)
		base_productivity = 0.5 + (skill_level * 0.1)

	# Loyalty changes based on satisfaction
	var salary_ratio = current_salary / salary_expectation
	if salary_ratio >= 1.0:
		loyalty = min(loyalty + 1, 100)
	elif salary_ratio < 0.8:
		loyalty = max(loyalty - 2, 0)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

func _generate_name() -> String:
	"""Generate a random researcher name"""
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

	return FIRST_NAMES[randi() % FIRST_NAMES.size()] + " " + LAST_NAMES[randi() % LAST_NAMES.size()]

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
		"traits": traits.duplicate(),
		"jet_lag_turns": jet_lag_turns,
		"jet_lag_severity": jet_lag_severity
	}

func from_dict(data: Dictionary):
	"""Deserialize from dictionary"""
	researcher_name = data.get("name", "")
	specialization = data.get("specialization", "safety")
	skill_level = data.get("skill_level", 5)
	salary_expectation = data.get("salary_expectation", 60000.0)
	current_salary = data.get("current_salary", 60000.0)
	base_productivity = data.get("base_productivity", 1.0)
	loyalty = data.get("loyalty", 50)
	burnout = data.get("burnout", 0.0)
	turns_employed = data.get("turns_employed", 0)
	jet_lag_turns = data.get("jet_lag_turns", 0)
	jet_lag_severity = data.get("jet_lag_severity", 0.0)

	if data.has("traits"):
		traits.clear()
		for trait_name in data["traits"]:
			traits.append(trait_name)

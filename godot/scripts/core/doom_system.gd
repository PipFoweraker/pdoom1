extends Node
class_name DoomSystem
## Modular doom calculation system - designed for incremental complexity
## Start simple, add layers over time (Path of Exile style)

# ============================================================================
# PHASE 1: DOOM MOMENTUM (Current Implementation)
# ============================================================================

## Core doom state
var current_doom: float = 50.0

## Momentum mechanics - doom changes accumulate and compound
var doom_velocity: float = 0.0  # Current rate of doom change per turn
var doom_momentum: float = 0.0  # Accumulated momentum (compounds over time)

## Momentum tuning parameters (exposed for easy balancing)
var momentum_accumulation_rate: float = 0.15  # How much of each doom change becomes momentum
var momentum_decay_rate: float = 0.92  # Momentum decay per turn (0.92 = 8% decay)
var momentum_cap: float = 8.0  # Maximum momentum (prevents infinite spirals)

# ============================================================================
# PHASE 2: DOOM SOURCES (Tracking & Visualization)
# ============================================================================

## Source tracking - know where doom is coming from
var doom_sources: Dictionary = {
	"base": 0.0,               # Base organizational risk
	"capabilities": 0.0,        # From capabilities research
	"rivals": 0.0,              # From competitor actions
	"safety": 0.0,              # From safety research (negative)
	"unproductive": 0.0,        # From idle employees
	"events": 0.0,              # From random events
	"momentum": 0.0,            # From accumulated momentum
	# Future sources (placeholder):
	"technical_debt": 0.0,      # Phase 3
	"specializations": 0.0,     # Phase 3
	"cascades": 0.0,            # Phase 4
	"market_pressure": 0.0,     # Phase 4
}

# ============================================================================
# PHASE 3: DOOM MODIFIERS (Future - Researcher Specs, Tech Debt)
# ============================================================================

## Multipliers for doom sources (1.0 = normal, >1.0 = worse, <1.0 = better)
var doom_multipliers: Dictionary = {
	"capabilities": 1.0,        # Modified by: researcher traits, market cycles
	"safety": 1.0,              # Modified by: researcher specializations, upgrades
	"rivals": 1.0,              # Modified by: scouting, intelligence actions
	"events": 1.0,              # Modified by: reputation, safety culture
}

## Flat doom modifiers (added/subtracted from sources)
var doom_modifiers: Dictionary = {
	"capabilities": 0.0,        # e.g., "Safety Conscious" trait = -0.5
	"safety": 0.0,              # e.g., "Specialization bonus" = +1.0 to reduction
	"rivals": 0.0,              # e.g., "Intelligence gathered" = -2.0
}

# ============================================================================
# PHASE 4: DOOM AXES (Future - Multi-dimensional doom)
# ============================================================================

## Future: Split doom into strategic categories
var doom_axes_enabled: bool = false
var doom_capability_risk: float = 50.0
var doom_safety_gap: float = 50.0
var doom_competitive_pressure: float = 50.0

# ============================================================================
# CORE DOOM CALCULATION
# ============================================================================

func calculate_doom_change(state: GameState) -> Dictionary:
	"""
	Calculate doom change for this turn.
	Returns Dictionary with breakdown and metadata.

	Design: Modular calculation that can be extended over time
	"""

	# Reset source tracking
	_reset_doom_sources()

	# === PHASE 1: BASIC DOOM SOURCES ===
	_calculate_base_doom()
	_calculate_capability_doom(state)
	_calculate_safety_doom(state)
	_calculate_rival_doom(state)
	_calculate_unproductive_doom(state)

	# === PHASE 2: SOURCE TRACKING ===
	var raw_doom_change = _sum_doom_sources()

	# === PHASE 3: APPLY MULTIPLIERS (future enhancement point) ===
	raw_doom_change = _apply_doom_multipliers(raw_doom_change)

	# === PHASE 1: MOMENTUM SYSTEM ===
	var momentum_contribution = _calculate_momentum(raw_doom_change)
	doom_sources["momentum"] = momentum_contribution

	# === FINAL DOOM CHANGE ===
	var total_doom_change = raw_doom_change + momentum_contribution

	# Update doom
	current_doom += total_doom_change
	current_doom = clamp(current_doom, 0.0, 100.0)

	# Return detailed breakdown
	return {
		"total_change": total_doom_change,
		"raw_change": raw_doom_change,
		"momentum": momentum_contribution,
		"velocity": doom_velocity,
		"sources": doom_sources.duplicate(),
		"new_doom": current_doom,
		"trend": _get_doom_trend()
	}

# ============================================================================
# PHASE 1 CALCULATIONS
# ============================================================================

func _calculate_base_doom():
	"""Base doom increase - organizational risk"""
	doom_sources["base"] = 1.0

func _calculate_capability_doom(state: GameState):
	"""Doom from capabilities research - Modified by specializations if using new system"""
	# Let _calculate_safety_doom handle both if using researcher system
	if state.researchers.size() > 0:
		return  # Will be calculated in _calculate_researcher_doom

	# Legacy fallback
	doom_sources["capabilities"] = state.capability_researchers * 3.0

func _calculate_safety_doom(state: GameState):
	"""Doom reduction from safety research - Modified by researcher specializations"""
	# Use new researcher system if available
	if state.researchers.size() > 0:
		_calculate_researcher_doom(state)
		return

	# Legacy fallback
	# Only count productive safety researchers
	var total_staff = state.safety_researchers + state.capability_researchers + state.compute_engineers
	var management_capacity = state.get_management_capacity()
	var managed = min(total_staff, management_capacity)
	var available_compute = int(state.compute)
	var productive = min(managed, available_compute)

	# Estimate productive safety researchers (proportional distribution)
	var productive_safety = 0
	if total_staff > 0:
		var safety_ratio = float(state.safety_researchers) / float(total_staff)
		productive_safety = int(productive * safety_ratio)

	doom_sources["safety"] = -productive_safety * 3.5

func _calculate_researcher_doom(state: GameState):
	"""Calculate doom from individual researchers with specializations"""
	var total_staff = state.researchers.size()
	var management_capacity = state.get_management_capacity()
	var managed = min(total_staff, management_capacity)
	var available_compute = int(state.compute)
	var productive_count = min(managed, available_compute)

	var safety_doom = 0.0
	var cap_doom = 0.0
	var spec_doom = 0.0  # Specialization modifiers

	# Calculate per-researcher contributions
	var processed = 0
	for researcher in state.researchers:
		# Only productive researchers contribute
		if processed >= productive_count:
			break
		processed += 1

		var productivity = researcher.get_effective_productivity()

		# Base doom contribution by specialization
		match researcher.specialization:
			"safety":
				# Base 3.5, modified by specialization bonus (15%)
				var base = -3.5 * productivity
				var bonus = base * Researcher.SPECIALIZATIONS["safety"]["doom_reduction_bonus"]
				safety_doom += base + bonus

			"capabilities":
				# Base 3.0, with doom penalty (5%)
				var base = 3.0 * productivity
				var penalty = base * Researcher.SPECIALIZATIONS["capabilities"]["doom_per_research"]
				cap_doom += base + penalty

			"interpretability":
				# Counts as safety researcher
				safety_doom += -3.0 * productivity

			"alignment":
				# Counts as safety researcher with slight bonus
				safety_doom += -3.2 * productivity

		# Apply researcher's personal doom modifier (from traits)
		spec_doom += researcher.get_doom_modifier() * productivity

	doom_sources["safety"] = safety_doom
	doom_sources["capabilities"] = cap_doom
	doom_sources["specializations"] = spec_doom

func _calculate_rival_doom(state: GameState):
	"""Doom from rival actions - already calculated in turn manager"""
	# This is set externally by turn_manager after rival processing
	pass

func _calculate_unproductive_doom(state: GameState):
	"""Doom from unproductive employees"""
	var unmanaged = state.get_unmanaged_count()
	var total_staff = state.safety_researchers + state.capability_researchers + state.compute_engineers
	var management_capacity = state.get_management_capacity()
	var managed = min(total_staff, management_capacity)
	var available_compute = int(state.compute)
	var productive = min(managed, available_compute)
	var total_unproductive = (total_staff - productive) + unmanaged

	doom_sources["unproductive"] = total_unproductive * 0.5

# ============================================================================
# MOMENTUM SYSTEM (PHASE 1)
# ============================================================================

func _calculate_momentum(raw_doom_change: float) -> float:
	"""
	Calculate momentum contribution.

	Momentum accumulates from doom changes and compounds over time.
	Creates "doom spiral" or "safety flywheel" effects.
	"""

	# Update velocity (smoothed doom change)
	doom_velocity = doom_velocity * 0.7 + raw_doom_change * 0.3  # 30% new, 70% old

	# Accumulate momentum (portion of doom change becomes momentum)
	doom_momentum += raw_doom_change * momentum_accumulation_rate

	# Cap momentum (prevent infinite spirals)
	doom_momentum = clamp(doom_momentum, -momentum_cap, momentum_cap)

	# Decay momentum slightly each turn (prevents permanent momentum)
	doom_momentum *= momentum_decay_rate

	# Return momentum contribution
	return doom_momentum

# ============================================================================
# PHASE 3: MULTIPLIERS & MODIFIERS (Extension Point)
# ============================================================================

func _apply_doom_multipliers(raw_doom_change: float) -> float:
	"""
	Apply multipliers to doom sources.

	Extension point for:
	- Researcher specializations
	- Market cycles
	- Technical debt effects
	- Upgrade bonuses
	"""

	# Future: Apply multipliers per source
	# For now, just return raw value
	return raw_doom_change

func apply_doom_modifier(source: String, modifier: float):
	"""
	Add a modifier to a doom source.

	Examples:
	- apply_doom_modifier("capabilities", -0.5)  # Safety Conscious trait
	- apply_doom_modifier("safety", 1.0)         # Specialization bonus
	"""
	if doom_modifiers.has(source):
		doom_modifiers[source] += modifier

func set_doom_multiplier(source: String, multiplier: float):
	"""
	Set a multiplier for a doom source.

	Examples:
	- set_doom_multiplier("rivals", 0.7)  # Intelligence reduces rival doom 30%
	- set_doom_multiplier("events", 1.5)  # Market panic increases event doom 50%
	"""
	if doom_multipliers.has(source):
		doom_multipliers[source] = multiplier

# ============================================================================
# EVENT DOOM (Extension Point)
# ============================================================================

func add_event_doom(amount: float, reason: String = ""):
	"""
	Add doom from an event.
	Useful for one-time doom spikes (breakthroughs, cascades, etc.)
	"""
	doom_sources["events"] += amount
	current_doom += amount
	current_doom = clamp(current_doom, 0.0, 100.0)

func set_rival_doom_contribution(amount: float):
	"""Called by turn_manager after processing rival actions"""
	doom_sources["rivals"] = amount

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

func _reset_doom_sources():
	"""Reset source tracking for new turn"""
	for key in doom_sources.keys():
		doom_sources[key] = 0.0

func _sum_doom_sources() -> float:
	"""Sum all doom sources except momentum (calculated separately)"""
	var total = 0.0
	for key in doom_sources.keys():
		if key != "momentum":
			total += doom_sources[key]
	return total

func _get_doom_trend() -> String:
	"""Get human-readable doom trend"""
	if doom_velocity < -2.0:
		return "strongly_decreasing"
	elif doom_velocity < -0.5:
		return "decreasing"
	elif doom_velocity < 0.5:
		return "stable"
	elif doom_velocity < 2.0:
		return "increasing"
	else:
		return "strongly_increasing"

func get_doom_status() -> String:
	"""Get doom status level"""
	if current_doom < 25:
		return "safe"
	elif current_doom < 50:
		return "warning"
	elif current_doom < 70:
		return "danger"
	elif current_doom < 90:
		return "critical"
	else:
		return "catastrophic"

func get_momentum_description() -> String:
	"""Human-readable momentum description"""
	if abs(doom_momentum) < 0.5:
		return "neutral"
	elif doom_momentum > 0:
		return "doom spiral (%.1f)" % doom_momentum
	else:
		return "safety flywheel (%.1f)" % abs(doom_momentum)

# ============================================================================
# FUTURE EXTENSION POINTS (Commented Examples)
# ============================================================================

# PHASE 3 EXAMPLE: Researcher Specialization
# func apply_researcher_specialization_effects(researchers: Array):
#     for researcher in researchers:
#         match researcher.specialization:
#             "safety":
#                 apply_doom_modifier("safety", 0.15)  # +15% safety effectiveness
#             "capabilities":
#                 apply_doom_modifier("capabilities", 0.05)  # +5% cap doom
#             "interpretability":
#                 set_doom_multiplier("events", 0.9)  # -10% event doom
#             "alignment":
#                 apply_doom_modifier("rivals", -0.5)  # Reduce rival doom

# PHASE 3 EXAMPLE: Technical Debt
# func apply_technical_debt_effects(debt: int):
#     var debt_multiplier = 1.0 + (debt * 0.05)  # 5% per debt point
#     set_doom_multiplier("rivals", debt_multiplier)
#     doom_sources["technical_debt"] = debt * 0.2  # Direct doom from debt

# PHASE 4 EXAMPLE: Multi-Axis Doom
# func enable_doom_axes():
#     doom_axes_enabled = true
#     # Split current doom into axes
#     doom_capability_risk = current_doom * 0.4
#     doom_safety_gap = current_doom * 0.4
#     doom_competitive_pressure = current_doom * 0.2

# PHASE 4 EXAMPLE: Cascade Events
# func trigger_cascade_event(cascade_type: String, severity: float):
#     var cascade_doom = severity * 5.0  # 10-20 doom for big cascades
#     doom_sources["cascades"] = cascade_doom
#     add_event_doom(cascade_doom, "cascade_%s" % cascade_type)

# ============================================================================
# SERIALIZATION (for save/load)
# ============================================================================

func to_dict() -> Dictionary:
	"""Serialize doom system state"""
	return {
		"current_doom": current_doom,
		"doom_velocity": doom_velocity,
		"doom_momentum": doom_momentum,
		"doom_sources": doom_sources.duplicate(),
		"doom_multipliers": doom_multipliers.duplicate(),
		"doom_modifiers": doom_modifiers.duplicate()
	}

func from_dict(data: Dictionary):
	"""Deserialize doom system state"""
	current_doom = data.get("current_doom", 50.0)
	doom_velocity = data.get("doom_velocity", 0.0)
	doom_momentum = data.get("doom_momentum", 0.0)
	if data.has("doom_sources"):
		doom_sources = data["doom_sources"].duplicate()
	if data.has("doom_multipliers"):
		doom_multipliers = data["doom_multipliers"].duplicate()
	if data.has("doom_modifiers"):
		doom_modifiers = data["doom_modifiers"].duplicate()

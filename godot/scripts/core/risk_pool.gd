extends Node
class_name RiskPool
## Hidden risk accumulation system - consequences manifest stochastically over time
## See godot/docs/design/RISK_SYSTEM.md for full design documentation

# ============================================================================
# RISK POOLS
# ============================================================================

## The six risk pools - hidden from players, visible in dev mode
var pools: Dictionary = {
	"capability_overhang": 0.0,    # AI capabilities outpacing safety
	"research_integrity": 0.0,     # Quality/trustworthiness of work
	"regulatory_attention": 0.0,   # Government/institutional scrutiny
	"public_awareness": 0.0,       # General public attention to AI risks
	"insider_threat": 0.0,         # Internal organizational risk
	"financial_exposure": 0.0,     # Funding uncertainty and cash flow fragility
}

## Human-readable names for UI
const POOL_NAMES: Dictionary = {
	"capability_overhang": "Capability Overhang",
	"research_integrity": "Research Integrity",
	"regulatory_attention": "Regulatory Attention",
	"public_awareness": "Public Awareness",
	"insider_threat": "Insider Threat",
	"financial_exposure": "Financial Exposure",
}

## Pool descriptions for tooltips
const POOL_DESCRIPTIONS: Dictionary = {
	"capability_overhang": "The gap between AI capabilities and safety understanding",
	"research_integrity": "The quality and trustworthiness of your lab's work",
	"regulatory_attention": "Government and institutional scrutiny of AI development",
	"public_awareness": "General public attention to AI risks and your lab",
	"insider_threat": "Risk from within your organization",
	"financial_exposure": "Funding uncertainty and cash flow fragility",
}

# ============================================================================
# THRESHOLD TRACKING
# ============================================================================

## Thresholds that trigger guaranteed events
const THRESHOLDS: Array[int] = [50, 75, 100]

## Track which threshold tier has been triggered for each pool (0-3)
## Prevents re-triggering the same tier multiple times
var triggered_tiers: Dictionary = {
	"capability_overhang": 0,
	"research_integrity": 0,
	"regulatory_attention": 0,
	"public_awareness": 0,
	"insider_threat": 0,
	"financial_exposure": 0,
}

# ============================================================================
# HISTORY TRACKING
# ============================================================================

## History of risk changes for trend analysis
## Format: Array of {turn: int, pool: String, change: float, source: String}
var risk_history: Array[Dictionary] = []

## Maximum history entries to keep
const MAX_HISTORY: int = 100

# ============================================================================
# RISK CONTRIBUTION (Adding Risk)
# ============================================================================

func add_risk(pool_name: String, amount: float, source: String = "", turn: int = -1) -> void:
	"""
	Add risk to a pool.

	Examples:
		add_risk("research_integrity", 5.0, "rushed_paper", state.turn)
		add_risk("financial_exposure", 3.0, "aggressive_hiring")
		add_risk("capability_overhang", -2.0, "safety_publication")  # Negative = reduction
	"""
	if not pools.has(pool_name):
		push_warning("RiskPool: Unknown pool '%s'" % pool_name)
		return

	pools[pool_name] += amount
	pools[pool_name] = clamp(pools[pool_name], 0.0, 150.0)  # Allow overflow past 100 for severe cases

	# Track history
	_add_history_entry(pool_name, amount, source, turn)


func add_risk_multi(contributions: Dictionary, source: String = "", turn: int = -1) -> void:
	"""
	Add risk to multiple pools at once.

	Example:
		add_risk_multi({
			"research_integrity": 3.0,
			"capability_overhang": 2.0
		}, "rushed_capabilities_paper", state.turn)
	"""
	for pool_name in contributions.keys():
		add_risk(pool_name, contributions[pool_name], source, turn)


func reduce_risk(pool_name: String, amount: float, source: String = "", turn: int = -1) -> void:
	"""
	Reduce risk in a pool (convenience wrapper for negative add_risk).
	Risk does NOT decay automatically - requires active intervention.

	Examples:
		reduce_risk("research_integrity", 5.0, "published_negative_results")
		reduce_risk("financial_exposure", 10.0, "successful_grant")
	"""
	add_risk(pool_name, -abs(amount), source, turn)

# ============================================================================
# EVENT TRIGGERING (Hybrid System)
# ============================================================================

func process_turn(state, rng: RandomNumberGenerator) -> Array[Dictionary]:
	"""
	Process risk pools for this turn. Called during turn execution.

	Returns array of triggered events (may be empty).
	Uses hybrid system: probabilistic + threshold guarantees.
	"""
	var triggered_events: Array[Dictionary] = []

	for pool_name in pools.keys():
		var pool_value = pools[pool_name]

		# Skip if pool is empty or very low
		if pool_value < 5.0:
			continue

		# === PROBABILISTIC CHECK ===
		# Probability scales with pool value (pool 30 = 30% chance)
		var probability = pool_value / 100.0
		var roll = rng.randf()
		var triggered_by_roll = roll < probability

		# === THRESHOLD CHECK ===
		# Guaranteed trigger when crossing 50, 75, 100
		var current_tier = _get_threshold_tier(pool_value)
		var triggered_by_threshold = current_tier > triggered_tiers[pool_name]

		# === TRIGGER EVENT ===
		if triggered_by_roll or triggered_by_threshold:
			var event = _create_risk_event(pool_name, current_tier, triggered_by_threshold)
			triggered_events.append(event)

			# Update threshold tracking
			if triggered_by_threshold:
				triggered_tiers[pool_name] = current_tier

			# Record for verification (if VerificationTracker exists)
			_record_trigger(pool_name, roll, probability, triggered_by_roll, triggered_by_threshold, state)

	return triggered_events


func _get_threshold_tier(pool_value: float) -> int:
	"""Get threshold tier for a pool value"""
	if pool_value >= 100:
		return 3  # Catastrophic
	elif pool_value >= 75:
		return 2  # Severe
	elif pool_value >= 50:
		return 1  # Moderate
	return 0      # None


func _create_risk_event(pool_name: String, tier: int, from_threshold: bool) -> Dictionary:
	"""
	Create a risk event dictionary.

	Note: Actual event content comes from events.gd event tables.
	This returns metadata for the event system to use.
	"""
	var severity = "minor"
	if tier >= 3:
		severity = "catastrophic"
	elif tier >= 2:
		severity = "severe"
	elif tier >= 1:
		severity = "moderate"

	return {
		"type": "risk_event",
		"pool": pool_name,
		"pool_name": POOL_NAMES.get(pool_name, pool_name),
		"severity": severity,
		"tier": tier,
		"from_threshold": from_threshold,
		"pool_value": pools[pool_name],
		# Event content populated by events.gd
		"event_id": "",
		"title": "",
		"description": "",
		"choices": [],
	}


func _record_trigger(pool_name: String, roll: float, probability: float,
					  by_roll: bool, by_threshold: bool, state) -> void:
	"""Record trigger for verification/debugging"""
	# Check if VerificationTracker exists (it's an autoload)
	if Engine.has_singleton("VerificationTracker"):
		var tracker = Engine.get_singleton("VerificationTracker")
		if tracker.has_method("record_rng_outcome"):
			var turn = state.turn if state and state.has("turn") else -1
			tracker.record_rng_outcome("risk_%s" % pool_name, roll, turn)

# ============================================================================
# OPPONENT CONTRIBUTIONS (Stub for Future)
# ============================================================================

func add_opponent_contribution(pool_name: String, amount: float, opponent_id: String = "") -> void:
	"""
	Add risk contribution from opponent/rival lab.

	Stub for future opponent system integration.
	Some pools are shared (capability_overhang), others are lab-specific.
	"""
	# For now, just add to pool
	# Future: track opponent contributions separately for causal analysis
	add_risk(pool_name, amount, "opponent_%s" % opponent_id)


func apply_industry_effect(pool_name: String, amount: float, reason: String = "") -> void:
	"""
	Apply industry-wide effect to a pool.

	Examples:
		- Major AI incident increases public_awareness for everyone
		- Industry safety initiative reduces capability_overhang for all
	"""
	add_risk(pool_name, amount, "industry_%s" % reason)

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

func get_pool_value(pool_name: String) -> float:
	"""Get current value of a pool"""
	return pools.get(pool_name, 0.0)


func get_pool_status(pool_name: String) -> String:
	"""Get human-readable status for a pool"""
	var value = get_pool_value(pool_name)
	if value < 25:
		return "low"
	elif value < 50:
		return "moderate"
	elif value < 75:
		return "high"
	elif value < 100:
		return "critical"
	else:
		return "extreme"


func get_highest_risk_pool() -> String:
	"""Get the pool with highest current risk"""
	var highest_pool = ""
	var highest_value = -1.0

	for pool_name in pools.keys():
		if pools[pool_name] > highest_value:
			highest_value = pools[pool_name]
			highest_pool = pool_name

	return highest_pool


func get_total_risk() -> float:
	"""Get sum of all pool values (for aggregate indicators)"""
	var total = 0.0
	for pool_name in pools.keys():
		total += pools[pool_name]
	return total


func get_average_risk() -> float:
	"""Get average risk across all pools"""
	return get_total_risk() / pools.size()


func get_pools_above_threshold(threshold: float) -> Array[String]:
	"""Get list of pools above a given threshold"""
	var result: Array[String] = []
	for pool_name in pools.keys():
		if pools[pool_name] >= threshold:
			result.append(pool_name)
	return result

# ============================================================================
# HISTORY & TRENDS
# ============================================================================

func _add_history_entry(pool_name: String, change: float, source: String, turn: int) -> void:
	"""Add entry to risk history"""
	risk_history.append({
		"turn": turn,
		"pool": pool_name,
		"change": change,
		"source": source,
		"new_value": pools[pool_name],
	})

	# Trim history if too long
	while risk_history.size() > MAX_HISTORY:
		risk_history.pop_front()


func get_pool_trend(pool_name: String, turns: int = 5) -> float:
	"""
	Get trend for a pool over last N turns.
	Returns average change per turn (positive = increasing risk).
	"""
	var relevant_entries = risk_history.filter(func(entry):
		return entry["pool"] == pool_name
	)

	# Get last N entries
	var recent = relevant_entries.slice(-turns) if relevant_entries.size() > turns else relevant_entries

	if recent.is_empty():
		return 0.0

	var total_change = 0.0
	for entry in recent:
		total_change += entry["change"]

	return total_change / recent.size()


func get_recent_risk_sources(pool_name: String, count: int = 5) -> Array[Dictionary]:
	"""Get recent sources of risk for a pool (for causal analysis)"""
	var relevant = risk_history.filter(func(entry):
		return entry["pool"] == pool_name and entry["change"] > 0
	)
	return relevant.slice(-count) if relevant.size() > count else relevant

# ============================================================================
# DEV MODE / DEBUG
# ============================================================================

func get_debug_summary() -> String:
	"""Get formatted debug summary of all pools"""
	var lines: Array[String] = ["=== RISK POOLS ==="]

	for pool_name in pools.keys():
		var value = pools[pool_name]
		var status = get_pool_status(pool_name)
		var tier = triggered_tiers[pool_name]
		var trend = get_pool_trend(pool_name)
		var trend_str = "+" if trend > 0 else ""

		lines.append("%s: %.1f (%s) [tier %d] %s%.1f/turn" % [
			POOL_NAMES[pool_name],
			value,
			status,
			tier,
			trend_str,
			trend
		])

	lines.append("Total: %.1f | Avg: %.1f" % [get_total_risk(), get_average_risk()])

	return "\n".join(lines)


func get_dev_mode_data() -> Dictionary:
	"""Get all data for dev mode display"""
	var pool_data: Dictionary = {}

	for pool_name in pools.keys():
		pool_data[pool_name] = {
			"value": pools[pool_name],
			"status": get_pool_status(pool_name),
			"tier": triggered_tiers[pool_name],
			"trend": get_pool_trend(pool_name),
			"name": POOL_NAMES[pool_name],
			"description": POOL_DESCRIPTIONS[pool_name],
			"trigger_probability": pools[pool_name] / 100.0,
		}

	return {
		"pools": pool_data,
		"total_risk": get_total_risk(),
		"average_risk": get_average_risk(),
		"highest_risk": get_highest_risk_pool(),
		"pools_above_50": get_pools_above_threshold(50),
		"recent_history": risk_history.slice(-10),
	}

# ============================================================================
# NARRATIVE HINTS (Player-Facing, Insight-Gated)
# ============================================================================

func get_narrative_hint(pool_name: String, insight_level: int = 0) -> String:
	"""
	Get player-facing hint about a pool's status.

	insight_level:
		0 = No hint
		1-2 = Vague
		3-4 = Directional
		5-6 = Specific
		7+ = Quantified
	"""
	var value = pools[pool_name]
	var status = get_pool_status(pool_name)

	if insight_level <= 0:
		return ""

	if insight_level <= 2:
		# Vague hints
		if value >= 75:
			return "Something feels deeply wrong."
		elif value >= 50:
			return "There are concerning signs."
		elif value >= 25:
			return "Minor tensions are present."
		return ""

	elif insight_level <= 4:
		# Directional hints
		var pool_name_display = POOL_NAMES.get(pool_name, pool_name)
		if value >= 75:
			return "%s is becoming critical." % pool_name_display
		elif value >= 50:
			return "%s needs attention." % pool_name_display
		elif value >= 25:
			return "%s is elevated." % pool_name_display
		return ""

	elif insight_level <= 6:
		# Specific hints
		var pool_name_display = POOL_NAMES.get(pool_name, pool_name)
		return "%s: %s (trending %s)" % [
			pool_name_display,
			status,
			"up" if get_pool_trend(pool_name) > 0 else "stable" if get_pool_trend(pool_name) == 0 else "down"
		]

	else:
		# Full quantified (expert/dev mode)
		return "%s: %.1f / 100" % [POOL_NAMES.get(pool_name, pool_name), value]


func get_all_narrative_hints(insight_level: int = 0) -> Array[String]:
	"""Get narrative hints for all pools above threshold"""
	var hints: Array[String] = []

	for pool_name in pools.keys():
		var hint = get_narrative_hint(pool_name, insight_level)
		if not hint.is_empty():
			hints.append(hint)

	return hints

# ============================================================================
# SERIALIZATION
# ============================================================================

func to_dict() -> Dictionary:
	"""Serialize risk pool state for save/load"""
	return {
		"pools": pools.duplicate(),
		"triggered_tiers": triggered_tiers.duplicate(),
		"risk_history": risk_history.duplicate(),
	}


func from_dict(data: Dictionary) -> void:
	"""Deserialize risk pool state"""
	if data.has("pools"):
		# Merge with defaults to handle new pools added in updates
		for pool_name in data["pools"].keys():
			if pools.has(pool_name):
				pools[pool_name] = data["pools"][pool_name]

	if data.has("triggered_tiers"):
		for pool_name in data["triggered_tiers"].keys():
			if triggered_tiers.has(pool_name):
				triggered_tiers[pool_name] = data["triggered_tiers"][pool_name]

	if data.has("risk_history"):
		risk_history = data["risk_history"].duplicate()


func reset() -> void:
	"""Reset all pools to zero (for new game)"""
	for pool_name in pools.keys():
		pools[pool_name] = 0.0
		triggered_tiers[pool_name] = 0
	risk_history.clear()

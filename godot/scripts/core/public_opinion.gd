extends Node
class_name PublicOpinion
## Tracks public sentiment and opinion metrics for the AI safety lab
##
## The public opinion system provides a more nuanced view of how the world
## perceives your lab beyond simple reputation. It tracks four key metrics
## that affect gameplay in different ways.

## General public sentiment about AI development (0-100)
## High sentiment = public optimism, Low sentiment = fear/pessimism
var public_sentiment: float = 50.0

## Public trust specifically in your organization (0-100)
## High trust = easier funding/recruitment, Low trust = scrutiny/penalties
var lab_trust: float = 50.0

## How much the public cares about AI safety (0-100)
## High awareness = safety research valued, capability research scrutinized
var safety_awareness: float = 20.0

## Current level of media attention on AI sector (0-100)
## High attention = amplified effects, more scrutiny
var media_attention: float = 0.0

## Opinion volatility multiplier (affects rate of change)
var volatility: float = 1.0

## History of opinion values (for tracking trends)
var history: Array[Dictionary] = []
const MAX_HISTORY: int = 20

## Active opinion modifiers (temporary effects)
var active_modifiers: Array[Dictionary] = []


func _init(starting_reputation: float = 50.0):
	"""Initialize public opinion with optional reputation-based adjustments"""
	# Adjust starting trust based on initial reputation
	lab_trust = 40.0 + (starting_reputation * 0.2)  # 40-60 range based on rep

	# Record initial state
	_record_history()


func update_opinion(metric: String, change: float, reason: String = ""):
	"""
	Update a public opinion metric by a given amount

	Args:
		metric: One of "public_sentiment", "lab_trust", "safety_awareness", "media_attention"
		change: Amount to change (can be positive or negative)
		reason: Optional description for tracking
	"""
	# Apply volatility multiplier
	var actual_change = change * volatility

	# Update the appropriate metric
	match metric:
		"public_sentiment":
			public_sentiment = clamp(public_sentiment + actual_change, 0.0, 100.0)
		"lab_trust":
			lab_trust = clamp(lab_trust + actual_change, 0.0, 100.0)
		"safety_awareness":
			safety_awareness = clamp(safety_awareness + actual_change, 0.0, 100.0)
		"media_attention":
			media_attention = clamp(media_attention + actual_change, 0.0, 100.0)
		_:
			push_warning("Unknown public opinion metric: " + metric)

	if reason:
		print("[PublicOpinion] %s %+.1f (%s)" % [metric, actual_change, reason])


func add_modifier(metric: String, change_per_turn: float, duration: int, description: String = ""):
	"""
	Add a temporary modifier that affects opinion over multiple turns

	Args:
		metric: Which opinion metric to affect
		change_per_turn: Amount of change each turn
		duration: How many turns the modifier lasts
		description: What caused this modifier
	"""
	active_modifiers.append({
		"metric": metric,
		"change_per_turn": change_per_turn,
		"duration": duration,
		"remaining_turns": duration,
		"description": description
	})


func process_turn():
	"""Process end-of-turn effects: apply modifiers, natural decay, record history"""
	# Apply active modifiers
	for modifier in active_modifiers:
		update_opinion(modifier["metric"], modifier["change_per_turn"], modifier["description"])
		modifier["remaining_turns"] -= 1

	# Remove expired modifiers
	active_modifiers = active_modifiers.filter(func(m): return m["remaining_turns"] > 0)

	# Natural decay toward neutral (50)
	_apply_natural_decay()

	# Record current state
	_record_history()


func _apply_natural_decay():
	"""Opinion values naturally drift toward neutral over time"""
	const DECAY_RATE = 0.5  # Points per turn toward center

	# Public sentiment drifts to 50
	if public_sentiment > 50.0:
		public_sentiment = max(50.0, public_sentiment - DECAY_RATE)
	elif public_sentiment < 50.0:
		public_sentiment = min(50.0, public_sentiment + DECAY_RATE)

	# Lab trust drifts to 50
	if lab_trust > 50.0:
		lab_trust = max(50.0, lab_trust - DECAY_RATE)
	elif lab_trust < 50.0:
		lab_trust = min(50.0, lab_trust + DECAY_RATE)

	# Media attention decays to 0
	if media_attention > 0.0:
		media_attention = max(0.0, media_attention - DECAY_RATE * 2)  # Faster decay

	# Safety awareness decays slowly to 20 (baseline low awareness)
	if safety_awareness > 20.0:
		safety_awareness = max(20.0, safety_awareness - DECAY_RATE * 0.5)


func _record_history():
	"""Record current opinion state to history"""
	history.append({
		"public_sentiment": public_sentiment,
		"lab_trust": lab_trust,
		"safety_awareness": safety_awareness,
		"media_attention": media_attention
	})

	# Limit history size
	if history.size() > MAX_HISTORY:
		history.pop_front()


func get_lab_trust_level() -> String:
	"""Get descriptive level of lab trust"""
	if lab_trust >= 80.0:
		return "Exemplary"
	elif lab_trust >= 70.0:
		return "High"
	elif lab_trust >= 50.0:
		return "Moderate"
	elif lab_trust >= 30.0:
		return "Low"
	else:
		return "Crisis"


func get_public_sentiment_level() -> String:
	"""Get descriptive level of public sentiment"""
	if public_sentiment >= 70.0:
		return "Optimistic"
	elif public_sentiment >= 50.0:
		return "Neutral"
	elif public_sentiment >= 30.0:
		return "Concerned"
	else:
		return "Fearful"


func get_awareness_level() -> String:
	"""Get descriptive level of safety awareness"""
	if safety_awareness >= 70.0:
		return "Highly Aware"
	elif safety_awareness >= 40.0:
		return "Moderately Aware"
	else:
		return "Largely Unaware"


func get_funding_multiplier() -> float:
	"""Calculate funding availability multiplier based on lab trust"""
	if lab_trust >= 70.0:
		return 1.2  # +20% funding
	elif lab_trust <= 30.0:
		return 0.7  # -30% funding
	else:
		return 1.0  # Neutral


func get_regulatory_pressure_modifier() -> float:
	"""Calculate regulatory pressure modifier based on lab trust"""
	if lab_trust >= 70.0:
		return -0.1  # -10% regulatory pressure
	elif lab_trust <= 30.0:
		return 0.2  # +20% regulatory pressure
	else:
		return 0.0  # Neutral


func get_reputation_multiplier_for_safety_research() -> float:
	"""Safety research generates more reputation when safety awareness is high"""
	if safety_awareness >= 70.0:
		return 1.5  # +50% reputation from safety research
	else:
		return 1.0  # Normal reputation gains


func is_high_media_attention() -> bool:
	"""Check if media attention is high enough to amplify effects"""
	return media_attention >= 50.0


func get_active_modifier_count() -> int:
	"""Get number of active opinion modifiers"""
	return active_modifiers.size()


func get_modifier_summary() -> String:
	"""Get summary of active modifiers for display"""
	if active_modifiers.is_empty():
		return "No active modifiers"

	var summary = "Active modifiers:\n"
	for modifier in active_modifiers:
		summary += "- %s: %+.1f/turn (%d turns)\n" % [
			modifier["description"],
			modifier["change_per_turn"],
			modifier["remaining_turns"]
		]
	return summary


func to_dict() -> Dictionary:
	"""Serialize to dictionary for saving"""
	return {
		"public_sentiment": public_sentiment,
		"lab_trust": lab_trust,
		"safety_awareness": safety_awareness,
		"media_attention": media_attention,
		"volatility": volatility,
		"history": history,
		"active_modifiers": active_modifiers
	}


func from_dict(data: Dictionary):
	"""Deserialize from dictionary for loading"""
	public_sentiment = data.get("public_sentiment", 50.0)
	lab_trust = data.get("lab_trust", 50.0)
	safety_awareness = data.get("safety_awareness", 20.0)
	media_attention = data.get("media_attention", 0.0)
	volatility = data.get("volatility", 1.0)
	history = data.get("history", [])
	active_modifiers = data.get("active_modifiers", [])


func get_status_summary() -> String:
	"""Get compact status summary for UI display"""
	return "Lab Trust: %s (%.0f) | Public Sentiment: %s (%.0f) | Safety Awareness: %s (%.0f) | Media Attention: %.0f" % [
		get_lab_trust_level(),
		lab_trust,
		get_public_sentiment_level(),
		public_sentiment,
		get_awareness_level(),
		safety_awareness,
		media_attention
	]

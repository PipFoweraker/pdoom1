extends RefCounted
class_name SeedSchedule
## ADR-0005 -- a seed = RNG seed + event schedule.
##
## A schedule is an ordered list of "scheduled causes": the designer's thumb on the scale.
## HARD INVARIANT (ADR-0005 "author causes, never outcomes"): a cause may only touch sim
## INPUTS -- rival funding, rival aggression, an injected event id -- never the doom variable
## or any other outcome directly. The wave that reaches the player is whatever the sim does
## with the cause given opponent state and the player's ledger. This keeps every spike
## attributable (SA content for free), replay deterministic, and the meta rotatable by
## rotating schedules instead of nerfing numbers.
##
## Cause shape: {"turn": int, "cause": String, "target": String, "magnitude": float}
## Extensible seam: pdoom-data timeline entries become causes (content, not engine code).

# Recognised cause types. Add new INPUT-only handlers here; the invariant test guards that
# none of this file writes an outcome.
const CAUSE_TYPES := ["rival_funding_wave", "rival_aggression_shift", "inject_event"]


static func apply_due_causes(state) -> Array:
	## Apply every scheduled cause whose `turn` equals the current turn. Deterministic and
	## fired exactly once per turn (start_turn runs once per turn). Returns human-readable
	## summaries of what fired -- these are legible SA content, not side effects.
	var applied: Array = []
	for cause in state.event_schedule:
		if int(cause.get("turn", -1)) != state.turn:
			continue
		var summary: String = _apply_cause(state, cause)
		if summary != "":
			applied.append(summary)
	return applied


static func _apply_cause(state, cause: Dictionary) -> String:
	var kind: String = str(cause.get("cause", ""))
	var target: String = str(cause.get("target", ""))
	var magnitude: float = float(cause.get("magnitude", 0.0))
	match kind:
		"rival_funding_wave":
			# INPUT: rivals decide their number of actions from funding; more funding => more
			# capability/safety moves => an emergent doom wave next, produced by the sim.
			var rival = _find_rival(state, target)
			if rival != null:
				rival.funding += magnitude
				return "%s received a $%.0fk funding wave" % [rival.name, magnitude / 1000.0]
		"rival_aggression_shift":
			# INPUT: shifts a rival's capability-vs-safety bias.
			var rival = _find_rival(state, target)
			if rival != null:
				rival.aggression = clampf(rival.aggression + magnitude, 0.0, 1.0)
				return "%s shifted its research posture" % rival.name
		"inject_event":
			# INPUT: queue an event id for this turn's normal resolution. Any outcome the
			# event carries runs through the event pipeline (the sim), never here.
			state.pending_events.append({"id": target, "scheduled": true})
			return "Scheduled development: %s" % target
		_:
			push_warning("[SeedSchedule] Unknown cause type: %s" % kind)
	return ""


static func _find_rival(state, rival_id: String):
	for rival in state.rival_labs:
		if rival.id == rival_id or rival.name.to_lower().replace(" ", "_") == rival_id:
			return rival
	return null

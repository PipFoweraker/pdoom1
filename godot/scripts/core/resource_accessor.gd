extends RefCounted
class_name ResourceAccessor
## Shared GameState resource access by name (L9, #621).
##
## Replaces the triplicated resource-name match flagged on the duplication
## kill-list (TECH_DEBT_REGISTER): events.gd evaluate_condition +
## execute_event_choice, and event_service.gd _map_variable's fallback map.
## Behavior is a 1:1 transcription of those matches -- including the deliberate
## absence of clamping in add() (clamps happen downstream, e.g. check_win_lose).


static func has_readable(resource_name: String) -> bool:
	"""True if read() knows this resource (condition strings referencing unknown
	names evaluate false, matching the old match's default arm)."""
	return resource_name in [
		"money", "compute", "research", "papers", "reputation", "doom",
		"action_points", "safety_researchers", "capability_researchers",
		"compute_engineers", "managers", "researchers", "total_staff",
	]


static func read(state, resource_name: String) -> float:
	"""Read a scalar or derived resource value by name (0.0 for unknown names --
	gate with has_readable() where the distinction matters)."""
	match resource_name:
		"money":
			return state.money
		"compute":
			return state.compute
		"research":
			return state.research
		"papers":
			return state.papers
		"reputation":
			return state.reputation
		"doom":
			return state.doom
		"action_points":
			return float(state.action_points)
		"safety_researchers":
			return float(state.safety_researchers)
		"capability_researchers":
			return float(state.capability_researchers)
		"compute_engineers":
			return float(state.compute_engineers)
		"managers":
			return float(state.managers)
		"researchers":
			# Individual researcher count (new system)
			return float(state.researchers.size())
		"total_staff":
			# Total staff including managers
			return float(state.get_total_staff())
	return 0.0


static func add(state, resource_name: String, value) -> bool:
	"""Add a delta to a simple scalar resource. Returns false for names that are
	not simple scalars (researcher creation, has_cat, ...), so callers can handle
	those specially. Deliberately does NOT clamp -- identical to the pre-L9
	execute_event_choice writes."""
	match resource_name:
		"money":
			state.money += value
		"compute":
			state.compute += value
		"research":
			state.research += value
		"papers":
			state.papers += value
		"reputation":
			state.reputation += value
		"doom":
			# ADR-0015 REMAINDER (Legacy #15 / memo S7.1): event-content doom sink. Clobbered by
			# doom resolution in the real loop (inert no-op); the authority is DoomSystem's streams.
			# Follow-up content lane re-authors events to write intermediaries instead.
			state.doom += value
		"compute_engineers":
			# Compute engineers use legacy count only (no Researcher object)
			state.compute_engineers += value
		_:
			return false
	return true


static func map_external_name(pdoom_var: String) -> String:
	"""Map a pdoom-data variable name to a game resource name ("" = unmapped).
	Fallback used when data/events/balancing/variable_mapping.json lacks an entry
	(transcribed from event_service.gd _map_variable)."""
	match pdoom_var:
		"cash", "money", "funding":
			return "money"
		"stress", "burnout_risk", "vibey_doom":
			return "doom"
		"reputation", "public_opinion":
			return "reputation"
		"research", "papers":
			return "research"
		"compute":
			return "compute"
		_:
			return ""

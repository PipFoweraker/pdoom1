extends Node
class_name GameEvents
## Random and triggered events system

# WS-0 determinism: the event-firing registry (triggered_events / event_cooldowns) now lives
# as per-game INSTANCE state on GameState, threaded via `state`. As static class vars it
# persisted across in-process games and replays, desyncing state.rng consumption between
# otherwise-identical runs (candidate/rival divergence with matching score).

# #568 event pacing:
#   FIRST_EVENT_TURN — start_turn() increments state.turn BEFORE checking events, so turn 1 is
#     the player's very first (as-yet-unacted) turn. Suppress all event firing until this turn,
#     so the game doesn't open with a popup before the player has taken a single action.
#   MAX_NEW_EVENTS_PER_TURN — cap on how many *new* events fire in a single turn. Without it, a
#     turn where several probabilistic/threshold events happen to qualify dumps a "flood" of 6+
#     popups at once. Excess qualifying events are simply not marked this turn, so random ones
#     re-roll and turn/threshold beats re-evaluate on a later turn — the burst is spread out.
#   NOTE (design, parked): this does NOT change the event *pool size / density* (how often events
#     qualify in the first place) — that is a deliberate design call tracked in #578/#579.
const FIRST_EVENT_TURN := 2
const MAX_NEW_EVENTS_PER_TURN := 2

# L9 (#621): built-in event definitions live in data, not code. Loaded once and
# cached; array order in the file is trigger-check order (cap priority, #568).
const CORE_EVENTS_PATH := "res://data/events/core_events.json"
const RISK_EVENTS_PATH := "res://data/events/risk_events.json"

static var _core_events: Array[Dictionary] = []
static var _core_events_loaded := false
static var _risk_events: Dictionary = {}
static var _risk_events_loaded := false


static func get_all_events() -> Array[Dictionary]:
	"""Return all built-in event definitions (externalized to JSON — L9, #621)"""
	if not _core_events_loaded:
		_core_events_loaded = true
		_core_events = []
		var data := _load_definition_file(CORE_EVENTS_PATH)
		for event in data.get("events", []):
			if event is Dictionary:
				_core_events.append(_resolve_option_templates(event))
		if _core_events.is_empty():
			push_error("[GameEvents] No core events loaded from %s" % CORE_EVENTS_PATH)
	return _core_events


static func reload_definitions() -> void:
	"""Drop the definition caches so the next access re-reads the JSON (tests/tuning)."""
	_core_events_loaded = false
	_risk_events_loaded = false


static func _load_definition_file(path: String) -> Dictionary:
	"""Load + parse a definition JSON. Whole-number floats are normalized back to int
	(JSON parses all numbers as float; costs/effects must stay int so typed state
	fields like action_points accept them — behavior identical to the old literals)."""
	if not FileAccess.file_exists(path):
		push_error("[GameEvents] Definition file missing: %s" % path)
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("[GameEvents] Failed to open definition file: %s" % path)
		return {}
	var json := JSON.new()
	var err := json.parse(file.get_as_text())
	file.close()
	if err != OK:
		push_error("[GameEvents] Failed to parse %s: %s" % [path, json.get_error_message()])
		return {}
	var data = json.get_data()
	if not data is Dictionary:
		push_error("[GameEvents] %s is not a JSON object" % path)
		return {}
	return _intify(data)


static func _intify(value):
	"""Recursively convert whole-number floats to int (JSON round-trip normalization).
	Non-whole floats (e.g. probability 0.12) are preserved."""
	match typeof(value):
		TYPE_FLOAT:
			if value == floor(value):
				return int(value)
			return value
		TYPE_ARRAY:
			for i in range(value.size()):
				value[i] = _intify(value[i])
			return value
		TYPE_DICTIONARY:
			for key in value.keys():
				value[key] = _intify(value[key])
			return value
	return value


static func _resolve_option_templates(event: Dictionary) -> Dictionary:
	"""Resolve display placeholders in option text at load time. {cost_money} becomes
	GameConfig.format_money(option.costs.money), so a tuned cost auto-updates the label
	(replaces the inline format_money calls the old literals baked in)."""
	for option in event.get("options", []):
		if not option is Dictionary:
			continue
		var text: String = option.get("text", "")
		if text.contains("{cost_money}"):
			var money_cost = option.get("costs", {}).get("money", 0)
			option["text"] = text.replace("{cost_money}", GameConfig.format_money(float(money_cost)))
	return event


static func check_triggered_events(state: GameState, rng: RandomNumberGenerator) -> Array[Dictionary]:
	"""Check all events and return those that should trigger this turn.

	#568: no events fire before the player's first turn (FIRST_EVENT_TURN), and at most
	MAX_NEW_EVENTS_PER_TURN new events fire on any single turn. Qualifying events are
	collected WITHOUT being marked, then only the ones we actually fire get marked — so
	events squeezed out by the cap simply defer to a later turn instead of being lost.
	should_trigger() is still called for every candidate, so rng consumption (and thus
	determinism / replay) is unchanged relative to the pre-cap behaviour."""
	# Suppress event firing entirely until the player's first turn has begun.
	# Pacing values from Balance ("events.*", L9 #621); consts are the fallbacks.
	if state.turn < Balance.inum("events.first_event_turn", FIRST_EVENT_TURN):
		return []

	# Two buckets so scripted beats (turn_exact / turn_and_resource / threshold) are never
	# crowded out of the cap by a swarm of "random" events — scripted fire first.
	var scripted: Array[Dictionary] = []
	var random_pool: Array[Dictionary] = []

	# Check built-in events
	for event in get_all_events():
		if should_trigger(event, state, rng):
			_bucket_candidate(event, scripted, random_pool)

	# Check scenario-specific events (Issue #483: Mod/Scenario hook)
	if state.has_meta("scenario_events"):
		var scenario_events = state.get_meta("scenario_events")
		for event in scenario_events:
			if should_trigger(event, state, rng):
				_bucket_candidate(event, scripted, random_pool)

	# Check historical events from EventService (Issue #442: API Event Fetching)
	# Historical events are real AI safety timeline events transformed into game events
	# Only trigger events that occur on or after the game's configured start date
	if EventService and EventService.is_ready():
		var historical_events = EventService.get_historical_events()
		for event in historical_events:
			# Skip events from before the game start date
			var event_year = event.get("year", 0)
			if event_year < state.start_year:
				continue
			if should_trigger(event, state, rng):
				_bucket_candidate(event, scripted, random_pool)

	# Fire scripted beats first, then random ones, up to the per-turn cap. Only fired
	# events are marked; the rest defer (random → re-roll, threshold/turn → re-evaluate).
	var to_trigger: Array[Dictionary] = []
	var max_new_events := Balance.inum("events.max_new_events_per_turn", MAX_NEW_EVENTS_PER_TURN)
	for event in scripted:
		if to_trigger.size() >= max_new_events:
			break
		to_trigger.append(event)
		_mark_event_triggered(event, state.turn, state)
	for event in random_pool:
		if to_trigger.size() >= max_new_events:
			break
		to_trigger.append(event)
		_mark_event_triggered(event, state.turn, state)

	return to_trigger

static func _bucket_candidate(event: Dictionary, scripted: Array[Dictionary], random_pool: Array[Dictionary]) -> void:
	"""Route a qualifying event into the scripted or random bucket for cap prioritisation (#568)."""
	if event.get("trigger_type", "") == "random":
		random_pool.append(event)
	else:
		scripted.append(event)

static func should_trigger(event: Dictionary, state: GameState, rng: RandomNumberGenerator) -> bool:
	"""Check if event should trigger"""
	var event_id = event.get("id", "")

	# Don't trigger if already triggered (unless repeatable)
	if event_id in state.triggered_events and not event.get("repeatable", false):
		return false

	# Check cooldown for repeatable events (cooldown_turns = minimum turns between triggers)
	var cooldown_turns = event.get("cooldown_turns", 0)
	if cooldown_turns > 0 and state.event_cooldowns.has(event_id):
		var last_triggered = state.event_cooldowns[event_id]
		if state.turn - last_triggered < cooldown_turns:
			return false

	var trigger_type = event.get("trigger_type", "")

	match trigger_type:
		"turn_exact":
			# Exact turn trigger (e.g., cat on turn 7)
			return state.turn == event.get("trigger_turn", -1)

		"turn_and_resource":
			# Specific turn + condition
			if state.turn != event.get("trigger_turn", -1):
				return false
			return evaluate_condition(event.get("trigger_condition", "false"), state)

		"threshold":
			# Resource threshold condition
			return evaluate_condition(event.get("trigger_condition", "false"), state)

		"random":
			# Random chance after min turn
			if state.turn < event.get("min_turn", 0):
				return false
			# Checks trigger condition if available
			var cond = event.get("trigger_condition", "")
			if cond != "" and not evaluate_condition(cond, state):
				return false
			# Check extra_condition if present (e.g., salary_disparity checks)
			var extra_cond = event.get("extra_condition", "")
			if extra_cond != "" and not evaluate_condition(extra_cond, state):
				return false
			var event_roll = rng.randf()

			# Record RNG outcome for verification
			VerificationTracker.record_rng_outcome("event_%s" % event_id, event_roll, state.turn)

			return event_roll < event.get("probability", 0.1)

	return false

static func evaluate_condition(condition: String, state: GameState) -> bool:
	"""Evaluate condition string safely"""
	# Simple parser for conditions like "money < 50000"
	# Format: "resource operator value"
	#
	# Special conditions:
	# - "salary_disparity > X" - true if salary coefficient of variation > X%
	#   (e.g., "salary_disparity > 20" means >20% salary spread)

	if condition == "false":
		return false
	if condition == "true":
		return true

	var parts = condition.split(" ")
	if parts.size() < 3:
		return false

	var resource_name = parts[0]
	var operator = parts[1]
	var value_str = parts[2]

	# Special condition: salary_disparity (coefficient of variation as percentage)
	if resource_name == "salary_disparity":
		var disparity = _calculate_salary_disparity(state)
		var threshold = float(value_str)
		match operator:
			">":
				return disparity > threshold
			">=":
				return disparity >= threshold
			"<":
				return disparity < threshold
			"<=":
				return disparity <= threshold
		return false

	# Get resource value from state
	var resource_value = 0.0
	match resource_name:
		"money":
			resource_value = state.money
		"compute":
			resource_value = state.compute
		"research":
			resource_value = state.research
		"papers":
			resource_value = state.papers
		"reputation":
			resource_value = state.reputation
		"doom":
			resource_value = state.doom
		"action_points":
			resource_value = state.action_points
		"safety_researchers":
			resource_value = state.safety_researchers
		"capability_researchers":
			resource_value = state.capability_researchers
		"compute_engineers":
			resource_value = state.compute_engineers
		"managers":
			resource_value = state.managers
		"researchers":
			# Individual researcher count (new system)
			resource_value = state.researchers.size()
		"total_staff":
			# Total staff including managers
			resource_value = state.get_total_staff()
		_:
			return false

	var threshold = float(value_str)

	# Evaluate operator
	match operator:
		"<":
			return resource_value < threshold
		">":
			return resource_value > threshold
		"<=":
			return resource_value <= threshold
		">=":
			return resource_value >= threshold
		"==":
			return abs(resource_value - threshold) < 0.01
		"!=":
			return abs(resource_value - threshold) >= 0.01

	return false

static func execute_event_choice(event: Dictionary, choice_id: String, state: GameState) -> Dictionary:
	"""Execute player's event choice and return result"""
	var options = event.get("options", [])

	# Find chosen option
	var chosen_option: Dictionary = {}
	for opt in options:
		if opt.get("id", "") == choice_id:
			chosen_option = opt
			break

	if chosen_option.is_empty():
		return {"success": false, "message": "Unknown choice"}

	# Check costs
	var costs = chosen_option.get("costs", {})
	if not state.can_afford(costs):
		return {"success": false, "message": "Cannot afford this choice"}

	# Pay costs
	state.spend_resources(costs)

	# Apply effects
	var effects = chosen_option.get("effects", {})
	for key in effects.keys():
		var value = effects[key]

		# Map effect keys to state properties
		match key:
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
				state.doom += value
			"safety_researchers":
				# Create actual Researcher objects for the new system
				for i in range(value):
					var researcher = Researcher.new()
					researcher.generate_random(state.rng)
					researcher.specialization = "safety"
					state.add_researcher(researcher)
			"capability_researchers":
				for i in range(value):
					var researcher = Researcher.new()
					researcher.generate_random(state.rng)
					researcher.specialization = "capabilities"
					state.add_researcher(researcher)
			"compute_engineers":
				# Compute engineers use legacy count only (no Researcher object)
				state.compute_engineers += value
			"has_cat":
				state.has_cat = (value > 0)
			"lose_researcher":
				# Remove a random researcher (poaching)
				if state.researchers.size() > 0:
					var idx = state.rng.randi() % state.researchers.size()

					# Record RNG outcome for verification
					VerificationTracker.record_rng_outcome("poach_researcher_select", float(idx), state.turn)

					var researcher = state.researchers[idx]
					state.remove_researcher(researcher)

	var message = chosen_option.get("message", "Event resolved")
	return {"success": true, "message": message}

static func _mark_event_triggered(event: Dictionary, turn: int, state: GameState):
	"""Mark an event as triggered, handling both one-time and cooldown tracking"""
	var event_id = event.get("id", "")
	if not event.get("repeatable", false):
		state.triggered_events.append(event_id)
	# Always record cooldown for repeatable events with cooldown_turns
	if event.get("cooldown_turns", 0) > 0:
		state.event_cooldowns[event_id] = turn

static func _calculate_salary_disparity(state: GameState) -> float:
	"""Calculate salary disparity as coefficient of variation (percentage).

	Returns 0 if fewer than 2 researchers.
	A value of 20 means salaries vary by ~20% from the mean.
	Higher values indicate more pay inequality.
	"""
	if state.researchers.size() < 2:
		return 0.0

	# Collect all salaries
	var salaries: Array[float] = []
	for researcher in state.researchers:
		salaries.append(researcher.current_salary)

	# Calculate mean
	var total = 0.0
	for salary in salaries:
		total += salary
	var mean = total / salaries.size()

	if mean <= 0:
		return 0.0

	# Calculate standard deviation
	var variance_sum = 0.0
	for salary in salaries:
		variance_sum += pow(salary - mean, 2)
	var std_dev = sqrt(variance_sum / salaries.size())

	# Coefficient of variation as percentage
	return (std_dev / mean) * 100.0


# ============================================================================
# RISK-TRIGGERED EVENTS
# See godot/docs/design/RISK_SYSTEM.md for design documentation
# ============================================================================

static func get_risk_events() -> Dictionary:
	"""Return all risk event definitions, organized by pool and severity
	(externalized to JSON - L9, #621). Format: {pool_name: {severity: [events]}}"""
	if not _risk_events_loaded:
		_risk_events_loaded = true
		var data := _load_definition_file(RISK_EVENTS_PATH)
		_risk_events = data.get("pools", {})
		if _risk_events.is_empty():
			push_error("[GameEvents] No risk events loaded from %s" % RISK_EVENTS_PATH)
	return _risk_events


static func get_risk_event_for_pool(pool_name: String, severity: String, rng: RandomNumberGenerator) -> Dictionary:
	"""Get a random risk event for a pool at a given severity level.
	Returns empty dict if no matching events found."""
	var all_risk_events = get_risk_events()

	if not all_risk_events.has(pool_name):
		return {}

	var pool_events = all_risk_events[pool_name]
	if not pool_events.has(severity):
		return {}

	var severity_events = pool_events[severity]
	if severity_events.is_empty():
		return {}

	# Pick random event from available options
	var idx = rng.randi() % severity_events.size()
	return severity_events[idx]

# WS-0: reset_triggered_events() removed — the registry is now per-GameState instance state,
# so it resets automatically with each new GameState. No global reset is needed.

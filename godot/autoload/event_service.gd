extends Node
## EventService - Fetches and caches historical events from external sources
##
## This service handles:
## 1. Fetching historical AI safety timeline data from pdoom-data API or local cache
## 2. Transforming raw historical data into game-playable events
## 3. Applying game-balance overrides from local config files
## 4. Caching events locally for offline play
## 5. Providing events to GameEvents system
##
## Data Flow:
##   pdoom-data -> Fetch -> Apply Overrides -> Transform -> Cache -> GameEvents
##
## Key Principle:
##   pdoom-data owns facts and defaults; pdoom1 owns balance tuning via overrides
##
## The historical data contains real AI safety milestones (papers, org founding,
## policy events, etc.) which get transformed into game events with costs,
## effects, and player choices.

# Configuration
const API_BASE_URL = "https://api.pdoom.org/v1"  # Future API endpoint
const FALLBACK_DATA_PATH = "res://data/historical_events.json"  # Bundled pdoom-data export
const CACHE_PATH = "user://event_cache.json"
const CACHE_EXPIRY_HOURS = 24  # Re-fetch after this many hours

# Config file paths
const VARIABLE_MAPPING_PATH = "res://data/events/balancing/variable_mapping.json"
const RARITY_CURVES_PATH = "res://data/events/balancing/rarity_curves.json"
const OVERRIDES_DIR_PATH = "res://data/events/overrides/"

# Signals
signal events_loaded(event_count: int)
signal events_fetch_failed(error: String)
signal events_transformed(event_count: int)

# State
var cached_events: Array[Dictionary] = []
var transformed_events: Array[Dictionary] = []
var is_loading: bool = false
var last_fetch_time: float = 0.0
var http_request: HTTPRequest = null

# Config data (loaded from JSON files)
var _variable_mapping: Dictionary = {}
var _scale_factors: Dictionary = {}
var _rarity_curves: Dictionary = {}
var _overrides: Dictionary = {}
var _default_effects: Dictionary = {}


func _ready():
	# Create HTTP request node for API calls
	http_request = HTTPRequest.new()
	http_request.timeout = 30.0  # 30 second timeout
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

	# Load config files first
	_load_variable_mapping()
	_load_rarity_curves()
	_load_overrides()

	# Load cached events on startup
	_load_from_cache()

	print("[EventService] Initialized with %d cached events, %d overrides loaded" % [cached_events.size(), _overrides.size()])


## Public API

func get_historical_events() -> Array[Dictionary]:
	"""Get all transformed historical events ready for game use"""
	return transformed_events


func get_events_for_year(year: int) -> Array[Dictionary]:
	"""Get events that should trigger in a specific year"""
	var year_events: Array[Dictionary] = []
	for event in transformed_events:
		var event_year = event.get("year", 0)
		if event_year == year:
			year_events.append(event)
	return year_events


func get_events_by_category(category: String) -> Array[Dictionary]:
	"""Get events filtered by category (research, policy, organization, etc.)"""
	var filtered: Array[Dictionary] = []
	for event in transformed_events:
		if event.get("category", "") == category:
			filtered.append(event)
	return filtered


func refresh_events(force: bool = false) -> void:
	"""Refresh events from API or cache"""
	if is_loading:
		push_warning("[EventService] Already loading events")
		return

	# Check if cache is still valid
	if not force and _is_cache_valid():
		print("[EventService] Using valid cache, skipping refresh")
		events_loaded.emit(transformed_events.size())
		return

	is_loading = true

	# Try API first, fall back to bundled data
	_fetch_from_api()


func get_event_count() -> int:
	"""Get total number of available historical events"""
	return transformed_events.size()


func is_ready() -> bool:
	"""Check if events are loaded and ready"""
	return transformed_events.size() > 0 and not is_loading


## Internal Methods

func _load_from_cache() -> bool:
	"""Load events from local cache file"""
	if not FileAccess.file_exists(CACHE_PATH):
		print("[EventService] No cache file found, loading bundled data")
		return _load_bundled_data()

	var file = FileAccess.open(CACHE_PATH, FileAccess.READ)
	if file == null:
		push_error("[EventService] Failed to open cache file")
		return _load_bundled_data()

	var json_text = file.get_as_text()
	file.close()

	var json = JSON.new()
	var error = json.parse(json_text)
	if error != OK:
		push_error("[EventService] Failed to parse cache JSON: %s" % json.get_error_message())
		return _load_bundled_data()

	var data = json.get_data()
	if not data is Dictionary:
		push_error("[EventService] Cache data is not a dictionary")
		return _load_bundled_data()

	cached_events.clear()
	var events_array = data.get("events", [])
	for event in events_array:
		cached_events.append(event)

	last_fetch_time = data.get("fetch_time", 0.0)

	# Transform cached events
	_transform_all_events()

	print("[EventService] Loaded %d events from cache" % cached_events.size())
	return true


func _load_bundled_data() -> bool:
	"""Load bundled fallback data shipped with the game (pdoom-data export)"""
	if not FileAccess.file_exists(FALLBACK_DATA_PATH):
		print("[EventService] No bundled data found at %s" % FALLBACK_DATA_PATH)
		return false

	var file = FileAccess.open(FALLBACK_DATA_PATH, FileAccess.READ)
	if file == null:
		push_error("[EventService] Failed to open bundled data file")
		return false

	var json_text = file.get_as_text()
	file.close()

	var json = JSON.new()
	var error = json.parse(json_text)
	if error != OK:
		push_error("[EventService] Failed to parse bundled JSON: %s" % json.get_error_message())
		return false

	var data = json.get_data()
	cached_events.clear()

	# Handle multiple data formats:
	# 1. pdoom-data format: Dictionary with event IDs as keys
	# 2. Legacy array format: Array of event objects
	# 3. Legacy wrapper format: {"events": [...]}
	if data is Dictionary:
		# Check if it's a wrapper with "events" key (legacy format)
		if data.has("events") and data["events"] is Array:
			for event in data["events"]:
				cached_events.append(event)
		else:
			# pdoom-data format: Dictionary with event IDs as keys
			for event_id in data.keys():
				if event_id.begins_with("_"):
					continue  # Skip metadata keys like "_description"
				var event = data[event_id]
				if event is Dictionary:
					# Ensure the event has its ID set
					if not event.has("id"):
						event["id"] = event_id
					cached_events.append(event)
	elif data is Array:
		for event in data:
			cached_events.append(event)

	# Transform loaded events
	_transform_all_events()

	print("[EventService] Loaded %d events from bundled data" % cached_events.size())
	return true


func _save_to_cache() -> void:
	"""Save current events to cache file"""
	var cache_data = {
		"fetch_time": Time.get_unix_time_from_system(),
		"version": "1.0",
		"events": cached_events
	}

	var file = FileAccess.open(CACHE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("[EventService] Failed to open cache file for writing")
		return

	file.store_string(JSON.stringify(cache_data, "\t"))
	file.close()
	print("[EventService] Saved %d events to cache" % cached_events.size())


func _is_cache_valid() -> bool:
	"""Check if cache is still valid (not expired)"""
	if cached_events.is_empty():
		return false

	var current_time = Time.get_unix_time_from_system()
	var expiry_seconds = CACHE_EXPIRY_HOURS * 3600
	return (current_time - last_fetch_time) < expiry_seconds


func _fetch_from_api() -> void:
	"""Fetch events from external API"""
	var url = "%s/events/timeline" % API_BASE_URL

	print("[EventService] Fetching events from %s" % url)

	var error = http_request.request(url)
	if error != OK:
		push_error("[EventService] HTTP request failed with error: %d" % error)
		_handle_fetch_failure("HTTP request failed")


func _on_request_completed(result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	"""Handle HTTP response"""
	is_loading = false

	if result != HTTPRequest.RESULT_SUCCESS:
		_handle_fetch_failure("Request failed with result: %d" % result)
		return

	if response_code != 200:
		_handle_fetch_failure("API returned status: %d" % response_code)
		return

	var json_text = body.get_string_from_utf8()
	var json = JSON.new()
	var error = json.parse(json_text)

	if error != OK:
		_handle_fetch_failure("Failed to parse API response: %s" % json.get_error_message())
		return

	var data = json.get_data()

	# Clear and reload events
	cached_events.clear()

	if data is Array:
		for event in data:
			cached_events.append(event)
	elif data is Dictionary and data.has("events"):
		for event in data["events"]:
			cached_events.append(event)
	else:
		_handle_fetch_failure("Unexpected API response format")
		return

	last_fetch_time = Time.get_unix_time_from_system()

	# Save to cache
	_save_to_cache()

	# Transform events
	_transform_all_events()

	print("[EventService] Fetched and cached %d events from API" % cached_events.size())
	events_loaded.emit(cached_events.size())


func _handle_fetch_failure(error_message: String) -> void:
	"""Handle API fetch failure by falling back to cache/bundled data"""
	push_warning("[EventService] API fetch failed: %s" % error_message)

	# Try loading from cache or bundled data
	if cached_events.is_empty():
		if _load_bundled_data():
			events_loaded.emit(transformed_events.size())
		else:
			events_fetch_failed.emit(error_message)
	else:
		# Use existing cached data
		print("[EventService] Using existing cached data after fetch failure")
		events_loaded.emit(transformed_events.size())


## Event Transformation

func _transform_all_events() -> void:
	"""Transform all cached historical events into game-ready events"""
	transformed_events.clear()

	for raw_event in cached_events:
		# Apply overrides before transformation
		var event_with_overrides = _apply_overrides(raw_event)
		var game_event = _transform_event(event_with_overrides)
		if game_event != null and not game_event.is_empty():
			transformed_events.append(game_event)

	events_transformed.emit(transformed_events.size())
	print("[EventService] Transformed %d events" % transformed_events.size())


func _transform_event(raw: Dictionary) -> Dictionary:
	"""
	Transform a raw historical event into a game-playable event.

	pdoom-data format (new):
	{
		"id": "ftx_future_fund_collapse_2022",
		"title": "FTX Future Fund Collapse",
		"year": 2022,
		"category": "funding_catastrophe",
		"description": "...",
		"impacts": [{"variable": "cash", "change": -80}, ...],
		"rarity": "rare",
		"safety_researcher_reaction": "Devastating blow...",
		"media_reaction": "Crypto collapse..."
	}

	Trigger modes by rarity:
	- legendary: deterministic - always fires at exact turn (major narrative beats)
	- rare: probabilistic_window - eligible around historical date, rolls each turn
	- common: random_after_eligible - random chance after min_turn

	Game event format (output):
	{
		"id": "hist_miri_founded",
		"name": "MIRI Founded",
		"type": "popup",
		"trigger_type": "turn_exact" | "random",
		"trigger_turn": <calculated from year>,
		"eligibility_start": <first turn event can fire>,
		"eligibility_end": <last turn for window>,
		...
	}
	"""
	if not raw.has("id") or not raw.has("title"):
		return {}

	var event_id = "hist_%s" % raw["id"]
	var category = raw.get("category", "general")
	var rarity = raw.get("rarity", "common")

	# Get year from either "year" field (pdoom-data) or "date" field (legacy)
	var year: int
	if raw.has("year"):
		year = int(raw["year"])
	else:
		year = _extract_year(raw.get("date", "2017-01-01"))

	# Get rarity curve settings
	var rarity_settings = _get_rarity_settings(rarity)
	var trigger_mode = rarity_settings.get("trigger_mode", "random_after_eligible")

	# Calculate trigger turn based on year (52 turns per year)
	var year_config = _rarity_curves.get("year_trigger", {})
	var base_year = year_config.get("base_year", 2017)
	var turns_per_year = year_config.get("turns_per_year", 52)

	# Years before game start get clamped to turn 1
	var years_from_start = year - base_year
	var base_turn = max(1, years_from_start * turns_per_year + 1)

	# Calculate trigger timing based on rarity
	var trigger_turn: int
	var trigger_type: String
	var eligibility_start: int
	var eligibility_end: int

	match trigger_mode:
		"deterministic":
			# Legendary: fires at exact turn (mid-year for year-only events)
			var month_offset = year_config.get("legendary_month_offset", 26)
			trigger_turn = base_turn + month_offset
			trigger_type = "turn_exact"
			eligibility_start = trigger_turn
			eligibility_end = trigger_turn

		"probabilistic_window":
			# Rare: eligible within a window around the historical date
			var spread = year_config.get("rare_spread_turns", 13)
			var window = rarity_settings.get("eligibility_window_turns", 26)
			trigger_turn = base_turn + spread  # Center of eligibility
			eligibility_start = max(1, trigger_turn - window / 2)
			eligibility_end = trigger_turn + window / 2
			trigger_type = "random"

		_:  # "random_after_eligible" (common)
			# Common: can fire anytime after becoming eligible
			trigger_turn = max(rarity_settings.get("min_turn", 10), base_turn)
			eligibility_start = trigger_turn
			eligibility_end = 9999  # No end
			trigger_type = "random"

	# Calculate significance from impacts or use legacy field
	var significance = raw.get("significance", _calculate_significance(raw))

	# Generate options based on event category and impacts
	var options = _generate_options(raw, category, significance)

	# Build the game event
	var game_event: Dictionary = {
		"id": event_id,
		"name": raw.get("title", "Historical Event"),
		"description": raw.get("description", "A significant event in AI safety history."),
		"type": "popup",
		"trigger_type": trigger_type,
		"trigger_turn": trigger_turn,
		"eligibility_start": eligibility_start,
		"eligibility_end": eligibility_end,
		"year": year,
		"category": category,
		"rarity": rarity,
		"trigger_mode": trigger_mode,
		"significance": significance,
		"repeatable": false,
		"historical": true,
		"source_data": raw,
		"options": options,
		# Rarity-based trigger settings
		"probability": rarity_settings.get("base_probability", 0.1),
		"min_turn": eligibility_start,
		"cooldown_turns": rarity_settings.get("cooldown_turns", 20)
	}

	# Add reactions if present (for UI display)
	if raw.has("safety_researcher_reaction"):
		game_event["safety_researcher_reaction"] = raw["safety_researcher_reaction"]
	if raw.has("media_reaction"):
		game_event["media_reaction"] = raw["media_reaction"]

	# Add pdoom_impact if present
	if raw.has("pdoom_impact") and raw["pdoom_impact"] != null:
		game_event["pdoom_impact"] = raw["pdoom_impact"]

	return game_event


func _calculate_significance(raw: Dictionary) -> int:
	"""Calculate significance score from impacts array"""
	if not raw.has("impacts") or not raw["impacts"] is Array:
		return 5  # Default significance

	var total_impact = 0
	for impact in raw["impacts"]:
		if impact is Dictionary and impact.has("change"):
			total_impact += abs(int(impact["change"]))

	# Map total impact to 1-10 scale
	if total_impact >= 100:
		return 10
	elif total_impact >= 75:
		return 9
	elif total_impact >= 50:
		return 8
	elif total_impact >= 35:
		return 7
	elif total_impact >= 25:
		return 6
	elif total_impact >= 15:
		return 5
	elif total_impact >= 10:
		return 4
	elif total_impact >= 5:
		return 3
	else:
		return 2


func _get_rarity_settings(rarity: String) -> Dictionary:
	"""Get trigger settings for a rarity tier"""
	if _rarity_curves.has(rarity):
		return _rarity_curves[rarity]

	# Fallback defaults with trigger modes
	match rarity:
		"legendary":
			return {
				"base_probability": 1.0,
				"min_turn": 1,
				"cooldown_turns": 0,
				"trigger_mode": "deterministic"
			}
		"rare":
			return {
				"base_probability": 0.06,
				"min_turn": 20,
				"cooldown_turns": 15,
				"eligibility_window_turns": 26,
				"trigger_mode": "probabilistic_window"
			}
		_:  # common or unknown
			return {
				"base_probability": 0.12,
				"min_turn": 10,
				"cooldown_turns": 8,
				"trigger_mode": "random_after_eligible"
			}


func _extract_year(date_string: String) -> int:
	"""Extract year from date string (YYYY-MM-DD format)"""
	if date_string.length() >= 4:
		return date_string.substr(0, 4).to_int()
	return 2017


func _generate_options(raw: Dictionary, category: String, significance: int) -> Array:
	"""
	Generate player choice options based on event category, significance, and impacts.

	Uses pdoom-data impacts array to create meaningful effects, then generates
	options based on category templates.

	Options vary by category:
	- organization, organization_founding: Partner, compete, ignore
	- research, paper, technical_research_breakthrough: Adopt, critique, build upon
	- policy, regulation, policy_event: Support, oppose, lobby
	- incident, capability, capability_advance: Respond, ignore, capitalize
	- funding_catastrophe: Emergency response options
	"""
	var options: Array = []

	# Calculate base effects from impacts array or significance
	var base_effects = _calculate_base_effects(raw, significance)
	var effect_multiplier = significance / 5.0
	var rep_effect = int(5 * effect_multiplier)
	var doom_effect = int(3 * effect_multiplier)
	var money_effect = int(10000 * effect_multiplier)

	# Get reactions for flavor text
	var safety_reaction = raw.get("safety_researcher_reaction", "")
	var media_reaction = raw.get("media_reaction", "")

	# Normalize category for matching
	var cat_lower = category.to_lower()

	if cat_lower in ["organization", "organization_founding"]:
		options = [
			{
				"id": "collaborate",
				"text": "Seek collaboration",
				"costs": {"action_points": 1},
				"effects": {"reputation": rep_effect, "doom": -doom_effect},
				"message": "Established collaborative relationship." + (_format_reaction(safety_reaction))
			},
			{
				"id": "compete",
				"text": "Position as competitor",
				"costs": {},
				"effects": {"reputation": -rep_effect / 2, "research": rep_effect * 2},
				"message": "Competitive positioning may accelerate progress."
			},
			{
				"id": "observe",
				"text": "Monitor developments",
				"costs": {},
				"effects": {},
				"message": "Taking a wait-and-see approach."
			}
		]

	elif cat_lower in ["research", "paper", "technical_research_breakthrough", "alignment_research"]:
		options = [
			{
				"id": "build_upon",
				"text": "Build upon this research",
				"costs": {"action_points": 1, "money": money_effect},
				"effects": {"research": rep_effect * 3, "doom": doom_effect / 2},
				"message": "Advancing the research frontier." + (_format_reaction(safety_reaction))
			},
			{
				"id": "safety_analysis",
				"text": "Conduct safety analysis",
				"costs": {"action_points": 1},
				"effects": {"research": rep_effect, "doom": -doom_effect, "reputation": rep_effect / 2},
				"message": "Published safety analysis of the work."
			},
			{
				"id": "acknowledge",
				"text": "Acknowledge and continue",
				"costs": {},
				"effects": {"research": rep_effect / 2},
				"message": "Noted for future reference."
			}
		]

	elif cat_lower in ["policy", "regulation", "policy_event"]:
		options = [
			{
				"id": "support",
				"text": "Publicly support",
				"costs": {"action_points": 1},
				"effects": {"reputation": rep_effect, "doom": -doom_effect},
				"message": "Your support strengthens the policy effort." + (_format_reaction(media_reaction))
			},
			{
				"id": "critique",
				"text": "Offer constructive critique",
				"costs": {"action_points": 1},
				"effects": {"reputation": rep_effect / 2, "research": rep_effect},
				"message": "Your expertise shapes the discussion."
			},
			{
				"id": "stay_neutral",
				"text": "Remain neutral",
				"costs": {},
				"effects": {},
				"message": "Maintaining political neutrality."
			}
		]

	elif cat_lower in ["incident", "capability", "capability_advance"]:
		options = [
			{
				"id": "respond_publicly",
				"text": "Issue public response",
				"costs": {"action_points": 1},
				"effects": {"reputation": rep_effect, "doom": -doom_effect / 2},
				"message": "Your response shapes public understanding." + (_format_reaction(media_reaction))
			},
			{
				"id": "internal_review",
				"text": "Conduct internal review",
				"costs": {"action_points": 1},
				"effects": {"research": rep_effect, "doom": -doom_effect},
				"message": "Lessons learned improve your safety practices."
			},
			{
				"id": "note_concerns",
				"text": "Note concerns privately",
				"costs": {},
				"effects": {"research": rep_effect / 2},
				"message": "Added to internal risk assessment."
			}
		]

	elif cat_lower in ["funding_catastrophe", "funding"]:
		# Special handling for funding disasters like FTX collapse
		var money_impact = base_effects.get("money", -money_effect)
		options = [
			{
				"id": "emergency_fundraise",
				"text": "Emergency Fundraising",
				"costs": {"action_points": 2},
				"effects": {"money": abs(money_impact) / 2, "reputation": -rep_effect / 2},
				"message": "Launched emergency fundraising campaign." + (_format_reaction(safety_reaction))
			},
			{
				"id": "diversify_funding",
				"text": "Diversify Funding Sources",
				"costs": {"action_points": 1},
				"effects": {"doom": -doom_effect / 2, "reputation": rep_effect / 2},
				"message": "Reduced dependency on any single funder."
			},
			{
				"id": "accept_losses",
				"text": "Accept and Adapt",
				"costs": {},
				"effects": _apply_scaled_effects(base_effects, 0.5),
				"message": "Accepting the impact and adapting operations."
			}
		]

	else:
		# Default options for other categories
		options = [
			{
				"id": "engage",
				"text": "Engage with this development",
				"costs": {"action_points": 1},
				"effects": {"reputation": rep_effect, "research": rep_effect / 2},
				"message": "Engaging with the broader AI safety community."
			},
			{
				"id": "acknowledge",
				"text": "Acknowledge and continue",
				"costs": {},
				"effects": {},
				"message": "Noted for future reference."
			}
		]

	return options


func _calculate_base_effects(raw: Dictionary, significance: int) -> Dictionary:
	"""Convert pdoom-data impacts array to game effects dictionary"""
	var effects: Dictionary = {}

	if not raw.has("impacts") or not raw["impacts"] is Array:
		# No impacts array - use default effects based on rarity
		var rarity = raw.get("rarity", "common")
		return _default_effects.get(rarity, {})

	for impact in raw["impacts"]:
		if not impact is Dictionary:
			continue
		if not impact.has("variable") or not impact.has("change"):
			continue

		var pdoom_var = impact["variable"]
		var change = int(impact["change"])

		# Map pdoom-data variable to game variable
		var game_var = _map_variable(pdoom_var)
		if game_var.is_empty():
			continue

		# Apply scale factor
		var scale = _scale_factors.get(game_var, 1)
		var scaled_change = change * scale

		# Accumulate effects (some pdoom-data vars map to same game var)
		if effects.has(game_var):
			effects[game_var] += scaled_change
		else:
			effects[game_var] = scaled_change

	return effects


func _map_variable(pdoom_var: String) -> String:
	"""Map a pdoom-data variable name to a game state variable"""
	if _variable_mapping.has(pdoom_var):
		return _variable_mapping[pdoom_var]

	# Fallback mapping
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


func _apply_scaled_effects(effects: Dictionary, scale: float) -> Dictionary:
	"""Apply a scale factor to all effects"""
	var scaled: Dictionary = {}
	for key in effects:
		scaled[key] = int(effects[key] * scale)
	return scaled


func _format_reaction(reaction: String) -> String:
	"""Format a reaction string for inclusion in message"""
	if reaction.is_empty():
		return ""
	return " \"%s\"" % reaction


## Utility Methods

func clear_cache() -> void:
	"""Clear the local cache file"""
	if FileAccess.file_exists(CACHE_PATH):
		DirAccess.remove_absolute(CACHE_PATH)
	cached_events.clear()
	transformed_events.clear()
	last_fetch_time = 0.0
	print("[EventService] Cache cleared")


func get_cache_info() -> Dictionary:
	"""Get information about the current cache state"""
	return {
		"cached_count": cached_events.size(),
		"transformed_count": transformed_events.size(),
		"last_fetch_time": last_fetch_time,
		"cache_valid": _is_cache_valid(),
		"is_loading": is_loading,
		"overrides_count": _overrides.size()
	}


## Config Loading Methods

func _load_variable_mapping() -> void:
	"""Load variable mapping from balancing config"""
	if not FileAccess.file_exists(VARIABLE_MAPPING_PATH):
		print("[EventService] No variable mapping found, using defaults")
		_set_default_variable_mapping()
		return

	var file = FileAccess.open(VARIABLE_MAPPING_PATH, FileAccess.READ)
	if file == null:
		push_warning("[EventService] Failed to open variable mapping file")
		_set_default_variable_mapping()
		return

	var json = JSON.new()
	var error = json.parse(file.get_as_text())
	file.close()

	if error != OK:
		push_warning("[EventService] Failed to parse variable mapping: %s" % json.get_error_message())
		_set_default_variable_mapping()
		return

	var data = json.get_data()
	if not data is Dictionary:
		push_warning("[EventService] Variable mapping is not a dictionary")
		_set_default_variable_mapping()
		return

	# Extract mapping and scale factors
	_variable_mapping = data.get("mapping", {})
	_scale_factors = data.get("scale_factors", {})
	_default_effects = data.get("default_effects", {})

	print("[EventService] Loaded variable mapping with %d entries" % _variable_mapping.size())


func _set_default_variable_mapping() -> void:
	"""Set default variable mapping when config not found"""
	_variable_mapping = {
		"cash": "money",
		"money": "money",
		"stress": "doom",
		"vibey_doom": "doom",
		"doom": "doom",
		"reputation": "reputation",
		"research": "research",
		"papers": "papers",
		"burnout_risk": "doom",
		"compute": "compute"
	}
	_scale_factors = {
		"money": 1000,
		"doom": 1,
		"reputation": 1,
		"research": 2,
		"papers": 1,
		"compute": 10
	}
	_default_effects = {
		"common": {"research": 5},
		"rare": {"research": 10, "reputation": 5},
		"legendary": {"research": 20, "reputation": 10, "doom": 5}
	}


func _load_rarity_curves() -> void:
	"""Load rarity curve settings from balancing config"""
	if not FileAccess.file_exists(RARITY_CURVES_PATH):
		print("[EventService] No rarity curves found, using defaults")
		_set_default_rarity_curves()
		return

	var file = FileAccess.open(RARITY_CURVES_PATH, FileAccess.READ)
	if file == null:
		push_warning("[EventService] Failed to open rarity curves file")
		_set_default_rarity_curves()
		return

	var json = JSON.new()
	var error = json.parse(file.get_as_text())
	file.close()

	if error != OK:
		push_warning("[EventService] Failed to parse rarity curves: %s" % json.get_error_message())
		_set_default_rarity_curves()
		return

	var data = json.get_data()
	if not data is Dictionary:
		push_warning("[EventService] Rarity curves is not a dictionary")
		_set_default_rarity_curves()
		return

	_rarity_curves = data
	print("[EventService] Loaded rarity curves")


func _set_default_rarity_curves() -> void:
	"""Set default rarity curves when config not found"""
	_rarity_curves = {
		"common": {
			"base_probability": 0.15,
			"min_turn": 5,
			"cooldown_turns": 10
		},
		"rare": {
			"base_probability": 0.08,
			"min_turn": 10,
			"cooldown_turns": 25
		},
		"legendary": {
			"base_probability": 0.03,
			"min_turn": 20,
			"cooldown_turns": 50
		},
		"year_trigger": {
			"turns_per_year": 12,
			"base_year": 2017,
			"fuzzy_window_turns": 2
		}
	}


func _load_overrides() -> void:
	"""Load all override files from the overrides directory"""
	_overrides.clear()

	var dir = DirAccess.open(OVERRIDES_DIR_PATH)
	if dir == null:
		print("[EventService] No overrides directory found")
		return

	dir.list_dir_begin()
	var filename = dir.get_next()

	while filename != "":
		if not dir.current_is_dir() and filename.ends_with(".json"):
			var filepath = OVERRIDES_DIR_PATH + filename
			_load_override_file(filepath)
		filename = dir.get_next()

	dir.list_dir_end()
	print("[EventService] Loaded %d event overrides" % _overrides.size())


func _load_override_file(filepath: String) -> void:
	"""Load a single override file and merge into overrides dictionary"""
	var file = FileAccess.open(filepath, FileAccess.READ)
	if file == null:
		push_warning("[EventService] Failed to open override file: %s" % filepath)
		return

	var json = JSON.new()
	var error = json.parse(file.get_as_text())
	file.close()

	if error != OK:
		push_warning("[EventService] Failed to parse override file %s: %s" % [filepath, json.get_error_message()])
		return

	var data = json.get_data()
	if not data is Dictionary:
		push_warning("[EventService] Override file %s is not a dictionary" % filepath)
		return

	# Merge overrides (keys starting with _ are metadata)
	for event_id in data.keys():
		if event_id.begins_with("_"):
			continue
		_overrides[event_id] = data[event_id]


func _apply_overrides(raw_event: Dictionary) -> Dictionary:
	"""Apply override values to a raw event (deep merge)"""
	var event_id = raw_event.get("id", "")
	if event_id.is_empty() or not _overrides.has(event_id):
		return raw_event

	# Create a copy to avoid modifying the original
	var result = raw_event.duplicate(true)
	var override = _overrides[event_id]

	# Deep merge override values
	for key in override.keys():
		if key.begins_with("_"):
			continue  # Skip metadata keys like "_reason"

		var override_value = override[key]

		if override_value is Dictionary and result.has(key) and result[key] is Dictionary:
			# Merge dictionaries
			for subkey in override_value.keys():
				result[key][subkey] = override_value[subkey]
		elif override_value is Array:
			# Arrays replace entirely (e.g., impacts)
			result[key] = override_value.duplicate(true)
		else:
			# Scalar values replace
			result[key] = override_value

	return result


func reload_config() -> void:
	"""Reload all config files and re-transform events"""
	print("[EventService] Reloading configuration...")
	_load_variable_mapping()
	_load_rarity_curves()
	_load_overrides()
	_transform_all_events()
	print("[EventService] Configuration reloaded, %d events transformed" % transformed_events.size())

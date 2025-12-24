extends Node
## EventService - Fetches and caches historical events from external sources
##
## This service handles:
## 1. Fetching historical AI safety timeline data from pdoom-data API or local cache
## 2. Transforming raw historical data into game-playable events
## 3. Caching events locally for offline play
## 4. Providing events to GameEvents system
##
## Data Flow:
##   External API (pdoom-data) -> Fetch -> Transform -> Cache -> GameEvents
##
## The historical data contains real AI safety milestones (papers, org founding,
## policy events, etc.) which get transformed into game events with costs,
## effects, and player choices.

# Configuration
const API_BASE_URL = "https://api.pdoom.org/v1"  # Future API endpoint
const FALLBACK_DATA_PATH = "res://data/historical_events.json"  # Bundled fallback
const CACHE_PATH = "user://event_cache.json"
const CACHE_EXPIRY_HOURS = 24  # Re-fetch after this many hours

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

# Transformation rules for converting historical data to game events
var _transformation_rules: Dictionary = {}


func _ready():
	# Create HTTP request node for API calls
	http_request = HTTPRequest.new()
	http_request.timeout = 30.0  # 30 second timeout
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)

	# Load cached events on startup
	_load_from_cache()

	print("[EventService] Initialized with %d cached events" % cached_events.size())


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
	"""Load bundled fallback data shipped with the game"""
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

	if data is Array:
		for event in data:
			cached_events.append(event)
	elif data is Dictionary and data.has("events"):
		for event in data["events"]:
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
		var game_event = _transform_event(raw_event)
		if game_event != null and not game_event.is_empty():
			transformed_events.append(game_event)

	events_transformed.emit(transformed_events.size())
	print("[EventService] Transformed %d events" % transformed_events.size())


func _transform_event(raw: Dictionary) -> Dictionary:
	"""
	Transform a raw historical event into a game-playable event.

	Historical data format (from pdoom-data):
	{
		"id": "miri_founded",
		"date": "2000-01-01",
		"title": "MIRI Founded",
		"description": "Machine Intelligence Research Institute founded...",
		"category": "organization",
		"significance": 8,
		"sources": ["https://..."]
	}

	Game event format:
	{
		"id": "hist_miri_founded",
		"name": "MIRI Founded",
		"description": "...",
		"type": "popup",
		"trigger_type": "turn_exact",
		"trigger_turn": <calculated from date>,
		"year": 2000,
		"category": "organization",
		"options": [...]
	}
	"""
	if not raw.has("id") or not raw.has("title"):
		return {}

	var event_id = "hist_%s" % raw["id"]
	var category = raw.get("category", "general")
	var significance = raw.get("significance", 5)
	var year = _extract_year(raw.get("date", "2017-01-01"))

	# Calculate trigger turn based on year (game starts in 2017)
	var base_year = 2017
	var turns_per_year = 12  # Assuming monthly turns
	var trigger_turn = max(1, (year - base_year) * turns_per_year + 1)

	# Generate options based on event category
	var options = _generate_options(raw, category, significance)

	var game_event: Dictionary = {
		"id": event_id,
		"name": raw.get("title", "Historical Event"),
		"description": raw.get("description", "A significant event in AI safety history."),
		"type": "popup",
		"trigger_type": "turn_exact",
		"trigger_turn": trigger_turn,
		"year": year,
		"category": category,
		"significance": significance,
		"repeatable": false,
		"historical": true,  # Flag to identify historical events
		"source_data": raw,  # Keep original data for reference
		"options": options
	}

	return game_event


func _extract_year(date_string: String) -> int:
	"""Extract year from date string (YYYY-MM-DD format)"""
	if date_string.length() >= 4:
		return date_string.substr(0, 4).to_int()
	return 2017


func _generate_options(raw: Dictionary, category: String, significance: int) -> Array:
	"""
	Generate player choice options based on event category and significance.

	Options vary by category:
	- organization: Partner, compete, ignore
	- research: Adopt, critique, build upon
	- policy: Support, oppose, lobby
	- incident: Respond, ignore, capitalize
	"""
	var options: Array = []

	# Scale effects by significance (1-10 scale)
	var effect_multiplier = significance / 5.0
	var rep_effect = int(5 * effect_multiplier)
	var doom_effect = int(3 * effect_multiplier)
	var money_effect = int(10000 * effect_multiplier)

	match category:
		"organization":
			options = [
				{
					"id": "collaborate",
					"text": "Seek collaboration",
					"costs": {"action_points": 1},
					"effects": {"reputation": rep_effect, "doom": -doom_effect},
					"message": "Established collaborative relationship."
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

		"research", "paper":
			options = [
				{
					"id": "build_upon",
					"text": "Build upon this research",
					"costs": {"action_points": 1, "money": money_effect},
					"effects": {"research": rep_effect * 3, "doom": doom_effect / 2},
					"message": "Advancing the research frontier."
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

		"policy", "regulation":
			options = [
				{
					"id": "support",
					"text": "Publicly support",
					"costs": {"action_points": 1},
					"effects": {"reputation": rep_effect, "doom": -doom_effect},
					"message": "Your support strengthens the policy effort."
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

		"incident", "capability":
			options = [
				{
					"id": "respond_publicly",
					"text": "Issue public response",
					"costs": {"action_points": 1},
					"effects": {"reputation": rep_effect, "doom": -doom_effect / 2},
					"message": "Your response shapes public understanding."
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

		_:  # Default options for other categories
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
		"is_loading": is_loading
	}

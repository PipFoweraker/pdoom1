extends Node
class_name ScenarioLoader
## Scenario/Mod Pack Loader for Godot
##
## Loads scenario packs from JSON files allowing custom game configurations.
## Scenarios can override starting resources, add custom events, and more.
## Drop new .json files into res://data/scenarios/ to add new scenarios.
##
## Usage:
##   var loader = ScenarioLoader.new()
##   var scenarios = loader.get_available_scenarios()
##   var scenario = loader.load_scenario("my_scenario")

## Path to scenario data directory (can be overridden for user mods)
var data_dir: String = "res://data/scenarios"

## User scenario directory (writable, for downloaded/custom mods)
var user_data_dir: String = "user://scenarios"

## Cache of loaded scenarios
var _scenario_cache: Dictionary = {}


func _init(custom_data_dir: String = ""):
	"""Initialize scenario loader with optional custom data directory"""
	if custom_data_dir != "":
		data_dir = custom_data_dir

	# Ensure user scenarios directory exists
	var user_dir = DirAccess.open("user://")
	if user_dir and not user_dir.dir_exists("scenarios"):
		user_dir.make_dir("scenarios")


func load_scenario(scenario_id: String) -> Dictionary:
	"""
	Load a scenario by ID

	Args:
		scenario_id: The scenario identifier (filename without .json)

	Returns:
		Dictionary with scenario data, or empty dict if not found
	"""
	# Check cache first
	if _scenario_cache.has(scenario_id):
		return _scenario_cache[scenario_id]

	# Try built-in scenarios first
	var file_path = "%s/%s.json" % [data_dir, scenario_id]
	var scenario = _load_scenario_file(file_path)

	# If not found, try user scenarios
	if scenario.is_empty():
		file_path = "%s/%s.json" % [user_data_dir, scenario_id]
		scenario = _load_scenario_file(file_path)

	if not scenario.is_empty():
		# Ensure scenario has an id
		scenario["id"] = scenario_id
		_scenario_cache[scenario_id] = scenario

	return scenario


func _load_scenario_file(file_path: String) -> Dictionary:
	"""Load and parse a scenario JSON file"""
	if not FileAccess.file_exists(file_path):
		return {}

	var file = FileAccess.open(file_path, FileAccess.READ)
	if file == null:
		push_error("[ScenarioLoader] Failed to open scenario file: %s" % file_path)
		return {}

	var json_string = file.get_as_text()
	file.close()

	var json = JSON.new()
	var parse_result = json.parse(json_string)

	if parse_result != OK:
		push_error("[ScenarioLoader] Failed to parse JSON in %s: %s" % [file_path, json.get_error_message()])
		return {}

	var data = json.get_data()

	# Validate required fields
	if not _validate_scenario(data, file_path):
		return {}

	return data


func _validate_scenario(data: Dictionary, file_path: String) -> bool:
	"""Validate that scenario has required fields"""
	if not data.has("title"):
		push_error("[ScenarioLoader] Scenario missing 'title' field: %s" % file_path)
		return false

	if not data.has("description"):
		push_error("[ScenarioLoader] Scenario missing 'description' field: %s" % file_path)
		return false

	return true


func get_available_scenarios() -> Array[Dictionary]:
	"""
	Get list of all available scenarios (built-in + user)

	Returns:
		Array of scenario summaries with id, title, description
	"""
	var scenarios: Array[Dictionary] = []

	# Add default/standard scenario first
	scenarios.append({
		"id": "",
		"title": "Standard Game",
		"description": "The default P(Doom) experience. Start your AI safety lab in 2017 and work to reduce existential risk.",
		"is_default": true
	})

	# Load built-in scenarios
	_scan_directory_for_scenarios(data_dir, scenarios)

	# Load user scenarios
	_scan_directory_for_scenarios(user_data_dir, scenarios)

	return scenarios


func _scan_directory_for_scenarios(dir_path: String, scenarios: Array[Dictionary]):
	"""Scan a directory for scenario JSON files"""
	var dir = DirAccess.open(dir_path)

	if dir == null:
		# Directory doesn't exist - that's okay for user dir
		return

	dir.list_dir_begin()
	var file_name = dir.get_next()

	while file_name != "":
		if file_name.ends_with(".json"):
			var scenario_id = file_name.get_basename()
			var scenario = load_scenario(scenario_id)

			if not scenario.is_empty():
				scenarios.append({
					"id": scenario_id,
					"title": scenario.get("title", scenario_id),
					"description": scenario.get("description", "No description"),
					"author": scenario.get("author", "Unknown"),
					"version": scenario.get("version", "1.0"),
					"is_default": false
				})

		file_name = dir.get_next()

	dir.list_dir_end()


func get_starting_resources(scenario_id: String) -> Dictionary:
	"""
	Get starting resource overrides for a scenario

	Args:
		scenario_id: The scenario identifier

	Returns:
		Dictionary of resource overrides (only includes values to change)
	"""
	if scenario_id.is_empty():
		return {}

	var scenario = load_scenario(scenario_id)
	return scenario.get("starting_resources", {})


func get_custom_events(scenario_id: String) -> Array:
	"""
	Get custom events defined by a scenario

	Args:
		scenario_id: The scenario identifier

	Returns:
		Array of custom event definitions
	"""
	if scenario_id.is_empty():
		return []

	var scenario = load_scenario(scenario_id)
	return scenario.get("events", [])


func get_scenario_config(scenario_id: String) -> Dictionary:
	"""
	Get additional configuration options for a scenario

	Args:
		scenario_id: The scenario identifier

	Returns:
		Dictionary of config options (start_date, modifiers, etc.)
	"""
	if scenario_id.is_empty():
		return {}

	var scenario = load_scenario(scenario_id)
	return scenario.get("config", {})


func clear_cache():
	"""Clear the scenario cache (useful for development/testing)"""
	_scenario_cache.clear()


## Convenience function (non-static to avoid class_name reference issues)
## Use: var loader = ScenarioLoader.new(); var scenarios = loader.get_available_scenarios()

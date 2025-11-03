extends Node
class_name TimelineLoader
## Historical Timeline Data Loader for Godot
##
## Loads historical AI safety/capabilities events from JSON files.
## Used to populate the "default timeline" - what happens if player takes no action.
##
## Usage:
##   var loader = TimelineLoader.new()
##   var events = loader.load_all_events(2017)
##   var year_data = loader.load_year(2018)

## Path to timeline data directory
var data_dir: String = "res://data/historical_timeline"

## Cache of loaded years
var _year_cache: Dictionary = {}


func _init(custom_data_dir: String = ""):
	"""Initialize timeline loader with optional custom data directory"""
	if custom_data_dir != "":
		data_dir = custom_data_dir


func load_year(year: int) -> Dictionary:
	"""
	Load timeline events for a specific year

	Args:
		year: Year to load (e.g., 2017, 2018)

	Returns:
		Dictionary with year data, or empty dict if file doesn't exist
	"""
	# Check cache first
	if _year_cache.has(year):
		return _year_cache[year]

	var file_path = "%s/%d.json" % [data_dir, year]

	if not FileAccess.file_exists(file_path):
		push_warning("Timeline data not found for year %d: %s" % [year, file_path])
		return {}

	var file = FileAccess.open(file_path, FileAccess.READ)
	if file == null:
		push_error("Failed to open timeline file: %s" % file_path)
		return {}

	var json_string = file.get_as_text()
	file.close()

	var json = JSON.new()
	var parse_result = json.parse(json_string)

	if parse_result != OK:
		push_error("Failed to parse JSON in %s: %s" % [file_path, json.get_error_message()])
		return {}

	var data = json.get_data()

	# Cache the result
	_year_cache[year] = data

	return data


func load_all_events(start_year: int = 2017, end_year: int = 0) -> Array[Dictionary]:
	"""
	Load all timeline events from start_year to end_year

	Args:
		start_year: First year to load (default: 2017)
		end_year: Last year to load (default: current year)

	Returns:
		Array of all timeline events, sorted by trigger_date
	"""
	if end_year == 0:
		# Default to current year
		var date_dict = Time.get_datetime_dict_from_system()
		end_year = date_dict["year"]

	var all_events: Array[Dictionary] = []

	for year in range(start_year, end_year + 1):
		var year_data = load_year(year)
		if year_data.is_empty():
			continue

		var events = year_data.get("default_timeline_events", [])
		for event in events:
			all_events.append(event)

	# Sort by trigger_date
	all_events.sort_custom(func(a, b): return a.get("trigger_date", "9999") < b.get("trigger_date", "9999"))

	return all_events


func get_events_for_date(date_str: String, events: Array[Dictionary] = []) -> Array[Dictionary]:
	"""
	Get all events that trigger on a specific date

	Args:
		date_str: Date in YYYY-MM-DD format
		events: Array of events to filter (default: load all)

	Returns:
		Array of events that trigger on this date
	"""
	if events.is_empty():
		events = load_all_events()

	var matching: Array[Dictionary] = []
	for event in events:
		if event.get("trigger_date") == date_str:
			matching.append(event)

	return matching


func get_available_years() -> Array[int]:
	"""
	Get list of years that have timeline data

	Returns:
		Sorted array of years with data files
	"""
	var years: Array[int] = []
	var dir = DirAccess.open(data_dir)

	if dir == null:
		push_error("Failed to open timeline data directory: %s" % data_dir)
		return years

	dir.list_dir_begin()
	var file_name = dir.get_next()

	while file_name != "":
		if file_name.ends_with(".json"):
			var year_str = file_name.get_basename()
			if year_str.is_valid_int():
				years.append(int(year_str))
		file_name = dir.get_next()

	dir.list_dir_end()
	years.sort()

	return years


func get_events_by_type(event_type: String, events: Array[Dictionary] = []) -> Array[Dictionary]:
	"""
	Filter events by type

	Args:
		event_type: Type to filter (paper_publication, conference, etc.)
		events: Array of events to filter (default: load all)

	Returns:
		Array of events matching type
	"""
	if events.is_empty():
		events = load_all_events()

	var matching: Array[Dictionary] = []
	for event in events:
		if event.get("type") == event_type:
			matching.append(event)

	return matching


func get_events_by_tag(tag: String, events: Array[Dictionary] = []) -> Array[Dictionary]:
	"""
	Filter events by tag

	Args:
		tag: Tag to search for (e.g., 'safety', 'transformers')
		events: Array of events to filter (default: load all)

	Returns:
		Array of events with this tag
	"""
	if events.is_empty():
		events = load_all_events()

	var matching: Array[Dictionary] = []
	for event in events:
		var tags = event.get("tags", [])
		if tag in tags:
			matching.append(event)

	return matching


func get_background_events(year: int) -> Array[Dictionary]:
	"""
	Get background/flavor events for a year

	Args:
		year: Year to load

	Returns:
		Array of background events
	"""
	var year_data = load_year(year)
	if year_data.is_empty():
		return []

	return year_data.get("background_events", [])


func clear_cache():
	"""Clear the year cache (useful for development/testing)"""
	_year_cache.clear()


## Convenience static function
static func load_timeline(start_year: int = 2017) -> Array[Dictionary]:
	"""
	Static convenience function to quickly load timeline

	Args:
		start_year: Starting year (default: 2017)

	Returns:
		Array of all timeline events
	"""
	var loader = TimelineLoader.new()
	return loader.load_all_events(start_year)

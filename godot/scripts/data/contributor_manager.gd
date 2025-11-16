extends Node
## Manages community contributor data and office cat display system
##
## This system loads contributor data from contributors.json (synced from pdoom-data repository)
## and provides functionality for displaying contributor cats with doom-level variants.
##
## Integration points:
## - pdoom-data repo: Source of truth for contributors.json
## - pdoom1-website: Airtable CRM system feeds contributor data
## - UI: Office cat display in main UI
##
## @tutorial: See docs/CONTRIBUTOR_SYSTEM.md for full documentation

class_name ContributorManager

## Emitted when contributor data is loaded
signal contributors_loaded(count: int)

## Emitted when current contributor changes
signal contributor_changed(contributor: Dictionary)

const CONTRIBUTORS_DATA_PATH = "res://data/contributors.json"

## All contributors loaded from JSON
var contributors: Array = []

## Currently displayed contributor
var current_contributor: Dictionary = {}

## Contributor data version
var data_version: String = "1.0"

## Last updated timestamp
var last_updated: String = ""

func _ready():
	load_contributors()

## Load contributors from JSON file
## Returns true if successful, false otherwise
func load_contributors() -> bool:
	if not FileAccess.file_exists(CONTRIBUTORS_DATA_PATH):
		push_warning("Contributors data file not found: " + CONTRIBUTORS_DATA_PATH)
		contributors = []
		contributors_loaded.emit(0)
		return false

	var file = FileAccess.open(CONTRIBUTORS_DATA_PATH, FileAccess.READ)
	if file == null:
		push_error("Failed to open contributors data file")
		contributors = []
		contributors_loaded.emit(0)
		return false

	var json_string = file.get_as_text()
	file.close()

	var json = JSON.new()
	var parse_result = json.parse(json_string)

	if parse_result != OK:
		push_error("Failed to parse contributors JSON: " + json.get_error_message())
		contributors = []
		contributors_loaded.emit(0)
		return false

	var data = json.data

	if not data is Dictionary:
		push_error("Invalid contributors data format: expected Dictionary")
		contributors = []
		contributors_loaded.emit(0)
		return false

	# Store metadata
	data_version = data.get("version", "1.0")
	last_updated = data.get("last_updated", "")

	# Load contributors array
	contributors = data.get("contributors", [])

	print("Loaded %d contributors (version %s, updated %s)" % [contributors.size(), data_version, last_updated])
	contributors_loaded.emit(contributors.size())

	return true

## Get a random contributor from the list
## Returns empty Dictionary if no contributors available
func get_random_contributor() -> Dictionary:
	if contributors.is_empty():
		return {}

	var random_index = randi() % contributors.size()
	return contributors[random_index]

## Set current contributor to display
func set_current_contributor(contributor: Dictionary) -> void:
	current_contributor = contributor
	contributor_changed.emit(contributor)

## Select and set a random contributor as current
func select_random_contributor() -> Dictionary:
	var contributor = get_random_contributor()
	if not contributor.is_empty():
		set_current_contributor(contributor)
	return contributor

## Get cat image path for current doom level
## @param doom_percentage: Current doom level (0.0 to 1.0)
## Returns path to appropriate cat variant image
func get_cat_image_for_doom_level(doom_percentage: float) -> String:
	if current_contributor.is_empty():
		return get_default_cat_image(doom_percentage)

	var cat_image_base = current_contributor.get("cat_image_base", "")
	if cat_image_base.is_empty():
		return get_default_cat_image(doom_percentage)

	# Determine which doom variant to use
	var variant_name = get_doom_variant_name(doom_percentage)

	# Build path: res://assets/cats/{cat_image_base}/{variant_name}.png
	# Try PNG first, fallback to SVG
	var image_path_png = "res://assets/cats/%s/%s.png" % [cat_image_base, variant_name]
	var image_path_svg = "res://assets/cats/%s/%s.svg" % [cat_image_base, variant_name]

	if FileAccess.file_exists(image_path_png):
		return image_path_png
	elif FileAccess.file_exists(image_path_svg):
		return image_path_svg
	else:
		push_warning("Contributor cat image not found: " + image_path_png + ", using default")
		return get_default_cat_image(doom_percentage)

## Get default cat image for doom level
## Used when no contributors are loaded or as fallback
func get_default_cat_image(doom_percentage: float) -> String:
	var variant_name = get_doom_variant_name(doom_percentage)
	# Try PNG first, fallback to SVG (currently we have SVG placeholders)
	var png_path = "res://assets/cats/default/%s.png" % variant_name
	var svg_path = "res://assets/cats/default/%s.svg" % variant_name

	if FileAccess.file_exists(png_path):
		return png_path
	else:
		return svg_path  # Use SVG placeholder

## Convert doom percentage to variant name
## Doom levels: 0-20% = happy, 21-40% = concerned, 41-60% = worried,
##              61-80% = distressed, 81-100% = corrupted
func get_doom_variant_name(doom_percentage: float) -> String:
	if doom_percentage <= 0.2:
		return "happy"
	elif doom_percentage <= 0.4:
		return "concerned"
	elif doom_percentage <= 0.6:
		return "worried"
	elif doom_percentage <= 0.8:
		return "distressed"
	else:
		return "corrupted"

## Get current contributor info
func get_current_contributor() -> Dictionary:
	return current_contributor

## Get all contributors
func get_all_contributors() -> Array:
	return contributors

## Reload contributors from file
## Useful for hot-reloading when data is updated
func reload_contributors() -> bool:
	return load_contributors()

## Check if any contributors are loaded
func has_contributors() -> bool:
	return not contributors.is_empty()

## Get contributor count
func get_contributor_count() -> int:
	return contributors.size()

## Get contributor by ID
func get_contributor_by_id(id: String) -> Dictionary:
	for contributor in contributors:
		if contributor.get("id", "") == id:
			return contributor
	return {}

## Get contributors by contribution type
## @param contribution_type: e.g., "bug_report", "feature_request", "playtesting"
func get_contributors_by_type(contribution_type: String) -> Array:
	var filtered = []
	for contributor in contributors:
		var types = contributor.get("contribution_types", [])
		if contribution_type in types:
			filtered.append(contributor)
	return filtered

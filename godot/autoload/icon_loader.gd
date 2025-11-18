extends Node
## Loads and caches icons based on mapping file
## Autoload singleton - access via IconLoader.get_action_icon() etc.

const MAPPING_PATH = "res://data/icon_mapping.json"

var _icon_cache: Dictionary = {}
var _mapping: Dictionary = {}
var _mapping_loaded: bool = false
var _placeholder_texture: Texture2D = null

func _ready():
	_load_mapping()
	_create_placeholder_texture()

func _load_mapping():
	"""Load icon mapping from JSON file"""
	if FileAccess.file_exists(MAPPING_PATH):
		var file = FileAccess.open(MAPPING_PATH, FileAccess.READ)
		if file:
			var json = JSON.new()
			var parse_result = json.parse(file.get_as_text())
			if parse_result == OK:
				_mapping = json.data
				_mapping_loaded = true
				print("[IconLoader] Loaded mapping with %d action icons" % _mapping.get("actions", {}).size())
			else:
				push_error("[IconLoader] Failed to parse mapping JSON: " + json.get_error_message())
		file.close()
	else:
		push_error("[IconLoader] Mapping file not found: " + MAPPING_PATH)

func _create_placeholder_texture():
	"""Create a neon placeholder texture for missing icons"""
	var img = Image.create(64, 64, false, Image.FORMAT_RGBA8)

	# Fill with neon magenta/cyan checkerboard pattern
	for x in range(64):
		for y in range(64):
			@warning_ignore("integer_division")
			var is_checker = ((x / 8) + (y / 8)) % 2 == 0
			if is_checker:
				img.set_pixel(x, y, Color(1.0, 0.0, 1.0))  # Neon magenta
			else:
				img.set_pixel(x, y, Color(0.0, 1.0, 1.0))  # Neon cyan

	# Add question mark pattern in center (simple)
	var center_color = Color(1.0, 1.0, 0.0)  # Yellow
	for x in range(24, 40):
		for y in range(16, 24):
			img.set_pixel(x, y, center_color)
	for x in range(32, 40):
		for y in range(24, 40):
			img.set_pixel(x, y, center_color)
	for x in range(24, 40):
		for y in range(40, 48):
			img.set_pixel(x, y, center_color)

	_placeholder_texture = ImageTexture.create_from_image(img)

func _get_icon_path_from_mapping(category: String, action_id: String) -> String:
	"""Extract icon path from mapping, handling both old and new format"""
	var category_data = _mapping.get(category, {})
	if not category_data.has(action_id):
		return ""

	var entry = category_data[action_id]

	# New format: {"icon": "path", "status": "mapped"}
	if entry is Dictionary:
		var icon_path = entry.get("icon", "")
		if icon_path == "PLACEHOLDER":
			return ""
		return icon_path

	# Old format: direct path string
	return entry

func get_action_icon(action_id: String) -> Texture2D:
	"""Get icon texture for an action, returns placeholder if missing"""
	if not _mapping_loaded:
		return _placeholder_texture

	# Check cache first
	if _icon_cache.has(action_id):
		return _icon_cache[action_id]

	# Look up in mapping - check all categories
	var icon_path = ""

	# Check actions
	icon_path = _get_icon_path_from_mapping("actions", action_id)
	if icon_path == "":
		# Check hiring
		icon_path = _get_icon_path_from_mapping("hiring", action_id)
	if icon_path == "":
		# Check fundraising
		icon_path = _get_icon_path_from_mapping("fundraising", action_id)

	if icon_path == "":
		# Return placeholder for unmapped actions
		_icon_cache[action_id] = _placeholder_texture
		return _placeholder_texture

	# Load texture
	var texture = load(icon_path) as Texture2D
	if texture:
		_icon_cache[action_id] = texture
		return texture
	else:
		push_warning("[IconLoader] Could not load icon: " + icon_path)
		_icon_cache[action_id] = _placeholder_texture
		return _placeholder_texture

func is_placeholder(action_id: String) -> bool:
	"""Check if an action uses a placeholder icon"""
	if not _mapping_loaded:
		return true

	# Check all categories
	for category in ["actions", "hiring", "fundraising"]:
		var category_data = _mapping.get(category, {})
		if category_data.has(action_id):
			var entry = category_data[action_id]
			if entry is Dictionary:
				return entry.get("status", "") == "needs_generation" or entry.get("icon", "") == "PLACEHOLDER"
			return false

	return true

func get_resource_icon(resource_name: String) -> Texture2D:
	"""Get icon texture for a resource"""
	if not _mapping_loaded:
		return _placeholder_texture

	var cache_key = "resource_" + resource_name
	if _icon_cache.has(cache_key):
		return _icon_cache[cache_key]

	var icon_path = _mapping.get("resources", {}).get(resource_name, "")
	if icon_path == "":
		return _placeholder_texture

	var texture = load(icon_path) as Texture2D
	if texture:
		_icon_cache[cache_key] = texture
		return texture

	return _placeholder_texture

func get_decorative_icon(element_name: String) -> Texture2D:
	"""Get decorative UI element texture"""
	if not _mapping_loaded:
		return null

	var cache_key = "deco_" + element_name
	if _icon_cache.has(cache_key):
		return _icon_cache[cache_key]

	var icon_path = _mapping.get("decorative", {}).get(element_name, "")
	if icon_path == "":
		return null

	var texture = load(icon_path) as Texture2D
	if texture:
		_icon_cache[cache_key] = texture
		return texture

	return null

func get_risk_indicator(level: String) -> Texture2D:
	"""Get risk level indicator texture"""
	if not _mapping_loaded:
		return null

	var cache_key = "risk_" + level
	if _icon_cache.has(cache_key):
		return _icon_cache[cache_key]

	var icon_path = _mapping.get("risk_indicators", {}).get(level, "")
	if icon_path == "":
		return null

	var texture = load(icon_path) as Texture2D
	if texture:
		_icon_cache[cache_key] = texture
		return texture

	return null

func get_alert_indicator(type: String) -> Texture2D:
	"""Get alert indicator texture"""
	if not _mapping_loaded:
		return null

	var cache_key = "alert_" + type
	if _icon_cache.has(cache_key):
		return _icon_cache[cache_key]

	var icon_path = _mapping.get("alert_indicators", {}).get(type, "")
	if icon_path == "":
		return null

	var texture = load(icon_path) as Texture2D
	if texture:
		_icon_cache[cache_key] = texture
		return texture

	return null

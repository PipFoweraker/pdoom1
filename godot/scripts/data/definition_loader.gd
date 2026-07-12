extends RefCounted
class_name DefinitionLoader
## Shared JSON definition loader (L9, #621), copied from the proven
## scenario_loader.gd load pattern. Used by GameEvents and GameActions to read
## externalized definition files from res://data/.
##
## JSON parses every number as float; whole-number floats are normalized back to
## int so definitions behave identically to the old in-code literals (typed
## GameState fields such as action_points reject float assignment). Non-whole
## floats (probabilities, weights) are preserved.


static func load_object(path: String, context: String) -> Dictionary:
	"""Load + parse a JSON object file, int-normalized. Empty dict on any failure
	(with a push_error naming the consumer), so callers fall back safely."""
	if not FileAccess.file_exists(path):
		push_error("[%s] Definition file missing: %s" % [context, path])
		return {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_error("[%s] Failed to open definition file: %s" % [context, path])
		return {}
	var json := JSON.new()
	var err := json.parse(file.get_as_text())
	file.close()
	if err != OK:
		push_error("[%s] Failed to parse %s: %s" % [context, path, json.get_error_message()])
		return {}
	var data = json.get_data()
	if not data is Dictionary:
		push_error("[%s] %s is not a JSON object" % [context, path])
		return {}
	return intify(data)


static func intify(value):
	"""Recursively convert whole-number floats to int (JSON round-trip
	normalization). Non-whole floats are preserved."""
	match typeof(value):
		TYPE_FLOAT:
			if value == floor(value):
				return int(value)
			return value
		TYPE_ARRAY:
			for i in range(value.size()):
				value[i] = intify(value[i])
			return value
		TYPE_DICTIONARY:
			for key in value.keys():
				value[key] = intify(value[key])
			return value
	return value

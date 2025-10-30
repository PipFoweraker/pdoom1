extends Node
## Bridge between Godot UI and Python game logic
##
## Manages communication with the Python game engine running shared/ code.
## Uses JSON for serialization between GDScript and Python.

signal game_state_updated(state: Dictionary)
signal event_triggered(event: Dictionary)
signal action_result(result: Dictionary)

var python_process: int = -1
var game_state: Dictionary = {}
var is_initialized: bool = false

const PYTHON_BRIDGE_PATH = "res://../shared_bridge/bridge_server.py"

func _ready():
	print("[GameBridge] Initializing Python bridge...")
	initialize_python_bridge()

func initialize_python_bridge():
	"""Start Python process that runs shared game logic"""
	# For now, we'll use a simpler approach: import Python logic directly
	# through a JSON file-based communication system
	# TODO: Implement proper IPC or use GDExtension for direct Python calls
	pass

func start_new_game(seed: String = ""):
	"""Initialize a new game with the shared logic"""
	var init_data = {
		"action": "init_game",
		"seed": seed if seed != "" else str(Time.get_ticks_msec())
	}
	return _send_command(init_data)

func execute_action(action_id: String) -> Dictionary:
	"""Execute a game action through the shared logic"""
	var command = {
		"action": "execute_action",
		"action_id": action_id
	}
	return _send_command(command)

func end_turn() -> Dictionary:
	"""Process end of turn through shared logic"""
	var command = {
		"action": "end_turn"
	}
	return _send_command(command)

func get_available_actions() -> Array:
	"""Get list of available actions from game logic"""
	var command = {
		"action": "get_actions"
	}
	var result = _send_command(command)
	return result.get("actions", [])

func _send_command(command: Dictionary) -> Dictionary:
	"""
	Send command to Python bridge and get response.
	For Phase 4 MVP, we'll use file-based IPC.
	"""
	# TODO: Implement proper IPC
	# For now, return mock data
	return {
		"success": true,
		"data": {}
	}

func _on_python_output(output: String):
	"""Handle output from Python process"""
	var json = JSON.new()
	var parse_result = json.parse(output)
	if parse_result == OK:
		var data = json.get_data()
		_handle_python_message(data)

func _handle_python_message(data: Dictionary):
	"""Process messages from Python game logic"""
	match data.get("type", ""):
		"state_update":
			game_state = data.get("state", {})
			game_state_updated.emit(game_state)
		"event":
			event_triggered.emit(data.get("event", {}))
		"action_result":
			action_result.emit(data.get("result", {}))
		_:
			push_warning("Unknown message type from Python: " + str(data.get("type")))

func get_game_state() -> Dictionary:
	"""Get current game state"""
	return game_state

func _exit_tree():
	"""Clean up Python process on exit"""
	if python_process:
		# TODO: Properly terminate Python process
		pass

extends Node
## Main game manager - handles Python bridge and game state
##
## This is the central singleton that manages all game logic through the Python bridge.
## Spawns bridge_server.py as a subprocess and communicates via JSON over stdin/stdout.

signal game_state_updated(state: Dictionary)
signal turn_phase_changed(phase_info: Dictionary)
signal event_triggered(event: Dictionary)
signal action_executed(result: Dictionary)
signal error_occurred(error_msg: String)
signal actions_available(actions: Array)

# Python process
var python_process: int = -1
var python_output: Array = []
var awaiting_response: bool = false
var pending_callback: Callable

# Game state
var game_state: Dictionary = {}
var current_phase: Dictionary = {}
var is_initialized: bool = false

# Paths (relative to Godot project root)
const PYTHON_PATH = "python"
const BRIDGE_SCRIPT = "../shared_bridge/bridge_server.py"

func _ready():
	print("[GameManager] Starting...")
	initialize_python_bridge()

func initialize_python_bridge():
	"""Spawn Python bridge process"""
	print("[GameManager] Spawning Python bridge process...")

	# Get absolute path to bridge script
	var project_path = ProjectSettings.globalize_path("res://")
	var bridge_path = project_path.path_join(BRIDGE_SCRIPT).replace("/", "\\")

	print("[GameManager] Bridge path: ", bridge_path)

	# Spawn Python process
	# Note: In Godot 4.x, we use OS.execute in non-blocking mode
	# For stdio communication, we'll use a different approach with temporary files
	# or implement a proper async communication layer

	# For now, we'll start with a simpler synchronous approach
	# TODO: Implement async process communication
	print("[GameManager] Bridge initialized (sync mode)")

func start_new_game(seed: String = ""):
	"""Initialize a new game"""
	print("[GameManager] Starting new game with seed: ", seed if seed else "random")

	var actual_seed = seed if seed else str(Time.get_ticks_msec())
	var command = {
		"action": "init_game",
		"seed": actual_seed
	}

	send_command(command, func(response):
		if response.get("success", false):
			game_state = response.get("state", {})
			current_phase = response.get("turn_phase", {})
			is_initialized = true
			print("[GameManager] Game initialized!")
			print("[GameManager] Turn: ", game_state.get("turn", 0))
			print("[GameManager] Money: $", game_state.get("money", 0))
			game_state_updated.emit(game_state)
			turn_phase_changed.emit(current_phase)
		else:
			var error = response.get("error", "Unknown error")
			print("[GameManager] Failed to initialize: ", error)
			error_occurred.emit(error)
	)

func get_available_actions():
	"""Request list of available actions"""
	var command = {"action": "get_actions"}
	send_command(command, func(response):
		if response.get("success", false):
			var actions = response.get("actions", [])
			print("[GameManager] Got ", actions.size(), " available actions")
			actions_available.emit(actions)
		else:
			print("[GameManager] Failed to get actions: ", response.get("error", ""))
			error_occurred.emit(response.get("error", "Failed to load actions"))
	)

func select_action(action_id: String):
	"""Queue an action for execution (doesn't execute immediately)"""
	print("[GameManager] Selecting action: ", action_id)
	var command = {
		"action": "select_action",
		"action_id": action_id
	}

	send_command(command, func(response):
		if response.get("success", false):
			var result = response.get("result", {})
			print("[GameManager] Action selected: ", result.get("message", ""))
			action_executed.emit(result)
		else:
			print("[GameManager] Failed to select action: ", response.get("error", ""))
			error_occurred.emit(response.get("error", ""))
	)

func end_turn():
	"""End current turn - executes queued actions and processes turn"""
	print("[GameManager] Ending turn...")
	var command = {"action": "end_turn"}

	send_command(command, func(response):
		if response.get("success", false):
			var result = response.get("result", {})
			print("[GameManager] Turn ended successfully")

			# Update state from result
			if result.has("state"):
				game_state = result.get("state", {})
				game_state_updated.emit(game_state)

			print("[GameManager] New turn: ", game_state.get("turn", 0))
		else:
			print("[GameManager] Failed to end turn: ", response.get("error", ""))
			error_occurred.emit(response.get("error", ""))
	)

func start_turn():
	"""Start new turn phase - triggers events"""
	print("[GameManager] Starting turn phase...")
	var command = {"action": "start_turn"}

	send_command(command, func(response):
		if response.get("success", false):
			current_phase = response.get("phase_info", {})
			game_state = response.get("state", {})

			turn_phase_changed.emit(current_phase)
			game_state_updated.emit(game_state)

			# Check for events
			if current_phase.has("pending_events") and current_phase["pending_events"].size() > 0:
				print("[GameManager] Events triggered!")
				for event in current_phase["pending_events"]:
					event_triggered.emit(event)
		else:
			print("[GameManager] Failed to start turn: ", response.get("error", ""))
	)

func resolve_event(event_id: String, choice_id: String):
	"""Resolve an event with a player choice"""
	print("[GameManager] Resolving event: ", event_id, " with choice: ", choice_id)
	var command = {
		"action": "resolve_event",
		"event_id": event_id,
		"choice_id": choice_id
	}

	send_command(command, func(response):
		if response.get("success", false):
			game_state = response.get("state", {})
			game_state_updated.emit(game_state)
			print("[GameManager] Event resolved")
		else:
			print("[GameManager] Failed to resolve event: ", response.get("error", ""))
	)

func get_current_state():
	"""Request current game state"""
	var command = {"action": "get_state"}
	send_command(command, func(response):
		if response.get("success", false):
			game_state = response.get("state", {})
			game_state_updated.emit(game_state)
	)

func send_command(command: Dictionary, callback: Callable):
	"""
	Send command to Python bridge via echo + pipe to python.

	Uses OS.execute to run: echo 'json' | python bridge_server.py
	This is synchronous and simple for MVP.

	Future: Use OS.create_process + pipe communication for async.
	"""

	# Convert command to JSON (escape for shell)
	var json_str = JSON.stringify(command)

	# Get absolute path to bridge
	var project_path = ProjectSettings.globalize_path("res://")
	var bridge_path = project_path.path_join(BRIDGE_SCRIPT).replace("/", "\\")

	# Execute: printf 'json\n' | python bridge_server.py
	# On Windows, use powershell or cmd
	var output = []

	# Use PowerShell for reliable piping on Windows
	var ps_command = 'echo \'' + json_str + '\' | python "' + bridge_path + '"'

	var exit_code = OS.execute(
		"powershell",
		["-NoProfile", "-Command", ps_command],
		output,
		true,  # read_stderr
		false  # open_console
	)

	# Parse output (should be 2 lines: {"ready": true} then actual response)
	if output.size() > 0:
		var full_output = output[0]
		var lines = full_output.split("\n")

		# Find the response line (skip "ready" line)
		for line in lines:
			line = line.strip_edges()
			if line.is_empty():
				continue

			var json = JSON.new()
			var parse_result = json.parse(line)

			if parse_result == OK:
				var response = json.get_data()
				# Skip the "ready" message, process actual command response
				if not response.has("ready"):
					callback.call(response)
					return

		print("[GameManager] No valid response found in output: ", full_output)
		error_occurred.emit("No valid response from bridge")
	else:
		print("[GameManager] No output from Python bridge")
		error_occurred.emit("No response from bridge")

func get_game_state() -> Dictionary:
	"""Get current cached game state"""
	return game_state

func get_current_phase() -> Dictionary:
	"""Get current turn phase info"""
	return current_phase

func _exit_tree():
	"""Clean up on exit"""
	if python_process != -1:
		# TODO: Terminate Python process if running async
		pass
	print("[GameManager] Shutdown complete")

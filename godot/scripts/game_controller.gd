extends Control
# game_controller.gd
# Main game controller for P(Doom) - bridges Godot UI to Python shared logic

# Load leaderboard script
var LeaderboardClass = preload("res://scripts/leaderboard.gd")
var leaderboard = null

# Game session tracking
var game_start_time: float = 0.0
var game_seed: String = "default"
var lab_name: String = "AI Safety Lab"

# Game state (will eventually come from Python)
var game_state = {
	"turn": 0,
	"money": 100000.0,
	"compute": 100.0,
	"safety": 0.0,
	"capabilities": 0.0,
	"employees": {
		"safety_researchers": 0,
		"capabilities_researchers": 0,
		"compute_researchers": 0
	},
	"game_over": false,
	"victory": false,
	"game_over_reason": ""
}

# UI node references
@onready var turn_label = $GameUI/TopBar/TurnLabel
@onready var money_label = $GameUI/Resources/MoneyPanel/Value
@onready var compute_label = $GameUI/Resources/ComputePanel/Value
@onready var safety_label = $GameUI/Resources/SafetyPanel/Value
@onready var capabilities_label = $GameUI/Resources/CapabilitiesPanel/Value
@onready var message_label = $GameUI/BottomBar/MessageLabel
@onready var end_game_screen = $EndGameScreen

func _ready():
	print("P(Doom) Game Controller: Initializing...")

	# Initialize leaderboard
	leaderboard = LeaderboardClass.new(game_seed)

	# Start session tracking
	game_start_time = Time.get_ticks_msec() / 1000.0

	update_ui()
	show_message("Welcome to P(Doom)! Manage your AI safety lab wisely.")

func _input(event):
	# Handle spacebar for end turn
	if event.is_action_pressed("ui_accept") or (event is InputEventKey and event.keycode == KEY_SPACE and event.pressed):
		if not game_state["game_over"]:
			_on_end_turn_pressed()
			get_viewport().set_input_as_handled()

	# Handle R key for restart
	if event is InputEventKey and event.keycode == KEY_R and event.pressed:
		_on_restart_pressed()
		get_viewport().set_input_as_handled()

# Action button handlers
func _on_hire_safety_pressed():
	execute_action("hire_safety_researcher")

func _on_hire_capabilities_pressed():
	execute_action("hire_capabilities_researcher")

func _on_purchase_compute_pressed():
	execute_action("purchase_compute")

func _on_fundraise_pressed():
	execute_action("fundraise")

func _on_end_turn_pressed():
	if game_state["game_over"]:
		show_message("Game Over! Press 'New Game' or R to restart.")
		return
	process_turn_end()

func _on_restart_pressed():
	print("Restarting game...")
	get_tree().reload_current_scene()

# Core game logic (temporary - will move to Python)
func execute_action(action_id: String):
	if game_state["game_over"]:
		show_message("Game Over! Start a new game to continue.")
		return

	var success = false
	var message = ""

	print("Attempting action: ", action_id)

	match action_id:
		"hire_safety_researcher":
			if game_state["money"] >= 50000:
				game_state["money"] -= 50000
				game_state["safety"] += 2
				game_state["employees"]["safety_researchers"] += 1
				success = true
				message = "Hired safety researcher (+2 safety)"
			else:
				message = "Not enough money ($50,000 needed)"

		"hire_capabilities_researcher":
			if game_state["money"] >= 50000:
				game_state["money"] -= 50000
				game_state["capabilities"] += 3
				game_state["employees"]["capabilities_researchers"] += 1
				success = true
				message = "Hired capabilities researcher (+3 capabilities)"
			else:
				message = "Not enough money ($50,000 needed)"

		"purchase_compute":
			if game_state["money"] >= 10000:
				game_state["money"] -= 10000
				game_state["compute"] += 50
				success = true
				message = "Purchased compute (+50)"
			else:
				message = "Not enough money ($10,000 needed)"

		"fundraise":
			game_state["money"] += 100000
			success = true
			message = "Successfully raised $100,000!"

	if success:
		print("Action executed: ", action_id)

	show_message(message)
	update_ui()

func process_turn_end():
	print("Processing turn end...")

	# Increment turn
	game_state["turn"] += 1

	# Consume compute
	game_state["compute"] -= 5.0

	# Staff maintenance
	var total_employees = (game_state["employees"]["safety_researchers"] +
						  game_state["employees"]["capabilities_researchers"] +
						  game_state["employees"]["compute_researchers"])

	if total_employees > 0:
		var maintenance_cost = total_employees * 10000.0
		game_state["money"] -= maintenance_cost
		show_message("Turn %d: Staff maintenance -$%s" % [game_state["turn"], format_number(maintenance_cost)])
	else:
		show_message("Turn %d" % game_state["turn"])

	# Check game over conditions
	if game_state["money"] <= 0:
		game_state["game_over"] = true
		game_state["money"] = 0  # Floor at 0
		game_state["game_over_reason"] = "Out of money! Lab bankrupt."
		handle_game_over()
	elif game_state["compute"] <= 0:
		game_state["game_over"] = true
		game_state["compute"] = 0  # Floor at 0
		game_state["game_over_reason"] = "Out of compute! Research halted."
		handle_game_over()

	update_ui()

func handle_game_over():
	"""Handle game over - save score and show results"""
	print("=== GAME OVER ===")
	print("Reason: ", game_state["game_over_reason"])
	print("Final Turn: ", game_state["turn"])

	# Calculate game duration
	var game_end_time = Time.get_ticks_msec() / 1000.0
	var duration = game_end_time - game_start_time

	# Create score entry
	var score_entry = LeaderboardClass.ScoreEntry.new(
		game_state["turn"],  # Score = turns survived
		lab_name,
		game_state["turn"],  # Level reached
		"Bootstrap_v0.1.0",  # Game mode
		duration
	)

	# Add to leaderboard
	var result = leaderboard.add_score(score_entry)

	# Show console message
	if result["added"]:
		print("Score added: %d turns (Rank #%d)" % [game_state["turn"], result["rank"]])
	else:
		print("Score: %d turns" % game_state["turn"])

	# Disable buttons
	disable_action_buttons()

	# Show end game screen
	end_game_screen.show_end_game(game_state, result["rank"], duration, leaderboard)

func disable_action_buttons():
	"""Disable all action buttons when game is over"""
	$GameUI/Actions/ActionButtons/HireSafetyButton.disabled = true
	$GameUI/Actions/ActionButtons/HireCapabilitiesButton.disabled = true
	$GameUI/Actions/ActionButtons/PurchaseComputeButton.disabled = true
	$GameUI/Actions/ActionButtons/FundraiseButton.disabled = true
	$GameUI/BottomBar/EndTurnButton.disabled = true

func update_ui():
	turn_label.text = "Turn %d" % game_state["turn"]
	money_label.text = "$%s" % format_number(game_state["money"])
	compute_label.text = str(game_state["compute"])
	safety_label.text = str(game_state["safety"])
	capabilities_label.text = str(game_state["capabilities"])

func show_message(msg: String):
	message_label.text = msg
	print("Message: ", msg)

func format_number(num: float) -> String:
	var s = str(int(num))
	var result = ""
	var count = 0
	for i in range(s.length() - 1, -1, -1):
		if count == 3:
			result = "," + result
			count = 0
		result = s[i] + result
		count += 1
	return result

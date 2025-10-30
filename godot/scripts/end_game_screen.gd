extends Control
# end_game_screen.gd
# End game screen showing stats and leaderboard

var LeaderboardClass = preload("res://scripts/leaderboard.gd")
var leaderboard = null
var game_seed: String = "default"

# UI references
@onready var reason_label = $Panel/VBox/Reason
@onready var score_value = $Panel/VBox/Stats/Score/Value
@onready var rank_value = $Panel/VBox/Stats/Rank/Value
@onready var duration_value = $Panel/VBox/Stats/Duration/Value
@onready var money_label = $Panel/VBox/FinalResources/Money
@onready var compute_label = $Panel/VBox/FinalResources/Compute
@onready var safety_label = $Panel/VBox/FinalResources/Safety
@onready var capabilities_label = $Panel/VBox/FinalResources/Capabilities
@onready var leaderboard_entries = $Panel/VBox/Leaderboard/Entries

func _ready():
	visible = false

func show_end_game(game_state: Dictionary, rank: int, duration: float, p_leaderboard):
	"""Display end game screen with stats"""
	visible = true
	leaderboard = p_leaderboard
	game_seed = game_state.get("seed", "default")

	# Set reason
	reason_label.text = game_state.get("game_over_reason", "Game Over")

	# Set stats
	score_value.text = str(game_state["turn"])
	rank_value.text = "#%d" % rank
	duration_value.text = "%d seconds" % int(duration)

	# Set final resources
	money_label.text = "Money: $%s" % format_number(game_state["money"])
	compute_label.text = "Compute: %d" % int(game_state["compute"])
	safety_label.text = "Safety: %d" % int(game_state["safety"])
	capabilities_label.text = "Capabilities: %d" % int(game_state["capabilities"])

	# Display top 5 leaderboard
	_display_leaderboard()

func _display_leaderboard():
	"""Display top 5 leaderboard entries"""
	# Clear existing entries
	for child in leaderboard_entries.get_children():
		child.queue_free()

	# Get top 5 scores
	var top_scores = leaderboard.get_top_scores(5)

	if top_scores.size() == 0:
		var no_scores = Label.new()
		no_scores.text = "No scores yet"
		leaderboard_entries.add_child(no_scores)
		return

	# Display each entry
	for i in range(top_scores.size()):
		var entry = top_scores[i]
		var entry_label = Label.new()

		var rank_str = "#%d" % (i + 1)
		var name_str = entry.player_name
		var score_str = "%d turns" % entry.score

		entry_label.text = "%s  %s - %s" % [rank_str, name_str, score_str]

		# Color ranks
		if i == 0:
			entry_label.add_theme_color_override("font_color", Color(1.0, 0.84, 0.0))  # Gold
		elif i == 1:
			entry_label.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))  # Silver
		elif i == 2:
			entry_label.add_theme_color_override("font_color", Color(0.8, 0.5, 0.2))  # Bronze

		leaderboard_entries.add_child(entry_label)

func _on_play_again_pressed():
	get_tree().reload_current_scene()

func _on_view_leaderboard_pressed():
	# TODO: Show full leaderboard screen
	print("View full leaderboard - TODO")

func _on_main_menu_pressed():
	# TODO: Return to main menu
	print("Main menu - TODO")
	get_tree().reload_current_scene()

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

extends Control
## End Game Screen - Enhanced victory/defeat display with celebration

var LeaderboardClass = preload("res://scripts/leaderboard.gd")
var leaderboard = null
var game_seed: String = "default"
var is_victory: bool = false
var is_new_record: bool = false

# UI references
@onready var title_label = $Panel/VBox/Title
@onready var reason_label = $Panel/VBox/Reason
@onready var score_value = $Panel/VBox/Stats/Score/Value
@onready var rank_value = $Panel/VBox/Stats/Rank/Value
@onready var duration_value = $Panel/VBox/Stats/Duration/Value
@onready var money_label = $Panel/VBox/FinalResources/Money
@onready var compute_label = $Panel/VBox/FinalResources/Compute
@onready var safety_label = $Panel/VBox/FinalResources/Safety
@onready var capabilities_label = $Panel/VBox/FinalResources/Capabilities
@onready var leaderboard_entries = $Panel/VBox/Leaderboard/Entries
@onready var play_again_button = $Panel/VBox/Buttons/PlayAgainButton

func _ready():
	visible = false

func show_end_game(game_state: Dictionary, rank: int, duration: float, p_leaderboard):
	"""Display end game screen with stats and celebration"""
	visible = true
	leaderboard = p_leaderboard
	game_seed = game_state.get("seed", "default")

	# Determine victory/defeat
	is_victory = game_state.get("victory", false)
	is_new_record = (rank == 1)

	# Set title with color and celebration
	if is_victory:
		if is_new_record:
			title_label.text = "🏆 RECORD VICTORY! 🏆"
			title_label.add_theme_color_override("font_color", Color(1.0, 0.84, 0.0))  # Gold
		else:
			title_label.text = "✓ VICTORY!"
			title_label.add_theme_color_override("font_color", Color(0.2, 1.0, 0.2))  # Green
	else:
		title_label.text = "☠ GAME OVER ☠"
		title_label.add_theme_color_override("font_color", Color(1.0, 0.2, 0.2))  # Red

	# Set reason with appropriate flavor
	var reason = game_state.get("game_over_reason", "Game Over")
	if is_victory:
		reason_label.text = "Successfully reduced P(Doom) to 0%! Humanity is safe... for now."
		reason_label.add_theme_color_override("font_color", Color(0.2, 1.0, 0.2))
	else:
		reason_label.text = reason
		reason_label.add_theme_color_override("font_color", Color(1.0, 0.6, 0.6))

	# Set stats
	score_value.text = str(game_state["turn"])
	rank_value.text = "#%d" % rank
	duration_value.text = "%d seconds" % int(duration)

	# Color rank based on performance
	if rank == 1:
		rank_value.add_theme_color_override("font_color", Color(1.0, 0.84, 0.0))  # Gold
	elif rank <= 3:
		rank_value.add_theme_color_override("font_color", Color(0.75, 0.75, 0.75))  # Silver
	elif rank <= 5:
		rank_value.add_theme_color_override("font_color", Color(0.8, 0.5, 0.2))  # Bronze

	# Set final resources with color coding
	money_label.text = "Money: $%s" % format_number(game_state.get("money", 0))
	compute_label.text = "Compute: %d" % int(game_state.get("compute", 0))
	safety_label.text = "Safety Researchers: %d" % int(game_state.get("safety_researchers", 0))
	capabilities_label.text = "Capability Researchers: %d" % int(game_state.get("capability_researchers", 0))

	# Add additional stats
	var doom_value = game_state.get("doom", 0)
	var doom_label = Label.new()
	doom_label.text = "Final P(Doom): %.1f%%" % doom_value
	if doom_value == 0:
		doom_label.add_theme_color_override("font_color", Color(0.2, 1.0, 0.2))
	elif doom_value > 70:
		doom_label.add_theme_color_override("font_color", Color(1.0, 0.2, 0.2))
	else:
		doom_label.add_theme_color_override("font_color", Color(1.0, 1.0, 0.2))
	$Panel/VBox/FinalResources.add_child(doom_label)

	var papers_label = Label.new()
	papers_label.text = "Papers Published: %d" % int(game_state.get("papers", 0))
	$Panel/VBox/FinalResources.add_child(papers_label)

	# Display top 5 leaderboard
	_display_leaderboard()

	# Update button text for victory
	if is_victory:
		play_again_button.text = "Play Again & Beat Your Record!"

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
	"""Restart the game with same seed"""
	print("[EndGameScreen] Restarting game...")
	get_tree().change_scene_to_file("res://scenes/main.tscn")

func _on_view_leaderboard_pressed():
	"""View full leaderboard"""
	print("[EndGameScreen] Opening full leaderboard screen...")
	ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Opening leaderboard from end game", {})
	get_tree().change_scene_to_file("res://scenes/leaderboard_screen.tscn")

func _on_main_menu_pressed():
	"""Return to main menu"""
	print("[EndGameScreen] Returning to main menu...")
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _input(event: InputEvent):
	"""Handle keyboard shortcuts"""
	if not visible:
		return

	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_R:
			_on_play_again_pressed()
		elif event.keycode == KEY_ESCAPE:
			_on_main_menu_pressed()

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

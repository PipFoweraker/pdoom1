extends Control
class_name GameOverScreen
## Game Over screen showing final stats and offering replay options

@onready var title_label = $CenterContainer/PanelContainer/MarginContainer/VBox/TitleLabel
@onready var subtitle_label = $CenterContainer/PanelContainer/MarginContainer/VBox/SubtitleLabel
@onready var stats_label = $CenterContainer/PanelContainer/MarginContainer/VBox/StatsLabel

var game_manager: Node

func _ready():
	# Initially hidden
	visible = false

func show_game_over(is_victory: bool, final_state: Dictionary):
	"""Display game over screen with final statistics"""
	visible = true

	# Set title and colors based on outcome
	if is_victory:
		title_label.text = "VICTORY!"
		title_label.add_theme_color_override("font_color", Color(0.2, 1.0, 0.2))  # Green
		subtitle_label.text = "Humanity Survived the AI Revolution"
		subtitle_label.add_theme_color_override("font_color", Color(0.6, 1.0, 0.6))
	else:
		title_label.text = "DEFEAT"
		title_label.add_theme_color_override("font_color", Color(1.0, 0.2, 0.2))  # Red
		subtitle_label.text = "The AI Destroyed Humanity"
		subtitle_label.add_theme_color_override("font_color", Color(1.0, 0.6, 0.6))

	# Build statistics display
	var stats_text = "[center][b]FINAL STATISTICS[/b][/center]\n\n"

	# Game duration
	var turn = final_state.get("turn", 0)
	stats_text += "[color=cyan]◆ Turns Survived:[/color] [b]%d[/b]\n\n" % turn

	# Doom level
	var doom = final_state.get("doom", 0)
	var doom_color = _get_doom_display_color(doom)
	stats_text += "[color=cyan]◆ Final Doom:[/color] [color=%s][b]%.1f%%[/b][/color]\n" % [doom_color, doom]

	# Doom momentum
	var doom_momentum = final_state.get("doom_momentum", 0.0)
	if abs(doom_momentum) > 0.1:
		var momentum_text = "↑ %.1f (Spiral)" % doom_momentum if doom_momentum > 0 else "↓ %.1f (Flywheel)" % abs(doom_momentum)
		var momentum_color = "red" if doom_momentum > 0 else "green"
		stats_text += "[color=cyan]  └─ Momentum:[/color] [color=%s]%s[/color]\n" % [momentum_color, momentum_text]

	stats_text += "\n"

	# Resources accumulated
	stats_text += "[color=cyan]◆ Resources:[/color]\n"
	stats_text += "  [color=gold]Money:[/color] $%d\n" % final_state.get("money", 0)
	stats_text += "  [color=blue]Compute:[/color] %.1f\n" % final_state.get("compute", 0)
	stats_text += "  [color=purple]Research:[/color] %.1f\n" % final_state.get("research", 0)
	stats_text += "  [color=white]Papers:[/color] %d\n" % final_state.get("papers", 0)
	stats_text += "  [color=orange]Reputation:[/color] %.0f\n\n" % final_state.get("reputation", 0)

	# Team composition
	var safety = final_state.get("safety_researchers", 0)
	var capability = final_state.get("capability_researchers", 0)
	var compute_eng = final_state.get("compute_engineers", 0)
	var total_staff = safety + capability + compute_eng

	stats_text += "[color=cyan]◆ Team:[/color] [b]%d employees[/b]\n" % total_staff
	if total_staff > 0:
		stats_text += "  [color=green]Safety Researchers:[/color] %d\n" % safety
		stats_text += "  [color=red]Capability Researchers:[/color] %d\n" % capability
		stats_text += "  [color=blue]Compute Engineers:[/color] %d\n" % compute_eng

	# Upgrades purchased
	var upgrades = final_state.get("purchased_upgrades", [])
	if upgrades.size() > 0:
		stats_text += "\n[color=cyan]◆ Upgrades:[/color] [b]%d purchased[/b]\n" % upgrades.size()

	# Victory/defeat flavor text
	stats_text += "\n[center][color=gray]───────────────────[/color][/center]\n"
	if is_victory:
		stats_text += "\n[center][color=lime]Your leadership guided humanity safely through\nthe development of transformative AI.[/color][/center]"
	else:
		var reason = _get_defeat_reason(final_state)
		stats_text += "\n[center][color=red]%s[/color][/center]" % reason

	stats_label.text = stats_text

func _get_doom_display_color(doom: float) -> String:
	"""Get color name for doom display"""
	if doom < 30.0:
		return "green"
	elif doom < 60.0:
		return "yellow"
	elif doom < 80.0:
		return "orange"
	else:
		return "red"

func _get_defeat_reason(final_state: Dictionary) -> String:
	"""Generate defeat reason based on final state"""
	var doom = final_state.get("doom", 0)

	if doom >= 100.0:
		return "Doom reached 100%. The AI became\nunaligned and humanity was lost."
	elif final_state.get("money", 0) < 0:
		return "Your organization went bankrupt before\nthe mission could be completed."
	else:
		return "The experiment ended prematurely."

func _on_play_again_pressed():
	"""Restart the game"""
	print("[GameOverScreen] Play Again pressed")
	# Reload the main scene to restart
	get_tree().reload_current_scene()

func _on_main_menu_pressed():
	"""Return to main menu"""
	print("[GameOverScreen] Main Menu pressed")
	get_tree().change_scene_to_file("res://scenes/welcome.tscn")

func _on_quit_pressed():
	"""Quit to desktop"""
	print("[GameOverScreen] Quit pressed")
	get_tree().quit()

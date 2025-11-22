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

	# Connect URL click handler for AI safety links
	if stats_label:
		stats_label.meta_clicked.connect(_on_meta_clicked)

func show_game_over(is_victory: bool, final_state: Dictionary):
	"""Display game over screen with final statistics"""
	visible = true

	# Play appropriate end-game music
	if is_victory:
		# Victory music not yet implemented, keep gameplay music
		pass
	else:
		MusicManager.play_context(MusicManager.MusicContext.DEFEAT)


	# Calculate final score
	var final_score = calculate_final_score(final_state)
	print("[GameOverScreen] Final score: %d" % final_score)

	# Stop verification tracking and get final hash
	VerificationTracker.stop_tracking()
	var final_hash = VerificationTracker.get_final_hash()

	# Export verification data for submission (future leaderboard integration)
	var verification_data = VerificationTracker.export_for_submission(final_state)
	verification_data["score"] = final_score  # Include calculated score
	print("[GameOverScreen] Game ended - Verification hash: %s..." % final_hash.substr(0, 16))
	print("[GameOverScreen] Score: %d" % final_score)
	print("[GameOverScreen] Full verification data ready for submission")

	# TODO: Future - Add UI button to submit score to leaderboard with verification_data

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

	# Final Score (prominent display)
	stats_text += "[center][color=gold]★ FINAL SCORE ★[/color][/center]\n"
	stats_text += "[center][b][color=yellow]%d[/color][/b] points[/center]\n\n" % final_score

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

	# AI Safety resources call to action
	stats_text += "\n\n[center][color=gray]───────────────────[/color][/center]\n"
	stats_text += "\n[center][color=cyan][b]LEARN ABOUT REAL AI SAFETY[/b][/color][/center]\n"
	stats_text += "[center][color=white]The challenges in this game reflect real concerns.[/color][/center]\n"
	stats_text += "[center][color=gray]Visit [color=dodger_blue][url=https://aisafety.info]aisafety.info[/url][/color] to learn more.[/color][/center]"

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

func _on_meta_clicked(meta):
	"""Handle URL clicks in the stats label"""
	print("[GameOverScreen] Opening URL: %s" % meta)
	OS.shell_open(str(meta))

func calculate_final_score(state: Dictionary) -> int:
	"""
	Calculate final score from game state.

	CRITICAL: This formula must match the server-side calculation in
	pdoom1-website/scripts/verification_logic.py exactly!

	Components:
	- Safety Achievement: (100 - doom) * 1000    [Max: 100,000]
	- Research Output:    papers * 5000          [~5-10 papers = 25k-50k]
	- Team Excellence:    researchers * 2000     [~5-10 researchers = 10k-20k]
	- Survival Duration:  turn * 500             [50 turns = 25k]
	- Financial Success:  money * 0.1            [125k money = 12.5k]
	- Victory Bonus:      +50000 if doom < 20%   [50k bonus]

	Typical Range: 50k-250k (good game), 300k+ (excellent)
	"""
	var score = 0

	# Extract values with defaults
	var doom = state.get("doom", 0.0)
	var papers = state.get("papers", 0)
	var turn = state.get("turn", 0)
	var money = state.get("money", 0)

	# Count total researchers (all types)
	var researchers = 0
	researchers += state.get("safety_researchers", 0)
	researchers += state.get("capability_researchers", 0)
	researchers += state.get("compute_engineers", 0)

	# 1. Safety Achievement (40-50% of total score)
	var safety_score = (100 - doom) * 1000
	score += safety_score

	# 2. Research Output (20-30% of total score)
	var paper_score = papers * 5000
	score += paper_score

	# 3. Team Excellence (10-15% of total score)
	var team_score = researchers * 2000
	score += team_score

	# 4. Survival Duration (10-15% of total score)
	var survival_score = turn * 500
	score += survival_score

	# 5. Financial Success (5-10% of total score)
	var financial_score = money * 0.1
	score += financial_score

	# 6. Victory Bonus (unlocks at doom < 20%)
	if doom < 20.0:
		score += 50000  # Victory bonus

	return int(score)

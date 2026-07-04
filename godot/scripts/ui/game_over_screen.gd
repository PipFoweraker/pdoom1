extends Control
class_name GameOverScreen
## Game Over screen showing final stats and offering replay options

@onready var panel_container = $CenterContainer/PanelContainer
@onready var title_label = $CenterContainer/PanelContainer/MarginContainer/VBox/TitleLabel
@onready var subtitle_label = $CenterContainer/PanelContainer/MarginContainer/VBox/SubtitleLabel
@onready var stats_label = $CenterContainer/PanelContainer/MarginContainer/VBox/StatsLabel

var game_manager: Node
var final_turns: int = 0
var final_doom_integral: int = 0
var baseline_turns: int = 0
var baseline_doom_integral: int = 0
var baseline_result: Dictionary = {}
var leaderboard_entry_uuid: String = ""
var game_start_time: float = 0.0

func _ready():
	# Initially hidden
	visible = false

	# Delineate the end-game box with a solid panel + border so it reads clearly as an
	# overlay rather than blending into the dimmed game behind it (playtest: screen4).
	if panel_container:
		var box := StyleBoxFlat.new()
		box.bg_color = Color(0.10, 0.12, 0.15, 0.98)
		box.set_border_width_all(3)
		box.border_color = Color(0.45, 0.55, 0.50, 1.0)
		box.set_corner_radius_all(10)
		box.set_content_margin_all(6)
		panel_container.add_theme_stylebox_override("panel", box)

	# Enable input processing for ENTER key
	set_process_input(true)

	# Connect URL click handler for AI safety links
	if stats_label:
		stats_label.meta_clicked.connect(_on_meta_clicked)

func _input(event: InputEvent):
	"""Handle keyboard shortcuts - ENTER to continue to leaderboard"""
	if not visible:
		return  # Only process input when visible

	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ENTER or event.keycode == KEY_SPACE:
			_continue_to_leaderboard()
			get_viewport().set_input_as_handled()

func show_game_over(is_victory: bool, final_state: Dictionary):
	"""Display game over screen with final statistics"""
	visible = true

	# Play appropriate end-game music
	if is_victory:
		# Victory music not yet implemented, keep gameplay music
		pass
	else:
		MusicManager.play_context(MusicManager.MusicContext.DEFEAT)


	# ADR-0002: the engine is the scoring authority — read the (turns, doom_integral)
	# tuple straight off final_state; no formula here.
	var st = GameState.score_tuple(final_state)
	final_turns = st[0]
	final_doom_integral = st[1]
	print("[GameOverScreen] Final score: %s" % GameState.format_score(final_turns, final_doom_integral))

	# Get baseline (no-action) score for comparison (Issue #372)
	var game_seed = GameConfig.get_display_seed()
	baseline_result = BaselineSimulator.get_baseline_score(game_seed)
	baseline_turns = int(baseline_result.get("turns", 0))
	baseline_doom_integral = int(round(baseline_result.get("doom_integral", 0.0)))
	print("[GameOverScreen] Baseline: %s" % GameState.format_score(baseline_turns, baseline_doom_integral))

	# Stop verification tracking and get final hash
	VerificationTracker.stop_tracking()
	var final_hash = VerificationTracker.get_final_hash()

	# Export verification data for submission (future leaderboard integration)
	var verification_data = VerificationTracker.export_for_submission(final_state)
	verification_data["turns_survived"] = final_turns  # ADR-0002 score tuple
	verification_data["doom_integral"] = final_doom_integral
	print("[GameOverScreen] Game ended - Verification hash: %s..." % final_hash.substr(0, 16))
	print("[GameOverScreen] Score: %s" % GameState.format_score(final_turns, final_doom_integral))
	print("[GameOverScreen] Full verification data ready for submission")


	# Save score to leaderboard (game_seed already obtained for baseline)
	var leaderboard = Leaderboard.new(game_seed, "v" + GameConfig.CURRENT_VERSION)
	var duration = Time.get_ticks_msec() / 1000.0 - game_start_time

	var entry = Leaderboard.ScoreEntry.new(
		final_turns,
		GameConfig.lab_name,
		final_state.get("turn", 0),
		"v" + GameConfig.CURRENT_VERSION,  # Game version from GameConfig
		duration,
		baseline_turns,  # Baseline turns for comparison (Issue #372)
		final_doom_integral,  # ADR-0002 tiebreak
		baseline_doom_integral
	)

	var result = leaderboard.add_score(entry)
	leaderboard_entry_uuid = entry.entry_uuid
	var rank = result.get("rank", -1)

	print("[GameOverScreen] Score saved to leaderboard - Rank: %d" % rank)

	# Store entry UUID globally for leaderboard highlighting
	GameConfig.latest_leaderboard_entry = leaderboard_entry_uuid

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
	stats_text += "[center][b][color=yellow]%s[/color][/b][/center]\n" % GameState.format_score(final_turns, final_doom_integral)

	# Baseline comparison (Issue #372)
	if baseline_turns > 0:
		var comparison = BaselineSimulator.get_comparison_text(final_turns, final_doom_integral, baseline_turns, baseline_doom_integral)
		var comparison_color = comparison["color"].to_html(false)
		stats_text += "[center][color=%s]%s[/color][/center]\n" % [comparison_color, comparison["text"]]
		stats_text += "[center][color=gray](Baseline: %s with no actions)[/color][/center]\n\n" % GameState.format_score(baseline_turns, baseline_doom_integral)
	else:
		stats_text += "\n"

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

	# Navigation hint
	stats_text += "\n\n[center][color=gray]───────────────────[/color][/center]\n"
	stats_text += "\n[center][color=gold][b]⏎ Press ENTER for Leaderboard[/b][/color][/center]"

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

func _continue_to_leaderboard():
	"""Navigate to leaderboard screen to show saved score"""
	print("[GameOverScreen] Transitioning to leaderboard")
	get_tree().change_scene_to_file("res://scenes/leaderboard_screen.tscn")

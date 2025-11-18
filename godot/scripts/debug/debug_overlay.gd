extends CanvasLayer
## Debug Overlay - Press F3 to toggle

@onready var panel = $Panel
@onready var state_label = $"Panel/MarginContainer/VBoxContainer/TabContainer/Game State/StateLabel"
@onready var errors_list = $Panel/MarginContainer/VBoxContainer/TabContainer/Errors/ErrorsList
@onready var performance_label = $Panel/MarginContainer/VBoxContainer/TabContainer/Performance/PerformanceLabel
@onready var rate_slider = $Panel/MarginContainer/VBoxContainer/RefreshRate/RateSlider
@onready var rate_label = $Panel/MarginContainer/VBoxContainer/RefreshRate/RateLabel

var is_visible: bool = false
var update_timer: float = 0.0
var refresh_rate: float = 1.0
var frame_times: Array[float] = []
var max_frame_samples: int = 60

func _ready():
	panel.visible = false

	# Connect to keybind signals
	KeybindManager.debug_overlay_toggled.connect(toggle_visibility)

	var key_name = KeybindManager.get_key_name("debug_overlay")
	print("[DebugOverlay] Ready - Press %s to toggle" % key_name)

	# Connect to ErrorHandler signals
	if ErrorHandler:
		ErrorHandler.error_occurred.connect(_on_error_occurred)
		ErrorHandler.warning_occurred.connect(_on_warning_occurred)

func _process(delta):
	# Track frame time for performance monitoring
	frame_times.append(delta)
	if frame_times.size() > max_frame_samples:
		frame_times.pop_front()

	if not is_visible:
		return

	update_timer += delta
	if update_timer >= refresh_rate:
		update_timer = 0.0
		update_display()

func toggle_visibility():
	is_visible = not is_visible
	panel.visible = is_visible
	if is_visible:
		update_display()
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug overlay opened", {})
	else:
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug overlay closed", {})

func update_display():
	update_game_state()
	update_errors()
	update_performance()

func update_game_state():
	if not GameManager or not GameManager.state:
		state_label.text = "[No game state available]"
		return

	var state = GameManager.state
	var lines: Array[String] = []

	# Header
	lines.append("[b]Game State[/b]")
	lines.append("Turn: %d | Phase: %s" % [state.turn, GameState.TurnPhase.keys()[state.current_phase]])
	lines.append("Seed: %s" % state.seed)
	lines.append("")

	# Resources
	lines.append("[b]Resources[/b]")
	lines.append("Money: $%.0f" % state.money)
	lines.append("Compute: %.1f" % state.compute)
	lines.append("Research: %.1f" % state.research)
	lines.append("Papers: %d" % state.papers)
	lines.append("Reputation: %.1f" % state.reputation)
	lines.append("Action Points: %d / %d" % [state.action_points, state.max_action_points if "max_action_points" in state else 3])
	lines.append("")

	# Doom
	lines.append("[b]Doom System[/b]")
	lines.append("Doom: %.1f" % state.doom)
	if state.doom_system:
		lines.append("Velocity: %.2f" % state.doom_system.doom_velocity)
		lines.append("Momentum: %.2f" % state.doom_system.doom_momentum)
		lines.append("Status: %s" % state.doom_system.get_doom_status())
	lines.append("")

	# Staff
	lines.append("[b]Staff[/b]")
	lines.append("Safety: %d | Capabilities: %d" % [state.safety_researchers, state.capability_researchers])
	lines.append("Compute Eng: %d | Managers: %d" % [state.compute_engineers, state.managers])
	lines.append("Total: %d / %d capacity" % [state.get_total_staff(), state.get_management_capacity()])
	if state.get_unmanaged_count() > 0:
		lines.append("[color=red]Unmanaged: %d[/color]" % state.get_unmanaged_count())
	lines.append("")

	# Individual Researchers
	if state.researchers.size() > 0:
		lines.append("[b]Researchers (%d)[/b]" % state.researchers.size())
		for researcher in state.researchers:
			var burnout_color = "green" if researcher.burnout < 50 else "yellow" if researcher.burnout < 80 else "red"
			lines.append("- %s [%s] (Skill: %d, Burnout: [color=%s]%d[/color])" % [
				researcher.researcher_name,
				researcher.specialization,
				researcher.skill_level,
				burnout_color,
				researcher.burnout
			])
		lines.append("")

	# Actions
	if state.queued_actions.size() > 0:
		lines.append("[b]Queued Actions (%d)[/b]" % state.queued_actions.size())
		for action_id in state.queued_actions:
			lines.append("- %s" % action_id)
		lines.append("")

	# Events
	if state.pending_events.size() > 0:
		lines.append("[b]Pending Events (%d)[/b]" % state.pending_events.size())
		for event in state.pending_events:
			lines.append("- %s" % event.get("name", "Unknown"))
		lines.append("")

	# Rival Labs
	if state.rival_labs.size() > 0:
		lines.append("[b]Rival Labs (%d)[/b]" % state.rival_labs.size())
		for rival in state.rival_labs:
			lines.append("- %s (Cap: %.0f, Money: $%.0fk)" % [
				rival.get("name", "Unknown"),
				rival.get("capabilities", 0),
				rival.get("money", 0) / 1000
			])

	# Game Status
	if state.game_over:
		lines.append("")
		if state.victory:
			lines.append("[b][color=green]VICTORY![/color][/b]")
		else:
			lines.append("[b][color=red]GAME OVER[/color][/b]")

	state_label.text = "\n".join(lines)

func update_errors():
	# Clear existing error displays
	for child in errors_list.get_children():
		child.queue_free()

	if not ErrorHandler:
		return

	var recent_errors = ErrorHandler.get_recent_errors(20)

	if recent_errors.is_empty():
		var label = Label.new()
		label.text = "No errors recorded"
		label.add_theme_font_size_override("font_size", 12)
		errors_list.add_child(label)
		return

	# Show error stats
	var stats = ErrorHandler.get_error_stats()
	var stats_label = Label.new()
	stats_label.text = "[b]Error Stats[/b]\nTotal: %d | Errors: %d | Warnings: %d" % [
		stats["total"],
		stats["by_severity"].get("ERROR", 0) + stats["by_severity"].get("FATAL", 0),
		stats["by_severity"].get("WARNING", 0)
	]
	stats_label.add_theme_font_size_override("font_size", 12)
	errors_list.add_child(stats_label)

	var separator = HSeparator.new()
	errors_list.add_child(separator)

	# Show recent errors
	for error in recent_errors:
		var error_label = Label.new()
		var color = "white"
		match error.severity:
			ErrorHandler.Severity.WARNING:
				color = "yellow"
			ErrorHandler.Severity.ERROR:
				color = "orange"
			ErrorHandler.Severity.FATAL:
				color = "red"

		error_label.text = "[color=%s]%s[/color]" % [color, error.to_string()]
		error_label.add_theme_font_size_override("font_size", 10)
		error_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		errors_list.add_child(error_label)

func update_performance():
	var lines: Array[String] = []

	lines.append("[b]Performance Metrics[/b]")
	lines.append("")

	# FPS
	var fps = Engine.get_frames_per_second()
	var fps_color = "green" if fps >= 55 else "yellow" if fps >= 30 else "red"
	lines.append("FPS: [color=%s]%d[/color]" % [fps_color, fps])

	# Frame time
	if frame_times.size() > 0:
		var avg_frame_time = 0.0
		for ft in frame_times:
			avg_frame_time += ft
		avg_frame_time /= frame_times.size()
		lines.append("Avg Frame Time: %.2f ms" % (avg_frame_time * 1000))

	lines.append("")

	# Memory
	lines.append("[b]Memory[/b]")
	lines.append("Static: %.2f MB" % (OS.get_static_memory_usage() / 1024.0 / 1024.0))
	lines.append("Objects: %d" % Performance.get_monitor(Performance.OBJECT_COUNT))
	lines.append("Resources: %d" % Performance.get_monitor(Performance.OBJECT_RESOURCE_COUNT))
	lines.append("Nodes: %d" % Performance.get_monitor(Performance.OBJECT_NODE_COUNT))
	lines.append("")

	# Render
	lines.append("[b]Rendering[/b]")
	lines.append("Draw Calls: %d" % Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
	lines.append("Vertices: %d" % Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME))

	performance_label.text = "\n".join(lines)

# Signal handlers
func _on_error_occurred(error: ErrorHandler.GameError):
	# Flash the panel red briefly
	if is_visible:
		var tween = create_tween()
		var original_color = panel.modulate
		tween.tween_property(panel, "modulate", Color(1, 0.5, 0.5), 0.1)
		tween.tween_property(panel, "modulate", original_color, 0.3)

func _on_warning_occurred(warning: String):
	# Flash the panel yellow briefly
	if is_visible:
		var tween = create_tween()
		var original_color = panel.modulate
		tween.tween_property(panel, "modulate", Color(1, 1, 0.5), 0.1)
		tween.tween_property(panel, "modulate", original_color, 0.3)

# UI Callbacks
func _on_close_button_pressed():
	toggle_visibility()

func _on_rate_slider_value_changed(value):
	refresh_rate = value
	rate_label.text = "%.1fs" % value

func _on_add_money_button_pressed():
	if GameManager and GameManager.state:
		GameManager.state.money += 50000
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug: Added $50k", {})

func _on_add_ap_button_pressed():
	if GameManager and GameManager.state:
		GameManager.state.action_points += 5
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug: Added 5 AP", {})

func _on_trigger_event_button_pressed():
	if GameManager and GameManager.state:
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug: Trigger event requested", {})
		# Would need to implement event triggering

func _on_commit_plan_button_pressed():
	if GameManager and GameManager.is_initialized:
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug: Commit plan requested", {})
		# Would need to implement commit plan

func _on_reset_game_button_pressed():
	if GameManager:
		ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Debug: Reset game requested", {})
		GameManager.start_new_game()

extends Control
## Full Leaderboard Screen - Comprehensive view of all scores with filtering and pagination

var LeaderboardClass = preload("res://scripts/leaderboard.gd")
var current_seed: String = "all"
var current_page: int = 1
var entries_per_page: int = 20
var all_leaderboards: Dictionary = {}  # seed -> Leaderboard
var all_entries: Array = []  # All entries across all seeds
var filtered_entries: Array = []  # Current filtered/sorted view

# UI References
@onready var seed_dropdown = $MarginContainer/VBoxContainer/Filters/SeedDropdown
@onready var entries_container = $MarginContainer/VBoxContainer/LeaderboardPanel/MarginContainer/VBoxContainer/ScrollContainer/EntriesContainer
@onready var page_label = $MarginContainer/VBoxContainer/Pagination/PageLabel
@onready var prev_button = $MarginContainer/VBoxContainer/Pagination/PrevButton
@onready var next_button = $MarginContainer/VBoxContainer/Pagination/NextButton
@onready var total_games_label = $MarginContainer/VBoxContainer/Stats/TotalGames
@onready var avg_score_label = $MarginContainer/VBoxContainer/Stats/AvgScore
@onready var best_score_label = $MarginContainer/VBoxContainer/Stats/BestScore
@onready var subtitle = $MarginContainer/VBoxContainer/Header/Subtitle

func _ready():
	ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Leaderboard screen opened", {})
	_load_all_leaderboards()
	_populate_seed_dropdown()
	_filter_and_display()

func _load_all_leaderboards():
	"""Load all leaderboard files from user directory"""
	all_leaderboards.clear()
	all_entries.clear()

	var leaderboard_dir = "user://leaderboards"
	var dir = DirAccess.open(leaderboard_dir)

	if not dir:
		ErrorHandler.warning(
			ErrorHandler.Category.SAVE_LOAD,
			"Leaderboard directory not found",
			{"dir": leaderboard_dir}
		)
		return

	dir.list_dir_begin()
	var file_name = dir.get_next()

	while file_name != "":
		if file_name.ends_with(".json") and file_name.begins_with("leaderboard_"):
			# Extract seed from filename: "leaderboard_SEED.json"
			var lb_seed = file_name.substr(12, file_name.length() - 17)  # Remove "leaderboard_" and ".json"

			# Load this leaderboard
			var leaderboard = LeaderboardClass.new(lb_seed)
			all_leaderboards[lb_seed] = leaderboard

			# Add entries to combined list
			for entry in leaderboard.entries:
				all_entries.append(entry)

			ErrorHandler.info(
				ErrorHandler.Category.SAVE_LOAD,
				"Loaded leaderboard",
				{"seed": lb_seed, "entries": leaderboard.entries.size()}
			)

		file_name = dir.get_next()

	dir.list_dir_end()

	# Sort all entries by score (highest first)
	all_entries.sort_custom(func(a, b): return a.score > b.score)

	ErrorHandler.info(
		ErrorHandler.Category.SAVE_LOAD,
		"Loaded all leaderboards",
		{
			"total_seeds": all_leaderboards.size(),
			"total_entries": all_entries.size()
		}
	)

func _populate_seed_dropdown():
	"""Populate seed filter dropdown"""
	seed_dropdown.clear()
	seed_dropdown.add_item("All Seeds", 0)

	var idx = 1
	var seeds = all_leaderboards.keys()
	seeds.sort()

	for seed in seeds:
		var entry_count = all_leaderboards[seed].entries.size()
		seed_dropdown.add_item("%s (%d)" % [seed, entry_count], idx)
		seed_dropdown.set_item_metadata(idx, seed)
		idx += 1

	# Select "All Seeds" by default
	seed_dropdown.select(0)

func _filter_and_display():
	"""Filter entries based on current seed and display current page"""
	# Filter by seed
	if current_seed == "all":
		filtered_entries = all_entries.duplicate()
		subtitle.text = "Top scores across all seeds"
	else:
		filtered_entries.clear()
		if all_leaderboards.has(current_seed):
			filtered_entries = all_leaderboards[current_seed].entries.duplicate()
		subtitle.text = "Top scores for seed: %s" % current_seed

	# Reset to page 1 when filter changes
	current_page = 1

	# Display current page
	_display_current_page()
	_update_pagination_ui()
	_update_stats()

func _display_current_page():
	"""Display entries for current page"""
	# Clear existing entries
	for child in entries_container.get_children():
		child.queue_free()

	if filtered_entries.size() == 0:
		var no_entries = Label.new()
		no_entries.text = "No scores yet. Play a game to see your scores here!"
		no_entries.add_theme_font_size_override("font_size", 16)
		no_entries.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		entries_container.add_child(no_entries)
		return

	# Calculate page bounds
	var start_idx = (current_page - 1) * entries_per_page
	var end_idx = min(start_idx + entries_per_page, filtered_entries.size())

	# Display entries for this page
	for i in range(start_idx, end_idx):
		var entry = filtered_entries[i]
		var global_rank = i + 1  # Global rank in filtered list

		# Create entry row
		var entry_row = _create_entry_row(entry, global_rank)
		entries_container.add_child(entry_row)

func _create_entry_row(entry, rank: int) -> HBoxContainer:
	"""Create a styled entry row"""
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)

	# Highlight latest entry (just added from game over screen)
	var is_latest = (GameConfig.latest_leaderboard_entry != "" and
	                 entry.entry_uuid == GameConfig.latest_leaderboard_entry)

	if is_latest:
		# Add gold background panel for latest entry
		var panel = PanelContainer.new()
		var panel_style = StyleBoxFlat.new()
		panel_style.bg_color = Color(0.3, 0.25, 0.1, 0.8)  # Dark gold
		panel_style.border_width_left = 2
		panel_style.border_width_right = 2
		panel_style.border_color = Color(1.0, 0.84, 0.0, 1.0)  # Bright gold border
		panel_style.corner_radius_top_left = 4
		panel_style.corner_radius_top_right = 4
		panel_style.corner_radius_bottom_left = 4
		panel_style.corner_radius_bottom_right = 4
		row.add_theme_stylebox_override("panel", panel_style)


	# Rank container (icon + label)
	var rank_container = HBoxContainer.new()
	rank_container.custom_minimum_size = Vector2(80, 0)
	rank_container.add_theme_constant_override("separation", 4)

	# Try to get rank icon
	var rank_icon: Texture2D = null
	var rank_color = Color.WHITE

	if rank == 1:
		rank_icon = IconLoader.get_leaderboard_icon("rank_crown")
		rank_color = Color(1.0, 0.84, 0.0)  # Gold
	elif rank == 2:
		rank_icon = IconLoader.get_leaderboard_icon("rank_silver")
		rank_color = Color(0.75, 0.75, 0.75)  # Silver
	elif rank == 3:
		rank_icon = IconLoader.get_leaderboard_icon("rank_gold")
		rank_color = Color(0.8, 0.5, 0.2)  # Bronze
	elif rank <= 10:
		rank_color = Color(0.6, 0.8, 1.0)  # Light blue

	# Add icon if available
	if rank_icon:
		var icon_rect = TextureRect.new()
		icon_rect.texture = rank_icon
		icon_rect.custom_minimum_size = Vector2(20, 20)
		icon_rect.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		icon_rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		rank_container.add_child(icon_rect)

	# Rank label
	var rank_label = Label.new()
	rank_label.text = "#%d" % rank
	rank_label.add_theme_font_size_override("font_size", 14)
	rank_label.add_theme_color_override("font_color", rank_color)
	rank_container.add_child(rank_label)

	row.add_child(rank_container)

	# Player Name
	var player_label = Label.new()
	player_label.custom_minimum_size = Vector2(250, 0)
	player_label.text = entry.player_name
	player_label.add_theme_font_size_override("font_size", 14)
	player_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	row.add_child(player_label)

	# Score (Turns)
	var score_label = Label.new()
	score_label.custom_minimum_size = Vector2(100, 0)
	score_label.text = "%d" % entry.score
	score_label.add_theme_font_size_override("font_size", 14)
	row.add_child(score_label)

	# Duration
	var duration_label = Label.new()
	duration_label.custom_minimum_size = Vector2(120, 0)
	duration_label.text = _format_duration(entry.duration_seconds)
	duration_label.add_theme_font_size_override("font_size", 14)
	row.add_child(duration_label)

	# Date
	var date_label = Label.new()
	date_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	date_label.text = _format_date(entry.date)
	date_label.add_theme_font_size_override("font_size", 14)
	row.add_child(date_label)

	# Add hover effect (optional, for future enhancement)
	row.mouse_filter = Control.MOUSE_FILTER_PASS

	return row

func _format_duration(seconds: float) -> String:
	"""Format duration in human-readable format"""
	var minutes = int(seconds / 60)
	var secs = int(seconds) % 60

	if minutes > 0:
		return "%dm %ds" % [minutes, secs]
	else:
		return "%ds" % secs

func _format_date(date_string: String) -> String:
	"""Format date string to be more readable"""
	# Input format: "2025-10-31T14:30:45"
	# Output format: "Oct 31, 2025"

	if date_string.length() < 10:
		return date_string

	var parts = date_string.split("T")
	if parts.size() == 0:
		return date_string

	var date_parts = parts[0].split("-")
	if date_parts.size() != 3:
		return date_string

	var year = date_parts[0]
	var month_num = int(date_parts[1])
	var day = date_parts[2]

	var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
	var month = months[month_num - 1] if month_num >= 1 and month_num <= 12 else "???"

	return "%s %s, %s" % [month, day, year]

func _update_pagination_ui():
	"""Update pagination controls"""
	var total_pages = max(1, int(ceil(float(filtered_entries.size()) / float(entries_per_page))))

	page_label.text = "Page %d of %d" % [current_page, total_pages]

	prev_button.disabled = (current_page <= 1)
	next_button.disabled = (current_page >= total_pages)

func _update_stats():
	"""Update statistics display"""
	var entry_count = filtered_entries.size()

	total_games_label.text = "Total Games: %d" % entry_count

	if entry_count > 0:
		# Calculate average
		var total_score = 0
		for entry in filtered_entries:
			total_score += entry.score
		var avg = total_score / entry_count
		avg_score_label.text = "Avg Score: %.1f turns" % avg

		# Best score
		var best = filtered_entries[0].score if filtered_entries.size() > 0 else 0
		best_score_label.text = "Best Score: %d turns" % best
	else:
		avg_score_label.text = "Avg Score: --"
		best_score_label.text = "Best Score: --"

# Signal handlers

func _on_seed_dropdown_item_selected(index: int):
	"""Handle seed filter change"""
	if index == 0:
		current_seed = "all"
	else:
		current_seed = seed_dropdown.get_item_metadata(index)

	ErrorHandler.info(
		ErrorHandler.Category.VALIDATION,
		"Seed filter changed",
		{"seed": current_seed}
	)

	_filter_and_display()

func _on_refresh_button_pressed():
	"""Reload all leaderboards"""
	ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Refreshing leaderboards", {})
	_load_all_leaderboards()
	_populate_seed_dropdown()
	_filter_and_display()

func _on_clear_button_pressed():
	"""Clear all leaderboard scores (with confirmation)"""
	var dialog = ConfirmationDialog.new()
	dialog.dialog_text = "Are you sure you want to clear ALL leaderboard scores?\n\nThis action cannot be undone!"
	dialog.title = "Confirm Clear All"
	dialog.confirmed.connect(_perform_clear_all)
	add_child(dialog)
	dialog.popup_centered()

func _perform_clear_all():
	"""Actually clear all scores"""
	ErrorHandler.warning(
		ErrorHandler.Category.SAVE_LOAD,
		"Clearing all leaderboard scores",
		{"count": all_entries.size()}
	)

	for leaderboard in all_leaderboards.values():
		leaderboard.clear()

	# Reload
	_load_all_leaderboards()
	_populate_seed_dropdown()
	_filter_and_display()

func _on_prev_button_pressed():
	"""Go to previous page"""
	if current_page > 1:
		current_page -= 1
		_display_current_page()
		_update_pagination_ui()

func _on_next_button_pressed():
	"""Go to next page"""
	var total_pages = int(ceil(float(filtered_entries.size()) / float(entries_per_page)))
	if current_page < total_pages:
		current_page += 1
		_display_current_page()
		_update_pagination_ui()

func _on_back_button_pressed():
	"""Return to previous screen"""
	ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Exiting leaderboard screen", {})
	# Try to go back to previous scene
	if get_tree().current_scene.name == "LeaderboardScreen":
		# If launched as main scene, go to welcome
		get_tree().change_scene_to_file("res://scenes/welcome.tscn")
	else:
		# Otherwise hide this overlay
		queue_free()

func _on_play_again_button_pressed():
	"""Start a new game"""
	ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Starting new game from leaderboard", {})
	get_tree().change_scene_to_file("res://scenes/pregame_setup.tscn")

func _input(event):
	"""Handle keyboard shortcuts"""
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			_on_back_button_pressed()
		elif event.keycode == KEY_LEFT:
			_on_prev_button_pressed()
		elif event.keycode == KEY_RIGHT:
			_on_next_button_pressed()

extends Control
## Full Leaderboard Screen - Comprehensive view of all scores with filtering and pagination
##
## TODO (#743 / Pip ruling 2026-07-21): this screen becomes an "institutional records
## room" -- an archives feel with classic high-score-table callbacks (ledger/stamped
## register vibe), NOT the flat menu chrome. Deferred: the strong theme decisions here
## are downstream of the title-screen theme pass. For now it only inherits the shared
## menu_theme.tres (root Theme) so its buttons/dropdown/panel stop reading as unthemed
## default gray; the deeper records-room re-skin lands after the title screen settles.

var LeaderboardClass = preload("res://scripts/leaderboard.gd")
var current_seed: String = "all"
var current_page: int = 1
var entries_per_page: int = 20
var all_leaderboards: Dictionary = {}  # board_key -> entries Array (lazily populated)
var all_entries: Array = []  # All entries across all seeds (built lazily on the all-seeds view)
var filtered_entries: Array = []  # Current filtered/sorted view

# Lazy-open bookkeeping (perf: opening this screen used to parse EVERY seed file on
# every open -- ~5-7s with many boards). We now discover board files cheaply (a dir
# listing, no JSON parse), open only the current/most-relevant board by default, and
# parse the full cross-seed population LAZILY the first time the user picks "All Seeds"
# (cached for the rest of this screen instance). No board file is ever deleted or
# truncated -- this is a view/load change only.
var _board_files: Dictionary = {}   # board_key -> {"seed":..., "version":...}; cheap listing
var _default_key: String = ""       # newest / current board, shown on open
var _aggregate_loaded: bool = false # true once the full all-seeds scan has run this instance

# Remote/global board (LeaderboardSync). Pure view: fetched async, never on a
# deterministic path. Falls back to local silently on any failure.
var showing_global: bool = false
var global_toggle_button: Button = null

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
	# Cheap open: list board files (no parse), populate the dropdown, then show ONLY
	# the current/most-relevant board. The full all-seeds aggregate is parsed lazily
	# in _ensure_aggregate_loaded when the user selects "All Seeds".
	_discover_boards()
	_populate_seed_dropdown()
	_setup_global_toggle()
	_select_default_view()

func _exit_tree():
	# Cleanup guard: drop the working-set references the instant the screen leaves
	# the tree so the whole population of ScoreEntry objects is released now rather
	# than lingering until the node is GC'd. Combined with freeing the transient
	# Leaderboard Nodes in _load_one_board, re-opening the screen does not
	# accumulate memory across opens.
	all_leaderboards.clear()
	all_entries.clear()
	filtered_entries.clear()
	_board_files.clear()
	_aggregate_loaded = false

func _setup_global_toggle():
	"""Add a Local/Global view toggle next to the seed filter, but only when remote
	sync is enabled+configured. When off/unconfigured the screen stays local-only."""
	if not LeaderboardSync.can_fetch():
		return
	if not is_instance_valid(seed_dropdown):
		return
	var container = seed_dropdown.get_parent()
	if container == null:
		return
	global_toggle_button = Button.new()
	global_toggle_button.toggle_mode = true
	global_toggle_button.text = "View: Local"
	global_toggle_button.tooltip_text = "Toggle between your local scores and the global (online) board for this seed"
	global_toggle_button.toggled.connect(_on_global_toggle)
	container.add_child(global_toggle_button)

func _on_global_toggle(pressed: bool):
	showing_global = pressed
	if pressed:
		global_toggle_button.text = "View: Global"
		_fetch_and_show_global()
	else:
		global_toggle_button.text = "View: Local"
		_filter_and_display()

func _fetch_and_show_global():
	"""Async-fetch the global board for the CURRENT (seed, version) and show it."""
	var board_seed = GameConfig.get_display_seed()
	var version = "v" + GameConfig.CURRENT_VERSION
	subtitle.text = "Global board: fetching %s ..." % board_seed
	LeaderboardSync.fetch_board(board_seed, version, 100, _on_global_board_fetched)

func _on_global_board_fetched(ok: bool, entries: Array):
	"""Render the global board, or fall back to local silently on failure."""
	if not showing_global:
		return  # User toggled back to Local before the request resolved.
	if not ok:
		showing_global = false
		if is_instance_valid(global_toggle_button):
			global_toggle_button.set_pressed_no_signal(false)
			global_toggle_button.text = "View: Local"
		_filter_and_display()  # Silent local fallback.
		return
	filtered_entries = entries.duplicate()
	current_page = 1
	subtitle.text = "Global board: %s (v%s)" % [GameConfig.get_display_seed(), GameConfig.CURRENT_VERSION]
	_display_current_page()
	_update_pagination_ui()
	_update_stats()

func _board_key(lb_seed: String, lb_version: String) -> String:
	"""Full-identity key so same-seed/different-version boards don't collide (ADR-0002 #5)."""
	return lb_seed if lb_version == "" else "%s (%s)" % [lb_seed, lb_version]

func _discover_boards():
	"""CHEAP: list the leaderboard files and record their (seed, version) identities.

	No JSON is parsed here -- this is the part that must stay bounded so opening the
	screen is fast regardless of how many seed files have accumulated. Also picks the
	board to show on open (`_default_key`): the CURRENT (seed, version) board if it
	exists, else the most-recently-written file (the run the player just came from)."""
	_board_files.clear()
	_default_key = ""

	var leaderboard_dir = "user://leaderboards"
	var dir = DirAccess.open(leaderboard_dir)
	if not dir:
		ErrorHandler.warning(
			ErrorHandler.Category.SAVE_LOAD,
			"Leaderboard directory not found",
			{"dir": leaderboard_dir}
		)
		return

	var newest_mtime := -1
	dir.list_dir_begin()
	var file_name = dir.get_next()
	while file_name != "":
		if file_name.ends_with(".json") and file_name.begins_with("leaderboard_"):
			var identity = _parse_board_identity(file_name)
			var board_key = _board_key(identity["seed"], identity["version"])
			_board_files[board_key] = identity
			# Cheap stat (no parse) to find the newest board for the default view.
			var mtime := int(FileAccess.get_modified_time("%s/%s" % [leaderboard_dir, file_name]))
			if mtime > newest_mtime:
				newest_mtime = mtime
				_default_key = board_key
		file_name = dir.get_next()
	dir.list_dir_end()

	# Prefer the CURRENT run's board when present (it is what the player expects to see,
	# with their just-set score highlighted); otherwise keep the newest-file default.
	var current_key = _board_key(GameConfig.get_display_seed(), "v" + GameConfig.CURRENT_VERSION)
	if _board_files.has(current_key):
		_default_key = current_key

func _load_one_board(board_key: String) -> void:
	"""Parse a SINGLE board file into all_leaderboards[board_key] (cached per instance).

	MEMORY NOTE (bounded-view fix): Leaderboard `extends Node`, so an instance is NOT
	refcounted -- retaining it (as this once did) leaks one Node plus its whole entries
	array on every (re)open. We use the board only transiently to parse the file, copy
	its entries out (ScoreEntry is RefCounted and survives the free), then free() the
	Node. Entries as stored on disk are already sorted (Leaderboard.add_score sorts
	before save), so a single-seed view is correctly ordered without re-sorting."""
	if all_leaderboards.has(board_key):
		return  # already parsed this instance
	if not _board_files.has(board_key):
		all_leaderboards[board_key] = []
		return
	var identity = _board_files[board_key]
	var leaderboard = LeaderboardClass.new(identity["seed"], identity["version"])
	all_leaderboards[board_key] = leaderboard.entries.duplicate()
	ErrorHandler.info(
		ErrorHandler.Category.SAVE_LOAD,
		"Loaded leaderboard",
		{"seed": identity["seed"], "version": identity["version"], "entries": leaderboard.entries.size()}
	)
	leaderboard.free()  # transient Node -- entries already copied out.

func _ensure_aggregate_loaded() -> void:
	"""Lazily parse EVERY board file and build the sorted cross-seed population.

	Only reached when the user picks "All Seeds". Cached via _aggregate_loaded so
	toggling seed <-> all within one screen instance re-scans at most once."""
	if _aggregate_loaded:
		return
	_load_all_leaderboards()

func _load_all_leaderboards():
	"""FULL eager scan: parse every board file, populate all_leaderboards, and build the
	sorted all-seeds aggregate. This is the expensive path -- _ready no longer calls it
	(see _discover_boards + _select_default_view). It remains for Refresh, for the
	all-seeds aggregate (_ensure_aggregate_loaded), and as the entry point the
	bounded-view regression tests drive."""
	all_leaderboards.clear()
	all_entries.clear()
	_discover_boards()

	for board_key in _board_files.keys():
		_load_one_board(board_key)
		for entry in all_leaderboards[board_key]:
			all_entries.append(entry)

	# Sort lexicographically (ADR-0002): turns dominant, doom-integral tiebreak.
	all_entries.sort_custom(func(a, b): return GameState.compare_score(a.score, a.doom_integral, b.score, b.doom_integral) > 0)
	_aggregate_loaded = true

	ErrorHandler.info(
		ErrorHandler.Category.SAVE_LOAD,
		"Loaded all leaderboards",
		{
			"total_seeds": all_leaderboards.size(),
			"total_entries": all_entries.size()
		}
	)

func _parse_board_identity(file_name: String) -> Dictionary:
	"""Parse a leaderboard filename into its (seed, version) identity.

	Handles "leaderboard_SEED.json" and the version-keyed
	"leaderboard_SEED__VERSION.json" (ADR-0002 #5). The '__' delimiter survives
	hyphens/underscores in seeds. Shared by _load_all_leaderboards and
	_perform_clear_all so the two never drift."""
	var base_name = file_name.trim_prefix("leaderboard_").trim_suffix(".json")
	var lb_seed = base_name
	var lb_version = ""
	if base_name.contains("__"):
		var parts = base_name.rsplit("__", true, 1)
		lb_seed = parts[0]
		lb_version = parts[1]
	return {"seed": lb_seed, "version": lb_version}

func _populate_seed_dropdown():
	"""Populate seed filter dropdown from the discovered board files (no parse required).

	Per-seed entry counts are shown only for boards already parsed this instance -- we
	don't parse every file just to render a count (that was part of the slow open). Once
	the all-seeds aggregate loads, every board is parsed, so re-calling this fills them in.
	Selection is set by the caller (_select_default_view); select() does not emit
	item_selected, so re-populating never triggers a spurious filter change."""
	seed_dropdown.clear()
	seed_dropdown.add_item("All Seeds", 0)

	var idx = 1
	var seeds = _board_files.keys()
	seeds.sort()

	for seed in seeds:
		var label = seed
		if all_leaderboards.has(seed):
			label = "%s (%d)" % [seed, all_leaderboards[seed].size()]
		seed_dropdown.add_item(label, idx)
		seed_dropdown.set_item_metadata(idx, seed)
		idx += 1

func _select_dropdown_by_key(board_key: String) -> void:
	"""Select the dropdown row whose metadata matches board_key; fall back to All Seeds."""
	for i in range(seed_dropdown.item_count):
		if seed_dropdown.get_item_metadata(i) == board_key:
			seed_dropdown.select(i)
			return
	seed_dropdown.select(0)

func _select_default_view() -> void:
	"""Show the cheap default board on open: the current/most-relevant single seed.

	Never triggers the full all-seeds scan on open -- if there are no board files we show
	an (empty) all-seeds view, which is trivially cheap. "All Seeds" stays one click away."""
	if _default_key != "":
		current_seed = _default_key
		_select_dropdown_by_key(_default_key)
	else:
		current_seed = "all"
		seed_dropdown.select(0)
	_filter_and_display()

func _filter_and_display():
	"""Filter entries based on current seed and display current page (LOCAL view)."""
	# Any local filter action returns us to the local board.
	showing_global = false
	if is_instance_valid(global_toggle_button):
		global_toggle_button.set_pressed_no_signal(false)
		global_toggle_button.text = "View: Local"

	# Filter by seed. The all-seeds view triggers the (cached) full parse; a single seed
	# parses just that one file. Either way the population shown is complete and correctly
	# sorted -- no data is dropped, only the parse is deferred until the view needs it.
	if current_seed == "all":
		_ensure_aggregate_loaded()
		# Aggregate load repopulates counts; refresh the dropdown labels once.
		_populate_seed_dropdown()
		_select_dropdown_by_key("all")  # no metadata match -> selects "All Seeds" (index 0)
		filtered_entries = all_entries.duplicate()
		subtitle.text = "Top scores across all seeds"
	else:
		_load_one_board(current_seed)
		filtered_entries.clear()
		if all_leaderboards.has(current_seed):
			filtered_entries = all_leaderboards[current_seed].duplicate()
		subtitle.text = "Top scores for seed: %s" % current_seed

	# Reset to page 1 when filter changes
	current_page = 1

	# Display current page
	_display_current_page()
	_update_pagination_ui()
	_update_stats()

func _free_row_nodes():
	"""Free every instantiated row widget in the entries container, immediately.

	Bounded-render guarantee: at most `entries_per_page` row nodes (plus the
	empty-state label) are ever alive at once, no matter how many thousands of
	entries the population holds. We free() rather than queue_free() so the bound
	holds SYNCHRONOUSLY -- queue_free defers to end-of-frame, which would let two
	pages' worth of rows briefly coexist when paging. get_children() returns a
	copy, so freeing while iterating is safe."""
	for child in entries_container.get_children():
		entries_container.remove_child(child)
		child.free()

func _display_current_page():
	"""Display entries for current page.

	Only the current page's slice is ever instantiated as row widgets; the full
	(sorted) population lives in filtered_entries as lightweight data and is never
	turned into nodes wholesale. Paging frees the prior page first (_free_row_nodes),
	so node memory stays bounded regardless of population size."""
	# Clear existing entries (bounded: previous page's rows are freed first).
	_free_row_nodes()

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

	# Baseline comparison (Issue #372)
	var baseline_label = Label.new()
	baseline_label.custom_minimum_size = Vector2(100, 0)
	baseline_label.add_theme_font_size_override("font_size", 14)
	if entry.baseline_score > 0:
		var diff = entry.score - entry.baseline_score
		var pct = (float(entry.score) / float(entry.baseline_score) - 1.0) * 100.0
		if diff > 0:
			baseline_label.text = "+%d%%" % int(pct)
			baseline_label.add_theme_color_override("font_color", Color(0.4, 1.0, 0.4))  # Green
		elif diff < 0:
			baseline_label.text = "%d%%" % int(pct)
			baseline_label.add_theme_color_override("font_color", Color(1.0, 0.5, 0.4))  # Red
		else:
			baseline_label.text = "=base"
			baseline_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.4))  # Yellow
	else:
		baseline_label.text = "-"
		baseline_label.add_theme_color_override("font_color", Color(0.5, 0.5, 0.5))  # Gray
	row.add_child(baseline_label)

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
	"""Reload all leaderboards (explicit user action: a full re-scan is fine here)."""
	ErrorHandler.info(ErrorHandler.Category.VALIDATION, "Refreshing leaderboards", {})
	_load_all_leaderboards()
	_populate_seed_dropdown()
	_select_dropdown_by_key(current_seed)  # keep the visible selection in sync
	_filter_and_display()

func _on_clear_button_pressed():
	"""Clear the player's LOCAL saved scores (with confirmation).

	NOTE: This only wipes the local on-disk board files (user://leaderboards). The
	global/online board is untouched. If the dev later wants this button gone entirely,
	deleting the ClearButton node in leaderboard_screen.tscn plus this handler is enough."""
	var dialog = ConfirmationDialog.new()
	dialog.dialog_text = "Clear your LOCAL saved scores on this machine?\n\nThis wipes only the scores stored locally in this install. The GLOBAL (online) leaderboard is NOT affected. This cannot be undone."
	dialog.title = "Confirm Clear Local Scores"
	dialog.confirmed.connect(_perform_clear_all)
	add_child(dialog)
	dialog.popup_centered()

func _perform_clear_all():
	"""Actually clear all LOCAL scores.

	all_leaderboards now holds plain entry arrays (not Leaderboard Nodes -- see the
	memory note in _load_one_board), so we reconstruct each board transiently
	from disk to call clear(), then free() the Node. Same file set, same clear()
	semantics as before -- only the in-memory representation changed. Local only:
	the global/online board is never touched here."""
	ErrorHandler.warning(
		ErrorHandler.Category.SAVE_LOAD,
		"Clearing all leaderboard scores",
		{"count": all_entries.size()}
	)

	var dir = DirAccess.open("user://leaderboards")
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if file_name.ends_with(".json") and file_name.begins_with("leaderboard_"):
				var identity = _parse_board_identity(file_name)
				var leaderboard = LeaderboardClass.new(identity["seed"], identity["version"])
				leaderboard.clear()
				leaderboard.free()  # transient Node -- free to avoid a leak.
			file_name = dir.get_next()
		dir.list_dir_end()

	# Reload
	_load_all_leaderboards()
	_populate_seed_dropdown()
	_select_dropdown_by_key(current_seed)
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

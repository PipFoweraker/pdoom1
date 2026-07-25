class_name SubmenuController
extends RefCounted
## CARVE 2 (docs/MAIN_UI_SEAM_MAP.md, seam R5): the submenu/dialog ORCHESTRATION pulled out
## of the main_ui.gd monolith. Before this, seven near-identical `_show_*_submenu` builders +
## seven `_on_*_option_selected` handlers were copy-pasted inline (~1500 lines, the single
## biggest bloat in the view). This collapses them so the NEXT panel is a config entry, not an
## 8th copy-paste.
##
## NON-FORKING extraction (structure-only): the WHAT -- which options each submenu lists, their
## costs, and what queueing an option triggers -- is byte-for-byte identical to the pre-carve
## view. Only the HOW (one data-driven component vs seven hand-rolled functions) changed. No
## gameplay/RNG/scoring change; ladder stays L2.
##
## What it owns:
##   * open(id) -- the SINGLE entry point the view calls instead of the seven `_show_*_submenu`.
##   * GRID_CONFIG + _build_grid_submenu() -- the ONE generic icon-grid builder that fully
##     replaces the four near-identical grid builders (fundraise / publicity / strategic /
##     operations). Adding a fifth pure-grid panel is now a GRID_CONFIG entry.
##   * _build_financing_submenu() -- the financing list panel (bespoke LIST layout, not a grid),
##     kept as a sibling special-case but sharing the same mount + option-selected handler.
##   * on_option_selected() -- the ONE shared queue-an-option handler, routing through the
##     existing PlanController (CARVE 1). Was five byte-identical copies inline.
##
## What stays bespoke in the view (delegated to via open()): hiring (candidate-card pipeline,
## _build_candidate_card / onboarding) and travel (day/attention + paper/conference sections +
## sub-dialog routing). These do NOT generalize cleanly, so open() delegates back to the host's
## bespoke builder rather than forcing a lossy unification.
##
## The view keeps the LOW-LEVEL shared shell helpers it already had (_present_modal_dialog,
## _make_cost_label, _format_costs_inline, _costs_affordable, log_message, active_dialog state);
## this controller composes them. Keys are the real action_ids so the view's dispatch needs no
## translation layer.

var host  # MainUI node (untyped: avoids a class_name coupling cycle main_ui <-> controller)
var plan_controller  # PlanController (CARVE 1) -- the queue/attention/cost home

# The four pure icon-grid submenus. Everything that varied between the copy-pasted builders is
# captured here; _build_grid_submenu reads it. A new pure-grid panel == a new entry.
# name_transform: ordered [from, to] replace() pairs applied to the on-card name label (verbatim
# from the old builders). show_gains: fundraising alone appended a "Gains:" line to the tooltip.
const GRID_CONFIG := {
	"fundraise": {
		"panel_size": Vector2(420, 350), "panel_pos": Vector2(90, 80),
		"main_vbox_sep": -1,
		"header": null,
		"columns": 3, "h_sep": 8, "v_sep": 8, "btn_size": Vector2(100, 80),
		"key_labels": ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"],
		"name_transform": [[" Funding", ""], ["Publish ", ""]],
		"show_gains": true,
		"summary": {"text": "Costs vary: 0-2 Papers, 0-20 Rep", "color": Color(0.6, 0.6, 0.6)},
		"log_label": "Fundraising",
	},
	"publicity": {
		"panel_size": Vector2(420, 350), "panel_pos": Vector2(90, 80),
		"main_vbox_sep": -1,
		"header": null,
		"columns": 3, "h_sep": 8, "v_sep": 8, "btn_size": Vector2(100, 80),
		"key_labels": ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"],
		"name_transform": [[" Campaign", ""], ["Open Source ", ""]],
		"show_gains": false,
		"summary": {"text": "Build influence and public awareness", "color": Color(0.6, 0.6, 0.6)},
		"log_label": "Publicity",
	},
	"strategic": {
		"panel_size": Vector2(420, 350), "panel_pos": Vector2(90, 80),
		"main_vbox_sep": -1,
		"header": null,
		"columns": 2, "h_sep": 12, "v_sep": 12, "btn_size": Vector2(120, 90),
		"key_labels": ["Q", "W", "E", "R", "A", "S", "D", "F", "Z"],
		"name_transform": [],
		"show_gains": false,
		"summary": {"text": "High-stakes moves - use wisely!", "color": Color(1.0, 0.6, 0.3)},
		"log_label": "Strategic",
	},
	"operations": {
		"panel_size": Vector2(350, 250), "panel_pos": Vector2(90, 80),
		"main_vbox_sep": 10,
		"header": {"text": "OPERATIONS", "color": Color(0.6, 0.8, 0.6), "size": 14},
		"columns": 2, "h_sep": 12, "v_sep": 12, "btn_size": Vector2(140, 70),
		"key_labels": ["Q", "W", "E", "R"],
		"name_transform": [],
		"show_gains": false,
		"summary": null,
		"log_label": "Operations",
	},
}


func _init(host_ref, plan_ctrl) -> void:
	host = host_ref
	plan_controller = plan_ctrl


# --- Single entry point -------------------------------------------------------------------

func open(id: String) -> void:
	"""The view's one door into every submenu. Replaces the seven `_show_*_submenu()` calls.
	Grid ids build here from GRID_CONFIG; financing is a sibling list builder; hiring and travel
	are genuinely bespoke and delegate back to the host's builder (documented special-case)."""
	if GRID_CONFIG.has(id):
		_build_grid_submenu(id)
	elif id == "financing":
		_build_financing_submenu()
	elif id == "hire_staff":
		host._show_hiring_submenu()   # bespoke: candidate-card pipeline stays in the view
	elif id == "travel":
		host._show_travel_submenu()   # bespoke: paper/conference sections + sub-dialogs
	else:
		push_warning("[SubmenuController] open() unknown submenu id: %s" % id)


# --- Shared option-selected handler (was 5 byte-identical inline copies) -------------------

func on_option_selected(action_id: String, action_name: String, dialog: Control, log_label: String) -> void:
	"""Queue an option the player picked, routing through PlanController (CARVE 1). This is the
	verbatim body the fundraising / financing / publicity / strategic / operations handlers each
	copied; only the log_label prefix differed. #821: only add the UI tile when the backend
	accepts (select_action returns false on Attention overbook), so a rejected action leaves no
	phantom queue tile."""
	dialog.queue_free()
	host.active_dialog = null
	host.active_dialog_buttons = []

	var action_def = host._get_action_by_id(action_id)
	var ap_cost = action_def.get("costs", {}).get("action_points", 0)
	var available_ap = host.game_manager.state.get_available_ap()
	if available_ap < ap_cost:
		host.log_message("[color=red]Not enough AP: need %d, have %d[/color]" % [ap_cost, available_ap])
		return
	if not host.game_manager.state.can_afford(action_def.get("costs", {})):
		host.log_message("[color=red]Cannot afford: %s[/color]" % action_name)
		return
	host.log_message("[color=cyan]%s: %s[/color]" % [log_label, action_name])
	if plan_controller.select_action(action_id):
		plan_controller.queue_action(action_id, action_name)
		host.update_queued_actions_display()


# --- The one generic icon-grid builder (replaces 4 near-identical builders) ----------------

func _build_grid_submenu(id: String) -> void:
	var cfg: Dictionary = GRID_CONFIG[id]

	# Close any existing dialog first (single-active-submenu invariant).
	if host.active_dialog != null and is_instance_valid(host.active_dialog):
		host.active_dialog.queue_free()
		host.active_dialog = null
		host.active_dialog_buttons = []

	var dialog := Panel.new()
	var psize: Vector2 = cfg["panel_size"]
	dialog.custom_minimum_size = psize
	dialog.size = psize
	dialog.position = cfg["panel_pos"]

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox := VBoxContainer.new()
	if int(cfg["main_vbox_sep"]) >= 0:
		main_vbox.add_theme_constant_override("separation", int(cfg["main_vbox_sep"]))
	margin.add_child(main_vbox)

	# Optional header (operations only, among the grid four).
	if cfg["header"] != null:
		var hdr: Dictionary = cfg["header"]
		var header := Label.new()
		header.text = hdr["text"]
		header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		header.add_theme_font_size_override("font_size", int(hdr["size"]))
		header.add_theme_color_override("font_color", hdr["color"])
		main_vbox.add_child(header)

	var options: Array = _options_for(id)
	var current_state = host.game_manager.get_game_state()

	var grid := GridContainer.new()
	grid.columns = int(cfg["columns"])
	grid.add_theme_constant_override("h_separation", int(cfg["h_sep"]))
	grid.add_theme_constant_override("v_separation", int(cfg["v_sep"]))
	main_vbox.add_child(grid)

	var button_index := 0
	var buttons := []
	var key_labels: Array = cfg["key_labels"]
	var btn_size: Vector2 = cfg["btn_size"]
	var name_transform: Array = cfg["name_transform"]
	var show_gains: bool = cfg["show_gains"]
	var log_label: String = cfg["log_label"]

	for option in options:
		var opt_id = option.get("id", "")
		var opt_name = option.get("name", "")
		var opt_desc = option.get("description", "")
		var opt_costs = option.get("costs", {})

		var item_vbox := VBoxContainer.new()
		item_vbox.add_theme_constant_override("separation", 4)

		var btn := Button.new()
		btn.custom_minimum_size = btn_size
		btn.focus_mode = Control.FOCUS_NONE
		btn.mouse_filter = Control.MOUSE_FILTER_PASS

		var icon_texture = IconLoader.get_action_icon(opt_id)
		if icon_texture:
			btn.icon = icon_texture
			btn.expand_icon = true
			btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER

		var key_label = key_labels[button_index] if button_index < key_labels.size() else ""
		btn.text = key_label
		btn.add_theme_font_size_override("font_size", 10)
		btn.add_theme_color_override("font_color", Color(1, 1, 1, 0.6))

		var cost_text = host._format_costs_inline(opt_costs)
		var is_free = cost_text == "Free"

		var can_afford = host._costs_affordable(opt_costs, current_state)
		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)

		# Tooltip: fundraising alone appended a Gains line (it is the only grid submenu whose
		# options carry a money-gain range worth previewing) -- preserved verbatim.
		if show_gains:
			var opt_gains = option.get("gains", {})
			var gain_text = ""
			if opt_gains.has("money_min") and opt_gains.has("money_max"):
				gain_text = "%s-%s" % [GameConfig.format_money(opt_gains.get("money_min")), GameConfig.format_money(opt_gains.get("money_max"))]
			elif opt_gains.has("money"):
				gain_text = GameConfig.format_money(opt_gains.get("money"))
			btn.tooltip_text = "%s\n%s\n\nCosts: %s\nGains: %s" % [opt_name, opt_desc, cost_text, gain_text]
		else:
			btn.tooltip_text = "%s\n%s\n\nCosts: %s" % [opt_name, opt_desc, cost_text]

		btn.pressed.connect(func(): on_option_selected(opt_id, opt_name, dialog, log_label))

		item_vbox.add_child(btn)

		var name_label := Label.new()
		var short_name: String = opt_name
		for pair in name_transform:
			short_name = short_name.replace(pair[0], pair[1])
		name_label.text = short_name
		name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_label.add_theme_font_size_override("font_size", 10)
		name_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.8))
		item_vbox.add_child(name_label)

		var cost_label = host._make_cost_label(cost_text, is_free)
		if not can_afford:
			cost_label.modulate = Color(0.5, 0.5, 0.5)
		item_vbox.add_child(cost_label)

		grid.add_child(item_vbox)
		buttons.append(btn)
		button_index += 1

	# Optional bottom summary (all grid four except operations).
	if cfg["summary"] != null:
		var summ: Dictionary = cfg["summary"]
		var summary_label := Label.new()
		summary_label.text = summ["text"]
		summary_label.add_theme_font_size_override("font_size", 11)
		summary_label.add_theme_color_override("font_color", summ["color"])
		summary_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		main_vbox.add_child(summary_label)

	host.active_dialog = dialog
	host.active_dialog_buttons = buttons
	host._present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false


func _options_for(id: String) -> Array:
	"""Same option source each pre-carve builder used (GameActions static getters). Kept as an
	explicit match rather than a stored Callable -- these are static methods on the GameActions
	class_name, and a match is zero-ambiguity vs a Callable bound to a class object."""
	match id:
		"fundraise":
			return GameActions.get_fundraising_options()
		"publicity":
			return GameActions.get_publicity_options()
		"strategic":
			return GameActions.get_strategic_options()
		"operations":
			return GameActions.get_operations_options()
	return []


# --- Financing: bespoke LIST layout, shared mount + handler --------------------------------

func _build_financing_submenu() -> void:
	"""BL-1: the Liability Ledger financing menu (ADR-0003) -- lists the ledger trades plus a
	button that opens the full switchable ledger screen. A LIST, not an icon grid, so it is a
	sibling special-case; it still shares on_option_selected() and the modal mount. Verbatim
	move of the pre-carve _show_financing_submenu."""
	if host.active_dialog != null and is_instance_valid(host.active_dialog):
		host.active_dialog.queue_free()
		host.active_dialog = null
		host.active_dialog_buttons = []

	var dialog := Panel.new()
	dialog.custom_minimum_size = Vector2(440, 330)
	dialog.size = Vector2(440, 330)
	dialog.position = Vector2(90, 80)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 15)
	margin.add_theme_constant_override("margin_right", 15)
	margin.add_theme_constant_override("margin_top", 15)
	margin.add_theme_constant_override("margin_bottom", 15)
	dialog.add_child(margin)

	var main_vbox := VBoxContainer.new()
	main_vbox.add_theme_constant_override("separation", 6)
	margin.add_child(main_vbox)

	var title := Label.new()
	title.text = "FINANCING - every fix is a loan"
	title.add_theme_font_size_override("font_size", 13)
	title.add_theme_color_override("font_color", Color(0.85, 0.78, 0.55))
	main_vbox.add_child(title)

	var current_state = host.game_manager.get_game_state()
	var buttons := []
	var key_labels := ["Q", "W", "E", "R"]
	var idx := 0
	for option in GameActions.get_financing_options():
		var opt_id = option.get("id", "")
		var opt_name = option.get("name", "")
		var opt_costs = option.get("costs", {})
		var btn := Button.new()
		btn.focus_mode = Control.FOCUS_NONE
		btn.custom_minimum_size = Vector2(0, 44)
		var key = key_labels[idx] if idx < key_labels.size() else ""
		var cost_bits := []
		if opt_costs.get("action_points", 0) > 0:
			cost_bits.append("%d AP" % opt_costs["action_points"])
		if opt_costs.get("money", 0) > 0:
			cost_bits.append(GameConfig.format_money(opt_costs["money"]))
		var cost_txt = (" (%s)" % ", ".join(cost_bits)) if cost_bits.size() > 0 else ""
		btn.text = "[%s]  %s%s" % [key, opt_name, cost_txt]
		btn.tooltip_text = option.get("description", "")
		var can_afford = host._costs_affordable(opt_costs, current_state)
		if not can_afford:
			btn.disabled = true
			btn.modulate = Color(0.5, 0.5, 0.5)
		btn.pressed.connect(func(): on_option_selected(opt_id, opt_name, dialog, "Financing"))
		main_vbox.add_child(btn)
		buttons.append(btn)
		idx += 1

	var view_btn := Button.new()
	view_btn.focus_mode = Control.FOCUS_NONE
	view_btn.custom_minimum_size = Vector2(0, 34)
	view_btn.text = "View Ledger  >>"
	view_btn.add_theme_color_override("font_color", Color(0.7, 0.85, 0.9))
	view_btn.pressed.connect(func(): host._show_ledger_screen())
	main_vbox.add_child(view_btn)

	host.active_dialog = dialog
	host.active_dialog_buttons = buttons
	host._present_modal_dialog(dialog)
	dialog.visible = true
	dialog.z_index = 1000
	dialog.z_as_relative = false

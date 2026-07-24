class_name PlanScreen
extends VBoxContainer
## PLAN screen (BUILD_BRIEF_PLAN_WATCH_UI Lane 1) -- the strategy register: lay out the
## month before it plays. Owns the action hand, the upgrades list, and the planning verbs
## (Do-Nothing / pass). Extracted from the main_ui monolith: main_ui drives game logic
## against the public members below instead of reaching through absolute $ContentArea/...
## node paths, and ScreenModeController shows/hides this whole screen as one unit.

@onready var getting_started_hint: Label = $GettingStartedHint
@onready var actions_scroll: ScrollContainer = $ActionsScroll
@onready var actions_list: VBoxContainer = $ActionsScroll/ActionsList
@onready var upgrades_label: Label = $UpgradesLabel
@onready var upgrades_scroll: ScrollContainer = $UpgradesScroll
@onready var upgrades_list: VBoxContainer = $UpgradesScroll/UpgradesList
@onready var command_zone: VBoxContainer = $CommandZone

# The reserve/allocation gauge (ADR-0011 attention pips) -- a header strip built in code
# and mounted at the top of the screen. Refreshed each state tick via update_reserve_gauge.
var _reserve_gauge: RichTextLabel

# Transient rejection toast (playtest 2026-07-24). Built in code, mounted under the reserve
# gauge, hidden until flash_error() surfaces an action-queue rejection HERE on the PLAN screen
# (previously such errors went only to the WATCH feed, which is hidden in PLAN mode).
var _error_toast: Label
var _error_flash_seq: int = 0


func _ready() -> void:
	# Amber the upgrades label into the PLAN (strategy) register.
	upgrades_label.add_theme_color_override("font_color", TerminalTheme.AMBER_DIM)
	_build_reserve_gauge()
	_build_error_toast()


func _build_error_toast() -> void:
	_error_toast = Label.new()
	_error_toast.name = "PlanErrorToast"
	_error_toast.add_theme_color_override("font_color", Color(1.0, 0.45, 0.4))  # warm amber/red
	_error_toast.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_error_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_error_toast.visible = false
	add_child(_error_toast)
	move_child(_error_toast, 1)  # just under the reserve gauge


func flash_error(message: String) -> void:
	"""Surface an action-queue rejection (e.g. 'Not enough Attention', 'Cannot afford ...') ON
	the PLAN screen where the player is acting. Previously error_occurred routed only to the
	WATCH feed (hidden in PLAN mode), so a rejected queue attempt gave no visible feedback here
	(playtest 2026-07-24). Auto-hides after a few seconds; a newer flash supersedes an older
	one's pending hide. Pure presentation -- no sim/scene effect."""
	if _error_toast == null or message == "":
		return
	_error_toast.text = "[!] %s" % message
	_error_toast.visible = true
	_error_flash_seq += 1
	var my_seq := _error_flash_seq
	var timer := get_tree().create_timer(4.0)
	timer.timeout.connect(func() -> void:
		if is_instance_valid(_error_toast) and my_seq == _error_flash_seq:
			_error_toast.visible = false)


func _build_reserve_gauge() -> void:
	"""Header attention gauge: allocated pips vs reserved pips (BUILD_BRIEF PLAN element 1 /
	ADR-0011). A cheap, data-driven readout of the month-plan attention budget -- the honest
	scarcity made visible before you commit. Read-only view; the real numbers come from
	game_state.month_plan via update_reserve_gauge()."""
	var panel := PanelContainer.new()
	panel.name = "ReserveGauge"
	TerminalTheme.style_panel(panel, TerminalTheme.AMBER_DIM, TerminalTheme.PANEL_BG_DEEP)
	_reserve_gauge = RichTextLabel.new()
	_reserve_gauge.bbcode_enabled = true
	_reserve_gauge.fit_content = true
	_reserve_gauge.scroll_active = false
	_reserve_gauge.add_theme_font_override("normal_font", TerminalTheme.mono_font())
	_reserve_gauge.text = "[color=#a87a28]ATTENTION --[/color]"
	panel.add_child(_reserve_gauge)
	add_child(panel)
	move_child(panel, 0)


func update_reserve_gauge(state: Dictionary) -> void:
	"""Refresh the attention gauge from the live month plan. allocated * vs reserved o pips
	(ADR-0011 ~20/mo). Degrades gracefully to a dash row when no plan data is present yet."""
	if _reserve_gauge == null:
		return
	var mp: Dictionary = state.get("month_plan", {})
	var total := int(mp.get("attention_total", 0))
	var spent := int(mp.get("attention_spent", 0))
	var reserved := int(mp.get("attention_reserved", 0))
	if total <= 0:
		_reserve_gauge.text = "[color=#a87a28]ATTENTION -- plan the month[/color]"
		return
	var allocated: int = clampi(spent, 0, total)
	var held: int = clampi(reserved, 0, total - allocated)
	var free_slots: int = max(0, total - allocated - held)
	# Cap the pip render so a large budget can't overflow the strip.
	var cap := 24
	var pips := ""
	if total > cap:
		pips = "%d/%d" % [allocated, total]
	else:
		pips = "[color=#ffb833]%s[/color]" % "*".repeat(allocated)
		pips += "[color=#5cec78]%s[/color]" % "*".repeat(held)
		pips += "[color=#3a4a3a]%s[/color]" % "o".repeat(free_slots)
	_reserve_gauge.text = "[color=#a87a28]ATTENTION[/color]  %s  [color=#a87a28]- %d/%d allocated - %d reserved[/color]" % [pips, allocated, total, held]

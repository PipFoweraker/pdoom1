class_name PlanScreen
extends VBoxContainer
## PLAN screen (BUILD_BRIEF_PLAN_WATCH_UI Lane 1) — the strategy register: lay out the
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

# The reserve/allocation gauge (ADR-0011 attention pips) — a header strip built in code
# and mounted at the top of the screen. Refreshed each state tick via update_reserve_gauge.
var _reserve_gauge: RichTextLabel


func _ready() -> void:
	# Amber the upgrades label into the PLAN (strategy) register.
	upgrades_label.add_theme_color_override("font_color", TerminalTheme.AMBER_DIM)
	_build_reserve_gauge()


func _build_reserve_gauge() -> void:
	"""Header attention gauge: allocated pips vs reserved pips (BUILD_BRIEF PLAN element 1 /
	ADR-0011). A cheap, data-driven readout of the month-plan attention budget — the honest
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
	_reserve_gauge.text = "[color=#a87a28]ATTENTION —[/color]"
	panel.add_child(_reserve_gauge)
	add_child(panel)
	move_child(panel, 0)


func update_reserve_gauge(state: Dictionary) -> void:
	"""Refresh the attention gauge from the live month plan. allocated ● vs reserved ○ pips
	(ADR-0011 ~20/mo). Degrades gracefully to a dash row when no plan data is present yet."""
	if _reserve_gauge == null:
		return
	var mp: Dictionary = state.get("month_plan", {})
	var total := int(mp.get("attention_total", 0))
	var spent := int(mp.get("attention_spent", 0))
	var reserved := int(mp.get("attention_reserved", 0))
	if total <= 0:
		_reserve_gauge.text = "[color=#a87a28]ATTENTION — plan the month[/color]"
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
		pips = "[color=#ffb833]%s[/color]" % "●".repeat(allocated)
		pips += "[color=#5cec78]%s[/color]" % "◒".repeat(held)
		pips += "[color=#3a4a3a]%s[/color]" % "○".repeat(free_slots)
	_reserve_gauge.text = "[color=#a87a28]ATTENTION[/color]  %s  [color=#a87a28]· %d/%d allocated · %d reserved[/color]" % [pips, allocated, total, held]

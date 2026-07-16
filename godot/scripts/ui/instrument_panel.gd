class_name InstrumentPanel
extends VBoxContainer
## Shared instrument column (BUILD_BRIEF_PLAN_WATCH_UI Lane 1) — the always-on readouts
## that stay visible in BOTH PLAN and WATCH: the P(DOOM) gauge (with the doom trend /
## breakdown / ledger + employee affordances mounted into RightZones at runtime by main_ui),
## the staff roster, and the committed-month queue. The queue is the throughline between the
## two screens: the plan you commit in PLAN is the queue you watch execute in WATCH.
## Extracted from the main_ui monolith so the two screens embed one shared instrument set
## rather than duplicating it.

@onready var title_label: Label = $TitleZone/TitleLabel
@onready var office_cat = $CoreZone/CatZone/OfficeCat
@onready var right_zones: VBoxContainer = $CoreZone/RightZones
@onready var numeric_doom_label: Label = $CoreZone/RightZones/NumericDoomZone/NumericDoomLabel
@onready var doom_meter = $CoreZone/RightZones/DoomMeterZone/DoomMeterPanel/MarginContainer/DoomMeter
@onready var doom_meter_zone: CenterContainer = $CoreZone/RightZones/DoomMeterZone
@onready var roster_container: VBoxContainer = $EmployeeRosterZone/RosterScroll/RosterContainer
@onready var queue_panel: PanelContainer = $QueuePanel
@onready var queue_container: HBoxContainer = $QueuePanel/QueueContainer
@onready var queue_hint: Label = $QueuePanel/QueueContainer/QueueHint


func _ready() -> void:
	# Terminal-styling pass for the shared instruments (was in main_ui._setup).
	title_label.add_theme_color_override("font_color", TerminalTheme.AMBER)
	TerminalTheme.style_panel(queue_panel, TerminalTheme.RULE, TerminalTheme.PANEL_BG)

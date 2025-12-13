extends PanelContainer
class_name StaffPerksCompact
## Compact perks display for embedding in roster/main UI
## Shows researcher name, skill, equipped perks at a glance

signal expand_requested(researcher: Researcher)
signal perk_hovered(perk_name: String, description: String)
signal perk_unhovered()

@onready var name_label: Label = $VBox/Header/NameLabel
@onready var skill_label: Label = $VBox/Header/SkillLabel
@onready var tier1_slot: Panel = $VBox/PerksRow/Tier1Slot
@onready var tier2_slot: Panel = $VBox/PerksRow/Tier2Slot
@onready var tier3_slot: Panel = $VBox/PerksRow/Tier3Slot
@onready var expand_button: Button = $VBox/PerksRow/ExpandButton
@onready var spec_label: Label = $VBox/StatusRow/SpecLabel
@onready var prod_label: Label = $VBox/StatusRow/ProdLabel

var current_researcher: Researcher = null

const SPEC_COLORS = {
	"safety": Color(0.3, 0.8, 0.3),
	"capabilities": Color(0.8, 0.3, 0.3),
	"interpretability": Color(0.7, 0.3, 0.8),
	"alignment": Color(0.3, 0.7, 0.8)
}

const TIER_COLORS = {
	1: Color(0.5, 0.7, 0.9),
	2: Color(0.9, 0.7, 0.3),
	3: Color(0.8, 0.4, 0.9)
}

func _ready():
	if expand_button:
		expand_button.pressed.connect(_on_expand_pressed)

	# Setup hover for perk slots
	_setup_slot_hover(tier1_slot, 1)
	_setup_slot_hover(tier2_slot, 2)
	_setup_slot_hover(tier3_slot, 3)

func _setup_slot_hover(slot: Panel, tier: int):
	if slot:
		slot.mouse_entered.connect(_on_slot_hover.bind(slot, tier))
		slot.mouse_exited.connect(_on_slot_unhover)

func set_researcher(researcher: Researcher):
	"""Populate compact display with researcher data"""
	current_researcher = researcher

	if researcher == null:
		_show_empty()
		return

	# Name and skill
	name_label.text = researcher.researcher_name
	skill_label.text = "Lv.%d" % researcher.skill_level

	# Specialization
	var spec = researcher.specialization
	spec_label.text = spec.to_upper()
	spec_label.add_theme_color_override("font_color", SPEC_COLORS.get(spec, Color.WHITE))

	# Productivity
	var productivity = researcher.base_productivity * (1.0 - min(researcher.burnout / 200.0, 0.5))
	prod_label.text = "%.0f%%" % (productivity * 100)
	if productivity >= 1.0:
		prod_label.add_theme_color_override("font_color", Color(0.3, 0.8, 0.3))
	elif productivity >= 0.7:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.8, 0.3))
	else:
		prod_label.add_theme_color_override("font_color", Color(0.8, 0.3, 0.3))

	# Update tier slots based on skill level (simplified unlock check)
	_update_tier_slot(tier1_slot, 1, researcher.skill_level >= 3, researcher.traits)
	_update_tier_slot(tier2_slot, 2, researcher.skill_level >= 6, researcher.traits)
	_update_tier_slot(tier3_slot, 3, researcher.skill_level >= 8, researcher.traits)

func _show_empty():
	name_label.text = "Empty"
	skill_label.text = ""
	spec_label.text = "---"
	prod_label.text = "---"

func _update_tier_slot(slot: Panel, tier: int, unlocked: bool, traits: Array):
	var icon_label = slot.get_node_or_null("Icon")
	if not icon_label:
		return

	# Check if any trait matches this tier (simplified)
	var has_perk = false
	var perk_icon = "?"

	# Would check StaffPerksPanel.TIER_X_PERKS here in full implementation
	# For now, just show unlock state
	if unlocked:
		icon_label.text = "-"  # Available but not selected
		icon_label.add_theme_color_override("font_color", TIER_COLORS.get(tier, Color.WHITE).darkened(0.3))
		slot.tooltip_text = "Tier %d: Available\nClick MORE to select" % tier
	else:
		icon_label.text = "?"
		icon_label.add_theme_color_override("font_color", Color(0.4, 0.4, 0.4, 0.5))
		var req_skill = [0, 3, 6, 8][tier] if tier < 4 else 10
		slot.tooltip_text = "Tier %d: Locked\nRequires Skill %d+" % [tier, req_skill]

func _on_expand_pressed():
	expand_requested.emit(current_researcher)

func _on_slot_hover(slot: Panel, tier: int):
	var tooltip = slot.tooltip_text if slot else ""
	perk_hovered.emit("Tier %d Perk" % tier, tooltip)

func _on_slot_unhover():
	perk_unhovered.emit()

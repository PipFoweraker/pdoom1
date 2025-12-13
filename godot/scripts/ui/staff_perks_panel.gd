extends Panel
class_name StaffPerksPanel
## Modular staff perks/skills panel - can be used standalone or embedded
## Displays researcher perks in a tiered grid with preview and details

signal perk_hovered(perk_data: Dictionary)
signal perk_unhovered()
signal close_requested()

# Node references
@onready var header_label: Label = $MainLayout/LeftColumn/Header
@onready var researcher_name_label: Label = $MainLayout/CenterColumn/ResearcherPreview/VBox/NameLabel
@onready var researcher_title_label: Label = $MainLayout/CenterColumn/ResearcherPreview/VBox/TitleLabel
@onready var spec_icon_label: Label = $MainLayout/CenterColumn/ResearcherPreview/VBox/SpecIcon
@onready var perk_title_label: Label = $MainLayout/RightColumn/PerkHeader/PerkTitle
@onready var perk_tier_badge: Label = $MainLayout/RightColumn/PerkHeader/TierBadge
@onready var perk_description: RichTextLabel = $MainLayout/RightColumn/PerkDescription
@onready var requirements_list: Label = $MainLayout/RightColumn/Requirements/ReqList
@onready var close_button: Button = $CloseButton

# Equipped slot labels
@onready var equipped_slot1_name: Label = $MainLayout/LeftColumn/EquippedSection/EquippedBar/Slot1/VBox/PerkName
@onready var equipped_slot2_name: Label = $MainLayout/LeftColumn/EquippedSection/EquippedBar/Slot2/VBox/PerkName
@onready var equipped_slot3_name: Label = $MainLayout/LeftColumn/EquippedSection/EquippedBar/Slot3/VBox/PerkName

# Tier grids
@onready var tier1_grid: HBoxContainer = $MainLayout/LeftColumn/Tier1Container/Tier1Grid
@onready var tier2_grid: HBoxContainer = $MainLayout/LeftColumn/Tier2Container/Tier2Grid
@onready var tier3_grid: HBoxContainer = $MainLayout/LeftColumn/Tier3Container/Tier3Grid

# Current researcher data
var current_researcher: Researcher = null

# Specialization display config
const SPEC_COLORS = {
	"safety": Color(0.3, 0.8, 0.3),
	"capabilities": Color(0.8, 0.3, 0.3),
	"interpretability": Color(0.7, 0.3, 0.8),
	"alignment": Color(0.3, 0.7, 0.8)
}

const SPEC_ICONS = {
	"safety": "[SAFE]",
	"capabilities": "[CAPS]",
	"interpretability": "[INTRP]",
	"alignment": "[ALGN]"
}

# ============================================================================
# PERK DEFINITIONS - Tiered perk system
# ============================================================================

const TIER_1_PERKS = [
	{
		"id": "methodical",
		"name": "Methodical",
		"icon": "M",
		"description": "A careful, thorough approach to research.",
		"effects": {"research_quality": 0.10, "error_rate": -0.15},
		"requirements": {"min_skill": 3},
		"flavor": "Catches mistakes early and produces more reliable results."
	},
	{
		"id": "fast_learner",
		"name": "Fast Learner",
		"icon": "F",
		"description": "Rapidly improves skills over time.",
		"effects": {"skill_growth": 0.50},
		"requirements": {"min_skill": 3},
		"flavor": "Some people just pick things up faster than others."
	},
	{
		"id": "team_player",
		"name": "Team Player",
		"icon": "T",
		"description": "Boosts the productivity of nearby colleagues.",
		"effects": {"team_bonus": 0.10},
		"requirements": {"min_skill": 4},
		"flavor": "A rising tide lifts all boats."
	},
	{
		"id": "night_owl",
		"name": "Night Owl",
		"icon": "N",
		"description": "More productive during crunch periods.",
		"effects": {"crunch_bonus": 0.25, "burnout_rate": 0.10},
		"requirements": {"min_skill": 3},
		"flavor": "Best ideas come at 3 AM. So does the burnout."
	},
	{
		"id": "safety_conscious",
		"name": "Safety First",
		"icon": "S",
		"description": "Extra careful about AI safety implications.",
		"effects": {"doom_reduction": 0.10},
		"requirements": {"min_skill": 4, "specialization": "safety"},
		"flavor": "Always asking 'but what if it goes wrong?'"
	}
]

const TIER_2_PERKS = [
	{
		"id": "deep_focus",
		"name": "Deep Focus",
		"icon": "D",
		"description": "Extended concentration yields breakthrough insights.",
		"effects": {"research_output": 0.20, "multitask_penalty": -0.15},
		"requirements": {"min_skill": 6, "tier1_perk": true},
		"flavor": "One thing at a time, but that one thing gets done right."
	},
	{
		"id": "mentor",
		"name": "Mentor",
		"icon": "M",
		"description": "Accelerates skill growth of junior researchers.",
		"effects": {"mentee_skill_growth": 0.30},
		"requirements": {"min_skill": 6, "tier1_perk": true},
		"flavor": "Teaching is the best way to learn."
	},
	{
		"id": "publisher",
		"name": "Publisher",
		"icon": "P",
		"description": "More effective at writing and publishing papers.",
		"effects": {"paper_quality": 0.20, "reputation_on_publish": 2},
		"requirements": {"min_skill": 5, "tier1_perk": true},
		"flavor": "Knows how to frame results for maximum impact."
	},
	{
		"id": "networker",
		"name": "Networker",
		"icon": "N",
		"description": "Industry connections provide strategic advantages.",
		"effects": {"conference_bonus": 0.25, "poach_resistance": 0.15},
		"requirements": {"min_skill": 5, "tier1_perk": true},
		"flavor": "It's not what you know, it's who you know."
	},
	{
		"id": "resilient",
		"name": "Resilient",
		"icon": "R",
		"description": "Recovers quickly from setbacks and stress.",
		"effects": {"burnout_recovery": 0.30, "jet_lag_reduction": 0.25},
		"requirements": {"min_skill": 5, "tier1_perk": true},
		"flavor": "Bounces back from adversity stronger than before."
	}
]

const TIER_3_PERKS = [
	{
		"id": "visionary",
		"name": "Visionary",
		"icon": "V",
		"description": "Sees connections others miss. Unlocks special research paths.",
		"effects": {"breakthrough_chance": 0.15, "special_projects": true},
		"requirements": {"min_skill": 8, "tier2_perk": true},
		"flavor": "The kind of mind that changes fields."
	},
	{
		"id": "leader",
		"name": "Leader",
		"icon": "L",
		"description": "Inspires the entire lab. Major team-wide bonuses.",
		"effects": {"lab_productivity": 0.15, "morale_bonus": 10},
		"requirements": {"min_skill": 8, "tier2_perk": true},
		"flavor": "People want to do their best work for this person."
	},
	{
		"id": "specialist",
		"name": "Specialist",
		"icon": "S",
		"description": "Unmatched expertise in their specialization.",
		"effects": {"specialization_bonus": 0.40},
		"requirements": {"min_skill": 9, "tier2_perk": true, "turns_employed": 20},
		"flavor": "The world expert. Literally."
	},
	{
		"id": "polymath",
		"name": "Polymath",
		"icon": "P",
		"description": "Cross-disciplinary insights. Can work any specialization.",
		"effects": {"all_specializations": true, "research_versatility": 0.20},
		"requirements": {"min_skill": 8, "tier2_perk": true},
		"flavor": "Why limit yourself to one field?"
	},
	{
		"id": "sage",
		"name": "Sage",
		"icon": "W",
		"description": "Wisdom reduces lab-wide doom accumulation.",
		"effects": {"lab_doom_reduction": 0.10, "event_mitigation": 0.20},
		"requirements": {"min_skill": 9, "tier2_perk": true, "specialization": "safety"},
		"flavor": "The voice of caution that everyone actually listens to."
	}
]

# ============================================================================
# LIFECYCLE
# ============================================================================

func _ready():
	if close_button:
		close_button.pressed.connect(_on_close_pressed)

	# Setup perk button interactions
	_setup_perk_buttons()

	# Default to empty state
	_show_no_selection()

func _setup_perk_buttons():
	"""Connect all perk buttons for hover/click interactions"""
	var all_grids = [
		[tier1_grid, TIER_1_PERKS, 1],
		[tier2_grid, TIER_2_PERKS, 2],
		[tier3_grid, TIER_3_PERKS, 3]
	]

	for grid_data in all_grids:
		var grid = grid_data[0]
		var perks = grid_data[1]
		var tier = grid_data[2]

		if not grid:
			continue

		var buttons = grid.get_children()
		for i in range(min(buttons.size(), perks.size())):
			var btn = buttons[i]
			var perk = perks[i]

			# Connect hover signals
			btn.mouse_entered.connect(_on_perk_hover.bind(perk, tier))
			btn.mouse_exited.connect(_on_perk_unhover)

			# Clicking is disabled for now - just show message
			btn.pressed.connect(_on_perk_clicked.bind(perk))

# ============================================================================
# PUBLIC API
# ============================================================================

func set_researcher(researcher: Researcher):
	"""Populate panel with researcher data"""
	current_researcher = researcher

	if researcher == null:
		_show_empty_state()
		return

	# Update center preview
	var spec = researcher.specialization
	var spec_color = SPEC_COLORS.get(spec, Color.WHITE)

	researcher_name_label.text = researcher.researcher_name.to_upper()
	researcher_title_label.text = "%s | Skill %d/10" % [
		Researcher.SPECIALIZATIONS.get(spec, {}).get("name", "Researcher"),
		researcher.skill_level
	]
	spec_icon_label.text = SPEC_ICONS.get(spec, "[???]")
	spec_icon_label.add_theme_color_override("font_color", spec_color)

	# Update perk grid states based on researcher
	_update_perk_grid(tier1_grid, TIER_1_PERKS, 1, researcher)
	_update_perk_grid(tier2_grid, TIER_2_PERKS, 2, researcher)
	_update_perk_grid(tier3_grid, TIER_3_PERKS, 3, researcher)

	# Update equipped slots
	_update_equipped_slots(researcher)

	# Show default selection info
	_show_no_selection()

func _show_empty_state():
	"""Show when no researcher is selected"""
	researcher_name_label.text = "NO RESEARCHER"
	researcher_title_label.text = "Select a staff member"
	spec_icon_label.text = "[---]"
	spec_icon_label.add_theme_color_override("font_color", Color(0.4, 0.4, 0.4))

	equipped_slot1_name.text = "---"
	equipped_slot2_name.text = "---"
	equipped_slot3_name.text = "---"

	_show_no_selection()

func _show_no_selection():
	"""Default right panel state"""
	perk_title_label.text = "SELECT A PERK"
	perk_tier_badge.text = ">HOVER TO VIEW"
	perk_description.text = "[color=#888888]Hover over a perk icon to see its details.\n\nPerks are unlocked as researchers gain skill levels and experience.[/color]\n\n[color=#666666]Perk selection coming in a future update.[/color]"
	requirements_list.text = ""

# ============================================================================
# PERK GRID MANAGEMENT
# ============================================================================

func _update_perk_grid(grid: HBoxContainer, perks: Array, tier: int, researcher: Researcher):
	"""Update perk buttons based on researcher's state"""
	if not grid:
		return

	var buttons = grid.get_children()

	for i in range(min(buttons.size(), perks.size())):
		var btn = buttons[i]
		var perk = perks[i]

		var is_unlocked = _check_perk_requirements(perk, researcher)
		var is_equipped = _is_perk_equipped(perk, researcher)

		# Find icon label inside button
		var icon_label = btn.get_node_or_null("Icon")
		if not icon_label:
			icon_label = btn.get_node_or_null("LockIcon")

		if is_equipped:
			# Equipped - bright colored, checkmark
			btn.disabled = false
			btn.modulate = Color(1.0, 1.0, 1.0)
			if icon_label:
				icon_label.text = "[%s]" % perk.get("icon", "?")
				icon_label.add_theme_color_override("font_color", _get_tier_color(tier))
		elif is_unlocked:
			# Unlocked but not equipped - available
			btn.disabled = false
			btn.modulate = Color(0.8, 0.8, 0.8)
			if icon_label:
				icon_label.text = "[%s]" % perk.get("icon", "?")
				icon_label.add_theme_color_override("font_color", Color(0.6, 0.7, 0.6))
		else:
			# Locked
			btn.disabled = true
			btn.modulate = Color(0.4, 0.4, 0.4)
			if icon_label:
				icon_label.text = "[?]"
				icon_label.add_theme_color_override("font_color", Color(0.4, 0.4, 0.4, 0.6))

func _check_perk_requirements(perk: Dictionary, researcher: Researcher) -> bool:
	"""Check if researcher meets perk requirements"""
	var reqs = perk.get("requirements", {})

	# Skill level check
	if reqs.has("min_skill"):
		if researcher.skill_level < reqs["min_skill"]:
			return false

	# Specialization check
	if reqs.has("specialization"):
		if researcher.specialization != reqs["specialization"]:
			return false

	# Turns employed check
	if reqs.has("turns_employed"):
		if researcher.turns_employed < reqs["turns_employed"]:
			return false

	# Tier prerequisite checks (simplified - just check skill thresholds)
	if reqs.has("tier1_perk"):
		if researcher.skill_level < 5:  # Proxy for having tier 1
			return false

	if reqs.has("tier2_perk"):
		if researcher.skill_level < 7:  # Proxy for having tier 2
			return false

	return true

func _is_perk_equipped(perk: Dictionary, researcher: Researcher) -> bool:
	"""Check if this perk is currently equipped by the researcher"""
	# For now, use traits array as proxy for equipped perks
	return researcher.traits.has(perk.get("id", ""))

func _get_tier_color(tier: int) -> Color:
	match tier:
		1: return Color(0.5, 0.7, 0.9)  # Blue
		2: return Color(0.9, 0.7, 0.3)  # Gold
		3: return Color(0.8, 0.4, 0.9)  # Purple
		_: return Color.WHITE

func _update_equipped_slots(researcher: Researcher):
	"""Update the equipped bar at bottom"""
	# For now, show traits as "equipped perks"
	var traits = researcher.traits

	# Try to find matching perks for display
	equipped_slot1_name.text = "---"
	equipped_slot2_name.text = "---"
	equipped_slot3_name.text = "---"

	for trait_id in traits:
		# Check tier 1
		for perk in TIER_1_PERKS:
			if perk["id"] == trait_id:
				equipped_slot1_name.text = perk["name"].to_upper()
				equipped_slot1_name.add_theme_color_override("font_color", _get_tier_color(1))
		# Check tier 2
		for perk in TIER_2_PERKS:
			if perk["id"] == trait_id:
				equipped_slot2_name.text = perk["name"].to_upper()
				equipped_slot2_name.add_theme_color_override("font_color", _get_tier_color(2))
		# Check tier 3
		for perk in TIER_3_PERKS:
			if perk["id"] == trait_id:
				equipped_slot3_name.text = perk["name"].to_upper()
				equipped_slot3_name.add_theme_color_override("font_color", _get_tier_color(3))

# ============================================================================
# INTERACTION HANDLERS
# ============================================================================

func _on_perk_hover(perk: Dictionary, tier: int):
	"""Show perk details on hover"""
	var tier_names = {1: "FOUNDATION", 2: "SPECIALIZATION", 3: "MASTERY"}

	perk_tier_badge.text = ">TIER %d  %s" % [tier, tier_names.get(tier, "")]
	perk_tier_badge.add_theme_color_override("font_color", _get_tier_color(tier))

	perk_title_label.text = perk.get("name", "Unknown").to_upper()

	# Build description with effects
	var desc_text = "[color=#88cc88]%s[/color]\n\n" % perk.get("description", "")

	var effects = perk.get("effects", {})
	for effect_key in effects.keys():
		var value = effects[effect_key]
		var formatted_key = effect_key.replace("_", " ").capitalize()
		if value is bool:
			desc_text += "- [color=#aaddaa]%s[/color]: Yes\n" % formatted_key
		elif value is float:
			var sign_str = "+" if value >= 0 else ""
			desc_text += "- [color=#aaddaa]%s[/color]: %s%.0f%%\n" % [formatted_key, sign_str, value * 100]
		else:
			desc_text += "- [color=#aaddaa]%s[/color]: %s\n" % [formatted_key, value]

	desc_text += "\n[color=#888888]%s[/color]" % perk.get("flavor", "")

	perk_description.text = desc_text

	# Build requirements list
	var reqs = perk.get("requirements", {})
	var req_text = ""

	if reqs.has("min_skill"):
		var met = current_researcher and current_researcher.skill_level >= reqs["min_skill"]
		req_text += "[%s] Skill Level %d+\n" % ["x" if met else " ", reqs["min_skill"]]

	if reqs.has("specialization"):
		var met = current_researcher and current_researcher.specialization == reqs["specialization"]
		req_text += "[%s] %s Specialization\n" % ["x" if met else " ", reqs["specialization"].capitalize()]

	if reqs.has("turns_employed"):
		var met = current_researcher and current_researcher.turns_employed >= reqs["turns_employed"]
		req_text += "[%s] %d+ turns employed\n" % ["x" if met else " ", reqs["turns_employed"]]

	if reqs.has("tier1_perk"):
		req_text += "[ ] Tier 1 perk equipped\n"

	if reqs.has("tier2_perk"):
		req_text += "[ ] Tier 2 perk equipped\n"

	requirements_list.text = req_text

	# Emit signal for external info bar
	perk_hovered.emit(perk)

func _on_perk_unhover():
	"""Reset to default state"""
	_show_no_selection()
	perk_unhovered.emit()

func _on_perk_clicked(perk: Dictionary):
	"""Handle perk click - currently disabled"""
	# For now, just emit hover signal to show in info bar
	print("[StaffPerksPanel] Perk clicked (interaction coming soon): %s" % perk.get("name", ""))

func _on_close_pressed():
	"""Handle close button"""
	close_requested.emit()
	hide()

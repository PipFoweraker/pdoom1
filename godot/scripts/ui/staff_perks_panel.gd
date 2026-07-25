extends Panel
class_name StaffPerksPanel
## Staff ID card / DOSSIER (feat/quirk-skeleton). The old tiered perk grid this panel
## carried (TIER_1/2/3_PERKS, 15 perks) was DEAD content -- `_is_perk_equipped` always
## returned false and no sim system ever read a perk. The quirk catalogue
## (res://data/researchers/quirks.json) is the LIVE system, so the card now shows what
## the sim actually simulates: quirk (exposure-gated), appetites (reveal-gated),
## loyalty/tenure disposition, and a model-formula readout. The perks' flavour was
## harvested to docs/game-design/PERK_FLAVOUR_HARVEST.md before deletion.
## Quirk icon art for these surfaces: issue #903.

signal close_requested()

# Node references
@onready var header_label: Label = $MainLayout/LeftColumn/Header
@onready var quirk_name_label: Label = $MainLayout/LeftColumn/QuirkSection/QuirkSlot/QuirkMargin/QuirkVBox/QuirkName
@onready var quirk_flavour_label: Label = $MainLayout/LeftColumn/QuirkSection/QuirkSlot/QuirkMargin/QuirkVBox/QuirkFlavour
@onready var appetites_list: VBoxContainer = $MainLayout/LeftColumn/AppetiteSection/AppetitesSlot/AppetitesMargin/AppetitesList
@onready var disposition_text: Label = $MainLayout/LeftColumn/DispositionSection/DispositionSlot/DispositionMargin/DispositionText
@onready var researcher_name_label: Label = $MainLayout/CenterColumn/ResearcherPreview/VBox/NameLabel
@onready var researcher_title_label: Label = $MainLayout/CenterColumn/ResearcherPreview/VBox/TitleLabel
@onready var spec_icon_label: Label = $MainLayout/CenterColumn/ResearcherPreview/VBox/SpecIcon
@onready var detail_text: RichTextLabel = $MainLayout/RightColumn/DetailText
@onready var close_button: Button = $CloseButton

# Current researcher data
var current_researcher: Researcher = null

# Specialization display config (ASCII chrome, house style)
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

const QUIRK_KNOWN_COLOR := Color(0.78, 0.72, 0.54)
const QUIRK_UNKNOWN_COLOR := Color(0.45, 0.5, 0.45)

# Human labels for the quirk effect channels (shown in the readout once the quirk is
# known; keys per RESEARCHER_QUIRKS.md "Effect channels").
const EFFECT_LABELS = {
	"self_productivity_mult": "Own output",
	"burnout_per_turn_add": "Burnout drift",
	"doom_mod_add": "Risk disposition",
	"leak_chance": "Leak risk",
	"team_productivity_add": "Team effect",
	"skill_growth_mult": "Learning rate",
	"loyalty_per_turn_add": "Loyalty drift",
}

# ============================================================================
# LIFECYCLE
# ============================================================================

func _ready():
	if close_button:
		close_button.pressed.connect(_on_close_pressed)
	_show_empty_state()

# ============================================================================
# PUBLIC API
# ============================================================================

func set_researcher(researcher: Researcher):
	"""Populate the dossier from a full Researcher (callers rebuild via from_dict so the
	quirk/appetite layer is present -- see EmployeePanel._researcher_from_data)."""
	current_researcher = researcher

	if researcher == null:
		_show_empty_state()
		return

	# --- Center preview (unchanged look) ---
	var spec = researcher.specialization
	var spec_color = SPEC_COLORS.get(spec, Color.WHITE)
	researcher_name_label.text = researcher.researcher_name.to_upper()
	researcher_title_label.text = "%s | Skill %d/10" % [
		Researcher.SPECIALIZATIONS.get(spec, {}).get("name", "Researcher"),
		researcher.skill_level
	]
	spec_icon_label.text = SPEC_ICONS.get(spec, "[???]")
	spec_icon_label.add_theme_color_override("font_color", spec_color)

	_update_quirk_section(researcher)
	_update_appetites(researcher)
	_update_disposition(researcher)
	_update_readout(researcher)

func _show_empty_state():
	"""Shown when no researcher is selected."""
	researcher_name_label.text = "NO RESEARCHER"
	researcher_title_label.text = "Select a staff member"
	spec_icon_label.text = "[---]"
	spec_icon_label.add_theme_color_override("font_color", Color(0.4, 0.4, 0.4))
	quirk_name_label.text = "---"
	quirk_flavour_label.text = ""
	disposition_text.text = "---"
	detail_text.text = "[color=#888888]Select a staff member to open their dossier.[/color]"
	_clear_appetites()

# ============================================================================
# SECTIONS
# ============================================================================

func _update_quirk_section(researcher: Researcher) -> void:
	"""Exposure-gated (A2 contract): a hidden quirk and no quirk read IDENTICALLY --
	the card must never leak that a rider exists before an exposure surfaces it."""
	if researcher.quirk_known:
		if researcher.quirk != "":
			quirk_name_label.text = QuirkCatalogue.display_name(researcher.quirk)
			quirk_name_label.add_theme_color_override("font_color", QUIRK_KNOWN_COLOR)
			quirk_flavour_label.text = QuirkCatalogue.flavour(researcher.quirk)
		else:
			quirk_name_label.text = "None on file"
			quirk_name_label.add_theme_color_override("font_color", QUIRK_UNKNOWN_COLOR)
			quirk_flavour_label.text = "A checked absence. Genuinely unremarkable."
	else:
		quirk_name_label.text = "Nothing observed (yet)"
		quirk_name_label.add_theme_color_override("font_color", QUIRK_UNKNOWN_COLOR)
		quirk_flavour_label.text = "People reveal themselves in time. Keep watching."

func _clear_appetites() -> void:
	for child in appetites_list.get_children():
		child.queue_free()

func _update_appetites(researcher: Researcher) -> void:
	"""Reveal-gated: direct hires are fully revealed on employment; a BLIND pipeline hire
	keeps its hidden layer (the scouting gamble), so unrevealed appetites stay masked."""
	_clear_appetites()
	var revealed := researcher.is_field_revealed("appetites")
	for key in Researcher.APPETITE_KEYS:
		var row := Label.new()
		row.add_theme_font_size_override("font_size", 11)
		var pretty := String(key).replace("_", " ")
		if revealed:
			var v := float(researcher.appetites.get(key, 0.0))
			row.text = "%-14s %s %3d%%" % [pretty, _ascii_bar(v), int(round(v * 100.0))]
			row.add_theme_color_override("font_color",
				Color(0.85, 0.8, 0.6) if v >= Researcher.APPETITE_HUNGRY_THRESHOLD else Color(0.65, 0.7, 0.65))
		else:
			row.text = "%-14s %s" % [pretty, Researcher.HIDDEN_PLACEHOLDER]
			row.add_theme_color_override("font_color", Color(0.45, 0.5, 0.45))
		appetites_list.add_child(row)

func _update_disposition(researcher: Researcher) -> void:
	var lines: Array[String] = []
	lines.append("Loyalty  %s %3d/100" % [_ascii_bar(researcher.loyalty / 100.0), researcher.loyalty])
	lines.append("Tenure   %d turn%s" % [researcher.turns_employed, "" if researcher.turns_employed == 1 else "s"])
	lines.append("Salary   %s/yr (expects %s)" % [
		GameConfig.format_money(researcher.current_salary),
		GameConfig.format_money(researcher.salary_expectation)])
	disposition_text.text = "\n".join(lines)

func _update_readout(researcher: Researcher) -> void:
	"""Right-column readout: the MODEL's numbers (get_effective_productivity is the one
	burnout/quirk/onboarding formula -- no UI re-derivation), plus quirk mechanics once known."""
	var t := ""
	t += "[color=#88cc88]Effective productivity: %d%%[/color]\n" % int(round(researcher.get_effective_productivity() * 100.0))
	t += "Burnout: %d%%%s\n" % [int(researcher.burnout), "  [color=orange][!][/color]" if researcher.is_burned_out() else ""]
	if researcher.has_jet_lag():
		t += "[color=#aaaacc]%s[/color]\n" % researcher.get_jet_lag_status()
	if not researcher.onboarded:
		t += "[color=orange]Onboarding incomplete -- barely productive.[/color]\n"
	elif researcher.mentoring_skipped:
		t += "[color=#aa8866]Mentoring was skimped -- lasting debuff.[/color]\n"
	if researcher.quirk_known and researcher.quirk != "":
		t += "\n[color=#c8b98a][b]%s[/b][/color]\n" % QuirkCatalogue.display_name(researcher.quirk)
		var effects: Dictionary = QuirkCatalogue.get_def(researcher.quirk).get("effects", {})
		for key in effects.keys():
			t += "- [color=#aaddaa]%s[/color]: %s\n" % [
				EFFECT_LABELS.get(key, String(key).replace("_", " ").capitalize()),
				_format_effect(String(key), effects[key])]
	else:
		t += "\n[color=#888888]No quirk on record. Time and incidents tell.[/color]\n"
	detail_text.text = t

# ============================================================================
# HELPERS
# ============================================================================

func _ascii_bar(value: float, width: int = 10) -> String:
	"""House-style ASCII meter: [#####-----]."""
	var filled: int = clampi(int(round(clampf(value, 0.0, 1.0) * width)), 0, width)
	return "[%s%s]" % ["#".repeat(filled), "-".repeat(width - filled)]

func _format_effect(key: String, value) -> String:
	"""Deadpan mechanical phrasing per channel. Deliberately NO doom numbers -- the risk
	disposition reads as a direction, not a printed doom figure (ADR-0015 fiction rules)."""
	match key:
		"self_productivity_mult", "skill_growth_mult":
			var pct := int(round((float(value) - 1.0) * 100.0))
			return "%+d%%" % pct
		"team_productivity_add":
			return "%+d%% to the whole team" % int(round(float(value) * 100.0))
		"burnout_per_turn_add":
			return "%+.1f/turn" % float(value)
		"leak_chance":
			return "%d%% per turn" % int(round(float(value) * 100.0))
		"loyalty_per_turn_add":
			return "%+d/turn" % int(value)
		"doom_mod_add":
			return "raises it" if float(value) > 0.0 else "lowers it"
		_:
			return str(value)

# ============================================================================
# INTERACTION HANDLERS
# ============================================================================

func _on_close_pressed():
	"""Handle close button"""
	close_requested.emit()
	hide()


func _unhandled_input(event: InputEvent) -> void:
	# Escape contract (fix/ui-no-dead-ends): Esc closes the panel, matching the [X]
	# button, so the keyboard path is never a dead-end.
	if visible and event.is_action_pressed("ui_cancel"):
		_on_close_pressed()
		get_viewport().set_input_as_handled()

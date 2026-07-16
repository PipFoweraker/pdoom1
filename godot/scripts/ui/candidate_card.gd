extends PanelContainer
class_name CandidateCard
## Minimal Phase-A candidate / employee card (BUILD_BRIEF_HIRING_PIPELINE "Phase A").
##
## PURE VIEW: it renders Researcher.get_card_data() and never mutates the model. Revealed
## fields show their true value; fields above the current reveal_level (and an unexposed
## quirk) render as "??? (interview to reveal)" -- hire-as-scouting made visible (ADR-0004).
## The data model (Researcher) is the real deliverable; this is a deliberately thin view
## the Phase-B plan screen can replace or embed.

var _title: Label
var _body: Label
var _researcher: Researcher

func _ready() -> void:
	if _body == null:
		_build()

func _build() -> void:
	var vbox := VBoxContainer.new()
	add_child(vbox)
	_title = Label.new()
	_title.add_theme_font_size_override("font_size", 16)
	vbox.add_child(_title)
	_body = Label.new()
	vbox.add_child(_body)
	if _researcher != null:
		_refresh()

## Point the card at a Researcher (candidate or employee). Re-render is immediate.
func set_researcher(r: Researcher) -> void:
	_researcher = r
	if _body == null:
		_build()
	else:
		_refresh()

func _refresh() -> void:
	if _researcher == null:
		_title.text = "(no candidate)"
		_body.text = ""
		return
	var c: Dictionary = _researcher.get_card_data()
	_title.text = "%s  [%s]" % [c["name"], c["hire_state"]]
	_body.text = _researcher.get_card_text()

extends Control
## The conference mini-scene -- the tempo pocket (ADR-0014 shell, Pip ruling 2026-07-27).
##
## FIDELITY: option 1 from the design seed (text vignette), chosen for this pass. The seed
## recommends option 2 (an illustrated tableau with 2-4 hotspots) as the sweet spot -- the
## visual context-switch IS the break. This scene is deliberately structured so that upgrade
## is a re-skin: BEATS below drives a generic staged reveal, so a tableau backdrop and
## hotspots can be layered in without touching the sim seam or the navigation contract.
##
## SAFETY / SCOPE (the same contract cold_open_sequence.gd keeps, and ADR-0018's arrow):
##  * PURE PRESENTATION. The away window was ALREADY resolved synchronously by
##    ConferenceTrip.run_trip() before this scene loaded. Nothing here reads or writes the
##    simulation, draws RNG, or can influence the outcome -- it renders a decided result.
##  * ALL navigation goes through the SceneTransition autoload (the v0.11.0 segfault rule,
##    enforced by tools/check_scene_nav.py). Never change_scene_to_file.
##  * The return backlog is NOT shown here. It belongs to the office, on return, as ONE
##    panel (feed-channel discipline; see main_ui._show_conference_backlog).

const MAIN_SCENE := "res://scenes/main.tscn"

# --- Timing dials (seconds) -- Pip edits pacing here, in one place. ---
const LINE_FADE_IN := 0.7
const LINE_HOLD := 2.6
const HEADER_FADE_IN := 0.9
const OPENING_BLACK_HOLD := 0.4

var _trip: Dictionary = {}
var _lines: Array = []
var _line_index: int = 0
var _finished_reveal: bool = false
var _leaving: bool = false

var _body: VBoxContainer
var _lines_box: VBoxContainer
var _return_button: Button
var _skip_hint: Label
var _active_tween: Tween


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_trip = _read_trip()
	_build_ui()
	set_process_unhandled_input(true)
	await get_tree().create_timer(OPENING_BLACK_HOLD).timeout
	_reveal_next_line()


func _read_trip() -> Dictionary:
	"""The trip record produced at commit time. Read-only handoff -- if it is missing (scene
	opened directly, e.g. from the editor), fall back to an empty record and still offer the
	way back, so this scene can never trap a player."""
	var gm := get_node_or_null("/root/GameManager")
	if gm != null and gm.get("last_conference_trip") != null:
		var t = gm.last_conference_trip
		if t is Dictionary:
			return t
	return {}


func _conference() -> Dictionary:
	var conf = _trip.get("conference", {})
	return conf if conf is Dictionary else {}


func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.color = Color(0.04, 0.05, 0.06)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)

	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 120)
	margin.add_theme_constant_override("margin_right", 120)
	margin.add_theme_constant_override("margin_top", 90)
	margin.add_theme_constant_override("margin_bottom", 70)
	add_child(margin)

	_body = VBoxContainer.new()
	_body.add_theme_constant_override("separation", 18)
	_body.alignment = BoxContainer.ALIGNMENT_CENTER
	margin.add_child(_body)

	var conf := _conference()
	var title := Label.new()
	title.text = String(conf.get("name", "Away"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 34)
	title.add_theme_color_override("font_color", Color(0.85, 0.72, 0.35))
	title.modulate.a = 0.0
	_body.add_child(title)

	var subtitle := Label.new()
	subtitle.text = _away_summary()
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.add_theme_font_size_override("font_size", 15)
	subtitle.add_theme_color_override("font_color", Color(0.55, 0.58, 0.6))
	subtitle.modulate.a = 0.0
	_body.add_child(subtitle)

	var rule := HSeparator.new()
	_body.add_child(rule)

	_lines_box = VBoxContainer.new()
	_lines_box.add_theme_constant_override("separation", 22)
	_body.add_child(_lines_box)

	_skip_hint = Label.new()
	_skip_hint.text = "[ click or press any key to skip ahead ]"
	_skip_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_skip_hint.add_theme_font_size_override("font_size", 12)
	_skip_hint.add_theme_color_override("font_color", Color(0.35, 0.37, 0.4))
	_body.add_child(_skip_hint)

	_return_button = Button.new()
	_return_button.text = "Return to the office  >>"
	_return_button.custom_minimum_size = Vector2(280, 44)
	_return_button.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	_return_button.visible = false
	_return_button.pressed.connect(_leave)
	_body.add_child(_return_button)

	_lines = _collect_lines(conf)

	_fade_in_control(title, HEADER_FADE_IN)
	_fade_in_control(subtitle, HEADER_FADE_IN)


func _collect_lines(conf: Dictionary) -> Array:
	var out: Array = []
	var blurb := String(conf.get("blurb", ""))
	if not blurb.is_empty():
		out.append(blurb)
	for line in conf.get("vignette", []):
		out.append(String(line))
	# The one line that must SURPRISE (seed section 5: a boring auto-resolve turns the break
	# into a wait-state). Cut-short trips say so here rather than silently ending early.
	if bool(_trip.get("cut_short", false)):
		out.append("Then the phone goes. %s You are on the next flight home."
			% String(_trip.get("cut_short_reason", "Something at the lab could not wait.")))
	var memento = _trip.get("memento", {})
	if memento is Dictionary:
		var contact = memento.get("contact", {})
		if contact is Dictionary and not contact.is_empty():
			out.append("You leave with a name you did not have on the way out: %s."
				% String(contact.get("name", "someone")))
	if out.is_empty():
		out.append("A few days elsewhere. The work waits.")
	return out


func _away_summary() -> String:
	var resolved := int(_trip.get("ticks_resolved", 0))
	var attention := int(_trip.get("attention_consumed", 0))
	if resolved <= 0:
		return "Away."
	return "%d days away  |  %d Attention consumed  |  the lab runs on the standing plan" % [
		resolved, attention]


# ---------------------------------------------------------------------------
# Staged reveal
# ---------------------------------------------------------------------------
func _reveal_next_line() -> void:
	if _leaving:
		return
	if _line_index >= _lines.size():
		_finish_reveal()
		return
	var label := Label.new()
	label.text = String(_lines[_line_index])
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", 19)
	label.add_theme_color_override("font_color", Color(0.82, 0.84, 0.86))
	label.modulate.a = 0.0
	_lines_box.add_child(label)
	_line_index += 1
	_fade_in_control(label, LINE_FADE_IN)
	await get_tree().create_timer(LINE_FADE_IN + LINE_HOLD).timeout
	_reveal_next_line()


func _reveal_all_now() -> void:
	"""Skip: dump every remaining line at once, then offer the way back."""
	while _line_index < _lines.size():
		var label := Label.new()
		label.text = String(_lines[_line_index])
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		label.add_theme_font_size_override("font_size", 19)
		label.add_theme_color_override("font_color", Color(0.82, 0.84, 0.86))
		_lines_box.add_child(label)
		_line_index += 1
	_finish_reveal()


func _finish_reveal() -> void:
	if _finished_reveal:
		return
	_finished_reveal = true
	_skip_hint.visible = false
	_return_button.visible = true
	_return_button.grab_focus()


func _fade_in_control(node: CanvasItem, duration: float) -> void:
	var tween := create_tween()
	tween.tween_property(node, "modulate:a", 1.0, duration)


func _unhandled_input(event: InputEvent) -> void:
	if _leaving:
		return
	var pressed: bool = (event is InputEventKey and event.pressed and not event.echo) \
		or (event is InputEventMouseButton and event.pressed)
	if not pressed:
		return
	if _finished_reveal:
		_leave()
	else:
		_reveal_all_now()
	get_viewport().set_input_as_handled()


# ---------------------------------------------------------------------------
# Exit -- ALWAYS through SceneTransition (never change_scene_to_file; v0.11.0 rule)
# ---------------------------------------------------------------------------
func _leave() -> void:
	if _leaving:
		return
	_leaving = true
	# Tell main.tscn to RESUME the live run instead of booting a new one. Without this flag
	# main_ui._boot_game() would start_new_game() and destroy the run on re-entry.
	var gm := get_node_or_null("/root/GameManager")
	if gm != null:
		gm.pending_resume = true
	print("[ConferenceVignette] returning to the office (turn %d)" % int(_trip.get("end_turn", 0)))
	SceneTransition.go_to(MAIN_SCENE, true)

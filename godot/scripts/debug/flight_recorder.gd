extends CanvasLayer
class_name FlightRecorder
## Playtest "flight recorder" — WORKSHOP_2_BACKLOG "Playtest deep-dive protocol":
## a couple of comprehensively logged human run-throughs, reviewed as a unit. One
## press of F9 (the `flight_recorder` keybind) dumps, into a timestamped session
## directory under user://, everything needed to reconstruct "what did Pip see and
## think, right here": (a) a screenshot, (b) a JSON state snapshot — reusing
## GameState.to_dict(), the SAME serializer save/load uses, not a parallel one —
## and (c) an auto-incrementing marker id + an optional short note, also appended
## to one session manifest.jsonl so the whole run can be replayed as a timeline.
##
## Dev-build only (BuildInfo.is_dev_build(), same gate as DevModeOverlay); zero
## effect on normal play when gated off. Registered the same way as the DEV MODE
## overlay: a signal on KeybindManager, connected here, built in code (no .tscn).
##
## Pause semantics: this engine has no continuous auto-advance — MonthController
## only steps forward via an explicit advance_tick() call triggered by player input
## (End Turn / End Month). So capturing state never races a turn resolving on its
## own. The one place a press CAN'T be instantaneous is the note popup: while it
## waits for Enter/Esc, the full-rect modal (MOUSE_FILTER_STOP) blocks the game's
## own buttons the same way any other modal dialog in this codebase does — this is
## normal input-blocking, not a second pause mechanism layered on top of
## MonthController's. If MonthController is already mid a window pause
## (`month_controller.is_paused()`), the capture simply operates on that
## already-halted state; nothing extra is needed there either.

const SESSION_ROOT := "user://flight_recorder"
## Above the DEV MODE overlay (150) so the note popup is never hidden behind it,
## below the DEV BUILD badge (200).
const OVERLAY_LAYER := 180

## Reference to the MainUI node so the live GameManager/state can be resolved
## the same way DevModeOverlay does (main_ui.gd wires this at instantiation).
var main_ui: Node = null

var session_dir: String = ""
var marker_count: int = 0
var _built := false
var _root: Control = null
var _note_edit: LineEdit = null
var _pending: Dictionary = {}


# --- Live-manager resolution (mirrors dev_mode_overlay.gd's _live_gm) -------

func _live_gm() -> Node:
	if main_ui != null:
		var gm = main_ui.get("game_manager")
		if gm != null:
			return gm
	return GameManager


func _ready() -> void:
	layer = OVERLAY_LAYER
	if not BuildInfo.is_dev_build():
		visible = false
		return
	_build_note_popup()
	_built = true
	if is_instance_valid(KeybindManager):
		KeybindManager.flight_recorder_requested.connect(_on_capture_requested)


# --- Pure helpers (unit-tested without a live viewport/GameManager) --------

## Reuse the save-serialization path — do NOT hand-roll a parallel serializer.
static func build_state_snapshot(state) -> Dictionary:
	if state == null:
		return {}
	return state.to_dict()


## Zero-padded marker id + timestamp, chosen so a press's three files
## (…_note.txt, …_screenshot.png, …_state.json) sort adjacently by filename.
static func marker_prefix(marker_id: int, timestamp: Dictionary) -> String:
	return "%04d_%04d%02d%02d_%02d%02d%02d" % [
		marker_id,
		int(timestamp.get("year", 0)), int(timestamp.get("month", 0)), int(timestamp.get("day", 0)),
		int(timestamp.get("hour", 0)), int(timestamp.get("minute", 0)), int(timestamp.get("second", 0)),
	]


static func session_dir_name(timestamp: Dictionary) -> String:
	return "session_%04d%02d%02d_%02d%02d%02d" % [
		int(timestamp.get("year", 0)), int(timestamp.get("month", 0)), int(timestamp.get("day", 0)),
		int(timestamp.get("hour", 0)), int(timestamp.get("minute", 0)), int(timestamp.get("second", 0)),
	]


static func build_manifest_entry(marker_id: int, note: String, state, prefix: String) -> Dictionary:
	return {
		"marker_id": marker_id,
		"turn": (state.turn if state != null else -1),
		"note": note,
		"files": {
			"note": prefix + "_note.txt",
			"screenshot": prefix + "_screenshot.png",
			"state": prefix + "_state.json",
		},
	}


# --- Capture flow ------------------------------------------------------------

func _on_capture_requested() -> void:
	if not _built:
		return
	var gm := _live_gm()
	if gm == null or gm.get("state") == null:
		return
	_capture(gm.state)


func _capture(state) -> void:
	_ensure_session_dir()
	marker_count += 1
	var timestamp := Time.get_datetime_dict_from_system()
	var prefix := marker_prefix(marker_count, timestamp)

	# (a) Screenshot
	var image := get_viewport().get_texture().get_image()
	var screenshot_path := session_dir.path_join(prefix + "_screenshot.png")
	var shot_err := image.save_png(screenshot_path)
	if shot_err != OK:
		push_error("[FlightRecorder] Failed to save screenshot: %s" % shot_err)

	# (b) JSON state snapshot — GameState.to_dict(), the save/load serializer.
	var snapshot := build_state_snapshot(state)
	var state_path := session_dir.path_join(prefix + "_state.json")
	var sf := FileAccess.open(state_path, FileAccess.WRITE)
	if sf != null:
		sf.store_string(JSON.stringify(snapshot, "\t"))
		sf.close()
	else:
		push_error("[FlightRecorder] Failed to open state snapshot for writing: %s" % state_path)

	# (c) Marker id + optional note — collected via the popup, then appended
	# to the manifest once the player presses Enter/Esc.
	_pending = {"prefix": prefix, "marker_id": marker_count, "state": state}
	_show_note_popup()


func _ensure_session_dir() -> void:
	if session_dir != "":
		return
	var timestamp := Time.get_datetime_dict_from_system()
	var name := session_dir_name(timestamp)
	session_dir = SESSION_ROOT.path_join(name)
	DirAccess.make_dir_recursive_absolute(session_dir)
	# Print the absolute path on first use so a playtester can find the session
	# without hunting for Godot's user:// mapping.
	var abs_path := OS.get_user_data_dir().path_join("flight_recorder").path_join(name)
	print("[FlightRecorder] Session directory: %s" % abs_path)


func _append_manifest(entry: Dictionary) -> void:
	var path := session_dir.path_join("manifest.jsonl")
	var existing := ""
	if FileAccess.file_exists(path):
		var rf := FileAccess.open(path, FileAccess.READ)
		if rf != null:
			existing = rf.get_as_text()
			rf.close()
	var wf := FileAccess.open(path, FileAccess.WRITE)
	if wf != null:
		wf.store_string(existing + JSON.stringify(entry) + "\n")
		wf.close()


# --- Note popup UI (tiny textbox, Enter to save, Esc to skip) --------------

func _build_note_popup() -> void:
	_root = Control.new()
	_root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# Blocks clicks to the game behind it while the note prompt is up — the same
	# ordinary input-blocking any modal dialog in this codebase already does, not
	# an extra sim-pause mechanism (see class doc).
	_root.mouse_filter = Control.MOUSE_FILTER_STOP
	_root.visible = false
	add_child(_root)

	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.35)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.add_child(dim)

	var panel := PanelContainer.new()
	panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	panel.custom_minimum_size = Vector2(420, 0)
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.05, 0.05, 0.08, 0.96)
	style.border_color = Color(0.9, 0.6, 0.1)
	style.set_border_width_all(2)
	style.set_content_margin_all(12)
	panel.add_theme_stylebox_override("panel", style)
	_root.add_child(panel)

	var vb := VBoxContainer.new()
	panel.add_child(vb)

	var title := Label.new()
	title.text = "🛩  Flight recorder marker"
	title.add_theme_color_override("font_color", Color(1.0, 0.75, 0.2))
	vb.add_child(title)

	_note_edit = LineEdit.new()
	_note_edit.placeholder_text = "Optional note — Enter to save, Esc to skip"
	_note_edit.text_submitted.connect(_on_note_submitted)
	vb.add_child(_note_edit)


func _show_note_popup() -> void:
	_root.visible = true
	_note_edit.text = ""
	_note_edit.grab_focus()


func _on_note_submitted(text: String) -> void:
	_finish_marker(text)


func _on_note_skipped() -> void:
	_finish_marker("")


func _finish_marker(note: String) -> void:
	var prefix: String = _pending.get("prefix", "")
	if prefix != "":
		var note_path := session_dir.path_join(prefix + "_note.txt")
		var nf := FileAccess.open(note_path, FileAccess.WRITE)
		if nf != null:
			nf.store_string(note)
			nf.close()
		var entry := build_manifest_entry(_pending.get("marker_id", 0), note, _pending.get("state"), prefix)
		_append_manifest(entry)
		if is_instance_valid(NotificationManager) and NotificationManager.has_method("info"):
			NotificationManager.info("Flight recorder: marker %d captured" % entry["marker_id"])
	_root.visible = false
	_pending = {}


func _input(event: InputEvent) -> void:
	if _root == null or not _root.visible:
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_ESCAPE:
		_on_note_skipped()
		get_viewport().set_input_as_handled()

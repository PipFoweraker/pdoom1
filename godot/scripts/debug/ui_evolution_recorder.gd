extends CanvasLayer
class_name UIEvolutionRecorder
## UI evolution capture rail -- Pip's "it went from this... to this..." ask
## (2026-07-27): a lightweight way to programmatically snapshot visual state as UI
## lanes land, so a later devblog/anniversary/grantmaker montage can be assembled
## from a timeline instead of hunting through Win+PrtScn screenshots by hand.
##
## One press of F7 drops a screenshot + one-line context (scene name, version,
## turn) into user://ui_evolution/<version>/manifest.jsonl. Deliberately reuses
## flight_recorder.gd's shape -- session directory under user://, append-only
## manifest.jsonl, zero-padded sortable filenames -- rather than inventing a third
## capture layout. Unlike the flight recorder this is a single silent keypress: no
## note popup, no full GameState.to_dict() dump, because the ask is "before/after
## this visual change", not a deep playtest replay.
##
## Dev-build only (BuildInfo.is_dev_build(), same gate as FlightRecorder and
## DevModeOverlay); zero effect on normal play when gated off. Registered the same
## way: a signal on KeybindManager, connected here, built in code (no .tscn).
##
## tools/collect_ui_evolution.py sweeps user://ui_evolution/ (plus optionally
## Windows' Pictures\Screenshots, the manual Win+PrtScn rail) into
## G:/tmp/pdoom1-ui-evolution/<date>/ -- OUTSIDE the repo, per
## docs/art/ART_MASTERS_POLICY.md (the .pck packs the whole godot/ tree, and
## these captures accumulate indefinitely).

const ROOT := "user://ui_evolution"

## Reference to the MainUI node so the live GameManager/state can be resolved
## the same way FlightRecorder/DevModeOverlay do (main_ui.gd wires this at
## instantiation).
var main_ui: Node = null

var _built := false
var _shot_count := 0


# --- Live-manager resolution (mirrors flight_recorder.gd's _live_gm) -------

func _live_gm() -> Node:
	if main_ui != null:
		var gm = main_ui.get("game_manager")
		if gm != null:
			return gm
	return GameManager


func _ready() -> void:
	# Below FlightRecorder's note popup (180) and the DEV BUILD badge (200); this
	# recorder has no visible UI of its own, so exact layering barely matters.
	layer = 170
	if not BuildInfo.is_dev_build():
		visible = false
		return
	_built = true
	if is_instance_valid(KeybindManager):
		KeybindManager.ui_evolution_shot_requested.connect(_on_capture_requested)


# --- Pure helpers (unit-tested without a live viewport/GameManager) --------

static func session_dir(version: String) -> String:
	return ROOT.path_join(version)


## Zero-padded index + timestamp so shots within one version sort chronologically
## by filename -- same convention as flight_recorder.gd's marker_prefix.
static func shot_filename(index: int, timestamp: Dictionary) -> String:
	return "%04d_%04d%02d%02d_%02d%02d%02d.png" % [
		index,
		int(timestamp.get("year", 0)), int(timestamp.get("month", 0)), int(timestamp.get("day", 0)),
		int(timestamp.get("hour", 0)), int(timestamp.get("minute", 0)), int(timestamp.get("second", 0)),
	]


static func iso_timestamp(timestamp: Dictionary) -> String:
	return "%04d-%02d-%02d %02d:%02d:%02d" % [
		int(timestamp.get("year", 0)), int(timestamp.get("month", 0)), int(timestamp.get("day", 0)),
		int(timestamp.get("hour", 0)), int(timestamp.get("minute", 0)), int(timestamp.get("second", 0)),
	]


static func manifest_entry(index: int, timestamp: Dictionary, version: String, scene_name: String, turn: int, screenshot: String) -> Dictionary:
	return {
		"index": index,
		"timestamp": iso_timestamp(timestamp),
		"version": version,
		"scene": scene_name,
		"turn": turn,
		"screenshot": screenshot,
	}


# --- Capture flow ------------------------------------------------------------

func _on_capture_requested() -> void:
	if not _built:
		return
	_capture()


func _capture() -> void:
	var version: String = GameConfig.CURRENT_VERSION if is_instance_valid(GameConfig) else "unknown"
	var dir := session_dir(version)
	DirAccess.make_dir_recursive_absolute(dir)

	_shot_count += 1
	var timestamp := Time.get_datetime_dict_from_system()
	var filename := shot_filename(_shot_count, timestamp)

	# (a) Screenshot
	var image := get_viewport().get_texture().get_image()
	var shot_path := dir.path_join(filename)
	var shot_err := image.save_png(shot_path)
	if shot_err != OK:
		push_error("[UIEvolutionRecorder] Failed to save screenshot: %s" % shot_err)

	# (b) One-line context: scene name, version, turn (if a run is live).
	var scene_name := "unknown"
	var scene := get_tree().current_scene
	if scene != null:
		scene_name = scene.name

	var turn := -1
	var gm := _live_gm()
	if gm != null and gm.get("state") != null:
		turn = gm.get("state").turn

	var entry := manifest_entry(_shot_count, timestamp, version, scene_name, turn, filename)
	_append_manifest(dir, entry)

	# Cross-reference hook: the perf story and the visual story can be joined by
	# timestamp later (PerfLog.mark is a no-op when PerfLog isn't active).
	if is_instance_valid(PerfLog):
		PerfLog.mark("ui_evolution", {"index": _shot_count, "version": version, "scene": scene_name})

	if is_instance_valid(NotificationManager) and NotificationManager.has_method("info"):
		NotificationManager.info("UI evolution shot %d captured" % _shot_count)

	var abs_path := OS.get_user_data_dir().path_join("ui_evolution").path_join(version)
	print("[UIEvolutionRecorder] Captured %s -> %s" % [filename, abs_path])


func _append_manifest(dir: String, entry: Dictionary) -> void:
	var path := dir.path_join("manifest.jsonl")
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

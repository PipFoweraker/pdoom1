extends RefCounted
class_name SaveLoad
## L7 (#618): mid-game save/load — snapshot fidelity for 6-8 hr runs (EE-2, promoted).
##
## A save file is a JSON envelope:
##   { save_format, game_version, saved_at, scenario_id, state: GameState.to_dict() }
## The state body follows the SERIALIZATION CONVENTION documented above
## GameState.to_dict() (JSON-safe values, int64s as Strings, derived fields ignored).
##
## Replay (ADR-0006) rebuilds from turn 0 and is untouched by this; DQ-11
## fork/divergence builds on this same envelope later.

const SAVE_DIR := "user://saves"
const QUICKSAVE_PATH := "user://saves/quicksave.json"
const SAVE_FORMAT := 1


static func build_envelope(state: GameState) -> Dictionary:
	return {
		"save_format": SAVE_FORMAT,
		"game_version": GameConfig.CURRENT_VERSION,
		"saved_at": Time.get_datetime_string_from_system(),
		# Scenario custom events live as node meta (Issue #483), not in state
		# serialization — record the pack id so load can re-attach them.
		"scenario_id": GameConfig.scenario_id,
		"state": state.to_dict(),
	}


static func save_game(state: GameState, path: String = QUICKSAVE_PATH) -> Error:
	if state == null:
		return ERR_INVALID_PARAMETER
	var err := DirAccess.make_dir_recursive_absolute(SAVE_DIR)
	if err != OK and err != ERR_ALREADY_EXISTS:
		return err
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		return FileAccess.get_open_error()
	# full_precision=true is LOAD-BEARING: the default truncates float decimals,
	# which shifts every restored float by ulps — the drift then compounds turn
	# over turn, so a loaded game would slowly diverge from an unsaved one.
	f.store_string(JSON.stringify(build_envelope(state), "\t", true, true))
	f.close()
	print("[SaveLoad] Saved turn %d to %s" % [state.turn, path])
	return OK


static func has_save(path: String = QUICKSAVE_PATH) -> bool:
	return FileAccess.file_exists(path)


static func load_envelope(path: String = QUICKSAVE_PATH) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var text := f.get_as_text()
	f.close()
	var parsed = JSON.parse_string(text)
	if not (parsed is Dictionary):
		print("[SaveLoad] Corrupt save (not a JSON object): %s" % path)
		return {}
	return parsed


## Rebuild a GameState from an envelope. Returns null on failure.
## The caller owns the returned Node (GameState extends Node).
static func restore_state(envelope: Dictionary) -> GameState:
	var sd = envelope.get("state", {})
	if not (sd is Dictionary) or sd.is_empty():
		return null
	var schedule: Array = []
	if sd.get("event_schedule", null) is Array:
		schedule = sd["event_schedule"]
	# Seed + schedule are constructor-time identity (WS-C); from_dict then
	# overwrites every member — including the rng stream position.
	var state := GameState.new(String(sd.get("game_seed", "")), schedule)
	state.from_dict(sd)
	return state

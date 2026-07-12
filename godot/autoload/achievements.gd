extends Node
## Achievements — observer-only run recognition (build lane L8, issue #619).
##
## THE CONTRACT (ADR-0002 anti-sink rule; WORKSHOP_2_BUILD_LANES §L8):
## achievements are RECOGNITION, never in-run reward. This node is a read-only
## listener. It consumes the Dictionary snapshots GameManager already emits via
## `game_state_updated` — GameState.to_dict() copies, never the live GameState
## object — and writes NOTHING back into sim, score, or any gameplay system.
## No achievement may ever gate, grant, or price anything inside a run; a
## proposed achievement with an in-run effect is rejected on sight, exactly as
## ADR-0002 rejects stock score terms. tests/unit/test_achievements.gd asserts
## that evaluate() leaves the snapshot byte-identical (the observer-only proof).
##
## Persistence is per-PROFILE, not per-save: user://achievements.json survives
## runs and records the first-unlock date. Unlocks are permanent.
##
## Year marks derive from the game calendar (state.calendar; ADR-0009 "the badge
## is the date") — never from turn arithmetic — so they survive turn-cadence
## changes (the L0 plan-month migration).
##
## New candidates accumulate in WORKSHOP_2_BACKLOG.md DQ-17 ([ACHIEVEMENT] tags).

signal achievement_unlocked(achievement: Dictionary)

const SAVE_PATH_DEFAULT := "user://achievements.json"
var save_path: String = SAVE_PATH_DEFAULT  # var, so tests can redirect it

## v1 definitions. Flavor register: bureaucratic deadpan around enormous stakes
## (WORLD_AND_LORE.md tone section; Papers, Please is the north star).
const DEFINITIONS: Array = [
	{"id": "year_2022", "title": "Still Here: 2022",
		"flavor": "Five years of payroll met on time. The world persists. So, against expectation, do you."},
	{"id": "year_2027", "title": "Still Here: 2027",
		"flavor": "Most labs with your opening decade are case studies by now. You are a footnote with staff."},
	{"id": "year_2032", "title": "Still Here: 2032",
		"flavor": "The interns have interns. Doom does not respect seniority."},
	{"id": "year_2037", "title": "Still Here: 2037",
		"flavor": "You have outlived three funding paradigms and at least one ideology."},
	{"id": "first_hire", "title": "Personnel File Opened",
		"flavor": "A costly human, complete with their own problems. Congratulations."},
	{"id": "first_departure", "title": "Offboarding Complete",
		"flavor": "The badge has been returned. The institutional knowledge has not."},
	{"id": "first_paper", "title": "Peer Reviewed",
		"flavor": "Reviewer 2 had concerns. Humanity gains a PDF."},
	{"id": "first_liability", "title": "Signed in Ink",
		"flavor": "Money now, consequences later. The ledger will remember this so you don't have to."},
	{"id": "doom90_survived", "title": "White Knuckles",
		"flavor": "Doom passed 90. You filed the paperwork anyway."},
]

# EE-4 seam (deferred to boards work — do not implement here): "fastest X this
# season" records are LEADERBOARD-derived, not observer-derived. Anticipated
# shape in this file, keyed (season_id, achievement_id):
#   "season_records": {"<season_id>": {"<achievement_id>": {
#       "turns": int, "game_date": String, "entry_uuid": String}}}
# EE-4 populates season_records from Leaderboard entries at submission time;
# achievements.gd only ever reads them for display. Recognition, never reward.

var unlocked: Dictionary = {}       # id -> {first_unlocked_utc, run_turn, game_date}
var unlocked_this_run: Array = []   # ids unlocked this run, for the game-over screen
var _prev: Dictionary = {}          # previous snapshot's transition basis

const _MONTH_NAMES := ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
	"Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


func _ready() -> void:
	load_profile()
	# Watch the registered GameManager autoload. NOTE (known debt, #619 report):
	# the live game actually runs a scene-local GameManager node in main.tscn;
	# main_ui registers that one via watch(). Watching both covers either path.
	var gm := get_node_or_null("/root/GameManager")
	if gm:
		watch(gm)


func watch(game_manager: Node) -> void:
	"""Subscribe to a GameManager instance (idempotent). Observer-only: the sole
	signal consumed is game_state_updated, whose payload is already a to_dict()
	snapshot — never the live GameState."""
	if game_manager == null or not game_manager.has_signal("game_state_updated"):
		return
	if not game_manager.game_state_updated.is_connected(_on_game_state_updated):
		game_manager.game_state_updated.connect(_on_game_state_updated)


func _on_game_state_updated(state: Dictionary) -> void:
	evaluate(state)


func evaluate(state: Dictionary) -> Array:
	"""Evaluate all still-locked achievements against a state snapshot.
	Returns the ids newly unlocked (possibly empty). READ-ONLY on `state` by
	contract — the GUT test asserts the snapshot is byte-identical afterwards."""
	var newly: Array = []
	var turn := int(state.get("turn", 0))
	if not _prev.is_empty() and turn < int(_prev.get("turn", 0)):
		_reset_run_tracking()  # turn went backwards: a new run started
	for def in DEFINITIONS:
		if unlocked.has(def["id"]):
			continue
		if _predicate_holds(def["id"], state):
			_unlock(def, state)
			newly.append(def["id"])
	_prev = {
		"turn": turn,
		"doom": float(state.get("doom", 0.0)),
		"total_staff": int(state.get("total_staff", 0)),
		"papers": float(state.get("papers", 0.0)),
		"ledger_entries": int(state.get("ledger", {}).get("entry_count", 0)),
	}
	return newly


func _predicate_holds(id: String, state: Dictionary) -> bool:
	# Year marks carry no game_over gate: ADR-0009 badge-is-the-date semantics —
	# a run whose death date lands in 2027 "made it to 2027".
	var year := int(state.get("calendar", {}).get("year", 0))
	match id:
		"year_2022":
			return year >= 2022
		"year_2027":
			return year >= 2027
		"year_2032":
			return year >= 2032
		"year_2037":
			return year >= 2037
		"first_hire":
			return not _prev.is_empty() \
				and int(state.get("total_staff", 0)) > int(_prev.get("total_staff", 0))
		"first_departure":
			return not _prev.is_empty() \
				and int(state.get("total_staff", 0)) < int(_prev.get("total_staff", 0))
		"first_paper":
			return not _prev.is_empty() \
				and float(state.get("papers", 0.0)) > float(_prev.get("papers", 0.0))
		"first_liability":
			# Snapshot only exposes ledger aggregates (entry_count), not entry
			# sources, so this fires on the first liability of ANY kind (loan,
			# funding-with-strings, desperation lever) — deliberately broader
			# than "first loan" to keep the observer snapshot-pure.
			return not _prev.is_empty() \
				and int(state.get("ledger", {}).get("entry_count", 0)) > int(_prev.get("ledger_entries", 0))
		"doom90_survived":
			# Doom was past 90 at the previous snapshot, a turn has since
			# resolved, and the run is still alive: that turn was survived
			# at doom > 90.
			return not _prev.is_empty() \
				and float(_prev.get("doom", 0.0)) > 90.0 \
				and int(state.get("turn", 0)) > int(_prev.get("turn", 0)) \
				and not state.get("game_over", false)
	return false


func _unlock(def: Dictionary, state: Dictionary) -> void:
	var record := {
		"first_unlocked_utc": Time.get_datetime_string_from_system(true),
		"run_turn": int(state.get("turn", 0)),
		"game_date": _format_game_date(state.get("calendar", {})),
	}
	unlocked[def["id"]] = record
	unlocked_this_run.append(def["id"])
	_save()
	achievement_unlocked.emit({
		"id": def["id"], "title": def["title"], "flavor": def["flavor"], "record": record,
	})
	# Toast via the existing NotificationManager ACHIEVEMENT type — display only.
	if is_inside_tree():
		var nm := get_node_or_null("/root/NotificationManager")
		if nm:
			nm.achievement("Achievement — %s" % def["title"])


func is_unlocked(id: String) -> bool:
	return unlocked.has(id)


func get_definition(id: String) -> Dictionary:
	for def in DEFINITIONS:
		if def["id"] == id:
			return def
	return {}


func _reset_run_tracking() -> void:
	unlocked_this_run.clear()
	_prev.clear()


func _format_game_date(calendar: Dictionary) -> String:
	if calendar.is_empty():
		return ""
	var month := int(calendar.get("month", 1))
	return "%s %d, %d" % [
		_MONTH_NAMES[clampi(month - 1, 0, 11)],
		int(calendar.get("day", 1)),
		int(calendar.get("year", 0)),
	]


# --- Persistence (per-profile; mirrors leaderboard.gd's JSON convention) -----

func _save() -> void:
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	if file == null:
		push_warning("[Achievements] Could not write %s" % save_path)
		return
	file.store_string(JSON.stringify({"version": 1, "unlocked": unlocked}, "\t"))
	file.close()


func load_profile() -> void:
	if not FileAccess.file_exists(save_path):
		return
	var file := FileAccess.open(save_path, FileAccess.READ)
	if file == null:
		return
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	if parsed is Dictionary and parsed.get("unlocked") is Dictionary:
		unlocked = parsed["unlocked"]

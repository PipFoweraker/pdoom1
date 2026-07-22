extends GutTest
## L8 (#619): achievements observer -- unlock predicates + the observer-only
## proof: evaluate() must leave the state snapshot byte-identical (ADR-0002
## anti-sink rule; achievements are recognition, never in-run reward).

const TEST_SAVE := "user://test_achievements_l8.json"

var ach


func before_each():
	var AchievementsScript = load("res://autoload/achievements.gd")
	ach = AchievementsScript.new()
	ach.save_path = TEST_SAVE
	autofree(ach)


func after_each():
	var dir := DirAccess.open("user://")
	if dir and dir.file_exists("test_achievements_l8.json"):
		dir.remove("test_achievements_l8.json")


func _snapshot(overrides: Dictionary = {}) -> Dictionary:
	"""A minimal GameState.to_dict()-shaped snapshot (only the fields the
	observer reads), 2017 start per ADR-0009 fiction anchors."""
	var state := {
		"turn": 10,
		"doom": 50.0,
		"game_over": false,
		"papers": 0.0,
		"total_staff": 0,
		"ledger": {"entry_count": 0},
		"calendar": {"year": 2017, "month": 7, "day": 14},
	}
	for key in overrides:
		state[key] = overrides[key]
	return state


func test_year_mark_unlocks_from_calendar():
	var newly = ach.evaluate(_snapshot({"calendar": {"year": 2022, "month": 1, "day": 5}}))
	assert_has(newly, "year_2022")
	assert_true(ach.is_unlocked("year_2022"))
	assert_false(ach.is_unlocked("year_2027"), "later year marks must stay locked")


func test_year_mark_locked_before_the_year():
	ach.evaluate(_snapshot())  # 2017
	assert_false(ach.is_unlocked("year_2022"))


func test_evaluate_never_mutates_the_snapshot():
	# The observer-only proof. This evaluate() call actually unlocks something
	# (year_2022), i.e. the busiest code path runs -- and the snapshot must come
	# out byte-identical and hash-identical.
	var state = _snapshot({"calendar": {"year": 2022, "month": 1, "day": 5}})
	var json_before = JSON.stringify(state)
	var hash_before = hash(state)
	var newly = ach.evaluate(state)
	assert_gt(newly.size(), 0, "precondition: an unlock must actually fire")
	assert_eq(JSON.stringify(state), json_before,
		"evaluate() wrote into the state snapshot - observer contract broken")
	assert_eq(hash(state), hash_before,
		"state hash changed across evaluate() - observer contract broken")


func test_first_hire_and_departure_transitions():
	ach.evaluate(_snapshot({"total_staff": 0}))
	assert_false(ach.is_unlocked("first_hire"), "no hire happened yet")
	ach.evaluate(_snapshot({"total_staff": 1}))
	assert_true(ach.is_unlocked("first_hire"))
	assert_false(ach.is_unlocked("first_departure"))
	ach.evaluate(_snapshot({"total_staff": 0}))
	assert_true(ach.is_unlocked("first_departure"))


func test_first_liability_fires_on_ledger_entry():
	ach.evaluate(_snapshot())
	assert_false(ach.is_unlocked("first_liability"))
	ach.evaluate(_snapshot({"ledger": {"entry_count": 1}}))
	assert_true(ach.is_unlocked("first_liability"))


func test_doom90_requires_surviving_the_turn():
	ach.evaluate(_snapshot({"turn": 10, "doom": 95.0}))
	assert_false(ach.is_unlocked("doom90_survived"), "turn not yet resolved")
	ach.evaluate(_snapshot({"turn": 11, "doom": 95.0}))
	assert_true(ach.is_unlocked("doom90_survived"))


func test_doom90_not_awarded_when_the_turn_kills_you():
	ach.evaluate(_snapshot({"turn": 10, "doom": 95.0}))
	ach.evaluate(_snapshot({"turn": 11, "doom": 100.0, "game_over": true}))
	assert_false(ach.is_unlocked("doom90_survived"))


func test_unlocks_persist_across_instances():
	ach.evaluate(_snapshot({"calendar": {"year": 2027, "month": 3, "day": 3}}))
	assert_true(ach.is_unlocked("year_2027"))
	var second = load("res://autoload/achievements.gd").new()
	second.save_path = TEST_SAVE
	second.load_profile()
	autofree(second)
	assert_true(second.is_unlocked("year_2027"), "unlock must survive a reload")
	assert_false(second.is_unlocked("year_2032"))


func test_new_run_resets_run_scoped_list_but_not_profile():
	ach.evaluate(_snapshot({"turn": 50, "calendar": {"year": 2022, "month": 1, "day": 5}}))
	assert_has(ach.unlocked_this_run, "year_2022")
	# Turn goes backwards: a fresh run started.
	ach.evaluate(_snapshot({"turn": 0}))
	assert_eq(ach.unlocked_this_run.size(), 0, "run-scoped list must reset")
	assert_true(ach.is_unlocked("year_2022"), "profile unlock is permanent")

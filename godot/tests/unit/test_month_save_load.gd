extends GutTest
## L1 (#612 / ADR-0009, L7): save/load must survive the month plan layer, INCLUDING a
## save taken while day-tick playback is PAUSED on an open response window.

const TEST_SAVE_NAME := "test_l1_month_pause.json"
const TEST_SAVE_PATH := "user://saves/" + TEST_SAVE_NAME


func after_each():
	var dir := DirAccess.open("user://saves")
	if dir and dir.file_exists(TEST_SAVE_NAME):
		dir.remove(TEST_SAVE_NAME)


func _window(id: String) -> Dictionary:
	return {
		"id": id, "type": "popup", "delivery_tier": "window", "event_class": "deferrable",
		"options": [
			{"id": "handle", "costs": {}, "effects": {"reputation": 1}, "message": "handled"},
			{"id": "ignore", "costs": {}, "effects": {"reputation": -1}, "message": "ignored"},
		],
		"window": {"attention_cost": 2, "handle_option": "handle", "ignore_option": "ignore"},
	}


func test_month_plan_survives_save_load():
	var s := GameState.new("l1-month-save")
	s.month_plan.set_reserve(6)
	s.month_plan.pay_from_reserve(2)
	s.month_plan.queue_strategic("fundraise_campaign", 5, 4, s.turn)

	SaveLoad.save_game(s, TEST_SAVE_PATH)
	var restored := SaveLoad.restore_state(SaveLoad.load_envelope(TEST_SAVE_PATH))

	assert_eq(restored.month_plan.attention_total, s.month_plan.attention_total, "Attention grant survives")
	assert_eq(restored.month_plan.reserve_remaining(), s.month_plan.reserve_remaining(), "reserve survives")
	assert_eq(restored.month_plan.available(), s.month_plan.available(), "available Attention survives")
	assert_eq(restored.month_plan.queued_strategic.size(), 1, "in-flight strategic WIP survives")
	assert_eq(int(restored.month_plan.queued_strategic[0].resolves_on_turn),
		int(s.month_plan.queued_strategic[0].resolves_on_turn), "WIP duration timing survives")


func test_pause_on_window_survives_save_load():
	# Drive a tick into a paused-on-window state, save mid-pause, load into a fresh state,
	# and confirm the open window and plan state are recovered so playback can resume.
	var s := GameState.new("l1-pause-save")
	s.money = 245000.0
	s.month_plan.set_reserve(4)
	var mc := MonthController.new(s, null)
	s.pending_events.assign([_window("audit_notice")])
	var r := mc.advance_tick()
	assert_eq(String(r.status), "paused_on_window", "we are paused on a window before saving")
	assert_eq(s.pending_events.size(), 1, "the open window is mirrored into serialized state")

	SaveLoad.save_game(s, TEST_SAVE_PATH)
	var restored := SaveLoad.restore_state(SaveLoad.load_envelope(TEST_SAVE_PATH))

	assert_eq(restored.pending_events.size(), 1, "the open window survived the round trip")
	assert_eq(restored.month_plan.reserve_remaining(), 4, "the reserve held for it survived")

	# A fresh controller rehydrates the pause and resumes exactly where it stopped.
	var mc2 := MonthController.new(restored, null)
	mc2.rehydrate_from_state()
	assert_true(mc2.is_paused(), "playback re-enters the paused state after load")
	assert_eq(mc2.window_queue.size(), 1, "the window is back in the live queue")
	var res := mc2.resolve_current_window("handle_reserve")  # reserve 4 covers the cost-2 window
	assert_true(res.success, "the recovered window can be resolved after load")
	assert_false(mc2.is_paused(), "playback resumes")

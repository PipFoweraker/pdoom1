extends GutTest
## The stub-vs-rule contract for player-facing refusals (playtest 2026-08-14, Pip).
##
## "A stub that refuses in the voice of a rule teaches the player a rule that does not
## exist." These pin the two halves of scripts/core/refusal.gd -- the classification API
## itself, and the first refusal it was built for: HANDLE-by-cannibalizing, which refused
## with "Insufficient capacity" for what is really an unbuilt mechanic.
##
## The load-bearing pin is test_cannibalize_refusal_becomes_a_rule_once_wip_exists: it is
## what proves the discriminator is DERIVED rather than hardcoded, i.e. that the marker
## retires itself when the mechanic gets built instead of needing someone to remember.

func _state() -> GameState:
	var s := GameState.new("refusal-stub-vs-rule-seed")
	s.money = 245000.0
	s.reputation = 50.0
	return s


func _window() -> Dictionary:
	return {
		"id": "vendor_dispute",
		"type": "popup",
		"delivery_tier": "window",
		"event_class": "deferrable",
		"source_id": "legal_counsel",
		"options": [
			{"id": "settle", "costs": {"money": 20000}, "effects": {"reputation": 5}},
			{"id": "let_it_ride", "costs": {}, "effects": {"reputation": -3}},
		],
		"window": {"attention_cost": 2, "handle_option": "settle", "ignore_option": "let_it_ride"},
	}


# --- The classification API ------------------------------------------------------------

func test_rule_ships_unmarked():
	var r := Refusal.rule("No desk. Get a bigger office.")
	assert_false(bool(r["success"]), "a refusal is a failure")
	assert_eq(String(r["refusal"]), Refusal.CLASS_RULE, "classified as a real constraint")
	assert_eq(String(r["message"]), "No desk. Get a bigger office.",
		"a RULE is worldbuilding -- it carries no apology")


func test_stub_carries_the_alpha_marker():
	var r := Refusal.stub("Insufficient capacity to handle by cannibalizing")
	assert_false(bool(r["success"]), "a refusal is a failure")
	assert_eq(String(r["refusal"]), Refusal.CLASS_STUB, "classified as unbuilt")
	assert_true(String(r["message"]).contains(Refusal.ALPHA_STUB_MARKER),
		"a STUB tells the player it is an apology, not a rule")
	assert_true(String(r["message"]).begins_with("Insufficient capacity"),
		"the original sentence survives -- the marker is appended, the copy is not restyled")


func test_marking_is_idempotent():
	var once := Refusal.mark_stub("Not built.")
	var twice := Refusal.mark_stub(once)
	assert_eq(twice, once, "a message crossing two layers is not marked twice")


func test_marking_an_empty_message_yields_just_the_marker():
	assert_eq(Refusal.mark_stub(""), Refusal.ALPHA_STUB_MARKER,
		"no sentence to apologise for -- the marker alone still beats silence")
	assert_eq(Refusal.mark_stub("   "), Refusal.ALPHA_STUB_MARKER, "whitespace counts as empty")


func test_marker_round_trips_for_presentation_layers():
	var marked := Refusal.mark_stub("Insufficient capacity to handle by cannibalizing")
	assert_true(Refusal.is_stub_message(marked), "the kind is recoverable from the string")
	assert_eq(Refusal.strip_marker(marked), "Insufficient capacity to handle by cannibalizing",
		"EventDialog can lift the marker out and re-place it without rewording anything")
	assert_false(Refusal.is_stub_message("Not enough money."), "an unmarked message is not a stub")


func test_marker_is_pure_ascii_bracket_chrome():
	# CLAUDE.md hard rule (issue #744): no codepoint above U+007F in player-facing strings.
	for i in Refusal.ALPHA_STUB_MARKER.length():
		assert_lt(Refusal.ALPHA_STUB_MARKER.unicode_at(i), 128,
			"the marker must stay ASCII -- it ships to players")


# --- The refusal it was built for -------------------------------------------------------

func test_cannibalize_refusal_is_a_stub_when_there_is_no_wip_to_eat():
	# The shipped-game case. MonthPlan.queued_strategic has no production writer
	# (GameManager.queue_strategic_action() has zero callers), so "pull from planned work"
	# can never reach the queue the player can actually see (GameState.queued_actions).
	var s := _state()
	var mp: MonthPlan = s.month_plan
	mp.set_reserve(0)
	mp.attention_spent = mp.attention_total  # a full month, nothing cannibalisable
	var r := WindowResolver.resolve(s, mp, _window(), "handle_cannibalize")
	assert_false(bool(r["success"]), "there is genuinely no Attention left")
	assert_eq(int(r["attention_paid"]), 0, "nothing was charged")
	assert_eq(String(r.get("refusal", "")), Refusal.CLASS_STUB,
		"nothing was cannibalisable, so this refused an UNBUILT mechanic, not a rule")
	assert_true(Refusal.is_stub_message(String(r["message"])),
		"Pip's marker reaches the player: the refusal reads as an apology, not a rule")


func test_cannibalize_refusal_becomes_a_rule_once_wip_exists():
	# THE ANTI-ROT PIN. The discriminator is derived from what pay_by_cannibalizing actually
	# ate, not declared by a flag. Queue real strategic WIP -- as the sim harness does and as
	# the UI one day will -- and the same code path reclassifies itself to RULE with no
	# marker and nothing for anyone to remember to switch off.
	var s := _state()
	var mp: MonthPlan = s.month_plan
	mp.set_reserve(0)
	assert_true(mp.queue_strategic("big_bet", 1, 3, s.turn), "one unit of cannibalisable WIP")
	# Squeeze the month dry. Eating the 1-Attention WIP refunds 1 against a 2-Attention
	# window, so the sacrifice is real but still not enough -- which is the genuine RULE.
	mp.attention_spent = mp.attention_total
	var r := WindowResolver.resolve(s, mp, _window(), "handle_cannibalize")
	assert_false(bool(r["success"]), "eating all the WIP still does not cover the window")
	assert_eq(r["cancelled_wip"], ["big_bet"], "the WIP really was sacrificed")
	assert_eq(String(r.get("refusal", "")), Refusal.CLASS_RULE,
		"WIP existed and was eaten -- this IS a real capacity constraint")
	assert_false(Refusal.is_stub_message(String(r["message"])),
		"a genuine rule ships unmarked; the marker retires itself when the mechanic lands")


func test_successful_cannibalize_is_not_classified_at_all():
	var s := _state()
	s.month_plan.set_reserve(0)
	var r := WindowResolver.resolve(s, s.month_plan, _window(), "handle_cannibalize")
	assert_true(bool(r["success"]), "plenty of free capacity")
	assert_false(r.has("refusal"), "nothing was refused, so there is nothing to classify")

extends GutTest
## EE-7 (ADR-0012): loss legibility -- engine-side pieces.
## Resource-affecting event choices report their net deltas; the ledger returns
## what it billed so the turn log can state every bill and its fallout. The one
## human ledger-death specimen was low-resolution because the player couldn't
## see the spiral -- these are the numbers future specimens point at.

func test_event_choice_reports_net_resource_deltas():
	var state = GameState.new("legibility-ev")
	var event := {"id": "test_ev", "options": [
		{"id": "a", "costs": {"money": 5000}, "effects": {"doom": -3, "reputation": 2}, "message": "ok"}
	]}
	var r: Dictionary = GameEvents.execute_event_choice(event, "a", state)
	assert_true(r.success, "choice executes")
	assert_true(r.has("deltas"), "result carries the applied deltas")
	assert_eq(float(r.deltas.money), -5000.0, "costs count negative")
	assert_eq(float(r.deltas.doom), -3.0, "doom effect reported")
	assert_eq(float(r.deltas.reputation), 2.0, "rep effect reported")
	assert_false(r.deltas.has("compute"), "untouched resources are omitted")


func test_tick_and_bill_returns_only_what_it_billed():
	var state = GameState.new("legibility-bill")
	state.ledger.add(Ledger.Entry.new("due_now", "money", 1000.0, 0, 0.0))
	state.ledger.add(Ledger.Entry.new("due_later", "money", 1000.0, 3, 0.0))
	var billed: Array = state.ledger.tick_and_bill(state)
	assert_eq(billed.size(), 1, "only the due entry bills this turn")
	assert_eq(str(billed[0].source), "due_now")


func test_turn_log_states_ledger_bill_and_fallout():
	var state = GameState.new("legibility-fallout")
	var tm = TurnManager.new(state)
	state.money = 500.0  # cannot cover the bill -> default -> doom/rep conversion
	state.ledger.add(Ledger.Entry.new("loan", "money", 50000.0, 0, 0.0))
	var result: Dictionary = tm.start_turn()
	var joined: String = "\n".join(result.messages)
	assert_string_contains(joined, "Ledger bill due: 'loan'", "the bill itself is stated")
	assert_string_contains(joined, "Ledger fallout", "the default's resource damage is stated")

extends GutTest
## L7 (#618) -- mid-game save/load round-trip. THE lane acceptance criterion.
##
## Plays N turns with a fixed seed (events resolved deterministically, ledger
## entries injected, a researcher hired, a paper in flight, an action queued
## mid-planning), saves through the REAL JSON file path, restores into a fresh
## GameState, then asserts:
##   1. to_dict() deep-equality (JSON-normalized both sides),
##   2. the previously-forgotten fields (EE-2) explicitly,
##   3. the next turn produces byte-identical state in both continuations
##      (rng stream position included).
##
## Replay (ADR-0006) rebuilds from turn 0 and is untouched; this is snapshot
## fidelity. See the SERIALIZATION CONVENTION block above GameState.to_dict().

const SEED := "l7-roundtrip-seed"
const TURNS_BEFORE_SAVE := 8
const TEST_SAVE_NAME := "test_l7_roundtrip.json"
const TEST_SAVE_PATH := "user://saves/" + TEST_SAVE_NAME


func after_each():
	var dir := DirAccess.open("user://saves")
	if dir and dir.file_exists(TEST_SAVE_NAME):
		dir.remove(TEST_SAVE_NAME)


# --- deterministic turn driving -------------------------------------------------

func _resolve_pending_events(tm: TurnManager, state: GameState) -> void:
	# First affordable option wins -- a pure function of state, so the pre-save run
	# and the post-load continuation make identical choices.
	var guard := 0
	while state.pending_events.size() > 0 and guard < 50:
		guard += 1
		var event: Dictionary = state.pending_events[0]
		var resolved := false
		for opt in event.get("options", []):
			if state.can_afford(opt.get("costs", {})):
				var res = tm.resolve_event(event, opt.get("id", ""))
				if res.get("success", false):
					resolved = true
					break
		if not resolved:
			# No affordable option: drop the event (mirrors BaselineSimulator) and
			# keep the phase machine consistent.
			state.pending_events.remove_at(0)
			if state.pending_events.size() == 0:
				state.current_phase = GameState.TurnPhase.ACTION_SELECTION
				state.can_end_turn = true


func _play_full_turn(tm: TurnManager, state: GameState) -> void:
	tm.start_turn()
	_resolve_pending_events(tm, state)
	tm.execute_turn()


func _end_turn(tm: TurnManager, state: GameState) -> void:
	# Mirrors GameManager.end_turn(): committed AP converts to spent AP.
	state.action_points -= state.committed_ap
	state.committed_ap = 0
	tm.execute_turn()


# --- comparison helpers ----------------------------------------------------------

func _norm(d: Dictionary) -> String:
	# JSON round-trip both sides so int-vs-float and typed-vs-untyped array
	# representation differences cannot mask (or fake) a divergence.
	# full_precision=true so a single-ulp float drift is a FAILURE, not noise.
	return JSON.stringify(JSON.parse_string(JSON.stringify(d, "", true, true)), "", true, true)


func _report_divergence(a_json: String, b_json: String) -> void:
	var a: Dictionary = JSON.parse_string(a_json)
	var b: Dictionary = JSON.parse_string(b_json)
	for k in a.keys():
		var va := JSON.stringify(a[k])
		var vb := JSON.stringify(b.get(k))
		if va != vb:
			gut.p("  DIVERGES [%s]\n    saved =%s\n    loaded=%s" % [k, va, vb])
	for k in b.keys():
		if not a.has(k):
			gut.p("  EXTRA KEY in loaded [%s]" % k)


func _assert_states_equal(state1: GameState, state2: GameState, context: String) -> void:
	var d1 := _norm(state1.to_dict())
	var d2 := _norm(state2.to_dict())
	if d1 != d2:
		gut.p("Round-trip divergence (%s):" % context)
		_report_divergence(d1, d2)
	assert_eq(d1, d2, "to_dict must be deep-equal: %s" % context)


# --- a mid-game state worth saving ----------------------------------------------

func _build_midgame(state: GameState, tm: TurnManager) -> void:
	# Cash buffer so the injected loan bills without bankrupting the run inside
	# the test horizon (deterministic either way, but alive is a stronger test).
	state.add_resources({"money": 500000.0})
	# Start low: the early doom ramp (rival momentum) reaches 100 by ~turn 5 from
	# the default 50, and this test wants a run that is still ALIVE at the save.
	state.doom = 5.0
	state.doom_system.current_doom = 5.0

	for i in range(3):
		_play_full_turn(tm, state)

	# WS-1 ledger content (BL-1: no clickable ledger actions yet, so inject):
	# a compounding loan that will bill before the save point, and a small
	# SECRET governance entry that stays live across it.
	state.ledger.add(Ledger.loan(50000.0))
	state.ledger.add(Ledger.Entry.new("test_secret", "governance", 500.0, 6, 0.1, true))

	# A hired researcher (traits/skill round-trip) and a rushed research stance.
	if state.candidate_pool.size() > 0:
		state.hire_candidate(state.candidate_pool[0])
	state.set_research_quality("rushed")
	state.add_technical_debt(12.0, "roundtrip test")

	# A paper in flight (Issue #468 structures).
	var paper := PaperSubmissions.PaperSubmission.new()
	paper.title = "Round-trip fidelity of latent snapshots"
	paper.target_conference_id = "neurips_2017"
	paper.status = PaperSubmissions.Status.UNDER_REVIEW
	paper.submit_turn = state.turn
	paper.quality = 0.7
	paper.topic = PaperSubmissions.Topic.INTERPRETABILITY
	paper.lead_researcher_name = "R. Oundtrip"
	paper.co_author_names.append("A. Turing")
	state.add_paper_submission(paper)

	for i in range(TURNS_BEFORE_SAVE - 3):
		_play_full_turn(tm, state)


# --- the acceptance test ----------------------------------------------------------

func test_save_load_roundtrip_deep_equality_and_next_turn_identical():
	var state1: GameState = autofree(GameState.new(SEED))
	var tm1: TurnManager = autofree(TurnManager.new(state1))
	_build_midgame(state1, tm1)
	assert_false(state1.game_over, "run must still be alive at the save point")
	assert_gt(state1.triggered_events.size() + state1.event_cooldowns.size(), 0,
		"test horizon should have fired at least one event (else the WS-0 registry check is vacuous)")
	assert_gt(state1.ledger.entries.size(), 0, "ledger must have entries at the save point")

	# Mid-planning snapshot: an action queued but not yet executed
	# (mirrors GameManager.select_action's bookkeeping).
	state1.queued_actions.append("fundraise")
	state1.committed_ap += 1

	# SAVE -> LOAD through the real file path (JSON coercions included).
	assert_eq(SaveLoad.save_game(state1, TEST_SAVE_PATH), OK, "save must write")
	assert_true(SaveLoad.has_save(TEST_SAVE_PATH), "save file must exist")
	var envelope := SaveLoad.load_envelope(TEST_SAVE_PATH)
	assert_false(envelope.is_empty(), "envelope must parse")
	var state2: GameState = autofree(SaveLoad.restore_state(envelope))
	assert_not_null(state2, "state must restore")

	# 1) Deep equality of the full serialized state.
	_assert_states_equal(state1, state2, "immediately after load")

	# 2) The previously-forgotten fields (EE-2 + audit), explicitly.
	assert_eq(state2.triggered_events, state1.triggered_events, "WS-0 triggered_events")
	assert_eq(JSON.stringify(state2.event_cooldowns), JSON.stringify(state1.event_cooldowns), "WS-0 event_cooldowns")
	assert_eq(state2.ledger.entries.size(), state1.ledger.entries.size(), "WS-1 ledger entries")
	for i in range(state1.ledger.entries.size()):
		assert_eq(state2.ledger.entries[i].to_dict(), state1.ledger.entries[i].to_dict(),
			"ledger entry %d" % i)
	assert_eq(state2.governance, state1.governance, "governance")
	assert_eq(state2.queued_actions, state1.queued_actions, "queued_actions")
	assert_eq(state2.committed_ap, state1.committed_ap, "committed_ap")
	assert_eq(state2.max_action_points, state1.max_action_points, "max_action_points (difficulty)")
	assert_eq(state2.rng.state, state1.rng.state, "rng stream position")
	assert_eq(state2.rival_labs.size(), state1.rival_labs.size(), "rival count")
	for i in range(state1.rival_labs.size()):
		assert_eq(state2.rival_labs[i].to_dict(), state1.rival_labs[i].to_dict(), "rival %d" % i)

	# 3) The next turn must be identical in both continuations: execute the
	# queued action, then run a full further turn including event resolution.
	var tm2: TurnManager = autofree(TurnManager.new(state2))
	_end_turn(tm1, state1)
	_end_turn(tm2, state2)
	_assert_states_equal(state1, state2, "after executing the queued turn")

	tm1.start_turn()
	tm2.start_turn()
	_resolve_pending_events(tm1, state1)
	_resolve_pending_events(tm2, state2)
	tm1.execute_turn()
	tm2.execute_turn()
	_assert_states_equal(state1, state2, "after one further full turn (rng stream continuity)")


func test_restore_state_returns_null_for_garbage():
	assert_null(SaveLoad.restore_state({}), "empty envelope -> null")
	assert_null(SaveLoad.restore_state({"state": "not a dict"}), "non-dict state -> null")
	assert_true(SaveLoad.load_envelope("user://saves/does_not_exist.json").is_empty(),
		"missing file -> empty envelope")

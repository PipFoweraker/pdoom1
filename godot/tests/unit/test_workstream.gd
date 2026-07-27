extends GutTest
## ADR-0011 s3/s4 WORKSTREAM SUBSTRATE (lane T1 / issue #613).
##
## Covers the substrate atoms this lane owns:
##  1. Workstream object -- effort accrual, completion, lead contributor, compute intensity.
##  2. Backlog + per-person assignment (one person, one bet).
##  3. Topic-tagged accrual through the turn hook; unassigned staff self-direct on their
##     agenda and REPORT optimistically (actual vs reported; audits reconcile them later).
##  4. compute_intensity (atom A7) billed per assigned head against the compute resource.
##  5. Serialization round-trip (Workstream, GameState keys, PaperSubmission.source_workstream).
##
## DETERMINISM (ADR-0006) is the load-bearing property: accrual makes no rng draws, so the
## same seed + same inputs must produce byte-identical tallies. Tests 3/5 pin that.
##
## NOT covered here (other lanes): AP-pool deletion, founder-hour typing, manager shields,
## artifact emission from a completed workstream, the plan-screen assignment UI.


func _new_state(seed_str: String) -> GameState:
	var s := GameState.new(seed_str)
	s.turn = 1
	return s


func _employ(state: GameState, spec: String, name: String, skill: int = 5) -> Researcher:
	var r := Researcher.new(spec, name)
	r.researcher_name = name
	r.skill_level = skill
	r.base_productivity = 0.5 + skill * 0.1
	state.add_researcher(r)
	return r


func _entry(id_str: String = "t_ws", topic: String = "safety", target: float = 10.0,
		intensity: float = 1.0) -> Dictionary:
	return {
		"id": id_str,
		"title": "Test workstream",
		"topic": topic,
		"effort_target": target,
		"duration_months": 2,
		"compute_intensity": intensity,
	}


# ============================================================================
# 1. The Workstream object
# ============================================================================

func test_make_reads_the_backlog_entry():
	var ws := Workstream.make("ws_1", _entry("eval", "interpretability", 40.0, 2.5), 7)
	assert_eq(ws.id, "ws_1")
	assert_eq(ws.backlog_id, "eval")
	assert_eq(ws.topic, PaperSubmissions.Topic.INTERPRETABILITY, "topic key parses to the shared paper enum")
	assert_eq(ws.effort_target, 40.0)
	assert_eq(ws.compute_intensity, 2.5)
	assert_eq(ws.status, Workstream.Status.ACTIVE, "a started workstream is active at once")
	assert_eq(ws.started_on_turn, 7)


func test_accrual_accumulates_and_completes_at_target():
	var ws := Workstream.make("ws_1", _entry("t", "safety", 10.0, 0.0), 0)
	ws.assign("staff_1")
	ws.accrue("staff_1", 4.0, 1)
	assert_almost_eq(ws.progress(), 0.4, 0.0001, "progress is effort over target")
	assert_false(ws.is_complete(), "not done yet")
	ws.accrue("staff_1", 6.0, 2)
	assert_true(ws.is_complete(), "hitting the target completes it")
	assert_eq(ws.completed_on_turn, 2, "completion stamps the turn it landed")


func test_completed_workstream_accepts_no_more_effort():
	var ws := Workstream.make("ws_1", _entry("t", "safety", 5.0, 0.0), 0)
	ws.accrue("staff_1", 5.0, 1)
	assert_eq(ws.accrue("staff_1", 5.0, 2), 0.0, "a finished bet is a closed account")
	assert_almost_eq(ws.effort_accrued, 5.0, 0.0001)


func test_lead_contributor_is_the_biggest_contributor_and_ties_break_stably():
	var ws := Workstream.make("ws_1", _entry("t", "safety", 1000.0, 0.0), 0)
	ws.accrue("staff_2", 3.0, 1)
	ws.accrue("staff_1", 9.0, 1)
	assert_eq(ws.lead_contributor(), "staff_1", "most effort leads")
	var tied := Workstream.make("ws_2", _entry("t2", "safety", 1000.0, 0.0), 0)
	tied.accrue("staff_9", 5.0, 1)
	tied.accrue("staff_3", 5.0, 1)
	assert_eq(tied.lead_contributor(), "staff_3", "ties break on the lower id, never on dict order")


func test_agenda_topic_prefers_explicit_focus_over_lane():
	assert_eq(Workstream.agenda_topic("capabilities", -1), PaperSubmissions.Topic.CAPABILITIES,
		"unset focus falls back to the researcher's lane")
	assert_eq(Workstream.agenda_topic("capabilities", PaperSubmissions.Topic.GOVERNANCE),
		PaperSubmissions.Topic.GOVERNANCE, "an explicitly-set focus_topic wins")


# ============================================================================
# 2. Backlog + assignment
# ============================================================================

func test_backlog_loads_and_is_id_sorted():
	var ids := WorkstreamBacklog.ids()
	assert_gt(ids.size(), 0, "the backlog data file loads")
	var sorted_ids := ids.duplicate()
	sorted_ids.sort()
	assert_eq(ids, sorted_ids, "entries come back id-sorted (order-stable across platforms)")


func test_start_workstream_consumes_the_backlog_entry():
	var s := _new_state("ws_start")
	var backlog_id: String = WorkstreamBacklog.ids()[0]
	var before := s.available_backlog().size()
	var ws = s.start_workstream(backlog_id)
	assert_not_null(ws, "a known backlog id starts")
	assert_eq(s.workstreams.size(), 1)
	assert_eq(s.available_backlog().size(), before - 1, "the entry leaves the available list")
	assert_null(s.start_workstream(backlog_id), "starting the same entry twice is refused")
	assert_null(s.start_workstream("no_such_entry"), "an unknown id is refused")


func test_assignment_is_exclusive_one_person_one_workstream():
	var s := _new_state("ws_assign")
	var r := _employ(s, "safety", "Assignee One")
	var ids := WorkstreamBacklog.ids()
	var a = s.start_workstream(ids[0])
	var b = s.start_workstream(ids[1])
	assert_true(s.assign_to_workstream(r, a.id), "first assignment lands")
	assert_eq(s.workstream_for_researcher(r).id, a.id)
	assert_true(s.assign_to_workstream(r, b.id), "re-assigning moves them")
	assert_eq(s.workstream_for_researcher(r).id, b.id, "they are on the new bet")
	assert_eq(a.assigned_count(), 0, "and off the old one -- no splitting a person across bets")
	assert_false(s.assign_to_workstream(r, b.id), "assigning where they already are is a no-op")


func test_release_keeps_the_contribution():
	var s := _new_state("ws_release")
	var r := _employ(s, "safety", "Departing Person")
	var ws = s.start_workstream(WorkstreamBacklog.ids()[0])
	s.assign_to_workstream(r, ws.id)
	ws.accrue(r.candidate_id, 7.0, 1)
	assert_true(s.release_from_workstreams(r), "they come off the workstream")
	assert_eq(ws.assigned_count(), 0)
	assert_almost_eq(float(ws.contributions.get(r.candidate_id, 0.0)), 7.0, 0.0001,
		"effort already spent stays on the record (authorship reads it later)")


func test_removing_a_researcher_releases_them():
	var s := _new_state("ws_remove")
	var r := _employ(s, "safety", "Quitter")
	var ws = s.start_workstream(WorkstreamBacklog.ids()[0])
	s.assign_to_workstream(r, ws.id)
	s.remove_researcher(r)
	assert_eq(ws.assigned_count(), 0, "a departing person stops accruing")


func test_researcher_ids_are_stable_and_unique():
	var s := _new_state("ws_ids")
	var a := _employ(s, "safety", "Person A")
	var b := _employ(s, "safety", "Person B")
	var id_a := s.researcher_id(a)
	assert_ne(id_a, "", "an employed person always resolves to an id")
	assert_eq(s.researcher_id(a), id_a, "resolving is idempotent for the same person")
	assert_ne(s.researcher_id(b), id_a, "and unique across people")


func test_ids_are_minted_only_for_people_who_have_none():
	# add_researcher already stamps a pipeline 'cand_N' id; minting is the fallback for
	# people who never went through it (legacy/loaded records).
	var s := _new_state("ws_mint")
	var stamped := _employ(s, "safety", "Stamped Person")
	assert_true(stamped.candidate_id.begins_with("cand_"), "the pipeline id is left alone")
	var orphan := Researcher.new("safety", "Orphan Record")
	var minted := s.researcher_id(orphan)
	assert_true(minted.begins_with("staff_"), "a minted id cannot collide with 'cand_' serials")
	assert_eq(s.researcher_id(orphan), minted, "and it sticks to that person")


# ============================================================================
# 3. Topic-tagged accrual through the turn hook
# ============================================================================

func _run_accrual(state: GameState, ticks: int) -> void:
	var tm := TurnManager.new(state)
	for i in range(ticks):
		tm._step_workstream_accrual()


func test_assigned_effort_lands_on_the_workstream():
	var s := _new_state("ws_accrue")
	var r := _employ(s, "safety", "Worker")
	var ws = s.start_workstream("incident_taxonomy")  # compute_intensity 0.0: isolates effort
	s.assign_to_workstream(r, ws.id)
	_run_accrual(s, 3)
	assert_gt(ws.effort_accrued, 0.0, "assigned work accrues into the bet")
	assert_almost_eq(ws.effort_accrued, r.get_effective_productivity() * 3.0, 0.0001,
		"three ticks of one person's effective productivity, ungambled")
	assert_almost_eq(r.self_directed_effort, 0.0, 0.0001, "an assigned person self-directs nothing")


func test_unassigned_staff_self_direct_on_their_lane():
	var s := _new_state("ws_selfdirect")
	var r := _employ(s, "interpretability", "Unsteered Person")
	_run_accrual(s, 2)
	assert_gt(r.self_directed_effort, 0.0, "idle staff don't exist -- they work on their own agenda")
	assert_true(s.self_directed_progress.has("interpretability"),
		"the tally is tagged with their lane's topic")
	assert_false(s.self_directed_progress.has("safety"), "and not with anyone else's")


func test_focus_topic_redirects_self_directed_work():
	var s := _new_state("ws_focus")
	var r := _employ(s, "capabilities", "Redirected Person")
	r.focus_topic = PaperSubmissions.Topic.GOVERNANCE
	_run_accrual(s, 1)
	assert_true(s.self_directed_progress.has("governance"),
		"an explicit focus_topic beats the lane default")


func test_self_reported_progress_is_optimistic_and_deterministic():
	var s := _new_state("ws_optimism")
	var r := _employ(s, "safety", "Optimistic Person")
	_run_accrual(s, 4)
	assert_gt(r.self_directed_reported, r.self_directed_effort,
		"unsupervised progress is over-claimed (the audit seam)")
	var factor := r.self_report_optimism()
	assert_gte(factor, 1.0, "the optimism factor never under-claims")
	assert_lte(factor, 1.05 + 0.3 + 0.0001, "and stays inside the first-pass gentle band")
	assert_eq(r.self_report_optimism(), factor, "the factor is stable for one person")
	assert_almost_eq(r.self_report_gap(), r.self_directed_reported - r.self_directed_effort, 0.0001)


func test_assigned_progress_stays_single_valued_and_truthful():
	# By ruling (2026-07-27): only SELF-DIRECTED work misreports, first pass. A planned
	# workstream's progress is the truth, full stop.
	var s := _new_state("ws_truthful")
	var r := _employ(s, "safety", "Steered Person")
	var ws = s.start_workstream("incident_taxonomy")
	s.assign_to_workstream(r, ws.id)
	_run_accrual(s, 3)
	assert_eq(s.self_directed_progress.size(), 0, "assigned work leaves no self-directed tally")
	assert_almost_eq(r.self_directed_reported, 0.0, 0.0001, "and nothing to over-claim")


func test_accrual_is_deterministic_for_the_same_seed():
	# THE replay-safety property: no rng in the accrual path, so two identical runs must
	# produce identical tallies down to the float.
	var results: Array = []
	for run in range(2):
		var s := _new_state("ws_determinism")
		var a := _employ(s, "safety", "Alpha", 6)
		var b := _employ(s, "capabilities", "Beta", 4)
		var ws = s.start_workstream("eval_harness")
		s.assign_to_workstream(a, ws.id)
		_run_accrual(s, 5)
		results.append({
			"effort": ws.effort_accrued,
			"compute": s.compute,
			"self_actual": b.self_directed_effort,
			"self_reported": b.self_directed_reported,
			"tally": s.self_directed_progress.duplicate(true),
		})
	assert_eq(results[0], results[1], "same seed, same inputs -> byte-identical accrual")


func test_accrual_draws_no_rng():
	var s := _new_state("ws_no_rng")
	_employ(s, "safety", "Person")
	var before := s.rng.state
	_run_accrual(s, 5)
	assert_eq(s.rng.state, before, "the accrual hook must not move the seeded stream")


# ============================================================================
# 4. compute_intensity (atom A7)
# ============================================================================

func test_compute_intensity_is_billed_per_assigned_head():
	var s := _new_state("ws_compute")
	var r := _employ(s, "safety", "Compute Hog")
	var ws = s.start_workstream("scaling_probe")  # compute_intensity 4.0/month
	s.assign_to_workstream(r, ws.id)
	var before := s.compute
	_run_accrual(s, 1)
	var expected := 4.0 / float(Workstream.turns_per_month())
	assert_almost_eq(before - s.compute, expected, 0.0001,
		"one tick bills one month's intensity divided by the month's ticks, per head")


func test_zero_intensity_workstreams_bill_nothing():
	var s := _new_state("ws_pen_and_paper")
	var r := _employ(s, "governance", "Policy Person")
	var ws = s.start_workstream("incident_taxonomy")  # compute_intensity 0.0
	s.assign_to_workstream(r, ws.id)
	var before := s.compute
	_run_accrual(s, 3)
	assert_almost_eq(s.compute, before, 0.0001, "pen-and-paper work costs no compute")


func test_compute_starvation_slows_but_does_not_idle():
	var s := _new_state("ws_starved")
	var r := _employ(s, "safety", "Queued Person")
	var ws = s.start_workstream("scaling_probe")
	s.assign_to_workstream(r, ws.id)
	s.compute = 0.0
	_run_accrual(s, 1)
	assert_almost_eq(s.compute, 0.0, 0.0001, "an unpayable charge is skipped, never overdrawn")
	assert_gt(ws.effort_accrued, 0.0, "a starved researcher is slowed, not idled")
	assert_lt(ws.effort_accrued, r.get_effective_productivity(),
		"but they get less done than a researcher whose runs never queue")


func test_monthly_demand_scales_with_staffing():
	var ws := Workstream.make("ws_1", _entry("t", "safety", 100.0, 2.0), 0)
	assert_almost_eq(ws.compute_demand_per_month(), 0.0, 0.0001, "an unstaffed bet demands nothing")
	ws.assign("staff_1")
	ws.assign("staff_2")
	assert_almost_eq(ws.compute_demand_per_month(), 4.0, 0.0001, "two heads at intensity 2.0")


# ============================================================================
# 5. Serialization
# ============================================================================

func _json_hop(d: Dictionary) -> Dictionary:
	return JSON.parse_string(JSON.stringify(d)) as Dictionary


func test_workstream_round_trips_through_json():
	var ws := Workstream.make("ws_7", _entry("eval", "alignment", 55.0, 1.5), 3)
	ws.assign("staff_2")
	ws.assign("staff_1")
	ws.accrue("staff_1", 12.5, 4)
	var restored := Workstream.from_dict(_json_hop(ws.to_dict()))
	assert_eq(restored.to_dict(), ws.to_dict(), "a workstream survives the JSON hop intact")
	assert_eq(restored.assigned_ids, ["staff_1", "staff_2"], "assignment order is stable (sorted)")
	assert_almost_eq(float(restored.contributions.get("staff_1", 0.0)), 12.5, 0.0001)


func test_game_state_round_trips_the_substrate():
	var s := _new_state("ws_save")
	var r := _employ(s, "safety", "Saved Person")
	var idle := _employ(s, "alignment", "Idle Person")
	var ws = s.start_workstream("red_team_program")
	s.assign_to_workstream(r, ws.id)
	_run_accrual(s, 3)

	var restored := GameState.new("ws_save")
	restored.from_dict(_json_hop(s.to_dict()))
	assert_eq(restored.workstreams.size(), 1, "workstreams restore")
	assert_eq(restored.workstreams[0].id, ws.id)
	assert_almost_eq(restored.workstreams[0].effort_accrued, ws.effort_accrued, 0.0001)
	assert_eq(restored.workstream_backlog_taken, s.workstream_backlog_taken, "taken backlog ids restore")
	assert_eq(restored.workstream_serial, s.workstream_serial)
	assert_eq(restored.researcher_id_serial, s.researcher_id_serial)
	assert_eq(restored.self_directed_progress, s.self_directed_progress,
		"the actual/reported self-direction tally restores as a pair")
	assert_eq(restored.to_dict()["workstreams"], s.to_dict()["workstreams"],
		"and the whole substrate re-serializes deep-equal")
	assert_eq(idle.focus_topic, -1, "an unset focus stays unset")


func test_researcher_direction_fields_round_trip():
	var r := Researcher.new("safety", "Round Tripper")
	r.candidate_id = "cand_3"
	r.focus_topic = PaperSubmissions.Topic.GOVERNANCE
	r.accrue_self_directed(4.0)
	var restored := Researcher.new()
	restored.from_dict(_json_hop(r.to_dict()))
	assert_eq(restored.focus_topic, PaperSubmissions.Topic.GOVERNANCE)
	assert_almost_eq(restored.self_directed_effort, r.self_directed_effort, 0.0001)
	assert_almost_eq(restored.self_directed_reported, r.self_directed_reported, 0.0001)


func test_pre_substrate_saves_load_with_an_empty_board():
	# Additive-keys guarantee: a save written before this lane has none of the new keys.
	var s := _new_state("ws_legacy")
	var legacy := s.to_dict()
	legacy.erase("workstreams")
	legacy.erase("workstream_backlog_taken")
	legacy.erase("workstream_serial")
	legacy.erase("researcher_id_serial")
	legacy.erase("self_directed_progress")
	var restored := GameState.new("ws_legacy")
	restored.from_dict(_json_hop(legacy))
	assert_eq(restored.workstreams.size(), 0, "old saves load with an empty board")
	assert_eq(restored.workstream_backlog_taken.size(), 0)
	assert_eq(restored.self_directed_progress.size(), 0)


func test_paper_carries_its_source_workstream():
	var paper := PaperSubmissions.PaperSubmission.new()
	paper.title = "Toward Safe Something"
	paper.source_workstream = "ws_4"
	var restored := PaperSubmissions.PaperSubmission.from_dict(_json_hop(paper.to_dict()))
	assert_eq(restored.source_workstream, "ws_4", "the idea-carrying ref survives the save hop")
	var legacy_dict := paper.to_dict()
	legacy_dict.erase("source_workstream")
	var legacy := PaperSubmissions.PaperSubmission.from_dict(legacy_dict)
	assert_eq(legacy.source_workstream, "", "a pre-substrate paper loads with no workstream")


func test_readout_lists_workstreams_and_the_self_report_gap():
	var s := _new_state("ws_readout")
	assert_true("none started" in s.workstream_readout()[0], "an empty board says so")
	var r := _employ(s, "safety", "Readout Person")
	var idle := _employ(s, "governance", "Drifting Person")
	var ws = s.start_workstream("incident_taxonomy")
	s.assign_to_workstream(r, ws.id)
	_run_accrual(s, 2)
	var lines := s.workstream_readout()
	assert_gt(lines.size(), 1, "the readout lists the workstream and the drift")
	var joined := "\n".join(lines)
	assert_true("[workstreams]" in joined, "workstream lines are tagged")
	assert_true("[self-directed]" in joined, "so is the unsteered drift")
	assert_true("gap" in joined, "and the claimed-vs-true gap the audit hour will reconcile")
	assert_not_null(idle)

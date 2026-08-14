extends GutTest
## ADR-0015 guard for RUNTIME-GENERATED event options (event_service.gd `_generate_options`).
##
## Sibling of test_events.gd::test_no_authored_event_content_writes_literal_doom, which scans
## authored CONTENT in res://data. That scan cannot see this class of defect: the pdoom-data
## historical events build their options IN CODE at load time, so seven inline `"doom": -N`
## literals lived past the content migration (test_events.gd's HANDLED_EFFECT_KEYS comment
## even records the gap -- "the runtime pdoom-data path in event_service.gd still emits it").
##
## Two things are asserted here:
##
##  1. STRUCTURE (ADR-0015 S1) -- no runtime-generated option may carry a literal `doom`
##     effect. Effects address a named world-state INTERMEDIARY; DoomSystem alone writes the
##     doom LEVEL. A literal here is not inert: execute_event_choice's trap (events.gd:303)
##     catches it and posts it to the `panic` stream, so it lands as REAL doom that is
##     MIS-ATTRIBUTED -- "Conduct internal review" shows up in the L6 death chain as panic.
##
##  2. BOUNDEDNESS (the exploit) -- the pdoom-data pool ships 1181 events (of 1194) whose
##     best option carried a negative doom literal, 1174 of them the strictly-dominant
##     `safety_analysis` on `technical_research_breakthrough`: 1 attention, +research,
##     +reputation, and -3 doom with no downside. At the shipped cap of 2 new events/turn
##     that is -6 doom/turn against a natural accumulation of ~+3.6 doom/turn (the
##     do_nothing calibration: 50 -> 100 over 14 months). Net -2.4/turn == doom-immortality,
##     bounded only by the 0.0 display clamp. The trend invariant LOGS this but never clamps
##     it, by design, so nothing in the engine stops it.
##
## Routing the reducers through `safety_absorption` closes it STRUCTURALLY rather than by
## tuning: the overhang stream is `W_frontier * max(0.0, frontier_max - safety_absorption)`,
## so absorption past the frontier buys literally nothing, and the other eight streams are
## untouched. Alarm/panic routing would NOT have closed it -- a repeated input to a decaying
## stock reaches a steady state of input/(1-decay), which reproduces the same -6/turn.

const DOOM_REDUCING_CATEGORIES := [
	"organization", "organization_founding",
	"research", "paper", "technical_research_breakthrough", "alignment_research",
	"policy", "regulation", "policy_event",
	"incident", "capability", "capability_advance",
	"funding_catastrophe", "funding",
	"general",
]

## The dominant real shape: 1174 of the 1194 shipped pdoom-data events land here.
func _raw_event(category: String, significance: int = 6) -> Dictionary:
	return {
		"id": "adr15_%s" % category,
		"title": "ADR-0015 probe (%s)" % category,
		"description": "synthetic probe event",
		"category": category,
		"year": 2017,
		"rarity": "common",
		"significance": significance,
		"impacts": [{"variable": "vibey_doom", "change": 10}],
	}


func _options_for(category: String, significance: int = 6) -> Array:
	var event: Dictionary = EventService._transform_event(_raw_event(category, significance))
	assert_false(event.is_empty(), "transform should build an event for category '%s'" % category)
	return event.get("options", [])


# ---------------------------------------------------------------------------
# 1. STRUCTURE -- no literal doom in any runtime-generated option
# ---------------------------------------------------------------------------

func test_no_runtime_generated_option_carries_a_literal_doom_effect() -> void:
	var offenders: Array[String] = []
	var options_seen := 0

	for category in DOOM_REDUCING_CATEGORIES:
		for option in _options_for(category):
			options_seen += 1
			if option.get("effects", {}).has("doom"):
				offenders.append("%s/%s" % [category, option.get("id", "?")])

	assert_gt(options_seen, 20, "the probe should have exercised every _generate_options branch")
	assert_eq(offenders.size(), 0,
		"runtime-generated options must write a world-state intermediary, never a literal "
		+ "doom effect (ADR-0015 S1). Offenders: " + ", ".join(PackedStringArray(offenders)))


func test_runtime_generated_options_still_address_the_doom_system() -> void:
	## The intent is legitimate -- an internal review SHOULD reduce risk. Guard against a
	## "fix" that simply deletes the effect: each doom-flavoured option must still write a
	## named intermediary that DoomSystem._compute_streams actually reads.
	var intermediaries := ["safety_absorption", "global_alarm", "global_panic",
		"frontier_capability", "general_capability"]

	var expectations := {
		"organization": "collaborate",
		"technical_research_breakthrough": "safety_analysis",
		"policy": "support",
		"incident": "internal_review",
		"funding_catastrophe": "diversify_funding",
	}

	for category in expectations.keys():
		var want_id: String = expectations[category]
		var found := false
		for option in _options_for(category):
			if option.get("id", "") != want_id:
				continue
			found = true
			var keys = option.get("effects", {}).keys()
			var hits := 0
			for k in keys:
				if k in intermediaries:
					hits += 1
			assert_gt(hits, 0,
				"%s/%s must still reach the doom system through a named intermediary; got %s"
				% [category, want_id, str(keys)])
		assert_true(found, "expected option '%s' in category '%s'" % [want_id, category])


# ---------------------------------------------------------------------------
# 2. BOUNDEDNESS -- the exploit itself
# ---------------------------------------------------------------------------

const EXPLOIT_TURNS := 20
const EVENTS_PER_TURN := 2  # the shipped events.max_new_events_per_turn


func _run(turns: int, picks_per_turn: int) -> float:
	"""Play `turns` turns taking the doom-reducing option `picks_per_turn` times each turn,
	resolving the doom system between turns exactly as the real loop does. Returns the final
	doom LEVEL. A clean world (no seeded rivals) so the measurement isolates the option."""
	var state := GameState.new("adr15_exploit_seed")
	state.doom = 50.0
	state.doom_system.current_doom = 50.0

	var event: Dictionary = EventService._transform_event(
		_raw_event("technical_research_breakthrough"))

	for t in range(turns):
		state.turn = t + 1
		# A fresh Attention grant each turn. At 20/month against a 1-Attention choice the
		# founder budget is never the binding constraint -- event SUPPLY is what caps this.
		state.month_plan.begin_month(Balance.inum("attention.per_month", 20), t)
		for _p in range(picks_per_turn):
			var res: Dictionary = GameEvents.execute_event_choice(event, "safety_analysis", state)
			assert_true(res.get("success", false),
				"the harness must actually execute the choice (got: %s)"
				% res.get("message", "?"))
		state.doom_system.calculate_doom_change(state)
		state.doom = state.doom_system.current_doom

	return state.doom


func test_repeated_risk_reduction_cannot_drive_doom_to_the_floor() -> void:
	## RED before the fix: the panic stream read exactly -6.00/turn (-7.78 with momentum) and
	## doom pinned at the 0.0 clamp inside ~8 turns.
	var exploited := _run(EXPLOIT_TURNS, EVENTS_PER_TURN)

	assert_gt(exploited, 5.0,
		("repeatedly taking the doom-reducing event option must not drive doom to the floor "
		+ "-- an unbounded doom sink makes runs non-comparable on the league board "
		+ "(got %.2f after %d turns x %d picks, started at 50.0)")
		% [exploited, EXPLOIT_TURNS, EVENTS_PER_TURN])


func test_risk_reduction_cannot_reverse_the_natural_doom_trend() -> void:
	## The load-bearing invariant, measured as a DIFFERENTIAL so it does not depend on how
	## hostile the surrounding world is: playing the option must not flip a rising doom
	## trajectory into a falling one. Pre-fix the control rose to 51.57 while the exploited
	## run sat on the 0.0 floor -- a 51.6-point swing (and only that small because the clamp
	## ate the rest of the -120).
	var control := _run(EXPLOIT_TURNS, 0)
	var exploited := _run(EXPLOIT_TURNS, EVENTS_PER_TURN)

	assert_gt(control, 50.0, "sanity: doom should rise on its own over %d turns" % EXPLOIT_TURNS)
	assert_gt(exploited, 50.0,
		("doom must still RISE over %d turns even while spending every event on risk "
		+ "reduction -- one relief channel must not out-run the other eight streams "
		+ "(control %.2f, exploited %.2f)") % [EXPLOIT_TURNS, control, exploited])

	var swing := control - exploited
	assert_lt(swing, 25.0,
		("the total doom a player can buy with %d risk-reducing choices must stay well "
		+ "inside the 0-100 scale; got a %.2f-point swing (control %.2f vs exploited %.2f)")
		% [EXPLOIT_TURNS * EVENTS_PER_TURN, swing, control, exploited])

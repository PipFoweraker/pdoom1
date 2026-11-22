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

## --------------------------------------------------------------------------------------
## CODE-SIDE SCAN (added 2026-08-14 with the ratchet loosening -- see test_events.gd).
##
## The data-side guard capped risk_events.json at a shrink-only count of 20 doom literals.
## That proxy failed in both directions on the same day: it blocked 28 events of legitimate
## content (#1230) whose POSITIVE pool doom is honest, while the two real violations -- and
## in the end seven -- sat in .gd files it never opened. Pip ratified dropping the count cap
## for content velocity on condition that the mechanism get tighter and louder. This is that
## half: the same rule, "doom moves through named streams", enforced where the defect
## actually lived.
##
## Everything currently writing doom outside doom_system.gd is enumerated below WITH ITS
## REASON. A new write fails this test and prints its own source line, so the author has to
## classify it rather than discover later that a guard quietly did not cover their file.
## --------------------------------------------------------------------------------------

const DOOM_AUTHORITY := "res://scripts/core/doom_system.gd"
const CODE_SCAN_DIRS := ["res://scripts", "res://autoload"]

## Legitimate doom writes, keyed by file, matched on the exact trimmed source line.
const DOOM_WRITE_ALLOWLIST := {
	# The single authoritative sync: DoomSystem's level -> the mirror on GameState.
	"res://scripts/core/turn_manager.gd": [
		"state.doom = state.doom_system.current_doom",
		# Legacy fallbacks, reached only when no doom_system exists (lightweight test doubles).
		'state.add_resources({"doom": total_doom_increase})',
		'state.add_resources({"doom": doom_impact})',
		'state.add_resources({"doom": amount})',
	],
	# execute_event_choice's ADR-0015 trap: routes a literal to add_stream_input("panic"),
	# falling back to the direct sink only where there is no doom engine to route into.
	"res://scripts/core/events.gd": [
		'state.add_resources({"doom": value})',
	],
	# Ledger bills route to the `ledger` stream; the direct write is the test-double fallback
	# (test_liability_ledger.gd deliberately frees doom_system to exercise it). The _note()
	# payloads are ATTRIBUTION records, not effects.
	"res://scripts/core/ledger.gd": [
		"state.doom += amount",
		'"money_shortfall": shortfall, "doom": doom_hit, "reputation": -rep_hit})',
		'{"governance_deficit": deficit, "doom": doom_hit})',
		'_note(state, "ledger_doom_bill", e.source, {"doom": applied})',
	],
	# Documented inert sinks (ADR-0015 Legacy #15): clobbered at resolve in the real loop,
	# retained for direct-state unit tests.
	"res://scripts/core/game_state.gd": ['doom += gains["doom"]'],
	"res://scripts/core/resource_accessor.gd": ["state.doom += value"],
	# Terminal jam on resign + the scenario START-LEVEL dial (an ADR-0015 carve-out).
	"res://scripts/game_manager.gd": [
		"state.doom = 100.0",
		'state.doom = float(resources["doom"])',
	],
	# Debug-gated nudges (OS.is_debug_build / alpha-tool gated).
	"res://scripts/debug/dev_mode_overlay.gd": ["s.doom = clampf(s.doom + delta, 0.0, 100.0)"],
	"res://scripts/ui/main_ui.gd": [
		"st.doom = st.doom_system.current_doom",
		"st.doom = clampf(st.doom + delta, 0.0, 100.0)",
	],
	# pdoom-data variable map: a NAME->NAME entry and a scale factor, not effects.
	"res://autoload/event_service.gd": ['"doom": "doom",', '"doom": 1,'],
}

## Known-unrouted writes: real ADR-0015 violations that are DELIBERATELY still here, each
## with an owner-visible reason. Listed separately from the allowlist so they read as debt,
## not as blessing, and so the count can be asserted downward over time.
const DOOM_WRITE_KNOWN_DEBT := {
	# EMPTY, and that is the win. This held ONE entry -- desperation_payroll's
	# `state.add_resources({"doom": -suppress})`, which advertised "-10 doom now" and
	# delivered nothing because the sink is clobbered at resolve (#967).
	#
	# The entry's own note said migrating it "would turn a no-op into a real -10 doom --
	# a BALANCE change, not a routing fix, so it is out of scope for this lane." That
	# balance call was MADE on 2026-08-22: Pip ruled "I'd rather have a bad thing in
	# there now, unsubtle, rather than no thing... players need to suffer", the write was
	# migrated to safety_absorption like its actions.gd sibling, and
	# doom.streams.action_desperation_absorb went 0.0 -> 25.0 with a dated balancing
	# commitment (docs/game-design/DESPERATION_LEVER_PRICING.md, 2026-09-19).
	#
	# Keep this dict EMPTY. A new entry means a new unrouted doom write was tolerated,
	# and it must carry the same thing this one did: a reason, and what would retire it.
}


func _all_gd_paths(dir_path: String, out: Array) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	dir.list_dir_begin()
	var entry := dir.get_next()
	while entry != "":
		var full := dir_path.path_join(entry)
		if dir.current_is_dir():
			if entry != "addons":
				_all_gd_paths(full, out)
		elif entry.ends_with(".gd"):
			out.append(full)
		entry = dir.get_next()
	dir.list_dir_end()


func test_no_code_outside_the_doom_system_writes_doom_directly() -> void:
	var paths: Array = []
	for d in CODE_SCAN_DIRS:
		_all_gd_paths(d, paths)
	assert_gt(paths.size(), 50, "the .gd tree was found and walked")

	# A `doom` key given a VALUE (an effect), or a direct write to the doom level.
	var effect_re := RegEx.new()
	effect_re.compile('"doom"\\s*:\\s*\\S')
	var write_re := RegEx.new()
	write_re.compile('(?:^|[^\\w.])(?:\\w+\\.)?doom\\s*(?:\\+=|-=)|(?:\\w+)\\.doom\\s*=(?!=)')
	# Readouts/serialisation, where the doom LEVEL is the value being reported.
	var readout_re := RegEx.new()
	readout_re.compile('"doom"\\s*:\\s*(?:float\\()?(?:[\\w.]*\\.)?doom\\b|"doom"\\s*:\\s*DoomSystem\\._snap')

	var offenders: Array[String] = []
	var debt_seen := 0

	for path in paths:
		if path == DOOM_AUTHORITY:
			continue
		var text: String = FileAccess.get_file_as_string(path)
		var line_no := 0
		for raw_line in text.split("\n"):
			line_no += 1
			var line: String = str(raw_line).strip_edges()
			if line.begins_with("#") or line.contains("`"):
				continue
			if line.contains('== "doom"') or line.contains('!= "doom"'):
				continue
			if line.contains('state.get("doom"'):
				continue
			if readout_re.search(line) != null:
				continue
			if effect_re.search(line) == null and write_re.search(line) == null:
				continue

			if DOOM_WRITE_KNOWN_DEBT.get(path, []).has(line):
				debt_seen += 1
				continue
			if DOOM_WRITE_ALLOWLIST.get(path, []).has(line):
				continue
			offenders.append("%s:%d: %s" % [path, line_no, line])

	assert_eq(offenders.size(), 0,
		("doom must move through a NAMED STREAM, in code as well as in data (ADR-0015 S1). "
		+ "These writes are neither on the reviewed allowlist nor on the known-debt list at "
		+ "the top of this file. If the write is legitimate plumbing, add it there WITH ITS "
		+ "REASON; if it is an effect, write an intermediary (safety_absorption / "
		+ "global_alarm / global_panic / frontier_capability) instead:\n  ")
		+ "\n  ".join(PackedStringArray(offenders)))

	assert_eq(debt_seen, 0,
		("the known-unrouted doom write list is EMPTY since #967 migrated the last entry "
		+ "(finance_engine desperation_payroll -> safety_absorption); got %d. A non-zero "
		+ "count means a new unrouted doom write was added to the debt list -- it needs a "
		+ "reason and a retirement condition, not just an entry.") % debt_seen)


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

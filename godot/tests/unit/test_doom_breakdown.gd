extends GutTest
## Unit tests for DoomBreakdown -- the #578 colour-coded per-source doom "blow-by-blow".
## Covers the pure builder: per-source signed text, red/green classification, and
## omission of zero / negligible sources. On-screen layout still needs a human eye.

func test_positive_source_classified_as_increase_red():
	# A source pushing doom UP classifies as +1 and resolves to the theme "error" (red) colour.
	assert_eq(DoomBreakdown.classify(12.3), 1, "Positive value should increase doom")
	assert_eq(
		DoomBreakdown.color_for_sign(1),
		ThemeManager.get_color("error"),
		"Doom-increasing source should be red (theme 'error')"
	)

func test_negative_source_classified_as_decrease_green():
	# A source pulling doom DOWN classifies as -1 and resolves to the theme "success" (green).
	assert_eq(DoomBreakdown.classify(-14.4), -1, "Negative value should decrease doom")
	assert_eq(
		DoomBreakdown.color_for_sign(-1),
		ThemeManager.get_color("success"),
		"Doom-decreasing source should be green (theme 'success')"
	)

func test_zero_and_negligible_classified_as_omit():
	assert_eq(DoomBreakdown.classify(0.0), 0, "Exact zero should be omitted")
	assert_eq(DoomBreakdown.classify(0.02), 0, "Below-epsilon positive should be omitted")
	assert_eq(DoomBreakdown.classify(-0.03), 0, "Below-epsilon negative should be omitted")

func test_build_entries_omits_zero_sources():
	# Keys are the ADR-0015 stream vocabulary (overhang/alarm/...); the dead "rivals" key
	# is gone -- rival hazard now rides the "overhang" stream, no direct rival doom write.
	var sources := {
		"baseline": 1.0,
		"overhang": 12.3,
		"alarm": -14.4,
		"momentum": 0.0,       # exactly zero -- omitted
		"diffusion": 0.01,     # negligible -- omitted
	}
	var entries := DoomBreakdown.build_entries(sources)
	assert_eq(entries.size(), 3, "Only non-zero sources should be shown")
	var keys: Array = []
	for e in entries:
		keys.append(e["key"])
	assert_does_not_have(keys, "momentum", "Zero source omitted")
	assert_does_not_have(keys, "diffusion", "Negligible source omitted")

func test_build_entries_signed_text_and_labels():
	var entries := DoomBreakdown.build_entries({"overhang": 12.3, "alarm": -14.4})
	# Sorted by descending magnitude: alarm (14.4) before overhang (12.3).
	assert_eq(entries[0]["text"], "Alarm -14.4", "Negative source shows human label + signed value")
	assert_eq(entries[0]["sign"], -1, "Alarm pulls doom down")
	assert_eq(entries[1]["text"], "Overhang +12.3", "Positive source shows explicit + sign")
	assert_eq(entries[1]["sign"], 1, "Overhang pushes doom up")

func test_build_entries_sorted_by_magnitude():
	var entries := DoomBreakdown.build_entries({
		"baseline": 1.0,
		"overhang": 12.3,
		"alarm": -14.4,
	})
	assert_eq(entries[0]["key"], "alarm", "Biggest mover (|14.4|) first")
	assert_eq(entries[1]["key"], "overhang", "Then |12.3|")
	assert_eq(entries[2]["key"], "baseline", "Then |1.0|")

func test_label_for_known_and_unknown_keys():
	assert_eq(DoomBreakdown.label_for("overhang"), "Overhang", "ADR-0015 stream key uses friendly label")
	assert_eq(DoomBreakdown.label_for("technical_debt"), "Technical Debt", "Known key uses friendly label")
	# The dead "rivals" key no longer has a bespoke label -- it just capitalizes now.
	assert_eq(DoomBreakdown.label_for("rivals"), "Rivals", "Removed key falls back to capitalize")
	# Unknown key falls back to a capitalized rendering rather than crashing.
	assert_eq(DoomBreakdown.label_for("some_new_source"), "Some New Source", "Unknown key capitalizes")

func test_no_rivals_label_in_map():
	# ADR-0015 pin: no "rivals" doom-source key is ever populated, so the bespoke label was
	# removed. Guard against a future re-introduction masking the dead key.
	assert_false(DoomBreakdown.SOURCE_LABELS.has("rivals"), "Dead 'rivals' label must not be re-added")

func test_build_entries_empty_when_all_zero():
	var entries := DoomBreakdown.build_entries({"baseline": 0.0, "overhang": 0.0})
	assert_eq(entries.size(), 0, "All-zero sources produce an empty (hidden) breakdown")

# ---------------------------------------------------------------------------
# Overhang attribution -- names the rival labs behind the acute-hazard stream,
# masked by each lab's real visibility (never leaks an undiscovered lab's name).
# ---------------------------------------------------------------------------

func _rival_dict(lab_name: String, visibility: int, aggression: float = 0.9) -> Dictionary:
	var lab := RivalLabs.RivalLab.new(lab_name, aggression)
	lab.visibility = visibility
	return lab.to_dict()

func test_overhang_attribution_lists_visible_labs():
	# CapabiliCorp holds the highest frontier and is KNOWN -> named in the attribution line.
	var rivals := [
		_rival_dict("CapabiliCorp", RivalLabs.VisibilityState.KNOWN),
		_rival_dict("DeepSafety", RivalLabs.VisibilityState.KNOWN, 0.3),
	]
	var frontier := {"player": 100.0, "capabilicorp": 800.0, "deepsafety": 200.0}
	var text := DoomBreakdown.overhang_attribution_text(frontier, rivals)
	assert_true(text.find("CapabiliCorp") != -1, "Visible frontier leader is named")
	# Leader (max frontier) comes first in the list.
	assert_true(text.begins_with("frontier held by CapabiliCorp"), "Max-frontier actor leads: %s" % text)

func test_overhang_attribution_hides_undiscovered_labs():
	# A HIDDEN lab holding the frontier must read as an unknown actor -- never its real name.
	var rivals := [_rival_dict("StealthAI", RivalLabs.VisibilityState.HIDDEN)]
	var frontier := {"player": 50.0, "stealthai": 900.0}
	var text := DoomBreakdown.overhang_attribution_text(frontier, rivals)
	assert_eq(text.find("StealthAI"), -1, "Undiscovered lab name must NOT leak: %s" % text)
	assert_true(text.find("an unknown actor") != -1, "Hidden lab masked as unknown actor: %s" % text)

func test_frontier_leaders_skip_negligible_and_rank():
	var rivals := [_rival_dict("CapabiliCorp", RivalLabs.VisibilityState.KNOWN)]
	var frontier := {"player": 300.0, "capabilicorp": 800.0, "idle": 0.1}
	var leaders := DoomBreakdown.frontier_leaders(frontier, rivals)
	assert_eq(leaders.size(), 2, "Negligible (<epsilon) frontier slices are dropped")
	assert_eq(str(leaders[0]["id"]), "capabilicorp", "Highest frontier ranks first")
	assert_eq(str(leaders[1]["id"]), "player", "Player second")
	assert_eq(str(leaders[1]["name"]), "your own frontier", "Player slice reads as own frontier")

func test_overhang_attribution_empty_without_frontier():
	assert_eq(DoomBreakdown.overhang_attribution_text({}, []), "", "No frontier data -> no attribution")
	assert_eq(DoomBreakdown.overhang_attribution_text({"player": 0.0}, []), "", "All-negligible -> no attribution")

# ---------------------------------------------------------------------------
# Death attribution on the game-over screen -- the causal chain renders, and the
# overhang killer line names the top visible lab for an overhang-driven doom death.
# ---------------------------------------------------------------------------

func test_game_over_renders_attribution_chain_when_data_present():
	# DeathAttribution.classify over a state with a logged cause yields a non-empty chain,
	# which the game-over BBCode builder must render as a non-empty cause-of-death panel.
	var state := GameState.new("test_death_chain")
	state.cause_log.append({
		"turn": 3,
		"kind": "ledger_default",
		"source": "payroll",
		"effects": {"doom": 2.0, "reputation": -8.0},
	})
	var result := DeathAttribution.classify(state)
	var chain: Array = result.get("chain", [])
	assert_gt(chain.size(), 0, "DeathAttribution should produce a non-empty chain")
	var bbcode := GameOverScreen.build_attribution_bbcode(chain, "")
	assert_ne(bbcode, "", "Non-empty chain must render a non-empty attribution panel")
	assert_true(bbcode.find("CAUSE OF DEATH") != -1, "Panel carries the cause-of-death header")

func test_game_over_attribution_empty_without_data():
	assert_eq(GameOverScreen.build_attribution_bbcode([], ""), "", "No chain + no killer line -> empty")

func test_overhang_killer_line_names_visible_lab():
	var rivals := [_rival_dict("CapabiliCorp", RivalLabs.VisibilityState.KNOWN)]
	var frontier := {"player": 100.0, "capabilicorp": 900.0}
	var line := GameOverScreen.overhang_killer_line("doom", "overhang", frontier, rivals)
	assert_true(line.find("CapabiliCorp") != -1, "Overhang doom death names the visible frontier leader")
	assert_eq(line.find("!"), -1, "Deadpan register: no exclamation marks")

func test_overhang_killer_line_masks_hidden_lab():
	var rivals := [_rival_dict("StealthAI", RivalLabs.VisibilityState.HIDDEN)]
	var frontier := {"player": 50.0, "stealthai": 900.0}
	var line := GameOverScreen.overhang_killer_line("doom", "overhang", frontier, rivals)
	assert_eq(line.find("StealthAI"), -1, "Hidden lab name must not leak on the death screen")
	assert_true(line.find("an unknown actor") != -1, "Hidden killer masked as unknown actor")

func test_overhang_killer_line_only_for_overhang_doom_death():
	var rivals := [_rival_dict("CapabiliCorp", RivalLabs.VisibilityState.KNOWN)]
	var frontier := {"capabilicorp": 900.0}
	assert_eq(GameOverScreen.overhang_killer_line("rep", "overhang", frontier, rivals), "", "Rep death -> no overhang lab line")
	assert_eq(GameOverScreen.overhang_killer_line("doom", "ledger", frontier, rivals), "", "Ledger-dominant doom death -> no lab line")

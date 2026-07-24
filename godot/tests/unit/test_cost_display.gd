extends GutTest
## Cost-display sweep (2026-07-24 playtest, issue #822-adjacent): "the simulator is brutal
## because it is precise -- hidden costs violate that." Locks in the on-face cost display +
## affordability rules for event-dialog options and the icon-grid action submenus
## (fundraising / publicity / strategic / travel / operations / financing), and guards
## against a duplicate-cost regression sneaking back into event data (a baked-in "($35k)"
## in the option text PLUS the auto-appended cost summary reads as conflicting, not merely
## redundant, to a player).

var _main_ui_script: GDScript = load("res://scripts/ui/main_ui.gd")


# --- EventDialog.format_cost_summary (event-dialog options) -------------------------------

func test_format_cost_summary_shows_money_and_ap():
	var text := EventDialog.format_cost_summary({"money": 35000, "action_points": 1})
	assert_string_contains(text, "1 AP", "AP cost must be on the button face, not hover-only")
	assert_string_contains(text, "$35,000", "money cost must be on the button face")

func test_format_cost_summary_zero_cost_is_free():
	assert_eq(EventDialog.format_cost_summary({}), " (Free)",
		"a costless option must say Free, not show nothing (ambiguous != free)")

func test_format_cost_summary_zero_valued_entries_do_not_render_as_a_cost():
	# A {"action_points": 0} entry is not a real cost -- must not clutter the face as "0 AP".
	var text := EventDialog.format_cost_summary({"action_points": 0})
	assert_eq(text, " (Free)", "a zero-valued cost entry must read as Free, not '0 AP'")

func test_format_cost_summary_reputation_cost_shown():
	# Regression: reputation-only costs (e.g. compute_deal's "Negotiate Better Terms") must
	# not be silently dropped -- only money/action_points had bespoke handling historically.
	var text := EventDialog.format_cost_summary({"reputation": 5})
	assert_string_contains(text, "5 Reputation")


# --- Event data quality gate: no duplicate/baked-in cost text -----------------------------

func test_core_events_option_text_has_no_baked_in_cost_strings():
	# format_cost_summary already appends the authoritative cost to every option button.
	# An option "text" field that ALSO bakes in a cost substring (legacy pre-sweep pattern,
	# e.g. "Install Security System ($35k)") shows the cost twice and can drift from the
	# real costs dict. This is a regression gate, not a style nit: a stale baked-in number
	# that disagrees with the real costs dict is a silent lie on the button face.
	GameEvents.reload_definitions()
	var events := GameEvents.get_all_events()
	assert_gt(events.size(), 0, "core events loaded")
	# Targets the specific baked-in patterns the sweep removed: "{cost_money}" placeholder,
	# "costs N AP", or a parenthesized "$<amount>" money figure. Deliberately narrow (vs. a
	# blanket "costs "/"$" substring check) so narrative text like "(costs trust -- ...)"
	# doesn't false-positive.
	var cost_pattern := RegEx.new()
	cost_pattern.compile("(\\{cost_money\\}|costs? \\d+ AP|\\(\\$\\d)")
	var offenders: Array[String] = []
	for event in events:
		for option in event.get("options", []):
			var t: String = String(option.get("text", ""))
			if cost_pattern.search(t):
				offenders.append("%s/%s: %s" % [event.get("id", "?"), option.get("id", "?"), t])
	assert_eq(offenders.size(), 0,
		"option text should not bake in its own cost string (duplicates the auto cost display): %s" % [offenders])


# --- Free-out options cost 0 Attention (task requirement 4) --------------------------------

func test_declineignore_style_outs_cost_zero_action_points():
	# "defer / reject offer / ignore / acknowledge"-style free outs must cost 0 AP. This does
	# not change gameplay -- it is a regression lock on the existing data.
	GameEvents.reload_definitions()
	var events := GameEvents.get_all_events()
	var free_out_markers := ["decline", "ignore", "defer", "refuse", "silent", "stay_out", "let_them_leave", "minimize"]
	var violations: Array[String] = []
	for event in events:
		for option in event.get("options", []):
			var oid: String = String(option.get("id", "")).to_lower()
			var is_free_out := false
			for marker in free_out_markers:
				if oid.contains(marker):
					is_free_out = true
					break
			if is_free_out:
				var ap_cost = option.get("costs", {}).get("action_points", 0)
				if ap_cost > 0:
					violations.append("%s/%s costs %s AP" % [event.get("id", "?"), option.get("id", "?"), ap_cost])
	assert_eq(violations.size(), 0, "free-out style options must cost 0 Attention: %s" % [violations])


# --- Submenu cost-display helpers (fundraising/publicity/strategic/travel/operations) -----

func test_format_costs_inline_free_when_empty():
	var ui = _main_ui_script.new()
	assert_eq(ui._format_costs_inline({}), "Free")
	ui.free()

func test_format_costs_inline_lists_all_known_resources():
	var ui = _main_ui_script.new()
	var text: String = ui._format_costs_inline({"action_points": 2, "money": 8000, "reputation": 1})
	assert_string_contains(text, "2 AP")
	assert_string_contains(text, "$8,000")
	assert_string_contains(text, "1 Rep")
	ui.free()

func test_costs_affordable_uses_available_ap_not_raw_action_points():
	# Regression for the AP-skip / raw-action_points bug found during the sweep: a state
	# with plenty of raw action_points but a fully committed monthly Attention budget
	# (available_ap == 0) must NOT read as affordable for an AP-costing option.
	var ui = _main_ui_script.new()
	var state := {"action_points": 5, "available_ap": 0, "money": 100000}
	assert_false(ui._costs_affordable({"action_points": 1}, state),
		"available_ap (not the raw action_points primitive) must gate AP affordability")
	assert_true(ui._costs_affordable({"money": 50000}, state),
		"a money-only cost within budget should be affordable")
	assert_false(ui._costs_affordable({"money": 200000}, state),
		"a money-only cost beyond budget should be unaffordable")
	ui.free()

func test_costs_affordable_free_option_always_affordable():
	var ui = _main_ui_script.new()
	assert_true(ui._costs_affordable({}, {}), "a free option is always affordable regardless of state")
	ui.free()

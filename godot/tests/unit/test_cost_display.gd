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

func test_format_cost_summary_shows_money_and_attention():
	var text := EventDialog.format_cost_summary({"money": 35000, "attention": 1})
	# "Attention", not "AP": the AP pool was retired in #996 and the founder currency is
	# Attention. The ASSERTION is unchanged -- the cost must be on the button face, not
	# hover-only -- only the currency's name moved. (#1037)
	assert_string_contains(text, "1 Attention",
		"Attention cost must be on the button face, not hover-only")
	assert_string_contains(text, "$35,000", "money cost must be on the button face")

func test_format_cost_summary_zero_cost_is_free():
	assert_eq(EventDialog.format_cost_summary({}), " (Free)",
		"a costless option must say Free, not show nothing (ambiguous != free)")

func test_format_cost_summary_zero_valued_entries_do_not_render_as_a_cost():
	# An {"attention": 0} entry is not a real cost -- must not clutter the face.
	var text := EventDialog.format_cost_summary({"attention": 0})
	assert_eq(text, " (Free)", "a zero-valued cost entry must read as Free, not '0 Attention'")

func test_format_cost_summary_reputation_cost_shown():
	# Regression: reputation-only costs (e.g. compute_deal's "Negotiate Better Terms") must
	# not be silently dropped -- only money/attention had bespoke handling historically.
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

func test_declineignore_style_outs_cost_zero_attention():
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
				var ap_cost = option.get("costs", {}).get("attention", 0)
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
	var text: String = ui._format_costs_inline({"attention": 2, "money": 8000, "reputation": 1})
	assert_string_contains(text, "2 Attention")
	assert_string_contains(text, "$8,000")
	assert_string_contains(text, "1 Rep")
	ui.free()

func test_costs_affordable_uses_month_plan_attention():
	# Regression for the AP-skip bug found during the sweep: a state whose monthly
	# Attention budget is fully committed
	# (available_ap == 0) must NOT read as affordable for an AP-costing option.
	var ui = _main_ui_script.new()
	var state := {"attention": 0, "money": 100000}
	assert_false(ui._costs_affordable({"attention": 1}, state),
		"the month plan's spendable Attention must gate affordability")
	assert_true(ui._costs_affordable({"money": 50000}, state),
		"a money-only cost within budget should be affordable")
	assert_false(ui._costs_affordable({"money": 200000}, state),
		"a money-only cost beyond budget should be unaffordable")
	ui.free()

func test_costs_affordable_free_option_always_affordable():
	var ui = _main_ui_script.new()
	assert_true(ui._costs_affordable({}, {}), "a free option is always affordable regardless of state")
	ui.free()


# --- The window's OWN Attention price reaches the button face (playtest 2026-08-10) --------
#
# A response window charges WindowResolver.attention_cost(event) -- a price that lives on the
# EVENT and appears in no option's costs dict. strip_attention() then erased any declared
# Attention before the dialog ever saw the event, so the founder currency was spent with the
# label saying "($500)" or, on the free-out, "(Free)". Pip, on the stray cat: "Adopting the
# cat also costs attention, which is not advertised on the screen."
#
# These lock the disclosure, not the price. Nothing here asserts a cost VALUE that gameplay
# owns -- they compare the label against WindowResolver's own accessors, so a rebalance moves
# both together and only a DIVERGENCE fails.

func _event_by_id(event_id: String) -> Dictionary:
	GameEvents.reload_definitions()
	for event in GameEvents.get_all_events():
		if String(event.get("id", "")) == event_id:
			return event
	return {}

func _option_by_id(event: Dictionary, option_id: String) -> Dictionary:
	for option in event.get("options", []):
		if option is Dictionary and String(option.get("id", "")) == option_id:
			return option
	return {}

func test_stray_cat_priced_options_advertise_the_window_attention():
	# The reported bug, pinned on the exact event. Adopting and feeding are HANDLEs, so they
	# draw the window's Attention on top of their money -- and must say so on the face.
	var cat := _event_by_id("stray_cat")
	assert_false(cat.is_empty(), "stray_cat event still exists in the event data")
	var shown := WindowResolver.present_for_dialog(cat)
	for option_id in ["adopt_cat", "feed_and_release"]:
		var option := _option_by_id(shown, option_id)
		assert_false(option.is_empty(), "stray_cat still has option %s" % option_id)
		var text := EventDialog.format_cost_summary(
			EventDialog.costs_with_window_attention(shown, option))
		assert_string_contains(text, "Attention",
			"%s spends founder Attention and must advertise it on the button face" % option_id)

func test_stray_cat_free_out_is_not_surcharged():
	# shoo_away resolves as IGNORE (WindowResolver.ignore_option_id picks the first option with
	# an empty costs dict), which draws NO Attention. Labelling it would be the opposite lie.
	var cat := _event_by_id("stray_cat")
	var shown := WindowResolver.present_for_dialog(cat)
	assert_eq(WindowResolver.ignore_option_id(cat), "shoo_away",
		"shoo_away is the auto-detected free-out; the label below depends on that")
	var option := _option_by_id(shown, "shoo_away")
	assert_eq(EventDialog.window_attention_for_option(shown, option), 0,
		"the IGNORE option pays no Attention, so it must not be surcharged on the face")

func test_free_out_label_tracks_the_resolver_not_a_hardcoded_id():
	# Anti-drift: the option the LABEL treats as free must be the same one RESOLUTION treats as
	# free, for every window-tier popup -- not a name the UI happens to recognise.
	GameEvents.reload_definitions()
	var checked := 0
	for event in GameEvents.get_all_events():
		if not EventTiers.is_window(event) or EventTiers.is_unignorable(event):
			continue
		var shown := WindowResolver.present_for_dialog(event)
		var free_id := WindowResolver.ignore_option_id(event)
		if free_id == "":
			continue
		var option := _option_by_id(shown, free_id)
		if option.is_empty():
			continue
		checked += 1
		assert_eq(EventDialog.window_attention_for_option(shown, option), 0,
			"%s/%s resolves as IGNORE (no Attention drawn) but the face would surcharge it" % [
				event.get("id", "?"), free_id])
	assert_gt(checked, 0, "the sweep must actually have inspected some windows")

func test_every_charging_window_option_now_shows_attention():
	# The class, not the instance. Every non-free option of every window-tier popup draws
	# attention_cost(event); before this lock, all of them rendered money-only or " (Free)".
	GameEvents.reload_definitions()
	var silent: Array[String] = []
	var checked := 0
	for event in GameEvents.get_all_events():
		if not EventTiers.is_window(event):
			continue
		var shown := WindowResolver.present_for_dialog(event)
		if WindowResolver.attention_cost(event) <= 0:
			continue
		for option in shown.get("options", []):
			if not (option is Dictionary):
				continue
			if EventDialog.window_attention_for_option(shown, option) <= 0:
				continue  # the free-out, covered by its own test above
			checked += 1
			var text := EventDialog.format_cost_summary(
				EventDialog.costs_with_window_attention(shown, option))
			if not text.contains("Attention"):
				silent.append("%s/%s -> %s" % [event.get("id", "?"), option.get("id", "?"), text])
	assert_gt(checked, 0, "the sweep must actually have inspected some charging options")
	assert_eq(silent.size(), 0,
		"these window options draw founder Attention without saying so: %s" % [silent])

func test_unstamped_events_claim_nothing():
	# The negative control, and the reason the price is STAMPED rather than recomputed in the
	# UI. Plan-phase legacy popups and the synthetic month review reach the dialog WITHOUT
	# going through present_for_dialog; their options are un-stripped and self-describing, so
	# an un-stamped event must add no surcharge at all.
	var raw := {"id": "unstamped", "type": "popup", "options": [
		{"id": "act", "text": "Act", "costs": {"money": 100}},
	]}
	var option := _option_by_id(raw, "act")
	assert_eq(EventDialog.window_attention_for_option(raw, option), 0,
		"no display stamp means no claim -- the UI must not re-derive resolution policy")
	assert_eq(EventDialog.costs_with_window_attention(raw, option), {"money": 100},
		"an un-stamped option's shown costs are exactly its declared costs")

func test_declared_attention_is_not_billed_twice_on_the_label():
	# An option whose own costs still carry `attention` is an UN-stripped legacy event.
	# format_cost_summary already prints that number; adding the window price on top would
	# show one charge as two.
	var event := {"id": "legacy", "type": "popup",
		WindowResolver.DISPLAY_ATTENTION_KEY: 1,
		WindowResolver.DISPLAY_FREE_OPTION_KEY: "",
		"options": [{"id": "act", "text": "Act", "costs": {"attention": 2}}]}
	var option := _option_by_id(event, "act")
	assert_eq(EventDialog.window_attention_for_option(event, option), 0,
		"a declared Attention cost is already on the face; do not add the window price to it")

func test_option_verbs_windows_are_not_double_labelled():
	# #789 hiring accept-prompts write the price INTO the option text ("Set them up now
	# (2 Att from reserve)"), so present_for_dialog stamps zero and the generic suffix stays
	# out of the way.
	var event := {"id": "hiring_onboard", "type": "popup",
		"window": {"attention_cost": 2, "option_verbs": {"provision_reserve": "handle_reserve"}},
		"options": [{"id": "provision_reserve", "text": "Set them up now (2 Att from reserve)"}]}
	var shown := WindowResolver.present_for_dialog(event)
	var option := _option_by_id(shown, "provision_reserve")
	assert_eq(EventDialog.window_attention_for_option(shown, option), 0,
		"an option whose text already names the price must not also get the generic suffix")

func test_month_review_door_is_still_free_and_prefix_free():
	# B2/B3 guard: is_navigation_popup reads the RAW option costs, so folding the window price
	# into the display must not turn the month-review door back into a priced decision.
	var review := {"id": "month_review", "type": "popup",
		"options": [{"id": "begin", "text": "Begin planning August 2017", "costs": {}}]}
	assert_true(EventDialog.is_navigation_popup(review),
		"the month review is a door, not a decision -- no price tag, no letter prefix")

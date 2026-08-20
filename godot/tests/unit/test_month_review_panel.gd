extends GutTest
## The month review as a diegetic clipboard (Pip, 2026-08-14: "can take up a lot more of the
## screen space ... the month review screen could come in, like, clipboard form or some other
## diegetic form").
##
## Nothing here proves the screen LOOKS right -- only Pip's eyes can do that, same caveat as
## test_month_review_navigation. What these tests CAN hold is the three things a restyle
## silently breaks:
##
##   1. Not one word of Pip's copy is dropped by the re-typesetting. The panel now splits the
##      review across a masthead, a callout, two columns and a footer instead of printing one
##      string, and the failure mode of that kind of change is a line quietly going missing.
##   2. The presentation payload and the plain-text description never disagree. The WATCH feed
##      records the text (A10); if the panel and the record drifted, two "copies" of the same
##      month would say different things.
##   3. The panel is actually bigger, and the ADR-0015 doom rule survives the new payload.

const GameManagerScript := preload("res://scripts/game_manager.gd")

## The generic event dialog's fixed footprint (event_dialog.gd), the thing "double or triple
## the area" is measured against.
const GENERIC_DIALOG_AREA := 600.0 * 450.0


func _gm() -> Node:
	var gm: Node = GameManagerScript.new()
	autofree(gm)
	return gm


func _stats(money: float, doom: float, staff: int) -> Dictionary:
	return {"money": money, "doom": doom, "staff": staff}


func _payload() -> Dictionary:
	"""A review payload in the shape game_manager._finish_month_playback emits."""
	return {
		"heading": "Month Review",
		"period": "October 2017",
		"lede": "October 2017 begins.",
		"attention": "Attention: 20 fresh decisions this month (last month's unspent reserve evaporated -- no banking).",
		"movement_title": "Last month's movement",
		"movement": _gm()._collect_month_movement_rows(
			_stats(1119896.0, 25.3, 3), _stats(1083712.0, 25.3, 2)),
		"rivals_title": "Rivals this month",
		"rivals": [
			{"name": "DeepSafety", "focus": "safety", "drift": "capabilities flat", "heat": 0,
				"line": "  DeepSafety (safety) -- capabilities flat"},
			{"name": "CapabiliCorp", "focus": "capabilities", "drift": "capabilities climbing fast",
				"heat": 3, "line": "  CapabiliCorp (capabilities) -- capabilities climbing fast"},
		],
		"closing": "Queue this month's actions, then press COMMIT THE MONTH to play the month out.",
	}


func _texts(node: Node, out: Array[String] = []) -> Array[String]:
	"""Every Label string in a built subtree, so a test can ask what the sheet actually says."""
	if node is Label:
		out.append((node as Label).text)
	for child in node.get_children():
		_texts(child, out)
	return out


func _build_sheet(payload: Dictionary) -> Panel:
	var dialog := Panel.new()
	autofree(dialog)
	MonthReviewPanel.apply_geometry(dialog, Vector2(1920, 1080))
	MonthReviewPanel.build(dialog, {"review": payload})
	return dialog


# --- routing: which events get the clipboard ------------------------------------------------

func test_a_review_payload_selects_the_clipboard() -> void:
	assert_true(MonthReviewPanel.is_month_review({"review": _payload()}))


func test_an_ordinary_event_does_not() -> void:
	# Every crisis window and flavour popup must keep the generic forest-green dialog.
	assert_false(MonthReviewPanel.is_month_review(
		{"id": "some_crisis", "name": "X", "description": "y", "options": []}))


func test_an_empty_or_malformed_payload_falls_back_to_the_generic_dialog() -> void:
	# Keyed on the payload rather than on MONTH_REVIEW_EVENT_ID precisely so a review built
	# without one degrades to a dialog that still renders "description" in full, instead of
	# handing the player an empty clipboard they cannot dismiss.
	assert_false(MonthReviewPanel.is_month_review({"review": {}}))
	assert_false(MonthReviewPanel.is_month_review({"review": "not a dictionary"}))
	assert_false(MonthReviewPanel.is_month_review({}))


# --- the ask: double to triple the area ------------------------------------------------------

func test_the_clipboard_is_between_two_and_three_and_a_half_times_the_generic_panel() -> void:
	# "can take up a lot more of the screen space, like, double or triple the area". The upper
	# bound is here so a later tweak cannot quietly grow it into a full-screen takeover.
	for viewport in [Vector2(1920, 1080), Vector2(1600, 900), Vector2(1280, 720)]:
		var dialog := Panel.new()
		autofree(dialog)
		MonthReviewPanel.apply_geometry(dialog, viewport)
		var ratio: float = (dialog.size.x * dialog.size.y) / GENERIC_DIALOG_AREA
		assert_between(ratio, 1.9, 3.5,
			"at %s the clipboard is %.2fx the generic dialog" % [viewport, ratio])


func test_the_clipboard_always_fits_on_screen() -> void:
	# A modal the player cannot fully see is worse than a small one -- and this one carries the
	# only button that closes it.
	for viewport in [Vector2(1920, 1080), Vector2(1366, 768), Vector2(1280, 720), Vector2(1024, 600)]:
		var dialog := Panel.new()
		autofree(dialog)
		MonthReviewPanel.apply_geometry(dialog, viewport)
		assert_true(dialog.position.x >= 0.0 and dialog.position.y >= 0.0,
			"at %s the clipboard starts off-screen at %s" % [viewport, dialog.position])
		assert_true(dialog.position.x + dialog.size.x <= viewport.x + 1.0,
			"at %s the clipboard runs off the right edge" % viewport)
		assert_true(dialog.position.y + dialog.size.y <= viewport.y + 1.0,
			"at %s the clipboard runs off the bottom edge" % viewport)


func test_the_review_darkens_the_screen_more_than_a_generic_event() -> void:
	# The occlusion complaint: at the generic 0.6 the WATCH feed behind the review still read at
	# close to full strength, so the review covered the month it was summarising. If this ever
	# drops back to 0.6 the panel is occluding the feed again.
	assert_gt(MonthReviewPanel.BACKDROP_ALPHA, 0.6,
		"the review must darken the office further than an ordinary popup does")
	assert_lte(MonthReviewPanel.BACKDROP_ALPHA, 1.0)


func test_the_type_went_up_two_to_four_points() -> void:
	# Pip, 2026-08-14: "the text can just all universally go up 2 to 4 points." Applied to this
	# panel only. Baselines are the generic dialog's: body 16, small 14, button 16.
	assert_between(MonthReviewPanel.SIZE_BODY, 18, 20)
	assert_between(MonthReviewPanel.SIZE_SMALL, 16, 18)
	assert_between(MonthReviewPanel.SIZE_BUTTON, 18, 20)


# --- Pip's words all survive the re-typesetting ----------------------------------------------

func test_every_line_of_the_review_reaches_the_sheet() -> void:
	# The whole risk of splitting one description string across a masthead, a callout box, two
	# columns and a footer is that a piece stops being rendered and nobody notices for months.
	var payload := _payload()
	var said := _texts(_build_sheet(payload))
	for key in ["heading", "period", "lede", "attention", "movement_title", "rivals_title", "closing"]:
		assert_has(said, String(payload[key]), "the sheet dropped the '%s' line" % key)


func test_every_movement_row_reaches_the_sheet_with_its_delta() -> void:
	var payload := _payload()
	assert_false(payload["movement"].is_empty(), "test precondition: this month moved")
	var said := _texts(_build_sheet(payload))
	for row in payload["movement"]:
		assert_has(said, "%s -> %s" % [row["from"], row["to"]])
		assert_has(said, String(row["delta"]), "a delta must still be printed, not just implied")
		assert_has(said, String(row["stat"]))


func test_every_rival_reaches_the_sheet_with_its_focus_and_drift() -> void:
	var said := _texts(_build_sheet(_payload()))
	for row in _payload()["rivals"]:
		assert_has(said, String(row["name"]))
		assert_has(said, String(row["focus"]))
		assert_has(said, String(row["drift"]))


func test_a_first_month_with_no_movement_and_no_rivals_still_renders() -> void:
	# Month 1 of a run, and any run resumed from a save: both blocks are empty by design
	# (A4). The sheet must still show the standing rule and the way out.
	var payload := _payload()
	payload["movement"] = []
	payload["rivals"] = []
	var said := _texts(_build_sheet(payload))
	assert_has(said, String(payload["attention"]))
	assert_has(said, String(payload["closing"]))


func test_the_sheet_prints_no_doom_percentage() -> void:
	# ADR-0015 guard, carried onto the new surface. The old one (test_month_review_movement)
	# only sees the string; this one sees what is actually drawn.
	var payload := _payload()
	payload["movement"] = _gm()._collect_month_movement_rows(
		_stats(102000.0, 5.0, 3), _stats(84200.0, 95.0, 4))
	for text in _texts(_build_sheet(payload)):
		assert_false(text.contains("%"), "no doom percentage may reach the sheet: got '%s'" % text)


# --- payload and plain text cannot drift ------------------------------------------------------

func test_the_payload_rows_and_the_feed_text_are_the_same_content() -> void:
	# The review is recorded into the WATCH feed as text (A10) and drawn from rows. Both are
	# built from ONE collection, and this is the assertion that keeps it that way: every row's
	# parts must appear in the line the feed records for that row.
	var gm := _gm()
	var rows: Array = gm._collect_month_movement_rows(
		_stats(1119896.0, 25.3, 3), _stats(1083712.0, 25.3, 2))
	assert_false(rows.is_empty())
	var text: String = gm._format_month_movement_section(rows)
	for row in rows:
		assert_string_contains(text, String(row["stat"]))
		assert_string_contains(text, String(row["from"]))
		assert_string_contains(text, String(row["to"]))
		assert_string_contains(text, String(row["delta"]))


func test_movement_rows_carry_the_display_sign_the_hud_uses() -> void:
	# main_ui._render_delta_chip: doom rising is bad, everything else rising is good. The sheet
	# colours its deltas off this sign, so an inverted one would print a loss in green.
	var gm := _gm()
	var lost: Array = gm._collect_month_movement_rows(_stats(100.0, 10.0, 3), _stats(50.0, 10.0, 3))
	assert_eq(int(lost[0]["sign"]), -1, "a month that lost money must read as adverse")
	var gained: Array = gm._collect_month_movement_rows(_stats(50.0, 10.0, 3), _stats(100.0, 10.0, 3))
	assert_eq(int(gained[0]["sign"]), 1)

	assert_true(ThemeManager.get_doom_band_index(5.0) < ThemeManager.get_doom_band_index(95.0),
		"test precondition: 5%% and 95%% doom must be different bands")
	var doom_up: Array = _gm()._collect_month_movement_rows(_stats(1.0, 5.0, 3), _stats(1.0, 95.0, 3))
	assert_eq(int(doom_up[0]["sign"]), -1, "doom crossing UP is the adverse direction")
	var doom_down: Array = _gm()._collect_month_movement_rows(_stats(1.0, 95.0, 3), _stats(1.0, 5.0, 3))
	assert_eq(int(doom_down[0]["sign"]), 1)


func test_rival_heat_bands_agree_with_the_words_beside_them() -> void:
	# heat is what colours a rival card. If the bands and RivalLabs.capability_drift_label ever
	# used different cuts, a card could say "flat" in the running-away colour.
	var expected := {
		0: "capabilities flat",
		1: "capabilities slipping",
		2: "capabilities rising",
		3: "capabilities climbing fast",
	}
	var deltas := {0: 0.0, 1: -5.0, 2: 2.0, 3: 10.0}
	for heat in expected.keys():
		assert_eq(RivalLabs.capability_drift_label(deltas[heat]), expected[heat],
			"heat band %d and its label must describe the same movement" % heat)
	assert_eq(MonthReviewPanel.HEAT_INKS.size(), expected.size(),
		"every heat band needs an ink, and no ink may be unreachable")


# --- through the real presenter ---------------------------------------------------------------

func _present(event: Dictionary) -> Array:
	"""Drive EventDialog for real -- the branch added to _show_next_event is the part a unit test
	of the builder alone would miss. Returns [dialog, buttons] as the presenter handed them to
	its host. The caller frees the dialog; its tree_exited hook takes the blocker with it."""
	var presenter := EventDialog.new()
	add_child_autofree(presenter)
	presenter.state_provider = func(): return {}
	var opened: Array = []
	presenter.dialog_opened.connect(func(dialog, buttons): opened.append([dialog, buttons]))
	presenter.present(event)
	await wait_frames(2)
	assert_eq(opened.size(), 1, "the presenter opened exactly one dialog")
	return opened[0] if opened.size() == 1 else [null, []]


func _review_event() -> Dictionary:
	var payload := _payload()
	return {
		"id": "__month_review__",
		"name": "Month Review -- October 2017",
		"description": "%s\n\n%s\n\n%s" % [payload["lede"], payload["attention"], payload["closing"]],
		"type": "popup",
		"options": [{"id": "begin_planning", "text": "Begin planning October 2017", "costs": {}, "effects": {}}],
		"review": payload,
	}


func test_the_presenter_puts_the_review_on_the_clipboard() -> void:
	var opened: Array = await _present(_review_event())
	var dialog: Control = opened[0]
	assert_not_null(dialog)
	var area: float = dialog.size.x * dialog.size.y
	assert_gt(area / GENERIC_DIALOG_AREA, 1.9,
		"the review must not come back as the 600x450 generic panel")
	assert_has(_texts(dialog), "Month Review")
	dialog.queue_free()


func test_the_review_keeps_every_behaviour_the_playtests_pinned() -> void:
	# B1/B2/B3 and the one-button contract. The restyle shares the presenter's button loop
	# precisely so none of this had to be re-implemented -- this asserts it did not have to.
	var opened: Array = await _present(_review_event())
	var dialog: Control = opened[0]
	var buttons: Array = opened[1]
	assert_eq(buttons.size(), 1, "the review is a door: exactly one option")
	assert_true(dialog.get_meta("space_advances", false), "B1: SPACE still opens the door")
	assert_true(dialog.get_meta("is_event_dialog", false), "#452: ESC still must not close it")
	var face: String = buttons[0].text
	assert_string_contains(face, "[SPACE]")
	assert_false(face.contains("(Free)"), "B2: no price tag on a door that was never for sale")
	assert_false(face.contains("[Q]"), "B2: no letter-menu prefix on a one-option popup")
	assert_false(buttons[0].disabled, "a costless door can never be unaffordable")
	dialog.queue_free()


func test_an_ordinary_event_still_gets_the_generic_dialog() -> void:
	# The other half of the branch: every crisis window must be untouched by this change, at the
	# original 600x450, still printing its whole description as one label.
	var opened: Array = await _present({
		"id": "some_crisis",
		"name": "A Crisis",
		"description": "Something happened and you must choose.",
		"type": "popup",
		"options": [
			{"id": "handle", "text": "Handle it", "costs": {"money": 20000}},
			{"id": "ignore", "text": "Ignore it", "costs": {}},
		],
	})
	var dialog: Control = opened[0]
	assert_eq(dialog.size, Vector2(600, 450), "ordinary events keep the generic footprint")
	var said := _texts(dialog)
	assert_has(said, "A Crisis")
	assert_has(said, "Something happened and you must choose.")
	assert_eq(opened[1].size(), 2)
	dialog.queue_free()


# --- the art slot ------------------------------------------------------------------------------

func test_the_declared_surface_art_is_actually_packed() -> void:
	# Both surfaces are pre-existing assets under godot/assets/ -- nothing was promoted for this
	# panel. If either is ever moved or retired, the panel silently degrades to a flat fill, so
	# this is the only place that would notice.
	for path in [MonthReviewPanel.BOARD_TEXTURE_PATH, MonthReviewPanel.PAPER_TEXTURE_PATH]:
		if path == "":
			continue  # an emptied slot is a legitimate configuration, not a failure
		assert_true(ResourceLoader.exists(path), "declared surface art is missing: %s" % path)


func test_a_missing_surface_texture_does_not_break_the_sheet() -> void:
	# The degradation path, exercised for real: a sheet built while the art slot points nowhere
	# must still carry every word. This is what stops a retired asset turning the month boundary
	# into an undismissable modal.
	var dialog := Panel.new()
	autofree(dialog)
	MonthReviewPanel.apply_geometry(dialog, Vector2(1920, 1080))
	MonthReviewPanel._add_surface(dialog, "res://assets/textures/surfaces/__no_such_file__.png",
		Color.WHITE, 2)
	MonthReviewPanel.build(dialog, {"review": _payload()})
	assert_has(_texts(dialog), "Month Review")

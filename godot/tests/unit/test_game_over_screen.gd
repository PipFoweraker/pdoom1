extends GutTest
## Defeat-screen legibility tests (#580): the screen must name the REAL cause of death
## (reputation<=0 was previously falling through to a generic message) and surface the
## ledger death-attribution that already exists in state.

func test_defeat_reason_reputation_zero_is_named():
	var s = GameOverScreen.new()
	var reason = s._get_defeat_reason({"doom": 45.0, "reputation": 0.0, "money": 5000})
	assert_true(reason.to_lower().contains("reputation") or reason.to_lower().contains("credibility"),
		"reputation death should be named, got: %s" % reason)
	assert_false(reason.to_lower().contains("prematurely"),
		"reputation death should NOT fall through to the generic reason")
	s.free()

func test_defeat_reason_doom_is_named():
	var s = GameOverScreen.new()
	var reason = s._get_defeat_reason({"doom": 100.0, "reputation": 50.0})
	assert_true(reason.to_lower().contains("doom"), "doom death should be named")
	s.free()

func test_defeat_reason_generic_fallback():
	var s = GameOverScreen.new()
	# No loss condition met -> generic (shouldn't normally happen, but must be safe)
	var reason = s._get_defeat_reason({"doom": 50.0, "reputation": 50.0, "money": 5000})
	assert_gt(reason.length(), 0, "always returns a reason string")
	s.free()

func test_ledger_attribution_shown_when_present():
	var s = GameOverScreen.new()
	var state = {"ledger": {"death_attribution": [
		{"source": "loan", "currency": "money", "magnitude": 115517.0},
		{"source": "loan", "currency": "money", "magnitude": 167940.0}
	]}}
	var txt = s._get_ledger_attribution_text(state)
	assert_gt(txt.length(), 0, "attribution should be shown when present")
	assert_true(txt.to_lower().contains("loan"), "should name the source(s)")
	s.free()

func test_ledger_attribution_empty_when_absent():
	var s = GameOverScreen.new()
	assert_eq(s._get_ledger_attribution_text({"ledger": {"death_attribution": []}}), "")
	assert_eq(s._get_ledger_attribution_text({}), "")
	s.free()

# --- Issue #734: shareable "Copy result" one-liner (pure static helper) -------------------

func test_share_line_matches_the_example():
	# The example from the issue must render verbatim (ASCII "--" dash, "P(Doom)1" brand name).
	var line = GameOverScreen.format_share_line(14, 62.0, "weekly-2026-w29", "0.11.0")
	assert_eq(line, "I survived 14 months at 62% doom on seed weekly-2026-w29 -- P(Doom)1 v0.11.0")

func test_share_line_rounds_doom_to_whole_percent():
	var line = GameOverScreen.format_share_line(3, 61.6, "seed-x", "0.12.0")
	assert_true(line.contains("62% doom"), "doom rounds to nearest whole percent, got: %s" % line)

func test_share_line_is_single_ascii_line():
	var line = GameOverScreen.format_share_line(1, 5.0, "abc", "0.11.0")
	assert_false(line.contains("\n"), "the share line must be a single clipboard line")
	assert_true(line.contains(" -- "), "uses the ASCII double-hyphen dash, not a unicode em-dash")

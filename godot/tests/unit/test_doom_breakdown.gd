extends GutTest
## Unit tests for DoomBreakdown — the #578 colour-coded per-source doom "blow-by-blow".
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
	var sources := {
		"base": 1.0,
		"rivals": 12.3,
		"safety": -14.4,
		"momentum": 0.0,       # exactly zero — omitted
		"specializations": 0.01,  # negligible — omitted
	}
	var entries := DoomBreakdown.build_entries(sources)
	assert_eq(entries.size(), 3, "Only non-zero sources should be shown")
	var keys: Array = []
	for e in entries:
		keys.append(e["key"])
	assert_does_not_have(keys, "momentum", "Zero source omitted")
	assert_does_not_have(keys, "specializations", "Negligible source omitted")

func test_build_entries_signed_text_and_labels():
	var entries := DoomBreakdown.build_entries({"rivals": 12.3, "safety": -14.4})
	# Sorted by descending magnitude: safety (14.4) before rivals (12.3).
	assert_eq(entries[0]["text"], "Safety -14.4", "Negative source shows human label + signed value")
	assert_eq(entries[0]["sign"], -1, "Safety pulls doom down")
	assert_eq(entries[1]["text"], "Rivals +12.3", "Positive source shows explicit + sign")
	assert_eq(entries[1]["sign"], 1, "Rivals push doom up")

func test_build_entries_sorted_by_magnitude():
	var entries := DoomBreakdown.build_entries({
		"base": 1.0,
		"rivals": 12.3,
		"safety": -14.4,
	})
	assert_eq(entries[0]["key"], "safety", "Biggest mover (|14.4|) first")
	assert_eq(entries[1]["key"], "rivals", "Then |12.3|")
	assert_eq(entries[2]["key"], "base", "Then |1.0|")

func test_label_for_known_and_unknown_keys():
	assert_eq(DoomBreakdown.label_for("technical_debt"), "Technical Debt", "Known key uses friendly label")
	assert_eq(DoomBreakdown.label_for("market_pressure"), "Market Pressure", "Known key uses friendly label")
	# Unknown key falls back to a capitalized rendering rather than crashing.
	assert_eq(DoomBreakdown.label_for("some_new_source"), "Some New Source", "Unknown key capitalizes")

func test_build_entries_empty_when_all_zero():
	var entries := DoomBreakdown.build_entries({"base": 0.0, "rivals": 0.0})
	assert_eq(entries.size(), 0, "All-zero sources produce an empty (hidden) breakdown")

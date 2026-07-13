extends GutTest
## L1 (#612 / workshop#3 addendum #1-2, ADR-0012): event delivery-tier classification.

func test_explicit_tiers_classify():
	assert_eq(EventTiers.tier_of({"delivery_tier": "ambient"}), "ambient")
	assert_eq(EventTiers.tier_of({"delivery_tier": "feed"}), "feed")
	assert_eq(EventTiers.tier_of({"delivery_tier": "window"}), "window")


func test_legacy_popup_with_options_defaults_to_window():
	# Behaviour-preserving: pre-L1 popups all demanded a decision.
	var ev := {"type": "popup", "options": [{"id": "ok"}]}
	assert_eq(EventTiers.tier_of(ev), "window", "un-annotated popups stay decision-demanding")


func test_source_id_provenance_with_fallback():
	assert_eq(EventTiers.source_id_of({"source_id": "gov_liaison"}), "gov_liaison")
	assert_eq(EventTiers.source_id_of({"category": "funding"}), "funding", "falls back to category")
	assert_eq(EventTiers.source_id_of({}), "unknown", "last-resort provenance")


func test_class_governs_legal_responses():
	var unsnoozable := {"delivery_tier": "window", "event_class": "un-snoozable"}
	var verbs := EventTiers.legal_responses(unsnoozable)
	assert_false(verbs.has("defer"), "un-snoozable does not sell DEFER")
	assert_true(verbs.has("ignore"), "but IGNORE at list price is available")

	var deferrable := {"delivery_tier": "window", "event_class": "deferrable"}
	assert_true(EventTiers.legal_responses(deferrable).has("defer"), "deferrable sells DEFER")


func test_unignorable_removes_ignore():
	var ev := {"delivery_tier": "window", "event_class": "un-snoozable", "unignorable": true}
	var verbs := EventTiers.legal_responses(ev)
	assert_false(verbs.has("ignore"), "an unignorable window cannot be ignored")
	assert_true(EventTiers.is_unignorable(ev))


func test_defer_allowed_only_for_deferrable():
	assert_true(EventTiers.defer_allowed({"event_class": "deferrable"}))
	assert_false(EventTiers.defer_allowed({"event_class": "un-snoozable"}))
	assert_false(EventTiers.defer_allowed({"event_class": "standing"}))


func test_partition_splits_the_stream():
	var events := [
		{"delivery_tier": "ambient"},
		{"delivery_tier": "feed", "source_id": "a"},
		{"delivery_tier": "feed", "source_id": "b"},
		{"type": "popup", "options": [{"id": "x"}]},  # -> window
	]
	var parts := EventTiers.partition(events)
	assert_eq((parts.ambient as Array).size(), 1, "one ambient")
	assert_eq((parts.feed as Array).size(), 2, "two feed items")
	assert_eq((parts.windows as Array).size(), 1, "one window demands a decision")

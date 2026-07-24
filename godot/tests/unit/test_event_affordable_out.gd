extends GutTest
## Outs sweep (launch guard, L2). Every player-CHOICE event must offer at least one
## AFFORDABLE OUT: an option that costs neither money nor action_points, so a money-
## constrained OR Attention-constrained player always has a legible legal response and
## can never be walled by an event. This guards two option sources:
##   1. the data-driven core events (GameEvents.get_all_events -> core_events.json), and
##   2. the EventService category-option generator (historical / pdoom-data events).
## A month-controller auto-lapse safety net exists too, but this asserts the OUT is a real
## CHOICE the player can pick -- not something the engine silently does for them.

const CONSTRAINED := ["money", "action_points"]


func _has_affordable_out(options: Array) -> bool:
	# An out = an option that spends none of the constrained resources (may cost reputation,
	# take a downstream hit, or cost nothing). costs:{} always qualifies.
	for o in options:
		if not (o is Dictionary):
			continue
		var costs: Dictionary = o.get("costs", {})
		var walled := false
		for k in CONSTRAINED:
			if costs.has(k) and float(costs[k]) > 0.0:
				walled = true
				break
		if not walled:
			return true
	return false


func test_every_core_event_has_an_affordable_out():
	GameEvents.reload_definitions()
	var events := GameEvents.get_all_events()
	assert_gt(events.size(), 0, "core events loaded from JSON")
	for ev in events:
		var options: Array = ev.get("options", [])
		if options.is_empty():
			continue  # non-choice / auto-applied event -- no dead-end is possible
		assert_true(_has_affordable_out(options),
			"core event '%s' must offer an option costing neither money nor action_points" % String(ev.get("id", "?")))


func test_every_event_service_category_has_an_affordable_out():
	# The category generator branches on category; each branch must yield an out. Covers the
	# named categories plus the default fallback (an unknown category).
	var categories := ["organization", "organization_founding", "research", "paper",
		"policy", "regulation", "incident", "capability", "funding_catastrophe", "funding",
		"unmapped_category_fallback"]
	var raw := {"impacts": [], "rarity": "common"}
	for cat in categories:
		var options: Array = EventService._generate_options(raw, cat, 5)
		assert_gt(options.size(), 0, "category '%s' generated options" % cat)
		assert_true(_has_affordable_out(options),
			"EventService category '%s' must offer an affordable out" % cat)

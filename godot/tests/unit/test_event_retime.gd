extends GutTest
## Retime + promotion pass (#1125 / #1111): historical events must land in the
## ruled ERA under the month-per-turn dial, the week dial must rescale them, and
## every override key must target a record that actually exists (example.json
## shipped 2 dead keys for months -- that failure mode is a red test now).
##
## Uses a FRESH EventService instance (not the autoload) so nothing here mutates
## the live deck other tests isolate against (#534).

const EventServiceScript = preload("res://autoload/event_service.gd")
const CORPUS_PATH := "res://data/historical_events.json"
const OVERRIDES_DIR := "res://data/events/overrides/"

# Expected firing turns under month_per_turn (12/yr):
# base_turn(year) = (year-2017)*12 + 1; legendary fires base+6.
const LEGENDARY_TURNS := {
	"hist_microsoft_tay_2016": 7,             # year overridden to 2017
	"hist_gpt2_staged_release_2019": 31,
	"hist_distill_ed5ab808068ad61f": 43,      # Circuits, 2020
	"hist_anthropic_exodus_2021": 55,
	"hist_ftx_future_fund_collapse_2022": 67,
	"hist_openai_board_crisis_2023": 79,
	"hist_anthropic_alignment_faking_2024": 91,
	"hist_claude_4_opus_blackmail_2025": 103,
}

# Rare promotions: eligibility_start == base_turn (spread 3, window 6).
const RARE_ELIGIBILITY := {
	"hist_rlhf_origin_2017": 1,
	"hist_google_project_maven_2018": 13,
	"hist_emergent_tool_use_2019": 25,
	"hist_training_data_extraction_2020": 37,
	"hist_cais_ftx_clawback_2023": 73,
	"hist_openai_safety_team_departures_2024": 85,
	"hist_ai_sandbagging_research_2024": 85,
	"hist_apollo_scheming_evals_2024": 85,
	"hist_metr_deceptive_ai_evaluation_2024": 85,
	"hist_international_coordination_breakdown_2025": 97,
}

# Common promotions: trigger_turn == max(10, base_turn).
const COMMON_TURNS := {
	"hist_reward_modeling_agenda_2018": 13,
	"hist_tesla_autopilot_incidents_2016_2024": 13,
	"hist_distill_eb5c12bc89464f38": 25,      # social scientists, 2019
	"hist_webgpt_browsing_2021": 49,
	"hist_truthfulqa_benchmark_2021": 49,
	"hist_red_teaming_lms_2022": 61,
}

var svc


func before_each():
	svc = EventServiceScript.new()
	autofree(svc)
	svc._load_variable_mapping()
	svc._load_rarity_curves()
	svc._load_overrides()


func _load_corpus_into(service) -> void:
	assert_true(service._load_bundled_data(), "bundled historical corpus should load")


func _find(service, event_id: String) -> Dictionary:
	for ev in service.transformed_events:
		if ev.get("id", "") == event_id:
			return ev
	return {}


func _parse_json_file(path: String) -> Dictionary:
	var file = FileAccess.open(path, FileAccess.READ)
	assert_not_null(file, "should open %s" % path)
	var json = JSON.new()
	assert_eq(json.parse(file.get_as_text()), OK, "should parse %s" % path)
	file.close()
	var data = json.get_data()
	assert_true(data is Dictionary, "%s should be a dictionary" % path)
	return data


func test_month_dial_is_active_and_calendar_true():
	# THE GUARD: one turn = one month (#1125) means 12 turns per historical year.
	# If someone restores the old 52/yr numbers, everything dated 2022+ fires
	# past turn 287 -- beyond every observed run -- and the promotion pass
	# regresses to events nobody sees (the #1027 signature failure).
	assert_eq(str(svc._rarity_curves.get("timescale", "")), "month_per_turn",
		"month_per_turn is the shipped timescale")
	var yt = svc._rarity_curves.get("year_trigger", {})
	assert_eq(int(yt.get("turns_per_year", 0)), 12, "one turn = one month -> 12 turns/year")
	assert_eq(int(yt.get("legendary_month_offset", 0)), 6, "legendary beats land mid-year")
	assert_eq(int(yt.get("rare_spread_turns", 0)), 3, "rare spread scaled to month grain")
	assert_eq(int(svc._rarity_curves.get("rare", {}).get("eligibility_window_turns", 0)), 6,
		"rare eligibility window scaled to month grain")


func test_override_keys_all_exist_in_corpus():
	# Kills the example.json failure mode: an override keyed to a missing record
	# is a silent no-op that looks exactly like a working override.
	var corpus = _parse_json_file(CORPUS_PATH)
	var dir = DirAccess.open(OVERRIDES_DIR)
	assert_not_null(dir, "overrides dir should open")
	dir.list_dir_begin()
	var filename = dir.get_next()
	var checked := 0
	while filename != "":
		if not dir.current_is_dir() and filename.ends_with(".json"):
			var data = _parse_json_file(OVERRIDES_DIR + filename)
			for key in data.keys():
				if str(key).begins_with("_"):
					continue
				checked += 1
				assert_true(corpus.has(key),
					"%s: override key '%s' must exist in historical_events.json" % [filename, key])
		filename = dir.get_next()
	dir.list_dir_end()
	assert_gt(checked, 20, "the promotion pass overrides should be present and counted")


func test_promoted_events_land_in_their_era():
	_load_corpus_into(svc)
	assert_gt(svc.transformed_events.size(), 1100, "full corpus transformed")

	for event_id in LEGENDARY_TURNS.keys():
		var ev = _find(svc, event_id)
		assert_false(ev.is_empty(), "%s should exist after overrides" % event_id)
		if ev.is_empty():
			continue
		assert_eq(ev.get("trigger_type", ""), "turn_exact", "%s is a deterministic beat" % event_id)
		assert_eq(int(ev.get("trigger_turn", -1)), int(LEGENDARY_TURNS[event_id]),
			"%s fires in its era" % event_id)
		assert_lte(int(ev.get("trigger_turn", 999)), 110,
			"%s stays inside the realistic run band (deaths observed t14-229, best board 153)" % event_id)

	for event_id in RARE_ELIGIBILITY.keys():
		var ev = _find(svc, event_id)
		assert_false(ev.is_empty(), "%s should exist after overrides" % event_id)
		if ev.is_empty():
			continue
		assert_eq(int(ev.get("eligibility_start", -1)), int(RARE_ELIGIBILITY[event_id]),
			"%s becomes eligible at its historical date" % event_id)

	for event_id in COMMON_TURNS.keys():
		var ev = _find(svc, event_id)
		assert_false(ev.is_empty(), "%s should exist after overrides" % event_id)
		if ev.is_empty():
			continue
		assert_eq(int(ev.get("trigger_turn", -1)), int(COMMON_TURNS[event_id]),
			"%s becomes eligible at its historical date" % event_id)


func test_promoted_events_are_windows_not_flavour():
	_load_corpus_into(svc)
	var all_promoted := LEGENDARY_TURNS.keys() + RARE_ELIGIBILITY.keys() + COMMON_TURNS.keys()
	for event_id in all_promoted:
		var ev = _find(svc, event_id)
		assert_false(ev.is_empty(), "%s should exist" % event_id)
		if ev.is_empty():
			continue
		assert_ne(str(ev.get("delivery_tier", "")), "feed",
			"%s must not be flavour-demoted" % event_id)
		var options = ev.get("options", [])
		assert_gt(options.size(), 0, "%s has options" % event_id)
		if options.size() > 0:
			assert_ne(str(options[0].get("id", "")), "engage",
				"%s uses a real template, not the bland default" % event_id)

	# Spot-check template routing: category override picks the decision.
	var tay = _find(svc, "hist_microsoft_tay_2016")
	if not tay.is_empty():
		assert_eq(str(tay["options"][0].get("id", "")), "respond_publicly", "incident template")
	var exodus = _find(svc, "hist_anthropic_exodus_2021")
	if not exodus.is_empty():
		assert_eq(str(exodus["options"][0].get("id", "")), "collaborate", "organization template")
	var gpt2 = _find(svc, "hist_gpt2_staged_release_2019")
	if not gpt2.is_empty():
		assert_eq(str(gpt2["options"][0].get("id", "")), "support", "policy template")
	var ftx = _find(svc, "hist_ftx_future_fund_collapse_2022")
	if not ftx.is_empty():
		assert_eq(str(ftx["options"][0].get("id", "")), "emergency_fundraise", "funding template")

	# The flavour gate itself must survive the pass: an unpromoted arxiv record
	# stays on the feed tier.
	var still_flavour := 0
	for ev in svc.transformed_events:
		if str(ev.get("id", "")).begins_with("hist_arxiv_") and str(ev.get("delivery_tier", "")) == "feed":
			still_flavour += 1
	assert_gt(still_flavour, 1000, "the arxiv bulk stays flavour-demoted")


func test_ten_turn_grace_2018_content_stays_out_of_the_opening():
	# Pip's pacing frame (#1125): a player should be unlikely to die in the first
	# ten turns (= ten months), so a 2017 start reliably reaches 2018. Nothing
	# promoted and dated 2018+ may enter play inside that grace window.
	_load_corpus_into(svc)
	var all_promoted := LEGENDARY_TURNS.keys() + RARE_ELIGIBILITY.keys() + COMMON_TURNS.keys()
	for event_id in all_promoted:
		var ev = _find(svc, event_id)
		if ev.is_empty():
			continue
		if int(ev.get("year", 0)) >= 2018:
			assert_gte(int(ev.get("min_turn", 0)), 11,
				"%s (year %d) must not enter the 10-turn grace window" % [event_id, int(ev.get("year", 0))])


func test_week_dial_rescales_firing_turns():
	# The dial is the deliverable (#1111): flipping one string re-times the whole
	# corpus to week-per-turn pacing (52/yr -- the 'punished' variant).
	_load_corpus_into(svc)
	svc._rarity_curves["timescale"] = "week_per_turn"
	svc._resolve_timescale()
	svc._transform_all_events()

	var yt = svc._rarity_curves.get("year_trigger", {})
	assert_eq(int(yt.get("turns_per_year", 0)), 52, "week dial -> 52 turns/year")
	assert_eq(int(svc._rarity_curves.get("rare", {}).get("eligibility_window_turns", 0)), 26,
		"rare window rescales with the dial")

	var tay = _find(svc, "hist_microsoft_tay_2016")
	assert_eq(int(tay.get("trigger_turn", -1)), 27, "Tay under week pacing: (2017-2017)*52+1+26")
	var ftx = _find(svc, "hist_ftx_future_fund_collapse_2022")
	assert_eq(int(ftx.get("trigger_turn", -1)), 287, "FTX under week pacing: (2022-2017)*52+1+26")

extends GutTest
## Rivals become narratively visible (lane A, tier-S bundle).
##
## Pins the three player-facing guarantees:
##   1. A VISIBLE rival's turn surfaces a deadpan feed line (feed tier, never a window).
##   2. A HIDDEN rival's turn surfaces NOTHING.
##   3. A discovery fires exactly one reveal event.
## Plus the pure narration helpers (visibility gate, salience pick, drift label).
##
## Tests drive the real _step_* functions directly (same pattern as
## test_turn_manager's risk-pool tests) so no RNG is added and step order is untouched.

var state: GameState
var turn_manager: TurnManager


func before_each():
	# Isolate from the live historical timeline (see test_turn_manager.before_each).
	if EventService:
		EventService.transformed_events.clear()
	state = GameState.new("rivals_feed_seed")
	turn_manager = TurnManager.new(state)


func _make_rival(rname: String, aggression: float, visibility: int) -> RivalLabs.RivalLab:
	var r := RivalLabs.RivalLab.new(rname, aggression)
	r.visibility = visibility
	r.funding = 500000.0  # enough to guarantee non-fundraise capability actions
	return r


func _join_messages(results: Array) -> String:
	var joined := ""
	for r in results:
		joined += String(r.get("message", ""))
	return joined


# --- item 1: visible rivals surface, hidden rivals do not -------------------

func test_visible_rival_action_produces_feed_entry():
	var visible := _make_rival("CapabiliCorp", 0.9, RivalLabs.VisibilityState.KNOWN)
	state.rival_labs = [visible]
	var results: Array = []
	turn_manager._step_process_rival_turns(results)
	assert_gt(results.size(), 0, "A visible rival should surface at least one feed line")
	assert_string_contains(_join_messages(results), "CapabiliCorp",
		"Feed line names the visible rival")
	# Feed tier: carries the rivals channel and never a window/options payload.
	for r in results:
		assert_eq(String(r.get("channel", "")), "rivals", "rival feed line rides the rivals channel")
		assert_false(r.has("options"), "feed tier -- a rival line must never be a window/popup")


func test_hidden_rival_action_produces_no_feed_entry():
	var hidden := _make_rival("StealthLab", 0.9, RivalLabs.VisibilityState.HIDDEN)
	state.rival_labs = [hidden]
	var results: Array = []
	turn_manager._step_process_rival_turns(results)
	assert_eq(results.size(), 0, "A hidden rival must not surface any feed line")


func test_only_visible_rival_surfaces_in_mixed_field():
	var visible := _make_rival("DeepSafety", 0.3, RivalLabs.VisibilityState.KNOWN)
	var hidden := _make_rival("StealthLab", 0.9, RivalLabs.VisibilityState.HIDDEN)
	state.rival_labs = [visible, hidden]
	var results: Array = []
	turn_manager._step_process_rival_turns(results)
	var joined := _join_messages(results)
	assert_string_contains(joined, "DeepSafety", "Visible rival is narrated")
	assert_false(joined.contains("StealthLab"), "Hidden rival must never leak into the feed")


# --- item 3: discovery reveal is exactly one felt event ---------------------

func test_discovery_produces_exactly_one_reveal_event():
	var rumored := _make_rival("StealthAI", 0.5, RivalLabs.VisibilityState.RUMORED)
	rumored.discovery_threshold = 0.0
	state.rival_labs = [rumored]
	# reputation huge -> discovery_chance > 1 -> rng.randf() (< 1) always fires. No seed
	# dependence, no new RNG (check_discovery already owns this draw).
	state.reputation = 1000.0
	var results: Array = []
	turn_manager._step_check_rival_discovery(results)
	assert_eq(results.size(), 1, "Discovery fires exactly one reveal event")
	var msg := String(results[0].get("message", ""))
	assert_string_contains(msg, "INTEL", "Reveal is tagged intel")
	assert_string_contains(msg, "another lab", "Reveal uses the deadpan reveal register")
	assert_eq(String(results[0].get("channel", "")), "rivals", "Reveal rides the rivals channel")


func test_no_discovery_when_reputation_below_threshold():
	var rumored := _make_rival("StealthAI", 0.5, RivalLabs.VisibilityState.RUMORED)
	rumored.discovery_threshold = 100.0
	state.rival_labs = [rumored]
	state.reputation = 0.0  # below threshold -> discovery_chance stays 0 -> never fires
	var results: Array = []
	turn_manager._step_check_rival_discovery(results)
	assert_eq(results.size(), 0, "No reveal when reputation is below the discovery threshold")


# --- pure narration helpers -------------------------------------------------

func test_get_action_feed_line_gated_on_visibility():
	var hidden := _make_rival("Ghost", 0.9, RivalLabs.VisibilityState.HIDDEN)
	assert_eq(RivalLabs.get_action_feed_line(hidden, "capability_research"), "",
		"Hidden rival yields no line even when asked directly")
	var seen := _make_rival("Ghost", 0.9, RivalLabs.VisibilityState.KNOWN)
	assert_ne(RivalLabs.get_action_feed_line(seen, "capability_research"), "",
		"Visible rival yields a narrative line")
	assert_eq(RivalLabs.get_action_feed_line(seen, "not_a_real_action"), "",
		"Unknown action id yields no line")


func test_pick_headline_action_prefers_salient():
	assert_eq(RivalLabs.pick_headline_action(["buy_compute", "capability_research"]),
		"capability_research", "Reckless capability move outranks a quiet compute buy")
	assert_eq(RivalLabs.pick_headline_action(["safety_research"]), "safety_research",
		"Single action is the headline")
	assert_eq(RivalLabs.pick_headline_action([]), "", "Empty action list yields no headline")


func test_capability_drift_label_thresholds():
	assert_eq(RivalLabs.capability_drift_label(10.0), "capabilities climbing fast")
	assert_eq(RivalLabs.capability_drift_label(2.0), "capabilities rising")
	assert_eq(RivalLabs.capability_drift_label(0.0), "capabilities flat")
	assert_eq(RivalLabs.capability_drift_label(-5.0), "capabilities slipping")

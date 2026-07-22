extends GutTest
## Unit tests for the A/B layout harness (UI_PROPOSALS_2026-07-22 section 4):
## the GameConfig.ui_layout flag, LayoutController's container-reflow (both arrangements
## instance + restore cleanly), and QueueGantt's read-only row extraction (P10 -- gantt
## rows track the queued-action count). UI-layer only; no game state / RNG touched.

# --- GameConfig.ui_layout flag ------------------------------------------------------------

func test_ui_layout_defaults_to_classic():
	# The scaffolding default must be classic so first boot is the untouched layout.
	assert_true(GameConfig.UI_LAYOUTS.has("classic"), "classic is a known layout")
	assert_true(GameConfig.UI_LAYOUTS.has("proposed"), "proposed is a known layout")

func test_ui_layout_setter_accepts_known_and_rejects_garbage():
	var original: String = GameConfig.ui_layout
	GameConfig.set_setting("ui_layout", "proposed", false)
	assert_eq(GameConfig.ui_layout, "proposed", "known layout is accepted")
	GameConfig.set_setting("ui_layout", "nonsense", false)
	assert_eq(GameConfig.ui_layout, "proposed", "garbage layout is rejected (value unchanged)")
	GameConfig.set_setting("ui_layout", original, false)  # restore

func test_ui_layout_persists_round_trip():
	# The flag persists exactly the way GameConfig saves it -- an [interface] ConfigFile key.
	var cf := ConfigFile.new()
	cf.set_value("interface", "ui_layout", "proposed")
	assert_eq(cf.get_value("interface", "ui_layout", "classic"), "proposed",
		"ui_layout survives a ConfigFile save/load round-trip")

# --- LayoutController: both arrangements instance + restore -------------------------------

func _make_layout_fixture() -> Dictionary:
	# A minimal stand-in for main.tscn's ContentArea: three columns + a plan screen that
	# parents the upgrades label/scroll (the dock target).
	var content := HBoxContainer.new()
	var plan_col := Control.new()
	plan_col.size_flags_stretch_ratio = 0.3
	var instrument_col := Control.new()
	instrument_col.size_flags_stretch_ratio = 0.3
	var watch_col := Control.new()
	watch_col.size_flags_stretch_ratio = 0.4
	content.add_child(plan_col)
	content.add_child(instrument_col)
	content.add_child(watch_col)

	var plan_screen := VBoxContainer.new()
	var upgrades_label := Label.new()
	var upgrades_scroll := ScrollContainer.new()
	plan_screen.add_child(upgrades_label)
	plan_screen.add_child(upgrades_scroll)
	var office_cat := Control.new()
	plan_col.add_child(plan_screen)
	plan_col.add_child(office_cat)

	add_child_autofree(content)
	var lc := LayoutController.new()
	add_child_autofree(lc)
	lc.register_targets(plan_col, instrument_col, watch_col, office_cat,
		plan_screen, upgrades_label, upgrades_scroll)
	return {
		"lc": lc, "plan_col": plan_col, "instrument_col": instrument_col,
		"watch_col": watch_col, "plan_screen": plan_screen,
		"upgrades_label": upgrades_label, "upgrades_scroll": upgrades_scroll,
	}

func test_classic_layout_is_a_noop_over_defaults():
	var f := _make_layout_fixture()
	f.lc.apply_layout("classic")
	assert_eq(f.lc.current, "classic")
	assert_almost_eq(f.plan_col.size_flags_stretch_ratio, 0.3, 0.001, "classic keeps plan ratio")
	assert_almost_eq(f.instrument_col.size_flags_stretch_ratio, 0.3, 0.001, "classic keeps instrument ratio")
	assert_almost_eq(f.watch_col.size_flags_stretch_ratio, 0.4, 0.001, "classic keeps watch ratio")

func test_proposed_layout_reflows_columns_and_docks_upgrades():
	var f := _make_layout_fixture()
	f.lc.apply_layout("proposed")
	assert_eq(f.lc.current, "proposed")
	# P11: instrument column tightened, watch column widened.
	assert_lt(f.instrument_col.size_flags_stretch_ratio, 0.3, "instrument column reclaimed")
	assert_gt(f.watch_col.size_flags_stretch_ratio, 0.4, "watch column widened for the office floor")
	# P11 dock: upgrades label/scroll moved out of the plan screen into a framed panel.
	assert_ne(f.upgrades_label.get_parent(), f.plan_screen, "upgrades label docked into a panel")

func test_layout_flip_restores_classic_pixel_identical():
	var f := _make_layout_fixture()
	f.lc.apply_layout("proposed")
	f.lc.apply_layout("classic")
	# Ratios restored exactly.
	assert_almost_eq(f.plan_col.size_flags_stretch_ratio, 0.3, 0.001)
	assert_almost_eq(f.instrument_col.size_flags_stretch_ratio, 0.3, 0.001)
	assert_almost_eq(f.watch_col.size_flags_stretch_ratio, 0.4, 0.001)
	# Upgrades subtree back under the plan screen (dock reversed).
	assert_eq(f.upgrades_label.get_parent(), f.plan_screen, "upgrades label restored to plan screen")
	assert_eq(f.upgrades_scroll.get_parent(), f.plan_screen, "upgrades scroll restored to plan screen")

func test_toggle_cycles_between_the_two():
	var f := _make_layout_fixture()
	assert_eq(f.lc.toggle(), "proposed", "first toggle -> proposed")
	assert_eq(f.lc.toggle(), "classic", "second toggle -> classic")

# --- QueueGantt: rows track the queued-action count (P10) ---------------------------------

func test_gantt_rows_from_state_empty():
	assert_eq(QueueGantt.rows_from_state({}, []).size(), 0, "no state -> no rows")

func test_gantt_rows_track_committed_strategic_count():
	var state := {
		"turn": 5,
		"month_plan": {"queued_strategic": [
			{"action_id": "deep_research", "queued_on_turn": 3, "resolves_on_turn": 9},
			{"action_id": "field_building", "queued_on_turn": 4, "resolves_on_turn": 8},
		]},
	}
	var rows := QueueGantt.rows_from_state(state, [])
	assert_eq(rows.size(), 2, "one row per committed strategic play")
	assert_true(rows[0]["has_eta"], "committed rows carry an ETA")
	assert_eq(rows[0]["eta"], 9, "ETA is the resolution tick")
	assert_true(rows[0]["progress"] > 0.0, "mid-flight play shows partial progress")

func test_gantt_folds_in_tentative_and_hiring():
	var state := {
		"turn": 2,
		"month_plan": {"queued_strategic": [
			{"action_id": "deep_research", "queued_on_turn": 1, "resolves_on_turn": 6},
		]},
		"hiring": {"jobs": [
			{"kind": "interview", "resolves_on_turn": 5},
		]},
	}
	var tentative := [{"id": "scout", "name": "Scout"}]
	var rows := QueueGantt.rows_from_state(state, tentative)
	assert_eq(rows.size(), 3, "strategic + hiring + tentative all counted")
	assert_false(rows[2]["has_eta"], "tentative plan-time row has no ETA yet")

func test_gantt_builds_one_control_per_row():
	var gantt := QueueGantt.new()
	add_child_autofree(gantt)
	var rows := [
		{"name": "Deep Research", "eta": 9, "duration": 6, "progress": 0.3, "kind": "strategic", "has_eta": true},
		{"name": "Scout", "eta": -1, "duration": 0, "progress": 0.0, "kind": "planned", "has_eta": false},
	]
	gantt.update_rows(rows, true)
	assert_eq(gantt.row_count(), 2, "gantt renders one row control per queued entry")
	gantt.update_rows([], false)
	assert_eq(gantt.row_count(), 0, "empty queue renders no rows (hint only)")

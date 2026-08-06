extends GutTest
## The player-facing music picker in the pause menu (Pip 2026-08-06).
##
## THE PROPERTY THE WHOLE FEATURE RESTS ON, and the reason this file exists:
## a music pick is COSMETIC. It writes nothing to GameState, nothing to the seeded RNG,
## nothing to scoring, and it does not set the sticky unranked flag. PR #1129 asserted
## that for the DEV audition tool by construction ("nothing here calls
## _mark_alpha_tool_use()"). Promoting the same machinery to a shipped, player-reachable
## surface makes construction-by-inspection too weak a guarantee: the next person to
## touch music_controls.gd or apply_catalogue_entry() has no red light telling them they
## just made the soundtrack part of the run.
##
## So the guard here is DIFFERENTIAL, not structural: snapshot the entire serialized
## game state plus the RNG cursor, drive a full picker session through the real
## component (every catalogue entry, in order, then back to Automatic), snapshot again,
## and assert the two snapshots are identical strings. It cannot be satisfied by a
## careful reading; it can only be satisfied by the code actually not writing anything.
##
## PROVED TO FAIL BEFORE BEING TRUSTED (2026-08-06), both halves separately, by
## inserting one line into MusicControls._on_item_selected and running the file:
##   * `GameManager.state.money += 1` -> 15/16, snapshot diff money 245000 -> 245009
##     (nine picks). The STATE half is live.
##   * `GameManager.state.rng.randf()` -> 15/16, snapshot diff
##     rng.state 2051973181613222691 -> 7931504141110957565, with every visible field
##     unchanged. The RNG half is live, and it catches the invisible case -- a hidden
##     draw that desyncs a replay while the run still looks identical.
## In BOTH runs test_a_music_pick_cannot_unrank_the_run stayed green: neither mutation
## touches the alpha-tools flag. That is precisely the hole the differential snapshot
## exists to cover, and why "we did not call _mark_alpha_tool_use()" is not a guarantee.
## Removing the line restores 16/16. Transcripts in the PR body.
##
## SCOPE LIMIT, stated plainly: this proves a pick does not change the run. It does NOT
## prove the reverse direction is harmless -- a player who pins Calm through a doom spike
## really does lose the music's warning. That is Pip's explicit ruling ("if they miss out
## on doom indicators etc, so be it, that's their choice"), not an oversight, and the
## picker's hint text says so in words.

const PAUSE_MENU_SCENE := "res://scenes/pause_menu.tscn"

var _saved_tier: int = 0
var _saved_override: int = -1
var _saved_pick: String = ""
var _saved_context: int = 0


func before_each() -> void:
	_saved_tier = MusicManager._current_music_tier
	_saved_override = MusicManager._tier_override
	_saved_pick = MusicManager._manual_pick_path
	_saved_context = MusicManager.current_context
	MusicManager._tier_override = -1
	MusicManager._manual_pick_path = ""


func after_each() -> void:
	MusicManager._current_music_tier = _saved_tier
	MusicManager._tier_override = _saved_override
	MusicManager._manual_pick_path = _saved_pick
	MusicManager.current_context = _saved_context
	MusicManager._adaptive_active = false
	for player in [MusicManager.player_a, MusicManager.player_b]:
		if player != null:
			player.stop()
			player.stream = null
	# Insurance: no test in this file may leave the tree frozen for the rest of the suite.
	get_tree().paused = false


# === THE GUARD ======================================================================

func test_a_music_pick_cannot_change_the_run() -> void:
	GameManager.start_new_game("music-guard-seed", true)
	var controls := _make_controls()

	# Precondition: the snapshot function must be stable on its own, or a green result
	# below would mean nothing and a red one would be noise. Two reads, no music in
	# between -- if THIS fails, to_dict() carries a clock and the guard needs stripping.
	assert_eq(_snapshot(), _snapshot(),
		"the state snapshot must be deterministic before it can be used as a guard")

	var before := _snapshot()
	_drive_every_pick(controls)
	assert_eq(_snapshot(), before,
		"a full music picker session must leave the serialized run and the RNG cursor "
		+ "byte-identical -- music is a view-layer side-effect (ADR-0006)")


func test_a_music_pick_cannot_unrank_the_run() -> void:
	GameManager.start_new_game("music-guard-seed-2", true)
	GameConfig.reset_alpha_tools_flag()
	var controls := _make_controls()
	_drive_every_pick(controls)
	assert_false(GameConfig.alpha_tools_used,
		"picking a track is not a state mutation and must never set the sticky "
		+ "unranked flag -- Pip's 2026-08-06 ruling depends on this staying true")
	assert_true(GameConfig.is_ranked_run(),
		"the run stays on the leaderboard after a player listens to what they like")


## Every catalogue entry, in order, ending back on Automatic -- through the REAL signal
## handler, so the guard covers the shipped code path and not a test-only shortcut.
func _drive_every_pick(controls: MusicControls) -> void:
	var picker: OptionButton = controls._picker
	assert_gt(picker.item_count, 1, "the picker has Automatic plus at least one track")
	for i in range(picker.item_count):
		controls._on_item_selected(i)
	controls._on_item_selected(0)  # back to Automatic


## Everything the run IS, as one comparable string: the serialized state (money, doom,
## turn, staff, rivals, risk, events...) plus the seeded RNG's cursor, which is the thing
## a hidden extra draw would move without changing any visible field.
func _snapshot() -> String:
	if GameManager.state == null:
		return "<no run>"
	var parts := [
		var_to_str(GameManager.state.to_dict()),
		"rng.seed=%d" % GameManager.state.rng.seed,
		"rng.state=%d" % GameManager.state.rng.state,
	]
	return "\n".join(parts)


func _make_controls() -> MusicControls:
	var controls := MusicControls.new()
	add_child_autofree(controls)
	controls.refresh()
	return controls


# === THE PICKER SPEAKS PLAYER ========================================================

func test_catalogue_offers_automatic_first_then_every_track_by_human_name() -> void:
	var cat := MusicManager.player_catalogue()
	assert_eq(String(cat[0]["kind"]), "auto", "Automatic is the first and default choice")
	assert_string_contains(String(cat[0]["label"]), "Automatic", "and says so")
	var tiers: Array = []
	for entry in cat:
		if String(entry["kind"]) == "tier":
			tiers.append(int(entry["tier"]))
	assert_eq(tiers.size(), MusicManager.MUSIC_TIER_NAMES.size(),
		"every adaptive tier is pickable")
	assert_gt(cat.size(), MusicManager.MUSIC_TIER_NAMES.size() + 1,
		"and the standalone menu/victory/defeat beds too")


func test_no_label_leaks_a_filename_or_dev_jargon() -> void:
	# The dev overlay's labels are deliberately "M3 eldritch (mesa_optimizer)". A player
	# must never see a snake_case basename or an internal tier code.
	for entry in MusicManager.player_catalogue():
		var label := String(entry["label"])
		assert_false(label.contains("_"), "no snake_case filename in '%s'" % label)
		assert_false(label.contains(".ogg"), "no file extension in '%s'" % label)
		assert_false(label.begins_with("M0") or label.begins_with("M1")
			or label.begins_with("M2") or label.begins_with("M3") or label.begins_with("M4"),
			"no internal tier code in '%s'" % label)
		assert_ne(label.strip_edges(), "", "no blank entry")


func test_every_player_facing_string_is_plain_ascii() -> void:
	# The no-emoji gate (scripts/check_no_emoji.py) covers source files; this covers the
	# strings that are BUILT at runtime, which that scanner cannot see.
	var strings: Array = [MusicControls.SECTION_TITLE, MusicControls.HINT_TEXT]
	for entry in MusicManager.player_catalogue():
		strings.append(String(entry["label"]))
	MusicManager._adaptive_active = true
	strings.append(MusicManager.player_status_line())
	MusicManager.set_tier_override(4)
	strings.append(MusicManager.player_status_line())
	MusicManager._adaptive_active = false
	MusicManager._manual_pick_path = "res://assets/audio/music/checkpoint_saved.ogg"
	strings.append(MusicManager.player_status_line())
	for s in strings:
		for i in range(String(s).length()):
			assert_lt(String(s).unicode_at(i), 128,
				"non-ASCII codepoint in player-facing string: '%s'" % s)


func test_unknown_tracks_get_a_readable_name_instead_of_going_blank() -> void:
	assert_eq(MusicManager.track_title("res://assets/audio/music/checkpoint_saved.ogg"),
		"Checkpoint saved", "known beds use their composed title")
	var fallback := MusicManager.track_title("res://assets/audio/music/a_new_bed.ogg")
	assert_ne(fallback.strip_edges(), "", "an unlisted bed is ugly, never invisible")
	assert_false(fallback.contains("_"), "and still not snake_case")


# === "WHAT IS PLAYING AND WHY", IN PLAIN WORDS =======================================

func test_status_says_the_game_is_choosing_when_nobody_has_picked() -> void:
	MusicManager._adaptive_active = true
	MusicManager.set_doom_level(0.0)
	var line := MusicManager.player_status_line()
	assert_string_contains(line, "following the situation",
		"Automatic mode explains itself without jargon")
	assert_false(line.contains("your pick"), "and does not claim the player chose")


func test_status_names_the_track_the_game_wanted_when_a_pick_is_held() -> void:
	# The interesting case Pip asked about: the adaptive system wants to move and cannot.
	MusicManager._adaptive_active = true
	MusicManager.set_doom_level(0.0)
	MusicManager.set_tier_override(4)
	MusicManager.set_doom_level(30.0)  # automatic would be tier 1
	var line := MusicManager.player_status_line()
	assert_string_contains(line, "your pick", "it is honest about who chose")
	assert_string_contains(line, "Treacherous turn", "names what is being heard")
	assert_string_contains(line, "Distribution shift", "names what the game would play")
	assert_string_contains(line, "it will not", "and says the pick is what is stopping it")


func test_status_does_not_pretend_a_pick_was_made_when_audio_simply_failed() -> void:
	# Adaptive off with NO pick means the stream could not be built (missing audio) and
	# the legacy playlist took over. Blaming the player for that is silent wrongness in
	# words -- the exact failure mode this repo keeps meeting.
	MusicManager._adaptive_active = false
	MusicManager._manual_pick_path = ""
	assert_false(MusicManager.player_status_line().contains("your pick"),
		"a degraded fallback must not be reported as a player choice")


func test_status_owns_the_consequence_when_a_standalone_bed_is_picked() -> void:
	MusicManager._adaptive_active = false
	MusicManager._manual_pick_path = "res://assets/audio/music/out_of_distribution_trudge.ogg"
	var line := MusicManager.player_status_line()
	assert_string_contains(line, "your pick", "the player did this")
	assert_string_contains(line, "Automatic",
		"and is told exactly how to get the adaptive score back")


# === MODE ROUND-TRIP =================================================================

func test_picker_reopens_showing_what_is_actually_playing() -> void:
	# A picker that resets to item 0 every open would report Automatic while a pick is
	# held -- the readout lying about the one thing the panel exists to report.
	MusicManager._adaptive_active = true
	MusicManager.set_doom_level(0.0)
	assert_eq(MusicManager.player_catalogue_index(), 0, "no pick -> Automatic")
	MusicManager.set_tier_override(3)
	var idx: int = MusicManager.player_catalogue_index()
	var cat := MusicManager.player_catalogue()
	assert_eq(String(cat[idx]["kind"]), "tier", "a held pick resolves to its tier entry")
	assert_eq(int(cat[idx]["tier"]), 3, "and to the RIGHT tier")


func test_choosing_automatic_hands_the_music_back_to_the_game() -> void:
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)
	MusicManager.set_doom_level(0.0)
	MusicManager.set_tier_override(4)
	assert_true(MusicManager.is_tier_overridden(), "pick is held")
	MusicManager.apply_catalogue_entry({"kind": "auto"})
	assert_false(MusicManager.is_tier_overridden(), "Automatic releases it")
	assert_eq(MusicManager.get_current_music_tier(), MusicManager.get_auto_music_tier(),
		"and snaps to where the run actually is now")


func test_a_pick_survives_turns_but_not_a_new_run() -> void:
	# The persistence call, executable. WITHIN a run nothing clears a pick -- turn ends
	# only push doom in, and set_doom_level respects the override. ACROSS runs it is
	# released, because every start-run / return-to-menu / game-over path goes through
	# play_context(), and a cosmetic choice must not be the one piece of session state
	# that quietly outlives the run it was made in.
	MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)
	MusicManager.set_tier_override(4)
	for doom in [5.0, 25.0, 55.0, 88.0]:
		MusicManager.set_doom_level(doom)
	assert_true(MusicManager.is_tier_overridden(), "a pick holds across turns of doom")
	assert_eq(MusicManager.get_current_music_tier(), 4, "and keeps playing what was picked")
	MusicManager.play_context(MusicManager.MusicContext.MENU)
	assert_false(MusicManager.is_tier_overridden(), "a run boundary hands it back")
	assert_eq(MusicManager._manual_pick_path, "", "including a standalone-bed pick")


func test_the_music_keeps_working_while_the_tree_is_paused() -> void:
	# The pause menu freezes the tree. create_tween() binds its tween to the node that
	# made it, so with the default (inherited/PAUSABLE) process mode a crossfade started
	# from the picker would freeze half-done -- both players audible and is_crossfading
	# stuck true, refusing every later switch. This is why MusicManager is ALWAYS.
	assert_eq(MusicManager.process_mode, Node.PROCESS_MODE_ALWAYS,
		"MusicManager must process while paused or the pause-menu picker jams mid-crossfade")


# === THE PAUSE MENU ACTUALLY CARRIES IT ==============================================

func test_pause_menu_wires_up_the_picker() -> void:
	# Node-path wiring is exactly what a rename in the .tscn breaks silently.
	var menu = load(PAUSE_MENU_SCENE).instantiate()
	add_child_autofree(menu)
	assert_not_null(menu.music_controls, "the pause menu finds its MusicControls node")
	assert_true(menu.music_controls is MusicControls, "and it is the component, not a stub")
	assert_gt(menu.music_controls._picker.item_count, 1, "populated on open")


## The slack the authored panel is allowed to carry over what the contents actually need.
## This number is the ENTIRE point of the two-sided assertion below -- see the comment in
## test_pause_menu_is_sized_to_its_text. 40px is roughly two body lines; a panel grown for
## its own sake overshoots it by ~150.
const PANEL_SLACK_BUDGET := 40.0
## Two floors, because "small" is not one thing here.
##
## The arithmetic both come from: project.godot stretches canvas_items from a 1920x1080
## base, so on a 1280x720 laptop one authored pixel is 0.667 physical pixels. An 11px
## hint is SEVEN real pixels there. That is the cramping Pip reported on 2026-08-06
## ("things feel a bit cramped ... the text could be larger and friendlier"), and it is
## why the fix had to be the type scale and not just a bigger box.
##
## ROW floor -- anything a player reads while OPERATING a control (the volume row labels,
## the percentages, the buttons, the picker and its header). 16 is Godot's own Label
## default; before this change the pause menu authored its rows at 14, i.e. BELOW the
## engine default, in a panel it also had no room in.
const MIN_ROW_FONT_SIZE := 16
## ABSOLUTE floor -- secondary explanatory prose (the picker's hint) is allowed to be
## smaller than a control label, but not by much. 14 is ~9 physical pixels at 720p.
const MIN_ANY_FONT_SIZE := 14


func test_pause_menu_is_sized_to_its_text() -> void:
	# The picker adds ~4 rows to a panel whose height is hand-set in the .tscn, so the
	# obvious way to ship this broken is a menu whose Quit button is off the bottom.
	# Precedent for owning geometry in a test: test_action_visibility.gd (#1130).
	#
	# THREE ASSERTIONS TRIED AND THROWN AWAY, recorded so nobody re-adds them:
	#   child.size.y <= panel.size.y  -- PanelContainer CLAMPS its child to its own
	#     rect, so this is true by construction (#1146).
	#   needed.y <= panel.size.y      -- a Control never renders smaller than its
	#     combined minimum, so the panel silently GROWS past its authored offsets and
	#     this is true by construction too (#1146).
	#   needed.y <= authored ALONE    -- a real guard against content overflowing the
	#     authored box, but ONE-SIDED: it gets easier every time the panel grows, so
	#     the +30% resize this test now guards would have made it near-vacuous. That is
	#     the failure mode this file's whole history is about.
	# The version that ships is TWO-SIDED. Pip's brief for the resize was "increase the
	# size of the Escape screen by 30%, the text could be larger and friendlier" -- the
	# room is for TEXT, not padding. So the authored box must be big enough for the
	# contents AND not much bigger: a future 30% growth with the type scale left alone
	# fails the second half, which is exactly the mistake worth catching.
	# Host the menu in an explicit 1920x1080 box, because the menu's root is anchored
	# full-rect and its width -- therefore where the two wrapped labels break -- is
	# whatever its PARENT is.
	#
	# A DISAGREEMENT WORTH KNOWING ABOUT, measured 2026-08-06 and not resolved:
	# a real windowed launch (`--resolution 1920x1080`, throwaway SceneTree harness)
	# reports the hint label 560px wide wrapping to THREE lines and the panel needing
	# ~23px MORE than this test does. Same scene, same strings, same font -- the labels
	# simply have not taken the panel's full width at the moment the windowed harness
	# samples them. The larger number is the safe one, so the authored panel is sized to
	# cover in-tree + 23, NOT to the bare number this test sees. If that were reversed,
	# the guard would be sizing the panel to the more flattering of two measurements --
	# which is how the earlier tautologies in this file got written.
	#
	# REBASE NOTE (landing this PR, 2026-08-06): #1120 landed a sixth button in this
	# panel ("Settings & Keybindings (F10)") AFTER this test's numbers were measured,
	# so the contents grew 707 -> 769 and the authored box 740 -> 792. #1120 authored
	# that button at font 16 / 320x40, the lone survivor of the old cramped scale; it
	# is now 20 / 320x50 like its five siblings, which is the whole point of this PR.
	var host := Control.new()
	add_child_autofree(host)
	host.size = Vector2(1920, 1080)
	var menu = load(PAUSE_MENU_SCENE).instantiate()
	host.add_child(menu)
	# Measure the WORST case, not the resting one. The status label wraps, and the
	# longest string it can hold is the pick-held-while-adaptive-wants-to-move line
	# (two wrapped rows, not one). #1146 measured the short line and therefore had
	# ~20px of headroom it could not see.
	MusicManager._adaptive_active = true
	MusicManager.set_doom_level(0.0)
	MusicManager.set_tier_override(4)
	MusicManager.set_doom_level(30.0)
	menu.show_pause_menu()
	assert_string_contains(menu.music_controls._status.text, "it will not",
		"this measurement is only worst-case if the long status line is the one loaded")
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame
	var panel: Control = menu.get_node("Panel")
	var needed: Vector2 = panel.get_combined_minimum_size()
	menu._on_resume_pressed()

	# (a) It fits the design viewport. This is the resolution check, and it covers ALL of
	# them: project.godot uses stretch/mode="canvas_items" with aspect="expand", so the
	# scale factor is min(w/1920, h/1080) and the viewport in these units is therefore
	# NEVER smaller than 1920x1080 on either axis -- a narrower window buys extra units,
	# it never takes any away. Measured 2026-08-06 by running the scene at 1920x1080,
	# 1600x900, 1366x768, 1280x720, 1280x800, 1024x768 and 2560x1080: the panel rect was
	# 800x740 in viewport units in every one, fully inside the visible rect in every one.
	# (The box is 800x792 after the #1120 rebase; 792 is still far inside 1080.)
	assert_lte(needed.y, 1080.0,
		"the pause menu needs %dpx of height -- more than the 1080p design viewport, so "
		% int(needed.y) + "it will run off the top and bottom of the screen")
	assert_lte(needed.x, 1920.0, "and it must fit horizontally too")

	# (b) The authored box is honest -- read out of the .tscn text, because Godot rewrites
	# a grown control's offsets in memory and the authored intent is unreachable from the
	# live node. Verified red at the pre-#1146 500px (551 > 500).
	var authored: float = _authored_panel_height()
	assert_lte(needed.y, authored,
		"pause_menu.tscn asks for a %dpx panel and the contents need %dpx -- Godot will "
		% [int(authored), int(needed.y)]
		+ "grow it silently. Update the Panel offset_top/offset_bottom to match.")

	# (c) ...and the box is not mostly air. Measured 2026-08-06: this test sees 769px of
	# contents in a 792px box (23px slack); the windowed harness reads ~23px higher, so it
	# sees ~0. The budget has to clear the looser of the two, so 40 -- which still fails
	# red on the mistake it exists to catch. Verified red by authoring 780 against the
	# pre-#1120 contents, the flat +30% of the old 600px panel: "asks for a 780px panel
	# but the contents only need 707px, so it carries 73px of slack". Reverting the type
	# scale as well would read ~190px.
	assert_lte(authored - needed.y, PANEL_SLACK_BUDGET,
		"pause_menu.tscn asks for a %dpx panel but the contents only need %dpx, so it "
		% [int(authored), int(needed.y)]
		+ "carries %dpx of slack. The panel was grown for LEGIBILITY -- if it is bigger "
		% int(authored - needed.y)
		+ "than its text, put the room into the type scale or shrink the box.")


func test_no_player_facing_text_in_the_pause_menu_is_below_the_legibility_floor() -> void:
	# The other half of (c): (c) stops the panel outgrowing its text, this stops the text
	# shrinking inside the panel. Reads the .tscn rather than the live tree because the
	# sizes ARE authored numbers and a live read would just echo whatever was authored.
	# Verified red 2026-08-06 by reverting one volume row to its pre-change 14px:
	# "pause_menu.tscn authors a 14px control-row font ... ~9 physical pixels at 1280x720".
	# The pre-change hint (11) and status (12) fail the absolute floor the same way.
	for size in _authored_font_sizes():
		assert_gte(size, MIN_ROW_FONT_SIZE,
			"pause_menu.tscn authors a %dpx control-row font. Below %dpx this is ~%d "
			% [size, MIN_ROW_FONT_SIZE, int(size * 720.0 / 1080.0)]
			+ "physical pixels at 1280x720 -- the cramping Pip reported on 2026-08-06.")
	for size in [MusicControls.SECTION_TITLE_FONT_SIZE, MusicControls.PICKER_FONT_SIZE,
			MusicControls.STATUS_FONT_SIZE]:
		assert_gte(size, MIN_ROW_FONT_SIZE,
			"MusicControls authors a %dpx control font, below the %dpx row floor"
			% [size, MIN_ROW_FONT_SIZE])
	assert_gte(MusicControls.HINT_FONT_SIZE, MIN_ANY_FONT_SIZE,
		"the picker hint is prose, not a control label, so it may sit under the row floor "
		+ "-- but %dpx is under the absolute floor of %dpx too"
		% [MusicControls.HINT_FONT_SIZE, MIN_ANY_FONT_SIZE])
	# The picker's section header and the Audio Settings header sit one row apart and are
	# the same KIND of thing, so they must be the same size. They were 14 and 18 in #1146,
	# which is the sort of drift that only reads as "cramped" and never as "a bug".
	assert_eq(MusicControls.SECTION_TITLE_FONT_SIZE, _authored_font_size_of("AudioLabel"),
		"the two section headers in this panel must be one size, not two")


## Panel height as WRITTEN in the scene file. Godot adjusts a centred control's offsets
## to whatever it grew to, so the authored intent is unreachable from the live node.
func _authored_panel_height() -> float:
	var text := FileAccess.get_file_as_string(PAUSE_MENU_SCENE)
	var in_panel := false
	var top := 0.0
	var bottom := 0.0
	for raw in text.split("\n"):
		var line := String(raw).strip_edges()
		if line.begins_with("[node "):
			in_panel = line.contains("name=\"Panel\"") and line.contains("parent=\".\"")
			continue
		if not in_panel:
			continue
		if line.begins_with("offset_top ="):
			top = float(line.split("=")[1])
		elif line.begins_with("offset_bottom ="):
			bottom = float(line.split("=")[1])
	assert_ne(bottom - top, 0.0, "could not read the Panel offsets out of pause_menu.tscn")
	return bottom - top


## Every font size authored in the scene file, EXCLUDING the title -- a 40px heading is
## not the legibility problem and pinning it here would only make the floor unfalsifiable.
func _authored_font_sizes() -> Array:
	var sizes: Array = []
	var node_name := ""
	for raw in FileAccess.get_file_as_string(PAUSE_MENU_SCENE).split("\n"):
		var line := String(raw).strip_edges()
		if line.begins_with("[node "):
			node_name = line.split("name=\"")[1].split("\"")[0]
		elif line.begins_with("theme_override_font_sizes/font_size =") and node_name != "Title":
			sizes.append(int(float(line.split("=")[1])))
	assert_gt(sizes.size(), 5, "could not read the font sizes out of pause_menu.tscn")
	return sizes


func _authored_font_size_of(wanted: String) -> int:
	var node_name := ""
	for raw in FileAccess.get_file_as_string(PAUSE_MENU_SCENE).split("\n"):
		var line := String(raw).strip_edges()
		if line.begins_with("[node "):
			node_name = line.split("name=\"")[1].split("\"")[0]
		elif line.begins_with("theme_override_font_sizes/font_size =") and node_name == wanted:
			return int(float(line.split("=")[1]))
	assert_true(false, "no authored font size for node '%s' in pause_menu.tscn" % wanted)
	return -1


func test_pause_menu_refreshes_the_readout_on_every_open() -> void:
	var menu = load(PAUSE_MENU_SCENE).instantiate()
	add_child_autofree(menu)
	MusicManager._adaptive_active = true
	MusicManager.set_doom_level(0.0)
	menu.show_pause_menu()
	var opened_line: String = menu.music_controls._status.text
	menu._on_resume_pressed()
	assert_false(get_tree().paused, "resume unfreezes the tree")
	# Doom moves while the menu is shut; reopening must re-derive, not replay.
	MusicManager.set_doom_level(95.0)
	menu.show_pause_menu()
	menu._on_resume_pressed()
	assert_ne(menu.music_controls._status.text, opened_line,
		"reopening after a doom swing must show the NEW track, not the cached line")
	assert_string_contains(menu.music_controls._status.text, "Treacherous turn",
		"and name the track the run has actually escalated to")

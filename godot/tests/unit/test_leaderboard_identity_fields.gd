extends GutTest
## Leaderboard identity: the operator and the lab are TWO values, not one.
##
## The defect (Pip, playing the shipped build 2026-08-07): "we still haven't
## solved player names on the leaderboard?" -- game_over_screen.gd built the
## submitted entry as
##     Leaderboard.ScoreEntry.new(final_turns, GameConfig.lab_name, ...)
## where the receiving field was named `player_name`. GameConfig has carried a
## real `player_name` since #1133 and the game-over identity prompt collects it
## under the label "Operator:", but no code path ever moved it toward the board.
## A player who typed their name saw it nowhere.
##
## Pip's ruling (2026-08-08) is BOTH, as separate values, with his reasoning:
## generated lab names COLLIDE (that is why #1133 exists), so a lab name alone
## cannot identify a person; and one player running several labs over several
## months is a feature, so a single conflated field destroys that permanently.
##
## Second measured defect: the remote board stores 40 bytes and cuts the rest.
## The live (weekly-2026-w32, L4) board holds Pip's lab as
##     "GRIM (Global Risk Intervention Mechanism"
## -- exactly 40 bytes, amputated mid-word with the closing bracket eaten, from
## a 41-byte submission. pdoom1 cannot change the server, so the client fits the
## value deliberately and the server's cut never fires.
##
## What these tests deliberately do NOT assert: that the operator name reaches
## the SERVER. The wire contract is frozen and server-side (score_api.php is not
## in any repo here), so sending an unknown key blind is not a tonight change.

# The exact string sitting on the live public board, byte for byte. If a future
# change ever reproduces this value the guard fails and names why.
const LIVE_AMPUTATED := "GRIM (Global Risk Intervention Mechanism"
const LIVE_FULL_LAB := "GRIM (Global Risk Intervention Mechanism)"

const GAME_OVER_SRC := "res://scripts/ui/game_over_screen.gd"


func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	assert_not_null(f, "cannot open %s" % path)
	if f == null:
		return ""
	var text := f.get_as_text()
	f.close()
	return text


# ---- the measured truncation limit ------------------------------------------

func test_measured_limit_matches_the_live_board():
	# Provenance of the number: measured off the live board on 2026-08-08, not
	# taken on trust. 41 bytes submitted, 40 bytes stored.
	assert_eq(LIVE_AMPUTATED.to_utf8_buffer().size(), 40,
		"the live amputated row is 40 bytes -- that IS the limit")
	assert_eq(LIVE_FULL_LAB.to_utf8_buffer().size(), 41,
		"the submission was 41 bytes; the server ate exactly one")
	assert_eq(Leaderboard.BOARD_NAME_MAX_BYTES, 40,
		"the client must encode the MEASURED limit, not an assumed one")


func test_fit_board_name_never_exceeds_the_limit():
	# Bytes, not characters: the server's cut is byte-wise, so a byte-wise cut is
	# what the client must stay inside. A character-wise budget would still
	# overflow on any non-ASCII name and hand the server a split codepoint.
	var battery := [
		LIVE_FULL_LAB,
		"A".repeat(200),
		"word ".repeat(40),
		"Institute for the Study of Extremely Long Organisational Names",
	]
	for raw in battery:
		var fitted: String = Leaderboard.fit_board_name(raw)
		assert_true(fitted.to_utf8_buffer().size() <= Leaderboard.BOARD_NAME_MAX_BYTES,
			"fit_board_name('%s...') returned %d bytes, over the %d-byte board limit"
				% [raw.substr(0, 20), fitted.to_utf8_buffer().size(), Leaderboard.BOARD_NAME_MAX_BYTES])


func test_fit_board_name_passes_short_names_through_untouched():
	# The common case must be lossless and unmarked -- a cut mark on a name that
	# was never cut is its own lie.
	for raw in ["GRIM", "Pip", "AI Safety Lab", ""]:
		assert_eq(Leaderboard.fit_board_name(raw), raw,
			"'%s' fits and must pass through unchanged" % raw)


func test_the_live_amputation_is_never_reproduced():
	# The real defect, named: this exact output is what is on the public board.
	var fitted: String = Leaderboard.fit_board_name(LIVE_FULL_LAB)
	assert_ne(fitted, LIVE_AMPUTATED,
		"fit_board_name reproduced the live mid-word amputation")
	assert_true(fitted.ends_with(Leaderboard.BOARD_NAME_CUT_MARK),
		"a cut name must be LEGIBLY cut (ends with '%s'), not silently amputated"
			% Leaderboard.BOARD_NAME_CUT_MARK)
	assert_false(fitted.begins_with(LIVE_AMPUTATED),
		"the fitted name must not merely re-mark the same mid-word cut")


func test_cut_names_break_on_a_word_boundary_when_one_is_available():
	var fitted: String = Leaderboard.fit_board_name(LIVE_FULL_LAB)
	# "Mechanism)" is dropped whole rather than sliced into "Mechani".
	assert_eq(fitted, "GRIM (Global Risk Intervention...",
		"a name with spaces must cut at a space, not through a word")


func test_a_single_unbroken_word_still_gets_cut_rather_than_dropped():
	# Boundary: no space to break on. Dropping to empty would lose the identity
	# entirely, so a hard cut with the mark is correct here.
	var fitted: String = Leaderboard.fit_board_name("A".repeat(200))
	assert_true(fitted.to_utf8_buffer().size() <= Leaderboard.BOARD_NAME_MAX_BYTES)
	assert_true(fitted.length() > 10, "an unbroken word must survive, not vanish")
	assert_true(fitted.ends_with(Leaderboard.BOARD_NAME_CUT_MARK))


func test_fit_board_name_is_ascii_safe_on_multibyte_input():
	# A player typing an accented name is the case where a byte-wise server cut
	# produces an INVALID string. The client must never hand the server one.
	var raw := "Fondation de Recherche en Securite Avancee de l'Intelligence"
	var fitted: String = Leaderboard.fit_board_name(raw)
	assert_true(fitted.to_utf8_buffer().size() <= Leaderboard.BOARD_NAME_MAX_BYTES)
	# Round-trips through UTF-8 without corruption.
	assert_eq(fitted.to_utf8_buffer().get_string_from_utf8(), fitted,
		"fitted name must be valid UTF-8")


# ---- the two fields ----------------------------------------------------------

func test_score_entry_carries_operator_and_lab_separately():
	# The core of Pip's ruling: two values, never conflated.
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	assert_eq(entry.lab_name, "GRIM", "the lab slot holds the lab")
	assert_eq(entry.operator_name, "Pip", "the operator slot holds the human")


func test_operator_name_defaults_empty_and_never_borrows_the_lab():
	# Silent-wrongness guard: an absent operator must read as absent, not quietly
	# inherit the lab name and look like a claimed identity.
	var entry := Leaderboard.ScoreEntry.new(42, "GRIM", 42, "v0.14.0", 1.0)
	assert_eq(entry.operator_name, "",
		"a missing operator name must stay empty, never fall back to the lab")


func test_the_field_name_and_its_contents_agree():
	# The defect in schema form. leaderboard.gd carried
	#     var player_name: String  # Lab name
	# -- a field whose own comment admitted it was misnamed, feeding a public
	# column of the same wrong name.
	var entry := Leaderboard.ScoreEntry.new(42, "GRIM", 42, "v0.14.0", 1.0, 0, 0, 0, "Pip")
	assert_false("player_name" in entry,
		"ScoreEntry must not expose a `player_name` field that holds a lab name")


# ---- local persistence carries both ------------------------------------------

func test_local_dict_round_trips_both_names():
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	var back := Leaderboard.ScoreEntry.from_dict(entry.to_dict())
	assert_eq(back.lab_name, "GRIM", "lab survives the local round trip")
	assert_eq(back.operator_name, "Pip", "operator survives the local round trip")


func test_local_dict_keeps_the_legacy_key_readable():
	# Every local board file already on disk, and every row already on the live
	# board, stores the lab under the key `player_name`. Reading must keep
	# working, and such a row must present as lab-only -- NOT as an operator.
	var legacy := {
		"score": 12, "player_name": "GRIM", "level_reached": 12,
		"game_mode": "v0.13.2", "duration_seconds": 5.0,
	}
	var back := Leaderboard.ScoreEntry.from_dict(legacy)
	assert_eq(back.lab_name, "GRIM", "a legacy `player_name` value IS a lab name")
	assert_eq(back.operator_name, "",
		"a legacy row has no operator; inventing one would fabricate identity")


# ---- the frozen wire contract ------------------------------------------------

func test_wire_dict_keeps_the_frozen_player_name_key_carrying_the_lab():
	# score_api.php is server-side and in no repo here; its documented contract
	# (docs/LEADERBOARD_WEBSITE_INTEGRATION.md:148) defines `player_name` as
	# "Lab name displayed on leaderboard". Renaming the KEY is a server change.
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	var wire := entry.to_wire_dict()
	assert_eq(wire.get("player_name"), "GRIM",
		"the frozen wire key must keep carrying the lab -- the server reads it")


func test_wire_dict_does_not_send_the_operator_blind():
	# Deliberate omission, not an oversight: the server's tolerance for unknown
	# keys is unmeasured, and a rejected POST loses a score. Sending the operator
	# is the coordination item, not a tonight change.
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	assert_false(entry.to_wire_dict().has("operator_name"),
		"operator_name must not go on the wire until the server is known to take it")


func test_wire_dict_fits_the_board_limit_so_the_server_never_cuts():
	var entry := Leaderboard.ScoreEntry.new(
		42, LIVE_FULL_LAB, 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	var wire := entry.to_wire_dict()
	var sent := str(wire.get("player_name"))
	assert_true(sent.to_utf8_buffer().size() <= Leaderboard.BOARD_NAME_MAX_BYTES,
		"the wire value must already fit, so the server's substr never fires")
	assert_ne(sent, LIVE_AMPUTATED, "must not hand the server the amputated form")


func test_wire_dict_carries_the_full_contract_fields():
	# Fitting the name must not have dropped anything else the server reads.
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 7, 100, 9, "Pip")
	var wire := entry.to_wire_dict()
	for key in ["score", "player_name", "date", "level_reached", "game_mode",
			"duration_seconds", "entry_uuid", "baseline_score",
			"doom_integral", "baseline_doom_integral"]:
		assert_true(wire.has(key), "wire body lost contract field '%s'" % key)


# ---- the real call site ------------------------------------------------------

func test_game_over_screen_submits_the_operator_name_too():
	# Names the defect site directly: game_over_screen.gd:280 passed only
	# GameConfig.lab_name into an entry whose identity slot was `player_name`.
	var src := _read(GAME_OVER_SRC)
	var idx := src.find("ScoreEntry.new(")
	assert_true(idx >= 0, "could not find the submission site in game_over_screen.gd")
	var call_block := src.substr(idx, 500)
	assert_true(call_block.contains("GameConfig.lab_name"),
		"the submission must still carry the lab name")
	assert_true(call_block.contains("GameConfig.player_name"),
		"game_over_screen must pass the OPERATOR name into the entry -- #1133 collects it and nothing carried it")


func test_identity_prompt_is_honest_about_what_reaches_the_board():
	# The prompt collects "Operator:" and "Lab:". Until the wire carries both,
	# a prompt that implies both appear publicly is lying to the player.
	var src := _read(GAME_OVER_SRC)
	assert_true(src.contains("IDENTITY_PROMPT_BOARD_NOTE"),
		"the identity prompt must state which of the two values the board shows today")
	var note: String = load(GAME_OVER_SRC).get_script_constant_map().get(
		"IDENTITY_PROMPT_BOARD_NOTE", "")
	assert_true(note.contains("Lab"), "the note must name the Lab name")
	assert_true(note.contains("Operator"), "the note must name the Operator name")
	for i in note.length():
		assert_true(note.unicode_at(i) < 128,
			"player-facing string must be ASCII-only (house rule, issue #744)")


func test_prompt_retrofit_applies_both_names_to_the_pending_entry():
	# _apply_identity_from_prompt retrofitted only the lab onto the entry, so a
	# name claimed at the prompt could never reach the entry at all.
	var src := _read(GAME_OVER_SRC)
	var idx := src.find("func _apply_identity_from_prompt")
	assert_true(idx >= 0, "could not find _apply_identity_from_prompt")
	var body := src.substr(idx, 1200)
	assert_true(body.contains("operator_name"),
		"the claimed operator name must be retrofitted onto the pending entry")

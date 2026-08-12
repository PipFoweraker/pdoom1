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
## THIRD defect, measured 2026-08-10 against the DEPLOYED api.pdoom1.com on a
## throwaway board (never the live one). #1176 stopped short of the wire because
## the server's tolerance was unmeasured. Measured, it is this:
##
##   * the limit is 40 BYTES, not characters. 41 ASCII bytes -> 40 stored;
##     40 ASCII bytes -> stored untouched.
##   * an unknown extra key (`operator_name`, and a nonsense control key) is
##     ACCEPTED with HTTP 200 and then SILENTLY DROPPED -- absent on read-back.
##     So the feared rejection does not happen, but a separate key delivers
##     nothing, which is why both names now travel COMPOSED in the one field.
##   * a name whose byte-wise cut at 40 SPLITS a UTF-8 codepoint DESTROYS THE
##     WHOLE BOARD. Measured: a 7-row board went to 0 rows while the server
##     answered {"ok":true,"added":true,"rank":7}. An over-40 multibyte name
##     whose cut lands ON a codepoint boundary is stored normally, so the
##     trigger is precisely the split, not merely being non-ASCII.
##
## That last one turns fit_board_name from a cosmetic nicety into a board
## INTEGRITY guard, and it is why composition must fit CLIENT-SIDE: composing
## puts player-typed text into the byte-cut field for the first time.
##
## What these tests still do NOT assert: that a separate `operator_name` KEY
## reaches the server. Measured to be dropped; that is a coordination ask.

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
	# score_api.php's whitelist is the frozen contract; renaming the KEY is a
	# server change. The key still leads with the lab, so the column keeps the
	# same meaning it has on the 10 rows already up there.
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	var wire := entry.to_wire_dict()
	assert_true(str(wire.get("player_name")).begins_with("GRIM"),
		"the frozen wire key must still LEAD with the lab -- the server reads it")


func test_wire_dict_does_not_send_the_operator_as_its_own_key():
	# Not caution any more: MEASURED. An unknown key round-trips as HTTP 200 and
	# is then dropped by $ALLOWED_FIELDS, so a separate key delivers nothing.
	# Sending one anyway would put the operator on the wire TWICE (once composed,
	# once ignored) and desync the day the server whitelists it.
	var entry := Leaderboard.ScoreEntry.new(
		42, "GRIM", 42, "v0.14.0", 1.0, 0, 100, 0, "Pip")
	assert_false(entry.to_wire_dict().has("operator_name"),
		"operator_name must not go on the wire as its own key -- measured to be dropped")


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


# ---- composition: both names, one frozen field -------------------------------
#
# The server drops unknown keys (measured), so the only way the operator reaches
# a public board today is inside `player_name`.

## Reproduce the server's own cut, exactly: PHP substr($s, 0, 40) is BYTE-wise.
## Returns true when the result is still valid UTF-8 -- i.e. when the submission
## would NOT wipe the board.
func _survives_server_substr(name: String) -> bool:
	var bytes := name.to_utf8_buffer()
	if bytes.size() <= Leaderboard.BOARD_NAME_MAX_BYTES:
		return true  # substr is a no-op; nothing to split
	var cut := bytes.slice(0, Leaderboard.BOARD_NAME_MAX_BYTES)
	# Validity by BYTE ROUND-TRIP, not by an empty-string check: Godot's
	# get_string_from_utf8 substitutes replacement characters for a split
	# codepoint rather than failing, so decoding alone silently "succeeds".
	# Re-encoding only reproduces the original bytes when they were valid --
	# and it is exactly malformed bytes that make PHP json_encode() return
	# false and empty the board file.
	return cut.get_string_from_utf8().to_utf8_buffer() == cut


func test_composed_name_carries_both_names():
	# The whole point. Pip 2026-08-10: "we're going to get a LOT of colliding
	# labs" -- the operator is the disambiguator, so it must actually be there.
	var composed := Leaderboard.compose_board_name("GRIM", "Pip")
	assert_true(composed.contains("GRIM"), "the lab must appear on the board")
	assert_true(composed.contains("Pip"), "the operator must appear on the board")
	assert_true(composed.begins_with("GRIM"),
		"lab FIRST: the 10 rows already on the board hold a bare lab in this "
		+ "column, and leading with the operator would change what the column means")


func test_composed_name_never_exceeds_the_measured_byte_budget():
	# RED before the budget split: naive concatenation of a real lab and a real
	# operator blows straight past 40 bytes and hands the server its substr.
	var battery := [
		[LIVE_FULL_LAB, "Pip"],
		[LIVE_FULL_LAB, "Kaur, Chen & Lindqvist"],
		["Institute for the Study of Extremely Long Organisational Names", "Pip"],
		["A".repeat(200), "B".repeat(200)],
		["GRIM", "Pip"],
	]
	for pair in battery:
		var composed: String = Leaderboard.compose_board_name(pair[0], pair[1])
		assert_true(composed.to_utf8_buffer().size() <= Leaderboard.BOARD_NAME_MAX_BYTES,
			"compose_board_name('%s', '%s') = %d bytes, over the measured %d-byte budget"
				% [pair[0].substr(0, 16), pair[1], composed.to_utf8_buffer().size(),
					Leaderboard.BOARD_NAME_MAX_BYTES])


func test_a_composed_name_can_never_wipe_the_board():
	# THE measured catastrophe, encoded. On 2026-08-10 a submission whose
	# byte-wise cut at 40 split a UTF-8 codepoint took a 7-row throwaway board to
	# 0 rows, while the server answered {"ok":true,"added":true,"rank":7}: PHP
	# json_encode() returns false on malformed UTF-8, so the board file was
	# ftruncate(0)'d and then written with nothing.
	#
	# Composition is what makes this urgent -- it puts PLAYER-TYPED text into the
	# byte-cut field for the first time. An accented operator name is not exotic;
	# the newest real player on the live board is "Kaur, Chen & Lindqvist".
	var operators := ["Pip", "Bjorn Lindqvist", "Zoe" + char(0x00E9),
		char(0x00E9).repeat(30), "Chen " + char(0x00FC).repeat(20)]
	var labs := [LIVE_FULL_LAB, "GRIM", char(0x00E9).repeat(25),
		"C".repeat(39) + char(0x00E9), "A".repeat(200)]
	for lab in labs:
		for op in operators:
			var composed: String = Leaderboard.compose_board_name(lab, op)
			assert_true(_survives_server_substr(composed),
				("compose_board_name would hand the server a name whose byte-wise "
				+ "cut splits a codepoint -- that WIPES THE WHOLE BOARD (measured). "
				+ "lab=%d bytes op=%d bytes composed=%d bytes")
					% [lab.to_utf8_buffer().size(), op.to_utf8_buffer().size(),
						composed.to_utf8_buffer().size()])


func test_the_multibyte_split_really_is_the_wipe_trigger():
	# Calibrates the helper above against the two measured outcomes, so a future
	# reader can see the guard is testing the real boundary and not a proxy.
	# Cut lands ON a codepoint boundary (21 x 2-byte = 42 bytes) -> board survived.
	assert_true(_survives_server_substr(char(0x00E9).repeat(21)),
		"an over-40 multibyte name cut on a boundary was stored normally")
	# Cut lands INSIDE a codepoint (39 ASCII + 1 x 2-byte = 41 bytes) -> board died.
	assert_false(_survives_server_substr("C".repeat(39) + char(0x00E9)),
		"the measured wipe case must be recognised as unsafe")


func test_neither_name_can_erase_the_other():
	# A long operator must not swallow the lab, and a long lab must not swallow
	# the operator -- the operator is the collision-breaker, so it cannot be the
	# thing that silently vanishes.
	var composed: String = Leaderboard.compose_board_name(
		LIVE_FULL_LAB, "Kaur, Chen & Lindqvist")
	assert_true(composed.begins_with("GRIM"), "the lab must still be recognisable")
	assert_true(composed.contains(Leaderboard.BOARD_NAME_SEPARATOR),
		"both halves must still be present, separated")
	var halves := composed.split(Leaderboard.BOARD_NAME_SEPARATOR)
	assert_eq(halves.size(), 2, "exactly one separator between the two names")
	assert_true(halves[0].length() >= 4, "the lab half must not be reduced to nothing")
	assert_true(halves[1].length() >= 4, "the operator half must not be reduced to nothing")


func test_a_name_containing_the_separator_cannot_forge_a_second_name():
	# Otherwise "Evil -- Pip" as a LAB name composes to "Evil -- Pip -- Someone"
	# and nobody reading the public board can tell which half is the operator.
	var composed: String = Leaderboard.compose_board_name("Evil -- Corp", "Pip")
	assert_eq(composed.split(Leaderboard.BOARD_NAME_SEPARATOR).size(), 2,
		"exactly one separator may survive into the composed name; got '%s'" % composed)
	assert_true(composed.ends_with("Pip"), "the real operator is still the last half")


func test_a_cut_half_is_legibly_cut():
	# Same rule as fit_board_name: an amputation that reads as a typo is the
	# defect. If a half had to be shortened, it says so.
	var composed: String = Leaderboard.compose_board_name(LIVE_FULL_LAB, "Pip")
	assert_true(composed.contains(Leaderboard.BOARD_NAME_CUT_MARK),
		"a lab that had to be shortened must show the '%s' mark, not be amputated"
			% Leaderboard.BOARD_NAME_CUT_MARK)
	assert_false(composed.contains(LIVE_AMPUTATED),
		"must never reproduce the live mid-word amputation")


func test_no_operator_composes_to_exactly_todays_behaviour():
	# DEGRADE-SAFELY guard. Every one of the 10 rows already on the board, and
	# every player who never typed a name, must be byte-identical to before --
	# no separator, no empty parenthetical, no fabricated identity.
	for lab in ["GRIM", "AI Safety Lab", LIVE_FULL_LAB, "", "   "]:
		var composed: String = Leaderboard.compose_board_name(lab, "")
		assert_eq(composed, Leaderboard.fit_board_name(lab.strip_edges()),
			"a lab with no operator must submit exactly as it does today")
		assert_false(composed.contains(Leaderboard.BOARD_NAME_SEPARATOR),
			"'%s' has no operator -- it must not grow a dangling separator" % lab)


func test_a_legacy_row_read_back_is_never_given_a_fabricated_operator():
	# The other half of degrading safely: reading. A row on the board today holds
	# a bare lab under `player_name`. Round-tripping it must not invent a human.
	var legacy := {"score": 44, "player_name": "Kaur, Chen & Lindqvist",
		"level_reached": 44, "duration_seconds": 1546.0}
	var back := Leaderboard.ScoreEntry.from_dict(legacy)
	assert_eq(back.operator_name, "", "a legacy row has no operator, and stays that way")
	assert_eq(back.to_wire_dict().get("player_name"), "Kaur, Chen & Lindqvist",
		"re-submitting a legacy row must not mutate the name it already has")


# ---- what a rejected POST does to the score ----------------------------------

func test_a_rejected_post_keeps_the_score_in_the_outbox():
	# Measured question 3. leaderboard_sync writes the body to the outbox BEFORE
	# dispatch and removes it ONLY on ok (RESULT_SUCCESS + HTTP 200 + ok:true),
	# so a 4xx retains the score and the next launch retries it. Proving the
	# retention primitive: a remove for a DIFFERENT uuid -- which is what a
	# non-ack looks like, since remove is simply never called -- keeps the row.
	var sync = load("res://autoload/leaderboard_sync.gd").new()
	sync._write_outbox([])
	sync._outbox_add({"entry_uuid": "kept-me", "score": 44, "player_name": "GRIM -- Pip"})
	sync._outbox_remove("some-other-uuid")
	var queued: Array = sync._read_outbox()
	assert_eq(queued.size(), 1, "a score the server never acked must stay queued")
	assert_eq(str(queued[0].get("entry_uuid", "")), "kept-me",
		"the unacked score, not some other one, is what survives")
	sync._write_outbox([])
	sync.free()


func test_every_failure_message_says_the_score_was_kept():
	# The player-facing half of the same property: no rejection may read as
	# "my run was lost", because it never is.
	var LS = load("res://autoload/leaderboard_sync.gd")
	for code in [400, 401, 403, 404, 413, 429, 500, 503]:
		var msg: String = LS.submit_status_message(
			false, 0, HTTPRequest.RESULT_SUCCESS, code)
		assert_true(msg.contains("saved locally"),
			"HTTP %d must still tell the player the score is kept; got '%s'" % [code, msg])


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
	# The prompt collects "Operator:" and "Lab:". The wire carries BOTH, composed
	# as `LAB -- OPERATOR` into the frozen `player_name` field (leaderboard.gd:196),
	# so a prompt that implies only the lab appears publicly is lying to the player
	# -- and lying in the direction a privacy statement must never be wrong in.
	var src := _read(GAME_OVER_SRC)
	assert_true(src.contains("IDENTITY_PROMPT_BOARD_NOTE"),
		"the identity prompt must state which of the two values the board shows today")
	var note: String = load(GAME_OVER_SRC).get_script_constant_map().get(
		"IDENTITY_PROMPT_BOARD_NOTE", "")
	assert_true(note.contains("Lab"), "the note must name the Lab name")
	assert_true(note.contains("Operator"), "the note must name the Operator name")
	# The note used to say the Operator name was "saved with the run on this
	# machine". Now that the wire composes both, that sentence would be a
	# PRIVACY misstatement: it would tell a player a name stays local while the
	# client publishes it. Understating what is shared is not a safe default.
	assert_false(note.contains("on this machine"),
		"the note must not still claim the Operator name stays local -- it is published now")
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

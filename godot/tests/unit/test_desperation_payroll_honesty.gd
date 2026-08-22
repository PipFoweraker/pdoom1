extends GutTest
## #967: desperation_payroll promised "-N doom now" and never delivered it.
##
## The offer called state.add_resources({"doom": -suppress}) and told the player
## "Pulled the desperation lever: -10 doom now; a SECRET liability is planted".
##
## That write goes through the INERT sink -- Resources.add() does `state.doom +=
## value` -- and turn_manager clobbers it every resolve with
## `state.doom = doom_system.current_doom` (ADR-0015: the streams are the
## authority). The suppression never survived one resolve.
##
## A no-op is a bug. A no-op that QUOTES A FIGURE is a lie, and that is what this
## fixes: the offer now routes through safety_absorption like its already-corrected
## sibling (actions.gd "desperation_lever") and prints no doom number.
##
## PRICED 2026-08-22, crudely and on purpose. doom.streams.action_desperation_absorb
## was 0.0, which made BOTH desperation levers dead buttons: a secret compounding
## liability bought numerically nothing, so nobody would ever pull one and the
## ledger's teeth could never reach a player. Pip: "I'd rather have a bad thing in
## there now, unsubtle, rather than no thing... players need to suffer."
## It is 25.0 flat now -- uncalibrated, expected to be wrong, and dated for
## balancing on 2026-09-19 (docs/game-design/DESPERATION_LEVER_PRICING.md).

const FE := preload("res://scripts/core/finance_engine.gd")

func _offer_text() -> String:
	"""The desperation_payroll arm with COMMENT LINES STRIPPED.

	The first version of these tests scanned raw source and failed -- on the
	explanatory comment written by the very fix they were checking, which quotes the
	old `add_resources({"doom": ...})` and the old "-%d doom now" message so a reader
	can see what was wrong.

	A text-scanning test that cannot tell code from commentary will either block
	honest documentation or, worse, pass because somebody deleted the explanation.
	Strip comments, scan code."""
	var f := FileAccess.open("res://scripts/core/finance_engine.gd", FileAccess.READ)
	assert_not_null(f, "finance_engine.gd must be readable")
	if f == null:
		return ""
	var raw := f.get_as_text()
	f.close()
	var code_lines: Array[String] = []
	for line in raw.split("
"):
		if line.strip_edges().begins_with("#"):
			continue
		code_lines.append(line)
	var code := "
".join(PackedStringArray(code_lines))
	var idx := code.find("\"desperation_payroll\":")
	if idx == -1:
		return ""
	return code.substr(idx, 1200)

func test_the_offer_no_longer_writes_doom_directly():
	# The inert sink. Any add_resources({"doom": ...}) in this factory is the bug.
	var arm := _offer_text()
	assert_ne(arm, "", "the factory arm still exists")
	assert_eq(arm.find("add_resources({\"doom\""), -1,
		"a direct doom write is clobbered every resolve -- it must not be here")

func test_the_message_quotes_no_doom_number():
	# The part that made it a lie rather than a no-op.
	var arm := _offer_text()
	assert_eq(arm.find("doom now"), -1,
		"the offer must not promise a doom figure it cannot deliver")

func test_it_routes_through_the_systemic_channel_like_its_sibling():
	var arm := _offer_text()
	assert_true(arm.find("safety_absorption") != -1,
		"ADR-0015: reprieve goes through safety_absorption, which the overhang stream reads")

func test_the_secret_liability_is_still_planted():
	# The teeth. The lie was the doom number; the compounding governance liability
	# was always real and must survive the fix.
	var arm := _offer_text()
	assert_true(arm.find("payroll_coinflip") != -1, "the secret entry is still minted")
	assert_true(arm.find("true") != -1, "and still secret")

func test_the_absorb_key_is_declared_not_invented():
	# #1276: an undeclared Balance key silently uses its code-side fallback, which is
	# how a UI drifts from the sim. This one is declared -- assert it stays that way.
	var f := FileAccess.open("res://data/balance/defaults.json", FileAccess.READ)
	assert_not_null(f)
	if f == null:
		return
	var raw := f.get_as_text()
	f.close()
	assert_true(raw.find("action_desperation_absorb") != -1,
		"doom.streams.action_desperation_absorb must exist in defaults.json")

func test_the_reprieve_is_priced_above_zero():
	# The whole point of the 2026-08-22 ruling. At 0.0 both desperation levers were
	# dead buttons: real cost (a secret compounding liability), zero benefit, so
	# nobody pulls them and the trap never springs. The VALUE is expected to be
	# wrong; being ZERO is the defect.
	assert_gt(Balance.num("doom.streams.action_desperation_absorb", 0.0), 0.0,
		"a desperation lever that buys nothing is a dead button, not a hard choice")

extends GutTest
## Locks the number-format policy ruled in #1087 (docs/NUMBER_FORMATS.md).
##
## The observed defect (v0.13.2 playtest, [3:12] "months, years, and cents, and
## billions"): ONE top bar carried four coexisting formats -- `$197,207.69` (money to
## the cent), `82.0` (a one-decimal float for compute), `* 70` (a bare int behind a
## sigil), and a hiring tooltip printing `money: 3000.0` (an internal dict dump).
## Nothing was individually wrong; the absence of a policy was the defect, because
## precision implies meaning it does not have.
##
## The hard requirement guarded here: A RAW FLOAT MUST NEVER REACH THE PLAYER.

const MONEY_SAMPLES := [0.0, 1.0, 999.4, 1000.0, 3000.0, 197207.69, 245000.0, 1234567.89]
const SCALAR_SAMPLES := [0.0, 1.0, 4.5, 82.0, 34.0, 70.0, 3400.0]


# --- Money: whole dollars, grouped, never cents ---------------------------------------

func test_money_never_shows_cents():
	for v in MONEY_SAMPLES:
		var s := GameConfig.format_money(v)
		assert_false(s.contains("."),
			"money must never show cents (a lab budget is not a bank statement): %f -> %s" % [v, s])


func test_money_is_grouped_and_rounded_not_truncated():
	assert_eq(GameConfig.format_money(197207.69), "$197,208",
		"the exact figure from the playtest frame must round to the nearest dollar")
	assert_eq(GameConfig.format_money(245000), "$245,000", "thousands separators (#436)")
	assert_eq(GameConfig.format_money(1234567.89), "$1,234,568", "millions group too")
	assert_eq(GameConfig.format_money(999.6), "$1,000",
		"rounds up -- truncation understated the balance")


func test_negative_money_keeps_the_sign_outside_the_dollar():
	assert_eq(GameConfig.format_money(-1000), "-$1,000")
	assert_eq(GameConfig.format_money(-238.46), "-$238")


func test_money_deltas_are_always_signed():
	assert_eq(GameConfig.format_money_delta(1200.0), "+$1,200")
	assert_eq(GameConfig.format_money_delta(-238.46), "-$238")
	assert_eq(GameConfig.format_money_delta(0.0), "+$0", "zero reads as a non-loss, not a bare 0")


# --- Resource scalars: whole units ------------------------------------------------------

func test_resource_scalars_are_whole_units():
	for v in SCALAR_SAMPLES:
		var s := GameConfig.format_scalar(v)
		assert_false(s.contains("."),
			"no mechanic trades in fractional compute/research/reputation: %f -> %s" % [v, s])
	assert_eq(GameConfig.format_scalar(82.0), "82", "'82.0' was the observed defect")
	assert_eq(GameConfig.format_scalar(3400.0), "3,400", "scalars group like money does")


func test_scalar_deltas_are_always_signed():
	assert_eq(GameConfig.format_scalar_delta(3.0), "+3")
	assert_eq(GameConfig.format_scalar_delta(-1.0), "-1")


# --- Percent: the one place a fraction is load-bearing ----------------------------------

func test_percent_keeps_one_decimal():
	assert_eq(GameConfig.format_percent(14.24), "14.2%",
		"p(Doom) momentum is visible at sub-point grain -- this is the deliberate exception")
	assert_eq(GameConfig.format_percent(14.26), "14.3%")
	assert_eq(GameConfig.format_percent(14.0, 0), "14%")


func test_percent_ties_round_away_from_zero_on_every_platform():
	"""14.25 sits EXACTLY on the boundary, and platforms disagree about it.

	MSVC printf rounds half away from zero; glibc rounds half to even. So this
	assertion passed on Windows and failed on the Ubuntu CI runner, red on main
	from 2026-08-04 until 2026-08-05 -- caught only because a PR inherited it.
	The tie direction is now a stated decision in format_percent, not whatever
	the host libc happens to do, because two players must not read different
	doom figures from the same state.
	"""
	assert_eq(GameConfig.format_percent(14.25), "14.3%", "positive tie rounds up")
	assert_eq(GameConfig.format_percent(-14.25), "-14.3%", "negative tie rounds away from zero")
	assert_eq(GameConfig.format_percent(0.5, 0), "1%", "the same rule at zero decimals")


# --- No internal dict dump can reach a tooltip ------------------------------------------

func test_resource_lines_never_leak_a_key_or_a_float():
	# The literal string that shipped in the hiring tooltip.
	assert_eq(GameConfig.format_resource("money", 3000.0), "Money $3,000",
		"'money: 3000.0' was a debug string in a player-facing tooltip")
	assert_eq(GameConfig.format_resource("attention", 2), "Attention 2")
	assert_eq(GameConfig.format_resource("safety_absorption", 20.0), "Safety Absorption 20",
		"an unmapped internal key must still be humanised, never printed raw")
	for key in ["money", "attention", "compute", "research", "reputation", "safety_absorption"]:
		for v in [0.0, 3000.0, 82.0, 1.0]:
			var line := GameConfig.format_resource(key, v)
			assert_false(line.contains("_"), "no snake_case key may reach the player: %s" % line)
			assert_false(line.contains(".0"), "no raw float may reach the player: %s" % line)


func test_resource_deltas_read_as_effects():
	assert_eq(GameConfig.format_resource_delta("reputation", 5), "Reputation +5")
	assert_eq(GameConfig.format_resource_delta("money", -3000.0), "Money -$3,000")


# --- Source guard: the dict-dump SHAPE may not come back --------------------------------
#
# The formatter tests above prove the right function does the right thing; they cannot
# stop someone re-writing `"  %s: %s" % [resource, costs[resource]]`. This scan forbids
# that exact shape -- a format string that pairs a Variant key with a Variant value --
# in the UI layer. Narrow on purpose: `%s: %s` is the dump, not a general colon.

const UI_DIRS := ["res://scripts/ui"]
const SOURCE_GUARD_EXCLUSIONS := ["office_floor/", "bug_report_panel.gd"]


func _walk_gd(dir_path: String, out: Array) -> void:
	var d := DirAccess.open(dir_path)
	if d == null:
		return
	d.list_dir_begin()
	var name := d.get_next()
	while name != "":
		if not name.begins_with("."):
			var full := dir_path.path_join(name)
			if d.current_is_dir():
				_walk_gd(full, out)
			elif name.get_extension() == "gd":
				var skip := false
				for frag in SOURCE_GUARD_EXCLUSIONS:
					if full.contains(frag):
						skip = true
				if not skip:
					out.append(full)
		name = d.get_next()
	d.list_dir_end()


## Lines carrying the dict-dump format shape. Comments and docstrings stripped, so a
## test/ADR mentioning the pattern in prose does not trip it.
func collect_dict_dump_lines() -> Array:
	var hits: Array = []
	var files: Array = []
	for dir_path in UI_DIRS:
		_walk_gd(dir_path, files)
	# Anchored to the WHOLE literal: the dump shape is a bare "key: value" line and
	# nothing else. A log line like "[color=cyan]%s: %s[/color]" pairs a label with a
	# message -- authored copy, not a dict dump -- and must not false-positive.
	var dump_re := RegEx.create_from_string("\"\\s*%s\\s*:\\s*%s(\\\\n)?\\s*\"")
	for path in files:
		var f := FileAccess.open(path, FileAccess.READ)
		if f == null:
			continue
		var src := f.get_as_text()
		f.close()
		src = RegEx.create_from_string("(?s)\"\"\".*?\"\"\"").sub(src, "", true)
		var line_no := 0
		for line in src.split("\n"):
			line_no += 1
			var code: String = line.split("#")[0]
			if dump_re.search(code) != null:
				hits.append("%s:%d %s" % [path, line_no, code.strip_edges()])
	return hits


func test_no_ui_script_dumps_a_raw_key_value_pair():
	var hits := collect_dict_dump_lines()
	assert_eq(hits.size(), 0,
		"'%%s: %%s' on a state/cost dict is how 'money: 3000.0' shipped -- use "
		+ "GameConfig.format_resource(). Offenders:\n  - %s" % "\n  - ".join(hits))


func test_the_source_guard_is_not_vacuous():
	var files: Array = []
	for dir_path in UI_DIRS:
		_walk_gd(dir_path, files)
	assert_gt(files.size(), 10, "the source guard must actually be reading the UI layer")
	# Anchored to the WHOLE literal: the dump shape is a bare "key: value" line and
	# nothing else. A log line like "[color=cyan]%s: %s[/color]" pairs a label with a
	# message -- authored copy, not a dict dump -- and must not false-positive.
	var dump_re := RegEx.create_from_string("\"\\s*%s\\s*:\\s*%s(\\\\n)?\\s*\"")
	assert_not_null(dump_re.search("tooltip += \"  %s: %s\\n\" % [resource, costs[resource]]"),
		"the detector must match the exact line that shipped the defect")
	assert_null(dump_re.search("tooltip += \"  %s\\n\" % GameConfig.format_resource(k, v)"),
		"the fixed form must not false-positive")

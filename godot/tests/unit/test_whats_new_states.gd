extends GutTest
## The What's New modal must tell the player WHICH of five things went wrong.
##
## WHY THIS EXISTS (Pip's ruling, 2026-08-23): the modal "collapses three
## different failures into one reassuring sentence -- let's do the opposite of
## that." The sentence was "No detailed patch notes available for this version.",
## rendered identically when:
##   1. data/patch_notes.json was missing from the build (a packaging failure),
##   2. the file was present but unreadable or corrupt (a corruption),
##   3. the file loaded fine and had no entry for this version (a content gap).
## Only (3) is that sentence being true. (1) and (2) told the player the release
## was quiet when the real story was a broken build.
##
## Three consequences follow, and each has tests below:
##   WORDS   every outcome gets its own player-facing body -- no two may share.
##   SEEN    only a content gap consumes the version. mark_patch_notes_seen() is
##           irreversible, so burning it on a broken file costs the player the
##           real notes permanently, even after a repaired build.
##   ROUTE   a broken build gets a quotable reference code and a report button;
##           a content gap gets neither, because nothing is wrong.
##
## Companion coverage: test_patch_notes.gd asserts the shipped DATA is present
## and shaped right. This file asserts the modal's BEHAVIOUR when it is not.

const WhatsNewModal := preload("res://scripts/ui/whats_new_modal.gd")
const MODAL_SCENE := preload("res://scenes/ui/whats_new_modal.tscn")
const PATCH_NOTES_PATH := "res://data/patch_notes.json"

const VALID_NOTES := '{"versions": [{"version": "1.2.3", "title": "T", "sections": {}}]}'

## Every state, including the degenerate one. Kept as a single list so a state
## added to the enum and forgotten here is a one-line fix rather than five.
var ALL_STATUSES := [
	WhatsNewModal.LoadStatus.NOT_LOADED,
	WhatsNewModal.LoadStatus.OK,
	WhatsNewModal.LoadStatus.FILE_MISSING,
	WhatsNewModal.LoadStatus.OPEN_FAILED,
	WhatsNewModal.LoadStatus.PARSE_FAILED,
	WhatsNewModal.LoadStatus.BAD_SHAPE,
]

## The four that mean "the build is broken". OK is deliberately absent.
var DEFECT_STATUSES := [
	WhatsNewModal.LoadStatus.NOT_LOADED,
	WhatsNewModal.LoadStatus.FILE_MISSING,
	WhatsNewModal.LoadStatus.OPEN_FAILED,
	WhatsNewModal.LoadStatus.PARSE_FAILED,
	WhatsNewModal.LoadStatus.BAD_SHAPE,
]

var _saved_last_seen: String = ""


func before_all() -> void:
	# show_modal() writes through GameConfig.mark_patch_notes_seen(), which calls
	# save_config(). The runner sandboxes the user directory, but leaving a
	# neighbouring test's gate flipped is still a way to make a suite lie.
	_saved_last_seen = GameConfig.last_seen_version

func after_all() -> void:
	GameConfig.last_seen_version = _saved_last_seen
	GameConfig.save_config()


func _modal() -> Node:
	# .new() does NOT run _ready(), so the @onready node refs stay null. The
	# methods exercised through this helper (ingest / load_from_path / statics)
	# are deliberately free of them.
	return autofree(WhatsNewModal.new())

func _scene_modal() -> Node:
	# _ready() runs here, so the labels exist and _display_* can be called.
	var modal = MODAL_SCENE.instantiate()
	add_child_autofree(modal)
	return modal


# --------------------------------------------------------------------------
# WORDS -- the collapse must be impossible to reintroduce
# --------------------------------------------------------------------------

func test_every_status_has_its_own_player_facing_body() -> void:
	# The original defect, stated as an assertion. Four of these five used to be
	# byte-identical to the fifth.
	var seen := {}
	for status in ALL_STATUSES:
		var body := String(WhatsNewModal.status_report(status)["body"])
		assert_ne(body, "", "status %d needs its own player-facing text" % status)
		assert_false(seen.has(body),
			"status %d reuses the body already used by status %s -- the whole point is that these read differently"
			% [status, str(seen.get(body, "?"))])
		seen[body] = status

func test_every_status_has_its_own_developer_facing_cause() -> void:
	var seen := {}
	for status in ALL_STATUSES:
		var cause := WhatsNewModal.describe_load_status(status)
		assert_ne(cause, "", "status %d needs a cause for the log" % status)
		assert_false(seen.has(cause), "status %d reuses the cause '%s'" % [status, cause])
		seen[cause] = true

func test_only_a_content_gap_is_not_a_defect() -> void:
	assert_false(bool(WhatsNewModal.status_report(WhatsNewModal.LoadStatus.OK)["is_defect"]),
		"a version with no notes written for it is a legitimate release, not a bug")
	for status in DEFECT_STATUSES:
		assert_true(bool(WhatsNewModal.status_report(status)["is_defect"]),
			"status %d (%s) means the build is broken and must be flagged as a defect"
			% [status, WhatsNewModal.describe_load_status(status)])

func test_no_defect_text_claims_the_release_had_no_notes() -> void:
	# The exact lie the ruling is about: telling the player the release was quiet
	# when the truth is that the file could not be read.
	for status in DEFECT_STATUSES:
		var body := String(WhatsNewModal.status_report(status)["body"])
		assert_false(body.contains("No detailed patch notes were written"),
			"status %d must not tell the player the release was quiet: %s" % [status, body])
		assert_false(body.contains("simply did not come with"),
			"status %d must not imply an empty release: %s" % [status, body])

func test_the_content_gap_text_does_not_accuse_the_build() -> void:
	# The mirror error. Claiming a defect where there is none sends the player
	# chasing a bug that does not exist.
	var body := String(WhatsNewModal.status_report(WhatsNewModal.LoadStatus.OK)["body"])
	assert_false(body.to_lower().contains("could not"),
		"a genuinely quiet release must not be described as a failure: %s" % body)
	assert_false(body.to_lower().contains("damaged"), body)

func test_player_facing_text_is_ascii_only() -> void:
	# House rule #744 plus the blocking no-emoji gate. These strings are rendered
	# through a BBCode label, so a smart quote is both a commit blocker and a
	# rendering risk.
	for status in ALL_STATUSES:
		var row := WhatsNewModal.status_report(status)
		for key in ["body", "code", "cause"]:
			var text := String(row[key])
			for i in text.length():
				assert_lt(text.unicode_at(i), 128,
					"status %d %s has a non-ASCII codepoint at %d: %s" % [status, key, i, text])


# --------------------------------------------------------------------------
# ROUTE -- how a player on a console-less build tells us which one they hit
# --------------------------------------------------------------------------

func test_only_defects_carry_a_reference_code() -> void:
	assert_eq(String(WhatsNewModal.status_report(WhatsNewModal.LoadStatus.OK)["code"]), "",
		"a quiet release has nothing to report, so offering a code would invent a defect")
	for status in DEFECT_STATUSES:
		assert_ne(String(WhatsNewModal.status_report(status)["code"]), "",
			"status %d is unreportable without a code -- a shipped build has no console"
			% status)

func test_reference_codes_are_distinct_and_quotable() -> void:
	var seen := {}
	for status in DEFECT_STATUSES:
		var code := String(WhatsNewModal.status_report(status)["code"])
		assert_false(seen.has(code),
			"status %d reuses code '%s' -- two causes behind one code is the same collapse"
			% [status, code])
		seen[code] = true
		# Short, upper-case, no spaces: a player has to read it off a screen and
		# type it into a report.
		assert_true(code.begins_with("PN-"), "code '%s' should be namespaced PN-" % code)
		assert_lt(code.length(), 16, "code '%s' is too long to quote by hand" % code)
		assert_eq(code, code.to_upper(), "code '%s' should be upper case" % code)
		assert_false(code.contains(" "), "code '%s' must not contain spaces" % code)

func test_a_defect_builds_a_report_that_names_the_cause() -> void:
	for status in DEFECT_STATUSES:
		var row := WhatsNewModal.status_report(status)
		var code := String(row["code"])
		var report := WhatsNewModal.build_defect_report(status, "9.9.9")
		assert_false(report.is_empty(), "status %d must produce a report" % status)
		assert_true(String(report.get("title", "")).contains(code),
			"the report title must carry the code the player can see: %s" % report.get("title", ""))
		var description := String(report.get("description", ""))
		assert_true(description.contains("9.9.9"),
			"the report must name the version the player could not read notes for")
		assert_true(description.contains(String(row["cause"])),
			"the report must carry the cause, or triage is back to guessing")
		# Both one-click exits carry it: the clipboard text and the issue URL.
		var transport := BugReporter.format_for_transport(report)
		assert_true(transport.contains(code),
			"the pasteable report must carry the code")
		assert_true(BugReporter.github_issue_url(report).contains(code),
			"the pre-filled issue must carry the code")

func test_a_quiet_release_produces_no_report() -> void:
	assert_true(WhatsNewModal.build_defect_report(WhatsNewModal.LoadStatus.OK, "9.9.9").is_empty(),
		"manufacturing a bug report for a release that simply had no notes is the same lie inverted")


# --------------------------------------------------------------------------
# SEEN -- the irreversible bookkeeping
# --------------------------------------------------------------------------

func test_a_shown_entry_always_consumes_the_version() -> void:
	for status in ALL_STATUSES:
		assert_true(WhatsNewModal.should_mark_seen(true, status),
			"status %d: the player read real notes, so the showing is spent" % status)

func test_a_genuine_content_gap_consumes_the_version() -> void:
	# The data was readable and says this version has nothing. Re-offering it on
	# every launch would nag forever about a release that has nothing to say.
	assert_true(WhatsNewModal.should_mark_seen(false, WhatsNewModal.LoadStatus.OK))

func test_a_broken_file_never_consumes_the_version() -> void:
	# The regression that costs the most. mark_patch_notes_seen() writes
	# last_seen_version = CURRENT_VERSION and has_unseen_patch_notes() is an
	# inequality against it, so this is permanent for this version.
	for status in DEFECT_STATUSES:
		assert_false(WhatsNewModal.should_mark_seen(false, status),
			("status %d (%s) must NOT consume the version -- the player is owed "
			+ "another look once the build is fixed")
			% [status, WhatsNewModal.describe_load_status(status)])

func test_the_seen_rule_and_the_defect_flag_stay_in_step() -> void:
	# should_mark_seen() is defined as "not a defect"; if someone ever hand-codes
	# one of the two, this catches the drift.
	for status in ALL_STATUSES:
		assert_eq(WhatsNewModal.should_mark_seen(false, status),
			not bool(WhatsNewModal.status_report(status)["is_defect"]),
			"status %d: the seen rule and the defect flag disagree" % status)


# --------------------------------------------------------------------------
# The wiring -- the rules above only matter if show_modal() consults them
# --------------------------------------------------------------------------

func _stage_fallback(modal, status: int) -> void:
	# Non-empty data so show_modal() does not reload from the real file and
	# overwrite the status under test; no entries, so no version can match and
	# the fallback is what fires.
	modal.patch_notes_data = {"versions": []}
	modal.load_status = status

func test_show_modal_does_not_burn_the_version_when_the_file_is_broken() -> void:
	var modal = _scene_modal()
	_stage_fallback(modal, WhatsNewModal.LoadStatus.PARSE_FAILED)
	GameConfig.last_seen_version = "0.0.0-sentinel"
	modal.show_modal(true)
	assert_eq(GameConfig.last_seen_version, "0.0.0-sentinel",
		"a corrupt patch-notes file must not consume the player's one showing")

func test_show_modal_burns_the_version_when_the_release_is_genuinely_quiet() -> void:
	var modal = _scene_modal()
	_stage_fallback(modal, WhatsNewModal.LoadStatus.OK)
	GameConfig.last_seen_version = "0.0.0-sentinel"
	modal.show_modal(true)
	assert_eq(GameConfig.last_seen_version, GameConfig.CURRENT_VERSION,
		"a readable file with no entry for this version is honest to mark seen")

func test_show_modal_respects_mark_as_seen_false() -> void:
	var modal = _scene_modal()
	_stage_fallback(modal, WhatsNewModal.LoadStatus.OK)
	GameConfig.last_seen_version = "0.0.0-sentinel"
	modal.show_modal(false)
	assert_eq(GameConfig.last_seen_version, "0.0.0-sentinel")


# --------------------------------------------------------------------------
# What the player actually reads, rendered
# --------------------------------------------------------------------------

func test_rendered_fallback_differs_for_every_status() -> void:
	var seen := {}
	for status in ALL_STATUSES:
		var modal = _scene_modal()
		modal.load_status = status
		modal._display_fallback_notes("1.2.3")
		var text: String = modal.content_label.text
		assert_false(seen.has(text),
			"status %d renders the same screen as status %s" % [status, str(seen.get(text, "?"))])
		seen[text] = status

func test_rendered_defect_shows_the_code_and_the_report_button() -> void:
	for status in DEFECT_STATUSES:
		var modal = _scene_modal()
		modal.load_status = status
		modal._display_fallback_notes("1.2.3")
		var code := String(WhatsNewModal.status_report(status)["code"])
		assert_true(modal.content_label.text.contains(code),
			"status %d must show its reference code on screen, got: %s"
			% [status, modal.content_label.text])
		assert_not_null(modal.report_button, "status %d needs the report route" % status)
		assert_true(modal.report_button.visible,
			"status %d must offer the report button" % status)

func test_rendered_content_gap_offers_no_code_and_no_report_button() -> void:
	var modal = _scene_modal()
	modal.load_status = WhatsNewModal.LoadStatus.OK
	modal._display_fallback_notes("1.2.3")
	assert_false(modal.content_label.text.contains("Reference code"),
		"a quiet release is not a defect and must not hand the player a code")
	if modal.report_button != null:
		assert_false(modal.report_button.visible,
			"a quiet release must not ask the player to report a bug")

func test_the_report_button_is_hidden_once_real_notes_are_shown() -> void:
	# Same node, two states: the button must not survive from a failed load into
	# a screen that worked.
	var modal = _scene_modal()
	modal.load_status = WhatsNewModal.LoadStatus.FILE_MISSING
	modal._display_fallback_notes("1.2.3")
	assert_true(modal.report_button.visible)
	modal._display_version_notes({"version": "1.2.3", "title": "T", "highlights": ["x"]})
	assert_false(modal.report_button.visible,
		"notes rendered fine, so there is nothing to report")

func test_the_report_button_is_hidden_in_the_all_notes_view() -> void:
	var modal = _scene_modal()
	modal.load_status = WhatsNewModal.LoadStatus.BAD_SHAPE
	modal._display_fallback_notes("1.2.3")
	assert_true(modal.report_button.visible)
	modal._display_all_notes()
	assert_false(modal.report_button.visible)


# --------------------------------------------------------------------------
# Reaching the states for real, not just naming them
# --------------------------------------------------------------------------

func test_a_missing_file_really_reports_file_missing() -> void:
	var modal := _modal()
	assert_eq(int(modal.load_from_path("res://data/no_such_patch_notes_file.json")),
		WhatsNewModal.LoadStatus.FILE_MISSING,
		"the FILE_MISSING branch must be reachable, or nobody has ever checked it")
	assert_true(modal.patch_notes_data.is_empty())

func test_valid_notes_load_ok() -> void:
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text(VALID_NOTES)), WhatsNewModal.LoadStatus.OK)
	assert_eq(modal.patch_notes_data.get("versions", []).size(), 1)

func test_unparseable_json_is_parse_failed_not_ok() -> void:
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text("{ this is not json")),
		WhatsNewModal.LoadStatus.PARSE_FAILED,
		"a corrupt file must be distinguishable from a version with no notes")
	assert_true(modal.patch_notes_data.is_empty(),
		"a failed parse must not leave half-loaded data behind")

func test_valid_json_of_the_wrong_shape_is_bad_shape() -> void:
	# A bare array is valid JSON. Treating it as notes yields zero versions --
	# which looks exactly like a quiet release.
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text('["not", "an", "object"]')),
		WhatsNewModal.LoadStatus.BAD_SHAPE)

func test_object_without_versions_array_is_bad_shape() -> void:
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text('{"somethingelse": 1}')),
		WhatsNewModal.LoadStatus.BAD_SHAPE)

func test_versions_of_the_wrong_type_is_bad_shape() -> void:
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text('{"versions": "soon"}')),
		WhatsNewModal.LoadStatus.BAD_SHAPE)

func test_the_shipped_patch_notes_file_loads_cleanly() -> void:
	# If this goes red, every player sees a fallback screen.
	var modal := _modal()
	assert_eq(int(modal.load_from_path(PATCH_NOTES_PATH)), WhatsNewModal.LoadStatus.OK,
		"the shipped patch_notes.json must load")

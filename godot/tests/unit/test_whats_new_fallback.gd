extends GutTest
## The What's New modal must not say "no notes" when it means "could not read notes".
##
## WHY THIS EXISTS (2026-08-24):
## Three genuinely different conditions collapsed into one reassuring sentence --
## "No detailed patch notes available for this version." -- shown identically when:
##   1. data/patch_notes.json was missing from the build,
##   2. the file was there but was not valid JSON,
##   3. the file loaded fine and simply had no entry for this version.
## Only (3) is the sentence being true. (1) and (2) mean the BUILD is broken, and the
## player was told the release was quiet instead.
##
## Worse, mark_patch_notes_seen() ran on the fallback path unconditionally.
## GameConfig.has_unseen_patch_notes() is an inequality against last_seen_version, so
## a build that shipped without the data file silently consumed the player's one
## showing -- they never got a second chance at the real notes, not even after a
## repaired build.
##
## Companion coverage: test_patch_notes.gd asserts the DATA is present and shaped
## right. This file asserts the modal's BEHAVIOUR when it is not.

const WhatsNewModal := preload("res://scripts/ui/whats_new_modal.gd")
const MODAL_SCENE := preload("res://scenes/ui/whats_new_modal.tscn")
const PATCH_NOTES_PATH := "res://data/patch_notes.json"

const VALID_NOTES := '{"versions": [{"version": "1.2.3", "title": "T", "sections": {}}]}'


func _modal() -> Node:
	# .new() does NOT run _ready(), so the @onready node refs stay null. Every method
	# exercised here (ingest / lookup / the two statics) is deliberately free of them.
	return autofree(WhatsNewModal.new())


# --------------------------------------------------------------------------
# The three causes must stay three causes
# --------------------------------------------------------------------------

func test_valid_notes_load_ok() -> void:
	var modal := _modal()
	var status: int = modal.ingest_patch_notes_text(VALID_NOTES)
	assert_eq(status, WhatsNewModal.LoadStatus.OK, "well-formed notes should load")
	assert_eq(modal.patch_notes_data.get("versions", []).size(), 1)

func test_unparseable_json_is_parse_failed_not_ok() -> void:
	var modal := _modal()
	var status: int = modal.ingest_patch_notes_text("{ this is not json")
	assert_eq(status, WhatsNewModal.LoadStatus.PARSE_FAILED,
		"a corrupt file must be distinguishable from a version with no notes")
	assert_true(modal.patch_notes_data.is_empty(),
		"a failed parse must not leave half-loaded data behind")

func test_valid_json_of_the_wrong_shape_is_bad_shape() -> void:
	# A bare array is valid JSON. Assigning it into a typed Dictionary would error,
	# and treating it as notes would silently yield zero versions.
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text('["not", "an", "object"]')),
		WhatsNewModal.LoadStatus.BAD_SHAPE)

func test_object_without_versions_array_is_bad_shape() -> void:
	var modal := _modal()
	assert_eq(int(modal.ingest_patch_notes_text('{"somethingelse": 1}')),
		WhatsNewModal.LoadStatus.BAD_SHAPE)

func test_each_cause_has_its_own_description() -> void:
	# The whole point is that these do not collapse into one sentence.
	var seen := {}
	for status in [
		WhatsNewModal.LoadStatus.OK,
		WhatsNewModal.LoadStatus.FILE_MISSING,
		WhatsNewModal.LoadStatus.OPEN_FAILED,
		WhatsNewModal.LoadStatus.PARSE_FAILED,
		WhatsNewModal.LoadStatus.BAD_SHAPE,
		WhatsNewModal.LoadStatus.NOT_LOADED,
	]:
		var text: String = WhatsNewModal.describe_load_status(status)
		assert_ne(text, "", "status %d needs a description" % status)
		assert_false(seen.has(text),
			"status %d reuses the description '%s' -- causes must stay distinct"
			% [status, text])
		seen[text] = true


# --------------------------------------------------------------------------
# Burning the version is the expensive mistake
# --------------------------------------------------------------------------

func test_version_is_marked_seen_when_it_genuinely_has_no_notes() -> void:
	# Data loaded, no entry for this version. The sentence is true; consume the showing.
	assert_true(WhatsNewModal.should_mark_seen(false, WhatsNewModal.LoadStatus.OK))

func test_version_is_marked_seen_when_real_notes_were_shown() -> void:
	assert_true(WhatsNewModal.should_mark_seen(true, WhatsNewModal.LoadStatus.OK))

func test_version_is_NOT_marked_seen_when_the_data_could_not_be_read() -> void:
	# The regression that matters. Each of these means "broken build", and burning the
	# version here costs the player the real notes permanently.
	for status in [
		WhatsNewModal.LoadStatus.FILE_MISSING,
		WhatsNewModal.LoadStatus.OPEN_FAILED,
		WhatsNewModal.LoadStatus.PARSE_FAILED,
		WhatsNewModal.LoadStatus.BAD_SHAPE,
		WhatsNewModal.LoadStatus.NOT_LOADED,
	]:
		assert_false(WhatsNewModal.should_mark_seen(false, status),
			("status %d (%s) must NOT consume the version -- the player is owed "
			+ "another look once the build is fixed")
			% [status, WhatsNewModal.describe_load_status(status)])

func test_a_shown_entry_still_marks_seen_even_if_the_load_was_odd() -> void:
	# If we actually rendered notes, the player got what they were owed.
	assert_true(WhatsNewModal.should_mark_seen(true, WhatsNewModal.LoadStatus.BAD_SHAPE))


# --------------------------------------------------------------------------
# What the player actually reads
# --------------------------------------------------------------------------

func test_fallback_text_does_not_claim_absence_when_the_file_failed() -> void:
	var modal = MODAL_SCENE.instantiate()
	add_child_autofree(modal)
	modal.load_status = WhatsNewModal.LoadStatus.PARSE_FAILED
	modal._display_fallback_notes("1.2.3")
	var text: String = modal.content_label.text
	assert_true(text.contains("could not be loaded"),
		"a corrupt data file must be described as a load failure, got: %s" % text)
	assert_false(text.contains("No detailed patch notes were written"),
		"must not tell the player the release was quiet when the file failed to parse")

func test_fallback_text_may_state_absence_when_the_data_really_is_silent() -> void:
	var modal = MODAL_SCENE.instantiate()
	add_child_autofree(modal)
	modal.load_status = WhatsNewModal.LoadStatus.OK
	modal._display_fallback_notes("1.2.3")
	var text: String = modal.content_label.text
	assert_true(text.contains("No detailed patch notes were written"),
		"when the data loaded and has no entry, saying so is honest; got: %s" % text)


# --------------------------------------------------------------------------
# The shipped data file itself
# --------------------------------------------------------------------------

func test_the_shipped_patch_notes_file_ingests_cleanly() -> void:
	# Mirrors tools/check_patch_notes.py, which gates this at commit time because
	# pre-commit cannot run the Godot tier.
	var file := FileAccess.open(PATCH_NOTES_PATH, FileAccess.READ)
	assert_not_null(file, "patch_notes.json must be in the build")
	if file == null:
		return
	var text := file.get_as_text()
	file.close()
	assert_eq(int(_modal().ingest_patch_notes_text(text)), WhatsNewModal.LoadStatus.OK,
		"the shipped patch_notes.json must load, or every player sees the fallback")

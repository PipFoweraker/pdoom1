extends GutTest
## The What's New modal must have something to say about the version that shipped.
##
## WHY THIS EXISTS: patch_notes.json went three releases stale (last entry 0.11.0
## while 0.14.0 was live and published), so whats_new_modal.gd fell through to
## _display_fallback_notes() and told every player "No detailed patch notes
## available for this version." Nothing failed; the modal just quietly said
## nothing. A staleness check is the only thing that turns that into a red test
## instead of a player-visible shrug.

const PATCH_NOTES_PATH := "res://data/patch_notes.json"

var _data: Dictionary = {}

func before_all() -> void:
	var file := FileAccess.open(PATCH_NOTES_PATH, FileAccess.READ)
	assert_not_null(file, "patch_notes.json must exist at %s" % PATCH_NOTES_PATH)
	if file == null:
		return
	var json := JSON.new()
	var err := json.parse(file.get_as_text())
	file.close()
	assert_eq(err, OK, "patch_notes.json must be valid JSON")
	if err == OK:
		_data = json.get_data()

func _versions() -> Array:
	return _data.get("versions", [])

func test_shipped_version_has_an_entry() -> void:
	# whats_new_modal._get_version_data() matches on the EXACT string returned by
	# GameConfig.get_current_version(), so a "v" prefix or a trailing space here
	# is the same failure as no entry at all.
	var current := GameConfig.get_current_version()
	var found := false
	for entry in _versions():
		if entry.get("version", "") == current:
			found = true
			break
	assert_true(found,
		("patch_notes.json has no entry for the shipped version %s -- the What's New "
		+ "modal will show its 'no detailed patch notes' fallback to every player. "
		+ "Add an entry before cutting the release.") % current)

func test_shipped_entry_says_something() -> void:
	var current := GameConfig.get_current_version()
	for entry in _versions():
		if entry.get("version", "") != current:
			continue
		assert_gt(int(String(entry.get("title", "")).length()), 0,
			"the %s entry needs a title -- the modal renders it in the header" % current)
		var sections: Dictionary = entry.get("sections", {})
		var body_count := int(entry.get("highlights", []).size())
		body_count += int(sections.get("added", []).size())
		body_count += int(sections.get("fixed", []).size())
		body_count += int(sections.get("changed", []).size())
		assert_gt(body_count, 0,
			"the %s entry is empty -- an entry with no lines renders a blank modal, "
			% current + "which is the fallback message with extra steps")
		return

func test_every_entry_has_the_shape_the_modal_reads() -> void:
	# The modal calls .get() with defaults everywhere, so a malformed entry does
	# not crash -- it silently renders less. Assert the shape instead.
	assert_gt(_versions().size(), 0, "patch_notes.json must list at least one version")
	for entry in _versions():
		var version := String(entry.get("version", ""))
		assert_ne(version, "", "every entry needs a version string")
		assert_true(entry.has("title"), "%s: entry needs a title" % version)
		assert_true(entry.has("sections"), "%s: entry needs a sections dictionary" % version)
		assert_true(entry.get("sections", {}) is Dictionary,
			"%s: sections must be a Dictionary" % version)

func test_notes_are_ascii_only() -> void:
	# House rule #744 plus the blocking no-emoji gate: these strings are
	# player-facing and go through a BBCode label, so a stray smart quote is both
	# a commit blocker and a rendering risk.
	for entry in _versions():
		var version := String(entry.get("version", ""))
		var strings: Array = [String(entry.get("title", "")), String(entry.get("date", ""))]
		strings.append_array(entry.get("highlights", []))
		var sections: Dictionary = entry.get("sections", {})
		for key in ["added", "fixed", "changed"]:
			strings.append_array(sections.get(key, []))
		for text in strings:
			var line := String(text)
			var offenders := ""
			for i in line.length():
				if line.unicode_at(i) >= 128:
					offenders += " U+%04X@%d" % [line.unicode_at(i), i]
			assert_eq(offenders, "",
				"%s: non-ASCII in patch note line '%s' --%s" % [version, line, offenders])

extends GutTest
## Guard test for issue #971: Balance.num("doom.streams.action_*", ...) call sites in
## actions.gd silently fall back to 0.0 (or a code-side default) when their key is
## missing from defaults.json -- exactly how publish_paper/safety_research/audit_safety
## shipped as no-ops post-ADR-0015. This scans actions.gd for every Balance.num() key
## literal and asserts it resolves against defaults.json, so a future new stream key
## added to actions.gd without a matching defaults.json entry fails CI instead of
## degrading silently to its in-code fallback.

const ACTIONS_SRC_PATH := "res://scripts/core/actions.gd"
const DEFAULTS_PATH := "res://data/balance/defaults.json"


func test_every_balance_num_key_in_actions_exists_in_defaults() -> void:
	var src: String = FileAccess.get_file_as_string(ACTIONS_SRC_PATH)
	assert_false(src.is_empty(), "expected to read %s" % ACTIONS_SRC_PATH)

	var regex := RegEx.new()
	regex.compile("Balance\\.num\\(\\s*\"([^\"]+)\"")
	var matches := regex.search_all(src)
	assert_gt(matches.size(), 0, "expected at least one Balance.num() call site in actions.gd")

	var defaults_text: String = FileAccess.get_file_as_string(DEFAULTS_PATH)
	var json := JSON.new()
	var err := json.parse(defaults_text)
	assert_eq(err, OK, "defaults.json should parse as valid JSON")
	var data = json.get_data()
	assert_true(data is Dictionary, "defaults.json root should be an object")

	var missing: Array[String] = []
	var seen: Dictionary = {}
	for m in matches:
		var key: String = m.get_string(1)
		if seen.has(key):
			continue
		seen[key] = true
		var node = data
		var found := true
		for part in key.split("."):
			if node is Dictionary and node.has(part):
				node = node[part]
			else:
				found = false
				break
		if not found:
			missing.append(key)

	assert_eq(missing.size(), 0,
		"Balance.num() keys referenced in actions.gd but missing from defaults.json (silent 0.0/code-fallback): %s" % [missing])

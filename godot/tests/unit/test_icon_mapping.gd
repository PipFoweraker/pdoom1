extends GutTest
## Guards that promoted action icons actually resolve to real textures and not to
## the magenta/cyan checkerboard placeholder IconLoader hands back for unmapped or
## unloadable ids (see autoload/icon_loader.gd::_create_placeholder_texture).
##
## Batch #649 promoted eight stopgap action icons; this test fails LOUDLY if any of
## them regresses to the placeholder (mapping repointed to a missing file, asset
## dropped from the commit, or import not run). It also floors the list so a refactor
## that empties it cannot pass vacuously.

# Action ids promoted in batch #649. These live across the actions/ and fundraising/
# mapping sections; IconLoader.get_action_icon() searches all three.
const PROMOTED_ACTIONS := [
	"team_building",
	"network",
	"acquire_startup",
	"sabotage_competitor",
	"lobby_government",
	"open_source_release",
	"take_loan",
	"grant_proposal",
]

const MIN_PROMOTED := 8


func test_floor_not_hollow():
	assert_true(
		PROMOTED_ACTIONS.size() >= MIN_PROMOTED,
		"expected at least %d promoted action ids, found %d" % [MIN_PROMOTED, PROMOTED_ACTIONS.size()]
	)


func test_promoted_icons_are_not_placeholder():
	# A deliberately unmapped id returns the shared placeholder instance; every real
	# id must return a DIFFERENT texture (reference inequality is enough because the
	# placeholder is a single cached ImageTexture).
	var placeholder := IconLoader.get_action_icon("__no_such_action_id__")
	assert_not_null(placeholder, "sanity: IconLoader should hand back a placeholder for a bogus id")

	for action_id in PROMOTED_ACTIONS:
		var tex := IconLoader.get_action_icon(action_id)
		assert_not_null(tex, "icon for '%s' should not be null" % action_id)
		assert_true(
			tex != placeholder,
			"action '%s' resolves to the checkerboard placeholder -- promotion/mapping broken" % action_id
		)


func test_mapped_icon_files_exist():
	# Independent of IconLoader's cache: read the mapping JSON and confirm each
	# promoted id points at a resource that actually exists on disk (imported).
	var file := FileAccess.open("res://data/icon_mapping.json", FileAccess.READ)
	assert_not_null(file, "icon_mapping.json must be readable")
	var json := JSON.new()
	assert_eq(json.parse(file.get_as_text()), OK, "icon_mapping.json must be valid JSON")
	var data: Dictionary = json.data
	file.close()

	for action_id in PROMOTED_ACTIONS:
		var path := ""
		for section in ["actions", "hiring", "fundraising"]:
			var entry = data.get(section, {}).get(action_id, null)
			if entry is Dictionary:
				path = entry.get("icon", "")
				break
		assert_ne(path, "", "no mapping entry found for '%s'" % action_id)
		assert_true(
			ResourceLoader.exists(path),
			"mapped icon for '%s' does not exist: %s" % [action_id, path]
		)

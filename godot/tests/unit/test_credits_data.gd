extends GutTest
## Guards the in-game credits surface. Three failure modes, all of which are
## SILENT -- the game runs perfectly with any of them and the only symptom is a
## contributor who is not credited, or is credited wrongly, and never finds out.
##
## 1. THE ROSTER DRIFTS. office_cat.gd's CAT_NAMES decides which cats a player
##    sees; CREDITS.md decides who gets named for them. Add a cat to one and not
##    the other and the game happily ships an uncredited cat forever.
## 2. THE SCREEN BECOMES UNREACHABLE. A credits screen nobody can open is the
##    same as no credits screen. This asserts the welcome menu still has the
##    button and still points at the scene.
## 3. A PLACEHOLDER SHIPS. CREDITS.md carries "[Pip to fill]" / "[Pip to
##    confirm]" markers by design. generate_credits.py drops them; if that drop
##    ever regresses, a player sees a TODO where a person's name belongs.
##
## Honest limitation: none of this proves a cat photo reached a screen, or that
## a contributor is happy with the name form used. The first needs a human
## looking at an exported build; the second needs Pip asking them (tracked in
## the CREDITS.md checklist).

const OFFICE_CAT_SCRIPT_PATH := "res://scripts/ui/office_cat.gd"
const WELCOME_SCENE_PATH := "res://scenes/welcome.tscn"
const WELCOME_SCRIPT_PATH := "res://scripts/ui/welcome_screen.gd"
const CREDITS_SCENE_PATH := "res://scenes/credits_screen.tscn"
const CAT_IMAGES_PATH := "res://assets/cats/simple/"

# Eight cats shipped in v0.13.2. Floored so an empty roster cannot pass this
# file vacuously (same reasoning as test_office_cat_assets.gd).
const MIN_CATS := 8


func before_each() -> void:
	CreditsData.reset_cache()


func _read(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	assert_not_null(f, "could not read " + path)
	if f == null:
		return ""
	var text := f.get_as_text()
	f.close()
	return text


func _cat_names() -> Dictionary:
	var script: GDScript = load(OFFICE_CAT_SCRIPT_PATH)
	assert_not_null(script, "could not load " + OFFICE_CAT_SCRIPT_PATH)
	return script.get_script_constant_map().get("CAT_NAMES", {})


func test_credits_data_loads_with_cats_and_sections():
	assert_true(
		FileAccess.file_exists(CreditsData.CREDITS_PATH),
		"credits.json is missing -- run: python scripts/generate_credits.py"
	)
	assert_true(
		CreditsData.cats().size() >= MIN_CATS,
		"expected at least %d credited cats, found %d" % [MIN_CATS, CreditsData.cats().size()]
	)
	assert_gt(CreditsData.sections().size(), 0, "credits.json carries no credit sections at all")


func test_cat_roster_matches_office_cat():
	# The load-bearing reconciliation. CAT_NAMES is what players SEE;
	# credits.json is who gets NAMED. They must describe the same eight cats.
	var in_game: Dictionary = _cat_names()
	var credited := {}
	for entry in CreditsData.cats():
		credited[str(entry.get("asset", ""))] = str(entry.get("name", ""))

	for asset in in_game.keys():
		assert_true(
			credited.has(asset),
			"cat '%s' ships in office_cat.gd but has no row in CREDITS.md -- it would"
			% asset
			+ " appear in game with nobody credited for it. Add it to the Cats table."
		)
	for asset in credited.keys():
		assert_true(
			in_game.has(asset),
			"CREDITS.md credits '%s' but office_cat.gd never shows it -- either the"
			% asset
			+ " asset was dropped from the game or the table has a typo."
		)
	for asset in credited.keys():
		if in_game.has(asset):
			assert_eq(
				str(credited[asset]),
				str(in_game[asset]),
				"cat display name disagrees between CREDITS.md and office_cat.gd for " + asset
			)


func test_every_credited_cat_asset_resolves():
	# ResourceLoader, never FileAccess: the exported .pck holds the imported
	# .ctex, not the source .jpg (#796).
	for entry in CreditsData.cats():
		var path: String = CAT_IMAGES_PATH + str(entry.get("asset", ""))
		assert_true(
			ResourceLoader.exists(path),
			"credited cat asset does not resolve through the import system: " + path
		)


func test_no_unresolved_placeholder_reaches_a_player():
	var raw := _read(CreditsData.CREDITS_PATH).to_lower()
	for marker in ["to fill", "to confirm", "[pip"]:
		assert_false(
			raw.contains(marker),
			"credits.json contains the unresolved marker '%s'." % marker
			+ " generate_credits.py is meant to DROP any entry still carrying one;"
			+ " a player would otherwise read a TODO where a contributor's name goes."
		)


func test_credits_screen_is_reachable_from_the_welcome_menu():
	# Failure mode 2: the surface exists but nothing opens it.
	assert_true(
		ResourceLoader.exists(CREDITS_SCENE_PATH), "missing scene: " + CREDITS_SCENE_PATH
	)
	var welcome_scene := _read(WELCOME_SCENE_PATH)
	assert_true(
		welcome_scene.contains("CreditsButton"),
		"welcome.tscn no longer has a CreditsButton -- the credits screen is unreachable."
	)
	var welcome_script := _read(WELCOME_SCRIPT_PATH)
	assert_true(
		welcome_script.contains(CREDITS_SCENE_PATH),
		"welcome_screen.gd no longer routes to " + CREDITS_SCENE_PATH
	)


func test_credits_screen_actually_renders_every_cat():
	# The only test here that runs the real screen. A data file can be perfect
	# while the surface that reads it renders an empty box -- which is how the
	# slot picker shipped with overlapping cards: nobody opened it.
	var packed: PackedScene = load(CREDITS_SCENE_PATH)
	assert_not_null(packed, "could not load " + CREDITS_SCENE_PATH)
	if packed == null:
		return
	var screen: Control = packed.instantiate()
	add_child_autofree(screen)
	await get_tree().process_frame

	var content: VBoxContainer = screen.get_node("Panel/VBox/ContentScroll/Content")
	assert_gt(content.get_child_count(), 0, "the credits screen rendered nothing at all")

	var cards := 0
	for child in content.get_children():
		if child is HFlowContainer:
			cards = child.get_child_count()
	assert_eq(
		cards,
		CreditsData.cats().size(),
		"the cat grid rendered %d cards for %d credited cats" % [cards, CreditsData.cats().size()]
	)


func test_office_cat_credit_lookup_is_not_a_second_hardcoded_table():
	# The cat -> person mapping must exist exactly once. If office_cat.gd ever
	# grows its own name table, one of the two copies will go stale silently.
	var src := _read(OFFICE_CAT_SCRIPT_PATH)
	assert_true(
		src.contains("CreditsData.credit_for_asset"),
		"office_cat.gd should look its contributor credit up through CreditsData,"
		+ " not carry a second copy of the names."
	)
	# And the lookup must actually answer for a real shipped asset.
	var answered := 0
	for asset in _cat_names().keys():
		if CreditsData.credit_for_asset(str(asset)) != "":
			answered += 1
	assert_gt(answered, 0, "CreditsData.credit_for_asset answered for none of the shipped cats")

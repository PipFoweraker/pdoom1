extends GutTest
## Tests for upgrades system

var state: GameState

func before_each():
	state = GameState.new("test-seed")

func test_initial_state_has_no_upgrades():
	assert_eq(state.purchased_upgrades.size(), 0, "Should start with no upgrades")

func test_can_purchase_upgrade():
	state.money = 300000.0
	GameUpgrades.purchase_upgrade("upgrade_computer", state)
	assert_true(state.has_upgrade("upgrade_computer"), "Should have purchased upgrade")
	assert_eq(state.purchased_upgrades.size(), 1, "Should have 1 upgrade")

func test_cannot_purchase_same_upgrade_twice():
	state.money = 300000.0
	GameUpgrades.purchase_upgrade("upgrade_computer", state)
	var before_size = state.purchased_upgrades.size()
	GameUpgrades.purchase_upgrade("upgrade_computer", state)
	assert_eq(state.purchased_upgrades.size(), before_size, "Should not purchase same upgrade twice")

func test_to_dict_includes_upgrades():
	state.money = 300000.0
	GameUpgrades.purchase_upgrade("upgrade_computer", state)
	var dict = state.to_dict()
	assert_true(dict.has("purchased_upgrades"), "State dict should include purchased_upgrades")
	assert_eq(dict["purchased_upgrades"].size(), 1, "Should have 1 upgrade in dict")

func test_game_upgrades_has_correct_structure():
	var upgrades = GameUpgrades.get_all_upgrades()
	assert_gt(upgrades.size(), 0, "Should have at least one upgrade")

	for upgrade in upgrades:
		assert_true(upgrade.has("id"), "Upgrade should have id")
		assert_true(upgrade.has("name"), "Upgrade should have name")
		assert_true(upgrade.has("description"), "Upgrade should have description")
		assert_true(upgrade.has("cost"), "Upgrade should have cost")
		assert_true(upgrade.has("effect_key"), "Upgrade should have effect_key")

func test_upgrade_ids_are_unique():
	var upgrades = GameUpgrades.get_all_upgrades()
	var ids = []
	for upgrade in upgrades:
		var id = upgrade["id"]
		assert_false(ids.has(id), "Upgrade ID should be unique: " + id)
		ids.append(id)

func test_comfy_chairs_and_accounting_software_are_flavor_only():
	# #970: both upgrades charged real money for claimed effects with zero backing code
	# (no low-funds staff-attrition system; no cash-flow-tracking / board-oversight system).
	# STOP SELLING: re-priced to 0 and relabelled as flavor-only pending a design ruling.
	var comfy = GameUpgrades.get_upgrade_by_id("comfy_chairs")
	assert_eq(int(comfy.get("cost", -1)), 0, "comfy_chairs should be free (no mechanical effect)")
	assert_string_contains(String(comfy.get("description", "")), "970", "description should point at the tracking issue")

	var accounting = GameUpgrades.get_upgrade_by_id("accounting_software")
	assert_eq(int(accounting.get("cost", -1)), 0, "accounting_software should be free (no mechanical effect)")
	assert_string_contains(String(accounting.get("description", "")), "970", "description should point at the tracking issue")

func test_secure_cloud_purchase_succeeds_and_is_recorded():
	# The purchase surface itself (money -> has_upgrade) for a WIRED upgrade; the mechanical
	# effect (frontier-growth dampening) is covered by test_doom_system.gd.
	state.money = 200000.0
	var result = GameUpgrades.purchase_upgrade("secure_cloud", state)
	assert_true(result.get("success", false), "secure_cloud purchase should succeed")
	assert_true(state.has_upgrade("secure_cloud"), "secure_cloud should be recorded as purchased")

extends GutTest
## Tests for upgrades system

var state: GameState

func before_each():
	state = GameState.new("test-seed")

func test_initial_state_has_no_upgrades():
	assert_eq(state.purchased_upgrades.size(), 0, "Should start with no upgrades")

func test_can_purchase_upgrade():
	state.money = 1000.0
	state.purchase_upgrade("upgrade_computers")
	assert_true(state.has_upgrade("upgrade_computers"), "Should have purchased upgrade")
	assert_eq(state.purchased_upgrades.size(), 1, "Should have 1 upgrade")

func test_cannot_purchase_same_upgrade_twice():
	state.money = 1000.0
	state.purchase_upgrade("upgrade_computers")
	var before_size = state.purchased_upgrades.size()
	state.purchase_upgrade("upgrade_computers")
	assert_eq(state.purchased_upgrades.size(), before_size, "Should not purchase same upgrade twice")

func test_to_dict_includes_upgrades():
	state.purchase_upgrade("upgrade_computers")
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

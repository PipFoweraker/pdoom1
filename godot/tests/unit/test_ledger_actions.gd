extends GutTest
## BL-1: player-facing Liability Ledger trades (via GameActions.execute_action) +
## the BL-2 deterministic exposure trigger. Engine-level; UI is exercised by the boot check.

func _fresh_state(seed_str: String = "bl1-test") -> GameState:
	var s = GameState.new(seed_str)
	s.money = 200000
	s.action_points = 5
	return s

func test_take_loan_pays_out_and_adds_bill():
	var s = _fresh_state()
	var before = s.money
	GameActions.execute_action("take_loan", s)
	assert_eq(s.money, before + 50000, "loan pays out immediately")
	assert_eq(s.ledger.entries.size(), 1, "loan adds one ledger entry")
	assert_gt(s.ledger.outstanding(Ledger.Side.PAYABLE), 0.0, "loan creates a payable liability")

func test_funding_strings_bills_governance():
	var s = _fresh_state()
	var before = s.money
	GameActions.execute_action("funding_strings", s)
	assert_eq(s.money, before + 40000, "funding pays out")
	assert_eq(s.ledger.entries[0].currency, "governance", "strings bill in governance")

func test_desperation_lever_plants_secret_without_printed_doom():
	# ADR-0015: no action writes doom. The lever's catch-up benefit is now a
	# safety_absorption reprieve (Balance doom.streams.action_desperation_absorb,
	# priced 0 in v1); the SECRET compounding liability (the real teeth) is unchanged.
	var s = _fresh_state()
	var before_doom = s.doom
	var before_absorb = s.safety_absorption
	GameActions.execute_action("desperation_lever", s)
	assert_eq(s.doom, before_doom, "no printed doom delta (ADR-0015)")
	assert_almost_eq(s.safety_absorption,
		before_absorb + Balance.num("doom.streams.action_desperation_absorb", 0.0), 0.0001,
		"the catch-up benefit is a Balance-priced absorption reprieve")
	assert_eq(s.ledger.secret_entries().size(), 1, "desperation plants a SECRET liability")

func test_staff_rider_grants_ap_and_rider():
	var s = _fresh_state()
	var before_ap = s.action_points
	GameActions.execute_action("staff_rider", s)
	assert_eq(s.action_points, before_ap + 2, "contractor grants +2 AP now")
	assert_eq(s.ledger.entries.size(), 1, "staff rider adds a ledger entry")

func test_exposure_fires_and_chains():
	var s = _fresh_state()
	GameActions.execute_action("desperation_lever", s)
	assert_eq(s.ledger.secret_entries().size(), 1, "one secret before exposure")
	var before_entries = s.ledger.entries.size()
	var exposed = s.ledger.check_exposures(s, 1.0)  # chance 1.0 -> deterministic expose
	assert_eq(exposed.size(), 1, "the secret entry is exposed")
	assert_false(exposed[0].secret, "the exposed entry is no longer secret")
	assert_gt(s.ledger.entries.size(), before_entries, "exposure offers a blackmail entry (chain continues)")
	var has_blackmail := false
	for e in s.ledger.entries:
		if e.source.begins_with("blackmail:"):
			has_blackmail = true
	assert_true(has_blackmail, "exposure creates a blackmail entry (itself a new secret liability)")

func test_soonest_fuse_is_nearest_bill():
	var s = _fresh_state()
	GameActions.execute_action("take_loan", s)          # loan fuse (Balance)
	GameActions.execute_action("desperation_lever", s)  # desperation fuse (Balance) -- the nearer bill
	# Assert against the Balance-driven desperation fuse (L1 re-denominated fuses to the month
	# cadence, ADR-0009); the invariant is that soonest_fuse returns the NEARER of the two.
	var nearer_fuse := Balance.inum("ledger.desperation_payroll.fuse_turns", 33)
	assert_eq(s.ledger.soonest_fuse(), nearer_fuse, "soonest fuse is the nearest upcoming bill")

func test_trade_stays_seed_deterministic():
	# WS-0 invariant: same seed + same trade -> identical ledger outcome.
	var a = _fresh_state("det-seed")
	GameActions.execute_action("desperation_lever", a)
	var b = _fresh_state("det-seed")
	GameActions.execute_action("desperation_lever", b)
	assert_eq(a.ledger.entries[0].principal, b.ledger.entries[0].principal,
		"desperation severity (rng-drawn) is identical for identical seeds")

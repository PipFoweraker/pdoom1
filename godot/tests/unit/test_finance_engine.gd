extends GutTest
## L5 (#616, ADR-0013): the cost-of-debt pricing engine + financing instruments.
## Covers pricing determinism + input-sensitivity, availability gating, standing-offer
## generation with optionality/expiry, offer minting with quoted terms, the #566
## billing regression (capped default, reconciled magnitudes), the "pay the bill"
## early-repayment interaction, and save-safe (0.001-grid) computed interest.

const NONPROFIT := "nonprofit"

func _ctx(overrides: Dictionary = {}) -> Dictionary:
	var base := {
		"org_type": NONPROFIT,
		"safety_rep": 50.0, "finance_rep": 50.0,
		"hype": 0.0, "leverage": 0.0, "turn": 0,
	}
	for k in overrides:
		base[k] = overrides[k]
	return base

func _rng(seed_str: String = "l5-test") -> RandomNumberGenerator:
	var r := RandomNumberGenerator.new()
	r.seed = seed_str.hash()
	return r

var _created: Array = []

func _fresh_state(seed_str: String = "l5-test") -> GameState:
	var s := GameState.new(seed_str)
	s.money = 300000
	s.action_points = 6
	_created.append(s)
	return s

func after_each() -> void:
	# GameState is a Node that spawns doom_system/risk_system Nodes -- free them so the
	# fast gate doesn't accumulate orphans (mirrors the L1 sweep's cleanup).
	for s in _created:
		if not is_instance_valid(s):
			continue
		if s.doom_system != null and is_instance_valid(s.doom_system):
			s.doom_system.free()
		if ("risk_system" in s) and s.risk_system != null and is_instance_valid(s.risk_system):
			s.risk_system.free()
		s.free()
	_created.clear()

# ---- Pricing engine: determinism + the ADR-0013 thesis (inputs move cost) ----

func test_price_is_deterministic() -> void:
	var a := FinanceEngine.price("bank_loan", _ctx())
	var b := FinanceEngine.price("bank_loan", _ctx())
	assert_eq(a["interest_rate"], b["interest_rate"], "same context -> same rate")
	assert_eq(a["fuse_ticks"], b["fuse_ticks"], "same context -> same term")

func test_higher_reputation_cheapens_debt() -> void:
	var lo := FinanceEngine.price("bank_loan", _ctx({"finance_rep": 10.0}))
	var hi := FinanceEngine.price("bank_loan", _ctx({"finance_rep": 90.0}))
	assert_lt(float(hi["interest_rate"]), float(lo["interest_rate"]),
		"better finance reputation prices debt cheaper (ADR-0010 typed rep)")

func test_higher_leverage_raises_rate() -> void:
	var lo := FinanceEngine.price("bank_loan", _ctx({"leverage": 0.0}))
	var hi := FinanceEngine.price("bank_loan", _ctx({"leverage": 2.5}))
	assert_gt(float(hi["interest_rate"]), float(lo["interest_rate"]),
		"more existing leverage raises the cost of the next loan")

func test_org_type_moves_cost() -> void:
	var np := FinanceEngine.price("bank_loan", _ctx({"org_type": "nonprofit"}))
	var fp := FinanceEngine.price("bank_loan", _ctx({"org_type": "for_profit"}))
	assert_lt(float(fp["interest_rate"]), float(np["interest_rate"]),
		"for-profit borrows cheaper than nonprofit (org type is the biggest input)")

func test_philanthropy_is_a_gift_not_debt() -> void:
	var q := FinanceEngine.price("philanthropy", _ctx({"safety_rep": 60.0}))
	assert_eq(float(q["interest_rate"]), 0.0, "philanthropy (counterparty factor 0) carries no interest")

func test_bank_loan_baseline_matches_calibration() -> void:
	# Continuity guard: at default context the engine's bank loan reproduces the calibrated
	# ledger.loan shape (~77-tick fuse, month-scale, ~0.008/tick) so financing does not
	# regress the L1 medians. Exact rate flexes with rep relief; the FUSE must stay months.
	var q := FinanceEngine.price("bank_loan", _ctx())
	assert_gt(int(q["fuse_ticks"]), 60, "bank loan fuse is month-scale, not day-scale (respects calibration)")
	assert_lt(int(q["fuse_ticks"]), 100, "bank loan fuse near the calibrated ~77 ticks")

# ---- Availability gating (org type / typed rep / hype) ----

func test_vc_equity_requires_forprofit_and_hype() -> void:
	assert_false(FinanceEngine.is_available("vc_equity", _ctx({"org_type": "nonprofit", "hype": 50.0, "finance_rep": 80.0})),
		"VC equity is closed to nonprofits")
	assert_false(FinanceEngine.is_available("vc_equity", _ctx({"org_type": "for_profit", "hype": 0.0, "finance_rep": 80.0})),
		"VC equity needs hype")
	assert_true(FinanceEngine.is_available("vc_equity", _ctx({"org_type": "for_profit", "hype": 40.0, "finance_rep": 80.0})),
		"for-profit + hype + rep opens the VC round")

func test_philanthropy_gated_on_safety_rep() -> void:
	assert_false(FinanceEngine.is_available("philanthropy", _ctx({"safety_rep": 10.0})), "low safety-rep, no philanthropy")
	assert_true(FinanceEngine.is_available("philanthropy", _ctx({"safety_rep": 45.0})), "safety-rep opens philanthropy")

func test_desperation_always_available() -> void:
	assert_true(FinanceEngine.is_available("desperation", _ctx({"safety_rep": 0.0, "finance_rep": 0.0})),
		"the desperation lever is always on the table (last resort)")

# ---- Offer generation: optionality, better-standing-better-menu, expiry ----

func test_generate_offers_menu_size_and_liveness() -> void:
	var offers := FinanceEngine.generate_offers(_ctx({"finance_rep": 80.0, "safety_rep": 80.0}), "compute", _rng(), 3)
	assert_between(offers.size(), 1, 3, "a raise yields a small concurrent menu")
	for o in offers:
		assert_true(FinanceEngine.offer_live(o, 0), "fresh offers are live")
		assert_false(FinanceEngine.offer_live(o, int(o["expiry_turn"]) + 1), "offers expire after their TTL (ADR-0012)")

func test_better_standing_gives_at_least_as_many_offers() -> void:
	var low := FinanceEngine.generate_offers(_ctx({"finance_rep": 20.0, "safety_rep": 20.0}), "x", _rng("a"), 3)
	var high := FinanceEngine.generate_offers(_ctx({"finance_rep": 80.0, "safety_rep": 80.0}), "x", _rng("a"), 3)
	assert_true(high.size() >= low.size(), "better reputation yields a menu at least as rich")

func test_offer_generation_is_seed_deterministic() -> void:
	var a := FinanceEngine.generate_offers(_ctx({"finance_rep": 70.0}), "x", _rng("same"), 3)
	var b := FinanceEngine.generate_offers(_ctx({"finance_rep": 70.0}), "x", _rng("same"), 3)
	assert_eq(a.size(), b.size(), "same seed -> same menu size")
	if a.size() > 0:
		assert_eq(float(a[0]["principal"]), float(b[0]["principal"]), "same seed -> same drawn principals")

func test_low_reputation_menu_is_desperation_heavy() -> void:
	var offers := FinanceEngine.generate_offers(_ctx({"finance_rep": 8.0, "safety_rep": 8.0}), "x", _rng(), 3)
	var ids: Array = []
	for o in offers:
		ids.append(o["instrument_id"])
	assert_true("desperation" in ids, "with almost no standing, only the desperation lever answers")

# ---- Acceptance: cash now, ledger entry carries the QUOTED terms ----

func test_accept_loan_offer_pays_cash_and_mints_quoted_entry() -> void:
	var s := _fresh_state()
	var ctx := FinanceEngine.context_from_state(s)
	var offers := FinanceEngine.generate_offers(ctx, "runway", s.rng, 3)
	var loan_offer: Dictionary = {}
	for o in offers:
		if String(o["factory"]) == "loan":
			loan_offer = o
			break
	if loan_offer.is_empty():
		# Force a loan offer deterministically if the menu did not surface one.
		loan_offer = {"offer_id": "bank_loan#1", "instrument_id": "bank_loan", "name": "Bank term loan",
			"counterparty": "bank", "factory": "loan", "purpose": "runway", "principal": 50000.0,
			"repayment": 60000.0, "term_months": 3.5, "fuse_ticks": 77, "interest_rate": 0.007,
			"non_cash": {}, "expiry_turn": 44}
	var before := s.money
	var res := FinanceEngine.accept_offer(loan_offer, s)
	assert_true(res["success"], "accepting a live loan offer succeeds")
	assert_eq(s.money, before + float(loan_offer["principal"]), "cash lands immediately")
	var e = s.ledger.entries.back()
	assert_eq(e.currency, "money", "a loan mints a money payable")
	assert_eq(e.interest, float(loan_offer["interest_rate"]), "the entry carries the QUOTED rate (menu is honest)")
	assert_eq(e.principal, float(loan_offer["repayment"]), "the entry bills the quoted repayment")

func test_expired_offer_cannot_be_accepted() -> void:
	var s := _fresh_state()
	s.turn = 100
	var stale := {"offer_id": "x", "instrument_id": "bank_loan", "name": "L", "counterparty": "bank",
		"factory": "loan", "purpose": "x", "principal": 40000.0, "repayment": 48000.0,
		"term_months": 3.5, "fuse_ticks": 77, "interest_rate": 0.007, "non_cash": {}, "expiry_turn": 44}
	var res := FinanceEngine.accept_offer(stale, s)
	assert_false(res["success"], "a lapsed standing offer mints nothing (ADR-0012 evaporation)")

func test_equity_round_mints_noncash_riders_not_debt() -> void:
	var s := _fresh_state()
	var offer := {"offer_id": "vc#1", "instrument_id": "vc_equity", "name": "VC round", "counterparty": "vc",
		"factory": "equity", "purpose": "scale", "principal": 250000.0, "repayment": 250000.0,
		"term_months": 0.0, "fuse_ticks": 0, "interest_rate": 0.0,
		"non_cash": {"equity_dilution": 0.12, "board_seat": true}, "expiry_turn": 44}
	var before := s.money
	var res := FinanceEngine.accept_offer(offer, s)
	assert_true(res["success"], "equity round accepts")
	assert_eq(s.money, before + 250000.0, "equity delivers cash")
	var currencies: Array = []
	for e in s.ledger.entries:
		currencies.append(e.currency)
	assert_true("equity" in currencies, "dilution is a recorded rider")
	assert_true("board_seat" in currencies, "board seat is a recorded rider (DQ-7 stub)")
	# Non-cash riders are inert: ticking should never bill them (huge fuse).
	var billed := s.ledger.tick_and_bill(s)
	for b in billed:
		assert_false(b.currency in ["equity", "board_seat", "agenda"], "non-cash riders never bill")

# ---- #566 regression: capped default + reconciled magnitudes ----

func test_566_large_default_is_capped_not_a_guillotine() -> void:
	var s := _fresh_state()
	s.money = 50000.0
	s.reputation = 50.0
	var doom_before := s.doom
	# A large balloon the debtor cannot cover (the #566 shape: money zeroes, shortfall huge).
	s.ledger.add(Ledger.Entry.new("loan", "money", 500000.0, 0, 0.0))
	s.ledger.tick_and_bill(s)
	assert_eq(s.money, 0.0, "the bill drains available cash to zero")
	var rep_drop := 50.0 - s.reputation
	var doom_rise := s.doom - doom_before
	assert_lte(rep_drop, Balance.num("ledger.max_rep_per_bill", 10.0) + 0.001,
		"#566: reputation loss is capped per bill (was an uncapped 50->7.5 crash)")
	assert_lte(doom_rise, Balance.num("ledger.max_doom_per_bill", 10.0) + 0.001,
		"#566: doom conversion is capped per tick (no one-click guillotine)")

func test_566_default_note_reconciles_magnitudes() -> void:
	var s := _fresh_state()
	s.money = 50000.0
	s.ledger.add(Ledger.Entry.new("loan", "money", 500000.0, 0, 0.0))
	s.ledger.tick_and_bill(s)
	var note := {}
	for c in s.cause_log:
		if String(c.get("kind", "")) == "ledger_default":
			note = c.get("effects", {})
	assert_false(note.is_empty(), "a default logs a ledger_default note")
	assert_eq(float(note["principal_billed"]), 500000.0, "note states the full bill (#566 reconciliation)")
	assert_eq(float(note["paid_from_cash"]), 50000.0, "note states cash applied")
	# billed == paid_from_cash + shortfall (the magnitudes now reconcile).
	assert_eq(float(note["principal_billed"]), float(note["paid_from_cash"]) + float(note["money_shortfall"]),
		"billed = paid_from_cash + shortfall (the #566 'magnitudes do not reconcile' fix)")

# ---- "Pay the bill" early repayment (#566 UX ask) ----

func test_pay_entry_settles_a_money_bill_early() -> void:
	var s := _fresh_state()
	s.money = 100000.0
	s.ledger.add(Ledger.Entry.new("loan", "money", 60000.0, 40, 0.008))
	var res := s.ledger.pay_soonest_payable(s)
	assert_true(res["success"], "an affordable bill can be settled early")
	assert_eq(s.money, 40000.0, "settling debits the principal from cash")
	assert_eq(s.ledger.outstanding(Ledger.Side.PAYABLE), 0.0, "the retired bill no longer looms")
	# A settled entry never bills.
	var billed := s.ledger.tick_and_bill(s)
	assert_eq(billed.size(), 0, "a pre-paid bill does not bill")

func test_pay_entry_refuses_when_unaffordable() -> void:
	var s := _fresh_state()
	s.money = 1000.0
	s.ledger.add(Ledger.Entry.new("loan", "money", 60000.0, 40, 0.008))
	var res := s.ledger.pay_soonest_payable(s)
	assert_false(res["success"], "cannot settle a bill you cannot afford")
	assert_eq(s.money, 1000.0, "an unaffordable settle leaves cash untouched")

# ---- Save-safe computed interest (calibration open-Q #2) ----

func test_computed_rate_is_on_the_save_safe_grid() -> void:
	# Every computed rate must be a 0.001-grid value (probe-verified to round-trip through
	# the full-precision JSON save path), else a minted entry drifts 1 ulp on load.
	for rep in [0.0, 17.0, 33.0, 51.0, 88.0, 100.0]:
		for lev in [0.0, 1.3, 2.7]:
			var q := FinanceEngine.price("bank_loan", _ctx({"finance_rep": rep, "leverage": lev}))
			var r := float(q["interest_rate"])
			assert_eq(r, snappedf(r, 0.001), "rate %f is on the 0.001 save-safe grid" % r)

func test_minted_entry_survives_json_roundtrip() -> void:
	# The real save path: JSON.stringify(..., "\t", true, true) -> parse -> from_dict.
	var s := _fresh_state()
	var offer := {"offer_id": "bank_loan#1", "instrument_id": "bank_loan", "name": "Bank term loan",
		"counterparty": "bank", "factory": "loan", "purpose": "x", "principal": 55000.0,
		"repayment": 66000.0, "term_months": 3.5, "fuse_ticks": 77, "interest_rate": 0.007,
		"non_cash": {}, "expiry_turn": 44}
	FinanceEngine.accept_offer(offer, s)
	var dict := s.ledger.to_dict()
	var text := JSON.stringify(dict, "\t", true, true)
	var parsed = JSON.parse_string(text)
	var restored := Ledger.new()
	restored.from_dict(parsed)
	assert_eq(restored.entries.size(), s.ledger.entries.size(), "entries survive the round trip")
	var orig = s.ledger.entries.back()
	var back = restored.entries.back()
	assert_eq(back.interest, orig.interest, "computed interest survives save/load exactly")
	assert_eq(back.principal, orig.principal, "principal survives save/load exactly")

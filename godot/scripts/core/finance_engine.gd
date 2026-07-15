class_name FinanceEngine
extends RefCounted
## The cost-of-debt pricing engine + financing instruments (ADR-0013, lane L5/#616).
##
## ONE pricing function for all liabilities (loans, funding-with-strings, equity,
## philanthropy, the desperation lever). Cost is a function of, at Pip's weights:
##   - org type       (MAJOR — set at char/org creation; DQ-4)
##   - counterparty   (MAJOR — who you owe changes what it costs; ADR-0007)
##   - typed reputation (safety-rep prices grants; finance-rep prices debt; ADR-0010)
##   - hype           (scoped to the raise's purpose)
##   - current leverage (MINOR direct — outstanding payables vs a scale)
## Coefficients are data-driven (Balance "financing.*"); this file is the mechanism.
##
## OPTIONALITY (Pip's authorization: "give the player some optionality in what they
## choose out of what they're offered"): generate_offers() mints 2-3 concurrent
## STANDING offers with varied terms and an expiry (ADR-0012 — expiry mints no ledger
## entry, the offer simply evaporates). Better standing => better menus. A raise is a
## campaign with lead time (ADR-0009): seek -> offers stand for N turns -> accept at
## plan speed.
##
## BOUNDARY (L5 lane): entries carry money-side TERMS. Doom conversion belongs to the
## doom-streams lane — this engine never touches doom_system nor how a ledger bill
## converts to doom. The desperation lever's immediate doom SUPPRESSION reuses the
## existing add_resources path (unchanged), same as the pre-L5 desperation_lever action.
##
## Stateless: pure static utility (never instantiated), mirroring GameActions.

const DEFAULT_ORG := "nonprofit"

# --- Balance surface accessors (all fall back to the shipped defaults) --------

static func _cfg_num(key: String, fallback: float) -> float:
	return Balance.num("financing." + key, fallback)

static func ticks_per_month() -> float:
	return _cfg_num("ticks_per_month", 22.0)

static func offer_ttl_turns() -> int:
	return Balance.inum("financing.offer_ttl_turns", 44)

static func instruments() -> Dictionary:
	return Balance.table("financing.instruments")

static func instrument_ids() -> Array:
	# Deterministic order (defaults.json insertion order preserved by Godot's JSON).
	return instruments().keys()

static func instrument_def(id: String) -> Dictionary:
	var all := instruments()
	return all.get(id, {}) if all.get(id, {}) is Dictionary else {}

# --- Pricing context ----------------------------------------------------------

## Assemble the pricing inputs from game state. Typed reputation and org type do not
## yet exist as first-class GameState fields (owed by ADR-0010 typed-attention and the
## DQ-4 char/org-creation lanes); until then this reads them if present and falls back
## to the scalar reputation / a nonprofit default. Duck-typed so lightweight test
## doubles work. `turn` seeds standing-offer expiry.
static func context_from_state(state) -> Dictionary:
	var scalar_rep: float = float(state.reputation) if _has(state, "reputation") else 50.0
	var leverage_scale: float = _cfg_num("leverage_scale", 120000.0)
	var outstanding := 0.0
	if _has(state, "ledger") and state.ledger != null:
		outstanding = state.ledger.outstanding(Ledger.Side.PAYABLE)
	return {
		"org_type": _read(state, "org_type", DEFAULT_ORG),
		"safety_rep": float(_read(state, "safety_reputation", scalar_rep)),
		"finance_rep": float(_read(state, "finance_reputation", scalar_rep)),
		"hype": float(_read(state, "hype", 0.0)),
		"leverage": (outstanding / leverage_scale) if leverage_scale > 0.0 else 0.0,
		"turn": int(_read(state, "turn", 0)),
	}

static func _rep_for_channel(ctx: Dictionary, channel: String) -> float:
	return float(ctx.get("safety_rep", 50.0)) if channel == "safety" else float(ctx.get("finance_rep", 50.0))

# --- Availability + pricing (the engine's thesis) -----------------------------

## Is this instrument on the menu for the current context? (org type gate, typed-rep
## floor, hype floor, leverage ceiling.) Data-driven per instrument.availability.
static func is_available(id: String, ctx: Dictionary) -> bool:
	var def := instrument_def(id)
	if def.is_empty():
		return false
	var av: Dictionary = def.get("availability", {}) if def.get("availability", {}) is Dictionary else {}
	var org_types: Array = av.get("org_types", []) if av.get("org_types", []) is Array else []
	if not org_types.is_empty() and not (String(ctx.get("org_type", DEFAULT_ORG)) in org_types):
		return false
	var rep := _rep_for_channel(ctx, String(def.get("rep_channel", "finance")))
	if rep < float(av.get("min_rep", 0.0)):
		return false
	if float(ctx.get("hype", 0.0)) < float(av.get("min_hype", 0.0)):
		return false
	if float(ctx.get("leverage", 0.0)) > float(av.get("max_leverage", 1e9)):
		return false
	return true

## THE cost-of-debt function. Returns quoted terms for one instrument in one context:
##   {available, instrument_id, name, counterparty, factory, rep_channel,
##    principal_min, principal_max, principal_multiplier,
##    term_months, fuse_ticks, interest_rate, non_cash}
## Interest is snapped to 0.001 (save-safe) and clamped to [rate_floor, rate_ceiling].
## A zero base_rate (equity, philanthropy) stays exactly 0 — not debt.
static func price(id: String, ctx: Dictionary) -> Dictionary:
	var def := instrument_def(id)
	if def.is_empty():
		return {"available": false, "instrument_id": id}
	var base_rate := float(def.get("base_rate", 0.0))
	var org := String(ctx.get("org_type", DEFAULT_ORG))
	var cp := String(def.get("counterparty", "bank"))
	var org_factor := Balance.num("financing.org_factors." + org, 1.0)
	var cp_factor := Balance.num("financing.counterparty_factors." + cp, 1.0)
	var rep := _rep_for_channel(ctx, String(def.get("rep_channel", "finance")))
	var leverage := float(ctx.get("leverage", 0.0))

	var rate := 0.0
	if base_rate > 0.0:
		# rate = base x org x counterparty, penalised by leverage, relieved by reputation.
		rate = base_rate * org_factor * cp_factor
		rate += leverage * _cfg_num("leverage_rate_penalty", 0.004)
		rate -= (rep / 100.0) * _cfg_num("rep_rate_relief", 0.004)
		rate = clampf(rate, _cfg_num("rate_floor", 0.002), _cfg_num("rate_ceiling", 0.05))
		# Save-safe quantisation: 0.001 grid round-trips through the full-precision JSON
		# save path exactly (calibration open-Q #2), so a minted entry survives save/load.
		rate = snappedf(rate, 0.001)

	var fuse_ticks := int(round(float(def.get("term_months", 0.0)) * ticks_per_month()))
	return {
		"available": is_available(id, ctx),
		"instrument_id": id,
		"name": String(def.get("name", id)),
		"counterparty": cp,
		"factory": String(def.get("factory", "loan")),
		"rep_channel": String(def.get("rep_channel", "finance")),
		"principal_min": float(def.get("principal_min", 0.0)),
		"principal_max": float(def.get("principal_max", 0.0)),
		"principal_multiplier": float(def.get("principal_multiplier", 1.0)),
		"term_months": float(def.get("term_months", 0.0)),
		"fuse_ticks": fuse_ticks,
		"interest_rate": rate,
		"non_cash": (def.get("non_cash", {}) as Dictionary).duplicate(true),
	}

# --- Offer generation (standing offers with optionality) ----------------------

static func _tier_count(ctx: Dictionary) -> int:
	# Best of the two typed reputations selects the menu size (ADR-0013 better-standing
	# => better-menus). thresholds/counts are paired arrays on the Balance surface.
	var best := maxf(float(ctx.get("safety_rep", 0.0)), float(ctx.get("finance_rep", 0.0)))
	var thresholds: Array = Balance.table("financing.offer_tiers").get("thresholds", [0])
	var counts: Array = Balance.table("financing.offer_tiers").get("counts", [2])
	var count := int(counts[0]) if counts.size() > 0 else 2
	for i in range(thresholds.size()):
		if best >= float(thresholds[i]) and i < counts.size():
			count = int(counts[i])
	return count

## Generate a menu of 2-3 concurrent STANDING offers (ADR-0012) for a purpose-tagged
## raise. Deterministic in `rng` (WS-0). Principals are drawn per-offer from each
## instrument's range so the menu has genuine spread; philanthropy appears only on a
## scarce dice roll (ADR-0013: philanthropy is starved by design). Each offer carries
## an expiry_turn (ctx.turn + offer_ttl); a lapsed offer evaporates, minting nothing.
static func generate_offers(ctx: Dictionary, purpose: String, rng: RandomNumberGenerator, max_count: int = 3) -> Array:
	var offers: Array = []
	var cap := mini(_tier_count(ctx), max_count)
	var expiry := int(ctx.get("turn", 0)) + offer_ttl_turns()
	var idx := 0
	for id in instrument_ids():
		if offers.size() >= cap:
			break
		if not is_available(id, ctx):
			continue
		var def := instrument_def(id)
		# Scarcity gate: philanthropy (and any instrument with appearance_chance) rolls to appear.
		if def.has("appearance_chance") and rng.randf() > float(def["appearance_chance"]):
			continue
		var quote := price(id, ctx)
		var pmin := float(quote["principal_min"])
		var pmax := float(quote["principal_max"])
		var principal := pmin
		if pmax > pmin:
			principal = roundf(pmin + rng.randf() * (pmax - pmin))
		var repay := roundf(principal * float(quote["principal_multiplier"]))
		idx += 1
		offers.append({
			"offer_id": "%s#%d" % [id, idx],
			"instrument_id": id,
			"name": quote["name"],
			"counterparty": quote["counterparty"],
			"factory": quote["factory"],
			"purpose": purpose,
			"principal": principal,          # cash the player receives now
			"repayment": repay,              # what the ledger entry bills (loans/strings)
			"term_months": quote["term_months"],
			"fuse_ticks": quote["fuse_ticks"],
			"interest_rate": quote["interest_rate"],
			"non_cash": quote["non_cash"],
			"expiry_turn": expiry,
		})
	return offers

## Is a standing offer still open at `turn`? (ADR-0012 standing-offer expiry.)
static func offer_live(offer: Dictionary, turn: int) -> bool:
	return turn <= int(offer.get("expiry_turn", 0))

# --- Acceptance: apply cash now, mint the future bill with the QUOTED terms --------

## Accept a standing offer: apply the immediate benefit (cash now / doom suppressed now)
## and mint the Ledger entry(ies) carrying the offer's OWN quoted terms (not the default
## factory magnitudes — the menu is honest: what you saw is what you owe). Non-cash terms
## (equity dilution, board seat, agenda strings) mint ledger riders (ADR-0011). Returns
## {success, message, money_delta, doom_delta, entries:[Entry]}.
static func accept_offer(offer: Dictionary, state) -> Dictionary:
	var result := {"success": false, "message": "", "money_delta": 0.0, "doom_delta": 0.0, "entries": []}
	if offer.is_empty():
		result["message"] = "No offer to accept"
		return result
	var turn := int(_read(state, "turn", 0))
	if not offer_live(offer, turn):
		result["message"] = "Offer has expired"
		return result

	var factory := String(offer.get("factory", "loan"))
	var principal := float(offer.get("principal", 0.0))
	var repayment := float(offer.get("repayment", principal))
	var fuse := int(offer.get("fuse_ticks", 0))
	var rate := float(offer.get("interest_rate", 0.0))
	var cp := String(offer.get("counterparty", ""))
	var non_cash: Dictionary = offer.get("non_cash", {}) if offer.get("non_cash", {}) is Dictionary else {}
	var entries: Array = []

	match factory:
		"loan":
			state.add_resources({"money": principal})
			result["money_delta"] = principal
			entries.append(Ledger.Entry.new("loan:" + cp, "money", repayment, fuse, rate, false, Ledger.Side.PAYABLE, cp))
			result["message"] = "Accepted %s: +$%d now; ~$%d bills in %d ticks" % [offer.get("name", "loan"), int(principal), int(repayment), fuse]
		"funding_strings":
			state.add_resources({"money": principal})
			result["money_delta"] = principal
			# The agenda-narrowing cost bills in governance (reuses the calibrated strings machinery).
			entries.append(Ledger.Entry.new("funding_strings:" + cp, "governance", repayment, fuse, rate, false, Ledger.Side.PAYABLE, cp))
			result["message"] = "Accepted %s: +$%d now; agenda strings bill later in governance" % [offer.get("name", "grant"), int(principal)]
		"equity":
			state.add_resources({"money": principal})
			result["money_delta"] = principal
			# Equity is not debt: no repayment entry. The dilution + board seat are priced-regret
			# riders (ADR-0013 single dilution scalar v1; board seat = options-curtailed stub, DQ-7).
			result["message"] = "Accepted %s: +$%d now (equity round — no repayment, but dilution + board terms apply)" % [offer.get("name", "equity"), int(principal)]
		"philanthropy":
			state.add_resources({"money": principal})
			result["money_delta"] = principal
			result["message"] = "Accepted %s: +$%d, a gift — no repayment (scarce)" % [offer.get("name", "gift"), int(principal)]
		"desperation_payroll":
			# Immediate doom SUPPRESSION (unchanged pre-L5 path — boundary: no doom_system touch),
			# plants a secret, compounding governance liability with the QUOTED terms.
			var suppress := _cfg_num("desperation_doom_suppression", 10.0)
			state.add_resources({"doom": -suppress})
			result["doom_delta"] = -suppress
			var sev := Balance.num("ledger.desperation_payroll.severity_base", 1200.0)
			if _has(state, "rng") and state.rng != null:
				sev += state.rng.randf() * Balance.num("ledger.desperation_payroll.severity_spread", 800.0)
			entries.append(Ledger.Entry.new("payroll_coinflip", "governance", sev, fuse, rate, true))
			result["message"] = "Pulled the desperation lever: -%d doom now; a SECRET liability is planted" % int(suppress)
		_:
			result["message"] = "Unknown instrument factory: %s" % factory
			return result

	# Non-cash riders (ADR-0011: agenda riders are ledger entries). Inert standing terms —
	# a huge fuse + zero interest keep them visible in the post-mortem trail without ever
	# billing; the governance/equity lanes (DQ-7, late-game equity) wire their consequences.
	if bool(non_cash.get("board_seat", false)):
		entries.append(_standing_rider("board_seat:" + cp, "board_seat", 1.0, cp))
	if non_cash.has("equity_dilution"):
		var bps := roundf(float(non_cash["equity_dilution"]) * 10000.0)  # basis points, integer
		entries.append(_standing_rider("equity_dilution:" + cp, "equity", bps, cp))
	if bool(non_cash.get("agenda_narrowing", false)) and factory != "funding_strings":
		entries.append(_standing_rider("agenda_narrowing:" + cp, "agenda", 1.0, cp))

	if _has(state, "ledger") and state.ledger != null:
		for e in entries:
			state.ledger.add(e)
	result["entries"] = entries
	result["success"] = true
	return result

## A non-cash standing term as an inert ledger rider (never bills: 10^9 fuse, 0 interest).
static func _standing_rider(source: String, currency: String, principal: float, counterparty: String) -> Object:
	return Ledger.Entry.new(source, currency, principal, 1000000000, 0.0, false, Ledger.Side.PAYABLE, counterparty)

# --- Duck-typing helpers (lightweight test doubles carry only some fields) -----

static func _has(obj, field: String) -> bool:
	return field in obj

static func _read(obj, field: String, fallback):
	if field in obj:
		var v = obj.get(field)
		return v if v != null else fallback
	return fallback

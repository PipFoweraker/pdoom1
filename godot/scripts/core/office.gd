class_name Office
extends RefCounted
## The office economy: tier-0 start state, the 3-option first-lease decision, the hire
## cap, and the monthly rent charge (#791; #811 item 1; OFFICE_ECONOMY_PROPOSAL.md).
##
## SHAPE (Pip's ruling 2026-07-27): "I want 3 offices to choose from and different size
## floorplans to go with that. Let's make the internals of each office upgradeable over
## time -- moving will have its own costs, but for now lets leave players locked in with
## their choices, mechanically, just architect extensibility."
##
## THE FORCE (#791: "force a little spend"): the force is NOT a scripted prompt. Tier 0
## hard-caps you at start.hire_cap hires; the third person has nowhere to sit. Growing
## REQUIRES signing, so the spend is forced by the cap, not by a modal.
##
## RENT RAIL (proposal Q2, decided here): rent rides the PAYROLL rail -- a direct cash
## deduction at the MONTH BOUNDARY (month_controller._open_plan_month), not a recurring
## ledger payable. Two reasons: (1) Ledger.Entry is one-shot and compounding; rent must be
## PREDICTABLE and non-compounding (#791: "predictable AP/cash sink"), and minting a fresh
## payable every month is new plumbing that buys nothing; (2) an unpayable rent should read
## as the same death as an unpayable payroll (funding_starvation), which the payroll rail
## already attributes. The one-shot, punitive charges -- break fee, downsize penalty -- are
## exactly what the ledger IS good at, and they stay reserved for the future move
## instrument. Split rule: recurring+predictable -> payroll rail; one-shot+punitive ->
## ledger.
##
## SIM/RENDER BOUNDARY (ADR-0018): floorplan.* in offices.json is RENDER-ONLY. Nothing in
## this file (or any sim path) reads floorplan -- the sim reads hire_cap. floorplan() is
## exposed purely so office_floor.gd can size itself off the signed lease later.
##
## Stateless: pure static utility (never instantiated), mirroring GameActions/FinanceEngine.

const Definitions = preload("res://scripts/data/definition_loader.gd")

const OFFICES_PATH := "res://data/office/offices.json"

static var _data: Dictionary = {}


static func reload_definitions() -> void:
	"""Drop the cache so the next access re-reads the JSON (tests/tuning)."""
	_data.clear()


static func data() -> Dictionary:
	if _data.is_empty():
		_data = Definitions.load_object(OFFICES_PATH, "Office")
	return _data


## The tier-0 bedroom/basement definition every run starts in.
static func start_office() -> Dictionary:
	var d: Dictionary = data().get("start", {})
	return d if d is Dictionary else {}


## The THREE lease options presented at the first-lease decision. Always all three --
## this menu is deliberately NOT reputation-gated the way FinanceEngine.generate_offers'
## menu size is: Pip ruled "3 offices to choose from", so the choice is fixed-width and
## the interesting variation lives in the terms, not in how many doors you can see.
static func lease_options() -> Array:
	var opts = data().get("lease_options", [])
	return opts if opts is Array else []


static func option_by_id(option_id: String) -> Dictionary:
	for o in lease_options():
		if o is Dictionary and String(o.get("id", "")) == option_id:
			return o
	var start := start_office()
	if String(start.get("id", "")) == option_id:
		return start
	return {}


## RENDER-ONLY (ADR-0018). The sim must never call this.
static func floorplan(option_id: String) -> Dictionary:
	var def := option_by_id(option_id)
	var fp = def.get("floorplan", {})
	return fp.duplicate(true) if fp is Dictionary else {}


# --- The hire cap (the thing that makes the lease decision real) ---------------

## Desks available under the CURRENT office. Reads GameState.office_hire_cap, which is
## set from the signed lease (or the tier-0 start value at reset).
static func hire_cap(state) -> int:
	if state != null and ("office_hire_cap" in state):
		return int(state.office_hire_cap)
	return int(start_office().get("hire_cap", 2))


## Employed headcount that occupies a desk. Managers sit at desks too.
static func occupied_desks(state) -> int:
	if state == null:
		return 0
	return int(state.get_total_staff()) if state.has_method("get_total_staff") else 0


static func has_desk_space(state) -> bool:
	return occupied_desks(state) < hire_cap(state)


## The crisp refusal (OFFICE_ECONOMY_PROPOSAL 2b, "hard cap, crisp refusal"). One
## sentence, no numbers the player cannot already see on the office panel.
static func no_desk_message(state) -> String:
	var tier := 0
	if state != null and ("office_tier" in state):
		tier = int(state.office_tier)
	if tier <= 0:
		return "No desk. You are running this out of a bedroom -- sign a lease."
	return "No desk. This office is full."


# --- Rent (payroll rail, month boundary) --------------------------------------

## Charge one month of rent. Called from month_controller._open_plan_month. Returns the
## amount charged (0.0 when no lease is signed -- an unsigned run is economically
## IDENTICAL to pre-#791 play, which is what keeps the blast radius small).
static func charge_rent(state) -> float:
	if state == null or not ("office_rent_per_month" in state):
		return 0.0
	var rent := float(state.office_rent_per_month)
	if rent <= 0.0:
		return 0.0
	var before := float(state.money)
	state.add_resources({"money": -rent})
	# EE-8 attribution: only note the charge that actually pushed the org under. Recording
	# only -- nothing reads cause_log during play.
	if before >= 0.0 and float(state.money) < 0.0 and state.has_method("note_cause"):
		state.note_cause("office_rent", String(state.office_id), {"money": -rent})
	return rent


static func rent_message(state, charged: float) -> String:
	return "Rent fell due: %s (%s)." % [
		GameConfig.format_money(charged), String(state.office_name)]


# --- Signing (the lock-in) ----------------------------------------------------

## Write a signed lease onto GameState. Cash (deposit + fitout) is charged by the CALLER
## (FinanceEngine._accept_lease) so the affordability check and the charge live together.
## LOCK-IN: office_locked flips true and no shipped code path ever flips it back. The
## future move instrument clears it -- that is the whole extension seam.
static func apply_lease(state, option: Dictionary) -> void:
	state.office_id = String(option.get("id", ""))
	state.office_name = String(option.get("name", ""))
	state.office_tier = int(option.get("tier", 1))
	state.office_hire_cap = int(option.get("hire_cap", 0))
	state.office_rent_per_month = float(option.get("rent_per_month", 0.0))
	state.office_locked = true
	# office_upgrades is ADDITIVE and stays untouched by signing -- see apply_upgrade.


## Reset GameState's office fields to the tier-0 start. Called from GameState.reset().
static func apply_start(state) -> void:
	var s := start_office()
	state.office_id = String(s.get("id", "bedroom"))
	state.office_name = String(s.get("name", "Bedroom / basement"))
	state.office_tier = int(s.get("tier", 0))
	state.office_hire_cap = int(s.get("hire_cap", 2))
	state.office_rent_per_month = float(s.get("rent_per_month", 0.0))
	state.office_locked = false
	state.office_upgrades.clear()


# --- Upgrade hook (the architected extensibility; nothing ships through it yet) ---

## THE SEAM. Pip: "let's make the internals of each office upgradeable over time... just
## architect extensibility." offices.json ships `"upgrades": []`, so this ALWAYS refuses
## today and says so honestly -- it fabricates no effect and prints no number. When the
## interior-decorating lane (W-3b) authors upgrade defs, they land in that array and this
## function is the ONE place that has to learn to apply them.
##
## Contract for whoever fills it in: an upgrade is ADDITIVE (appended to
## state.office_upgrades, never replacing the lease), it must survive save/load as a plain
## String id, and it must NOT change office_tier -- tier is the lease, upgrades are the
## fitout.
static func upgrade_defs() -> Array:
	var u = data().get("upgrades", [])
	return u if u is Array else []


static func apply_upgrade(state, upgrade_id: String) -> Dictionary:
	var def := {}
	for u in upgrade_defs():
		if u is Dictionary and String(u.get("id", "")) == upgrade_id:
			def = u
			break
	if def.is_empty():
		return {"success": false, "message": "No such office upgrade: %s" % upgrade_id}
	if state.office_upgrades.has(upgrade_id):
		return {"success": false, "message": "Already fitted: %s" % String(def.get("name", upgrade_id))}
	state.office_upgrades.append(upgrade_id)
	return {"success": true, "message": "Fitted %s." % String(def.get("name", upgrade_id))}

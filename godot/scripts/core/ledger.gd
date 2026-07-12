extends RefCounted
class_name Ledger
## The Liability Ledger (ADR-0003): every mitigation is a loan.
##
## A two-sided ledger of trades that pay now and bill later. There is NO new
## player-facing currency (ADR-0003 "no parallel economy"): every entry reads and
## writes only existing resources — money, reputation, governance, action_points,
## doom. Compounding interest on payables is the mortality guarantee (ADR-0002):
## an un-serviced debt grows without bound until a bill it cannot pay ends the run,
## and the death is attributable to specific entries.
##
## First-wave content (ADR-0003): loans, funding-with-strings, desperation levers
## (payroll coinflip -> secret governance rot), staff riders. Receivables/blackmail
## chains are modelled at entry level; their full event/UI wiring is parked (see PR).

enum Side { PAYABLE, RECEIVABLE }

## A single liability or asset. Heterogeneous by design (ADR-0003 boundary
## condition): fuses, currencies and interest profiles vary so the game does not
## degenerate into an inevitability queue.
class Entry:
	var id: String = ""
	var source: String = ""            # the trade that created it ("loan", "payroll_coinflip", ...)
	var currency: String = "money"     # money | reputation | governance | doom | action_points
	var principal: float = 0.0         # current magnitude; grows by `interest` each turn while unsettled
	var fuse: int = 0                  # turns until it bills (0 = due now)
	var interest: float = 0.0          # per-turn compounding rate (0.0 = does not grow)
	var secret: bool = false           # can be exposed by rivals/scheduled causes (ADR-0003)
	var side: int = Side.PAYABLE
	var counterparty: String = ""      # per-actor, for receivables (NO global influence stat, ADR-0003)
	var settled: bool = false          # billed and closed; kept for the post-mortem trail

	func _init(p_source: String, p_currency: String, p_principal: float, p_fuse: int, p_interest: float = 0.0, p_secret: bool = false, p_side: int = Side.PAYABLE, p_counterparty: String = "") -> void:
		source = p_source
		currency = p_currency
		principal = p_principal
		fuse = p_fuse
		interest = p_interest
		secret = p_secret
		side = p_side
		counterparty = p_counterparty

	func to_dict() -> Dictionary:
		return {
			"id": id,
			"source": source, "currency": currency, "principal": principal,
			"fuse": fuse, "interest": interest, "secret": secret,
			"side": side, "counterparty": counterparty, "settled": settled,
		}

	## L7 (#618): rebuild an Entry from serialized data. Numeric casts are explicit
	## because JSON round-trips every number as float.
	static func from_dict(d: Dictionary) -> Entry:
		var e := Entry.new(
			String(d.get("source", "")),
			String(d.get("currency", "money")),
			float(d.get("principal", 0.0)),
			int(d.get("fuse", 0)),
			float(d.get("interest", 0.0)),
			bool(d.get("secret", false)),
			int(d.get("side", Side.PAYABLE)),
			String(d.get("counterparty", "")))
		e.id = String(d.get("id", ""))
		e.settled = bool(d.get("settled", false))
		return e

# How hard an unpayable money bill converts to doom — the "teeth" that guarantee
# mortality when a debtor cannot cover a balloon payment. Live values come from the
# Balance surface ("ledger.*", L9 #621); these consts are the call-site fallbacks
# (and keep external references/tests compiling).
const DOOM_PER_UNPAID_1000: float = 3.5
const REP_PER_UNPAID_1000: float = 2.0

var entries: Array = []            # Array[Entry] — all entries, incl. settled (post-mortem trail)
var death_attribution: Array = []  # populated when a bill drives the killing blow

func add(entry: Entry) -> void:
	entries.append(entry)

# ---- First-wave content factories (ADR-0003). Callers apply the *immediate*
# benefit (money now / doom suppressed now) and add the returned future bill. ----

## Money now, balloon repayment later with compounding interest. The classic
## "bill for turn 2" — deep runs are heroic because of what funded them.
## Negative term/rate = "use the Balance surface" (defaults can't call autoloads).
static func loan(amount: float, term: int = -1, rate: float = -1.0) -> Entry:
	if term < 0:
		term = Balance.inum("ledger.loan.fuse_turns", 4)
	if rate < 0.0:
		rate = Balance.num("ledger.loan.interest_rate", 0.25)
	return Entry.new("loan", "money", amount * Balance.num("ledger.loan.principal_multiplier", 1.2), term, rate)

## Money now, an obligation that later bills in reputation/governance (strings).
static func funding_with_strings(amount: float) -> Entry:
	return Entry.new("funding_strings", "governance",
		amount * Balance.num("ledger.funding_strings.principal_multiplier", 0.15),
		Balance.inum("ledger.funding_strings.fuse_turns", 6),
		Balance.num("ledger.funding_strings.interest_rate", 0.05))

## Desperation lever = catch-up (ADR-0003/0008). Buys doom-suppression NOW but
## plants a SECRET, compounding governance liability (payroll coinflip -> rot ->
## exposure -> blackmail chain). Coinflip severity is drawn from state.rng so the
## run stays deterministic (WS-0).
static func desperation_payroll(rng: RandomNumberGenerator) -> Entry:
	var severity := Balance.num("ledger.desperation_payroll.severity_base", 8000.0) \
		+ rng.randf() * Balance.num("ledger.desperation_payroll.severity_spread", 6000.0)
	return Entry.new("payroll_coinflip", "governance", severity,
		Balance.inum("ledger.desperation_payroll.fuse_turns", 3),
		Balance.num("ledger.desperation_payroll.interest_rate", 0.35), true)

## A hire is AP-leverage with a small liability rider (ADR-0008). On departure a
## caller can flip it to `secret` (a disgruntled ex-researcher).
static func staff_rider(name: String) -> Entry:
	return Entry.new("staff:" + name, "governance",
		Balance.num("ledger.staff_rider.principal", 1200.0),
		Balance.inum("ledger.staff_rider.fuse_turns", 8),
		Balance.num("ledger.staff_rider.interest_rate", 0.02))

# ---- Turn processing: the mortality guarantee lives here ----

## Called once per turn (after WS-C scheduled causes). Compounds interest on live
## payables, advances fuses, and bills anything due. Unbounded compounding is the
## mortality guarantee (ADR-0002).
func tick_and_bill(state) -> void:
	for e in entries:
		if e.settled or e.side != Side.PAYABLE:
			continue
		if e.interest > 0.0:
			e.principal *= (1.0 + e.interest)   # unbounded growth -> no immortal runs
		if e.fuse > 0:
			e.fuse -= 1
			continue
		_bill(e, state)
		e.settled = true

## Bill a due entry in its own currency. A money bill the debtor cannot cover
## converts the shortfall into doom + reputation damage and records the entry as a
## cause of death — this is the escalation that makes debt lethal and traceable.
func _bill(e: Entry, state) -> void:
	match e.currency:
		"money":
			state.money -= e.principal
			if state.money < 0.0:
				var shortfall: float = -state.money
				state.money = 0.0
				var doom_hit: float = shortfall / 1000.0 * Balance.num("ledger.doom_per_unpaid_1000", DOOM_PER_UNPAID_1000)
				var rep_amount: float = shortfall / 1000.0 * Balance.num("ledger.rep_per_unpaid_1000", REP_PER_UNPAID_1000)
				var rep_hit: float = minf(state.reputation, rep_amount)
				state.doom += doom_hit
				state.reputation = max(0.0, state.reputation - rep_amount)
				_attribute(e, shortfall, state)
				_note(state, "ledger_default", e.source,
					{"money_shortfall": shortfall, "doom": doom_hit, "reputation": -rep_hit})
		"reputation":
			var rep_hit: float = minf(state.reputation, e.principal)
			state.reputation = max(0.0, state.reputation - e.principal)
			_note(state, "ledger_rep_bill", e.source, {"reputation": -rep_hit})
		"governance":
			# Governance is a resource the ledger reads/writes (ADR-0003). Its
			# player-facing design is parked (workshop #2). Below zero, corroded
			# governance leaks into doom — the bribery/blackmail pressure surface.
			state.governance -= e.principal
			if state.governance < 0.0:
				var deficit: float = -state.governance
				state.governance = 0.0
				var doom_hit: float = deficit / 1000.0 * Balance.num("ledger.doom_per_unpaid_1000", DOOM_PER_UNPAID_1000)
				state.doom += doom_hit
				_attribute(e, deficit, state)
				_note(state, "ledger_governance_deficit", e.source,
					{"governance_deficit": deficit, "doom": doom_hit})
		"doom":
			state.doom += e.principal
			_attribute(e, e.principal, state)
			_note(state, "ledger_doom_bill", e.source, {"doom": e.principal})
		"action_points":
			state.action_points = max(0, state.action_points - int(e.principal))

func _attribute(e: Entry, magnitude: float, state = null) -> void:
	# EE-8: turn-stamped so the death chain is orderable in the run record.
	var turn: int = int(state.turn) if state != null and "turn" in state else -1
	death_attribution.append({"source": e.source, "currency": e.currency, "magnitude": magnitude, "turn": turn})

## EE-8: forward a contributing cause to the GameState attribution trail (duck-typed
## so ledger unit tests with lightweight state doubles keep working).
func _note(state, kind: String, source: String, effects: Dictionary) -> void:
	if state != null and state.has_method("note_cause"):
		state.note_cause(kind, source, effects)

## Expose a secret entry (rival action / scheduled cause). Converts it to
## reputation + governance damage, and — the chain continues — may offer a
## blackmail entry (a new, worse liability). Blackmail is content, not a system.
func expose(entry: Entry, state, offer_blackmail: bool = true) -> void:
	if not entry.secret or entry.settled:
		return
	entry.secret = false
	var rep_amount: float = entry.principal / 1000.0 * Balance.num("ledger.expose.rep_per_1000", 4.0)
	var gov_hit: float = entry.principal * Balance.num("ledger.expose.governance_multiplier", 0.5)
	var rep_hit: float = minf(state.reputation, rep_amount)
	state.reputation = max(0.0, state.reputation - rep_amount)
	state.governance -= gov_hit
	_note(state, "ledger_exposure", entry.source,
		{"reputation": -rep_hit, "governance": -gov_hit})
	if offer_blackmail:
		# A worse liability that keeps the debtor quiet: shorter fuse, steeper rate.
		add(Entry.new("blackmail:" + entry.source, "money",
			entry.principal * Balance.num("ledger.blackmail.principal_multiplier", 1.5),
			Balance.inum("ledger.blackmail.fuse_turns", 2),
			Balance.num("ledger.blackmail.interest_rate", 0.5), true))

# ---- Read helpers ----

func outstanding(side: int = Side.PAYABLE) -> float:
	var total := 0.0
	for e in entries:
		if not e.settled and e.side == side:
			total += e.principal
	return total

func secret_entries() -> Array:
	return entries.filter(func(e): return e.secret and not e.settled)

## Soonest fuse among live payables (turns until the next bill), -1 if none.
func soonest_fuse() -> int:
	var soonest := -1
	for e in entries:
		if not e.settled and e.side == Side.PAYABLE:
			if soonest < 0 or e.fuse < soonest:
				soonest = e.fuse
	return soonest

## BL-2: minimal DETERMINISTIC exposure of secret liabilities. Each unsettled secret
## entry has `chance` (drawn from state.rng, so replay stays deterministic per WS-0) of
## being exposed this turn -> reputation/governance damage + a blackmail offer. Exact
## trigger design (rival-driven vs scheduled cause, probability) is PARKED (workshop #2).
## Returns the entries exposed on this call.
func check_exposures(state, chance: float) -> Array:
	var exposed := []
	for e in secret_entries():
		if state.rng.randf() < chance:
			expose(e, state)
			exposed.append(e)
	return exposed

func to_dict() -> Dictionary:
	# Summary keys (outstanding_*, entry_count, ...) are consumed by the UI; "entries"
	# carries the full per-entry state so a mid-game save/load round-trips (L7, #618).
	var entry_dicts := []
	for e in entries:
		entry_dicts.append(e.to_dict())
	return {
		"outstanding_payable": outstanding(Side.PAYABLE),
		"outstanding_receivable": outstanding(Side.RECEIVABLE),
		"entry_count": entries.size(),
		"secret_count": secret_entries().size(),
		"soonest_fuse": soonest_fuse(),
		"death_attribution": death_attribution.duplicate(true),
		"entries": entry_dicts,
	}


## L7 (#618): restore the full ledger — every entry (incl. settled post-mortem trail)
## and the death-attribution list. Summary keys are derived on read, so ignored here.
func from_dict(data: Dictionary) -> void:
	entries.clear()
	for ed in data.get("entries", []):
		if ed is Dictionary:
			entries.append(Entry.from_dict(ed))
	death_attribution.clear()
	for a in data.get("death_attribution", []):
		if a is Dictionary:
			death_attribution.append(a.duplicate(true))

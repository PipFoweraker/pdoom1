class_name MonthPlan
extends RefCounted
## The month plan layer (L1 / ADR-0009). The plan turn is a MONTH; the day-turn is the
## resolution tick beneath it (GameState.turn keeps counting workday ticks -- this object
## layers the monthly decision cadence on top without re-grainng the sim substrate).
##
## Holds the founder currency **Attention** (workshop#3 addendum #5): ~N decisions/month,
## admin as painful overhead. Staff spend a SEPARATE per-person `actions` currency -- there
## is no global pool here. **T2 (2026-07-28): the legacy AP pool is DELETED** -- Attention
## is now the ONLY founder currency; action/event cost dicts carry an `attention` key and
## nothing anywhere reads `action_points` (ADR-0011 amendment (a), ruled 2026-07-27 11:37).
##
## Attention splits three ways within a month:
##   available  -- free to fund queued strategic actions (plan speed)
##   reserved   -- explicitly set aside at plan time for response windows (instant speed);
##                this is ADR-0009's CRISP reserve -- the gamble that makes windows interlock
##   spent      -- already committed to queued strategic work
## Unspent reserve EVAPORATES at month end (ADR-0009 S4 -- no banking, ever): begin_month()
## resets the pools, discarding any carry.
##
## FOUNDER-HOUR TYPING (2-way, T3-rung FLOOR -- ADR-0011 point 2 / amendment (c)).
## Every Attention spend is one of two HOUR TYPES:
##   PLANNING  -- the planner mind: deciding direction, queuing strategic work, approvals.
##                Does NOT require being in the building (this is the #980 seam: away at a
##                conference you lose OPERATOR PRESENCE, not PLANNER MIND).
##   OPERATING -- presence work: face-time, firefighting, response windows, running the
##                hiring loop, being in the room.
## The typed pools are ADDITIVE ACCOUNTING over an AUTHORITATIVE SCALAR -- the same shape
## N2 used for typed reputation (ruled 2026-07-27). `attention_total`/`attention_spent`
## stay the authoritative aggregate; `hours_total`/`hours_spent` type it. Every legacy
## caller that only knows the aggregate keeps working unchanged.
##
## OVERFLOW IS ASYMMETRIC and that asymmetry is the whole design point:
##   OPERATING may overflow into PLANNING hours -- a crisis eats the time you meant to
##     spend thinking. (ADR-0011: "reserve -- instant-speed firefighting".)
##   PLANNING may NOT overflow into OPERATING -- you cannot retroactively have been in the
##     room. Running out of planner hours BLOCKS more strategic queuing this month.
##
## FOUNDER-HOUR KINDS (4-way, ADR-0011 point 2 / Ballot 4 ruled 2026-07-27, REVIEW-BY
## 2026-08-31). The four kinds SUBDIVIDE the two families; they do not replace them:
##   doors     -- stakeholder face-time, being in rooms         (family: OPERATING)
##   approvals -- hires, direction rulings, queuing strategy    (family: PLANNING)
##   audits    -- skip-level ground-truthing of reported work   (family: OPERATING)
##   reserve   -- instant-speed firefighting (the crisp reserve)(family: OPERATING)
## Third storey of the SAME additive-accounting tower: an authoritative scalar
## (attention_total/spent), typed by a 2-way family layer (hours_total/hours_spent), labelled
## by a 4-way kind layer (kind_spent). Each storey is additive over the one below, so the
## 2026-08-31 review can DELETE the kind layer without touching the gate logic if 4-way did
## not earn its complexity.
##
## DELIBERATE S-CUT SCOPE: kinds ACCOUNT, families GATE. There are no per-kind monthly
## budgets -- admissibility is decided entirely by the family pools and the asymmetric
## overflow rule above. Per-kind caps would be four more balance dials to sweep before a
## review that may collapse the split back to 2-way; that is a post-review call.
##
## Why audits and doors are OPERATING: both are presence by definition (you cannot
## skip-level ground-truth a researcher's real progress from a hotel room, and a door you
## are not standing in is not open). This is what makes #980 fall out for free -- travel
## drains the OPERATING family, so it kills doors and audits and leaves approvals (next
## month's direction) decidable from the road.
##
## Strategic actions carry DURATIONS (ADR-0009 S5 -- nothing strategic resolves instantly);
## queued items land on a future resolution tick. This is the seam L2 workstreams extend.

# --- Founder hour types (2-way floor) ---
const HOUR_PLANNING := "planning"
const HOUR_OPERATING := "operating"
const HOUR_TYPES := [HOUR_PLANNING, HOUR_OPERATING]

# --- Founder hour kinds (4-way, Ballot 4) -- labels over the families above ---
const KIND_DOORS := "doors"
const KIND_APPROVALS := "approvals"
const KIND_AUDITS := "audits"
const KIND_RESERVE := "reserve"
const HOUR_KINDS := [KIND_DOORS, KIND_APPROVALS, KIND_AUDITS, KIND_RESERVE]

## Which family each kind bills. THE one place the 4-way maps onto the 2-way.
const KIND_FAMILY := {
	KIND_DOORS: HOUR_OPERATING,
	KIND_APPROVALS: HOUR_PLANNING,
	KIND_AUDITS: HOUR_OPERATING,
	KIND_RESERVE: HOUR_OPERATING,
}

## What an un-subdivided family spend is LABELLED as. Presence-by-default is face-time;
## planner-mind-by-default is a direction ruling. Callers/data that mean something finer
## name the kind explicitly.
const FAMILY_DEFAULT_KIND := {
	HOUR_PLANNING: KIND_APPROVALS,
	HOUR_OPERATING: KIND_DOORS,
}

# --- Attention accounting (all integer Attention units) ---
var attention_total: int = 0        # granted this plan-month (Balance attention.per_month)
var attention_spent: int = 0        # committed to queued strategic actions
var attention_reserved: int = 0     # explicitly held for response windows (the crisp reserve)
var reserve_used: int = 0           # reserve consumed by HANDLE-from-reserve this month

# Typed founder hours (additive over the authoritative scalar above). hours_total sums to
# attention_total by construction in begin_month; hours_spent sums to attention_spent for
# every spend that goes through spend_attention/queue_strategic/the window payers.
var hours_total: Dictionary = {HOUR_PLANNING: 0, HOUR_OPERATING: 0}
var hours_spent: Dictionary = {HOUR_PLANNING: 0, HOUR_OPERATING: 0}

# 4-way kind labels over hours_spent. Invariants pinned by test_founder_hours.gd:
#   kind_spent[doors] + [approvals] + [audits] == attention_spent
#   kind_spent[reserve] == reserve_used   (the reserve is accounted separately -- see
#   set_reserve's T2 design note, which this lane deliberately did NOT overrule)
var kind_spent: Dictionary = {KIND_DOORS: 0, KIND_APPROVALS: 0, KIND_AUDITS: 0, KIND_RESERVE: 0}

# Which plan-month this is (0-based from run start) -- stamps the replay artifact (ADR-0016).
var month_ordinal: int = 0

# Queued strategic actions with durations. Each entry:
#   {action_id: String, attention_cost: int, resolves_on_turn: int, queued_on_turn: int}
# Nothing resolves instantly -- the MonthController lands these when state.turn reaches
# resolves_on_turn (mid-period or at month review).
var queued_strategic: Array = []


func begin_month(attention_per_month: int, ordinal: int, planning_share: float = -1.0) -> void:
	"""Open a fresh plan phase. Crisp reserve evaporation happens HERE by construction:
	the pools reset, so last month's unspent reserve is simply gone (ADR-0009 S4).
	`planning_share` splits the grant into PLANNING vs OPERATING hours; < 0 reads the
	Balance dial (`attention.planning_share`). The remainder after integer division goes
	to OPERATING, so an odd grant never silently loses an hour."""
	attention_total = attention_per_month
	attention_spent = 0
	attention_reserved = 0
	reserve_used = 0
	month_ordinal = ordinal
	var share: float = planning_share
	if share < 0.0:
		share = Balance.num("attention.planning_share", 0.6)
	share = clampf(share, 0.0, 1.0)
	var planning: int = int(floor(float(attention_per_month) * share))
	planning = clampi(planning, 0, attention_per_month)
	hours_total = {HOUR_PLANNING: planning, HOUR_OPERATING: attention_per_month - planning}
	hours_spent = {HOUR_PLANNING: 0, HOUR_OPERATING: 0}
	kind_spent = {KIND_DOORS: 0, KIND_APPROVALS: 0, KIND_AUDITS: 0, KIND_RESERVE: 0}
	# In-flight strategic actions persist across the boundary (they have durations);
	# resolved ones are pruned by the controller, not here.


# --- Typed founder hours (2-way families gate; 4-way kinds label) ---

static func family_of(hour_type: String) -> String:
	"""Resolve ANY hour token -- a 4-way kind OR a 2-way family -- to the family that gates
	it. Unknown tokens resolve to OPERATING (presence is the safe assumption: it is the
	family that can overflow, so a mis-typed spend is never silently granted planner mind).
	Every public entry point funnels through here, which is why callers written against the
	2-way API keep working verbatim after the 4-way landed."""
	if KIND_FAMILY.has(hour_type):
		return String(KIND_FAMILY[hour_type])
	if hour_type == HOUR_PLANNING:
		return HOUR_PLANNING
	return HOUR_OPERATING


static func kind_of(hour_type: String) -> String:
	"""Resolve ANY hour token to the 4-way kind it is BOOKED as. A family name maps to its
	default kind (see FAMILY_DEFAULT_KIND); an unknown token follows family_of to OPERATING
	and so books as doors."""
	if KIND_FAMILY.has(hour_type):
		return hour_type
	return String(FAMILY_DEFAULT_KIND.get(family_of(hour_type), KIND_DOORS))


func hours_available(hour_type: String) -> int:
	"""Hours of `hour_type`'s FAMILY not yet spent. Accepts a kind or a family. This is the
	TYPE gate only -- a spend must also fit inside the authoritative aggregate available()
	(which nets out the reserve). There is deliberately no per-KIND budget (see header)."""
	var fam: String = family_of(hour_type)
	return int(hours_total.get(fam, 0)) - int(hours_spent.get(fam, 0))


func kind_spend(kind: String) -> int:
	"""Hours booked against one 4-way kind this month. Read-only accounting/readout surface."""
	return int(kind_spent.get(kind, 0))


func can_spend_hours(cost: int, hour_type: String) -> bool:
	"""Would a `cost`-hour spend of `hour_type` be admissible right now? Applies both the
	aggregate gate and the asymmetric-overflow type rule."""
	if cost <= 0:
		return true
	if available() < cost:
		return false
	if hours_available(hour_type) >= cost:
		return true
	# OPERATING may eat PLANNING hours (a crisis costs you thinking time). PLANNING may not
	# eat OPERATING hours -- you cannot retroactively have been in the room.
	return family_of(hour_type) == HOUR_OPERATING


func _debit_hours(cost: int, hour_type: String) -> void:
	"""Record `cost` hours against the typed pools, spilling into the other FAMILY per the
	asymmetric-overflow rule, and label the whole spend with its 4-way KIND. Callers gate
	with can_spend_hours() first; this only books.
	Note the kind is booked whole even when the family spills: an audit hour that overflowed
	into planning capacity is still an audit -- the spill records WHERE the time came from,
	the kind records WHAT it was spent on."""
	if cost <= 0:
		return
	var fam: String = family_of(hour_type)
	kind_spent[kind_of(hour_type)] = int(kind_spent.get(kind_of(hour_type), 0)) + cost
	var from_type: int = mini(cost, maxi(0, hours_available(fam)))
	hours_spent[fam] = int(hours_spent.get(fam, 0)) + from_type
	var spill: int = cost - from_type
	if spill <= 0:
		return
	var other: String = HOUR_PLANNING if fam == HOUR_OPERATING else HOUR_OPERATING
	hours_spent[other] = int(hours_spent.get(other, 0)) + spill


func available() -> int:
	"""Attention free to fund new plan-speed commitments (not spent, not reserved)."""
	return attention_total - attention_spent - attention_reserved


func reserve_remaining() -> int:
	"""Reserve still available for response windows this month."""
	return attention_reserved - reserve_used


func set_reserve(amount: int) -> bool:
	"""Explicitly hold `amount` Attention for response windows (plan-time decision).
	Can raise or lower the reserve as long as it stays within what is unspent and what
	has already been drawn from reserve (reserve_used) this month."""
	if amount < reserve_used:
		return false  # can't reserve less than already drawn from reserve
	# The new reserve must fit within total minus what's spent on strategic work.
	if amount > attention_total - attention_spent:
		return false
	# T2 DESIGN CALL: the crisp reserve is deliberately UNTYPED, and is NOT capped at the
	# operating pool. Reason: the reserve is the emergency channel, and an emergency is
	# precisely where the type wall is allowed to break -- pay_by_cannibalizing already lets
	# OPERATING overflow into PLANNING hours. Capping the pre-declared reserve at operating
	# hours would forbid at plan time exactly what the overflow rule permits at crisis time,
	# which is incoherent (and would silently truncate the implicit end-of-month reserve).
	# Consequence for the invariant: reserve_used does NOT book into hours_spent, so
	# sum(hours_spent) == attention_spent continues to hold; the reserve is accounted
	# separately by attention_reserved / reserve_used.
	attention_reserved = amount
	return true


func can_queue(attention_cost: int) -> bool:
	return available() >= attention_cost


func spend_attention(cost: int, hour_type: String = HOUR_OPERATING) -> bool:
	"""Spend `cost` Attention from the AVAILABLE (un-reserved) pool at plan speed, without
	minting a queued-strategic WIP entry. This is the primitive the hiring pipeline (and
	other duration subsystems that track their own jobs) use: the founder currency is still
	debited here, but the duration/target bookkeeping lives in the subsystem. Returns false
	(no charge) if the cost doesn't fit within available Attention OR within the hour type
	(PLANNING cannot borrow OPERATING hours -- see the header).

	DEFAULT IS OPERATING: an un-typed spend is presence work. Callers that are genuinely
	planner-mind work (queuing strategic direction) pass HOUR_PLANNING explicitly."""
	if cost <= 0:
		return true
	if not can_spend_hours(cost, hour_type):
		return false
	attention_spent += cost
	_debit_hours(cost, hour_type)
	return true


func grant_hours(amount: int, hour_type: String = HOUR_OPERATING) -> void:
	"""Add `amount` hours of ONE type to this month's budget mid-month. This is ADR-0011
	point 6 ("ops/admin staff reduce the founder-price of routine actions") -- bought
	presence, e.g. a contractor absorbing routine operating load. It is deliberately NOT a
	way for staff to top up the founder's PLANNING mind (ADR-0011 point 1: the pool illusion
	is dead; staff never add founder capacity to think). Grants evaporate at month end like
	everything else -- begin_month resets both pools."""
	if amount <= 0:
		return
	var fam: String = family_of(hour_type)
	hours_total[fam] = int(hours_total.get(fam, 0)) + amount
	attention_total += amount


func refund_attention(cost: int, hour_type: String = HOUR_OPERATING) -> void:
	"""Give back `cost` Attention (queue clear / removed card / a subsystem rolling back).
	Clamped at zero on both the aggregate and the typed pool so a mismatched refund can
	never mint Attention out of nothing."""
	if cost <= 0:
		return
	attention_spent = maxi(0, attention_spent - cost)
	var fam: String = family_of(hour_type)
	var kind: String = kind_of(hour_type)
	kind_spent[kind] = maxi(0, int(kind_spent.get(kind, 0)) - cost)
	var booked: int = int(hours_spent.get(fam, 0))
	var from_type: int = mini(cost, booked)
	hours_spent[fam] = booked - from_type
	var spill: int = cost - from_type
	if spill > 0:
		var other: String = HOUR_PLANNING if fam == HOUR_OPERATING else HOUR_OPERATING
		hours_spent[other] = maxi(0, int(hours_spent.get(other, 0)) - spill)


func queue_strategic(action_id: String, attention_cost: int, duration_ticks: int, current_turn: int) -> bool:
	"""Queue a strategic action at plan speed. Spends Attention now; the EFFECT lands
	`duration_ticks` resolution ticks later (ADR-0009 S5). duration_ticks <= 0 is coerced
	to 1 -- nothing strategic resolves on the same tick it was queued.
	Queuing strategic work is PLANNER MIND -- it bills PLANNING hours (T2 2-way floor)."""
	if not can_queue(attention_cost) or not can_spend_hours(attention_cost, HOUR_PLANNING):
		return false
	var ticks: int = max(1, duration_ticks)
	attention_spent += attention_cost
	_debit_hours(attention_cost, HOUR_PLANNING)
	queued_strategic.append({
		"action_id": action_id,
		"attention_cost": attention_cost,
		"resolves_on_turn": current_turn + ticks,
		"queued_on_turn": current_turn,
	})
	return true


func take_due_strategic(current_turn: int) -> Array:
	"""Pop and return strategic items whose duration has elapsed (resolves_on_turn <=
	current_turn). The caller applies their effects on this tick."""
	var due: Array = []
	var still_pending: Array = []
	for item in queued_strategic:
		if int(item.get("resolves_on_turn", 0)) <= current_turn:
			due.append(item)
		else:
			still_pending.append(item)
	queued_strategic = still_pending
	return due


# --- Response-window payment sources (ADR-0009 S3) ---

func pay_from_reserve(cost: int) -> bool:
	"""HANDLE from reserve -- painless, what the reserve gamble was for. Draws from the
	explicitly-held reserve pool only."""
	if reserve_remaining() < cost:
		return false
	reserve_used += cost
	# 4-way LABEL only: the reserve kind mirrors reserve_used, it does not book into
	# hours_spent. Ballot 4 names `reserve` as one of the four kinds; T2's judgment call 2
	# left the crisp reserve's ACCOUNTING deliberately untyped and un-gated (an emergency is
	# exactly where the type wall may break). Both hold at once because this storey labels
	# rather than gates -- see the PR body's reconciliation note.
	kind_spent[KIND_RESERVE] = reserve_used
	return true


func pay_by_cannibalizing(cost: int) -> Dictionary:
	"""HANDLE by cannibalizing -- pay a window out of un-reserved capacity, and if that is
	short, DELAY/KILL planned WIP to free the Attention it holds (ADR-0009 S3). Returns
	{paid: bool, cancelled: Array[String]} listing action_ids sacrificed (LIFO)."""
	var cancelled: Array = []
	var free: int = available()
	# Cancel most-recent queued strategic WIP until we can cover the cost from free Attention.
	# Cancelled cards refund PLANNING hours (that is what queue_strategic billed); the window
	# then bills OPERATING and overflows into those freed planning hours -- which IS the
	# designed pain: the crisis you handled is the strategy month you did not get.
	while free < cost and not queued_strategic.is_empty():
		var victim: Dictionary = queued_strategic.pop_back()
		refund_attention(int(victim.get("attention_cost", 0)), HOUR_PLANNING)
		cancelled.append(String(victim.get("action_id", "")))
		free = available()
	if free < cost:
		# Roll back nothing was actually spent; report failure. (attention_spent already
		# reflects the cancellations, which is correct -- cancelling WIP is a real refund.)
		return {"paid": false, "cancelled": cancelled}
	attention_spent += cost  # the window consumes this much of the freed/available capacity
	_debit_hours(cost, HOUR_OPERATING)
	return {"paid": true, "cancelled": cancelled}


# --- Serialization (L7 save/load convention) ---

func to_dict() -> Dictionary:
	return {
		"attention_total": attention_total,
		"attention_spent": attention_spent,
		"attention_reserved": attention_reserved,
		"reserve_used": reserve_used,
		"month_ordinal": month_ordinal,
		"hours_total": hours_total.duplicate(),
		"hours_spent": hours_spent.duplicate(),
		"kind_spent": kind_spent.duplicate(),
		"queued_strategic": queued_strategic.duplicate(true),
	}


func from_dict(data: Dictionary) -> void:
	attention_total = int(data.get("attention_total", 0))
	attention_spent = int(data.get("attention_spent", 0))
	attention_reserved = int(data.get("attention_reserved", 0))
	reserve_used = int(data.get("reserve_used", 0))
	month_ordinal = int(data.get("month_ordinal", 0))
	# Typed hours. A pre-T2 save has neither key: rebuild the split from the grant and book
	# everything already spent as OPERATING (the un-typed default), so an old save loads
	# into a legal, invariant-satisfying state rather than a zeroed one that would block
	# every further spend.
	var raw_total: Variant = data.get("hours_total", null)
	if raw_total is Dictionary and not (raw_total as Dictionary).is_empty():
		hours_total = {
			HOUR_PLANNING: int((raw_total as Dictionary).get(HOUR_PLANNING, 0)),
			HOUR_OPERATING: int((raw_total as Dictionary).get(HOUR_OPERATING, 0)),
		}
	else:
		var planning: int = int(floor(float(attention_total) * clampf(Balance.num("attention.planning_share", 0.6), 0.0, 1.0)))
		planning = clampi(planning, 0, attention_total)
		hours_total = {HOUR_PLANNING: planning, HOUR_OPERATING: attention_total - planning}
	var raw_spent: Variant = data.get("hours_spent", null)
	if raw_spent is Dictionary and not (raw_spent as Dictionary).is_empty():
		hours_spent = {
			HOUR_PLANNING: int((raw_spent as Dictionary).get(HOUR_PLANNING, 0)),
			HOUR_OPERATING: int((raw_spent as Dictionary).get(HOUR_OPERATING, 0)),
		}
	else:
		hours_spent = {HOUR_PLANNING: 0, HOUR_OPERATING: 0}
		kind_spent = {KIND_DOORS: 0, KIND_APPROVALS: 0, KIND_AUDITS: 0, KIND_RESERVE: 0}
		_debit_hours(attention_spent, HOUR_OPERATING)
	# 4-way kind labels. A pre-Ballot-4 save has no `kind_spent`: rebuild it by labelling
	# each family's booked hours with that family's DEFAULT kind, so the invariant
	# sum(doors, approvals, audits) == attention_spent holds on load rather than reading zero.
	var raw_kinds: Variant = data.get("kind_spent", null)
	if raw_kinds is Dictionary and not (raw_kinds as Dictionary).is_empty():
		kind_spent = {}
		for kind in HOUR_KINDS:
			kind_spent[kind] = int((raw_kinds as Dictionary).get(kind, 0))
	else:
		kind_spent = {KIND_DOORS: 0, KIND_APPROVALS: 0, KIND_AUDITS: 0, KIND_RESERVE: 0}
		kind_spent[KIND_APPROVALS] = int(hours_spent.get(HOUR_PLANNING, 0))
		kind_spent[KIND_DOORS] = maxi(0, attention_spent - int(hours_spent.get(HOUR_PLANNING, 0)))
		kind_spent[KIND_RESERVE] = reserve_used
	queued_strategic = []
	for item in data.get("queued_strategic", []):
		if item is Dictionary:
			var c: Dictionary = item.duplicate(true)
			c["attention_cost"] = int(c.get("attention_cost", 0))
			c["resolves_on_turn"] = int(c.get("resolves_on_turn", 0))
			c["queued_on_turn"] = int(c.get("queued_on_turn", 0))
			c["action_id"] = String(c.get("action_id", ""))
			queued_strategic.append(c)

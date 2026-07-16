class_name MonthPlan
extends RefCounted
## The month plan layer (L1 / ADR-0009). The plan turn is a MONTH; the day-turn is the
## resolution tick beneath it (GameState.turn keeps counting workday ticks — this object
## layers the monthly decision cadence on top without re-grainng the sim substrate).
##
## Holds the founder currency **Attention** (workshop#3 addendum #5): ~N decisions/month,
## admin as painful overhead. Staff spend a SEPARATE per-person `actions` currency — there
## is no global pool here (this is NOT the legacy AP pool; L2 deletes that and migrates cost
## dicts onto Attention/staff — L1 introduces Attention alongside, seam left clean).
##
## Attention splits three ways within a month:
##   available  — free to fund queued strategic actions (plan speed)
##   reserved   — explicitly set aside at plan time for response windows (instant speed);
##                this is ADR-0009's CRISP reserve — the gamble that makes windows interlock
##   spent      — already committed to queued strategic work
## Unspent reserve EVAPORATES at month end (ADR-0009 §4 — no banking, ever): begin_month()
## resets the pools, discarding any carry.
##
## Strategic actions carry DURATIONS (ADR-0009 §5 — nothing strategic resolves instantly);
## queued items land on a future resolution tick. This is the seam L2 workstreams extend.

# --- Attention accounting (all integer Attention units) ---
var attention_total: int = 0        # granted this plan-month (Balance attention.per_month)
var attention_spent: int = 0        # committed to queued strategic actions
var attention_reserved: int = 0     # explicitly held for response windows (the crisp reserve)
var reserve_used: int = 0           # reserve consumed by HANDLE-from-reserve this month

# Which plan-month this is (0-based from run start) — stamps the replay artifact (ADR-0016).
var month_ordinal: int = 0

# Queued strategic actions with durations. Each entry:
#   {action_id: String, attention_cost: int, resolves_on_turn: int, queued_on_turn: int}
# Nothing resolves instantly — the MonthController lands these when state.turn reaches
# resolves_on_turn (mid-period or at month review).
var queued_strategic: Array = []


func begin_month(attention_per_month: int, ordinal: int) -> void:
	"""Open a fresh plan phase. Crisp reserve evaporation happens HERE by construction:
	the pools reset, so last month's unspent reserve is simply gone (ADR-0009 §4)."""
	attention_total = attention_per_month
	attention_spent = 0
	attention_reserved = 0
	reserve_used = 0
	month_ordinal = ordinal
	# In-flight strategic actions persist across the boundary (they have durations);
	# resolved ones are pruned by the controller, not here.


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
	attention_reserved = amount
	return true


func can_queue(attention_cost: int) -> bool:
	return available() >= attention_cost


func spend_attention(cost: int) -> bool:
	"""Spend `cost` Attention from the AVAILABLE (un-reserved) pool at plan speed, without
	minting a queued-strategic WIP entry. This is the primitive the hiring pipeline (and
	other duration subsystems that track their own jobs) use: the founder currency is still
	debited here, but the duration/target bookkeeping lives in the subsystem. Returns false
	(no charge) if the cost doesn't fit within available Attention."""
	if cost <= 0:
		return true
	if available() < cost:
		return false
	attention_spent += cost
	return true


func queue_strategic(action_id: String, attention_cost: int, duration_ticks: int, current_turn: int) -> bool:
	"""Queue a strategic action at plan speed. Spends Attention now; the EFFECT lands
	`duration_ticks` resolution ticks later (ADR-0009 §5). duration_ticks <= 0 is coerced
	to 1 — nothing strategic resolves on the same tick it was queued."""
	if not can_queue(attention_cost):
		return false
	var ticks: int = max(1, duration_ticks)
	attention_spent += attention_cost
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


# --- Response-window payment sources (ADR-0009 §3) ---

func pay_from_reserve(cost: int) -> bool:
	"""HANDLE from reserve — painless, what the reserve gamble was for. Draws from the
	explicitly-held reserve pool only."""
	if reserve_remaining() < cost:
		return false
	reserve_used += cost
	return true


func pay_by_cannibalizing(cost: int) -> Dictionary:
	"""HANDLE by cannibalizing — pay a window out of un-reserved capacity, and if that is
	short, DELAY/KILL planned WIP to free the Attention it holds (ADR-0009 §3). Returns
	{paid: bool, cancelled: Array[String]} listing action_ids sacrificed (LIFO)."""
	var cancelled: Array = []
	var free: int = available()
	# Cancel most-recent queued strategic WIP until we can cover the cost from free Attention.
	while free < cost and not queued_strategic.is_empty():
		var victim: Dictionary = queued_strategic.pop_back()
		attention_spent -= int(victim.get("attention_cost", 0))
		cancelled.append(String(victim.get("action_id", "")))
		free = available()
	if free < cost:
		# Roll back nothing was actually spent; report failure. (attention_spent already
		# reflects the cancellations, which is correct — cancelling WIP is a real refund.)
		return {"paid": false, "cancelled": cancelled}
	attention_spent += cost  # the window consumes this much of the freed/available capacity
	return {"paid": true, "cancelled": cancelled}


# --- Serialization (L7 save/load convention) ---

func to_dict() -> Dictionary:
	return {
		"attention_total": attention_total,
		"attention_spent": attention_spent,
		"attention_reserved": attention_reserved,
		"reserve_used": reserve_used,
		"month_ordinal": month_ordinal,
		"queued_strategic": queued_strategic.duplicate(true),
	}


func from_dict(data: Dictionary) -> void:
	attention_total = int(data.get("attention_total", 0))
	attention_spent = int(data.get("attention_spent", 0))
	attention_reserved = int(data.get("attention_reserved", 0))
	reserve_used = int(data.get("reserve_used", 0))
	month_ordinal = int(data.get("month_ordinal", 0))
	queued_strategic = []
	for item in data.get("queued_strategic", []):
		if item is Dictionary:
			var c: Dictionary = item.duplicate(true)
			c["attention_cost"] = int(c.get("attention_cost", 0))
			c["resolves_on_turn"] = int(c.get("resolves_on_turn", 0))
			c["queued_on_turn"] = int(c.get("queued_on_turn", 0))
			c["action_id"] = String(c.get("action_id", ""))
			queued_strategic.append(c)

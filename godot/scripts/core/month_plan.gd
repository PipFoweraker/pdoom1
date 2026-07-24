class_name MonthPlan
extends RefCounted
## The month plan layer (L1 / ADR-0009). The plan turn is a MONTH; the day-turn is the
## resolution tick beneath it (GameState.turn keeps counting workday ticks -- this object
## layers the monthly decision cadence on top without re-grainng the sim substrate).
##
## Holds the founder currency **Attention** (workshop#3 addendum #5): ~N decisions/month,
## admin as painful overhead. Staff spend a SEPARATE per-person `actions` currency -- there
## is no global pool here (this is NOT the legacy AP pool; L2 deletes that and migrates cost
## dicts onto Attention/staff -- L1 introduces Attention alongside, seam left clean).
##
## Attention splits three ways within a month:
##   available  -- free to fund queued strategic actions (plan speed)
##   reserved   -- explicitly set aside at plan time for response windows (instant speed);
##                this is ADR-0009's CRISP reserve -- the gamble that makes windows interlock
##   spent      -- already committed to queued strategic work
## Unspent reserve EVAPORATES at month end (ADR-0009 S4 -- no banking, ever): begin_month()
## resets the pools, discarding any carry.
##
## Strategic actions carry DURATIONS (ADR-0009 S5 -- nothing strategic resolves instantly);
## queued items land on a future resolution tick. This is the seam L2 workstreams extend.

# --- Attention accounting (all integer Attention units) ---
var attention_total: int = 0        # granted this plan-month (Balance attention.per_month)
var attention_spent: int = 0        # DEBITED as queued cards RESOLVE (see resolve_committed)
var attention_committed: int = 0    # SPIKE (resolve-time-spend): held by queued-but-not-yet-
                                    # resolved cards; moves into attention_spent on resolution.
                                    # Pre-spike this pool did not exist -- the debit landed in
                                    # attention_spent at QUEUE time. Now queue-time only COMMITS.
var attention_reserved: int = 0     # explicitly held for response windows (the crisp reserve)
var reserve_used: int = 0           # reserve consumed by HANDLE-from-reserve this month

# Which plan-month this is (0-based from run start) -- stamps the replay artifact (ADR-0016).
var month_ordinal: int = 0

# Queued strategic actions with durations. Each entry:
#   {action_id: String, attention_cost: int, resolves_on_turn: int, queued_on_turn: int}
# Nothing resolves instantly -- the MonthController lands these when state.turn reaches
# resolves_on_turn (mid-period or at month review).
var queued_strategic: Array = []


func begin_month(attention_per_month: int, ordinal: int) -> void:
	"""Open a fresh plan phase. Crisp reserve evaporation happens HERE by construction:
	the pools reset, so last month's unspent reserve is simply gone (ADR-0009 S4)."""
	attention_total = attention_per_month
	attention_spent = 0
	attention_committed = 0
	attention_reserved = 0
	reserve_used = 0
	month_ordinal = ordinal
	# In-flight strategic actions persist across the boundary (they have durations);
	# resolved ones are pruned by the controller, not here.


func available() -> int:
	"""Attention free to fund new plan-speed commitments. SPIKE: now also nets out
	attention_committed (queued-but-unresolved cards), so the queue gate still stops the
	founder committing past the 20/month budget even though the debit no longer lands in
	attention_spent until a card resolves."""
	return attention_total - attention_spent - attention_committed - attention_reserved


func reserve_remaining() -> int:
	"""Reserve still available for response windows this month."""
	return attention_reserved - reserve_used


func set_reserve(amount: int) -> bool:
	"""Explicitly hold `amount` Attention for response windows (plan-time decision).
	Can raise or lower the reserve as long as it stays within what is unspent and what
	has already been drawn from reserve (reserve_used) this month."""
	if amount < reserve_used:
		return false  # can't reserve less than already drawn from reserve
	# The new reserve must fit within total minus what's spent AND still committed to
	# strategic work (SPIKE: committed is 0 by the time end_month sets the implicit reserve --
	# every card has resolved -- so this is unchanged for the live caller; the term keeps the
	# invariant honest if a reserve is set mid-plan).
	if amount > attention_total - attention_spent - attention_committed:
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


# --- SPIKE (resolve-time-spend): commit at queue time, DEBIT at resolution ------------------
# The design goal (Pip): Attention leaves the founder's budget as queued cards RESOLVE over the
# month, not when they are queued. Queue-time COMMITS (reserves budget so the 20/month gate
# still holds); resolution DEBITS (moves committed -> spent). Removing a card before it resolves
# RELEASES its commitment untouched -- the diversion affordance. NOTE: with the current
# batch-execute model every queued card resolves in the single end_month execute_turn, so
# committed->spent all lands at once, before day-tick playout. True mid-month diversion needs the
# per-tick resolution seam (queue_strategic/take_due_strategic) wired into the real action path;
# that is the larger L3/WS-3 change this spike assesses.

func commit_attention(cost: int) -> bool:
	"""Queue-time COMMIT: hold `cost` Attention against the budget without debiting it. Returns
	false (no hold) if it doesn't fit within available Attention."""
	if cost <= 0:
		return true
	if available() < cost:
		return false
	attention_committed += cost
	return true


func resolve_committed(cost: int) -> void:
	"""Resolution-time DEBIT: a committed card resolves -- move its hold from committed to spent.
	Clamped so a mismatched cost can never drive committed negative."""
	if cost <= 0:
		return
	attention_committed = max(0, attention_committed - cost)
	attention_spent += cost


func release_committed(cost: int) -> void:
	"""Cancel a queued-but-unresolved card: give back its commitment (nothing was debited)."""
	if cost <= 0:
		return
	attention_committed = max(0, attention_committed - cost)


func queue_strategic(action_id: String, attention_cost: int, duration_ticks: int, current_turn: int) -> bool:
	"""Queue a strategic action at plan speed. Spends Attention now; the EFFECT lands
	`duration_ticks` resolution ticks later (ADR-0009 S5). duration_ticks <= 0 is coerced
	to 1 -- nothing strategic resolves on the same tick it was queued."""
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


# --- Response-window payment sources (ADR-0009 S3) ---

func pay_from_reserve(cost: int) -> bool:
	"""HANDLE from reserve -- painless, what the reserve gamble was for. Draws from the
	explicitly-held reserve pool only."""
	if reserve_remaining() < cost:
		return false
	reserve_used += cost
	return true


func pay_by_cannibalizing(cost: int) -> Dictionary:
	"""HANDLE by cannibalizing -- pay a window out of un-reserved capacity, and if that is
	short, DELAY/KILL planned WIP to free the Attention it holds (ADR-0009 S3). Returns
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
		# reflects the cancellations, which is correct -- cancelling WIP is a real refund.)
		return {"paid": false, "cancelled": cancelled}
	attention_spent += cost  # the window consumes this much of the freed/available capacity
	return {"paid": true, "cancelled": cancelled}


# --- Serialization (L7 save/load convention) ---

func to_dict() -> Dictionary:
	return {
		"attention_total": attention_total,
		"attention_spent": attention_spent,
		"attention_committed": attention_committed,
		"attention_reserved": attention_reserved,
		"reserve_used": reserve_used,
		"month_ordinal": month_ordinal,
		"queued_strategic": queued_strategic.duplicate(true),
	}


func from_dict(data: Dictionary) -> void:
	attention_total = int(data.get("attention_total", 0))
	attention_spent = int(data.get("attention_spent", 0))
	attention_committed = int(data.get("attention_committed", 0))
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

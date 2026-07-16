extends RefCounted
class_name HiringPipeline
## The hiring pipeline (BUILD_BRIEF_HIRING_PIPELINE "Phase B") -- the fishing-line:
## source -> interview -> offer -> onboard. Every stage is an Attention-gated, DURATION
## action (ADR-0009: nothing strategic resolves instantly): the player casts effort out
## now and the reward lands later.
##
## DESIGN GUARDS honored here:
##   - Deterministic / replay-safe (WS-0, ADR-0006): every draw comes from state.rng and
##     only ever happens when a pipeline action is actually taken, or when a campaign/job/
##     un-mentored hire is actually live. With no pipeline activity the RNG stream is
##     byte-unchanged, so pre-existing replays still verify.
##   - Hidden info is TRUE-but-incomplete: interviewing REVEALS the Phase-A card (never
##     fabricates); the negotiation self-worth range is the one genuinely-hidden function.
##   - Comp is NOT hidden (Pip ruling): salary_expectation reveals at interview level 1;
##     the hidden thing is the self-worth *floor* the offer must clear (self_worth_floor).
##   - `loyalty` (dynamic) stays distinct from `loyalty_risk` (hidden predisposition).
##   - Appetites are the negotiation CURRENCY (ADR-0011): a promise to feed a hunger buys
##     the candidate down in cash and MINTS A LEDGER ENTRY (ADR-0003) -- a real future bill.
##
## Instance state lives on GameState.hiring (mirrors state.ledger / state.month_plan), is
## reset per game, and round-trips through to_dict/from_dict. Attention is spent through
## state.month_plan (the founder currency); money/reputation through the normal resources.

# --- Persistent state (serialized) ---
var next_serial: int = 0      # monotonic id source for candidates + jobs (deterministic)
# Advertise campaigns: each trickles candidates into the pool at month boundaries.
#   {months_remaining:int, per_month_min:int, per_month_max:int}
var campaigns: Array = []
# In-flight duration jobs (interview / connections / offer). Each:
#   {job_id:String, kind:String, candidate_id:String, resolves_on_turn:int, params:Dictionary}
var jobs: Array = []
# Transient log of what resolved on the most recent on_tick / on_month_boundary (for the
# turn feed + tests). NOT serialized -- it is a per-call readout, not durable state.
var last_events: Array = []

const KIND_INTERVIEW := "interview"
const KIND_CONNECTIONS := "connections"
const KIND_OFFER := "offer"

# The lanes a sourced candidate can land in (identity is decoupled from ability, Phase A).
const SPEC_POOL := ["safety", "capabilities", "interpretability", "alignment"]

# Promise ids the player can attach to an offer (appetite -> the hunger it feeds).
const PROMISE_APPETITE := {
	"first_authorship": "prestige",
	"mentorship": "mentees",
	"compute_budget": "compute",
	"mission_charter": "mission_purity",
}


# ============================================================================
# IDENTITY
# ============================================================================

func next_id(prefix: String) -> String:
	"""A deterministic, unique id (candidate or job). Pure counter -- no RNG."""
	next_serial += 1
	return "%s_%d" % [prefix, next_serial]


func stamp_candidate(candidate: Researcher) -> void:
	"""Give a freshly-created candidate a stable id + a deterministic visa flag (foreign/
	remote hires need a visa at onboard). No RNG: the flag rides the serial so it is
	reproducible and does not perturb the Phase-A hidden-layer stream."""
	if candidate == null:
		return
	if candidate.candidate_id == "":
		candidate.candidate_id = next_id("cand")
	var modulo := Balance.inum("hiring.onboarding.foreign_modulo", 4)
	if modulo > 0:
		var serial := int(candidate.candidate_id.get_slice("_", 1))
		candidate.needs_visa = (serial % modulo == 0)


# ============================================================================
# SOURCE (two channels, distinct pricing)
# ============================================================================

func advertise(state) -> Dictionary:
	"""ADVERTISE channel: money + Attention -> a campaign that trickles UNVETTED candidates
	into the pool over the next few months (also a light reputation/discovery bump -- the
	market learns you're hiring). Slow, high-volume, cheap-on-favors. The trickle lands at
	month boundaries, so nothing arrives instantly (ADR-0009)."""
	last_events = []
	var cost_money := Balance.num("hiring.advertise.cost_money", 8000.0)
	var cost_att := Balance.inum("hiring.advertise.cost_attention", 3)
	if state.money < cost_money:
		return {"success": false, "message": "Can't afford the ad spend ($%d)" % int(cost_money)}
	if state.month_plan == null or not state.month_plan.spend_attention(cost_att):
		return {"success": false, "message": "Not enough Attention to launch an ad campaign (%d needed)" % cost_att}
	state.money -= cost_money
	# Light discovery effect: NPC awareness of you (reputation).
	state.reputation += Balance.num("hiring.advertise.reputation_gain", 1.0)
	campaigns.append({
		"months_remaining": Balance.inum("hiring.advertise.campaign_months", 3),
		"per_month_min": Balance.inum("hiring.advertise.per_month_min", 0),
		"per_month_max": Balance.inum("hiring.advertise.per_month_max", 2),
	})
	return {"success": true, "message": "Launched a hiring ad campaign (candidates trickle in over the coming months)."}


func use_connections(state) -> Dictionary:
	"""CONNECTIONS channel: spend a favor (reputation) + Attention -> a FAST, short-duration
	job that (on success) yields ONE PRE-VETTED candidate (skill + comp already known,
	reveal_level = SKILL). Success scales with relative-rep flattery: your standing vs the
	target's desirability -- a low-rep lab often calls in the favor and still gets a no. The
	favor is spent whether or not it lands (that's the gamble)."""
	last_events = []
	var cost_rep := Balance.num("hiring.connections.cost_reputation", 6.0)
	var cost_att := Balance.inum("hiring.connections.cost_attention", 2)
	if state.reputation < cost_rep:
		return {"success": false, "message": "Not enough standing to call in a favor (%d rep)" % int(cost_rep)}
	if state.month_plan == null or not state.month_plan.spend_attention(cost_att):
		return {"success": false, "message": "Not enough Attention to work your connections (%d needed)" % cost_att}
	state.reputation -= cost_rep
	var job_id := next_id("job")
	jobs.append({
		"job_id": job_id,
		"kind": KIND_CONNECTIONS,
		"candidate_id": "",
		"resolves_on_turn": int(state.turn) + Balance.inum("hiring.connections.duration_ticks", 2),
		"params": {},
	})
	return {"success": true, "message": "Reached out through your network -- a pre-vetted lead may surface shortly."}


func _connection_success_chance(state) -> float:
	"""Relative-rep flattery: your reputation vs a desirability scale. Higher standing ->
	the introduction lands more reliably. Bounded so it is never a sure thing either way."""
	var certainty := Balance.num("hiring.connections.rep_for_certainty", 80.0)
	var lo := Balance.num("hiring.connections.min_success", 0.05)
	var hi := Balance.num("hiring.connections.max_success", 0.95)
	if certainty <= 0.0:
		return hi
	return clampf(state.reputation / certainty, lo, hi)


func _spawn_candidate(state, prevet: bool) -> Researcher:
	"""Create one random candidate deterministically (draws from state.rng -> replay-safe).
	Pre-vetted candidates land higher-skill and partially revealed (skill + comp already
	known); advertised candidates arrive uninterviewed (reveal 0)."""
	var spec: String = SPEC_POOL[state.rng.randi() % SPEC_POOL.size()]
	var c := Researcher.new(spec)
	c.generate_random(state.rng)
	c.specialization = spec
	if prevet:
		var lo := Balance.inum("hiring.connections.prevet_skill_min", 5)
		var hi := Balance.inum("hiring.connections.prevet_skill_max", 8)
		c.skill_level = state.rng.randi_range(lo, hi)
		c.base_productivity = 0.5 + (c.skill_level * 0.1)
		c.set_reveal_level(Researcher.REVEAL_SKILL)  # pre-vetted: skill + comp known up front
	return c


func _add_sourced_candidate(state, candidate: Researcher) -> bool:
	"""Stamp + admit a sourced candidate, respecting the pool cap. Returns false if full."""
	stamp_candidate(candidate)
	if state.candidate_pool.size() >= state.MAX_CANDIDATES:
		return false
	state.candidate_pool.append(candidate)
	return true


# ============================================================================
# INTERVIEW (Attention-gated triage; reveals the Phase-A card)
# ============================================================================

func launch_interview(state, candidate_id: String) -> Dictionary:
	"""Queue an interview against a specific candidate (TRIAGE -- you can't screen the whole
	pool). Spends Attention now; the reveal lands after a few ticks (ADR-0009). Interviewing
	is the ONLY way to peel the reveal ladder; it never fabricates (ADR-0004)."""
	last_events = []
	var cand := find_pool_candidate(state, candidate_id)
	if cand == null:
		return {"success": false, "message": "No such candidate in the pool."}
	if cand.reveal_level >= Researcher.MAX_REVEAL:
		return {"success": false, "message": "%s is already fully interviewed." % cand.researcher_name}
	if _has_job_for(candidate_id, KIND_INTERVIEW):
		return {"success": false, "message": "%s already has an interview scheduled." % cand.researcher_name}
	var cost_att := Balance.inum("hiring.interview.cost_attention", 2)
	if state.month_plan == null or not state.month_plan.spend_attention(cost_att):
		return {"success": false, "message": "Not enough Attention to interview (%d needed)" % cost_att}
	jobs.append({
		"job_id": next_id("job"),
		"kind": KIND_INTERVIEW,
		"candidate_id": candidate_id,
		"resolves_on_turn": int(state.turn) + Balance.inum("hiring.interview.duration_ticks", 3),
		"params": {},
	})
	return {"success": true, "message": "Interview scheduled with %s." % cand.researcher_name}


# ============================================================================
# OFFER + NEGOTIATE (no minigame; the hidden self-worth range is the mechanic)
# ============================================================================

func self_worth_floor(candidate: Researcher, promises: Array = []) -> float:
	"""The hidden acceptance FLOOR -- the lowest cash the candidate will take. Built from the
	(revealed-at-L1) salary_expectation E and the hidden appetites:
	  floor = E * (1 - tolerance)             tolerance shrinks as the MONEY appetite grows
	Promises feed a hunger and buy the floor DOWN in proportion to the matching appetite
	(appetites as negotiation currency, ADR-0011). This is the one genuinely-hidden function
	the offer must land inside."""
	var e: float = candidate.salary_expectation
	var money_ap: float = float(candidate.appetites.get("money", 0.0))
	var base_tol := Balance.num("hiring.offer.base_tolerance", 0.15)
	var money_weight := Balance.num("hiring.offer.money_appetite_weight", 0.5)
	var tolerance: float = base_tol * (1.0 - money_weight * money_ap)
	var raw_floor: float = e * (1.0 - tolerance)
	var discount := 0.0
	var per_promise := Balance.num("hiring.offer.promise_discount", 0.20)
	for p in promises:
		var appetite_key: String = PROMISE_APPETITE.get(p, "")
		if appetite_key != "":
			discount += per_promise * float(candidate.appetites.get(appetite_key, 0.0)) * e
	return maxf(0.0, raw_floor - discount)


func negotiation_read(state, candidate: Researcher, promises: Array = []) -> Dictionary:
	"""The recruiter/lieutenant read ("we think X will take ~$Y / $Y+-") -- personified SA.
	With a recruiter on staff the visible band narrows tightly around the true floor; without
	one the player sees only a wide guess. Never leaks the exact number (still a judgement)."""
	var e: float = candidate.salary_expectation
	var floor: float = self_worth_floor(candidate, promises)
	var recruiter := _best_recruiter(state)
	if recruiter == null:
		# No read: a wide, uninformative band around the expectation.
		return {
			"has_recruiter": false,
			"low": e * 0.70, "high": e * 1.10, "mid": e,
			"text": "No recruiter read -- somewhere around $%d (wide guess)." % int(e),
		}
	# Recruiter read: a tight band around the real floor; skill sharpens it.
	var spread := Balance.num("hiring.offer.read_spread", 0.06) * e
	return {
		"has_recruiter": true,
		"recruiter": recruiter.researcher_name,
		"low": maxf(0.0, floor - spread), "high": floor + spread, "mid": floor,
		"text": "%s thinks %s takes about $%d (+-$%d)." % [
			recruiter.researcher_name, candidate.researcher_name, int(floor), int(spread)],
	}


func make_offer(state, candidate_id: String, cash_offer: float, promises: Array = []) -> Dictionary:
	"""Extend an offer (Attention-gated, short duration). The candidate transitions to
	OFFERED now; the accept/reject decision lands after a couple ticks (ADR-0009). Promises
	are recorded on the job and only MINT their ledger bills if the offer is accepted."""
	last_events = []
	var cand := find_pool_candidate(state, candidate_id)
	if cand == null:
		return {"success": false, "message": "No such candidate in the pool."}
	if _has_job_for(candidate_id, KIND_OFFER):
		return {"success": false, "message": "%s already has an offer out." % cand.researcher_name}
	var cost_att := Balance.inum("hiring.offer.cost_attention", 1)
	if state.month_plan == null or not state.month_plan.spend_attention(cost_att):
		return {"success": false, "message": "Not enough Attention to make an offer (%d needed)" % cost_att}
	if not cand.transition_hire_state(Researcher.HireState.OFFERED):
		# spend already happened; refund the attention since we can't proceed
		state.month_plan.attention_spent -= cost_att
		return {"success": false, "message": "%s can't be offered from their current state." % cand.researcher_name}
	jobs.append({
		"job_id": next_id("job"),
		"kind": KIND_OFFER,
		"candidate_id": candidate_id,
		"resolves_on_turn": int(state.turn) + Balance.inum("hiring.offer.duration_ticks", 2),
		"params": {"cash": roundf(cash_offer), "promises": promises.duplicate()},
	})
	return {"success": true, "message": "Offer out to %s ($%d)." % [cand.researcher_name, int(cash_offer)]}


func _resolve_offer(state, cand: Researcher, cash: float, promises: Array) -> Dictionary:
	"""Land an offer decision. In range -> accept; below floor -> roll reject vs resentment.
	Accept employs the candidate (keeping whatever stayed hidden -- blind hires are legal),
	mints promise ledger entries, and starts onboarding."""
	var floor: float = self_worth_floor(cand, promises)
	if cash >= floor:
		return _accept_offer(state, cand, cash, promises, false)
	# Below the floor: how far below sets the reject probability.
	var reject_scale := Balance.num("hiring.offer.reject_scale", 2.0)
	var shortfall_frac: float = (floor - cash) / maxf(1.0, floor)
	var prob_reject: float = clampf(shortfall_frac * reject_scale, 0.0, 1.0)
	if state.rng.randf() < prob_reject:
		# Declined -- candidate returns to the pool (still selectable / re-offerable).
		cand.transition_hire_state(Researcher.HireState.CANDIDATE_IN_POOL)
		return {"success": true, "outcome": "rejected",
			"message": "%s declined the offer (lowball) -- back in the pool." % cand.researcher_name}
	# Accepted, but resentful: employed with a loyalty debt (ADR-0003).
	return _accept_offer(state, cand, cash, promises, true)


func _accept_offer(state, cand: Researcher, cash: float, promises: Array, resentful: bool) -> Dictionary:
	"""Employ the candidate. Pipeline hires are NOT force-revealed (a blind hire keeps its
	hidden layer) and start UN-onboarded (not yet productive). Promises + resentment mint
	their ledger bills here, at the moment they become real obligations."""
	cand.transition_hire_state(Researcher.HireState.OFFERED)  # ensure OFFERED before EMPLOYED
	state.remove_candidate(cand)
	cand.current_salary = cash
	# Employ WITHOUT forcing full reveal (blind hires stay partly hidden, per the brief).
	state.add_researcher(cand, false)
	# Begin onboarding: not productive until the checklist clears.
	cand.onboarded = false
	cand.laptop_done = false
	cand.visa_done = not cand.needs_visa
	cand.mentoring_done = false
	cand.mentoring_skipped = false
	var minted: Array = []
	if state.ledger:
		for p in promises:
			if PROMISE_APPETITE.has(p):
				state.ledger.add(Ledger.appetite_promise(cand.researcher_name, String(p)))
				minted.append(p)
	var msg := "%s accepted ($%d)." % [cand.researcher_name, int(cash)]
	if minted.size() > 0:
		msg += " Promised: %s (a ledger obligation)." % ", ".join(minted)
	if resentful:
		var penalty := Balance.inum("hiring.offer.resentment_loyalty_penalty", 15)
		cand.loyalty = maxi(0, cand.loyalty - penalty)
		if state.ledger:
			state.ledger.add(Ledger.resentment_debt(cand.researcher_name))
		msg += " They took it resentfully -- a loyalty debt is on the books."
	return {"success": true, "outcome": "resentful_accept" if resentful else "accepted", "message": msg}


# ============================================================================
# ONBOARD (predictable checklist + situational events; gates productivity)
# ============================================================================

func onboarding_required(candidate: Researcher) -> Array:
	"""The HARD checklist that gates productivity: a laptop, plus a visa for foreign/remote
	hires. Mentoring is a soft (recommended-not-required) item handled separately."""
	var items: Array = ["laptop"]
	if candidate.needs_visa:
		items.append("visa")
	return items


func onboarding_status(candidate: Researcher) -> Dictionary:
	"""A readout of onboarding progress for the UI / tests."""
	return {
		"onboarded": candidate.onboarded,
		"needs_visa": candidate.needs_visa,
		"laptop_done": candidate.laptop_done,
		"visa_done": candidate.visa_done,
		"mentoring_done": candidate.mentoring_done,
		"mentoring_skipped": candidate.mentoring_skipped,
		"required": onboarding_required(candidate),
	}


func onboard_step(state, candidate_id: String, item: String) -> Dictionary:
	"""Complete one onboarding item, paying its Attention (+ money) cost. When the hard
	checklist clears, the hire becomes productive. Mentoring is optional: doing it avoids the
	lasting skimped-productivity debuff + the early-attrition risk (slack-as-insurance)."""
	last_events = []
	var cand := find_employed(state, candidate_id)
	if cand == null:
		return {"success": false, "message": "No such onboarding hire."}
	if cand.onboarded and item != "mentoring":
		return {"success": false, "message": "%s is already onboarded." % cand.researcher_name}
	match item:
		"laptop":
			if cand.laptop_done:
				return {"success": false, "message": "Laptop already issued."}
			if not _pay_onboard(state, Balance.num("hiring.onboarding.laptop_money", 3000.0), Balance.inum("hiring.onboarding.laptop_attention", 1)):
				return {"success": false, "message": "Can't afford to kit out %s yet." % cand.researcher_name}
			cand.laptop_done = true
		"visa":
			if not cand.needs_visa:
				return {"success": false, "message": "%s doesn't need a visa." % cand.researcher_name}
			if cand.visa_done:
				return {"success": false, "message": "Visa already sorted."}
			if not _pay_onboard(state, Balance.num("hiring.onboarding.visa_money", 5000.0), Balance.inum("hiring.onboarding.visa_attention", 2)):
				return {"success": false, "message": "Can't afford the visa sponsorship yet."}
			cand.visa_done = true
		"mentoring":
			if cand.mentoring_done:
				return {"success": false, "message": "Mentoring already done."}
			if not _pay_onboard(state, Balance.num("hiring.onboarding.mentoring_money", 0.0), Balance.inum("hiring.onboarding.mentoring_attention", 2)):
				return {"success": false, "message": "Not enough Attention to mentor %s." % cand.researcher_name}
			cand.mentoring_done = true
			cand.mentoring_skipped = false
		_:
			return {"success": false, "message": "Unknown onboarding item '%s'." % item}
	_maybe_finish_onboarding(cand)
	return {"success": true, "message": "%s: %s done." % [cand.researcher_name, item],
		"onboarded": cand.onboarded}


func skip_mentoring(state, candidate_id: String) -> Dictionary:
	"""Explicitly skip mentoring (slack-as-insurance, slow and tempting): saves the Attention
	now, but stamps a lasting productivity debuff + arms the early-attrition risk."""
	last_events = []
	var cand := find_employed(state, candidate_id)
	if cand == null:
		return {"success": false, "message": "No such onboarding hire."}
	cand.mentoring_skipped = true
	cand.mentoring_done = false
	_maybe_finish_onboarding(cand)
	return {"success": true, "message": "Skipped mentoring for %s (attrition risk + a productivity debuff)." % cand.researcher_name}


func _pay_onboard(state, money_cost: float, att_cost: int) -> bool:
	"""Charge an onboarding item (money + Attention), all-or-nothing."""
	if state.money < money_cost:
		return false
	if att_cost > 0 and (state.month_plan == null or state.month_plan.available() < att_cost):
		return false
	state.money -= money_cost
	if att_cost > 0:
		state.month_plan.spend_attention(att_cost)
	return true


func _maybe_finish_onboarding(cand: Researcher) -> void:
	"""Flip the hire to productive once the hard checklist (laptop + any visa) is clear.
	Mentoring is not required to become productive -- only to avoid the debuffs."""
	var ready := cand.laptop_done and (cand.visa_done or not cand.needs_visa)
	if ready:
		cand.onboarded = true


# ============================================================================
# TICKING (duration resolution + monthly trickle) -- deterministic, guarded
# ============================================================================

func on_tick(state) -> Array:
	"""Resolve any duration jobs due at state.turn. Called once per resolution tick. RNG is
	touched ONLY when a job actually resolves (offers roll; connections roll), so a tick with
	no due jobs leaves the deterministic stream untouched. Returns this tick's events."""
	last_events = []
	if jobs.is_empty():
		return last_events
	var still: Array = []
	for job in jobs:
		if int(job.get("resolves_on_turn", 0)) > int(state.turn):
			still.append(job)
			continue
		_resolve_job(state, job)
	jobs = still
	return last_events


func _resolve_job(state, job: Dictionary) -> void:
	var kind := String(job.get("kind", ""))
	match kind:
		KIND_INTERVIEW:
			var cand := find_pool_candidate(state, String(job.get("candidate_id", "")))
			if cand != null:
				var before := cand.reveal_level
				cand.reveal_more(Balance.inum("hiring.interview.reveal_step", 1))
				last_events.append({"kind": "interview_done", "candidate": cand.researcher_name,
					"reveal_level": cand.reveal_level, "was": before})
		KIND_CONNECTIONS:
			if state.rng.randf() < _connection_success_chance(state):
				var c := _spawn_candidate(state, true)
				if _add_sourced_candidate(state, c):
					last_events.append({"kind": "connection_hit", "candidate": c.researcher_name})
				else:
					last_events.append({"kind": "connection_pool_full"})
			else:
				last_events.append({"kind": "connection_miss"})
		KIND_OFFER:
			var oc := find_pool_candidate(state, String(job.get("candidate_id", "")))
			if oc != null:
				var params: Dictionary = job.get("params", {})
				var r := _resolve_offer(state, oc, float(params.get("cash", 0.0)), params.get("promises", []))
				last_events.append({"kind": "offer_" + String(r.get("outcome", "?")),
					"candidate": oc.researcher_name, "message": r.get("message", "")})


func on_month_boundary(state) -> Array:
	"""New plan month: advertise campaigns trickle candidates, and un-mentored recent hires
	face an early-attrition roll. RNG is touched only when a campaign is live or an at-risk
	hire exists, so a boundary with neither is stream-neutral (pre-existing month-loop
	replays unaffected). Returns this boundary's events."""
	last_events = []
	_tick_campaigns(state)
	_tick_attrition(state)
	return last_events


func _tick_campaigns(state) -> void:
	if campaigns.is_empty():
		return
	var still: Array = []
	for camp in campaigns:
		var lo := int(camp.get("per_month_min", 0))
		var hi := int(camp.get("per_month_max", 2))
		var n: int = state.rng.randi_range(lo, hi)
		for i in range(n):
			var c := _spawn_candidate(state, false)
			if _add_sourced_candidate(state, c):
				last_events.append({"kind": "advertise_hit", "candidate": c.researcher_name})
		var rem := int(camp.get("months_remaining", 0)) - 1
		if rem > 0:
			camp["months_remaining"] = rem
			still.append(camp)
	campaigns = still


func _tick_attrition(state) -> void:
	"""Un-mentored, still-at-risk hires can quit early (skimping bites). Deterministic."""
	var risk := Balance.num("hiring.onboarding.attrition_risk", 0.15)
	# Snapshot: _tick_attrition may remove from state.researchers as it goes.
	var at_risk: Array = []
	for r in state.researchers:
		if r.hire_state == Researcher.HireState.EMPLOYED and r.mentoring_skipped and not r.mentoring_done:
			at_risk.append(r)
	for r in at_risk:
		if state.rng.randf() < risk:
			r.mentoring_skipped = false  # one roll per skimped hire; consume the flag
			r.transition_hire_state(Researcher.HireState.DEPARTED)
			state.remove_researcher(r)
			if state.ledger:
				state.ledger.add(Ledger.staff_rider(r.researcher_name))  # disgruntled-departure rider
			last_events.append({"kind": "early_attrition", "candidate": r.researcher_name})


# ============================================================================
# LOOKUPS
# ============================================================================

func find_pool_candidate(state, candidate_id: String) -> Researcher:
	if candidate_id == "":
		return null
	for c in state.candidate_pool:
		if c.candidate_id == candidate_id:
			return c
	return null


func find_employed(state, candidate_id: String) -> Researcher:
	if candidate_id == "":
		return null
	for r in state.researchers:
		if r.candidate_id == candidate_id:
			return r
	return null


func _has_job_for(candidate_id: String, kind: String) -> bool:
	for j in jobs:
		if String(j.get("candidate_id", "")) == candidate_id and String(j.get("kind", "")) == kind:
			return true
	return false


func _best_recruiter(state) -> Researcher:
	"""The most senior employed, onboarded researcher acts as the recruiter/lieutenant that
	sharpens the negotiation read. null if the founder is still solo."""
	var best: Researcher = null
	var min_skill := Balance.inum("hiring.offer.recruiter_min_skill", 4)
	for r in state.researchers:
		if r.hire_state != Researcher.HireState.EMPLOYED or not r.onboarded:
			continue
		if r.skill_level < min_skill:
			continue
		if best == null or r.skill_level > best.skill_level:
			best = r
	return best


# ============================================================================
# CONVENIENCE (no-target) DRIVERS -- for the action-menu + sweep bots
# ============================================================================

func interview_next(state) -> Dictionary:
	"""Interview the least-revealed pool candidate that isn't already scheduled. Lets the
	action menu + bots drive the triage stage without a target-picker UI."""
	var target: Researcher = null
	for c in state.candidate_pool:
		if c.reveal_level >= Researcher.MAX_REVEAL:
			continue
		if _has_job_for(c.candidate_id, KIND_INTERVIEW):
			continue
		if target == null or c.reveal_level < target.reveal_level:
			target = c
	if target == null:
		return {"success": false, "message": "No un-interviewed candidate to screen."}
	return launch_interview(state, target.candidate_id)


func offer_best(state) -> Dictionary:
	"""Make a fair-value offer (at expectation) to the highest-skill candidate not already
	under offer -- the bot/menu 'just hire someone' driver. Uses no promises."""
	var target: Researcher = null
	for c in state.candidate_pool:
		if c.hire_state != Researcher.HireState.CANDIDATE_IN_POOL:
			continue
		if _has_job_for(c.candidate_id, KIND_OFFER):
			continue
		if target == null or c.skill_level > target.skill_level:
			target = c
	if target == null:
		return {"success": false, "message": "No candidate available to offer."}
	# Offer at the (revealed-or-not) expectation -> comfortably in range.
	return make_offer(state, target.candidate_id, target.salary_expectation, [])


func onboard_all(state) -> Dictionary:
	"""Advance every onboarding hire by one available checklist step (laptop -> visa ->
	mentoring). The bot/menu driver for the onboard stage."""
	var acted := 0
	for r in state.researchers:
		if r.onboarded and r.mentoring_done:
			continue
		if r.hire_state != Researcher.HireState.EMPLOYED:
			continue
		var step := ""
		if not r.laptop_done:
			step = "laptop"
		elif r.needs_visa and not r.visa_done:
			step = "visa"
		elif not r.mentoring_done:
			step = "mentoring"
		if step != "":
			var res := onboard_step(state, r.candidate_id, step)
			if res.get("success", false):
				acted += 1
	if acted == 0:
		return {"success": false, "message": "Nothing to onboard (or can't afford it)."}
	return {"success": true, "message": "Advanced onboarding for %d hire(s)." % acted}


# ============================================================================
# SERIALIZATION (mirrors Ledger / MonthPlan; JSON numbers come back as float)
# ============================================================================

func to_dict() -> Dictionary:
	return {
		"next_serial": next_serial,
		"campaigns": campaigns.duplicate(true),
		"jobs": jobs.duplicate(true),
	}


func from_dict(data: Dictionary) -> void:
	next_serial = int(data.get("next_serial", 0))
	campaigns = []
	for camp in data.get("campaigns", []):
		if camp is Dictionary:
			var c: Dictionary = camp.duplicate(true)
			c["months_remaining"] = int(c.get("months_remaining", 0))
			c["per_month_min"] = int(c.get("per_month_min", 0))
			c["per_month_max"] = int(c.get("per_month_max", 0))
			campaigns.append(c)
	jobs = []
	for job in data.get("jobs", []):
		if job is Dictionary:
			var j: Dictionary = job.duplicate(true)
			j["job_id"] = String(j.get("job_id", ""))
			j["kind"] = String(j.get("kind", ""))
			j["candidate_id"] = String(j.get("candidate_id", ""))
			j["resolves_on_turn"] = int(j.get("resolves_on_turn", 0))
			var params: Dictionary = j.get("params", {})
			if params.has("cash"):
				params["cash"] = roundf(float(params["cash"]))
			j["params"] = params
			jobs.append(j)

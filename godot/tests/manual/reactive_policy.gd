class_name ReactivePolicy
extends RefCounted
## EE-9 - Reactive rule-policy framework (Pip 2026-07-14, WORKSHOP_2_BACKLOG "Balance-instrument
## roadmap" + "#638 review rulings").
##
## A POLICY is a declarative, parameterized description of theorized play: an ordered list of
## (condition -> action) rules evaluated at TWO decision points, mirroring ADR-0009's plan/window split:
##   - plan_rules   -- evaluated once per PLAN PHASE (start of a month). Each rule whose condition
##                    holds contributes action ids to an ordered priority list; the sweep harness
##                    fills the month's Attention/AP against that priority (affordability-gated).
##   - window_rules -- evaluated per RESPONSE WINDOW during day-tick playback. The first rule whose
##                    condition holds names the verb (handle_reserve / handle_cannibalize / defer /
##                    ignore). ADR-0009's "do this unless <condition>, in which case do that".
##
## Conditions read a FEATURES snapshot of game state (cash, runway months, doom, reserve, ledger
## load, offers, staff, ...) computed once per decision -- so rules stay cheap and READABLE. The
## point (Pip): a policy is DOCUMENTATION of a theorized line, not opaque code. Parameters are
## named + carried on the policy so future sweeps can vary them (parameterized reactive policies --
## the established game-balancing technique the ruling calls for).
##
## Pure/deterministic: rules draw no randomness; given the same features they return the same
## decision. All engine randomness is the seeded state.rng, so every (seed, policy) run is replayable.
##
## This file is TOOLING (tests/manual/lib) -- it never ships in a build and touches no gameplay code.

const RUNWAY_UNKNOWN := 999.0  # runway when burn ~= 0 (no staff): effectively infinite


# --- Feature extraction: the read-only state snapshot conditions evaluate against ---

static func features(state) -> Dictionary:
	"""Snapshot the decision-relevant game state. Named fields keep policy conditions declarative.
	`runway_months` is an ESTIMATE: cash / (staff * annual_salary_base / 12). It uses the flat
	salary base (salaries.legacy_staff_annual), not per-researcher salaries -- a policy heuristic,
	not the payroll engine. Documented so tuning can argue with it."""
	var staff: int = state.get_total_staff()
	var annual_base: float = Balance.num("salaries.legacy_staff_annual", 60000.0)
	var monthly_burn: float = float(staff) * annual_base / 12.0
	var runway: float = RUNWAY_UNKNOWN if monthly_burn <= 1.0 else state.money / monthly_burn
	var plan = state.month_plan
	var ledger_outstanding: float = 0.0
	var ledger_open: int = 0
	var ledger_secrets: int = 0
	if state.ledger != null:
		ledger_outstanding = state.ledger.outstanding()
		ledger_open = (state.ledger.entries as Array).size()
		ledger_secrets = (state.ledger.secret_entries() as Array).size()
	return {
		"cash": state.money,
		"runway_months": runway,
		"monthly_burn": monthly_burn,
		"doom": state.doom,
		"reputation": state.reputation,
		"governance": state.governance,
		"staff": staff,
		"safety_researchers": state.safety_researchers,
		"capability_researchers": state.capability_researchers,
		"papers": state.papers,
		"turn": state.turn,
		"ap": state.action_points,
		"attention_available": plan.available() if plan != null else 0,
		"reserve_remaining": plan.reserve_remaining() if plan != null else 0,
		"ledger_outstanding": ledger_outstanding,
		"ledger_open": ledger_open,
		"ledger_secrets": ledger_secrets,
		# "offers available": windows currently demanding a decision (usually 0 at plan phase;
		# non-zero mid-playback). Kept as a legible feature for window rules.
		"offers_available": (state.pending_events as Array).size(),
	}


# --- Policy / rule constructors (declarative sugar) ---

static func make(name: String, params: Dictionary, plan_rules: Array, window_rules: Array = []) -> Dictionary:
	"""Build a named, parameterized policy. plan_rules/window_rules are ordered Arrays of rules."""
	return {
		"name": name,
		"params": params,
		"plan_rules": plan_rules,
		"window_rules": window_rules,
	}


static func rule(when: Callable, actions: Array, desc: String = "") -> Dictionary:
	"""A plan rule: when `when(features)` holds, append `actions` (ordered action ids) to the
	month's priority list. Rules are cumulative and ordered -- earlier rules bid first for Attention/AP."""
	return {"when": when, "actions": actions, "desc": desc}


static func wrule(when: Callable, verb: String, desc: String = "") -> Dictionary:
	"""A window rule: when `when(features, window)` holds, respond with `verb`. First match wins."""
	return {"when": when, "verb": verb, "desc": desc}


static func repeat(action_id: String, n: int) -> Array:
	"""n copies of an action id -- the readable way to say 'fill leftover capacity with X'."""
	var out: Array = []
	for _i in range(max(0, n)):
		out.append(action_id)
	return out


# --- Evaluation ---

static func plan_priority(policy: Dictionary, f: Dictionary) -> Array:
	"""Walk plan_rules in order; concatenate the actions of every rule whose condition holds.
	Returns the ordered action-id priority list the harness fills against (affordability-gated)."""
	var pri: Array = []
	for r in policy.get("plan_rules", []):
		var cond: Callable = r["when"]
		if bool(cond.call(f)):
			for a in r.get("actions", []):
				pri.append(String(a))
	return pri


static func window_verb(policy: Dictionary, f: Dictionary, window: Dictionary, default_verb: String = "handle_reserve") -> String:
	"""First window rule whose condition holds names the verb; else `default_verb`. The harness
	still validates legality/payment (an illegal verb falls back per the caller)."""
	for r in policy.get("window_rules", []):
		var cond: Callable = r["when"]
		if bool(cond.call(f, window)):
			return String(r["verb"])
	return default_verb


static func params_line(policy: Dictionary) -> String:
	"""One-line human-readable parameter dump for report headers (documents the tunables)."""
	var parts: Array = []
	for k in policy.get("params", {}).keys():
		parts.append("%s=%s" % [k, str(policy["params"][k])])
	return ", ".join(parts) if parts.size() > 0 else "(no parameters)"

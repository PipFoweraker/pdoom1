class_name WindowResolver
extends RefCounted
## Response-window resolution (L1 / ADR-0009 S3, ADR-0012). A window is the only event
## tier that demands a decision; this resolves the costed menu:
##   handle_reserve      -- HANDLE, paid painlessly from the crisp reserve (Attention)
##   handle_cannibalize  -- HANDLE, paid by eating un-reserved capacity / killing planned WIP
##   defer               -- mints a Liability Ledger entry (deferrable class only)
##   ignore              -- the stated list-price consequence
##   auto_ignore         -- an UNANSWERED window auto-resolves as IGNORE + a mild rep penalty
##                         (nonresponse annoys the offerer, addendum #1); illegal on
##                         unignorable windows.
##
## Attention (the founder decision currency) is paid via MonthPlan; the chosen option's own
## in-fiction resource costs (money/etc.) still apply through GameEvents.execute_event_choice.
## Legacy action_point costs on window options are STRIPPED -- Attention replaces AP as the
## window decision currency (L1 introduces Attention; L2 deletes the AP pool). Seam left clean
## for ADR-0015: this resolver never reads/writes doom directly -- it routes through option
## effects and ledger factories, both of which L2 migrates onto intermediaries.

const Events = preload("res://scripts/core/events.gd")

const DEFAULT_ATTENTION_COST := 1


static func window_config(event: Dictionary) -> Dictionary:
	return event.get("window", {}) if event.get("window", {}) is Dictionary else {}


static func attention_cost(event: Dictionary) -> int:
	return int(window_config(event).get("attention_cost", DEFAULT_ATTENTION_COST))


static func handle_option_id(event: Dictionary) -> String:
	"""Option applied on HANDLE. Defaults to the first option (pre-L1 popups led with the
	primary beneficial choice)."""
	var cfg := window_config(event)
	if cfg.has("handle_option"):
		return String(cfg["handle_option"])
	var options: Array = event.get("options", [])
	if not options.is_empty() and options[0] is Dictionary:
		return String(options[0].get("id", ""))
	return ""


static func ignore_option_id(event: Dictionary) -> String:
	"""Option applied on IGNORE (list price). Defaults to a zero-cost 'continue/do nothing'
	option if one exists, else the last option, else '' (no effect)."""
	var cfg := window_config(event)
	if cfg.has("ignore_option"):
		return String(cfg["ignore_option"])
	var options: Array = event.get("options", [])
	for opt in options:
		if opt is Dictionary and (opt.get("costs", {}) as Dictionary).is_empty():
			return String(opt.get("id", ""))
	if not options.is_empty() and options[-1] is Dictionary:
		return String(options[-1].get("id", ""))
	return ""


static func resolve(state: GameState, plan: MonthPlan, event: Dictionary, response: String, rng: RandomNumberGenerator = null) -> Dictionary:
	"""Apply a window response. Returns a result dict:
	{success, response, payment_source, attention_paid, cancelled_wip, ledger_source,
	 message, deltas}. Records the response into the replay artifact at this choke point."""
	var event_id := String(event.get("id", ""))
	var cost := attention_cost(event)
	var result := {
		# refusal: n/a -- result TEMPLATE, not a refusal. It says nothing to a player; each
		# branch below either succeeds or fills in its own message and `refusal` kind.
		"success": false,
		"response": response,
		"payment_source": "",
		"attention_paid": 0,
		"cancelled_wip": [],
		"ledger_source": "",
		"message": "",
		"deltas": {},
	}

	match response:
		"handle_reserve":
			if not plan.pay_from_reserve(cost):
				result["message"] = "Insufficient reserve to handle from reserve"
				return result
			result["payment_source"] = "reserve"
			result["attention_paid"] = cost
			_merge_option(result, _apply_option(state, event, handle_option_id(event)))
			result["success"] = true

		"handle_cannibalize":
			var pay := plan.pay_by_cannibalizing(cost)
			var cancelled: Array = pay.get("cancelled", [])
			result["cancelled_wip"] = cancelled
			if not pay.get("paid", false):
				# STUB-VS-RULE (see scripts/core/refusal.gd). ONE sentence was covering TWO
				# different failures, and the commoner of the two is not a rule at all.
				#
				# cancelled.is_empty() <=> pay_by_cannibalizing found NO strategic WIP to eat,
				# so the "pull from planned work" half of this verb did nothing. In the shipped
				# game that is ALWAYS the case: MonthPlan.queued_strategic has no production
				# writer -- its only one, GameManager.queue_strategic_action(), has zero callers
				# -- while the queue the player can SEE lives in GameState.queued_actions, which
				# this path cannot reach. Refusing with "insufficient capacity" taught a budget
				# rule for what is really an unbuilt mechanic (playtest 2026-08-14, Pip: "which,
				# like, isn't strictly true?").
				#
				# The discriminator is derived, not declared, so it self-heals: the day anything
				# wires queue_strategic_action() up, cancelled stops being empty and the genuine
				# RULE branch takes over on its own. There is no flag to remember to clear.
				result["message"] = "Insufficient capacity to handle by cannibalizing"
				if cancelled.is_empty():
					result["message"] = Refusal.mark_stub(result["message"])
					result["refusal"] = Refusal.CLASS_STUB
				else:
					result["refusal"] = Refusal.CLASS_RULE
				return result
			result["payment_source"] = "cannibalize"
			result["attention_paid"] = cost
			_merge_option(result, _apply_option(state, event, handle_option_id(event)))
			result["success"] = true

		"defer":
			if not EventTiers.defer_allowed(event):
				result["message"] = "This window cannot be deferred (%s class)" % EventTiers.class_of(event)
				return result
			var entry = _mint_deferral(event, rng)
			if entry != null:
				state.ledger.add(entry)
				result["ledger_source"] = entry.source
			result["payment_source"] = "defer"
			result["message"] = "Deferred -- minted ledger entry"
			result["success"] = true

		"ignore", "auto_ignore":
			if response == "auto_ignore" and EventTiers.is_unignorable(event):
				result["message"] = "Unignorable window cannot auto-resolve to ignore"
				return result
			result["payment_source"] = "ignore"
			_merge_option(result, _apply_option(state, event, ignore_option_id(event)))
			if response == "auto_ignore":
				# Nonresponse annoys the offerer: a mild, data-driven reputation penalty
				# (addendum #1). Applied on top of the list-price consequence. Windows a
				# player owes only themselves (#789 hiring prompts) opt out via
				# window.lapse_penalty=false -- there is no offerer to annoy.
				if bool(window_config(event).get("lapse_penalty", true)):
					var pen := Balance.num("events.unanswered_window_rep_penalty", 2.0)
					state.reputation = max(0.0, state.reputation - pen)
					var d: Dictionary = result["deltas"]
					d["reputation"] = float(d.get("reputation", 0.0)) - pen
					result["message"] = "Window lapsed -- auto-ignored (-%.1f reputation)" % pen
				else:
					result["message"] = "Window lapsed -- auto-ignored"
			result["success"] = true

		_:
			result["message"] = "Unknown window response: %s" % response
			return result

	# Record into the replay artifact at the choke point (schema bump: window responses
	# carry the payment source -- ADR-0009 consequence).
	if result["success"] and typeof(VerificationTracker) != TYPE_NIL:
		VerificationTracker.record_window_response(event_id, response, String(result["payment_source"]), state.turn)
	return result


static func resolve_chosen_option(state: GameState, plan: MonthPlan, event: Dictionary, option_id: String, rng: RandomNumberGenerator = null) -> Dictionary:
	"""Resolve a window via one of the event's OWN options (the v1 dialog path: the
	event_dialog presents the event's options, not the four verbs). Mapping onto the
	ADR-0009 menu:
	  - the window's ignore option -> IGNORE (list price, no Attention drawn)
	  - any other option           -> HANDLE, paid reserve-first, falling back to
	                                  cannibalizing un-reserved capacity/WIP
	The chosen option's own in-fiction costs/effects apply (AP stripped); the real payment
	source (reserve/cannibalize/ignore) lands in the replay artifact. The explicit
	four-verb menu incl. DEFER is the plan-screen UI's job -- DEFER is not reachable from
	this v1 path."""
	var event_id := String(event.get("id", ""))

	# #789: a window may map its OWN option ids onto explicit payment verbs
	# (window.option_verbs) -- the hiring accept-prompt uses this so the player chooses
	# the Attention source explicitly (reserve vs cannibalize; teaches the crisp
	# reserve). Pre-check the chosen option's own costs (money) BEFORE delegating, so a
	# failed money check can never consume the reserve.
	var verbs_cfg = window_config(event).get("option_verbs", {})
	if verbs_cfg is Dictionary and verbs_cfg.has(option_id):
		for opt in event.get("options", []):
			if opt is Dictionary and String(opt.get("id", "")) == option_id:
				if not state.can_afford(opt.get("costs", {})):
					return {"success": false, "message": "Cannot afford this choice"}
		return resolve(state, plan, event, String(verbs_cfg[option_id]), rng)

	if option_id == ignore_option_id(event) and not EventTiers.is_unignorable(event):
		return resolve(state, plan, event, "ignore", rng)

	# HANDLE with the chosen option. Check the option's own (Attention-stripped) costs
	# BEFORE drawing Attention, so a failed money check doesn't consume the reserve.
	var cleaned := strip_attention(event)
	var chosen: Dictionary = {}
	for opt in cleaned.get("options", []):
		if opt is Dictionary and String(opt.get("id", "")) == option_id:
			chosen = opt
			break
	if chosen.is_empty():
		return {"success": false, "message": "Unknown option: %s" % option_id}
	if not state.can_afford(chosen.get("costs", {})):
		return {"success": false, "message": "Cannot afford this choice"}

	var cost := attention_cost(event)
	var payment := ""
	var cancelled: Array = []
	if plan.pay_from_reserve(cost):
		payment = "reserve"
	else:
		var pay := plan.pay_by_cannibalizing(cost)
		cancelled = pay.get("cancelled", [])
		if not pay.get("paid", false):
			return {"success": false, "message": "Not enough Attention to handle this window", "cancelled_wip": cancelled}
		payment = "cannibalize"

	var opt_result := Events.execute_event_choice(cleaned, option_id, state)
	var result := {
		"success": opt_result.get("success", false),
		"response": "handle",
		"payment_source": payment,
		"attention_paid": cost,
		"cancelled_wip": cancelled,
		"ledger_source": "",
		"message": opt_result.get("message", ""),
		"deltas": opt_result.get("deltas", {}),
	}
	if opt_result.has("messages"):
		result["messages"] = opt_result["messages"]
	if result["success"] and typeof(VerificationTracker) != TYPE_NIL:
		VerificationTracker.record_window_response(event_id, "handle", payment, state.turn)
	return result


static func _apply_option(state: GameState, event: Dictionary, option_id: String) -> Dictionary:
	"""Apply an event option by id, STRIPPING the option's own Attention cost -- the window's
	Attention was already drawn from the reserve/cannibalize path above, so re-charging it
	here would double-bill. Returns the execute_event_choice result (or an empty success if
	the option id is blank -- a no-op ignore)."""
	if option_id == "":
		return {"success": true, "message": "No action", "deltas": {}}
	# #789: hiring prompt cards mutate pipeline state (onboarding flags + money), not
	# generic event effects -- route them to the pipeline. For handle verbs the Attention
	# was already drawn before this call; the pipeline charges money only.
	if String(event.get("kind", "")).begins_with("hiring_") and state.hiring != null:
		return state.hiring.apply_prompt_option(state, event, option_id)
	var cleaned := strip_attention(event)
	return Events.execute_event_choice(cleaned, option_id, state)


static func strip_attention(event: Dictionary) -> Dictionary:
	"""Clone an event with the founder Attention cost removed from every option's costs.
	Public: month playback presents windows through the event_dialog with Attention already
	stripped, so the dialog's affordability display matches what resolution will actually
	charge (the window Attention is drawn once, by resolve()).
	T2: renamed from strip_ap and now erases `attention`; the legacy `action_points` key is
	erased too so un-migrated content cannot resurrect a second founder charge."""
	var clone := event.duplicate(true)
	for opt in clone.get("options", []):
		if opt is Dictionary and opt.has("costs") and opt["costs"] is Dictionary:
			opt["costs"].erase("attention")
			opt["costs"].erase("action_points")
	return clone


## Display-only keys stamped onto the dialog's copy of a window by present_for_dialog().
## They exist so the PRESENTER never has to re-derive resolution policy -- see that function.
const DISPLAY_ATTENTION_KEY := "_display_window_attention"
const DISPLAY_FREE_OPTION_KEY := "_display_free_option_id"


static func present_for_dialog(event: Dictionary) -> Dictionary:
	"""The copy of a window the event_dialog should present: Attention stripped from the
	options (strip_attention's job) AND the window's own Attention price stamped back on as
	DISPLAY metadata.

	Why the stamp exists at all. strip_attention's docstring already promised that "the
	dialog's affordability display matches what resolution will actually charge" -- but it
	only ever did the erasing half. The window levies attention_cost(event) of its own, and
	nothing put that number anywhere the player could see it, so every popup with a priced
	option read as cheaper than it was and the free-out read " (Free)". Playtest 2026-08-10,
	Pip, on the stray cat: "Adopting the cat also costs attention, which is not advertised on
	the screen." That is not a cat bug -- stray_cat carries no `window` block, so it takes
	DEFAULT_ATTENTION_COST, exactly like every other un-annotated legacy popup.

	Stamping rather than letting the presenter compute it is deliberate. The dialog is handed
	events from SIX emit sites; only the two window paths strip, and a stripped event is
	indistinguishable from an un-stripped one whose options simply never declared Attention.
	The presenter therefore CANNOT tell from the dict alone whether a window charge is coming.
	Stamping at the one seam that knows makes the un-stamped paths (plan-phase legacy events,
	the synthetic month review) silently correct: no key, no claim.

	DISPLAY_FREE_OPTION_KEY mirrors resolve_chosen_option's free-out test verbatim -- the
	option that resolves as IGNORE pays no Attention, and on stray_cat that is `shoo_away`
	(it is the first option with an empty costs dict). Deriving it here rather than in the UI
	is what stops the label and the charge from drifting apart.

	Windows carrying `option_verbs` (#789 hiring accept-prompts) stamp ZERO: their option TEXT
	already names the price and the payment source ("Set them up now (2 Att from reserve)"),
	so a generic suffix would print the number twice."""
	var clone := strip_attention(event)
	var cfg := window_config(event)
	if cfg.has("option_verbs"):
		clone[DISPLAY_ATTENTION_KEY] = 0
	else:
		clone[DISPLAY_ATTENTION_KEY] = attention_cost(event)
	clone[DISPLAY_FREE_OPTION_KEY] = "" if EventTiers.is_unignorable(event) else ignore_option_id(event)
	return clone


static func _merge_option(result: Dictionary, opt_result: Dictionary) -> void:
	if opt_result.get("message", "") != "":
		result["message"] = opt_result["message"]
	if opt_result.has("deltas"):
		result["deltas"] = opt_result["deltas"]
	if opt_result.has("messages"):
		result["messages"] = opt_result["messages"]
	# Surface an option-level failure (e.g. couldn't afford the in-fiction money cost).
	if not opt_result.get("success", true):
		result["option_failed"] = true


static func _mint_deferral(event: Dictionary, rng: RandomNumberGenerator):
	"""Mint a Ledger entry for a DEFER, from the event's window.defer config. Defaults to a
	loan sized by the handle option's money cost (deferring a bill you didn't pay). Content
	tuning is L4/ADR-0013 -- this is the intake valve."""
	var cfg = window_config(event).get("defer", {})
	var factory: String = String(cfg.get("factory", "loan")) if cfg is Dictionary else "loan"
	var amount: float = float(cfg.get("amount", 0.0)) if cfg is Dictionary else 0.0
	if amount <= 0.0:
		# Fall back to the handle option's money cost as the deferred principal.
		for opt in event.get("options", []):
			if opt is Dictionary and String(opt.get("id", "")) == handle_option_id(event):
				amount = float((opt.get("costs", {}) as Dictionary).get("money", 0.0))
				break
	if amount <= 0.0:
		amount = 1000.0  # a nominal carried obligation so DEFER always has teeth
	match factory:
		"funding_strings":
			return Ledger.funding_with_strings(amount)
		"desperation_payroll":
			return Ledger.desperation_payroll(rng if rng != null else RandomNumberGenerator.new())
		_:
			return Ledger.loan(amount)

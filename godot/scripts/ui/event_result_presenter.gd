class_name EventResultPresenter
extends RefCounted
## CARVE 6 (docs/MAIN_UI_SEAM_MAP.md, seam R6): event / result PRESENTATION pulled out of the
## main_ui.gd monolith. This owns the "engine event/result -> on-screen feedback" translation:
## an executed action's result, an achievement unlock, and an engine error each become feed-log
## lines (and, for errors, the PLAN-screen toast). main_ui is now a thin view -- it wires the
## GameManager/achievements signals to one-line shims that forward here.
##
## This is a NON-FORKING extraction: every statement below is a VERBATIM move of presentation
## that previously lived inline in main_ui (_on_action_executed / _on_achievement_unlocked /
## _on_error_occurred + the _format_deltas helper). No gameplay/RNG/scoring change -- the same
## result Dictionaries produce the same feed lines. Ladder stays put.
##
## What this owns (was inline in the view):
##   * present_action_result(result)  -- was _on_action_executed's body: main feed line (honouring
##                                        the "flavour" channel so the arxiv-flood filter can
##                                        collapse it), the EE-7 delta summary, and any extra
##                                        `messages`.
##   * present_achievement(achievement) -- was _on_achievement_unlocked: the L8 unlock feed line.
##   * present_error(error_msg)         -- was _on_error_occurred: the red ERROR feed line plus the
##                                        PLAN-screen toast (surfaced where the player is acting).
##   * _format_deltas(deltas)           -- the EE-7 BBCode delta formatter, used only here.
##
## What STAYS in the view (main_ui), on purpose -- these are NOT event/result presentation:
##   * log_message / _feed_lines / _render_feed / _feed_passes_filter and the feed-filter toggle
##     handlers -- the feed MODEL + rendering substrate that this presenter WRITES INTO. It is
##     shared by dozens of call sites across the view (phase changes, hiring, etc.), so it stays
##     in the view and the presenter writes through `host.log_message(...)`, exactly as
##     ActionBarRenderer (CARVE 5) writes through host for the surfaces it does not own.
##   * plan_screen -- the view owns the PLAN screen node; present_error reaches it via
##     host.plan_screen.flash_error(...), unchanged.

var host  # MainUI node (untyped: avoids a class_name coupling cycle main_ui <-> presenter)


func _init(h = null) -> void:
	host = h


# --- Executed-action result (was main_ui._on_action_executed) -----------------------------

func present_action_result(result: Dictionary) -> void:
	print("[MainUI] Action executed: ", result)

	var message = result.get("message", "Action completed")
	# P0: FEED items carry a channel ("flavour" for the arxiv stream) so the feed filter can
	# collapse the spam. FEED lines are already BBCode-coloured; don't re-wrap them in lime.
	var channel := String(result.get("channel", "normal"))
	if channel != "normal":
		host.log_message(message, channel)
	else:
		host.log_message("[color=lime]" + message + "[/color]")

	# EE-7: resource-affecting events/actions state their applied deltas explicitly
	var deltas: Dictionary = result.get("deltas", {})
	if not deltas.is_empty():
		host.log_message("[color=gray]  `- delta[/color] " + _format_deltas(deltas))

	# Show any additional messages from action
	if result.has("messages"):
		for msg in result.get("messages", []):
			host.log_message("[color=white]  " + str(msg) + "[/color]")

	# Note: GameManager now handles auto-starting next turn


# --- Achievement unlock (was main_ui._on_achievement_unlocked) ----------------------------

func present_achievement(achievement: Dictionary) -> void:
	"""L8 (#619): surface unlocks in the message log. Recognition only (ADR-0002)."""
	host.log_message("[color=gold]* Achievement -- %s:[/color] [color=gray]%s[/color]" % [
		achievement.get("title", "?"), achievement.get("flavor", "")])


# --- Engine error (was main_ui._on_error_occurred) ----------------------------------------

func present_error(error_msg: String) -> void:
	print("[MainUI] Error: ", error_msg)
	host.log_message("[color=red]ERROR: " + error_msg + "[/color]")
	# Also surface it ON the PLAN screen where the player is acting (playtest 2026-07-24): the
	# feed above is WATCH-only (hidden in PLAN mode), so an action-queue rejection like "Not
	# enough Attention" / "Cannot afford ..." was previously invisible while planning. The toast
	# is hidden unless PLAN is the active screen, so this is additive, not duplicate noise.
	if host.plan_screen != null and is_instance_valid(host.plan_screen):
		host.plan_screen.flash_error(error_msg)


# --- Backend verdict for the BESPOKE submenu panels (hiring / travel) ----------------------

func present_outcome(result: Dictionary, verb: String) -> bool:
	"""ONE door for the {success, message} Dictionaries the bespoke submenu panels get back
	from their backend delegates. An ACCEPTANCE keeps the cyan feed line those panels already
	wrote; a REFUSAL goes out through present_error, so it reaches the PLAN toast as well as
	the feed. Returns result.success, so a call site can gate its follow-up on the backend
	having actually accepted (#821: the UI tile appears only when the backend accepts).

	Why this exists -- the gap #1204 left open. _on_dynamic_action_pressed returns at its
	`is_submenu` branch, ABOVE the attention/affordability guards that report through
	report_rejection(). SubmenuController.on_option_selected re-armed those guards for the six
	icon-grid panels plus financing, but the two BESPOKE panels never queue through it: hiring
	and travel call GameManager.hiring_* / GameActions.*_conference_* directly and presented
	the refusal with a bare log_message(). The feed lives inside WatchScreen, which
	ScreenModeController hides for the whole of PLAN, so every refused hiring/travel click
	looked like a dead button. Playtest, verbatim: "I can fail silently if I queue 19
	fundraisings and then try to make offers to 2 people. Making offers doesn't show up as a
	card."

	The refusal REASON is relayed from the backend VERBATIM, on purpose. The view must not
	re-derive it: a shadow pre-check in the view is exactly the defect #1204 fixed, and the
	backend is the only thing that knows why it said no (a hiring click can be refused for
	Attention, money, reputation, desk space, or pipeline state). It already answers in house
	voice and names the number -- "Not enough Attention to make an offer (1 needed)" -- the
	same shape as the view's own "Not enough Attention: need %d %s hours, have %d".

	This changes NO gameplay: same conditions, same early returns, same economy. Only which
	surface the refusal lands on."""
	var accepted := bool(result.get("success", false))
	var message := String(result.get("message", "")).strip_edges()
	if accepted:
		host.log_message("[color=cyan]%s: %s[/color]" % [verb, message])
		return true
	# A refusal with no reason is the same dead button by another route -- name the action at
	# least, so the player knows which click was rejected.
	present_error(message if message != "" else "%s was refused (no reason given)." % verb)
	return false


# --- Delta formatting helper (was main_ui._format_deltas) ---------------------------------

func _format_deltas(deltas: Dictionary) -> String:
	"""EE-7: BBCode-coloured 'money +$20k, doom +3.0' summary for the message log --
	resource-affecting events state their deltas instead of burying them in prose."""
	var order := ["money", "compute", "research", "papers", "reputation", "doom"]
	var parts := []
	for key in order:
		if not deltas.has(key):
			continue
		var d: float = float(deltas[key])
		var txt: String
		if key == "money":
			txt = ("+" if d > 0.0 else "-") + GameConfig.format_money(absf(d))
		else:
			txt = "%+.1f" % d
		var good: bool = (d < 0.0) if key == "doom" else (d > 0.0)
		parts.append("[color=%s]%s %s[/color]" % ["lime" if good else "red", key, txt])
	return ", ".join(parts)

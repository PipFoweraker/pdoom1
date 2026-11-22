extends RefCounted
class_name DeathAttribution
## EE-8 (ADR-0012): root-cause death attribution for finished runs.
##
## The ledger never owns a death screen -- defaults cascade into the existing
## doom/rep deaths through intermediate wreckage (unpaid entries -> rep collapse ->
## funding starvation -> death). The SURFACE cause (which counter ended the run)
## therefore hides the cascade: "dies of doom/rep" when the ledger fed the player
## to the thing that killed them. This classifier reads GameState.cause_log (the
## turn-stamped contributing-cause trail written by Ledger/TurnManager/GameState)
## and answers "what ROOT cause produced this death?" for balance accounting.
##
## READ-ONLY: classify() inspects a finished state; it never mutates and is never
## called during play, so attribution can never change run outcomes.

## Rules (documented so tuning sessions can argue with them):
## - A death is LEDGER-rooted when ledger-inflicted damage passes a NECESSITY test
##   in the death currency (without the ledger's contribution the run would not
##   have crossed the threshold), guarded by MATERIALITY (tiny scratches don't
##   count) and RECENCY (a default RECENT_WINDOW+ turns before death is history,
##   not cause -- rep/doom are absorbing-boundary walks; but-for at the margin is
##   fragile without a proximity guard).
const REP_MATERIALITY := 5.0   # min total ledger rep damage (starting rep is 50)
const DOOM_MATERIALITY := 1.0  # min total ledger doom contribution
const RECENT_WINDOW := 15      # turns before death within which a ledger cause is proximate

## cause_log kinds that are ledger-inflicted damage (vs cascade watermarks like
## rep_collapse / funding_starvation, which mark the chain but aren't damage).
const LEDGER_KINDS := [
	"ledger_default",            # unpaid money bill -> doom + rep conversion
	"ledger_governance_deficit", # governance below zero -> doom conversion
	"ledger_doom_bill",          # doom-currency entry billed
	"ledger_rep_bill",           # reputation-currency entry billed
	"ledger_exposure",           # secret entry exposed -> rep + governance damage
]


static func surface_cause(state) -> String:
	"""Which counter ended the run (mirrors GameState.check_win_lose order)."""
	if state.victory:
		return "win"
	if not state.game_over:
		return "none"
	if state.doom >= 99.9:
		return "doom"
	if state.reputation <= 0.0:
		return "rep"
	return "other"


static func classify(state) -> Dictionary:
	"""Attribute a finished run's death to its root cause.
	Returns {surface: String, root_cause: String, chain: Array[String]} where
	root_cause is one of: ledger | doom | rep | win | other | none, and chain is
	the human-readable turn-stamped causal trail (empty when no causes logged)."""
	var surface := surface_cause(state)
	var root := surface

	# Aggregate ledger-inflicted damage from the contributing-cause trail.
	var ledger_rep := 0.0    # rep damage (positive magnitude)
	var ledger_doom := 0.0   # doom contribution
	var last_ledger_turn := -1
	for c in state.cause_log:
		if str(c.get("kind", "")) in LEDGER_KINDS:
			var fx: Dictionary = c.get("effects", {})
			ledger_rep += -float(fx.get("reputation", 0.0))
			ledger_doom += float(fx.get("doom", 0.0))
			last_ledger_turn = max(last_ledger_turn, int(c.get("turn", -1)))
	var proximate: bool = last_ledger_turn >= 0 and (int(state.turn) - last_ledger_turn) <= RECENT_WINDOW

	match surface:
		"doom":
			# Necessity: without the ledger's doom contribution the run stays under 100.
			# (state.doom is clamped at 100, which makes this test conservative.)
			if ledger_doom >= DOOM_MATERIALITY and (state.doom - ledger_doom) < 100.0 and proximate:
				root = "ledger"
		"rep":
			# Rep floors at 0, so counterfactual rep ~= total ledger rep damage:
			# material recent ledger damage means the run dies of the cascade.
			if ledger_rep >= REP_MATERIALITY and proximate:
				root = "ledger"
		"other":
			# No doom/rep threshold crossed but the run is over with billed damage
			# attributed -- the ledger is the only remaining candidate.
			if state.ledger and (state.ledger.death_attribution as Array).size() > 0:
				root = "ledger"

	var split: Dictionary = chain_split(state)
	return {
		"surface": surface,
		"root_cause": root,
		# UNFILTERED, unchanged: the manual sweep drivers read this.
		"chain": chain_summary(state),
		# Recency-split, for any surface that shows a player a CAUSE (#1248).
		"chain_proximate": split["proximate"],
		"chain_earlier": split["earlier"],
	}


## One cause entry as its display line. Extracted so chain_summary() and
## chain_split() cannot drift into formatting the same event two ways.
static func _cause_line(c: Dictionary) -> String:
	var fx: Dictionary = c.get("effects", {})
	var parts: Array = []
	for key in fx.keys():
		# *_level / *_due keys are watermark LEVELS, not deltas -- print without a sign.
		var k := str(key)
		if k.ends_with("_level") or k.ends_with("_due"):
			parts.append("%s %.1f" % [_short_key(k), float(fx[key])])
		else:
			parts.append("%s %+.1f" % [_short_key(k), float(fx[key])])
	var fx_txt := (" (%s)" % ", ".join(parts)) if parts.size() > 0 else ""
	return "t%d %s %s%s" % [int(c.get("turn", -1)), str(c.get("kind", "?")), str(c.get("source", "?")), fx_txt]


## Split the causal trail into what is PROXIMATE to the death and what is history.
##
## WHY (issue #1248). The game-over screen printed the WHOLE cause_log under the
## heading CAUSE OF DEATH. In a run that ended on turn 130 that meant showing:
##
##     t80 funding_starvation payroll (cash@ 248.0, bills 670.3)
##     t87 rep_collapse reputation (rep@ 5.0)
##
## The player finished that run with $1,189,765. They did not die of the t80 cash
## crisis; they SURVIVED it and recovered by three orders of magnitude. The screen
## told them something false about their own run, at the exact moment they were
## looking for an explanation.
##
## Both guards to prevent that already existed in this file and neither was
## reachable from the panel: RECENT_WINDOW ("a default RECENT_WINDOW+ turns before
## death is history, not cause") and the fact that funding_starvation and
## rep_collapse are cascade WATERMARKS, explicitly "not damage". classify() used
## RECENT_WINDOW for its own ledger verdict; chain_summary() never did.
##
## funding_starvation makes it worse: it is one-shot-per-episode and RESETS on
## recovery (turn_manager.gd), but the cause_log entry it wrote is permanent.
## Recovering from a cash crisis clears the flag and leaves the tombstone.
##
## Returns {proximate: Array, earlier: Array}, both oldest-first. `proximate` is
## what may honestly sit under CAUSE OF DEATH; `earlier` is the run's history and
## belongs under its own heading. Neither is dropped -- the t80/t87 trail IS
## interesting, it is just not the cause.
static func chain_split(state) -> Dictionary:
	var proximate: Array = []
	var earlier: Array = []
	var death_turn := int(state.turn)
	for c in state.cause_log:
		var turn := int(c.get("turn", -1))
		# turn < 0 means the cause carries no turn stamp. Treat it as proximate:
		# an unstamped cause cannot be shown to be old, and quietly demoting it to
		# history would hide a real one.
		var is_recent: bool = turn < 0 or (death_turn - turn) <= RECENT_WINDOW
		if is_recent:
			proximate.append(_cause_line(c))
		else:
			earlier.append(_cause_line(c))
	return {"proximate": proximate, "earlier": earlier}


static func chain_summary(state, max_entries: int = 8) -> Array:
	"""Compact turn-stamped causal trail for reports, oldest first, e.g.
	't3 ledger_exposure payroll_coinflip (rep -32.1, gov -4711)'. Truncates the
	middle when the log is long -- first and last causes carry the chain.

	UNFILTERED on purpose: the manual sweep drivers (tests/manual/) analyse whole
	runs and want every cause. The game-over PANEL uses chain_split() instead --
	see #1248."""
	var lines: Array = []
	for c in state.cause_log:
		lines.append(_cause_line(c))
	if lines.size() > max_entries:
		var head := lines.slice(0, max_entries - 3)
		var tail := lines.slice(lines.size() - 2)
		head.append("... (%d more causes)" % (lines.size() - max_entries + 1))
		head.append_array(tail)
		lines = head
	return lines


static func _short_key(key: String) -> String:
	match key:
		"reputation": return "rep"
		"governance": return "gov"
		"money_shortfall": return "short$"
		"governance_deficit": return "gov_deficit"
		"reputation_level": return "rep@"
		"cash_level": return "cash@"
		"bills_due": return "bills"
		_: return key

extends RefCounted
class_name DevModeReadout
## Pure, unit-testable builder for the DEV MODE overlay's on-screen INFO readout.
##
## It mirrors, on-screen, everything the verbose PowerShell logs dump -- the full game
## state -- so the owner can answer "why did that happen" without reading logs. Kept as a
## static builder (no UI, no side effects) so it can be tested against a bare
## `GameState.new()` and so the overlay stays a thin renderer over this data.
##
## Contract: `build_sections(state)` returns an Array of
##   { "title": String, "lines": Array[String] }
## Every accessor is null-guarded so a partially-initialised or null state degrades to a
## readable placeholder rather than crashing the overlay.

## Build the full readout as an ordered list of titled sections.
## `state` is a live `GameState` (from `GameManager.state`), or null before a game starts.
static func build_sections(state) -> Array:
	if state == null:
		return [{"title": "No active game", "lines": ["GameManager.state is null -- start a game to see state."]}]

	var sections: Array = []
	sections.append(_resources_section(state))
	sections.append(_doom_section(state))
	sections.append(_doom_sources_section(state))
	sections.append(_risk_section(state))
	sections.append(_rivals_section(state))
	sections.append(_ledger_section(state))
	sections.append(_meta_section(state))
	return sections

static func _fnum(v) -> String:
	# Compact numeric formatting: integers stay clean, floats show one decimal.
	if typeof(v) == TYPE_INT:
		return str(v)
	return "%.1f" % float(v)

static func _resources_section(state) -> Dictionary:
	var lines: Array = []
	lines.append("Money:      $%s" % _fnum(state.money))
	lines.append("Compute:    %s" % _fnum(state.compute))
	lines.append("Research:   %s" % _fnum(state.research))
	lines.append("Papers:     %s" % _fnum(state.papers))
	lines.append("Reputation: %s" % _fnum(state.reputation))
	lines.append("Governance: %s" % _fnum(state.governance))
	lines.append("Stationery: %s" % _fnum(state.stationery))
	lines.append("Tech debt:  %s" % _fnum(state.technical_debt))
	var avail := 0
	var reserved := int(state.reserved_ap)
	var committed := int(state.committed_ap)
	if state.has_method("get_available_ap"):
		avail = int(state.get_available_ap())
	lines.append("AP: %d total | %d avail | %d committed | %d reserved" % [
		int(state.action_points), avail, committed, reserved
	])
	return {"title": "Resources", "lines": lines}

static func _doom_section(state) -> Dictionary:
	var lines: Array = []
	var ds = state.doom_system
	if ds == null:
		lines.append("doom: %s (doom_system null)" % _fnum(state.doom))
		return {"title": "Doom", "lines": lines}
	lines.append("Doom value: %s / 100" % _fnum(ds.current_doom))
	lines.append("Velocity:   %s" % _fnum(ds.doom_velocity))
	lines.append("Momentum:   %s" % _fnum(ds.doom_momentum))
	if ds.has_method("_get_doom_trend"):
		lines.append("Trend:      %s" % str(ds._get_doom_trend()))
	if ds.has_method("get_doom_status"):
		lines.append("Status:     %s" % str(ds.get_doom_status()))
	if ds.has_method("get_momentum_description"):
		lines.append("Momentum:   %s" % str(ds.get_momentum_description()))
	return {"title": "Doom", "lines": lines}

static func _doom_sources_section(state) -> Dictionary:
	var lines: Array = []
	var ds = state.doom_system
	if ds == null or ds.doom_sources == null:
		lines.append("(no doom_sources)")
		return {"title": "Doom sources (per-source breakdown)", "lines": lines}
	var srcs: Dictionary = ds.doom_sources
	# Sort by magnitude so the biggest contributor reads first, like the log dump.
	var keys := srcs.keys()
	keys.sort_custom(func(a, b): return abs(float(srcs[a])) > abs(float(srcs[b])))
	for k in keys:
		lines.append("%-16s %+.2f" % [str(k) + ":", float(srcs[k])])
	if lines.is_empty():
		lines.append("(all sources zero)")
	return {"title": "Doom sources (per-source breakdown)", "lines": lines}

static func _risk_section(state) -> Dictionary:
	var lines: Array = []
	var rs = state.risk_system
	if rs == null or rs.pools == null:
		lines.append("(risk_system null)")
		return {"title": "Risk pools", "lines": lines}
	var pools: Dictionary = rs.pools
	for name in pools.keys():
		var val := float(pools[name])
		var status := ""
		if rs.has_method("get_pool_status"):
			status = " [%s]" % str(rs.get_pool_status(name))
		lines.append("%-22s %5.1f / 100%s" % [str(name) + ":", val, status])
	if rs.has_method("get_total_risk"):
		lines.append("total: %s" % _fnum(rs.get_total_risk()))
	return {"title": "Risk pools", "lines": lines}

static func _rivals_section(state) -> Dictionary:
	var lines: Array = []
	var rivals = state.rival_labs
	if rivals == null or (rivals is Array and rivals.is_empty()):
		lines.append("(no rival labs)")
		return {"title": "Rival labs", "lines": lines}
	for lab in rivals:
		if lab == null:
			continue
		lines.append("%s" % str(lab.name))
		lines.append("   money $%s | rep %s | safety %s | cap %s" % [
			_fnum(lab.funding), _fnum(lab.reputation),
			_fnum(lab.safety_progress), _fnum(lab.capability_progress)
		])
	return {"title": "Rival labs", "lines": lines}

static func _ledger_section(state) -> Dictionary:
	var lines: Array = []
	var ledger = state.ledger
	if ledger == null or ledger.entries == null:
		lines.append("(no ledger)")
		return {"title": "Ledger (incl. secret entries)", "lines": lines}
	var entries: Array = ledger.entries
	if entries.is_empty():
		lines.append("(no entries)")
		return {"title": "Ledger (incl. secret entries)", "lines": lines}
	for e in entries:
		if e == null:
			continue
		var side_str := "PAY"
		if e.side == Ledger.Side.RECEIVABLE:
			side_str = "RECV"
		var flags := ""
		if e.secret:
			flags += " SECRET"
		if e.settled:
			flags += " settled"
		var cp := ""
		if String(e.counterparty) != "":
			cp = " <-> %s" % str(e.counterparty)
		lines.append("%s %s  %s %s  principal=%s fuse=%d int=%s%s%s" % [
			side_str, str(e.source), str(e.currency), "",
			_fnum(e.principal), int(e.fuse), _fnum(e.interest), cp, flags
		])
	# Death attribution -- what actually killed the run, if recorded.
	if ledger.death_attribution != null and ledger.death_attribution is Array and not ledger.death_attribution.is_empty():
		lines.append("-- death attribution --")
		for a in ledger.death_attribution:
			lines.append("   %s" % str(a))
	return {"title": "Ledger (incl. secret entries)", "lines": lines}

static func _meta_section(state) -> Dictionary:
	var lines: Array = []
	lines.append("Seed: %s" % str(state.game_seed_str))
	if state.rng != null:
		lines.append("RNG seed=%d state=%d" % [int(state.rng.seed), int(state.rng.state)])
	lines.append("Turn: %d" % int(state.turn))
	if state.has_method("get_turn_display"):
		lines.append("Calendar: %s" % str(state.get_turn_display()))
	# Verification hash lives on the VerificationTracker autoload.
	if is_instance_valid(VerificationTracker):
		if VerificationTracker.has_method("get_hash_prefix"):
			lines.append("Verify hash: %s" % str(VerificationTracker.get_hash_prefix(16)))
		else:
			lines.append("Verify hash: %s" % str(VerificationTracker.verification_hash))
	lines.append("Build: %s" % BuildInfo.get_stamp())
	return {"title": "Meta (seed / verify / build)", "lines": lines}

extends Node
class_name DoomSystem
## ADR-0015 doom engine: doom is an ACCUMULATING RATE computed each day tick from a sum
## of NAMED STREAMS, each stream fed by a world-state intermediary (DQ-21). No action or
## event writes doom directly — they write intermediaries; the doom function reads them.
##
## The nine intermediary concepts (DQ-21, round-4 rulings):
##   general_capability  -> diffusion stream (chronic floor; ratchet)
##   frontier_capability -> overhang stream  (acute hazard = frontier - safety_absorption)
##   global_compute      -> (no own stream; feeds dedicated_ai_compute / diffusion pace)
##   dedicated_ai_compute-> compute stream    (the controllable fleet)
##   ambient_risk        -> baseline stream   (year-keyed background trend)
##   political_pressure  -> (gate-only; no stream — gates typed dampers)
##   global_alarm        -> alarm stream      (small NEGATIVE relief) AND damper gate
##   global_panic        -> panic stream      (social accelerant)
##   scheduled pulses    -> pulse:* streams   (ramp/spike/tail envelopes, ADR-0005)
## plus typed dampers (targeted, durationed reductions on specific streams) and a gated
## momentum modifier on the sum. doom_rate = sum(streams); doom_level += rate * dt.
##
## Single-authority discipline (calibration #638): ONLY this system writes state.doom. The
## ledger's bills and risk shocks arrive as STREAM INPUTS (add_stream_input), folded into the
## rate on the next resolve — never a parallel write to the level.
##
## Legibility (ADR-0015 §3 / L6 EE-8): every stream is named, so the delta chip / death
## attribution can say which stream (and the intermediary behind it) is killing or saving you.
## The "wiggly stock-market lines" are the emergent interference of legible streams, never noise.

# ============================================================================
# CORE STATE — the two instruments (DQ-21 display ruling)
# ============================================================================

## The accumulated doom LEVEL (structural-dread surface; its crossing date is the badge).
var current_doom: float = 50.0

## The most recent doom RATE (delta-doom; the high-frequency feedback surface).
var doom_rate: float = 0.0

## Per-tick history of the rate — feeds the N=6-month trend telemetry invariant (DQ-21 R2-Q7).
var rate_history: Array[float] = []

# ============================================================================
# STREAMS — doom_rate = sum of these named streams (superposition; MAY be negative)
# ============================================================================
## Kept under the historical name `doom_sources` so existing consumers (dev overlays, the
## sweep's doom_src_at_death readout, GameState's technical_debt coupling) keep working; the
## KEYS are now the ADR-0015 stream vocabulary.
var doom_sources: Dictionary = {
	"baseline": 0.0,       # ambient_risk — year-keyed background floor
	"overhang": 0.0,       # frontier_capability - safety_absorption (acute)
	"diffusion": 0.0,      # general_capability (chronic floor)
	"compute": 0.0,        # dedicated_ai_compute pressure
	"panic": 0.0,          # global_panic (social accelerant)
	"alarm": 0.0,          # -global_alarm (small standing relief)
	"ledger": 0.0,         # routed ledger-bill stream input (ADR-0003 teeth)
	"technical_debt": 0.0, # GameState tech-debt coupling (migrated from a direct write)
	"momentum": 0.0,       # gated trend modifier on the sum (not an intermediary)
}

## Buffered STREAM INPUTS from off-tick sources (ledger bills, risk shocks). Added via
## add_stream_input()/add_event_doom() during the turn, folded into the streams on the next
## calculate_doom_change(), then cleared — so nothing writes the LEVEL in parallel (#638).
var _pending_stream_inputs: Dictionary = {}

## Rival overhang contribution stashed by turn_manager. LEGACY SHIM RETIRED (ADR-0015): rivals
## now raise frontier_capability[actor] and the overhang stream converts it; this field is kept
## only as a harmless no-op sink so any un-migrated caller cannot crash. Always 0 in the new path.
var _pending_rival_doom: float = 0.0

# ============================================================================
# MOMENTUM — a stream-level trend modifier, gated behind a Balance switch (#638)
# ============================================================================
var doom_velocity: float = 0.0
var doom_momentum: float = 0.0
var momentum_accumulation_rate: float = 0.15
var momentum_decay_rate: float = 0.92
var momentum_cap: float = 8.0

# Multipliers/modifiers retained as an extension point (unused by the stream model in v1).
var doom_multipliers: Dictionary = {}
var doom_modifiers: Dictionary = {}

# ============================================================================
# TREND TELEMETRY (DQ-21 R2-Q7, N=6) — instrumentation, NEVER a clamp
# ============================================================================
const TREND_MONTHS := 6
const TICKS_PER_MONTH := 22       # approx workday ticks / fiction month (ADR-0009)
var trend_flag_active: bool = false
var _last_trend_flag_tick: int = -1

func _init() -> void:
	momentum_accumulation_rate = Balance.num("doom.momentum_accumulation_rate", momentum_accumulation_rate)
	momentum_decay_rate = Balance.num("doom.momentum_decay_rate", momentum_decay_rate)
	momentum_cap = Balance.num("doom.momentum_cap", momentum_cap)

# ============================================================================
# STREAM COEFFICIENTS — the freely-tuned Balance layer (doom.streams.*).
# The FUNCTION is structure (ADR-0015 §4); these NUMBERS are priced by the sweep.
# ============================================================================
func _w(key: String, fallback: float) -> float:
	return Balance.num("doom.streams." + key, fallback)

# ============================================================================
# CORE: doom_rate = sum of named streams, computed each day tick
# ============================================================================

func calculate_doom_change(state: GameState) -> Dictionary:
	"""ADR-0015 day tick: advance the world-state intermediaries, recompute every named
	stream from them, sum to the rate, integrate into the level. Returns a breakdown dict
	(same shape the message builder + sweep expect)."""

	# (0) Advance the hazard-state intermediaries this tick (flow -> stock). This is the
	#     ONLY place capability/absorption/social stocks tick; effects elsewhere seed them.
	_advance_intermediaries(state)

	# (1) Recompute streams from the intermediaries.
	var streams := _compute_streams(state)

	# (2) Fold in buffered off-tick stream inputs (ledger bills, risk shocks) — routed, not
	#     parallel-written. Attributed to their own named streams so L6 can see them.
	for key in _pending_stream_inputs.keys():
		streams[key] = float(streams.get(key, 0.0)) + float(_pending_stream_inputs[key])
	_pending_stream_inputs.clear()

	# (3) GameState tech-debt coupling: migrated from a direct doom write to a named stream
	#     (Legacy #13). GameState writes doom_sources["technical_debt"]; carry it forward.
	streams["technical_debt"] = float(doom_sources.get("technical_debt", 0.0))

	# (4) Raw rate = superposition of hazard/relief streams (MAY be negative).
	var raw_rate := 0.0
	for key in streams.keys():
		raw_rate += float(streams[key])

	# (5) Momentum — a gated trend modifier ON TOP of the raw rate (#638 switch semantics:
	#     the accumulator keeps ticking while disabled; only the contribution is zeroed).
	var momentum_contribution := _calculate_momentum(raw_rate)
	momentum_contribution *= Balance.num("doom.momentum_weight", 1.0)
	if Balance.num("doom.momentum_enabled", 1.0) < 0.5:
		momentum_contribution = 0.0
	streams["momentum"] = momentum_contribution

	var total_rate := raw_rate + momentum_contribution

	# (6) Integrate: the LEVEL accumulates the RATE. May FALL on net-negative ticks (legal —
	#     "pulled something impressive off"). Clamp 0..100 is a display/lethality bound.
	#     Snap the persisted scalars to the binary-exact grid (SAVE_QUANTUM) so save/load is
	#     LOSSLESS (the "next turn identical" replay must match bit-for-bit — see SAVE_QUANTUM).
	doom_rate = _snap(total_rate)
	current_doom = _snap(clamp(current_doom + total_rate, 0.0, 100.0))
	doom_velocity = _snap(doom_velocity)
	doom_momentum = _snap(doom_momentum)

	# (7) Publish the streams for L6 chips / dev overlay / sweep, and run the trend invariant.
	doom_sources = streams
	rate_history.append(doom_rate)
	_check_trend_invariant(state, streams)

	return {
		"total_change": total_rate,
		"raw_change": raw_rate,
		"momentum": momentum_contribution,
		"velocity": doom_velocity,
		"sources": streams.duplicate(),
		"streams": streams.duplicate(),
		"new_doom": current_doom,
		"rate": total_rate,
		"level": current_doom,
		"trend": _get_doom_trend(),
	}

# ============================================================================
# INTERMEDIARY ADVANCEMENT (flow -> stock) — the ratchet dynamics
# ============================================================================

func _advance_intermediaries(state: GameState) -> void:
	"""Advance the stored world-state intermediaries one day tick. Rivals already accumulate
	their own capability_progress (read directly as their frontier slice); here we advance the
	PLAYER frontier, the safety_absorption stock, the diffusion floor, and decay the social
	stocks. All magnitudes are Balance-priced (doom.streams.*)."""
	if state == null:
		return

	# --- Player frontier + safety absorption + alarm, from the PRODUCTIVE researcher roster.
	# Reuse the engine's productive-count discipline (managed AND compute-fed researchers work).
	var cap_gain := _w("cap_frontier_gain", 0.9)          # frontier per productive capability researcher / tick
	var absorb_gain := _w("safety_absorb_gain", 1.15)     # absorption per productive safety researcher / tick
	var alarm_gain := _w("alarm_gain", 0.14)              # global_alarm per productive safety researcher / tick

	var cap_workers := 0
	var safety_workers := 0
	if state.researchers.is_empty():
		# Legacy count fallback (pre-researcher-object sweeps / L2): proportion the productive
		# staff by specialization count.
		var mgmt := int(state.get_management_capacity())
		var avail := int(state.compute)
		var total := state.safety_researchers + state.capability_researchers + state.compute_engineers
		var prod: int = min(min(total, mgmt), avail)
		if total > 0:
			cap_workers = int(round(prod * float(state.capability_researchers) / float(total)))
			safety_workers = int(round(prod * float(state.safety_researchers) / float(total)))
	else:
		for r in _productive_researchers(state):
			match r.specialization:
				"capabilities":
					cap_workers += 1
				"safety", "interpretability", "alignment":
					safety_workers += 1

	var pf: float = float(state.frontier_capability.get("player", 0.0))
	pf += cap_workers * cap_gain
	state.frontier_capability["player"] = pf
	state.safety_absorption += safety_workers * absorb_gain
	state.global_alarm += safety_workers * alarm_gain

	# --- Rival frontier slices (read their accumulating capability_progress) + diffusion.
	var rival_frontier_sum := 0.0
	for rival in state.rival_labs:
		state.frontier_capability[rival.id] = rival.capability_progress
		rival_frontier_sum += rival.capability_progress
	# Diffusion floor: today's frontier becomes tomorrow's commodity, slowly (ratchet).
	state.general_capability += _w("diffusion_gain", 0.00006) * rival_frontier_sum

	# --- Dedicated compute: the controllable fleet (player + rivals). Cheap proxy in v1.
	state.dedicated_ai_compute = float(state.compute)

	# --- Ambient risk baseline: year-keyed later; v1 = the re-denominated base floor.
	state.ambient_risk = Balance.num("doom.base_per_turn", 0.06)

	# --- Social stocks decay toward zero (habituation): alarm and panic both fade if unfed.
	state.global_alarm *= _w("alarm_decay", 0.985)
	state.global_panic *= _w("panic_decay", 0.97)

	# --- Snap every persisted intermediary to the binary-exact grid (SAVE_QUANTUM). The decay
	#     multiplies produce arbitrary-precision doubles that fail Godot's JSON parse round-trip
	#     (§7.2); keeping the stocks on a power-of-two grid makes save/load LOSSLESS (the
	#     "next turn identical" replay must match bit-for-bit). Gameplay-invisible (grid ~1e-6).
	state.frontier_capability["player"] = _snap(float(state.frontier_capability["player"]))
	state.safety_absorption = _snap(state.safety_absorption)
	state.general_capability = _snap(state.general_capability)
	state.dedicated_ai_compute = _snap(state.dedicated_ai_compute)
	state.ambient_risk = _snap(state.ambient_risk)
	state.global_alarm = _snap(state.global_alarm)
	state.global_panic = _snap(state.global_panic)

	# --- political_pressure tracks the alarm/panic balance (signed disposition; gate only).
	state.political_pressure = _snap(state.global_alarm - state.global_panic)

func _compute_streams(state: GameState) -> Dictionary:
	"""Read the intermediaries and produce the named hazard/relief streams (all Balance-priced).
	Hazard streams clamp at >= 0 in v1 (DQ-21 R2-Q9 — LOUD REVISIT MARKER below); the alarm
	stream is natively NEGATIVE by design and is deliberately exempt from the clamp — that
	clamp/negative-component boundary is the exact unsettled ground R2-Q9 flagged for revisit."""
	var s := {}

	# (a) baseline — ambient_risk, the always-there floor.
	s["baseline"] = state.ambient_risk

	# (b) overhang — the ACUTE hazard: frontier not matched by safety absorption. Scalar the
	#     doom function reads is max over actors (DQ-21 §1.2).
	var frontier_max := 0.0
	for actor in state.frontier_capability.keys():
		frontier_max = maxf(frontier_max, float(state.frontier_capability[actor]))
	# vvv R2-Q9 v1 CLAMP (LOUD REVISIT MARKER — streams clamp at 0 in v1; NOT SETTLED) vvv
	s["overhang"] = _w("W_frontier", 0.000145) * maxf(0.0, frontier_max - state.safety_absorption)
	# ^^^ revisit together with the natively-negative alarm stream (DQ-21 R2-Q9) ^^^

	# (c) diffusion — chronic floor from general_capability.
	s["diffusion"] = _w("W_general", 0.02) * state.general_capability

	# (d) compute — dedicated_ai_compute fuel term (small in v1; the ocean has no own term).
	s["compute"] = _w("W_compute", 0.0) * state.dedicated_ai_compute

	# (e) panic — additive social accelerant.
	s["panic"] = _w("W_panic", 0.02) * state.global_panic

	# (f) alarm — small direct NEGATIVE relief (a genuinely alarmed world is slightly safer even
	#     before formal governance lands). Small by design; heavy lifting is in dampers.
	s["alarm"] = -_w("W_alarm", 0.02) * state.global_alarm

	# (g) scheduled pulses — ADR-0005 schedule entries inject time-shaped rate bumps. v1 ships
	#     no pulse content; the hook is wired so the schema addition (R2-Q6) has a landing site.
	for pulse in _active_pulses(state):
		s["pulse:" + str(pulse.get("id", "?"))] = float(pulse.get("rate", 0.0))

	# --- TYPED DAMPERS — targeted, durationed reductions on SPECIFIC streams, gated by
	#     alarm/political_pressure (DQ-21 §2). v1 clamps a damped hazard stream at >= 0.
	for d in _active_dampers(state):
		var tgt := str(d.get("target", ""))
		if s.has(tgt):
			s[tgt] = maxf(0.0, float(s[tgt]) - float(d.get("strength", 0.0)))

	return s

# ============================================================================
# SCHEDULED PULSES + TYPED DAMPERS (v1 hooks; content lands in later lanes)
# ============================================================================

func _active_pulses(state: GameState) -> Array:
	"""ADR-0005 schedule entries with a pulse envelope active at the current tick. v1: none
	(R2-Q5 ships no cyclic machinery); the read is here so content/schedule can populate it."""
	if state != null and "doom_pulses" in state and state.doom_pulses is Array:
		return state.doom_pulses
	return []

func _active_dampers(state: GameState) -> Array:
	"""Typed dampers currently in force (target_stream, strength, expires_turn). Granted by
	completed workstreams / adopted safety work / governance wins, gated by alarm/pressure."""
	if state == null or not ("doom_dampers" in state) or not (state.doom_dampers is Array):
		return []
	var live: Array = []
	for d in state.doom_dampers:
		if int(d.get("expires_turn", 0)) >= int(state.turn):
			live.append(d)
	return live

# ============================================================================
# STREAM INPUTS (ledger bills, risk shocks) — routed, not parallel-written
# ============================================================================

func add_stream_input(stream: String, amount: float) -> void:
	"""Buffer an off-tick contribution to a NAMED stream (ledger bill, risk shock). Folded into
	the rate on the next calculate_doom_change() and attributed to `stream` — never a direct
	write to the level (single-authority discipline, #638 / ADR-0015)."""
	_pending_stream_inputs[stream] = float(_pending_stream_inputs.get(stream, 0.0)) + amount

func add_event_doom(amount: float, reason: String = "") -> void:
	"""Back-compat shim for the ledger/risk callers. Routes to a named stream input instead of
	the old `current_doom += amount` parallel write. Ledger bills -> `ledger` stream; risk
	shocks -> a `panic`-flavored stream (a shock the world reacts to). Attribution preserved."""
	var stream := "ledger"
	if reason.begins_with("risk"):
		stream = "panic"
	add_stream_input(stream, amount)

func set_rival_doom_contribution(_amount: float) -> void:
	"""RETIRED (ADR-0015): rivals now raise frontier_capability and the overhang stream converts
	it — there is no per-tick rival doom literal. Kept as a no-op sink so an un-migrated caller
	cannot crash; the value is ignored."""
	_pending_rival_doom = 0.0

# ============================================================================
# MOMENTUM (gated trend modifier)
# ============================================================================

func _calculate_momentum(raw_doom_change: float) -> float:
	doom_velocity = doom_velocity * Balance.num("doom.velocity_carry", 0.7) \
		+ raw_doom_change * Balance.num("doom.velocity_gain", 0.3)
	doom_momentum += raw_doom_change * momentum_accumulation_rate
	doom_momentum = clamp(doom_momentum, -momentum_cap, momentum_cap)
	doom_momentum *= momentum_decay_rate
	return doom_momentum

# ============================================================================
# TREND TELEMETRY INVARIANT (DQ-21 R2-Q7, N=6) — LOUD FLAG, never a clamp
# ============================================================================

func _check_trend_invariant(state: GameState, streams: Dictionary) -> void:
	"""Flag (debug + telemetry) a SUSTAINED 6-month negative rate trend without a
	sacred-object-grade cause. Single negative ticks are legal and unflagged. This NEVER
	clamps the rate — a bot policy that sustains this state is an exploit-sweep gate failure."""
	var window := TREND_MONTHS * TICKS_PER_MONTH
	if rate_history.size() < window:
		trend_flag_active = false
		return
	var trend := 0.0
	for i in range(rate_history.size() - window, rate_history.size()):
		trend += rate_history[i]
	if trend < 0.0 and not _sacred_grade_cause_in_window(state, window):
		trend_flag_active = true
		if _last_trend_flag_tick != int(state.turn):
			_last_trend_flag_tick = int(state.turn)
			# Telemetry/debug LOG line (NOT push_warning): the invariant is an instrument, and
			# a sustained decline is LEGAL play (only the exploit sweep gates on it). push_warning
			# would surface this legal state as an engine fault (and GUT flags any pushed warning
			# during a sim as a test failure); a tagged print keeps it loud in logs + telemetry.
			print("[DOOM_TREND_INVARIANT] sustained %d-month negative doom trend (%.2f) without a sacred-object-grade cause at turn %d — streams=%s" % [
				TREND_MONTHS, trend, int(state.turn), str(streams)])
	else:
		trend_flag_active = false

func _sacred_grade_cause_in_window(state: GameState, window: int) -> bool:
	"""A sacred-object-grade cause = a completed gauntlet chain / sacrifice payment logged
	recently (DQ-21 §2b). v1 has no such content wired, so this is always false; the hook is
	here so the invariant is correct the moment sacred-chain content lands."""
	if state == null or not ("sacred_chain_log" in state):
		return false
	for entry in state.sacred_chain_log:
		if int(state.turn) - int(entry.get("turn", -9999)) <= window:
			return true
	return false

# ============================================================================
# PER-STREAM API (F3 overlay data wiring + two-instrument readouts, DQ-21 display)
# ============================================================================

func get_doom_rate() -> float:
	"""Instrument (a): the delta-doom RATE — rises/falls with player outputs."""
	return doom_rate

func get_doom_level() -> float:
	"""Instrument (b): the accumulated doom LEVEL — the badge is its crossing date."""
	return current_doom

func get_stream_contributions() -> Dictionary:
	"""F3 overlay data: the per-stream breakdown of the most recent rate (named streams ->
	signed contributions). The 'wiggle' decomposed into legible components."""
	return doom_sources.duplicate()

func get_dominant_stream() -> String:
	"""The single stream contributing the most (by magnitude) to the current rate — the chip
	the delta-doom display would surface on a click."""
	var best := ""
	var best_mag := 0.0
	for k in doom_sources.keys():
		var m: float = abs(float(doom_sources[k]))
		if m > best_mag:
			best_mag = m
			best = k
	return best

# ============================================================================
# HELPERS
# ============================================================================

func _productive_researchers(state: GameState) -> Array:
	"""Researchers that actually work this tick: managed AND compute-fed, in roster order
	(mirrors _step_researcher_productivity's discipline so the intermediary advance matches
	the productivity the rest of the engine sees)."""
	var out: Array = []
	if state.researchers.is_empty():
		return out
	var management_capacity := int(state.get_management_capacity())
	var available_compute := int(state.compute)
	var idx := 0
	for r in state.researchers:
		if idx >= management_capacity:
			break
		if available_compute <= 0:
			break
		available_compute -= 1
		out.append(r)
		idx += 1
	return out

func _reset_doom_sources() -> void:
	for key in doom_sources.keys():
		doom_sources[key] = 0.0

func _get_doom_trend() -> String:
	if doom_velocity < -2.0:
		return "strongly_decreasing"
	elif doom_velocity < -0.5:
		return "decreasing"
	elif doom_velocity < 0.5:
		return "stable"
	elif doom_velocity < 2.0:
		return "increasing"
	else:
		return "strongly_increasing"

func get_doom_status() -> String:
	"""Doom tier id — ThemeManager's canonical band label, lowercased (display-only)."""
	return ThemeManager.get_doom_status_label(current_doom).to_lower()

func get_momentum_description() -> String:
	if abs(doom_momentum) < 0.5:
		return "neutral"
	elif doom_momentum > 0:
		return "doom spiral (%.1f)" % doom_momentum
	else:
		return "safety flywheel (%.1f)" % abs(doom_momentum)

# Extension points retained for compatibility with callers that poke modifiers.
func apply_doom_modifier(source: String, modifier: float) -> void:
	if doom_modifiers.has(source):
		doom_modifiers[source] += modifier

func set_doom_multiplier(source: String, multiplier: float) -> void:
	if doom_multipliers.has(source):
		doom_multipliers[source] = multiplier

# ============================================================================
# SERIALIZATION (save/load)
# ============================================================================

## Doom-adjacent float quantum — a BINARY-EXACT grid (2^-20 ≈ 9.5e-7). Godot's JSON parse
## is not correctly-rounded (L1 calibration §7.2): a full-precision double can come back
## from a save 1 ulp off, breaking save/load deep-equality. The fix is to keep every
## doom-adjacent LIVE value on a power-of-two grid: snappedf(v, 2^-20) yields N·2^-20, which
## is an exactly-representable double whose decimal string round-trips through Godot's parser
## intact (0.25 survives, 0.008 does not — §7.2). A decimal quantum (1e-6) does NOT work: it
## sits between representable doubles, so a 1-ulp parse drift can cross a snap boundary and
## AMPLIFY into a full-quantum divergence. The grid is far below any gameplay scale (doom
## deaths at 100, streams ~0.01–10), so the live dynamics are unaffected (sweep-verified).
const SAVE_QUANTUM := 1.0 / 1048576.0  # == 2^-20, binary-exact (computed so the const is precise)

static func _snap(v: float) -> float:
	return snappedf(v, SAVE_QUANTUM)

static func _snap_dict(d: Dictionary) -> Dictionary:
	var out := {}
	for k in d.keys():
		out[k] = snappedf(float(d[k]), SAVE_QUANTUM)
	return out

func to_dict() -> Dictionary:
	var hist: Array = []
	for v in rate_history:
		hist.append(_snap(v))
	return {
		"current_doom": _snap(current_doom),
		"doom_rate": _snap(doom_rate),
		"doom_velocity": _snap(doom_velocity),
		"doom_momentum": _snap(doom_momentum),
		"pending_rival_doom": _snap(_pending_rival_doom),
		"pending_stream_inputs": _snap_dict(_pending_stream_inputs),
		"doom_sources": _snap_dict(doom_sources),
		"rate_history": hist,
	}

func from_dict(data: Dictionary) -> void:
	current_doom = _snap(float(data.get("current_doom", 50.0)))
	doom_rate = _snap(float(data.get("doom_rate", 0.0)))
	doom_velocity = _snap(float(data.get("doom_velocity", 0.0)))
	doom_momentum = _snap(float(data.get("doom_momentum", 0.0)))
	_pending_rival_doom = _snap(float(data.get("pending_rival_doom", 0.0)))
	if data.has("pending_stream_inputs"):
		_pending_stream_inputs = _snap_dict(data["pending_stream_inputs"])
	if data.has("doom_sources"):
		doom_sources = _snap_dict(data["doom_sources"])
	if data.has("rate_history"):
		rate_history.clear()
		for v in data["rate_history"]:
			rate_history.append(_snap(float(v)))

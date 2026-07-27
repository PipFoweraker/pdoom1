extends RefCounted
class_name Workstream
## A multi-month unit of directed work (ADR-0011 s3/s4, build lane L2 / issue #613).
##
## This is the substrate the month plan was always pointing at: `month_plan.gd:21` calls
## staff effort + strategic WIP "the seam L2 workstreams extend". A Workstream is world
## state, not a trophy: it carries a TOPIC, the people committed to it, the effort they
## have poured in, and the compute that work demands. Artifacts (papers, systems,
## campaigns) are emitted off it by later lanes -- this object only owns the accounting.
##
## DETERMINISM (ADR-0006): every method here is a pure function of its inputs plus the
## object's own state. There is NO rng in this file and none is wanted -- effort accrual
## must replay byte-identically, and assignment is player input, which replays for free.
## Floats that cross the save boundary are snapped to DoomSystem.SAVE_QUANTUM (Godot's
## JSON parse is not correctly-rounded; see the SERIALIZATION block in game_state.gd).
##
## SCOPE NOTE (lane T1, 2026-07-27): objects + backlog + assignment + topic accrual +
## compute intensity only. AP-pool deletion and the Attention migration are lane T2;
## founder-hour typing (doors/approvals/audits/reserve) and manager shields are later
## rungs. Nothing here reads or writes action_points.

# Topic vocabulary is SHARED with papers on purpose (RESEARCH_IDEA_PAPER_PIPELINE_GAP
# "Add a per-researcher focus_topic (reuse the PaperSubmissions.Topic enum)") -- a
# workstream that emits a paper must not have to translate its topic on the way out.
const TOPIC_KEYS := {
	PaperSubmissions.Topic.SAFETY: "safety",
	PaperSubmissions.Topic.ALIGNMENT: "alignment",
	PaperSubmissions.Topic.INTERPRETABILITY: "interpretability",
	PaperSubmissions.Topic.CAPABILITIES: "capabilities",
	PaperSubmissions.Topic.GOVERNANCE: "governance",
}

# Researcher specialization -> the topic they self-direct toward when nobody has assigned
# them anything (ADR-0011 s3: "idle staff don't exist; unmanaged staff do"). A researcher
# with an explicit focus_topic overrides this; the map is only the fallback agenda.
const SPECIALIZATION_TOPIC := {
	"safety": PaperSubmissions.Topic.SAFETY,
	"alignment": PaperSubmissions.Topic.ALIGNMENT,
	"interpretability": PaperSubmissions.Topic.INTERPRETABILITY,
	"capabilities": PaperSubmissions.Topic.CAPABILITIES,
	"governance": PaperSubmissions.Topic.GOVERNANCE,
}

# Accrual cadence. A turn is one WORKDAY (Clock.TURNS_PER_WEEK = 5); a plan-month is the
# decision cadence above it. compute_intensity is quoted PER ASSIGNED RESEARCHER PER
# MONTH (the readable unit), so the per-turn charge divides by this. Balance-tunable
# ("workstreams.turns_per_month"); the const is the fallback.
const TURNS_PER_MONTH := 22

enum Status {
	PROPOSED,   # sitting on the backlog / created but not started
	ACTIVE,     # running: assigned people accrue into it each tick
	COMPLETE,   # effort_target reached
	ABANDONED,  # dropped by the player (terminal; kept for the ledger/readout)
}

var id: String = ""
var backlog_id: String = ""          # which backlog entry minted this (may be "" for ad-hoc)
var title: String = ""
var topic: int = PaperSubmissions.Topic.SAFETY
var status: int = Status.PROPOSED

# --- Effort accounting (the multi-month bet) ---
var effort_accrued: float = 0.0      # total effort poured in
var effort_target: float = 100.0     # effort at which the workstream completes
var duration_months: int = 3         # PLANNED span (design intent; the target is the gate)
var assigned_ids: Array[String] = [] # stable researcher ids (GameState mints these)
var contributions: Dictionary = {}   # researcher_id -> float effort contributed
var started_on_turn: int = -1
var completed_on_turn: int = -1
var turns_active: int = 0            # ticks on which this workstream accrued anything

# --- Compute intensity (atom A7, the nested streams-proposal dial) ---
# Compute units this workstream demands PER ASSIGNED RESEARCHER PER MONTH, on top of the
# flat per-researcher burn in turn_manager. 0.0 = a pen-and-paper workstream. This is one
# field and one consumption hook by design: no influence stocks, no compute market yet.
var compute_intensity: float = 1.0


static func topic_key(topic_value: int) -> String:
	"""Lowercase stable key for a topic enum value (used by balance lookups + readouts)."""
	return String(TOPIC_KEYS.get(topic_value, "general"))


static func topic_from_key(key: String, default_topic: int = PaperSubmissions.Topic.SAFETY) -> int:
	"""Parse a lowercase topic key (as written in data/workstreams/backlog.json)."""
	for t in TOPIC_KEYS.keys():
		if TOPIC_KEYS[t] == key:
			return int(t)
	return default_topic


static func agenda_topic(specialization: String, focus_topic: int) -> int:
	"""The topic a researcher works toward when self-directing. An explicitly-set
	focus_topic (>= 0) wins; otherwise their lane picks for them. Pure lookup, no rng --
	self-direction is a RULE, not a dice roll (ADR-0006)."""
	if focus_topic >= 0:
		return focus_topic
	return int(SPECIALIZATION_TOPIC.get(specialization, PaperSubmissions.Topic.SAFETY))


static func make(new_id: String, entry: Dictionary, current_turn: int) -> Workstream:
	"""Build a workstream from a backlog entry dict (see WorkstreamBacklog)."""
	var ws := Workstream.new()
	ws.id = new_id
	ws.backlog_id = String(entry.get("id", ""))
	ws.title = String(entry.get("title", new_id))
	ws.topic = Workstream.topic_from_key(String(entry.get("topic", "safety")))
	ws.effort_target = maxf(1.0, float(entry.get("effort_target", 100.0)))
	ws.duration_months = maxi(1, int(entry.get("duration_months", 3)))
	ws.compute_intensity = maxf(0.0, float(entry.get("compute_intensity", 1.0)))
	ws.status = Status.ACTIVE
	ws.started_on_turn = current_turn
	return ws


# --- Assignment ---

func assign(researcher_id: String) -> bool:
	"""Commit a researcher to this workstream. Idempotent-false on a double-assign so the
	caller can tell 'already here' from 'newly committed'."""
	if researcher_id == "" or assigned_ids.has(researcher_id):
		return false
	if status == Status.COMPLETE or status == Status.ABANDONED:
		return false
	assigned_ids.append(researcher_id)
	# Sorted so serialization, readouts and lead-contributor tie-breaks are order-stable
	# regardless of the order the player clicked people in.
	assigned_ids.sort()
	return true


func unassign(researcher_id: String) -> bool:
	"""Pull a researcher off. Their accrued CONTRIBUTION stays -- effort already spent is
	spent, and later lanes read contributions for authorship."""
	var idx := assigned_ids.find(researcher_id)
	if idx < 0:
		return false
	assigned_ids.remove_at(idx)
	return true


func is_assigned(researcher_id: String) -> bool:
	return assigned_ids.has(researcher_id)


func assigned_count() -> int:
	return assigned_ids.size()


# --- Accrual ---

func accrue(researcher_id: String, amount: float, current_turn: int) -> float:
	"""Pour `amount` effort in on behalf of `researcher_id`. Returns the effort actually
	accepted (0.0 once complete/abandoned). Deterministic: no rng, no clock reads."""
	if amount <= 0.0:
		return 0.0
	if status != Status.ACTIVE:
		return 0.0
	# SNAP AT THE ACCUMULATOR, not just at to_dict: the LIVE value has to sit on the same
	# binary-exact grid the save writes, or a loaded run continues from a 1-ulp-different
	# base and diverges from an unsaved continuation (the doom-intermediary lesson,
	# DoomSystem.SAVE_QUANTUM ~1e-6 -- gameplay-invisible, replay-critical).
	var accepted: float = amount
	effort_accrued = DoomSystem._snap(effort_accrued + accepted)
	contributions[researcher_id] = DoomSystem._snap(
		float(contributions.get(researcher_id, 0.0)) + accepted)
	turns_active += 1
	if effort_accrued >= effort_target:
		status = Status.COMPLETE
		completed_on_turn = current_turn
	return accepted


func progress() -> float:
	"""0.0 .. 1.0 fraction of the effort target reached."""
	if effort_target <= 0.0:
		return 1.0
	return clampf(effort_accrued / effort_target, 0.0, 1.0)


func is_complete() -> bool:
	return status == Status.COMPLETE


func abandon() -> void:
	"""Drop the workstream. Terminal; the accrued effort and contributions are kept so the
	readout (and any later ledger entry) can show what was sunk into it."""
	if status == Status.ACTIVE or status == Status.PROPOSED:
		status = Status.ABANDONED


func lead_contributor() -> String:
	"""The researcher id with the most effort in this workstream ("" if none). Ties break
	on the lower id string, so the answer never depends on Dictionary iteration order."""
	var best_id: String = ""
	var best: float = -1.0
	var keys: Array = contributions.keys()
	keys.sort()
	for k in keys:
		var v := float(contributions[k])
		if v > best:
			best = v
			best_id = String(k)
	return best_id


# --- Compute intensity (A7) ---

static func turns_per_month() -> int:
	return maxi(1, Balance.inum("workstreams.turns_per_month", TURNS_PER_MONTH))


func compute_demand_per_month() -> float:
	"""Compute units this workstream wants for a whole plan-month at its current staffing."""
	return compute_intensity * float(assigned_ids.size())


func compute_demand_per_turn() -> float:
	"""The per-workday slice of the monthly demand (what the accrual hook actually bills)."""
	return compute_demand_per_turn_per_head() * float(assigned_ids.size())


func compute_demand_per_turn_per_head() -> float:
	"""Per-assigned-researcher, per-turn compute charge. The consumption hook bills this
	per person so a partly-starved fleet degrades person-by-person, not all-or-nothing."""
	return compute_intensity / float(Workstream.turns_per_month())


# --- Readout (minimal UI for this lane; the plan-screen verb is a separate CARVE lane) ---

func status_text() -> String:
	match status:
		Status.PROPOSED: return "Proposed"
		Status.ACTIVE: return "Active"
		Status.COMPLETE: return "Complete"
		Status.ABANDONED: return "Abandoned"
	return "Unknown"


func readout_line() -> String:
	"""One ASCII line for the debug readout: no emoji, house chrome only."""
	return "[%s] %s (%s) %d%% -- %d assigned, %.1f/%.1f effort, compute %.2f/mo" % [
		status_text(), title, Workstream.topic_key(topic),
		int(round(progress() * 100.0)), assigned_ids.size(),
		effort_accrued, effort_target, compute_demand_per_month(),
	]


# --- Serialization (game_state.gd SERIALIZATION CONVENTION rule 1) ---

func to_dict() -> Dictionary:
	return {
		"id": id,
		"backlog_id": backlog_id,
		"title": title,
		"topic": topic,
		"status": status,
		"effort_accrued": DoomSystem._snap(effort_accrued),
		"effort_target": DoomSystem._snap(effort_target),
		"duration_months": duration_months,
		"assigned_ids": assigned_ids.duplicate(),
		"contributions": DoomSystem._snap_dict(contributions),
		"started_on_turn": started_on_turn,
		"completed_on_turn": completed_on_turn,
		"turns_active": turns_active,
		"compute_intensity": DoomSystem._snap(compute_intensity),
	}


static func from_dict(data: Dictionary) -> Workstream:
	"""Rebuild from a save dict. Explicit casts throughout: JSON hands every number back
	as a float and every array back untyped (#618)."""
	var ws := Workstream.new()
	ws.id = String(data.get("id", ""))
	ws.backlog_id = String(data.get("backlog_id", ""))
	ws.title = String(data.get("title", ""))
	ws.topic = int(data.get("topic", PaperSubmissions.Topic.SAFETY))
	ws.status = int(data.get("status", Status.PROPOSED))
	ws.effort_accrued = DoomSystem._snap(float(data.get("effort_accrued", 0.0)))
	ws.effort_target = DoomSystem._snap(float(data.get("effort_target", 100.0)))
	ws.duration_months = int(data.get("duration_months", 3))
	ws.assigned_ids.clear()
	for rid in data.get("assigned_ids", []):
		ws.assigned_ids.append(String(rid))
	ws.contributions = {}
	var contrib = data.get("contributions", {})
	if contrib is Dictionary:
		for k in contrib.keys():
			ws.contributions[String(k)] = DoomSystem._snap(float(contrib[k]))
	ws.started_on_turn = int(data.get("started_on_turn", -1))
	ws.completed_on_turn = int(data.get("completed_on_turn", -1))
	ws.turns_active = int(data.get("turns_active", 0))
	ws.compute_intensity = DoomSystem._snap(float(data.get("compute_intensity", 1.0)))
	return ws

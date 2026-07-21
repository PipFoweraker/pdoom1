extends RefCounted
class_name EmployeeFSM
## Pure state-mapping logic for the OfficeFloor view (Tier 1).
##
## READ-ONLY / determinism-safe (ADR-0006): maps an employee STATE SNAPSHOT
## (a plain Dictionary of copied values) to a sprite animation state. No game
## state is read live and none is ever written; fully deterministic and unit
## testable with zero rendering.
##
## The returned strings double as AnimatedSprite2D animation names, so a real
## pixellab.ai SpriteFrames only needs clips called idle/walking/working/stressed.

# Sprite / animation states.
const STATE_IDLE := "idle"          # present but not working (disengaged / no data)
const STATE_WALKING := "walking"    # aimless wander -- unmanaged / drifting
const STATE_WORKING := "working"    # heads-down at a desk
const STATE_STRESSED := "stressed"  # burnout -- head-in-hands

const ALL_STATES := [STATE_IDLE, STATE_WALKING, STATE_WORKING, STATE_STRESSED]

# Thresholds (tunable). BURNOUT_STRESSED matches Researcher.is_burned_out() (>=80).
const BURNOUT_STRESSED := 80.0
const LOYALTY_DISENGAGED := 15   # checked-out: physically present, not working

## Map ONE employee snapshot -> sprite state. Every field is optional; absent
## fields degrade gracefully (default idle/wander, never a false "working").
##
## Precedence (most salient problem first):
##   1. stressed  -- burnout >= BURNOUT_STRESSED
##   2. walking   -- unmanaged == true (drifting, no manager to focus them)
##   3. idle      -- loyalty <= LOYALTY_DISENGAGED (checked out)
##   4. working   -- assigned == true
##   5. idle      -- default / no signal
static func map_state(emp: Dictionary) -> String:
	var burnout := float(emp.get("burnout", 0.0))
	if burnout >= BURNOUT_STRESSED:
		return STATE_STRESSED

	if bool(emp.get("unmanaged", false)):
		return STATE_WALKING

	if emp.has("loyalty") and int(emp["loyalty"]) <= LOYALTY_DISENGAGED:
		return STATE_IDLE

	if bool(emp.get("assigned", false)):
		return STATE_WORKING

	return STATE_IDLE

## Map a whole roster snapshot (Array of Dictionaries) -> Array of state strings,
## index-aligned with the input. Non-dict entries are skipped.
static func map_roster(roster: Array) -> Array:
	var out: Array = []
	for emp in roster:
		if emp is Dictionary:
			out.append(map_state(emp))
	return out

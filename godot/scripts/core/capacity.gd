extends RefCounted
class_name Capacity
## THE single derivation point for the founder's monthly ATTENTION budget.
##
## Ruled 2026-08-12 (coordination/DESIGN_2026-08-12_interrupt-resolution-variants.md,
## sections "AMENDED minutes later" and "AMENDED again"):
##
##   The calendar is the world; ATTENTION is the player. The two are different objects
##   and the gap between them is the fiction -- you cannot attend to everything that
##   happens. So the budget does NOT track month length. It is 20, always, while gross
##   balance is being developed.
##
## What this file is for, then, given the value is locked: it is the SHAPE the budget
## will need when sickness / leave / per-difficulty capacity are unlocked later. Every
## input that future capacity needs is already in the signature -- the seed, the month,
## and a modifier set -- so unlocking variety is editing THIS function rather than
## hunting every reference. That is the whole cost of not retrofitting, and it is one
## parameter (ruling, "THE CONSTRAINT").
##
## THE CONSTRAINT, and it is load-bearing:
##   ANY variability here must derive from the SEED, never from runtime RNG.
##   This repo's run artifact is an input-replay re-simulated against the same engine
##   (ADR-0006), and a capacity drawn from an unseeded source would break replay
##   determinism SILENTLY -- the run still completes and still posts a score. Worse, a
##   draw taken from `state.rng` would advance the shared stream and fork every recorded
##   replay even while returning the same number. So:
##     - the value never touches an rng at all (it is the grant, unconditionally);
##     - the REASON uses a CHILD RandomNumberGenerator seeded off hash(seed|month), the
##       same pattern as GameState._init (game_state.gd) and Researcher's hidden-trait
##       draw (researcher.gd) -- it reads the seed, it never advances the run stream.
##
## FLAVOUR SHIPS BEFORE VARIETY. The function returns a value AND a reason, because a
## cap with no reason reads to a new player as a bug ("a decision with no destination
## reads as a decision that did not happen", the Jason playtest). While the value is
## locked at 20, the reason can already vary, so the architecture pays for itself during
## balance development rather than after it -- and when capacity does start moving, the
## explanation channel already exists and the player does not read the change as a break.
##
## NOTE for whoever unlocks variety: this returns the grant unchanged today. The moment
## `value` stops equalling `modifiers.grant`, the ladder epoch must bump
## (`ladder_version.txt`) -- by definition, per the ruling's sequencing step 3.

# The locked budget. Only a fallback: the live number is the Balance dial
# `attention.per_month`, and difficulty / scenario packs override it via `modifiers.grant`.
const DEFAULT_GRANT: int = 20

# Modifier-set keys. Today only GRANT is read. Named as constants so the future
# sickness / leave / difficulty inputs land next to it instead of as loose strings.
const MOD_GRANT := "grant"

# Month-flavoured explanations for the cap, indexed by CALENDAR month (0 = January).
# Selected deterministically from seed + month; see reason_for().
#
# House rules for anything added here:
#   1. Start with the month name and a full stop -- reason_for()'s contract, and
#      test_capacity.gd asserts it.
#   2. Never name a NUMBER. These sentences must stay true when the value unlocks.
#   3. ASCII only, no emoji (scripts/check_no_emoji.py is a blocking pre-commit gate).
#   4. Appending to a pool CHANGES which sentence a given seed reads in a given month.
#      That is cosmetic today (nothing consumes the reason yet) but it is a visible
#      diff to a player once the reason is surfaced -- treat pools as append-with-care.
const MONTH_REASONS: Array = [
	# January
	[
		"January. Half the team is still on leave and the other half is pretending to be back.",
		"January. Nothing has been signed off since mid-December and the queue knows it.",
		"January. The building's cooling lost an argument with the heat, and so did everyone in it.",
	],
	# February
	[
		"February. The shortest month bills you for a full one anyway.",
		"February. Grant season. Every hour not spent on a form is an hour spent worrying about a form.",
		"February. Two of the team are at a conference you approved in a more optimistic month.",
	],
	# March
	[
		"March. End of quarter, so every external party wants a number from you before Friday.",
		"March. The compliance review landed, and it landed on the calendar.",
		"March. Term started. Your academic collaborators have gone quiet until it stops.",
	],
	# April
	[
		"April. A long weekend, then another, then a week where nobody quite restarts.",
		"April. There is scaffolding on the building and the lift has opinions.",
		"April. Tax paperwork. It is not research, and it is not optional.",
	],
	# May
	[
		"May. Submission deadlines everywhere, and none of them are yours.",
		"May. Two of the team are interviewing elsewhere and being polite about it.",
		"May. Power was cut for building maintenance on the one day you had blocked out.",
	],
	# June
	[
		"June. Mid-year reviews. Everyone needs an hour and everyone gets one.",
		"June. The flu went around the office, then came back for the people it missed.",
		"June. Financial year end. Finance would like a word, several times.",
	],
	# July -- the ruling's worked example.
	[
		"July. Two researchers away, the university is shut, nobody answers email.",
		"July. Peak conference season. The people you need are all in a different timezone.",
		"July. Half the building is on leave and the other half is covering for them.",
	],
	# August
	[
		"August. Everyone who did not take July took August.",
		"August. The new cohort arrived, and onboarding is a full-time job you did not budget.",
		"August. Reviewing season. Your senior people are reading other people's papers.",
	],
	# September
	[
		"September. Term restarts, teaching loads land, and your collaborators vanish into lectures.",
		"September. The board wants a plan for next year, and wants it in a meeting.",
		"September. A funder visit. Two days of preparation for ninety minutes of nodding.",
	],
	# October
	[
		"October. Grant renewal season. The forms are longer this year.",
		"October. Three deadlines collided and the calendar simply gave up.",
		"October. The office move that was going to take a weekend is taking a fortnight.",
	],
	# November
	[
		"November. Conference travel, jet lag, and a week of catching up on what broke.",
		"November. Annual reviews, and the honest conversations they drag along.",
		"November. The audit arrived early, which is the only way audits ever arrive.",
	],
	# December
	[
		"December. Everything shuts, and it shuts earlier than anyone admits.",
		"December. End-of-year reporting eats the fortnight nobody thought to protect.",
		"December. Half the team has leave they must use or lose, and they are using it.",
	],
]

# Namespaces the child RNG so capacity's stream can never collide with another
# seed-derived feature that happens to key off the same (seed, month) pair.
const _REASON_SALT := "capacity/reason/v1"


static func derive(game_seed: String, month_index: int, modifiers: Dictionary = {}) -> Dictionary:
	"""The derivation point. Returns {"value": int, "reason": String}.

	`game_seed`   -- the run's seed string (GameState.game_seed_str). IGNORED by `value`
	                 today, present from the first line so unlocking variety is a body
	                 edit, not a signature change that ripples to every call site.
	`month_index` -- ABSOLUTE month ordinal, Clock.month_index() form (year*12 + month-1).
	                 Absolute rather than 0-based-since-start so the calendar month is
	                 recoverable (month_index % 12) and July is July in every run.
	`modifiers`   -- the modifier set. Today: {"grant": int} -- the difficulty / scenario
	                 grant already held on GameState.attention_per_month. Tomorrow: leave,
	                 sickness, difficulty capacity bands.

	ZERO BEHAVIOUR CHANGE is the contract: `value` is exactly the grant, for every seed
	and every month. Nothing here reads an rng."""
	return {
		"value": grant_of(modifiers),
		"reason": reason_for(game_seed, month_index),
	}


static func grant_of(modifiers: Dictionary = {}) -> int:
	"""The locked budget: the caller's grant, else the Balance dial, else DEFAULT_GRANT.

	This is the ONLY place `value` is decided. When variety unlocks, the leave /
	sickness / difficulty terms modulate the number returned HERE and nowhere else."""
	if modifiers.has(MOD_GRANT):
		return int(modifiers[MOD_GRANT])
	return Balance.inum("attention.per_month", DEFAULT_GRANT)


static func reason_for(game_seed: String, month_index: int) -> String:
	"""The month-flavoured sentence explaining the cap. SEED-DERIVED and pure: the same
	(seed, month) reads the same sentence in every run and every replay of that board.

	Determinism, stated so it can be checked rather than trusted:
	  - the draw uses a CHILD RandomNumberGenerator, seeded off hash(salt|seed|month).
	    Godot's String hash is a pure function of the characters, so it is stable across
	    runs and platforms for the same build (same argument as Researcher's
	    self_report_optimism, which is pinned by unit test).
	  - it NEVER touches GameState.rng, so calling this cannot advance the run stream and
	    cannot fork a recorded replay (ADR-0006). test_capacity.gd pins that too.
	  - the pools are fixed-order literal Arrays, not Dictionary iteration, so the index
	    draw is order-stable (the ADR-0006 sorted-index rule, satisfied by construction)."""
	var pool: Array = MONTH_REASONS[posmod(month_index, 12)]
	if pool.is_empty():
		return ""
	var reason_rng := RandomNumberGenerator.new()
	reason_rng.seed = hash("%s|%s|%d" % [_REASON_SALT, game_seed, month_index])
	return String(pool[reason_rng.randi() % pool.size()])

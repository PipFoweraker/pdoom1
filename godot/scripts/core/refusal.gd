class_name Refusal
extends RefCounted
## The stub-vs-rule contract for player-facing refusals (playtest 2026-08-14, Pip).
##
## THE PRINCIPLE. A stub that refuses in the voice of a rule teaches the player a rule that
## does not exist. "You cannot do that" and "we have not built that yet" are DIFFERENT
## STATEMENTS: the first is worldbuilding, the second is an apology. Conflating them is a
## lie to the player -- the in-game cousin of the false-claim problem the website audit
## spent two days on (docs/CLAIM_AUDIT_2026-08-06.md). An alpha is allowed to be
## incomplete. It is not allowed to present incompleteness as design.
##
## WHAT WENT WRONG. Onboarding a hire costs 3 Attention. With a full queue on screen, the
## card's "pull from planned work" option refused with
##     "Insufficient capacity to handle by cannibalizing"
## -- stated as a capacity rule. It is not one. MonthPlan.pay_by_cannibalizing() can only
## free Attention by cancelling MonthPlan.queued_strategic entries, and NOTHING in the
## shipped game ever writes that array: its sole production writer,
## GameManager.queue_strategic_action(), has zero callers. The player's visible queue lives
## in GameState.queued_actions, which the cannibalize path cannot see. So the option cannot
## do the thing it names, and the refusal explained a budget instead of an absence.
## Pip: "which, like, isn't strictly true?"
##
## THE CONTRACT. Every refusal is exactly one of two kinds, and the code must SAY WHICH:
##   RULE -- a real game constraint. Ships as-is. This is worldbuilding; the player should
##           learn it, plan around it, and still believe it at 1.0.
##   STUB -- refuses because the feature/branch is unbuilt. Carries ALPHA_STUB_MARKER so
##           the player can tell an apology from a rule, and so the sentence stops being a
##           lie the moment it is read.
## There is deliberately no third constructor. "WRONG" (states a reason that is not the
## actual reason) is a DEFECT to fix at the call site, not a class to ship.
##
## WHY THIS RESISTS ROT, in three independent ways:
##  1. The classification is a REQUIRED CHOICE, not a remembered step. You cannot build a
##     refusal through this API without naming rule() or stub(); there is no unclassified
##     constructor to fall into. (The `_facts_this_copy_must_not_break` block rotted
##     precisely because it relied on remembering to update it.)
##  2. The marker EXPIRES ON ITS OWN. It is gated on BuildInfo.ALPHA_TOOLS_ERA, the
##     existing era switch already documented "flip false at 1.0" -- so no stub marker can
##     survive into the finished game by being forgotten. One flip retires all of them.
##  3. A ratchet, not a plea. tools/check_refusal_classification.py fails on any refusal
##     site that is neither built through this class nor annotated, and its baseline of
##     pre-existing sites can only SHRINK. New debt cannot be added silently; old debt
##     cannot be re-added once paid off.
##
## RELATION TO THE EXISTING HALF-CONVENTIONS. This subsumes, it does not compete:
##   * `is_stub: true` in godot/data/actions/travel.json + the "[Coming Soon]" description
##     prefix -- the data-side "unbuilt" flag, used by travel_panel_controller.gd to grey a
##     button out. That marks an ACTION as unbuilt BEFORE the player presses it. This class
##     marks a REFUSAL as unbuilt AFTER they press. Both are wanted; they are different
##     moments. (TECH_DEBT_BURNDOWN.md item 5 tracks the keep-vs-hide ruling for the former.)
##   * ALPHA_TOOLS_TOGGLE_WARNING / ALPHA_TOOLS_GAME_OVER_NOTICE in game_config.gd -- the
##     settled wording for DEV POWERS. Same era switch, same ASCII bracket chrome, different
##     subject: those say "this tool will not exist", this says "this behaviour is not built".
##
## HOUSE STYLE. ASCII only (CLAUDE.md hard rule, issue #744) -- the marker is pure ASCII
## bracket chrome in the family of "[!]", "[OK]", "[M]", "[ESC] close".

## Pip's marker, verbatim (playtest 2026-08-14). Player-facing copy is his; do not restyle
## it. Change it here or nowhere -- every stub refusal in the game reads from this const.
const ALPHA_STUB_MARKER := "[ALPHA: This behaviour is a stub, harass the developers to extend it!]"

## Values of the `refusal` key on a result Dictionary. Machine-readable so UI surfaces can
## present the two kinds differently (event_dialog puts the marker on its own line) and so
## tests can assert a refusal's KIND rather than string-matching its prose.
const CLASS_RULE := "rule"
const CLASS_STUB := "stub"


static func rule(text: String) -> Dictionary:
	"""A REAL constraint, correctly stated. Ships unmarked -- the player is meant to learn
	this and still believe it at 1.0."""
	return {"success": false, "message": text, "refusal": CLASS_RULE}


static func stub(text: String) -> Dictionary:
	"""Refused because the behaviour is UNBUILT. `text` still explains what happened in
	Pip's voice; the marker is appended so the player can tell an apology from a rule."""
	return {"success": false, "message": mark_stub(text), "refusal": CLASS_STUB}


static func mark_stub(text: String) -> String:
	"""Append the alpha marker to an already-composed refusal string.

	For the sites that produce a BARE STRING rather than a result Dictionary -- a UI label,
	an `error_occurred.emit(...)`, a `result["message"] = ...` on a partially-built dict.
	Idempotent, so a message that passes through two layers is not marked twice, and a
	no-op once ALPHA_TOOLS_ERA is flipped false at 1.0."""
	if not BuildInfo.ALPHA_TOOLS_ERA:
		return text
	if text.contains(ALPHA_STUB_MARKER):
		return text
	if text.strip_edges().is_empty():
		return ALPHA_STUB_MARKER
	return "%s %s" % [text, ALPHA_STUB_MARKER]


static func is_stub_message(text: String) -> bool:
	"""True when `text` already carries the marker. Lets a presentation layer lay the marker
	out separately (see EventDialog._show_reason) without re-deriving the classification."""
	return text.contains(ALPHA_STUB_MARKER)


static func strip_marker(text: String) -> String:
	"""`text` with the marker removed and whitespace tidied. For presentation layers that
	want to re-place the marker rather than leave it mid-sentence."""
	return text.replace(ALPHA_STUB_MARKER, "").strip_edges()

class_name EventTiers
extends RefCounted
## Event delivery-tier classification (L1 / workshop#3 addendum #1-2, ADR-0012).
##
## The structural #630 fix: the flood ceiling was an INFORMATION budget (cap how many
## events fire). Under the month plan it becomes a DEMAND budget -- only one tier demands
## a decision. Every event genre is classified:
##   ambient -- board state mutates, no notification (the 2017 civilian-awareness floor)
##   feed    -- readable, pull, no acknowledgment; carries a source_id (a named character
##             who plausibly owns the information -- provenance now, UI later)
##   window  -- the ONLY tier that demands a decision (a costed response menu opens)
##
## Windows additionally carry an event CLASS (ADR-0012 taxonomy) governing which response
## verbs are legal:
##   un-snoozable   -- HANDLE or IGNORE only; DEFER is not for sale (keeps reserve worth holding)
##   deferrable     -- DEFER mints a Ledger entry (ADR-0013 carrying cost)
##   standing       -- open for expiry_turns, then evaporates to no-engage (NO ledger entry)
##   no-action      -- taking no action is legitimately correct; never punished
##
## Classification lives on the event DATA (delivery_tier / event_class / source_id /
## unignorable / expiry_turns / window{}); this module only reads it, applying Balance
## defaults so un-annotated legacy events degrade to a sane tier. Content wiring is L4.

const TIER_AMBIENT := "ambient"
const TIER_FEED := "feed"
const TIER_WINDOW := "window"

const CLASS_UNSNOOZABLE := "un-snoozable"
const CLASS_DEFERRABLE := "deferrable"
const CLASS_STANDING := "standing"
const CLASS_NO_ACTION := "no-action"

const VALID_TIERS := [TIER_AMBIENT, TIER_FEED, TIER_WINDOW]


static func default_tier() -> String:
	return Balance.table("events", {}).get("default_delivery_tier", TIER_FEED)


static func default_class() -> String:
	return Balance.table("events", {}).get("default_event_class", CLASS_DEFERRABLE)


static func tier_of(event: Dictionary) -> String:
	"""Delivery tier of an event, defaulting via Balance for un-annotated legacy defs.
	An event carrying its own `options` but no explicit tier is treated as a window --
	pre-L1 popups all demanded a decision, so that is the behaviour-preserving default
	for anything option-bearing; genuinely ambient/feed genres opt out via delivery_tier."""
	var t := String(event.get("delivery_tier", ""))
	if t in VALID_TIERS:
		return t
	# Legacy popup with options == a decision was demanded pre-L1 -> window.
	if String(event.get("type", "")) == "popup" and not event.get("options", []).is_empty():
		return TIER_WINDOW
	return default_tier()


static func class_of(event: Dictionary) -> String:
	var c := String(event.get("event_class", ""))
	if c != "":
		return c
	return default_class()


static func source_id_of(event: Dictionary) -> String:
	"""Provenance (addendum #2): the named character who owns this information. Falls back
	to any category/type hint, then 'unknown'. Feed items should always carry one."""
	var s := String(event.get("source_id", ""))
	if s != "":
		return s
	return String(event.get("category", "unknown"))


static func is_window(event: Dictionary) -> bool:
	return tier_of(event) == TIER_WINDOW


static func is_unignorable(event: Dictionary) -> bool:
	"""Legally unignorable windows cannot auto-resolve to IGNORE; the player must engage
	(addendum #1). Un-snoozable class is NOT automatically unignorable -- that's the DEFER
	ban; unignorable is a stronger explicit flag."""
	return bool(event.get("unignorable", false))


static func defer_allowed(event: Dictionary) -> bool:
	"""DEFER (mint a ledger entry) is sold only on the deferrable class (ADR-0012 S1-2)."""
	return class_of(event) == CLASS_DEFERRABLE


static func expiry_turns(event: Dictionary) -> int:
	"""Standing offers stay open this many resolution ticks, then evaporate. 0 = closes
	the same month it opened (un-snoozable-style single-tick window)."""
	return int(event.get("expiry_turns", 0))


static func legal_responses(event: Dictionary) -> Array:
	"""The response verbs a window legally offers, by class (ADR-0012). Always a subset of
	[handle_reserve, handle_cannibalize, defer, ignore]."""
	var verbs := ["handle_reserve", "handle_cannibalize"]
	if defer_allowed(event):
		verbs.append("defer")
	if not is_unignorable(event):
		verbs.append("ignore")
	return verbs


static func partition(events: Array) -> Dictionary:
	"""Split a fired-event list into the three tiers. Windows are what the demand budget
	throttles and what auto-pauses day-tick playback; ambient/feed never interrupt."""
	var out := {"ambient": [], "feed": [], "windows": []}
	for ev in events:
		if not ev is Dictionary:
			continue
		match tier_of(ev):
			TIER_AMBIENT:
				out["ambient"].append(ev)
			TIER_WINDOW:
				out["windows"].append(ev)
			_:
				out["feed"].append(ev)
	return out

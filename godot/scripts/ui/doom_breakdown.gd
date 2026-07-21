extends VBoxContainer
class_name DoomBreakdown
## Doom "blow-by-blow" -- colour-coded per-source breakdown of why doom moved this turn (#578).
##
## Surfaces state["doom_system"]["doom_sources"] (already computed by DoomSystem) as compact,
## coloured lines near the doom meter / trend graph, like old turn-based combat logs
## ("Rivals +12.3", "Safety -14.4"). Red = source pushing doom UP, green = source pulling it DOWN.
## Only non-zero sources are shown, biggest movers first.
##
## The pure builder build_entries() and the classify()/label_for() helpers are unit-tested
## (test_doom_breakdown.gd); the actual on-screen layout/legibility still needs a human eye.

## Values whose magnitude is below this round to 0.0 at one decimal place -- treat as "no move".
const EPSILON := 0.05

## Human-readable labels for known source keys. Unknown keys fall back to Capitalized words,
## so a new DoomSystem source still renders sanely without touching this map.
##
## ADR-0015 stream vocabulary (baseline/overhang/diffusion/compute/panic/alarm/ledger) is the
## live key set that DoomSystem populates; the older keys (base/safety/momentum/technical_debt)
## are retained for save-compat and the tech-debt coupling. The dead "rivals" key was REMOVED:
## post-ADR-0015 no rival writes doom, so no "rivals" source is ever populated (pinned by
## test_doom_system.gd). Rival attribution now rides the "overhang" stream -- see set_sources().
const SOURCE_LABELS := {
	"baseline": "Baseline",
	"overhang": "Overhang",
	"diffusion": "Diffusion",
	"compute": "Compute",
	"panic": "Panic",
	"alarm": "Alarm",
	"ledger": "Ledger",
	"momentum": "Momentum",
	"technical_debt": "Technical Debt",
	"base": "Base",
	"safety": "Safety",
	"specializations": "Specializations",
	"capabilities": "Capabilities",
	"events": "Events",
	"cascades": "Cascades",
	"market_pressure": "Market Pressure",
	"unproductive": "Unproductive Staff",
}

## Frontier slices below this magnitude round to "no meaningful frontier" and are left out of
## the overhang attribution list (a rival that has not moved the frontier is not driving doom).
const FRONTIER_EPSILON := 0.5

static func label_for(source_key: String) -> String:
	if SOURCE_LABELS.has(source_key):
		return SOURCE_LABELS[source_key]
	return source_key.capitalize()

## +1 = increases doom (red), -1 = decreases doom (green), 0 = negligible (omit from display).
static func classify(value: float) -> int:
	if value > EPSILON:
		return 1
	if value < -EPSILON:
		return -1
	return 0

## Colour for a classified sign, reusing the shared theme semantic colours.
static func color_for_sign(sign_value: int) -> Color:
	if sign_value > 0:
		return ThemeManager.get_color("error")     # red -- pushing doom up
	if sign_value < 0:
		return ThemeManager.get_color("success")   # green -- pulling doom down
	return ThemeManager.get_color("text_dim")

## Pure builder: given a doom_sources dict, return the ordered per-source display entries.
## Skips zero / negligible sources. Each entry is a Dictionary:
##   {key, label, value, sign, text}   (text e.g. "Rivals +12.3" / "Safety -14.4")
## Ordered by descending absolute magnitude so the biggest movers read first.
static func build_entries(doom_sources: Dictionary) -> Array:
	var entries: Array = []
	for key in doom_sources.keys():
		var value: float = float(doom_sources[key])
		var sign_value: int = classify(value)
		if sign_value == 0:
			continue
		entries.append({
			"key": key,
			"label": label_for(key),
			"value": value,
			"sign": sign_value,
			"text": "%s %+.1f" % [label_for(key), value],
		})
	entries.sort_custom(func(a, b): return abs(a["value"]) > abs(b["value"]))
	return entries

# ============================================================================
# OVERHANG ATTRIBUTION -- name the rival labs behind the acute-hazard stream.
#
# The "overhang" stream (doom_system.gd _compute_streams (b)) is priced off the MAX actor
# frontier: W_frontier * max(0, max_actor(frontier_capability) - safety_absorption). So the
# actor holding the highest frontier IS the one setting the acute hazard. We rank the
# non-negligible frontier holders (player + rivals) and mask each rival's name through its
# real visibility, so an undiscovered lab reads "an unknown actor" -- never a pre-discovery
# leak of its real name (e.g. StealthAI while still HIDDEN). READ-ONLY over sim state.
# ============================================================================

## Resolve a frontier actor id to a player-facing name. "player" is the local lab; a rival id
## is matched against the serialized rival dicts (state.rival_labs_full) and masked by its own
## visibility (RivalLab.is_visible_to_player()/get_visible_name()). Unknown/hidden -> masked.
static func mask_actor_name(actor_id: String, rival_labs) -> String:
	if actor_id == "player":
		return "your own frontier"
	if rival_labs is Array:
		for rd in rival_labs:
			if rd is Dictionary and str(rd.get("id", "")) == actor_id:
				var lab := RivalLabs.RivalLab.from_dict(rd)
				if lab.is_visible_to_player():
					return lab.get_visible_name()
				return "an unknown actor"
	return "an unknown actor"

## Ordered (descending frontier) list of {id, name, value} for actors holding a non-negligible
## frontier slice. Names are already visibility-masked. Pure -- unit-tested.
static func frontier_leaders(frontier_capability, rival_labs) -> Array:
	var out: Array = []
	if not (frontier_capability is Dictionary):
		return out
	for actor_id in frontier_capability.keys():
		var v: float = float(frontier_capability[actor_id])
		if v < FRONTIER_EPSILON:
			continue
		out.append({
			"id": str(actor_id),
			"name": mask_actor_name(str(actor_id), rival_labs),
			"value": v,
		})
	out.sort_custom(func(a, b): return a["value"] > b["value"])
	return out

## One-line attribution for the overhang stream, e.g. "frontier held by CapabiliCorp, DeepSafety".
## Empty string when no actor holds a meaningful frontier. Lists up to three top holders.
static func overhang_attribution_text(frontier_capability, rival_labs) -> String:
	var leaders := frontier_leaders(frontier_capability, rival_labs)
	if leaders.is_empty():
		return ""
	var names: Array = []
	for leader in leaders.slice(0, 3):
		names.append(str(leader["name"]))
	return "frontier held by %s" % ", ".join(names)

func _ready() -> void:
	add_theme_constant_override("separation", 1)
	visible = false  # nothing to show until the first doom_sources arrives

## Rebuild the breakdown from a doom_sources dict (state["doom_system"]["doom_sources"]).
## frontier_capability (state["frontier_capability"]) and rival_labs (state["rival_labs_full"])
## are optional -- when supplied, a dim per-lab attribution sub-line is rendered under the
## overhang line naming which actors' frontier is driving the acute hazard.
func set_sources(doom_sources, frontier_capability = {}, rival_labs = []) -> void:
	# Clear previous lines immediately (avoid a one-frame duplicate that queue_free would leave).
	while get_child_count() > 0:
		var old := get_child(0)
		remove_child(old)
		old.free()

	var entries := build_entries(doom_sources if doom_sources is Dictionary else {})
	visible = not entries.is_empty()
	if entries.is_empty():
		return

	var caption := Label.new()
	caption.text = "Doom this turn:"
	caption.add_theme_font_size_override("font_size", 20)
	caption.add_theme_color_override("font_color", ThemeManager.get_color("text_dim"))
	add_child(caption)

	for entry in entries:
		var line := Label.new()
		line.text = entry["text"]
		line.add_theme_font_size_override("font_size", 22)
		line.add_theme_color_override("font_color", color_for_sign(entry["sign"]))
		add_child(line)

		# Under a doom-increasing overhang line, name the rival labs whose frontier is
		# driving it (visibility-masked). Only when we were handed the frontier data.
		if entry["key"] == "overhang" and entry["sign"] > 0:
			var attribution := overhang_attribution_text(frontier_capability, rival_labs)
			if attribution != "":
				var sub := Label.new()
				sub.text = "  " + attribution
				sub.add_theme_font_size_override("font_size", 16)
				sub.add_theme_color_override("font_color", ThemeManager.get_color("text_dim"))
				add_child(sub)

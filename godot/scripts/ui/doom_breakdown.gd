extends VBoxContainer
class_name DoomBreakdown
## Doom "blow-by-blow" — colour-coded per-source breakdown of why doom moved this turn (#578).
##
## Surfaces state["doom_system"]["doom_sources"] (already computed by DoomSystem) as compact,
## coloured lines near the doom meter / trend graph, like old turn-based combat logs
## ("Rivals +12.3", "Safety -14.4"). Red = source pushing doom UP, green = source pulling it DOWN.
## Only non-zero sources are shown, biggest movers first.
##
## The pure builder build_entries() and the classify()/label_for() helpers are unit-tested
## (test_doom_breakdown.gd); the actual on-screen layout/legibility still needs a human eye.

## Values whose magnitude is below this round to 0.0 at one decimal place — treat as "no move".
const EPSILON := 0.05

## Human-readable labels for known source keys. Unknown keys fall back to Capitalized words,
## so a new DoomSystem source still renders sanely without touching this map.
const SOURCE_LABELS := {
	"base": "Base",
	"rivals": "Rivals",
	"safety": "Safety",
	"momentum": "Momentum",
	"specializations": "Specializations",
	"capabilities": "Capabilities",
	"events": "Events",
	"technical_debt": "Technical Debt",
	"cascades": "Cascades",
	"market_pressure": "Market Pressure",
	"unproductive": "Unproductive Staff",
}

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
		return ThemeManager.get_color("error")     # red — pushing doom up
	if sign_value < 0:
		return ThemeManager.get_color("success")   # green — pulling doom down
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

func _ready() -> void:
	add_theme_constant_override("separation", 1)
	visible = false  # nothing to show until the first doom_sources arrives

## Rebuild the breakdown from a doom_sources dict (state["doom_system"]["doom_sources"]).
func set_sources(doom_sources) -> void:
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

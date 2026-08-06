class_name MusicControls
extends VBoxContainer
## Player-facing music picker. Lives in the pause menu (ESC), next to the music volume
## slider that is already there.
##
## Pip 2026-08-06: "I think giving players access to the music control options including
## track swapping from the escape screen while in game would be cool." The machinery is
## PR #1129's dev audition tool; this is the same machinery with plain words and one
## control instead of four.
##
## WHY THIS IS SAFE TO SHIP TO PLAYERS (the property the whole feature rests on):
## picking a track calls MusicManager and nothing else. MusicManager is a pure view-layer
## side-effect (ADR-0006) -- it LISTENS to game_state_updated and never writes GameState,
## the seeded RNG, the turn loop or scoring. So this is not an Alpha Tool and does not
## unrank a run (Pip's ruling: "if people want to listen to their favourite tracks, they
## can do so and if they miss out on doom indicators etc, so be it, that's their choice").
## test_music_player_controls.gd snapshots the entire game state dict across a full picker
## session and asserts it comes back identical; that test is the guard on this paragraph.
##
## SELF-CONTAINED BY DESIGN: builds its own children in _ready(), reads nothing from its
## parent, and is a plain VBoxContainer. It drops into the settings menu or a future
## audio panel unchanged -- the UI architecture pass (docs/design/UI_ARCHITECTURE_2026-08-06.md)
## wants components, not more lines in main_ui.gd.

## TYPE SCALE -- must stay in step with pause_menu.tscn (Pip 2026-08-06: "things feel a
## bit cramped ... the text could be larger and friendlier"). These four numbers are the
## component's half of ONE scale that is authored across two files, so they are named
## rather than buried in _build(), and test_music_player_controls.gd asserts the shared
## floor and the header match instead of trusting this comment.
##
## NOT routed through ThemeManager.get_font_size() on purpose, and this is the reason:
## that API returns the ACTIVE theme's sizes, and the "retro" theme sets body_size 18
## where "default" sets 16 (theme_manager.gd:174-175). The pause menu's panel height is
## HAND-AUTHORED in the .tscn and guarded against the content's measured minimum, so a
## theme swap would silently move the content past a box no test run could have seen.
## Sizes here are fixed; colours below are the pause menu's local palette (the same amber
## as the Audio Settings header one row up, which ThemeManager's generic "warning" amber
## is close to but not equal to -- routing them would split two adjacent headers).
const SECTION_TITLE_FONT_SIZE := 22
const PICKER_FONT_SIZE := 20
const STATUS_FONT_SIZE := 16
const HINT_FONT_SIZE := 14
## Width the picker and the two wrapped labels ask for. The panel is wider than this and
## these are EXPAND_FILL, so the real wrap width is the panel's -- this is only the floor.
const CONTROL_MIN_WIDTH := 560

const SECTION_TITLE := "Music track"
const HINT_TEXT := ("The score normally follows how the run is going. Pick a track to keep "
	+ "it playing instead -- you may miss what the music was telling you. Your pick lasts "
	+ "this run; a new run starts on Automatic.")

var _picker: OptionButton = null
var _status: Label = null
var _hint: Label = null
## Guards the programmatic reselect in refresh() from firing item_selected and
## re-applying the entry that is already playing (which would restart a crossfade
## every time the pause menu opens).
var _applying: bool = false


func _ready() -> void:
	add_theme_constant_override("separation", 8)
	_build()
	refresh()


func _build() -> void:
	var title := Label.new()
	title.text = SECTION_TITLE
	title.add_theme_font_size_override("font_size", SECTION_TITLE_FONT_SIZE)
	title.add_theme_color_override("font_color", Color(0.91, 0.64, 0.24))
	add_child(title)

	_picker = OptionButton.new()
	_picker.name = "Picker"
	_picker.custom_minimum_size = Vector2(CONTROL_MIN_WIDTH, 0)
	_picker.add_theme_font_size_override("font_size", PICKER_FONT_SIZE)
	_picker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_picker.item_selected.connect(_on_item_selected)
	add_child(_picker)

	_status = Label.new()
	_status.name = "Status"
	_status.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_status.custom_minimum_size = Vector2(CONTROL_MIN_WIDTH, 0)
	_status.add_theme_font_size_override("font_size", STATUS_FONT_SIZE)
	_status.add_theme_color_override("font_color", Color(0.55, 0.85, 1.0))
	add_child(_status)

	_hint = Label.new()
	_hint.text = HINT_TEXT
	_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_hint.custom_minimum_size = Vector2(CONTROL_MIN_WIDTH, 0)
	_hint.add_theme_font_size_override("font_size", HINT_FONT_SIZE)
	_hint.add_theme_color_override("font_color", Color(0.6, 0.6, 0.65))
	add_child(_hint)


## Repopulate and re-sync to what is actually playing. Called on every pause-menu open,
## because doom moves while the menu is closed and a stale readout here would be a lie
## about the one thing this panel exists to report.
func refresh() -> void:
	if _picker == null or not is_instance_valid(MusicManager):
		return
	_applying = true
	_picker.clear()
	for entry in MusicManager.player_catalogue():
		_picker.add_item(String(entry.get("label", "?")))
		_picker.set_item_metadata(_picker.item_count - 1, entry)
	var idx: int = MusicManager.player_catalogue_index()
	if idx >= 0 and idx < _picker.item_count:
		_picker.select(idx)
	_applying = false
	_refresh_status()


func _on_item_selected(index: int) -> void:
	if _applying or not is_instance_valid(MusicManager):
		return
	var meta = _picker.get_item_metadata(index)
	if not (meta is Dictionary):
		return
	MusicManager.apply_catalogue_entry(meta)
	_refresh_status()


func _refresh_status() -> void:
	if _status == null or not is_instance_valid(MusicManager):
		return
	_status.text = MusicManager.player_status_line()

class_name WatchScreen
extends VBoxContainer
## WATCH screen (BUILD_BRIEF_PLAN_WATCH_UI Lane 1) — the tactics register: the committed
## month plays out in day-ticks. Owns the feed (dated event entries / message log). The
## playback control strip and the mid-month response-window overlays are built in code by
## ScreenModeController / event_dialog and mounted separately; the shared instruments (doom,
## roster) and the in-flight queue live in the InstrumentPanel, visible in both modes.
## Extracted from the main_ui monolith — main_ui logs into message_log via the public member.

@onready var message_log_label: Label = $MessageLogLabel
@onready var message_scroll: ScrollContainer = $MessageScroll
@onready var message_log: RichTextLabel = $MessageScroll/MessageLog

## P0 feed filter (playtest 2026-07-17): toggled ON = hide the low-severity arxiv/flavour
## stream that floods the feed; OFF = show everything. main_ui listens and re-renders.
signal feed_filter_changed(important_only: bool)
var feed_filter_button: CheckButton

## Rival-intel filter (v0 News feedline / DQ-32): toggled ON = hide the "rivals" channel
## lines. Preference persists via GameConfig.show_rivals_feed; main_ui listens and re-renders.
signal rivals_filter_changed(hide_rivals: bool)
var rivals_filter_button: CheckButton


func _ready() -> void:
	# The feed reads in the terminal register: monospace, dim phosphor text.
	TerminalTheme.style_feed(message_log)
	message_log_label.add_theme_color_override("font_color", TerminalTheme.GREEN_DIM)
	message_log_label.text = "Feed — the month as it happens:"

	# P0: a cheap "All / Important" filter for the feed. Default ON so the arxiv-flavour
	# spam is collapsed and real events stay legible; the player can flip it to see the lot.
	feed_filter_button = CheckButton.new()
	feed_filter_button.text = "Hide arxiv flood"
	feed_filter_button.button_pressed = true
	feed_filter_button.tooltip_text = "Collapse the low-severity arxiv/research-flavour feed stream"
	feed_filter_button.add_theme_color_override("font_color", TerminalTheme.GREEN_DIM)
	feed_filter_button.toggled.connect(func(on: bool): feed_filter_changed.emit(on))
	add_child(feed_filter_button)
	move_child(feed_filter_button, message_log_label.get_index() + 1)

	# Rival-intel filter: reflect the persisted preference (show_rivals_feed ON -> unpressed).
	rivals_filter_button = CheckButton.new()
	rivals_filter_button.text = "Hide rival intel"
	rivals_filter_button.button_pressed = not GameConfig.show_rivals_feed
	rivals_filter_button.tooltip_text = "Collapse rival-lab intel lines in the feed"
	rivals_filter_button.add_theme_color_override("font_color", TerminalTheme.GREEN_DIM)
	rivals_filter_button.toggled.connect(func(hide: bool): rivals_filter_changed.emit(hide))
	add_child(rivals_filter_button)
	move_child(rivals_filter_button, feed_filter_button.get_index() + 1)

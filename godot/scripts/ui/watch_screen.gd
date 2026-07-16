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


func _ready() -> void:
	# The feed reads in the terminal register: monospace, dim phosphor text.
	TerminalTheme.style_feed(message_log)
	message_log_label.add_theme_color_override("font_color", TerminalTheme.GREEN_DIM)
	message_log_label.text = "Feed — the month as it happens:"

extends Node
## Notification Manager - Toast-style notifications with animations

enum NotificationType {
	INFO,
	SUCCESS,
	WARNING,
	ERROR,
	ACHIEVEMENT
}

const NOTIFICATION_DURATION = 3.0
const SLIDE_DURATION = 0.3
const MAX_NOTIFICATIONS = 5

var active_notifications: Array = []
var notification_queue: Array = []

func _ready():
	print("[NotificationManager] Ready")

## Show a notification
func show_notification(message: String, type: NotificationType = NotificationType.INFO, duration: float = NOTIFICATION_DURATION):
	var notification_data = {
		"message": message,
		"type": type,
		"duration": duration
	}

	# If too many active, queue it
	if active_notifications.size() >= MAX_NOTIFICATIONS:
		notification_queue.append(notification_data)
		return

	_create_notification(notification_data)

## Create and display a notification
func _create_notification(data: Dictionary):
	var notif_panel = _build_notification_panel(data)

	# Position off-screen right BEFORE entering the tree, so the settle frame
	# below never flashes an unpositioned panel at (0, 0).
	var offset_y = 20 + (active_notifications.size() * 90)
	notif_panel.position = Vector2(
		get_viewport().get_visible_rect().size.x + 400,  # Start off-screen right
		offset_y
	)

	# Add to root
	get_tree().root.add_child(notif_panel)

	# Track it
	active_notifications.append(notif_panel)

	# v0.13.2 giant-purple-toast fix: collapse any degenerate first-layout
	# inflation before the panel becomes visible (see _settle_toast_size).
	await _settle_toast_size(notif_panel)
	if not is_instance_valid(notif_panel):
		return

	# Slide in animation
	var slide_in_pos = Vector2(
		get_viewport().get_visible_rect().size.x - 420,  # 20px from right edge
		offset_y
	)

	var tween = create_tween()
	tween.tween_property(notif_panel, "position", slide_in_pos, SLIDE_DURATION).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

	# Wait out the duration, or leave early if the player clicks the toast.
	var waited := 0.0
	while waited < float(data["duration"]):
		await get_tree().create_timer(0.1).timeout
		waited += 0.1
		if not is_instance_valid(notif_panel):
			active_notifications.erase(notif_panel)
			return
		if bool(notif_panel.get_meta("dismiss_early", false)):
			break

	var slide_out_pos = Vector2(
		get_viewport().get_visible_rect().size.x + 400,
		notif_panel.position.y
	)

	var tween_out = create_tween()
	tween_out.tween_property(notif_panel, "position", slide_out_pos, SLIDE_DURATION).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)

	await tween_out.finished

	# Remove
	active_notifications.erase(notif_panel)
	notif_panel.queue_free()

	# Reposition remaining notifications
	_reposition_notifications()

	# Show next queued
	if notification_queue.size() > 0:
		_create_notification(notification_queue.pop_front())

## Settle a toast back to its content size after the first layout tick.
##
## WHY (the v0.13.2 "giant purple rectangle" bug): the message Label autowraps
## (WORD_SMART breaks words that do not fit the line). On the FIRST layout pass
## the label's width can measure as ~zero, so a 36-char message wraps one glyph
## per line and reports a ~950px minimum height; the PanelContainer inflates to
## fit. Because the toast is a ROOT-level Control (child of the Window, not of
## any container), nothing ever re-lays it out when the minimum collapses on
## the next pass -- Controls keep their current size when their minimum
## shrinks -- so the inflated size stuck for the toast's whole 5s lifetime.
## One frame later the label has its real width, so resetting to the combined
## minimum yields the correct compact size (including legit multi-line wraps).
func _settle_toast_size(panel: Control) -> void:
	await get_tree().process_frame
	if is_instance_valid(panel):
		panel.reset_size()

## Click-to-dismiss: any mouse press on the toast ends its wait loop early.
func _on_toast_gui_input(event: InputEvent, panel: Control) -> void:
	if event is InputEventMouseButton and event.pressed:
		panel.set_meta("dismiss_early", true)

## Build notification panel
func _build_notification_panel(data: Dictionary) -> PanelContainer:
	var panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(400, 70)
	panel.gui_input.connect(_on_toast_gui_input.bind(panel))

	# Style the panel
	var style = StyleBoxFlat.new()
	style.bg_color = _get_notification_color(data["type"])
	style.border_color = _get_notification_border_color(data["type"])
	style.border_width_left = 4
	style.border_width_top = 2
	style.border_width_right = 2
	style.border_width_bottom = 2
	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8
	style.content_margin_left = 15
	style.content_margin_top = 10
	style.content_margin_right = 15
	style.content_margin_bottom = 10

	panel.add_theme_stylebox_override("panel", style)

	# Add content
	var hbox = HBoxContainer.new()
	hbox.add_theme_constant_override("separation", 10)

	# Icon -- tinted to the type's border colour so the chrome reads deliberate
	var icon_label = Label.new()
	icon_label.text = _get_notification_icon(data["type"])
	icon_label.add_theme_font_size_override("font_size", 24)
	icon_label.add_theme_color_override("font_color", _get_notification_border_color(data["type"]))
	hbox.add_child(icon_label)

	# Message. The pinned minimum width keeps the autowrap measurement sane:
	# without it, a degenerate ~zero-width first pass wraps one glyph per line
	# (see _settle_toast_size). 330 fits inside the 400px panel minus margins,
	# icon and separation, so it never widens the toast.
	var message_label = Label.new()
	message_label.text = data["message"]
	message_label.custom_minimum_size = Vector2(330, 0)
	message_label.add_theme_font_size_override("font_size", ThemeManager.get_font_size("body"))
	message_label.add_theme_color_override("font_color", Color.WHITE)
	message_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	message_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hbox.add_child(message_label)

	panel.add_child(hbox)

	return panel

## Get notification background color
func _get_notification_color(type: NotificationType) -> Color:
	match type:
		NotificationType.SUCCESS:
			return ThemeManager.get_color("success").darkened(0.3)
		NotificationType.WARNING:
			return ThemeManager.get_color("warning").darkened(0.3)
		NotificationType.ERROR:
			return ThemeManager.get_color("error").darkened(0.3)
		NotificationType.ACHIEVEMENT:
			# Recognition register: dark leather + amber, matching the Liability
			# Ledger chrome (ledger_screen.gd) and the #743 menu palette. The old
			# debug-looking Color(0.5, 0.3, 0.8) purple is retired.
			return Color(0.16, 0.11, 0.07, 0.97)
		_:
			return ThemeManager.get_color("panel")

## Get notification border color
func _get_notification_border_color(type: NotificationType) -> Color:
	match type:
		NotificationType.SUCCESS:
			return ThemeManager.get_color("success")
		NotificationType.WARNING:
			return ThemeManager.get_color("warning")
		NotificationType.ERROR:
			return ThemeManager.get_color("error")
		NotificationType.ACHIEVEMENT:
			return Color(0.91, 0.64, 0.24)  # house amber (menu register, #743)
		_:
			return ThemeManager.get_color("accent")

## Get notification icon
func _get_notification_icon(type: NotificationType) -> String:
	match type:
		NotificationType.SUCCESS:
			return "[OK]"
		NotificationType.WARNING:
			return "[!]"
		NotificationType.ERROR:
			return "[X]"
		NotificationType.ACHIEVEMENT:
			return "*"
		_:
			return "[i]"

## Reposition all active notifications
func _reposition_notifications():
	for i in range(active_notifications.size()):
		var notif = active_notifications[i]
		var target_y = 20 + (i * 90)

		var tween = create_tween()
		tween.tween_property(notif, "position:y", target_y, 0.2).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

## Quick helper methods
func success(message: String):
	show_notification(message, NotificationType.SUCCESS)

func warning(message: String):
	show_notification(message, NotificationType.WARNING)

func error(message: String):
	show_notification(message, NotificationType.ERROR)

func info(message: String):
	show_notification(message, NotificationType.INFO)

func achievement(message: String):
	show_notification(message, NotificationType.ACHIEVEMENT, 5.0)  # Longer duration

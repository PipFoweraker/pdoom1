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
	var notification = _build_notification_panel(data)

	# Add to root
	get_tree().root.add_child(notification)

	# Position at top-right, offset by number of active notifications
	var offset_y = 20 + (active_notifications.size() * 90)
	notification.position = Vector2(
		get_viewport().get_visible_rect().size.x + 400,  # Start off-screen right
		offset_y
	)

	# Track it
	active_notifications.append(notification)

	# Slide in animation
	var slide_in_pos = Vector2(
		get_viewport().get_visible_rect().size.x - 420,  # 20px from right edge
		offset_y
	)

	var tween = create_tween()
	tween.tween_property(notification, "position", slide_in_pos, SLIDE_DURATION).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

	# Wait, then slide out
	await get_tree().create_timer(data["duration"]).timeout

	var slide_out_pos = Vector2(
		get_viewport().get_visible_rect().size.x + 400,
		notification.position.y
	)

	var tween_out = create_tween()
	tween_out.tween_property(notification, "position", slide_out_pos, SLIDE_DURATION).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN)

	await tween_out.finished

	# Remove
	active_notifications.erase(notification)
	notification.queue_free()

	# Reposition remaining notifications
	_reposition_notifications()

	# Show next queued
	if notification_queue.size() > 0:
		_create_notification(notification_queue.pop_front())

## Build notification panel
func _build_notification_panel(data: Dictionary) -> PanelContainer:
	var panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(400, 70)

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

	# Icon
	var icon_label = Label.new()
	icon_label.text = _get_notification_icon(data["type"])
	icon_label.add_theme_font_size_override("font_size", 24)
	hbox.add_child(icon_label)

	# Message
	var message_label = Label.new()
	message_label.text = data["message"]
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
			return Color(0.5, 0.3, 0.8, 0.95)  # Purple
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
			return Color(0.8, 0.5, 1.0)
		_:
			return ThemeManager.get_color("accent")

## Get notification icon
func _get_notification_icon(type: NotificationType) -> String:
	match type:
		NotificationType.SUCCESS:
			return "✓"
		NotificationType.WARNING:
			return "⚠"
		NotificationType.ERROR:
			return "✗"
		NotificationType.ACHIEVEMENT:
			return "★"
		_:
			return "ℹ"

## Reposition all active notifications
func _reposition_notifications():
	for i in range(active_notifications.size()):
		var notification = active_notifications[i]
		var target_y = 20 + (i * 90)

		var tween = create_tween()
		tween.tween_property(notification, "position:y", target_y, 0.2).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

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

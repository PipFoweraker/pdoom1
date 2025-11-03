# UI Polish & Components Guide

## Overview
Comprehensive UI improvements with theme integration, notifications, and reusable components.

## New Components

### 1. Enhanced Message Log (`enhanced_message_log.gd`)
Rich text message log with styled, categorized messages.

**Features:**
- Message type styling (success, warning, error, info, action, event, doom)
- Optional timestamps
- Auto-scrolling
- Message limits (auto-trim old messages)
- Icons/prefixes per message type
- Separators and headers

**Usage:**
```gdscript
var message_log = EnhancedMessageLog.new()
message_log.add_message("Research complete!", "success")
message_log.add_message("Doom rising...", "doom")
message_log.add_header("TURN 5")
message_log.add_separator()
```

**Message Types:**
- `success` / `positive` - Green with ✓
- `warning` / `caution` - Yellow with ⚠
- `error` / `danger` - Red with ✗
- `info` - White with ℹ
- `action` - Light blue with →
- `event` - Gold with ★
- `doom` - Red with ☠
- `system` / `phase` - Accent color

### 2. Resource Bar (`resource_bar.gd`)
Visual resource display with icons, labels, and optional progress bars.

**Features:**
- Icon support (loads from ThemeManager)
- Name + value labels
- Optional progress bar
- Theme-aware styling
- Special formatting per resource type

**Usage:**
```gdscript
var money_bar = ResourceBar.new()
money_bar.resource_name = "Money"
money_bar.resource_key = "money"
money_bar.show_icon = true
money_bar.show_progress_bar = false
add_child(money_bar)

money_bar.set_value(5000.0)
```

**Supports:**
- money ($X formatting)
- doom (X% formatting + color coding)
- research/compute (decimal formatting)
- Generic resources

### 3. Resource Display (`resource_display.gd`)
Enhanced resource panel with theme integration.

**Features:**
- Centralized resource tracking
- Theme-aware colors
- Automatic doom color-coding
- Extensible for icons/progress bars

### 4. Notification System (`notification_manager.gd`)
Toast-style notifications with slide animations.

**Features:**
- 5 notification types (info, success, warning, error, achievement)
- Slide-in/slide-out animations
- Auto-stacking (up to 5 visible)
- Queueing for overflow
- Color-coded borders and backgrounds
- Icons per type

**Usage:**
```gdscript
# Quick helpers
NotificationManager.success("Game saved!")
NotificationManager.warning("Low funds")
NotificationManager.error("Action failed")
NotificationManager.info("Turn started")
NotificationManager.achievement("First victory!")

# Full control
NotificationManager.show_notification(
	"Custom message",
	NotificationManager.NotificationType.SUCCESS,
	5.0  # Duration in seconds
)
```

**Notification Types:**
- INFO: ℹ, Gray/blue background
- SUCCESS: ✓, Green background
- WARNING: ⚠, Yellow background
- ERROR: ✗, Red background
- ACHIEVEMENT: ★, Purple background

## Theme Integration

All components use `ThemeManager` for consistent styling:

### Colors
```gdscript
ThemeManager.get_color("background")
ThemeManager.get_color("text")
ThemeManager.get_doom_color(doom_percent)  # Auto-selects color
```

### Fonts
```gdscript
ThemeManager.get_font_size("title")   # 32
ThemeManager.get_font_size("header")  # 24
ThemeManager.get_font_size("body")    # 16
ThemeManager.get_font_size("small")   # 12
```

### Spacing
```gdscript
ThemeManager.get_spacing("margin")        # 20
ThemeManager.get_spacing("padding")       # 10
ThemeManager.get_spacing("gap")           # 5
ThemeManager.get_spacing("button_height") # 50
```

### Styled Components
```gdscript
# Create themed UI elements
var button = ThemeManager.create_button("Click Me", Vector2(200, 50))
var panel = ThemeManager.create_panel(Vector2(400, 300))
var label = ThemeManager.create_label("Hello", "header")

# Or apply theme to existing elements
ThemeManager.apply_button_style(existing_button)
ThemeManager.apply_panel_style(existing_panel, dark=true)
ThemeManager.apply_label_style(existing_label, "body")
```

## Main UI Updates

### Doom Color Coding
Changed from hardcoded colors to `ThemeManager.get_doom_color()`:
- < 30%: Green
- 30-60%: Yellow
- 60-85%: Orange
- > 85%: Red

### Action Buttons
Now created with `ThemeManager.create_button()`:
- Consistent styling across all buttons
- Theme-aware colors
- Proper hover/press states

## Integration with Existing Systems

### Screenshot Manager
- Now uses `NotificationManager.success()` instead of custom overlay
- Cleaner, more consistent UX

### Log Exporter
- Uses `NotificationManager.success()` for export confirmation
- Removed duplicate notification code

## Animation & Visual Feedback

### Notification Animations
- **Slide-in**: 0.3s cubic ease-out from right
- **Hold**: Configurable duration (default 3s)
- **Slide-out**: 0.3s cubic ease-in to right
- **Reposition**: 0.2s when other notifications dismiss

### Future Enhancements
- Button hover scale effects
- Resource bar fill animations
- Doom meter pulse at high values
- Panel fade-in on scene load
- Action confirmation overlays

## Best Practices

1. **Always use ThemeManager** for colors/fonts/spacing
2. **Use NotificationManager** for user feedback
3. **Prefer themed components** over custom UI
4. **Connect to theme_changed signal** for dynamic theming
5. **Test with all themes** (default, retro, high_contrast)

## Example: Complete Themed Panel

```gdscript
extends Control

func _ready():
	# Create themed panel
	var panel = ThemeManager.create_panel(Vector2(600, 400))
	add_child(panel)

	# Add content container
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", ThemeManager.get_spacing("gap"))
	panel.add_child(vbox)

	# Title
	var title = ThemeManager.create_label("Game Stats", "header")
	vbox.add_child(title)

	# Resource bars
	for resource in ["money", "compute", "research"]:
		var bar = ResourceBar.new()
		bar.resource_name = resource.capitalize()
		bar.resource_key = resource
		bar.show_icon = true
		vbox.add_child(bar)

	# Action button
	var button = ThemeManager.create_button("Save Game")
	button.pressed.connect(func():
		NotificationManager.success("Game saved!")
	)
	vbox.add_child(button)
```

## Files

**Components:**
- `godot/scripts/ui/enhanced_message_log.gd`
- `godot/scripts/ui/resource_bar.gd`
- `godot/scripts/ui/resource_display.gd`

**Systems:**
- `godot/autoload/theme_manager.gd`
- `godot/autoload/notification_manager.gd`

**Integration:**
- `godot/scripts/ui/main_ui.gd` (updated to use ThemeManager)
- `godot/autoload/screenshot_manager.gd` (updated for NotificationManager)
- `godot/autoload/log_exporter.gd` (updated for NotificationManager)

## Next Steps

- [ ] Apply ResourceBar to main game UI
- [ ] Replace message_log with EnhancedMessageLog
- [ ] Add button hover effects
- [ ] Create resource icons
- [ ] Add progress bars for research/doom
- [ ] Implement panel transitions
- [ ] Add sound effects per notification type

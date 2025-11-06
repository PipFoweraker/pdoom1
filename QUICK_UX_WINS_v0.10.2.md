# Quick UX Wins for v0.10.2

**Goal:** Drive-by improvements to enhance player experience before v0.10.1 release
**Time Budget:** 30-45 minutes of focused changes
**Risk Level:** Low (UI/validation improvements, no core logic changes)

---

## Priority 1: Critical Fixes (Must Have)

### 1. Prevent Action Overcommitment
**Problem:** Players can queue more actions than they have AP for
**Location:** `godot/scripts/game_manager.gd:60` (`select_action()`)
**Current Logic:** Checks `state.action_points < ap_cost` (available AP)
**New Logic:** Check `(state.action_points - state.committed_ap) < ap_cost` (remaining AP)

**Code Change:**
```gdscript
# Line 107: Change from
if state.action_points < ap_cost:

# To:
var available_ap = state.action_points - state.committed_ap
if available_ap < ap_cost:
```

**Also update error message (line 118):**
```gdscript
error_occurred.emit("Not enough AP: %d needed, %d remaining" % [ap_cost, available_ap])
```

---

## Priority 2: UI Clarity (High Impact, Low Effort)

### 2. Rename "End Turn" → "Commit Actions"
**Rationale:** Players are committing their action queue, not ending the turn yet
**Files:**
- `godot/scenes/main.tscn:260` - Change button text
- `godot/scripts/ui/main_ui.gd:23` - Rename variable (optional, but clean)
- `godot/scripts/ui/main_ui.gd:143` - Update keyboard shortcut hint

**Changes:**
```gdscript
# main.tscn line 260:
text = "Commit Actions (Space)"

# main_ui.gd line 60 (hint):
log_message("[color=gray]Keyboard: 1-9 for actions, Space to commit[/color]")
```

### 3. Make AP Counter More Prominent
**Problem:** Players don't notice when they're low on AP
**Location:** `godot/scripts/ui/main_ui.gd` - `_on_game_state_updated()`
**Enhancement:** Color-code AP label based on remaining AP

**Find the AP label update (search for `ap_label.text`) and add:**
```gdscript
# After setting ap_label.text:
var remaining_ap = state.action_points - state.committed_ap
if remaining_ap <= 0:
    ap_label.add_theme_color_override("font_color", Color(0.8, 0.2, 0.2))  # Red
elif remaining_ap == 1:
    ap_label.add_theme_color_override("font_color", Color(0.9, 0.7, 0.2))  # Yellow
else:
    ap_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))  # White
```

### 4. Show Remaining AP in Display
**Location:** Same as above
**Change:** Show "AP: 3 (1 remaining)" instead of just "AP: 3"

```gdscript
# Find ap_label.text = ... and change to:
var remaining = state.action_points - state.committed_ap
ap_label.text = "AP: %d (%d free)" % [state.action_points, remaining]
```

---

## Priority 3: Queue Management (Quick Win)

### 5. Add "Clear Queue" Button
**Location:** `godot/scenes/main.tscn` - Add button next to "Commit Actions"
**Functionality:** Remove all queued actions, refund AP

**Add to main.tscn (near line 258):**
```gdscript
[node name="ClearQueueButton" type="Button" parent="MainUI/BottomBar/ControlButtons"]
layout_mode = 2
text = "Clear Queue (X)"
disabled = true
```

**Add to main_ui.gd:**
```gdscript
@onready var clear_queue_button = $BottomBar/ControlButtons/ClearQueueButton

func _on_clear_queue_button_pressed():
    """Clear all queued actions and refund AP"""
    if queued_actions.size() == 0:
        return

    # Call GameManager to clear queue (refunds AP)
    game_manager.clear_action_queue()

    # Update local display
    queued_actions.clear()
    update_queued_actions_display()

    log_message("[color=yellow]Action queue cleared[/color]")

# Update button state in _on_game_state_updated():
clear_queue_button.disabled = (queued_actions.size() == 0)
```

**Add to game_manager.gd:**
```gdscript
func clear_action_queue():
    """Clear all queued actions and refund committed AP"""
    var refunded_ap = state.committed_ap
    state.queued_actions.clear()
    state.committed_ap = 0

    print("[GameManager] Queue cleared, refunded %d AP" % refunded_ap)
    game_state_updated.emit(state)
```

### 6. Add Remove Button to Queue Items
**Location:** `godot/scripts/ui/main_ui.gd:884` (`update_queued_actions_display()`)
**Enhancement:** Add small "X" button to each queued action

**Add after line 925 (after creating vbox):**
```gdscript
# Add remove button
var remove_btn = Button.new()
remove_btn.text = "X"
remove_btn.custom_minimum_size = Vector2(20, 20)
remove_btn.add_theme_font_size_override("font_size", 10)

# Capture action_id in closure
var captured_id = action_id
remove_btn.pressed.connect(func(): _remove_queued_action(captured_id))

vbox.add_child(remove_btn)
```

**Add function to main_ui.gd:**
```gdscript
func _remove_queued_action(action_id: String):
    """Remove a specific action from the queue"""
    for i in range(queued_actions.size()):
        if queued_actions[i].get("id") == action_id:
            var action = queued_actions[i]
            var ap_cost = action.get("costs", {}).get("action_points", 0)

            # Remove from local queue
            queued_actions.remove_at(i)

            # Tell GameManager to refund AP and update state queue
            game_manager.remove_queued_action(action_id)

            log_message("[color=yellow]Removed: %s (+%d AP)[/color]" % [action.get("name"), ap_cost])
            update_queued_actions_display()
            break
```

**Add to game_manager.gd:**
```gdscript
func remove_queued_action(action_id: String):
    """Remove specific action from queue and refund AP"""
    for i in range(state.queued_actions.size()):
        if state.queued_actions[i] == action_id:
            # Get AP cost
            var action = _get_action_by_id(action_id)
            var ap_cost = action.get("costs", {}).get("action_points", 0)

            # Remove and refund
            state.queued_actions.remove_at(i)
            state.committed_ap -= ap_cost

            print("[GameManager] Removed %s from queue, refunded %d AP" % [action_id, ap_cost])
            game_state_updated.emit(state)
            break
```

---

## Priority 4: Turn Progression Visibility (Medium Effort)

### 7. Add Turn Phase Indicator
**Location:** `godot/scripts/ui/main_ui.gd:12` - PhaseLabel already exists!
**Enhancement:** Make it more prominent and descriptive

**Update `_on_turn_phase_changed()` (search for it):**
```gdscript
func _on_turn_phase_changed(phase: String):
    current_turn_phase = phase

    # Update phase label with color coding
    match phase:
        "ACTION_SELECTION":
            phase_label.text = "📋 Planning Phase - Select Actions"
            phase_label.add_theme_color_override("font_color", Color(0.5, 0.8, 1.0))
        "TURN_PROCESSING":
            phase_label.text = "⚙️ Processing Turn..."
            phase_label.add_theme_color_override("font_color", Color(0.9, 0.7, 0.2))
        "TURN_END":
            phase_label.text = "✓ Turn Complete"
            phase_label.add_theme_color_override("font_color", Color(0.5, 1.0, 0.5))
        _:
            phase_label.text = "Phase: " + phase
```

---

## Priority 5: Future Enhancements (Post v0.10.1)

### 8. UI Customization System (Future)
**Idea:** Unlock UI themes/layouts when purchasing office upgrades
**Implementation:**
- Create `ThemeUnlocks` resource with themes per office level
- Store unlocked themes in `GameState.purchased_upgrades`
- Apply via `ThemeManager` autoload

**Placeholder for now:** Add comment to theme_manager.gd

### 9. Drag-and-Drop Queue Reordering (Future)
**Idea:** Players can reorder queued actions
**Complexity:** Medium (requires Godot drag-drop implementation)
**Impact:** High (players love this)

### 10. Action Preview Tooltips (Quick Win for v0.10.2)
**Enhancement:** Show full costs/effects on hover
**Location:** Action button creation in `main_ui.gd`

---

## Implementation Order (For Tonight)

1. ✅ **Fix overcommitment bug** (5 min) - Critical
2. ✅ **Rename "End Turn" → "Commit Actions"** (2 min) - High impact
3. ✅ **Color-code AP counter** (3 min) - High visibility
4. ✅ **Show remaining AP in counter** (2 min) - Clarity
5. ✅ **Add "Clear Queue" button** (10 min) - Player control
6. ⏸️ **Add remove buttons to queue items** (15 min) - Nice to have
7. ⏸️ **Enhance phase indicator** (5 min) - Polish

**Total: ~25-40 minutes for items 1-5, 40-60 for all 7**

---

## Testing Checklist

After implementing:
- [ ] Try to queue 4 actions with only 3 AP → Should block after 3
- [ ] Remove action from queue → AP refunded
- [ ] Clear queue → All AP refunded
- [ ] AP counter shows correct remaining AP
- [ ] AP counter turns red when depleted
- [ ] "Commit Actions" button text updated
- [ ] Phase indicator shows current phase clearly

---

## Files to Modify

1. `godot/scripts/game_manager.gd` - Add validation, clear/remove functions
2. `godot/scripts/ui/main_ui.gd` - UI updates, button handlers
3. `godot/scenes/main.tscn` - Add Clear Queue button, rename End Turn
4. (Optional) `godot/scripts/core/game_state.gd` - No changes needed (committed_ap already exists!)

**Estimated Risk:** Very Low
**Estimated Impact:** High (players will immediately notice better UX)
**Release Target:** v0.10.2 (can be done tonight after v0.10.1 export)

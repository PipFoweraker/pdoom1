# Keyboard Shortcuts Testing Guide

## Overview
This document outlines the testing procedure for keyboard shortcuts in P(Doom) Godot version.

## Test Philosophy
- **Test incrementally**: After each UI change, verify keyboard shortcuts still work
- **Document expected behavior**: Each shortcut should have clear expected outcome
- **Machine-readable logs**: Use debug output to verify shortcuts are being caught

## Main Game Screen

### Number Keys (1-9) - Action Selection
| Key | Action | Expected Behavior | Debug Output |
|-----|--------|------------------|--------------|
| 1 | First action | Selects/queues first available action | `[MainUI] _input called, keycode: 49` |
| 2 | Second action | Selects/queues second available action | `[MainUI] _input called, keycode: 50` |
| 3-9 | Nth action | Selects corresponding action | `[MainUI] _input called, keycode: 51-57` |

**Test Procedure:**
1. Launch game (F5)
2. Press 1 - Should queue "Hire Safety Researcher" or first action
3. Check message log shows action queued
4. Check action queue panel shows action
5. Verify debug output shows keycode received

### Special Keys - Game Control
| Key | Action | Expected Behavior | Debug Output |
|-----|--------|------------------|--------------|
| SPACE | End Turn | Ends current turn if actions queued | `[MainUI] _input called, keycode: 32` |
| ENTER | End Turn | Same as SPACE | `[MainUI] _input called, keycode: 16777221` |
| ESC | Cancel/Init | Context-dependent (init game or cancel) | `[MainUI] _input called, keycode: 16777217` |

## Dialog Submenus

### Letter Keys (Q/W/E/R/A/S/D/F/Z) - Dialog Options
**Contexts:** Hiring submenu, Fundraising submenu, any popup dialogs

| Key | Action | Expected Behavior | Debug Output |
|-----|--------|------------------|--------------|
| Q | First option | Selects first dialog button | `[MainUI] Dialog letter key pressed, index: 0` |
| W | Second option | Selects second dialog button | `[MainUI] Dialog letter key pressed, index: 1` |
| E | Third option | Selects third dialog button | `[MainUI] Dialog letter key pressed, index: 2` |
| R | Fourth option | Selects fourth dialog button | `[MainUI] Dialog letter key pressed, index: 3` |
| A-F,Z | 5th-9th options | Selects corresponding option | `[MainUI] Dialog letter key pressed, index: 4-8` |

**Test Procedure:**
1. Open dialog (click "Hire Staff" or press number for action)
2. Verify first button has focus (highlighted)
3. Press Q - should trigger first option
4. Verify action executed (money deducted, employee hired, etc.)
5. Check debug output confirms key caught

### Arrow Keys - Dialog Navigation
| Key | Action | Expected Behavior |
|-----|--------|------------------|
| UP/DOWN | Navigate | Changes which button has focus |
| ENTER | Activate | Triggers focused button |
| ESC | Close | Closes dialog without action |

## Common Issues & Solutions

### Issue: Letter keys don't work in dialogs
**Symptoms:**
- Arrow keys and ENTER work
- Letters Q/W/E do nothing
- Buttons show [Q] [W] [E] labels

**Root Cause:** Buttons consume letter key events when focused

**Solution:** Handle letter keys in `_input()` before buttons consume them
```gdscript
func _input(event: InputEvent):
    if active_dialog != null:
        var dialog_keys = [KEY_Q, KEY_W, KEY_E, ...]
        var key_index = dialog_keys.find(event.keycode)
        if key_index >= 0:
            active_dialog_buttons[key_index].pressed.emit()
            get_viewport().set_input_as_handled()
```

### Issue: Null viewport error
**Symptoms:**
- `Cannot call method 'set_input_as_handled' on a null value`
- Happens during scene initialization

**Solution:** Add null check
```gdscript
var viewport = get_viewport()
if viewport:
    viewport.set_input_as_handled()
```

### Issue: Dialog doesn't receive keyboard input
**Symptoms:**
- Dialog opens but keyboard does nothing
- Dialog is draggable (indicating it's a Window)

**Solution:** Grab focus when dialog opens
```gdscript
dialog.popup_centered()
await get_tree().process_frame
if buttons.size() > 0:
    buttons[0].grab_focus()
```

## Debug Output Reference

### Normal Flow (Working)
```
[MainUI] _input called, keycode: 49, active_dialog: false
[MainUI] Triggering action by index: 0
[MainUI] _input called, keycode: 81, active_dialog: true
[MainUI] Dialog is active, buttons count: 3
[MainUI] Dialog letter key pressed, index: 0, buttons: 3
[MainUI] Triggering dialog button: [Q] Safety Researcher ($50k, 1 AP)
```

### Broken Flow (Not Working)
```
[MainUI] _input called, keycode: 81, active_dialog: true
[MainUI] Dialog is active, buttons count: 3
# No "Dialog letter key pressed" message = letter keys not caught
```

## Automated Testing (Future)

### GUT Test Structure
```gdscript
# test_keyboard_shortcuts.gd
extends GutTest

func test_action_selection_with_number_keys():
    var main_ui = load("res://scenes/main.tscn").instantiate()
    add_child(main_ui)

    # Simulate pressing '1'
    var event = InputEventKey.new()
    event.keycode = KEY_1
    event.pressed = true
    main_ui._input(event)

    # Assert action was queued
    assert_eq(main_ui.queued_actions.size(), 1)

func test_dialog_letter_keys():
    var main_ui = load("res://scenes/main.tscn").instantiate()
    add_child(main_ui)

    # Open hiring dialog
    main_ui._show_hiring_submenu()
    await get_tree().process_frame

    # Press Q
    var event = InputEventKey.new()
    event.keycode = KEY_Q
    event.pressed = true
    main_ui._input(event)

    # Assert option selected
    assert_true(main_ui.active_dialog == null)  # Dialog closed
    assert_eq(main_ui.queued_actions.size(), 1)
```

## Test Checklist

Before declaring keyboard shortcuts "working":

- [ ] Number keys 1-9 select actions in main screen
- [ ] SPACE/ENTER ends turn
- [ ] ESC cancels/closes appropriately
- [ ] Dialog opens with first button focused
- [ ] Letter keys Q/W/E/R/A/S/D/F/Z trigger dialog options
- [ ] Arrow keys navigate dialog buttons
- [ ] ENTER activates focused dialog button
- [ ] ESC closes dialog
- [ ] No null viewport errors in console
- [ ] Debug output confirms keys are caught
- [ ] Actions execute correctly (money deducted, items added, etc.)

## Manual Test Script

Run this every time keyboard changes are made:

1. **Launch game** (F5)
2. **Main screen test:**
   - Press 1  ->  First action queued
   - Press SPACE  ->  Turn ends
3. **Dialog test:**
   - Press 1  ->  Opens hiring dialog
   - First button highlighted
   - Press Q  ->  Hires first employee
   - Check money deducted
4. **Repeat for fundraising:**
   - Press number for Fundraising
   - Press Q  ->  Money increases, reputation decreases
5. **Check Output console:**
   - No errors
   - See debug messages confirming keys caught

## Success Criteria

Keyboard shortcuts are considered "fully working" when:
1. All keys listed above function as expected
2. No errors in Output console
3. Debug output confirms keys are being caught
4. Actions execute with correct side effects
5. Can complete entire game using only keyboard (no mouse)

---
*Last Updated: 2025-11-03*
*Related Issues: #423 (Universal Keyboard Navigation)*

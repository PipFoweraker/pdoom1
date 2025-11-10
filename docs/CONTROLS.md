# P(Doom) Keyboard Controls

## Overview

P(Doom) features comprehensive keyboard navigation inspired by StarCraft 2. Every button has a keyboard shortcut for fast, efficient gameplay.

**Tip:** Press **F10** to access the keybind configuration screen and customize controls to your preference!

## Essential Controls

### Gameplay

| Key | Action | Description |
|-----|--------|-------------|
| **Space** | End Turn | Execute queued actions and advance to next turn |
| **Enter** | Skip Turn | Skip current turn without executing actions |
| **C** | Clear Queue | Clear all queued actions |
| **Esc** | Cancel/Back | Close dialogs, return to previous screen |

### Actions (Quick Access)

| Key | Action |
|-----|--------|
| **1-9** | Trigger Action 1-9 |

Number keys 1-9 trigger the corresponding action in the actions list. Actions are ordered top-to-bottom, so pressing **1** executes the first visible action.

**Example:**
- If "Hire Safety Researcher" is first action → Press **1**
- If "Purchase Compute" is third action → Press **3**

### UI Navigation

| Key | Action | Description |
|-----|--------|-------------|
| **Tab** | Next Tab | Switch to next UI tab |
| **Shift+Tab** | Previous Tab | Switch to previous UI tab |
| **E** | Employee Screen | Open employee management screen |
| **F8** | Bug Reporter | Open in-game bug reporter |
| **F10** | Settings | Open settings menu |

### Screenshots & Logging

| Key | Action | Description |
|-----|--------|-------------|
| **[** | Screenshot | Capture screenshot |
| **\\** | Export Log | Export game log for debugging |

### Debug & Admin (Dev Mode Only)

| Key | Action | Description |
|-----|--------|-------------|
| **~** | Debug Overlay | Toggle debug information overlay |
| **]** | Admin Mode | Toggle admin mode (dev builds) |

## Dialog Navigation

When a dialog is open (fundraising, events, etc.):

| Key | Option |
|-----|--------|
| **Q** | First option |
| **W** | Second option |
| **E** | Third option |
| **R** | Fourth option |
| **A** | Fifth option |
| **S** | Sixth option |
| **D** | Seventh option |
| **F** | Eighth option |
| **Z** | Ninth option |
| **Esc** | Close dialog |

Dialog options are mapped to convenient home-row keys for fast decision-making.

## Customization

### Accessing Keybind Settings

1. Press **F10** to open Settings
2. Navigate to "Keybindings" tab
3. Click on any action to rebind it
4. Press your desired key
5. Changes save automatically

### Keybind Profiles

P(Doom) supports multiple keybind profiles:

- **Default Profile:** Standard controls listed above
- **Custom Profiles:** Create your own profiles for different playstyles

**Creating a Profile:**
1. Open Settings → Keybindings
2. Click "New Profile"
3. Enter profile name
4. Customize keys as desired
5. Switch between profiles anytime

### Resetting Keybinds

To reset all keybinds to defaults:
1. Open Settings → Keybindings
2. Click "Reset to Defaults"
3. Confirm

## Quick Reference Card

### Essential Shortcuts

```
┌─────────────────────────────────────────┐
│         P(Doom) Quick Reference         │
├─────────────────────────────────────────┤
│ GAMEPLAY                                │
│   Space      End Turn                   │
│   Enter      Skip Turn                  │
│   1-9        Trigger Actions            │
│   C          Clear Queue                │
│                                         │
│ UI NAVIGATION                           │
│   E          Employee Screen            │
│   Tab        Next Tab                   │
│   F8         Bug Reporter               │
│   F10        Settings                   │
│   Esc        Cancel/Back                │
│                                         │
│ UTILITY                                 │
│   [          Screenshot                 │
│   \\         Export Log                 │
└─────────────────────────────────────────┘
```

## Accessibility

### Mouse-Free Gameplay

P(Doom) can be played entirely without a mouse:
- All actions have keyboard shortcuts
- Tab navigation between UI elements
- Enter to activate focused button
- Arrow keys for list navigation (where applicable)

### One-Handed Play

For one-handed play, all essential controls are accessible from the left side of the keyboard:
- Number keys (1-9) for actions
- Space for end turn
- Tab for navigation
- E for employee screen

### Customization for Accessibility

If default controls don't work for you:
1. Press F10 → Keybindings
2. Remap any action to your preferred key
3. Create a custom profile for your setup

## Tips & Tricks

### Speed Play

For fast gameplay:
1. **Learn action positions** - Memorize which number corresponds to common actions
2. **Use Space liberally** - End turn as soon as you've made decisions
3. **Dialog shortcuts** - Use Q/W/E/R for quick dialog responses
4. **Clear Queue with C** - Quickly undo accidental actions

### Efficiency Workflow

Experienced players often use this workflow:
1. **Tab** through UI sections to review state
2. **1-9** to queue multiple actions
3. **C** to clear if needed, **Space** to commit
4. **E** to check employees periodically
5. **F8** to report bugs immediately when found

### Screenshot Strategy

The **[** key captures screenshots automatically saved to:
- Windows: `%APPDATA%\Godot\app_userdata\pdoom1\screenshots\`
- Linux: `~/.local/share/godot/app_userdata/pdoom1/screenshots/`
- macOS: `~/Library/Application Support/Godot/app_userdata/pdoom1/screenshots/`

Great for:
- Capturing high scores
- Recording interesting events
- Documenting bugs (combine with F8 bug reporter!)

## Advanced: Multi-Key Bindings

Some actions support modifier keys (Shift, Ctrl, Alt):

| Combination | Action |
|-------------|--------|
| **Shift+Tab** | Previous Tab |

More modifier key combinations may be added in future updates!

## Reporting Issues

If a keyboard shortcut isn't working:
1. Press **F8** to open bug reporter
2. Describe the issue
3. Include which key isn't working
4. Attach screenshot if helpful (press **[** first!)

## Version History

- **v0.11.0:** Added F8 bug reporter, comprehensive action shortcuts (1-9)
- **v0.10.2:** Added keybind customization system
- **v0.10.0:** Initial Godot migration with basic keyboard support

---

**Can't remember a shortcut?** Most buttons show their keyboard shortcut in parentheses or tooltips!

*Last Updated: 2025-01-10*

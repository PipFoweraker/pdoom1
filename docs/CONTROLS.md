# P(Doom) keyboard controls

**Source of truth: `godot/autoload/keybind_manager.gd`.** If this page and that file ever
disagree, the file is right and this page is stale -- that has happened before (issue
#1011), which is why every key below was re-derived from the file on 2026-08-04 rather
than edited in place. The rules that decide these bindings are in
`docs/design/NAVIGATION_AUDIT.md`.

Every key here is rebindable in Settings -> Keybindings, except the reserved keys called
out at the bottom.

## Gameplay

| Key | Action | Description |
|-----|--------|-------------|
| **Space** | End Turn | Execute queued actions and advance |
| **Enter** | Commit Plan & Reserve Attention | Commit the current plan and hold remaining Attention for reactive responses. Deliberately does nothing while a dialog is open, so you cannot commit a turn by reflex while answering an event. |
| **1**-**9** | Action 1-9 | Trigger the corresponding action-bar slot, top to bottom |
| **Z** | Undo | Undo the last queued action |
| **C** | Clear Queue | Clear all queued actions |
| **V** | Toggle View | Flip between the PLAN and WATCH views |

## Menus

Each of these is a TOGGLE: the key that opens the panel also closes it. Every one of them
is also a visible button on the action bar -- no feature in this game is reachable only by
hotkey.

| Key | Panel |
|-----|-------|
| **H** | Hiring pipeline |
| **F** | Fundraising |
| **P** | Publicity |
| **T** | Travel & Conferences |
| **L** | Liability Ledger |

## UI

| Key | Action |
|-----|--------|
| **N** | Open the in-game bug reporter |
| **F10** | Settings menu |
| **F3** | Debug overlay (available in all builds) |
| **[** | Screenshot |
| **]** | Admin mode |
| **F12** | Export game log |

## Inside a dialog

Choice buttons show the key that fires them. The label on the button IS the key -- if a
button carries no letter, no key selects it.

| Key | Option |
|-----|--------|
| **Q** | First option |
| **W** | Second |
| **E** | Third |
| **R** | Fourth |
| **A** | Fifth |
| **S** | Sixth |
| **D** | Seventh |
| **F** | Eighth |
| **Z** | Ninth |
| **Esc** | Close the dialog |

Number keys **1**-**9** also work inside a dialog, but are not shown on the buttons --
outside a dialog those digits mean "action-bar slot", so the letters are what the game
advertises.

A key that names an option the dialog does not have does nothing. Pressing **R** at a
three-option event is silent, not an error.

**Event dialogs cannot be dismissed with Esc.** An event has to be answered; that is
deliberate, not a bug.

## Reserved keys

These are not rebindable, on purpose:

| Key | Why |
|-----|-----|
| **Esc** | The universal back/close key. It goes back exactly one level: it closes the topmost dialog, or leaves a sub-screen for the view that opened it, and only opens the game menu when nothing else is up. Rebinding it could leave you stuck in a panel with no way out. |
| **Tab** / **Shift+Tab** | Reserved for moving between fields in forms (like the bug reporter). No game action may claim them. |
| Dialog choice letters | These are labels printed on the buttons themselves, not standalone actions, so there is nothing stable to rebind. |

## Typing

While you are typing in any text field -- the bug report form, the seed box, your lab name
-- keyboard shortcuts are switched off, so letters go into the field instead of triggering
game actions. Click away, or press **Esc**, to get the shortcuts back.

## Customization

1. **F10** -> Keybindings
2. Click an action, press the key you want
3. Changes save automatically

Profiles: create, switch and reset to defaults from the same screen. Note that when the
game's DEFAULT bindings change in an update, saved profiles refresh to the new defaults --
otherwise a stale saved bind would silently override a new default.

## Screenshots

**[** saves to:

- Windows: `%APPDATA%\Godot\app_userdata\pdoom1\screenshots\`
- Linux: `~/.local/share/godot/app_userdata/pdoom1/screenshots/`
- macOS: `~/Library/Application Support/Godot/app_userdata/pdoom1/screenshots/`

## Dev-build-only keys

Present only in development builds; in a public build these do nothing.

| Key | Action |
|-----|--------|
| **\\** | Dev-mode overlay (state readout + dev controls) |
| **F6** | Flight recorder capture |
| **F7** | UI evolution capture |

## If a shortcut is not working

Press **N** to open the bug reporter, say which key, and attach a screenshot (press **[**
first).

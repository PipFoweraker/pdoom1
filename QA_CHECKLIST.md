# P(Doom) QA Checklist - v0.11+ Testing Session

**Tester:** _________________  **Date:** _________________  **Build:** _________________

---

## PRE-SESSION SETUP

- [ ] Game launches without errors
- [ ] Main menu displays correctly
- [ ] "What's New" / Patch Notes accessible from main menu
- [ ] Settings menu opens (F10)

---

## CORE GAMEPLAY FLOW (New Player Introduction)

### Turn 1 - Basic Actions
- [ ] Start New Game works
- [ ] Initial resources display correctly (Money, Compute, Research, Papers, Reputation)
- [ ] Action Points visible (should start with 3 AP)
- [ ] Doom meter visible and at starting value

### Hiring Staff
- [ ] Press **H** to open Hiring Menu (or click Hiring submenu)
- [ ] Can queue "Hire Safety Researcher" action
- [ ] Can queue "Hire Capability Researcher" action
- [ ] Can queue other staff types (Compute Engineer, Manager)
- [ ] Queued actions appear in action queue panel
- [ ] Turn Preview shows total costs of queued actions

### Action Queue Management
- [ ] **Undo button (Z)** removes last queued action
- [ ] Undo button disabled when queue is empty
- [ ] Clear Queue button (**C**) clears all queued actions
- [ ] Queue accepts multiple actions up to AP limit

### Executing Turn
- [ ] End Turn button (**SPACE**) executes queued actions
- [ ] Resources update correctly after turn execution
- [ ] Turn counter increments
- [ ] Message log shows action results

---

## QUICK MENU HOTKEYS

- [ ] **H** - Opens Hiring menu/submenu
- [ ] **F** - Opens Fundraising menu
- [ ] **R** - Opens Research actions
- [ ] **P** - Opens Publicity menu
- [ ] **T** - Opens Travel menu
- [ ] **Z** - Undo last queued action
- [ ] **C** - Clear action queue
- [ ] **SPACE** - End turn
- [ ] **ESC** - Cancel/Back
- [ ] **TAB** - Next tab
- [ ] **Shift+TAB** - Previous tab

---

## DEBUG & DEVELOPER TOOLS

### Debug Overlay (Press **~** tilde key)
- [ ] Debug overlay toggles on/off
- [ ] **Game State tab** shows:
  - [ ] Turn number and phase
  - [ ] All resources (Money, Compute, Research, Papers, Reputation)
  - [ ] Doom system status (Doom value, velocity, momentum)
  - [ ] Staff counts (Safety, Capability, Compute Eng, Managers)
  - [ ] Individual researcher details (name, specialization, skill, burnout)
  - [ ] Queued actions list
  - [ ] Pending events
  - [ ] Rival labs info
- [ ] **Errors tab** shows error log (if any)
- [ ] **Performance tab** shows:
  - [ ] FPS counter
  - [ ] Frame time
  - [ ] Memory usage
  - [ ] Object/node counts
  - [ ] Draw calls

### Debug Controls Tab
- [ ] "Add $50k Money" button works
- [ ] "Add 5 Action Points" button works
- [ ] "Trigger Random Event" opens event selection popup
- [ ] Event selection popup shows all 30+ events
- [ ] Selecting an event adds it to pending events
- [ ] "Reset Game" restarts the game
- [ ] Refresh rate slider adjusts update frequency

---

## ACCESSIBILITY FEATURES

### Colorblind Mode (Settings > Accessibility)
- [ ] Colorblind mode toggle exists
- [ ] Protanopia mode applies correctly
- [ ] Deuteranopia mode applies correctly
- [ ] Tritanopia mode applies correctly
- [ ] High contrast mode works

### Keyboard Navigation
- [ ] All buttons keyboard-focusable
- [ ] Focus indicators visible
- [ ] Action shortcuts displayed on buttons/tooltips

---

## MESSAGE LOG & HISTORY

- [ ] Action messages appear in log
- [ ] Messages color-coded by type (success=green, warning=yellow, error=red)
- [ ] Message prefixes display (checkmark, warning, etc.)
- [ ] Auto-scroll keeps newest messages visible
- [ ] **Persistent History**: Close and reopen game, last 20 messages restored

---

## EVENTS SYSTEM

### Event Triggering
- [ ] Random events occur during gameplay
- [ ] Event popup displays with title and description
- [ ] Event choices presented clearly
- [ ] Choosing an option applies effects
- [ ] Event resolution logged in message log

### Debug Event Testing (via Debug Overlay)
- [ ] Can trigger specific events manually
- [ ] Media coverage events work
- [ ] Funding events work
- [ ] Research breakthrough events work
- [ ] Crisis/disaster events work

---

## MUSIC & AUDIO

- [ ] Background music plays
- [ ] Music volume adjustable in settings
- [ ] Music context changes based on game state
- [ ] Crossfade between tracks works smoothly
- [ ] Mute option works

---

## DOOM SYSTEM

- [ ] Doom increases based on unsafe actions
- [ ] Doom decreases with safety research
- [ ] Doom velocity shown in debug overlay
- [ ] Doom momentum affects rate of change
- [ ] Doom status text accurate (Stable, Rising, etc.)
- [ ] Game over triggers at Doom 100

---

## VICTORY CONDITIONS

- [ ] Victory condition tracking visible
- [ ] Progress toward aligned AGI shown
- [ ] Victory screen displays on win

---

## BUG REPORTING

- [ ] Bug Reporter opens (**\\** backslash key)
- [ ] Can enter bug description
- [ ] Screenshot capture works
- [ ] Bug report includes game state

---

## SCREENSHOTS

- [ ] Screenshot key (**[** left bracket) captures screen
- [ ] Screenshot saved to user directory
- [ ] Screenshot notification appears

---

## SAVE/LOAD (If Implemented)

- [ ] Save game works
- [ ] Load game restores full state
- [ ] Autosave triggers at appropriate times

---

## PERFORMANCE NOTES

| Metric | Value | Notes |
|--------|-------|-------|
| Avg FPS | _____ | Target: 60+ |
| Memory Usage | _____ MB | |
| Load Time | _____ sec | |

---

## ISSUES FOUND

| # | Severity | Description | Steps to Reproduce |
|---|----------|-------------|-------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

**Severity Levels:** Critical / Major / Minor / Cosmetic

---

## NEW PLAYER FEEDBACK

### First Impressions
_____________________________________________________________
_____________________________________________________________

### Confusing Elements
_____________________________________________________________
_____________________________________________________________

### What They Enjoyed
_____________________________________________________________
_____________________________________________________________

### Suggestions
_____________________________________________________________
_____________________________________________________________

---

## SESSION NOTES

_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

---

**Session Complete:** [ ] Yes  **Recording Saved:** [ ] Yes

**Overall Assessment:** [ ] Ready for Release  [ ] Needs Work  [ ] Critical Issues

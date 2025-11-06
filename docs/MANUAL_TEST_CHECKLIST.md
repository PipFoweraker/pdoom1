# Manual Testing Checklist

**Purpose:** Ensure critical user-facing functionality works correctly before release.

**When to Use:**
- Before merging to main (if UI/gameplay changes)
- Before creating a release
- After fixing critical bugs
- When automated tests can't cover (visual, audio, platform-specific)

---

## Test Environment

**Date:** _______________________
**Tester:** _______________________
**Version:** _______________________
**Platform:** [ ] Windows  [ ] Linux  [ ] macOS  [ ] Web
**Build Type:** [ ] Development  [ ] Release

---

## 1. Game Launch & Welcome Screen

**Objective:** Verify game starts and welcome screen loads correctly

- [ ] Game launches without crashes
- [ ] Window size and resolution correct (1920x1080 default)
- [ ] Welcome screen displays properly
- [ ] Title "P(Doom)" visible
- [ ] All menu buttons visible and aligned
- [ ] Version number displayed in bottom-right
- [ ] Keyboard navigation works (↑/↓ or W/S)
- [ ] Mouse clicks work on all buttons
- [ ] No visual artifacts or rendering issues

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 2. Configuration Flow - Default Pathway

**Objective:** Verify default "Launch Lab" pathway with weekly seed

### A. Launch Lab Button
- [ ] Clicking "Launch Lab" goes to configuration confirmation screen
- [ ] Configuration confirmation screen displays correctly

### B. Configuration Confirmation Screen
- [ ] Title: "LABORATORY CONFIGURATION" displayed
- [ ] Player name shown (default: "Researcher" if empty)
- [ ] Lab name shown (default: "AI Safety Lab" if empty)
- [ ] Seed shown as "weekly-YYYY-wNN (Weekly Challenge)" with greyed text
- [ ] Difficulty shown as "Standard (Regulatory)" with greyed text
- [ ] Funding shown as "$245,000" with greyed text
- [ ] Info text explains greyed options are locked
- [ ] "Initialize Lab" button functional
- [ ] "Customize" button goes to pregame setup
- [ ] "Back" button returns to welcome screen
- [ ] ESC key returns to welcome screen
- [ ] ENTER key launches game

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 3. Configuration Flow - Custom Pathway

**Objective:** Verify custom seed pathway allows configuration

### A. Pregame Setup Screen
- [ ] Clicking "Launch with Custom Seed" goes to pregame setup
- [ ] Player name field works (can type, edit)
- [ ] Lab name field works (can type, edit)
- [ ] Random lab name button (🎲) generates names
- [ ] Seed field works (optional)
- [ ] Weekly seed button clears seed field
- [ ] Difficulty dropdown has 3 options (Easy, Standard, Hard)
- [ ] "Initialize Lab" disabled if name fields empty
- [ ] "Cancel" returns to welcome screen

### B. Configuration Confirmation (Custom Mode)
- [ ] After clicking "Initialize Lab", goes to confirmation screen
- [ ] All entered values displayed correctly
- [ ] Seed text is NOT greyed out (custom mode)
- [ ] Difficulty text is NOT greyed out (custom mode)
- [ ] Funding still greyed out ($245,000)
- [ ] Can click "Customize" to go back to pregame setup
- [ ] Values preserved when returning from customize
- [ ] "Initialize Lab" launches game with custom settings

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 4. Main Game Interface

**Objective:** Verify main game UI loads and displays correctly

### A. Initial Load
- [ ] Main game screen loads after confirmation
- [ ] All UI panels visible (resources, actions, queue, turn info)
- [ ] Starting resources correct:
  - Money: $245,000
  - Compute: 100
  - Research: 0
  - Papers: 0
  - Reputation: 50
  - Doom: 50
  - AP: 3
- [ ] Action list populated with available actions
- [ ] Action categories color-coded correctly
- [ ] No console errors or warnings

### B. UI Layout
- [ ] Top bar: resources displayed
- [ ] Left side: action list with categories
- [ ] Middle: action queue area
- [ ] Right side: upgrades panel
- [ ] Bottom: control buttons (End Turn, Clear Queue)
- [ ] All text readable and not overlapping
- [ ] Tooltips appear on hover (if implemented)

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 5. Action Queue System

**Objective:** Verify action queueing and execution

### A. Queue Actions
- [ ] Can click action to queue it
- [ ] Action appears in queue panel
- [ ] AP decreases when action queued
- [ ] Actions with insufficient AP disabled
- [ ] Can queue multiple actions
- [ ] Queue displays in order
- [ ] Visual feedback when action queued (highlight, animation)

### B. Clear Queue Button
- [ ] "Clear Queue (C)" button visible
- [ ] Button disabled when queue empty
- [ ] Button enabled when queue has actions
- [ ] Clicking button clears all queued actions
- [ ] AP refunded correctly when cleared
- [ ] **C key** clears queue (KeybindManager)
- [ ] Can rebind Clear Queue key in settings
- [ ] Visual confirmation when queue cleared

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 6. Turn Execution

**Objective:** Verify turn processing works correctly

### A. End Turn
- [ ] "End Turn (Space)" button visible
- [ ] Clicking button processes turn
- [ ] SPACE key ends turn
- [ ] Queued actions execute in order
- [ ] Action results displayed
- [ ] Resources update correctly
- [ ] Turn number increments
- [ ] AP resets to 3 (or appropriate value)
- [ ] Events trigger if applicable
- [ ] No crashes or freezes during processing

### B. Turn Results
- [ ] Results panel shows what happened
- [ ] Money changes displayed
- [ ] Reputation changes displayed
- [ ] Doom changes displayed
- [ ] Research generated shown
- [ ] Staff changes shown (if hired/fired)
- [ ] Results are accurate and match expectations

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 7. Keybinding System

**Objective:** Verify KeybindManager works correctly

### A. Default Keybinds
- [ ] SPACE: End Turn
- [ ] C: Clear Queue
- [ ] ESC: Cancel/Back
- [ ] TAB: Next Tab (if tabs implemented)
- [ ] ~: Toggle Debug Overlay
- [ ] [: Screenshot
- [ ] \: Export Log
- [ ] ]: Admin Mode

### B. Keybind Configuration
- [ ] Can access keybind settings from main menu
- [ ] All keybinds listed with current assignments
- [ ] Can click keybind to rebind
- [ ] New key assignment works
- [ ] Changes saved and persist after restart
- [ ] Can reset to defaults
- [ ] No conflicts between keybinds

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 8. Game State Persistence

**Objective:** Verify save/load functionality (if implemented)

- [ ] Can save game mid-session
- [ ] Save file created in correct location
- [ ] Can load saved game
- [ ] All resources restored correctly
- [ ] Queued actions restored
- [ ] Turn number correct after load
- [ ] Game settings preserved
- [ ] No corruption or data loss

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 9. Edge Cases & Error Handling

**Objective:** Verify game handles errors gracefully

### A. Resource Limits
- [ ] Negative resources handled correctly
- [ ] Very large numbers display properly (commas for thousands)
- [ ] Money displays with $ prefix
- [ ] Doom at 100 triggers game over
- [ ] Reputation at 0 triggers game over
- [ ] Win condition works (Doom at 0)

### B. Input Validation
- [ ] Empty player name prevents game start
- [ ] Empty lab name prevents game start
- [ ] Invalid seed handled gracefully
- [ ] Rapid clicking doesn't break UI
- [ ] Keyboard shortcuts don't conflict

### C. Error Messages
- [ ] Errors displayed to user (not just console)
- [ ] Error messages are clear and actionable
- [ ] Game doesn't crash on error
- [ ] Can recover from errors without restart

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 10. Visual & Audio

**Objective:** Verify visual and audio quality

### A. Visual
- [ ] No graphical glitches
- [ ] Colors consistent with theme
- [ ] Text readable on all backgrounds
- [ ] Buttons have hover effects
- [ ] Animations smooth (if any)
- [ ] No flickering
- [ ] Fullscreen mode works
- [ ] Window resizing works

### B. Audio (if implemented)
- [ ] Background music plays
- [ ] Sound effects work
- [ ] Volume controls work
- [ ] Audio doesn't crackle or distort
- [ ] Can mute audio

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 11. Performance

**Objective:** Verify acceptable performance

- [ ] Game loads in <10 seconds
- [ ] UI responsive (<100ms click-to-action)
- [ ] Turn processing completes in <5 seconds
- [ ] No lag or stuttering during gameplay
- [ ] Memory usage stable (no leaks)
- [ ] CPU usage reasonable (<50% on modern hardware)
- [ ] Frame rate stable (if monitoring available)

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 12. Platform-Specific (If Applicable)

### Windows
- [ ] .exe launches without admin rights
- [ ] No antivirus false positives
- [ ] Works on Windows 10
- [ ] Works on Windows 11

### Linux
- [ ] Binary has execute permissions
- [ ] Dependencies satisfied
- [ ] Works on Ubuntu/Debian
- [ ] Works on other distros (if tested)

### macOS
- [ ] .app bundle works
- [ ] No Gatekeeper issues
- [ ] Works on Intel Macs
- [ ] Works on Apple Silicon

### Web
- [ ] Loads in Chrome
- [ ] Loads in Firefox
- [ ] Loads in Safari (if applicable)
- [ ] No CORS errors
- [ ] Performance acceptable
- [ ] Controls work with keyboard/mouse

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## 13. Regression Testing

**Objective:** Verify previous bugs haven't returned

### Known Fixed Issues
- [ ] Issue #436: Configuration confirmation screen working
- [ ] Issue #436: Clear Queue button functional
- [ ] Issue #436: Default funding $245,000
- [ ] Issue #436: Money displays with commas
- [ ] Issue #436: Action categories color-coded
- [ ] (Add other fixed issues as needed)

**Notes:**
```
_______________________________________________
_______________________________________________
```

---

## Overall Assessment

### Critical Issues Found
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

### Non-Critical Issues
```
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________
```

### Recommendations
- [ ] **PASS** - Ready for release
- [ ] **PASS WITH MINOR ISSUES** - Can release with known issues documented
- [ ] **FAIL** - Must fix critical issues before release

**Tester Signature:** _______________________
**Date:** _______________________

---

## Appendix: Quick Smoke Test

**Use this for rapid validation (5 minutes):**

1. [ ] Game launches
2. [ ] Click "Launch Lab"
3. [ ] Configuration screen appears
4. [ ] Click "Initialize Lab"
5. [ ] Main game loads with correct starting resources
6. [ ] Queue an action
7. [ ] Press C to clear queue (AP refunded)
8. [ ] Queue action again
9. [ ] Press SPACE to end turn
10. [ ] Turn processes successfully

**Result:** [ ] PASS  [ ] FAIL

---

**Checklist Version:** 1.0
**Last Updated:** 2025-01-07
**Maintained By:** Project Team

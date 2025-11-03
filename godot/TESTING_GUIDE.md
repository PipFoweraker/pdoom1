# Godot UI Testing Guide
**Complete Manual Testing Procedures**

---

## 🚀 Quick Start

1. **Open Project:**
   ```bash
   godot godot/project.godot
   ```

2. **Run Game (F5)**
   - Should open to welcome.tscn
   - Should see "P(Doom)" title
   - Should see 5 buttons

3. **Check Console Output:**
   ```
   [GameConfig] Initializing global configuration...
   [GameConfig] No existing config found, using defaults  (first time)
   OR
   [GameConfig] Configuration loaded successfully  (subsequent runs)
   [GameConfig] Audio settings applied...
   [GameConfig] Graphics settings applied...
   [GameConfig] Configuration loaded and applied
   [WelcomeScreen] Ready
   ```

---

## 📋 Test Suite

### Test 1: Welcome Screen Navigation
**Purpose:** Verify all buttons work

| Action | Expected Result |
|--------|----------------|
| Click "Launch Lab" | → Transitions to main.tscn |
| Click "Launch with Custom Seed" | → Transitions to pregame_setup.tscn |
| Click "Settings" | → Transitions to settings_menu.tscn |
| Click "Player Guide" | → Transitions to player_guide.tscn |
| Click "Exit" | → Game closes |
| Press ↑/↓ keys | Button focus moves |
| Press Enter | Selected button activates |
| Press 1-5 | Corresponding button activates |
| Press Escape | Game closes |

**Console Output to Verify:**
```
[WelcomeScreen] Opening settings menu...
[SettingsMenu] Initializing...
```

---

### Test 2: Settings Menu - Audio
**Purpose:** Verify audio controls work and persist

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Go to Settings | Volume sliders show current values |
| 2 | Move Master Volume to 50% | Label updates to "50%" |
| 3 | Move SFX Volume to 60% | Label updates to "60%" |
| 4 | Click Apply | "Settings Saved" dialog appears for 2 seconds |
| 5 | Click Back | Return to welcome screen |
| 6 | Go to Settings again | Volume still 50% and 60% |
| 7 | Close game completely | |
| 8 | Relaunch game | |
| 9 | Go to Settings | **Volume persists!** Still 50% and 60% |

**Console Output:**
```
[SettingsMenu] Initializing...
[GameConfig] Audio settings applied - Master: 50% (-6.0 dB), SFX: 60% (-4.4 dB)
[SettingsMenu] Saving settings to disk...
[GameConfig] Saving configuration...
[GameConfig] Configuration saved successfully
```

**Config File Check:**
```bash
# Windows
cat "%APPDATA%\Godot\app_userdata\P(Doom)\config.cfg"

# Should contain:
[audio]
master_volume=50
sfx_volume=60
```

---

### Test 3: Settings Menu - Graphics
**Purpose:** Verify graphics controls work

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Change Graphics Quality to "Low" | Dropdown shows "Low" |
| 2 | Toggle Fullscreen ON | Checkbox checked |
| 3 | Click Apply | Dialog appears |
| 4 | Window becomes fullscreen | **Window enters fullscreen mode** |
| 5 | Toggle Fullscreen OFF | Checkbox unchecked |
| 6 | Click Apply | Window returns to windowed mode |

**Console Output:**
```
[SettingsMenu] Graphics quality changed to: Low
[SettingsMenu] Fullscreen: true
[GameConfig] Graphics settings applied - Fullscreen: true, Quality: 0
```

---

### Test 4: Settings Menu - Gameplay
**Purpose:** Verify difficulty setting

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Change difficulty to "Hard" | Dropdown shows "Hard" |
| 2 | Click Apply | Settings saved |
| 3 | Start a new game | Game uses Hard difficulty |

**Console Output:**
```
[SettingsMenu] Difficulty changed to: Hard
[GameManager] Applying HARD difficulty modifiers
```

---

### Test 5: Pre-Game Setup - Name Entry
**Purpose:** Verify text input and validation

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open Pre-Game Setup | Player name input has focus |
| 2 | Type "TestPlayer" | Text appears in field |
| 3 | Click lab name input | Focus moves |
| 4 | Type "Test Lab" | Text appears |
| 5 | Clear player name | Launch button becomes disabled |
| 6 | Type "Player" again | Launch button becomes enabled |

**Validation Rules:**
- Launch button disabled if player name empty
- Launch button disabled if lab name empty
- Launch button enabled when both filled

---

### Test 6: Pre-Game Setup - Random Lab Name
**Purpose:** Verify random name generator

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Click 🎲 button | Random name appears (e.g., "Advanced AI Safety Research") |
| 2 | Click 🎲 again | Different random name |
| 3 | Click 🎲 again | Different random name |

**Expected Name Patterns:**
- "Advanced AI Safety Research"
- "Machine Learning Studies"
- "Center for Beneficial AI"
- "Institute for Neural Networks Development"
- etc.

**Console Output:**
```
[PreGameSetup] Generated random lab name: Advanced AI Safety Research
```

---

### Test 7: Pre-Game Setup - Seed Management
**Purpose:** Verify seed input and weekly seed

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter custom seed: "test123" | Seed field shows "test123" |
| 2 | Click "Weekly" button | Seed field clears |
| 3 | Click "INITIALIZE LAB" | Game uses weekly seed |

**Console Output:**
```
[PreGameSetup] Using weekly challenge seed: weekly-2025-w44
[GameManager] Starting new game
  Seed: weekly-2025-w44
```

---

### Test 8: Pre-Game Setup - Game Launch
**Purpose:** Verify full launch sequence

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Enter player name: "Alice" | Text appears |
| 2 | Enter lab name: "Safety First Lab" | Text appears |
| 3 | Enter seed: "demo" | Text appears |
| 4 | Select difficulty: Easy | Dropdown shows "Easy" |
| 5 | Click "INITIALIZE LAB" | Game starts with config |

**Console Output (Complete Sequence):**
```
[PreGameSetup] Launching game...
[GameConfig] Saving configuration...
[GameConfig] Configuration saved successfully
[GameConfig] === Current Configuration ===
  Player: Alice
  Lab: Safety First Lab
  Seed: demo
  Difficulty: Easy
  Master Volume: 80%
  SFX Volume: 80%
  Graphics: Medium
  Fullscreen: false
  Games Played: 1
========================================
[GameConfig] Games played: 1
[GameManager] Starting new game
  Player: Alice
  Lab: Safety First Lab
  Seed: demo
  Difficulty: Easy
[GameManager] Applying EASY difficulty modifiers
```

---

### Test 9: Pre-Game Setup - Keyboard Shortcuts
**Purpose:** Verify keyboard navigation

| Action | Expected Result |
|--------|----------------|
| Press Tab | Focus moves through fields |
| Press Enter (when valid) | Launches game |
| Press Escape | Returns to welcome screen |

---

### Test 10: Player Guide - Display
**Purpose:** Verify guide displays correctly

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open Player Guide | Guide displays with all sections |
| 2 | Scroll down | All content visible |
| 3 | Read sections | Text formatted with colors/bold |
| 4 | Press Escape | Returns to welcome |
| 5 | Click Back button | Returns to welcome |

**Sections to Verify:**
- ✅ Game Objective (with color highlights)
- ✅ Controls (with keyboard shortcuts)
- ✅ Key Resources (with color-coded explanations)
- ✅ Strategy Tips (7 tips)

---

### Test 11: Difficulty System Integration
**Purpose:** Verify difficulty affects gameplay

| Difficulty | Expected Modifiers |
|------------|-------------------|
| Easy | Money × 1.5, Max AP: 4 |
| Standard | No changes (default) |
| Hard | Money × 0.75, Max AP: 2 |

**Test Procedure:**
1. Start game with Easy
2. Check starting money in game (should be 1.5x normal)
3. Check max AP (should be 4)
4. Restart with Hard
5. Check starting money (should be 0.75x normal)
6. Check max AP (should be 2)

---

### Test 12: Config Persistence
**Purpose:** Verify all settings persist across sessions

| Setting | Test |
|---------|------|
| Player name | Change → Restart → Still changed |
| Lab name | Change → Restart → Still changed |
| Difficulty | Change → Restart → Still changed |
| Master volume | Change → Restart → Still changed |
| SFX volume | Change → Restart → Still changed |
| Graphics quality | Change → Restart → Still changed |
| Fullscreen | Change → Restart → Still changed |
| Games played | Play game → Restart → Counter incremented |

**How to Test:**
1. Change all settings
2. Click Apply in settings menu
3. Launch a game from pre-game setup
4. Close game completely (Alt+F4 or close window)
5. Relaunch game
6. Check all settings → Should match what you set!

---

## 🐛 Bug Reporting Template

If you find a bug, report it with this format:

```markdown
### Bug: [Brief Description]

**Steps to Reproduce:**
1.
2.
3.

**Expected Behavior:**


**Actual Behavior:**


**Console Output:**
```
[paste console output here]
```

**System Info:**
- OS: Windows/Linux/Mac
- Godot Version: 4.x
- Session Date: 2025-10-31
```

---

## ✅ Sign-Off Checklist

After completing all tests, verify:

### Welcome Screen
- [ ] All 5 buttons navigate correctly
- [ ] Keyboard navigation works (arrows, enter, 1-5)
- [ ] Escape quits the game

### Settings Menu
- [ ] Master volume slider works + persists
- [ ] SFX volume slider works + persists
- [ ] Graphics quality dropdown works + persists
- [ ] Fullscreen toggle works + persists
- [ ] Difficulty dropdown works + persists
- [ ] Apply button shows confirmation
- [ ] Back button returns to welcome
- [ ] Escape returns to welcome

### Pre-Game Setup
- [ ] Player name input works
- [ ] Lab name input works
- [ ] Random lab name button generates names
- [ ] Seed input works
- [ ] Weekly seed button clears seed
- [ ] Difficulty dropdown works
- [ ] Launch button validation (disabled when empty)
- [ ] Launch starts game with correct config
- [ ] Enter launches (when valid)
- [ ] Escape cancels

### Player Guide
- [ ] All sections display correctly
- [ ] Scrolling works
- [ ] Colors/formatting display
- [ ] Back button works
- [ ] Escape works

### Integration
- [ ] Config file created at `user://config.cfg`
- [ ] Settings persist across sessions
- [ ] Difficulty modifiers apply correctly
- [ ] Games played counter increments
- [ ] Weekly seed generates correctly
- [ ] Console output is clean (no errors)

---

## 📊 Performance Checks

Monitor console for:
- ❌ **Error messages** (should be zero)
- ❌ **Warning messages** (should be minimal)
- ✅ **Clean output** (just info logs)

Expected FPS:
- Welcome screen: 60 FPS
- Settings menu: 60 FPS
- Pre-game setup: 60 FPS
- Player guide: 60 FPS (even while scrolling)

---

## 🔍 Advanced Testing

### Config File Corruption
1. Manually edit `config.cfg` with invalid data
2. Launch game
3. **Expected:** Game uses defaults, no crash

### Empty Config File
1. Delete `config.cfg`
2. Launch game
3. **Expected:** Creates new config with defaults

### Invalid Seed
1. Enter seed with special characters: `!@#$%^&*()`
2. Launch game
3. **Expected:** Game accepts it (seeds can be any string)

### Long Names
1. Enter 30-character player name (max length)
2. **Expected:** Accepts it
3. Try 31 characters
4. **Expected:** Truncates at 30

---

## 💡 Tips for Testing

1. **Keep Console Visible**
   - Watch for errors in real-time
   - Console output shows exactly what's happening

2. **Test Incrementally**
   - Don't change everything at once
   - Test one feature, verify it works, move to next

3. **Use Config File**
   - Check `user://config.cfg` to verify saves
   - Can manually edit for edge case testing

4. **Document Issues**
   - Note exact steps to reproduce
   - Include console output
   - Screenshot if visual bug

---

## 🎯 Success Criteria

All tests pass = **Option B Complete!** ✅

Ready to move to Option E (Python ↔ Godot Bridge) or Option D (Leaderboard).

---

*Testing is the foundation of quality. Take your time!* 🧪

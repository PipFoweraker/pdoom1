# Pre-Push Checklist

_Always run these checks before pushing to main to catch errors early_

---

## 🚦 Quick Checklist

- [ ] **1. Run automated tests** (`run_tests.bat`)
- [ ] **2. Launch game and verify no console errors**
- [ ] **3. Quick smoke test** (init game, take 1-2 turns)
- [ ] **4. Check git status** (no unintended files)
- [ ] **5. Push!**

---

## MEMO Detailed Steps

### 1. Run Automated Tests (GUT)

**Option A: Command Line** (fastest)
```bash
cd godot
run_tests.bat
```

**Option B: Godot Editor** (more detailed output)
1. Open Godot Editor
2. Go to **Project  ->  Tools  ->  Run GUT**
3. Or use the **GUT** tab in bottom panel
4. Click **Run All Tests**

**What to look for:**
- SUCCESS All tests pass (green)
- ERROR Any test failures (red) - **MUST FIX BEFORE PUSHING**

**Test coverage:**
- `tests/unit/test_actions.gd` - Action system validation
- `tests/unit/test_events.gd` - Event system validation
- `tests/unit/test_game_state.gd` - State management
- `tests/unit/test_game_manager.gd` - Game manager logic
- `tests/unit/test_turn_manager.gd` - Turn flow
- `tests/test_doom_momentum.gd` - Doom mechanics
- `tests/test_researcher_system.gd` - Employee system

---

### 2. Launch Game - Console Check

**Steps:**
1. Press **F5** (or click Play button)
2. Watch **Output** panel at bottom
3. Look for errors (red text)

**Common errors to catch:**
- `Cannot find member "X" in base "Y"` - typo or wrong constant
- `Invalid get index` - accessing wrong dictionary key
- `Null instance` - missing node reference

**Expected clean output:**
```
[GameConfig] Initializing global configuration...
[WelcomeScreen] Ready
[ThemeManager] Theme system initialized...
```

**If errors appear:**
- ERROR Read error message carefully
- ERROR Fix the error
- ERROR Restart from Step 1 (run tests again)

---

### 3. Quick Smoke Test (2 minutes)

**Minimal playthrough to catch runtime errors:**

1. **Launch Lab** from welcome screen
2. Click **Init Game**
3. Click a few action buttons (hire staff, run compute)
4. Click **End Turn**
5. Let turn process
6. Take 1-2 more turns
7. Check for:
   - ERROR Any red error messages in console
   - ERROR UI freezing or hanging
   - ERROR Buttons not responding

**Quick test checklist:**
- [ ] Game initializes without errors
- [ ] Action buttons work
- [ ] Turn processing completes
- [ ] No red console errors
- [ ] UI responsive

---

### 4. Git Status Check

**Before committing:**
```bash
git status
```

**Look for:**
- ERROR `.import/` files (should be in .gitignore)
- ERROR `*.tmp` files
- ERROR Personal config files
- ERROR Debug logs
- SUCCESS Only intended .gd, .tscn, .md files

**Clean up unwanted files:**
```bash
# If you see unwanted files:
git restore --staged <filename>
# or add to .gitignore
```

---

### 5. Commit and Push

**Good commit message format:**
```bash
git add .
git commit -m "feat: Brief description of feature

Detailed explanation:
- What changed
- Why it changed
- Any breaking changes

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

---

## 🐛 Common Pre-Push Catches

### Issue 1: Wrong Godot 4.x Constants
**Error:** `Cannot find member "AUTOWRAP_WORD_BOUND" in base "TextServer"`
**Fix:** Use `TextServer.AUTOWRAP_WORD` instead

### Issue 2: Missing @onready References
**Error:** `Null instance` when accessing UI elements
**Fix:** Add `@onready var my_node = $Path/To/Node` at top of script

### Issue 3: Dictionary Key Typos
**Error:** `Invalid get index 'actoin_points'` (typo in 'action')
**Fix:** Use correct key name `action_points`

### Issue 4: Scene Path Typos
**Error:** `Failed to load resource: res://scenes/ui/doom_meterr.tscn`
**Fix:** Correct the scene path (extra 'r' in 'meterr')

### Issue 5: Hot Reload vs Full Reload
**Error:** Changes not appearing in game
**Fix:** Close and reopen game (F5) for major changes, not just hot reload

---

## SEARCH When to Run Full Test Suite

**Quick tests (run_tests.bat):** Before every push

**Full manual testing:** When you've changed:
- Core game mechanics (actions, events, doom)
- UI layout or navigation
- State management or serialization
- Turn flow or phase management

---

## ⚡ Pro Tips

1. **Run tests in background:** Start tests while you're committing messages
2. **F5 > F6:** Use F5 (run) not F6 (run current scene) to test full flow
3. **Watch console:** Keep Output panel visible while testing
4. **Test save/load:** If you changed GameState, test save/load cycles
5. **Test game over:** If you changed end conditions, trigger victory/defeat

---

## TARGET Test Pyramid

```
           E2E Tests (Manual)
         /                   \
    Integration Tests (GUT)
   /                           \
Unit Tests (GUT - fast!)
```

- **Unit tests** (automated) - Run every time (2 seconds)
- **Integration tests** (automated) - Run every time (10 seconds)
- **E2E tests** (manual) - Run before major pushes (2 minutes)

---

## METRICS Test Coverage Goals

Current coverage:
- SUCCESS Core systems (90%+)
- SUCCESS Game mechanics (85%+)
- WARNING UI interactions (manual only)
- WARNING Edge cases (improving)

---

## 🚨 Hard Rules

**NEVER push if:**
1. ERROR Any GUT test fails
2. ERROR Game won't launch (red errors on F5)
3. ERROR Console shows errors during smoke test
4. ERROR You haven't tested your changes at all

**ALWAYS push if:**
1. SUCCESS All tests pass
2. SUCCESS Game launches clean
3. SUCCESS Smoke test succeeds
4. SUCCESS You've tested the specific feature you changed

---

## 📞 When Tests Fail

1. **Read the error message** - It tells you exactly what's wrong
2. **Check the file and line number** - Jump directly to problem
3. **Fix the issue** - Don't push broken code
4. **Re-run tests** - Verify fix works
5. **Commit the fix** - Include test fixes in commit

---

## 🎓 Learning From Failures

Keep a log of caught errors:
```
Date: 2025-10-31
Error: AUTOWRAP_WORD_BOUND not found
Lesson: Always check Godot 4.x constant names
Prevention: Run tests before pushing
```

This helps avoid repeating mistakes!

---

_Remember: Tests are faster than debugging in production. Take 30 seconds to run them!_ LAUNCH

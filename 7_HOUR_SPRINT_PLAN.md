# 7-Hour Sprint Plan - High-Confidence Fixes for v0.10.1

**Time Budget:** 7 hours (6.5h execution + 0.5h buffer)
**Reserved:** 30min UI polish + 1h website update
**Total Session:** 8.5 hours remaining

---

## Selection Criteria
✅ High confidence (can complete without unknowns)
✅ High impact (players will notice immediately)
✅ Low risk (won't break existing functionality)
✅ Godot-compatible (works in current engine)
❌ Skip: Major architecture changes, Python-only fixes, long-tail features

---

## TIER 1: Critical Fixes (2.5 hours) - MUST DO

### 1. #435 - Clean Up GDScript Warnings (45 min) ⭐
**Why:** Code quality, machine-readable, catches real bugs
**Effort:** Low - mostly renaming and prefixing
**Impact:** Professional code, easier debugging
**Files:**
- `godot/scripts/game_manager.gd` - unused `err` variables
- `godot/scripts/core/game_state.gd` - `seed` → `game_seed`
- `godot/autoload/*.gd` - `notification` shadowing

**Tasks:**
- [ ] Prefix unused vars with `_` (15min)
- [ ] Rename shadowing variables (15min)
- [ ] Test game still runs (10min)
- [ ] Document changes in commit (5min)

**Deliverable:** Zero GDScript warnings in Godot editor

---

### 2. #389 - Action Points System Validation (1 hour) ⭐⭐
**Why:** CRITICAL - Game balance, prevents exploits
**Effort:** Medium - need to audit all actions
**Impact:** Game fairness, proper validation
**Current Bug:** Some actions have 0 AP cost, validation broken

**Tasks:**
- [ ] Read all action definitions in actions.json (15min)
- [ ] Identify legitimate 0-AP actions vs bugs (15min)
- [ ] Fix action costs or update validation logic (20min)
- [ ] Run test_action_points.py tests (10min)

**Deliverable:** All actions have valid AP costs, tests pass

---

### 3. Finish Current UX Fixes (45 min) ⭐⭐⭐
**Why:** Already started, high player impact
**What's Left:**
- [ ] Re-export Godot build with C key fix (10min)
- [ ] Test with `test_ux_fixes.md` checklist (15min)
- [ ] Commit UX improvements (run script) (5min)
- [ ] Quick smoke test (15min)

**Deliverable:** Clean build with all UX fixes working

---

## TIER 2: Quick Wins (2 hours) - HIGH VALUE

### 4. #431 - Refine Game Description (15 min) ⭐
**Why:** Marketing, professionalism, first impressions
**Effort:** Trivial - text changes only
**Impact:** Better understanding of game tone

**Tasks:**
- [ ] Update README.md description (5min)
- [ ] Update website copy (part of 1h website time)
- [ ] Update Godot project description (5min)
- [ ] Update itch.io/Steam descriptions (future)

**Files:**
- README.md
- godot/project.godot
- website content

---

### 5. Add Danger Zone Warnings (45 min) ⭐⭐
**Why:** You mentioned this! Players want advance warning
**Effort:** Medium - need to calculate future doom/reputation
**Impact:** Prevents ragequit, better UX

**Implementation:**
```gdscript
func _on_end_turn_button_pressed():
    # Calculate projected end-of-turn stats
    var projected_doom = calculate_projected_doom()
    var projected_rep = calculate_projected_reputation()

    # Warn if danger zones
    if projected_doom > 80:
        show_warning("HIGH DOOM RISK: Actions may push doom above 80%!")
    if projected_rep < 20:
        show_warning("LOW REPUTATION: May lose funding!")

    # Require confirmation if critical
    if projected_doom > 95 or projected_rep < 10:
        show_confirmation_dialog("CRITICAL: Continue anyway?")
```

**Tasks:**
- [ ] Add projection calculations to TurnManager (20min)
- [ ] Add warning dialog system (15min)
- [ ] Test with deliberate bad actions (10min)

---

### 6. Visual Queue Item Buttons (1 hour) ⭐⭐
**Why:** You wanted X/spanner icons on queue items
**Effort:** Medium - UI work
**Impact:** Much better queue management UX

**Implementation:**
- Add small X button to each queue item (remove individual)
- Maybe add reorder buttons (future: drag-drop is v0.10.2)
- Visual feedback when hovering

**Tasks:**
- [ ] Update `update_queued_actions_display()` (30min)
- [ ] Add remove button to each item (20min)
- [ ] Test removing mid-queue items (10min)

---

## TIER 3: Polish (1.5 hours) - NICE TO HAVE

### 7. Better Phase Indicators (30 min)
**Why:** Turn progression visibility (you mentioned this)
**Current:** Basic phase label exists
**Enhance:** Make it MUCH more obvious

**Ideas:**
- Animated turn clock/spinner during processing
- Progress bar for turn phases
- Sound effects for phase transitions
- Flash/pulse effects

---

### 8. Improved Error Messages (30 min)
**Why:** Player confusion reduction
**Examples:**
- "Not enough AP" → "Not enough AP: need 2, have 1 (queue 3 to clear)"
- "Action failed" → "Cannot hire: Not enough money ($50k needed, $40k available)"

---

### 9. Quick Accessibility Pass (30 min)
**Partial #423:** Not full keyboard nav, just improvements
- Add more keyboard shortcuts for common actions
- Visual focus indicators
- Better shortcut hints

---

## TIER 4: Skip for v0.10.1

❌ #423 - Full Universal Keyboard Nav (too big - 4+ hours)
❌ #434 - UI Layout Redesign (major work - 6+ hours)
❌ #430 - Employee Management Screen (new feature - 3+ hours)
❌ #424 - Refactor Employee Productivity (risky - unknown time)
❌ #433/#432 - Data repository work (separate project)

---

## RECOMMENDED 7-HOUR EXECUTION ORDER

**Hour 1-2.5: CRITICAL TIER 1** (Must complete)
1. ✅ UX Fixes finish (45min) - Already started
2. ✅ GDScript warnings cleanup (45min) - Quick win
3. ✅ AP validation fix (1h) - Critical gameplay

**Hour 2.5-4.5: HIGH VALUE TIER 2**
4. ✅ Game description refinement (15min) - Trivial
5. ✅ Danger zone warnings (45min) - You wanted this
6. ✅ Visual queue buttons (1h) - UI improvement

**Hour 4.5-6: POLISH TIER 3** (If time permits)
7. ⏸️ Phase indicators (30min)
8. ⏸️ Error messages (30min)
9. ⏸️ Accessibility (30min)

**Hour 6-7: BUFFER & TESTING**
- Comprehensive playthrough
- Fix any regressions
- Update CHANGELOG
- Prepare for export

**Hour 7-7.5: UI POLISH** (Reserved 30min)
- Your manual tweaks
- Visual adjustments
- Final touches

**Hour 7.5-8.5: WEBSITE** (Reserved 1h)
- Update pdoom1-website repo
- Match new README content
- Deploy

---

## SUCCESS METRICS

**Minimum Success (Tier 1):**
- ✅ Zero GDScript warnings
- ✅ All AP validation tests pass
- ✅ UX fixes working (C key, disabled buttons, AP colors)

**Good Success (Tier 1 + 2):**
- ✅ All above
- ✅ Danger warnings before critical commits
- ✅ Queue items have remove buttons
- ✅ Professional game description

**Excellent Success (All Tiers):**
- ✅ Everything above
- ✅ Better phase visualization
- ✅ Improved error messages
- ✅ Some accessibility improvements

---

## RISK ASSESSMENT

**Low Risk (Safe to do):**
- GDScript warnings cleanup
- Game description text changes
- UI text/button improvements
- Error message improvements

**Medium Risk (Test carefully):**
- AP validation changes (could break action system)
- Danger zone warnings (calculation errors possible)
- Queue button functionality (AP refund logic)

**High Risk (Skip for now):**
- Major refactors
- New gameplay systems
- Architecture changes
- Python-Godot bridge changes

---

## DECISION POINT

**Recommended Plan: Tier 1 + Tier 2 (4.5 hours)**

This gives us:
- 3 critical fixes
- 3 high-value improvements
- 1.5h buffer for testing/issues
- 0.5h UI polish
- 1h website

**Alternative Conservative Plan: Tier 1 Only (2.5 hours)**
- Just critical fixes
- 4.5h for extensive tier 2+3 work
- Lower risk, more polish time

**Alternative Aggressive Plan: All Tiers (6+ hours)**
- Everything we can fit
- Minimal buffer
- Higher risk of incomplete work

---

## NEXT STEP

**I recommend: Start with Tier 1**

We've already made progress on #3 (UX fixes). Let's:
1. Finish UX fixes (45min)
2. Clean GDScript warnings (45min)
3. Fix AP validation (1h)

Then reassess at 2.5h mark. If ahead of schedule → Tier 2. If behind → stop and polish.

**Ready to execute? Say "start tier 1" and I'll begin with finishing the UX fixes!**

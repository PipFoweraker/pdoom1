# UX Fixes Testing Checklist

## Changes Made:
1. ✅ Changed Clear Queue shortcut: X → C (avoids conflicts)
2. ✅ Commit Actions button now disabled when queue is empty
3. ✅ Better error message: "ERROR: No actions queued! Press C to clear queue or select actions."
4. ✅ Both Clear Queue (C) and Commit Actions disabled when nothing queued

## Test Steps:

### Test 1: C Key Works
1. Start game
2. Queue 1-2 actions (press 1, 7, etc.)
3. **Press C key**
4. ✅ Expected: Queue clears, AP refunded, message shows "Action queue cleared - AP refunded"

### Test 2: Can't Commit Empty Turn
1. Start game (or clear queue with C)
2. Try to click "Commit Actions" button
3. ✅ Expected: Button is DISABLED (greyed out), can't click it
4. Try pressing Space/Enter
5. ✅ Expected: Nothing happens OR error message

### Test 3: Button Enables After Queuing
1. Queue 1 action (press 1)
2. ✅ Expected: "Commit Actions" button becomes ENABLED (clickable)
3. ✅ Expected: "Clear Queue (C)" button becomes ENABLED

### Test 4: Overcommitment Still Blocked
1. Queue 3 actions (use up all 3 AP)
2. Try to queue a 4th action
3. ✅ Expected: Error message "Not enough AP: 1 needed, 0 remaining (of 3 total)"
4. ✅ Expected: AP counter shows red "AP: 3 (0 free, 3 queued)"

### Test 5: C Doesn't Conflict with Submenus
1. Click action "[1] Hire Staff" (opens submenu)
2. Submenu should show Q/W/E/R/A/S/D/F/Z shortcuts
3. **Press C in the submenu**
4. ✅ Expected: Nothing happens (C not used in submenus)
5. Press Q to select first option
6. ✅ Expected: Submenu closes, action queues

## If Tests Fail:

**If C doesn't work:**
- Check console output (F12 or look at terminal)
- Make sure you're in ACTION_SELECTION phase (green)
- Make sure queue has items (button enabled)

**If button still enabled when empty:**
- This is the old build - need to re-export from Godot
- Go to Godot Editor → Project → Export → Windows Desktop → Export Project

## Next Steps After Testing:

If all tests pass → Re-export build → Package as zip → Create GitHub release
If tests fail → Report which test failed and I'll fix it

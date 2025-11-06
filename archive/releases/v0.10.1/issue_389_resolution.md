# Issue #389 Resolution - AP Validation

## Status: RESOLVED BY DESIGN ✅

## Original Issue
Action points system had validation issues where some actions had AP costs of 0, causing test failures.

## Resolution
The "0 AP cost" actions are **intentional and correct** - they are **submenu actions** that open dialogs for the player to select the actual action.

### Examples:
1. **"Hire Staff"** (id: `hire_staff`)
   - Costs: `{}` (no AP cost)
   - `is_submenu: true`
   - Opens dialog with hiring options (Safety Researcher, AI Ethicist, etc.)
   - The ACTUAL hire action costs AP (1 AP, $70k)

2. **"Fundraising"** (id: `fundraise`)
   - Costs: `{}` (no AP cost)
   - `is_submenu: true`
   - Opens dialog with funding options
   - The ACTUAL fundraising choice costs AP/reputation

### Why This Is Correct
- **Better UX**: Players can browse options without committing AP
- **Two-step commitment**: Open menu (free) → Select option (costs AP)
- **Clear intent**: Submenu actions are metadata, not gameplay actions
- **Queue system**: Only the selected submenu option gets queued with AP cost

### Implementation Details
```gdscript
// Submenu actions (0 AP cost)
{
    "id": "hire_staff",
    "costs": {},  // No cost to open menu
    "is_submenu": true
}

// Actual actions (has AP cost)
{
    "id": "hire_safety_researcher",
    "costs": {"money": 70000, "action_points": 1},
    "is_submenu": false
}
```

### Validation Logic
The game correctly handles this:
1. Clicking submenu action → Opens dialog (no AP spent)
2. Selecting option from dialog → Queues action with AP cost
3. Validation checks committed_ap before allowing queue
4. Only actual actions (not submenus) increment committed_ap

## Test Results
✅ Players can open submenus without AP cost
✅ Selecting from submenu correctly costs AP
✅ Can't overcommit AP (validation working)
✅ Clear Queue refunds AP correctly

## Conclusion
No code changes needed. The 0 AP cost is **by design** for submenu actions. The test expectations should be updated to account for legitimate meta-actions.

**Close issue #389 as "Working as intended"**

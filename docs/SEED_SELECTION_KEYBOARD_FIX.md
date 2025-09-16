# Seed Selection Keyboard Navigation Fix

## Issue Description
The seed selection screen had incomplete keyboard navigation. The `handle_seed_selection_keyboard` function contained a placeholder `pass` statement and no selection tracking variable, preventing users from navigating between "Use Weekly Seed" and "Use Custom Seed" options using arrow keys.

## Root Cause
1. Missing `seed_selected_item` global variable to track current selection
2. Incomplete keyboard navigation logic with `pass` placeholder
3. Hardcoded `selected_item=0` parameter in `draw_seed_selection` call

## Solution Implemented

### 1. Added Missing Selection Variable
Added `seed_selected_item = 0` to the global state variables around line 175:
```python
seed_selected_item = 0  # For seed selection navigation (0=Weekly, 1=Custom)
```

### 2. Implemented Proper Navigation Logic
Replaced the placeholder `pass` statement with functional UP/DOWN arrow handling:
```python
def handle_seed_selection_keyboard(key):
    """Handle keyboard navigation for seed selection screen."""
    global current_state, seed_choice, seed, seed_selected_item
    
    if key == pygame.K_UP:
        seed_selected_item = max(0, seed_selected_item - 1)
    elif key == pygame.K_DOWN:
        seed_selected_item = min(1, seed_selected_item + 1)  # 2 items: Weekly(0), Custom(1)
    elif key == pygame.K_RETURN:
        if seed_selected_item == 0:  # Weekly seed
            seed_choice = "weekly"
            seed = get_weekly_seed()
        else:  # Custom seed
            seed_choice = "custom"
            seed = seed_input if seed_input else get_weekly_seed()
        current_state = 'tutorial_choice'
    elif key == pygame.K_ESCAPE:
        current_state = 'pre_game_settings'
```

### 3. Updated UI Drawing Call
Changed the hardcoded `0` to use the actual selection state:
```python
draw_seed_selection(screen, SCREEN_W, SCREEN_H, seed_selected_item, seed_input, global_sound_manager)
```

### 4. Added Selection Reset
Added `seed_selected_item = 0` reset when transitioning to seed selection state (lines ~556 and ~580).

## Verification
- ✅ UP/DOWN arrows navigate between options
- ✅ Selection stays within bounds (0-1)
- ✅ Visual feedback shows selected option
- ✅ ENTER key selects chosen option and transitions properly
- ✅ ESCAPE key returns to previous screen
- ✅ Selection resets when entering the screen
- ✅ All existing keyboard navigation tests continue to pass

## Files Modified
- `main.py`: Added variable, implemented navigation logic, updated UI call, added resets

This fix follows the established pattern used by other menu screens in the codebase and provides full keyboard accessibility for the seed selection interface.

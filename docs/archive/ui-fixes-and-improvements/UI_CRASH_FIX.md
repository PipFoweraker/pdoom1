# UI Rectangle Crash Fix and Error Handling Improvements

## Problem Description

**Issue**: The game was crashing with a `TypeError: cannot unpack non-iterable NoneType object` error in the `_in_rect` method when checking mouse hover states.

**Root Cause**: The `_get_upgrade_rects()` method returns a list that can contain `None` values for upgrades that are not currently available or visible. The `check_hover()` method was iterating through this list without filtering out `None` values before passing them to `_in_rect()`, which attempted to unpack them as `(rx, ry, rw, rh)`.

**Stack Trace Location**: 
- File: `src/core/game_state.py`, line 1820, in `_in_rect`
- Called from: `check_hover` method when processing mouse hover events

## Additional Navigation Fix

**Issue**: End game menu "Settings" button was returning to main game launch window instead of proper settings menu.

**Root Cause**: The `handle_end_game_menu_click()` function was directly setting `current_state = 'overlay'` instead of using the navigation stack system with `push_navigation_state('overlay')`.

**Fix**: Changed to use proper navigation stack so settings overlay correctly returns to end game menu.

## Solution Implemented

### 1. Enhanced `_in_rect` Method
- Added null check for rectangle parameter
- Added try-catch error handling with logging
- Returns `False` gracefully for invalid rectangles

### 2. Enhanced `check_hover` Method  
- Added explicit `None` filtering for upgrade rectangles
- Wrapped entire method in try-catch for comprehensive error handling
- Added contextual error logging

### 3. Enhanced `handle_mouse_click` Method
- Added same `None` filtering for upgrade rectangles in click handling
- Prevents similar crashes during mouse click events

### 4. Rectangle Validation System
- Added `_validate_rect()` method for robust rectangle validation
- Enhanced `_get_upgrade_rects()` to validate rectangles before returning
- Added logging for invalid rectangle detection

### 5. General Error Handling Framework
- Added `_safe_ui_operation()` method for wrapping UI operations
- Consistent error logging across UI interactions
- Graceful degradation when errors occur

## Code Changes Summary

### Modified Files:
- `src/core/game_state.py` - Main fixes implemented

### Key Changes:

1. **`_in_rect` method**:
   ```python
   def _in_rect(self, pt, rect):
       """Check if point is within rectangle, with graceful error handling."""
       if not self._validate_rect(rect, "_in_rect"):
           return False
       
       try:
           x, y = pt
           rx, ry, rw, rh = rect
           return rx <= x <= rx+rw and ry <= y <= ry+rh
       except (TypeError, ValueError) as e:
           # Log the error for debugging
           if hasattr(self, 'game_logger'):
               self.game_logger.log(f"_in_rect error: pt={pt}, rect={rect}, error={e}")
           return False
   ```

2. **`check_hover` method**: Added `None` filtering:
   ```python
   for idx, rect in enumerate(u_rects):
       # Skip None rectangles (unavailable/hidden upgrades)
       if rect is None:
           continue
       if self._in_rect(mouse_pos, rect):
           # ... rest of hover logic
   ```

3. **Added validation framework**:
   ```python
   def _validate_rect(self, rect, context=""):
       """Validate that a rectangle is properly formatted."""
       # ... validation logic with logging
   ```

## Testing

Created `test_hover_fix.py` to verify:
- [EMOJI] Hover checking with `None` rectangles
- [EMOJI] Rectangle validation
- [EMOJI] Error handling in edge cases
- [EMOJI] Actual game functionality

## Prevention Strategies

### For Developers:

1. **Always validate rectangles**: Use `_validate_rect()` before UI operations
2. **Filter None values**: When iterating over rectangle lists, check for `None`
3. **Use error wrapping**: Wrap UI operations with `_safe_ui_operation()` when appropriate
4. **Test edge cases**: Test with various game states and upgrade configurations

### Code Patterns to Follow:

```python
# Good: Filter None values when iterating
for idx, rect in enumerate(rect_list):
    if rect is None:
        continue
    if self._in_rect(mouse_pos, rect):
        # ... safe to use rect

# Good: Validate before use
if self._validate_rect(rect, "operation_name"):
    # ... safe to use rect

# Good: Use error wrapping for complex operations
result = self._safe_ui_operation("hover_check", self.check_hover, mouse_pos, w, h)
```

### Code Patterns to Avoid:

```python
# Bad: Direct iteration without None check
for idx, rect in enumerate(rect_list):
    if self._in_rect(mouse_pos, rect):  # Can crash if rect is None
        # ...

# Bad: No validation of rectangle data
rx, ry, rw, rh = rect  # Can crash if rect is None or invalid
```

## Benefits of This Fix

1. **Crash Prevention**: Game no longer crashes on hover events
2. **Better Debugging**: Comprehensive logging helps identify future issues
3. **Graceful Degradation**: Game continues to function even with UI errors
4. **Future-Proof**: Framework prevents similar issues in new code
5. **Better User Experience**: Seamless gameplay without unexpected crashes

## Performance Impact

Minimal - the validation checks are lightweight and only add a few milliseconds to UI operations. The error handling only activates when problems occur, so normal gameplay performance is unaffected.

## Monitoring

The fix includes comprehensive logging that will help identify:
- Invalid rectangle data being generated
- UI interaction errors
- Performance issues in rectangle operations

Check game logs for messages starting with:
- "Invalid rectangle"
- "Error in check_hover"
- "_in_rect error"
- "Error validating rectangle"

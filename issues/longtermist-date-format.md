# Longtermist Date Format (5-Digit Years)

## Summary
Implement 5-digit year format (YYYYY-MMM-DD) for P(Doom) game dates as a longtermist touch, displaying dates like '02025/May/21' instead of '25/May/25'.

## Background
As a longtermist-themed game, P(Doom) would benefit from a date format that emphasizes longer time horizons. The current GameClock system uses 2-digit years (YY format), but displaying 5-digit years would add thematic flavor while maintaining all existing functionality.

## Scope Assessment
This is a **display-only change** - no breaking changes to core logic:
- GameClock internally uses standard datetime objects (2016, 2017, etc.)
- Only formatting methods need modification
- Save files, persistence, and all datetime math remain unchanged
- Libraries (datetime, timedelta) continue working normally

## Implementation Plan

### Phase 1: Core Display Methods
Modify GameClock formatting methods:
- `get_formatted_date()` - Change from 'DD/Mon/YY' to 'DD/Mon/YYYYY'
- `format_date()` - Update arbitrary date formatting
- `parse_formatted_date()` - Update parsing to handle 5-digit years

### Phase 2: Test Updates
Update test expectations:
- All format assertions in `tests/test_clock.py`
- Update expected strings from '04/Apr/16' to '04/Apr/02016'
- Verify parsing handles both formats (backward compatibility)

### Phase 3: Optional Extensions
Consider updating (low priority):
- Dev-blog date templates (currently YYYY-MM-DD)
- Screenshot timestamps (internal use only)
- Documentation examples

## Target Format Examples
- Current: '04/Apr/16', '25/Dec/14', '01/Jan/20'
- New: '04/Apr/02016', '25/Dec/02014', '01/Jan/02020'
- Game start: '04/Apr/02016' (April 4, 2016)

## Technical Details

### Files to Modify
1. **Primary**: `src/services/game_clock.py`
   - `get_formatted_date()` method
   - `format_date()` method  
   - `parse_formatted_date()` method
   - Update MONTH_ABBREVS usage

2. **Tests**: `tests/test_clock.py`
   - Update all expected date format strings
   - Add tests for 5-digit year parsing
   - Ensure backward compatibility

3. **Documentation**: Update any date format examples

### Implementation Strategy
```python
# Current formatting (line ~130 in game_clock.py):
year = self.current_date.year % 100  # Last 2 digits

# New formatting:
year = self.current_date.year  # Full 5-digit display with leading zeros
return f'{day:02d}/{month_abbrev}/{year:05d}'
```

## Testing Strategy
- Verify all existing tests pass with new format
- Test date parsing for both 2-digit and 5-digit years
- Confirm game progression still shows proper date advancement
- Validate save/load persistence unchanged

## Risk Assessment
**Low Risk** - This is purely cosmetic display formatting:
- No changes to core game logic
- No breaking changes to save files
- Standard datetime objects used throughout
- Easy to revert if needed

## Acceptance Criteria
- [ ] Game dates display as 5-digit years (e.g., '04/Apr/02016')
- [ ] Date progression works correctly through gameplay
- [ ] All existing tests pass with updated expectations
- [ ] Save/load functionality unchanged
- [ ] Performance impact negligible
- [ ] Backward compatibility maintained for parsing

## Future Considerations
- Could add configuration option to switch between formats
- Consider extending to other date displays in UI
- Potential for 'deep time' calendar features

## Priority
**Experimental** - Fun longtermist flavor enhancement, no impact on core gameplay

## Labels
- experimental
- ui-enhancement
- longtermist-theme
- low-risk
- display-only

---
*Created in experimental/longtermist-dates branch as a side quest feature*

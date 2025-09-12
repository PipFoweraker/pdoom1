# Enable and Configure Leaderboard System for Alpha

## Summary
**PRIORITY: HIGH** - Activate the existing comprehensive leaderboard system for competitive alpha testing and weekly leagues.

## Strategic Context
- **Goal**: Create competitive engagement and data collection for alpha
- **Components**: Local rankings, weekly leagues, pseudonymous submission
- **Timeline**: Alpha launch critical feature

## Current State - SYSTEM EXISTS!
**Found comprehensive leaderboard infrastructure:**
- ✅ `LocalLeaderboard` class with full ranking system
- ✅ `LeaderboardManager` with privacy-respecting submission
- ✅ `ScoreEntry` system with metadata tracking
- ✅ High score UI screen (placeholder state)
- ✅ Privacy manager with pseudonym generation

## Required Activation Tasks

### Phase 1: Basic Leaderboard (Alpha Launch)
1. **Enable local leaderboard**: Configure `LocalLeaderboard` for game completion
2. **Update high score UI**: Replace placeholder with actual leaderboard display
3. **Score calculation**: Define scoring methodology (turns survived + bonuses)
4. **Weekly reset**: Implement weekly league mechanics

### Phase 2: Enhanced Features (Alpha+)  
5. **Game mode filtering**: Separate leaderboards for difficulty levels
6. **Statistics display**: Show player rank, percentiles, progress
7. **Privacy controls**: User-friendly opt-in/opt-out interface
8. **Data validation**: Checksum verification for score integrity

## Implementation Files
- **Core**: `src/scores/local_store.py` (ready)
- **Manager**: `src/services/leaderboard.py` (ready) 
- **UI**: `ui.py` draw_high_score_screen() (needs activation)
- **Integration**: `main.py` score submission hooks (needs wiring)

## Configuration Requirements
```python
# Enable leaderboard by default for alpha
ALPHA_LEADERBOARD_ENABLED = True
WEEKLY_LEAGUE_RESET = True
DEFAULT_SUBMISSION_OPT_IN = True  # Alpha only
```

## Success Criteria
- [ ] Players see leaderboard after game completion
- [ ] Scores persist between game sessions  
- [ ] Weekly leagues reset automatically
- [ ] Privacy controls function correctly
- [ ] Score submission works without errors

## Testing Requirements
- [ ] Multiple game completions create leaderboard entries
- [ ] Rank calculation works correctly
- [ ] UI displays top scores properly
- [ ] Weekly reset functionality
- [ ] Pseudonym generation and privacy compliance

## Priority: HIGH
**Effort**: 2-4 hours (mostly UI integration)
**Impact**: Major competitive engagement
**Risk**: Low (existing robust system)

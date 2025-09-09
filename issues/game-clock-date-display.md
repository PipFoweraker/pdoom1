# Game Clock Date Display Integration

## Summary
Wire the existing GameClock service into GameState to show the current game date in the activity log and advance it weekly on each turn.

## Background
The GameClock service exists in `src/services/game_clock.py` with weekly tick functionality and DD/Mon/YY formatting, but it's not integrated into the main game loop or displayed to the player.

## Acceptance Criteria
- [ ] GameState initializes a GameClock instance on startup
- [ ] Each `end_turn()` call advances the clock by one week (7 days)
- [ ] Activity log shows date on turn advancement: "Week of 01/Jul/14 (Mon)"
- [ ] Date starts at July 1, 2014 (GameClock default) and increments to Mondays
- [ ] GameClock state persists between game sessions (save/load)

## Implementation Notes
- Import GameClock in GameState from `src.services.game_clock`
- Add `self.game_clock = GameClock()` in `__init__`
- In `end_turn()`, call `self.game_clock.tick()` and log the formatted date
- Consider header UI display in a future enhancement

## Files to Modify
- `src/core/game_state.py`: Add GameClock integration
- Optionally update save/load logic to persist clock state

## Priority
Medium - enhances immersion and provides temporal context for decisions.

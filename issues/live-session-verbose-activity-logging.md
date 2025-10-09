# LIVE SESSION: Enhanced Activity Log Verbosity

## Issue Summary
Make activity log more verbose by default to show detailed turn-by-turn progression like classic RPG combat logs ('you deal 20 damage to the orc!' style).

## Current State
- Activity log shows basic action results
- Limited detail on what happened during turn processing
- Players miss nuanced feedback about their actions

## Proposed Enhancement
Add detailed, RPG-style logging throughout turn sequence:

### Action Execution Feedback
```
> You execute Safety Research action (costs $40k, 1 AP)
> Research team discovers new alignment technique! 
> Doom reduced by 4 points (87 -> 83)
> Reputation increased by 2 points (12 -> 14)
```

### Economic System Feedback  
```
> Market conditions: Stable phase (1.0x funding multiplier)
> Fundraising attempt: Targeting venture capital
> Success! Secured $85k from venture capital
> Cash reserves: $45k -> $130k
```

### Staff Management Feedback
```
> Paying staff maintenance: 5 researchers x $15k = $75k
> All staff retained and productive
> Research productivity: +15% from happy staff
```

### Event System Feedback
```
> Random event triggered: 'Competitor Announces Breakthrough' 
> Impact: Doom +2, Competitive pressure increased
> Your response: Accelerate safety research recommended
```

## Implementation Points
- Enhanced logging in `src/core/game_state.py` turn processing
- Detailed feedback in action execution functions
- Verbose economic system reporting
- Rich event descriptions with impact analysis

## Benefits
- Better player understanding of game mechanics
- More engaging feedback loop
- Clearer cause-and-effect relationships
- Enhanced strategic decision making

## Priority
**HIGH** - Live session enhancement

## Files to Modify
- `src/core/game_state.py` (turn processing)
- `src/core/actions.py` (action execution feedback)
- `src/features/economic_cycles.py` (funding feedback)
- `src/core/events.py` (event impact descriptions)

## Acceptance Criteria
- [ ] Action execution provides detailed feedback
- [ ] Turn processing shows step-by-step progression
- [ ] Economic transactions are clearly explained
- [ ] Event impacts are described in detail
- [ ] Activity log is engaging and informative
- [ ] Verbose logging doesn't overwhelm UI

## Labels
`enhancement`, `ui-ux`, `live-session`, `player-experience`

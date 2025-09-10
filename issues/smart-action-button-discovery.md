# Smart Action Button Discovery System (Tech Tree Style)

## Summary
Implement intelligent action button states that progressively reveal abilities as prerequisites are met, similar to Starcraft 2 tech tree visualization.

## Enhancement Description
Transform the current action button system (left side of screen) to use progressive discovery:

### Current State
- All action buttons visible immediately
- Button states: available, cost-blocked, or disabled
- No mystery or progression feel

### Proposed Smart System
1. **Undiscovered State** (Initial)
   - Buttons greyed out completely
   - No description text visible
   - Non-interactive appearance
   - Hint that something exists without revealing details

2. **Discovered State** (Prerequisites Met)
   - Button becomes highlighted and obviously clickable
   - Full description and cost information revealed
   - Visual transition to indicate "unlocked" status
   - Even if cost-blocked, shows as discoverable

3. **Available State** (Ready to Use)
   - Fully active and clickable
   - All information displayed
   - Clear cost and effect details

## Visual Design Inspiration
Based on Starcraft 2 tech tree approach:
- **Locked**: Dim, mysterious, minimal visual information
- **Available**: Bright highlight indicating discoverability
- **Purchasable**: Full brightness with clear interaction cues

## Game Design Benefits
- **Progressive Discovery**: Teases future abilities without overwhelming
- **Sense of Progression**: Players feel they're unlocking new capabilities
- **Reduced Cognitive Load**: Shows only relevant options initially
- **Increased Engagement**: Creates curiosity about locked abilities

## Technical Implementation
### Button State System
```
enum ActionButtonState {
    UNDISCOVERED,    // Prerequisites not met
    DISCOVERED,      // Prerequisites met, but may be cost-blocked
    AVAILABLE        // Can be used immediately
}
```

### Visual States
- **Undiscovered**: 
  - 30% opacity
  - No text description
  - Greyed out appearance
  - No hover effects

- **Discovered**:
  - 80% opacity
  - Full description visible
  - Subtle highlight border
  - Hover effects enabled
  - "Newly unlocked" visual cue

- **Available**:
  - 100% opacity
  - Full interactivity
  - Cost information displayed
  - Click effects enabled

## Prerequisites System
Define clear unlock conditions:
- Staff count thresholds
- Money milestones
- Previous action completions
- Research progress gates
- Turn number requirements

## Files Involved
- `actions.py` - Action definition and prerequisites
- `ui.py` - Button rendering and state management
- Action button display logic
- Game state integration

## User Experience Goals
1. **Intuitive Progression**: Clear visual feedback for advancement
2. **Curiosity Drive**: Hint at future possibilities
3. **Achievement Feel**: Satisfaction when unlocking new abilities
4. **Reduced Overwhelm**: Show only relevant options

## Implementation Phases

### Phase 1: Core State System
- [ ] Define button state enum
- [ ] Implement prerequisite checking logic
- [ ] Basic visual state differentiation

### Phase 2: Visual Polish
- [ ] Smooth state transition animations
- [ ] "Newly unlocked" highlight effects
- [ ] Consistent visual language across all buttons

### Phase 3: Balance and Tuning
- [ ] Adjust prerequisite thresholds
- [ ] User testing for optimal discovery pacing
- [ ] Fine-tune visual feedback timing

## Priority
**Medium-High** - Significant UX enhancement that improves game feel

## Labels
- enhancement
- ui-ux
- game-mechanics
- progressive-disclosure
- user-experience

## Acceptance Criteria
- [ ] Action buttons start in undiscovered state
- [ ] Prerequisites clearly unlock button visibility
- [ ] Smooth visual transitions between states
- [ ] Maintains all existing functionality
- [ ] Improves new player experience
- [ ] No performance regression
- [ ] Clear visual language for all states

## Assignee
@PipFoweraker

## References
- Starcraft 2 tech tree UI patterns
- Progressive disclosure UX principles
- Game progression mechanics best practices

---
*Enhancement identified during local testing - develop branch*

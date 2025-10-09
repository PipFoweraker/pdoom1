# Top Icon Hover Context Enhancement

## Summary
Add hover context tooltips for the top resource icons (Money, Staff, AP, Reputation, Doom, Compute) to provide quick information about each resource.

## Background
The game has a hover context system that shows information in the bottom context window, but the top resource icons lack detailed tooltips. New players especially benefit from understanding what each resource represents.

## Current State
- `GameState.check_hover()` handles hover detection for actions/upgrades/End Turn
- Bottom context window displays hover information
- Top resource icons show values but no explanatory context

## Acceptance Criteria
- [ ] Hovering over Money icon shows: 'Money: Funds for actions, upgrades, and staff salaries'
- [ ] Hovering over Staff icon shows: 'Staff: Team members providing action points'
- [ ] Hovering over AP icon shows: 'Action Points: Actions you can take this turn'
- [ ] Hovering over Reputation icon shows: 'Reputation: Public trust affecting funding opportunities'
- [ ] Hovering over Doom icon shows: 'p(Doom): Probability of existential catastrophe'
- [ ] Hovering over Compute icon shows: 'Compute: Computational resources for research'
- [ ] Context appears in the existing bottom context window
- [ ] Context is concise and informative (under 80 characters)

## Implementation Notes
- Extend `check_hover()` method to detect top icon regions
- Add icon rect calculations similar to action/upgrade rects
- Use existing context window system for display
- Consider icon positioning and hover regions for accuracy

## Files to Modify
- `src/core/game_state.py`: `check_hover()` method and icon rect calculations
- Potentially UI rendering code for icon positioning

## Priority
Low - quality of life improvement for user experience and onboarding.

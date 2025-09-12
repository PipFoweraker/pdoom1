# LIVE SESSION: Expanded Fundraising Menu Options

## Issue Summary
Expand fundraising from single action to submenu with 4+ options like "Hire Staff", providing player choice and strategic trade-offs.

## Current State
- Single "Fundraise" action with automated source selection
- Limited player agency in funding strategy
- No risk/reward trade-offs in funding approach

## Proposed Fundraising Menu Structure

### 1. Fundraise Small
- **Description**: "Conservative funding approach - lower amounts, lower risk"
- **Mechanics**: $30-60k range, minimal reputation risk, always available
- **Trade-off**: Lower amounts but safe and reliable

### 2. Fundraise Big  
- **Description**: "Aggressive funding round - higher amounts, higher stakes"
- **Mechanics**: $80-150k range, reputation risk, requires established traction
- **Trade-off**: Higher potential but requires confidence/reputation

### 3. Borrow Money
- **Description**: "Immediate funds via debt - pay back with interest later"  
- **Mechanics**: Immediate cash, creates future payment obligations
- **Trade-off**: Instant liquidity vs future financial burden

### 4. Alternative Funding
- **Description**: "Grants, partnerships, revenue - non-traditional sources"
- **Mechanics**: Government grants, corporate partnerships, customer revenue
- **Trade-off**: Different requirements/timelines but diverse risk profile

## Strategic Benefits
- **Player Agency**: Choice between conservative vs aggressive strategies
- **Risk Management**: Different risk/reward profiles for different situations  
- **Economic Depth**: More nuanced funding strategy gameplay
- **Replayability**: Different approaches for different market conditions

## Implementation Architecture

### Menu Structure (Similar to Hire Staff)
```python
def get_fundraising_submenu_options(game_state):
    options = []
    
    # Always available: conservative funding
    options.append({
        "name": "Fundraise Small",
        "desc": "Conservative funding ($30-60k, low risk)",
        "action": "fundraise_small"
    })
    
    # Requires reputation: aggressive funding  
    if game_state.reputation >= 8:
        options.append({
            "name": "Fundraise Big", 
            "desc": "Aggressive funding ($80-150k, higher risk)",
            "action": "fundraise_big"
        })
    
    # Always available: debt financing
    options.append({
        "name": "Borrow Money",
        "desc": "Immediate funds with future repayment",
        "action": "borrow_money"  
    })
    
    # Unlocked after certain milestones
    if hasattr(game_state, 'advanced_funding_unlocked'):
        options.append({
            "name": "Alternative Funding",
            "desc": "Grants, partnerships, revenue streams", 
            "action": "alternative_funding"
        })
    
    return options
```

## Priority
**MEDIUM** - Live session enhancement (after activity log changes)

## Files to Modify
- `src/core/actions.py` (add new funding actions)
- `ui.py` or relevant UI files (add submenu interface)
- `src/features/economic_cycles.py` (enhanced funding mechanics)

## Acceptance Criteria
- [ ] Fundraising opens submenu with 4+ options
- [ ] Each option has distinct risk/reward profile
- [ ] Menu interface matches existing patterns (hire staff)
- [ ] Strategic choices feel meaningful
- [ ] Options unlock based on game progression
- [ ] Economic balance maintained

## Labels  
`enhancement`, `game-mechanics`, `live-session`, `player-agency`

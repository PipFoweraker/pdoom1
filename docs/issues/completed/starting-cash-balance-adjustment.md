# Increase Starting Cash for Alpha Testing

## OK COMPLETED v0.4.1 - EXCEEDS REQUIREMENTS
**Bootstrap Economic System**: Starting cash now $100,000 (10x requested amount) with realistic weekly staff maintenance costs creating authentic strategic pressure.

## Summary
~~**PRIORITY: HIGH** - Increase starting cash from $2,000 to $10,000 to provide players with more strategic optionality during alpha testing phase.~~

## Strategic Context
- **Goal**: Give alpha testers meaningful choices and prevent early-game resource constraints
- **Impact**: More engaging gameplay, better testing of mid-game mechanics
- **Timeline**: Immediate (pre-alpha launch)

## Current State
- Starting money: $2,000 (in `src/services/config_manager.py`)
- Players report feeling constrained in early decisions
- Limited ability to test various strategic paths

## Proposed Changes
1. **Update default config**: Change `"money": 2000` to `"money": 10000`
2. **Verify balance**: Ensure $10k doesn't trivialize early-game challenges
3. **Document change**: Update changelog with balance rationale

## Implementation
**Location**: `src/services/config_manager.py` line ~95
```python
"starting_resources": {
    "money": 10000,  # Increased from 2000 for alpha testing
    ...
}
```

## Testing Requirements
- [ ] Verify game starts with correct amount
- [ ] Test early-game action availability with higher cash
- [ ] Ensure UI displays correctly with 5-digit numbers
- [ ] Validate save/load preserves new starting amount

## Success Criteria
- Players report more strategic flexibility
- Alpha testers can explore diverse opening strategies
- No UI layout issues with larger money values
- Maintains challenge after initial resource phase

## Priority: HIGH
**Effort**: 5 minutes
**Impact**: High player satisfaction
**Risk**: Low (easily reversible)

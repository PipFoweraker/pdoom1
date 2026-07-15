# Personnel System Balancing Notes

Values requiring playtesting and future tuning for the enhanced personnel system (#197).

## Candidate Pool

### Population Rate
- **Base chance**: 30% per turn
- **Empty slot bonus**: +10% per empty slot
- **Reputation bonus**: +10% if reputation > 60
- **Double candidate chance**: 20% when pool < 3

**Tuning considerations**: If players feel stuck without candidates, increase base chance or reduce turn interval.

### Pool Size
- **Max candidates**: 6
- **Starting candidates**: 2-3 (50% chance for third)
- **Starting skill range**: 1-3 (intentionally low quality)

**Tuning considerations**: May need to allow 8+ candidates for larger organizations.

### Specialization Weights
- Safety: 35%
- Capabilities: 25%
- Interpretability: 20%
- Alignment: 20%

**Tuning considerations**: Adjust based on desired safety/capabilities balance.

## Researcher Traits

### Trait Probabilities
- **Positive trait chance**: 40%
- **Negative trait chance**: 25%

### Trait Effects
- **team_player**: +10% productivity per team player present (stacking)
- **leak_prone**: 1% chance per turn for +3.0 doom leak
- **media_savvy**: +3 reputation per researcher when publishing papers
- **safety_conscious**: +0.1 doom reduction for safety researchers
- **workaholic**: +25% productivity (defined in Researcher class)
- **burnout_prone**: +50% burnout accumulation
- **fast_learner**: +50% skill growth rate
- **prima_donna**: -20% productivity when other researchers present
- **pessimist**: -10% to team morale effects

**Tuning considerations**:
- leak_prone at 1% feels rare - increase if players never see leaks
- team_player stacking might need cap (currently unlimited)

## Team Management

### Team Structure
- **Team size**: 8 researchers per team
- **Manager capacity**: 1 team per manager
- **Unmanaged penalty**: +0.5 doom per unproductive researcher per turn

**Tuning considerations**:
- May want 6-10 variable team sizes
- Unmanaged penalty might be too harsh early game

## Specialization Effects

### Research Speed
- **Capabilities**: +25% research generation
- Others: base rate

### Doom Modifiers
- **Capabilities**: Adds doom based on researcher's doom_modifier (0.3-0.7)
- **Safety**: -0.3 doom reduction per productive researcher
- **Alignment**: -0.15 doom reduction per productive researcher

### Stationery Consumption
- Safety/Alignment: 1.0 per turn
- Interpretability: 0.8 per turn
- Capabilities: 0.5 per turn
- Managers: 0.5 per turn

## Poaching Events

### Trigger Conditions
- **Minimum turn**: 20
- **Probability**: 4% per turn (when conditions met)
- **Threshold**: researchers >= 2

**Tuning considerations**:
- User requested "less than once per year"
- At 12 turns/year, 4% gives ~48% chance per year (may be too high)
- Consider reducing to 2-3% for more infrequent poaching

### Poaching Costs
- **Match offer**: $100,000
- **Counter promotion**: $150,000

## Resource Costs

### Hiring Costs
- Safety/Capability Researcher: $60,000
- Compute Engineer: $50,000
- Manager: $80,000
- Ethicist: $70,000

### Salaries
- Individual researchers: Based on Researcher.current_salary / 12 per turn
- Managers: $5,000 per turn (flat rate)

## Known Issues for Future Tuning

1. **Poaching frequency**: 4% may trigger more than intended "once per year"
2. **Team player stacking**: Unlimited stacking could be exploited
3. **Starting candidates**: Low skill (1-3) might frustrate early game
4. **Candidate visibility**: UI needs to show available candidates before hiring
5. **Salary variation**: Need to verify salary range feels appropriate

## Recommended Playtest Scenarios

1. **Early game hiring**: Start game, try to hire - are candidates available?
2. **Poaching pressure**: Play 30+ turns - does poaching feel fair?
3. **Team scaling**: Grow to 16+ researchers - is management overhead reasonable?
4. **Trait impact**: Do traits feel meaningful without being overpowered?

## Version History

- **v0.11.0**: Initial implementation of enhanced personnel system (#197)

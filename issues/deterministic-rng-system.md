# Deterministic RNG System for Reproducible Gameplay

## Summary  
**PRIORITY: MEDIUM** - Implement deterministic random number generation to enable reproducible gameplay, bug reproduction, and competitive integrity.

## Strategic Context
- **Goal**: Enable reproducible gameplay for testing and competition
- **Current**: Standard Python random (non-deterministic)
- **Target**: Seed-based deterministic RNG with replay capability
- **Impact**: Better bug diagnosis, competitive fairness, demo consistency

## Current State Analysis

### Existing Random Usage
**Need to audit current random.py usage patterns:**
- Event system randomization
- Opponent AI decision making  
- Crisis event selection and parameters
- Resource variation calculations
- Any procedural generation elements

### Found Infrastructure
**Existing systems that support deterministic gameplay:**
- OK Game state management with turn tracking
- OK Action system with clear state transitions
- OK Event system with defined outcomes
- OK Configuration management for game parameters

## Required Implementation

### Phase 1: Deterministic Core (Alpha Priority)
1. **Seeded RNG Class**: Replace random.random() with seeded generator
2. **State Preservation**: RNG state saves with game state  
3. **Audit Current Usage**: Identify all random.py calls
4. **Migration Strategy**: Replace with deterministic equivalents
5. **Seed Management**: User-selectable and auto-generated seeds

### Phase 2: Replay System (Beta Priority)
6. **Action Recording**: Log all player decisions with RNG state
7. **Replay Playback**: Reproduce exact game sequences
8. **Demo Mode**: Share deterministic gameplay scenarios
9. **Bug Reproduction**: Recreate reported issues exactly
10. **Competitive Validation**: Verify fair play in tournaments

### Phase 3: Advanced Features (Post-Release)
11. **Branching Analysis**: Show alternative outcomes from decision points
12. **Statistical Validation**: Verify RNG distribution properties
13. **Performance Optimization**: Efficient deterministic generation
14. **Cross-Platform Consistency**: Same results across systems
15. **Save State Integration**: RNG state in save files

## Implementation Architecture

### Deterministic RNG Manager
```python
class DeterministicRNG:
    def __init__(self, seed=None):
        self.seed = seed or self.generate_seed()
        self.rng = random.Random(self.seed)
        self.state_history = []
        
    def random(self):
        '''Replacement for random.random()'''
        value = self.rng.random()
        self.state_history.append(self.rng.getstate())
        return value
        
    def choice(self, sequence):
        '''Replacement for random.choice()'''
        return self.rng.choice(sequence)
        
    def randint(self, a, b):
        '''Replacement for random.randint()'''
        return self.rng.randint(a, b)
        
    def get_state(self):
        '''Get current RNG state for saving'''
        return {
            'seed': self.seed,
            'state': self.rng.getstate(),
            'history_length': len(self.state_history)
        }
        
    def set_state(self, state_data):
        '''Restore RNG state from save'''
        self.seed = state_data['seed']
        self.rng.setstate(state_data['state'])
```

### Game State Integration
```python
# In game_state.py - add RNG state management
class GameState:
    def __init__(self, seed=None):
        self.rng = DeterministicRNG(seed)
        # ... existing initialization
        
    def save_state(self):
        state_data = {
            # ... existing save data
            'rng_state': self.rng.get_state(),
            'seed': self.rng.seed
        }
        return state_data
        
    def load_state(self, state_data):
        # ... existing load logic
        self.rng.set_state(state_data['rng_state'])
```

### Action Replay System
```python
class GameReplay:
    def __init__(self, initial_seed):
        self.seed = initial_seed
        self.action_sequence = []
        self.rng_checkpoints = []
        
    def record_action(self, action_data, rng_state):
        '''Record player action with RNG state'''
        self.action_sequence.append({
            'action': action_data,
            'rng_state': rng_state,
            'timestamp': time.time()
        })
        
    def replay_to_turn(self, target_turn):
        '''Replay game to specific turn'''
        game_state = GameState(self.seed)
        for i, recorded_action in enumerate(self.action_sequence):
            if game_state.turn >= target_turn:
                break
            game_state.rng.set_state(recorded_action['rng_state'])
            # Execute recorded action
        return game_state
```

## Migration Strategy

### Phase 1: Audit and Replace
1. **Search all random usage**: `grep -r 'import random' src/`
2. **Replace random calls**: Convert to deterministic equivalents
3. **Test compatibility**: Verify identical behavior with seeds
4. **Performance validation**: Ensure no significant slowdown

### Phase 2: Integration  
5. **Game state integration**: Add RNG state to save/load
6. **UI seed selection**: Allow players to choose/see seeds
7. **Debug console integration**: Show current seed and RNG state
8. **Configuration options**: Enable/disable deterministic mode

### Common Random Usage Patterns
```python
# Before: Non-deterministic
import random
event_choice = random.choice(available_events)
crisis_severity = random.randint(1, 10)
success_chance = random.random()

# After: Deterministic  
event_choice = self.game_state.rng.choice(available_events)
crisis_severity = self.game_state.rng.randint(1, 10)
success_chance = self.game_state.rng.random()
```

## File Integration Points

### Core Files to Modify
- **Core**: `src/core/game_state.py` (add RNG management)
- **New**: `src/services/deterministic_rng.py` (RNG manager)
- **New**: `src/services/game_replay.py` (replay system)
- **Events**: `src/core/events.py` (replace random calls)
- **Actions**: `src/core/actions.py` (replace random calls)  
- **Opponents**: `src/opponents.py` (replace random calls)

### UI Integration
- **Debug Console**: Show seed and RNG state
- **Settings Menu**: Seed selection interface
- **Game Setup**: Option to enter custom seed
- **Replay Browser**: List and play saved replays

## Seed Management

### Seed Generation
```python
def generate_game_seed():
    '''Generate human-readable game seed'''
    # Use timestamp + random component for uniqueness
    # Format: 'DOOM-2024-1234-ABCD' (human readable)
    
def parse_seed_input(user_input):
    '''Parse user-provided seed (flexible format)'''
    # Accept various formats: numbers, words, mixed
```

### Seed Display
- **Game Setup**: Show selected seed
- **Debug Console**: Current seed and RNG calls made
- **Save Files**: Include seed in save metadata  
- **Replay Files**: Seed + action sequence

## Success Criteria
- [ ] All random events are reproducible with same seed
- [ ] Game replays produce identical outcomes
- [ ] Save/load preserves RNG state correctly
- [ ] Performance impact is minimal (<5%)
- [ ] Seeds work consistently across platforms
- [ ] Debug tools show RNG state clearly
- [ ] Competitive integrity is maintained

## Testing Requirements
- [ ] Verify identical outcomes with same seed
- [ ] Test RNG state save/load functionality
- [ ] Validate replay system accuracy  
- [ ] Check performance with deterministic RNG
- [ ] Test seed parsing and generation
- [ ] Verify cross-platform consistency
- [ ] Ensure no random.py usage remains

## Competitive Benefits
- **Tournament Play**: Ensure fair starting conditions
- **Bug Reports**: Reproducible issue scenarios  
- **Demo Creation**: Consistent demonstration gameplay
- **Balance Testing**: Controlled scenario analysis
- **Speedrunning**: Standardized challenge seeds

## Priority: MEDIUM
**Effort**: 1-2 weeks (significant codebase audit required)
**Impact**: High for competitive play and bug diagnosis  
**Risk**: Medium (extensive codebase changes)
**Timeline**: Post-beta (polish and competitive features)

## Implementation Notes
- Maintain backward compatibility with existing saves
- Consider performance impact of RNG state tracking
- Ensure cross-platform deterministic behavior
- Plan migration strategy for existing random usage
- Document seed format and replay file structure

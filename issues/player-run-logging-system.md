# Privacy-Respecting Player Run Logging System

## Summary
**PRIORITY: HIGH** - Enable comprehensive game run logging with privacy controls, defaulting to ON for dev builds to accumulate strategy data for balancing.

## Strategic Context
- **Goal**: Collect gameplay data for balance analysis and strategy validation
- **Privacy**: Opt-in system with pseudonymous data collection
- **Dev Focus**: Default ON for alpha/beta, OFF for release builds
- **Data Usage**: Strategy analysis, balance tuning, dominant strategy detection

## Current State - FOUNDATION EXISTS!
**Found privacy-respecting logging infrastructure:**
- ✅ `PrivacyManager` with pseudonym generation
- ✅ `LeaderboardManager` with metadata tracking
- ✅ Game checksum and verification systems
- ✅ Configurable submission settings

## Required Enhancement

### Phase 1: Dev Build Logging (Alpha Priority)
1. **Enable by default**: Set `DEFAULT_LOGGING_ENABLED = True` for dev builds
2. **Comprehensive tracking**: Log all player actions, game state changes
3. **Run analytics**: Track full game sessions with strategy patterns
4. **Balance data**: Collect resource curves, action frequency, victory conditions

### Phase 2: Privacy Controls (Beta Priority)
5. **User controls**: Clear opt-in/opt-out interface
6. **Data transparency**: Show exactly what data is collected
7. **Local-first**: Always store locally, cloud submission optional
8. **Anonymization**: Remove personally identifiable information

## Implementation Architecture

### Core Logging System
```python
class GameRunLogger:
    def __init__(self, enabled_by_default=False):
        self.privacy_manager = PrivacyManager()
        self.enabled = enabled_by_default
        self.run_data = {
            'actions': [],
            'state_changes': [],
            'metadata': {},
            'strategy_patterns': []
        }
    
    def log_action(self, action_type, ap_cost, result):
        # Track player decision patterns
        
    def log_state_change(self, resource, old_value, new_value, cause):
        # Track resource flow and game balance
        
    def analyze_run(self):
        # Generate strategy analysis for balance team
```

### Dev Build Configuration
```python
# In config_manager.py - dev builds only
DEV_LOGGING_CONFIG = {
    'enabled_by_default': True,
    'collect_action_sequences': True,
    'track_resource_curves': True,  
    'analyze_victory_conditions': True,
    'log_dominant_strategies': True
}
```

## Data Collection Scope

### Player Actions
- Action type, AP cost, turn number
- Available alternatives at decision point
- Resource state before/after action
- Success/failure outcomes

### Game State Progression  
- Resource curves (money, staff, reputation, doom)
- Milestone achievements and timing
- Crisis events and player responses
- Victory/defeat conditions and causes

### Strategy Analysis
- Opening move patterns
- Mid-game resource allocation
- Dominant strategy identification
- Balance point analysis

## Privacy Implementation

### Pseudonymous Data
- Generate unique session ID per game
- Use lab names instead of player names
- No personally identifiable information
- Local storage with optional cloud sync

### User Controls
```python
def configure_logging_preferences(user_choice):
    if user_choice == 'full_logging':
        # Collect comprehensive data for balance
    elif user_choice == 'minimal_logging':  
        # Only basic performance metrics
    elif user_choice == 'no_logging':
        # Disable all data collection
```

## File Integration Points
- **Core**: `src/services/game_run_logger.py` (new)
- **Privacy**: `src/services/privacy_manager.py` (enhance existing)
- **Config**: `src/services/config_manager.py` (add logging config)
- **Game State**: `src/core/game_state.py` (add logging hooks)
- **UI**: Add privacy controls to settings menu

## Success Criteria
- [ ] Dev builds log comprehensive gameplay data by default
- [ ] Privacy controls allow user opt-out
- [ ] Data collection is pseudonymous and secure  
- [ ] Balance team can analyze strategy patterns
- [ ] No performance impact during gameplay
- [ ] Clear user communication about data collection

## Testing Requirements
- [ ] Verify logging captures complete game runs
- [ ] Test privacy controls work correctly
- [ ] Validate data anonymization  
- [ ] Check performance impact is minimal
- [ ] Ensure opt-out is respected
- [ ] Test data export for analysis

## Release Strategy
1. **Alpha**: Enabled by default with clear notification
2. **Beta**: User choice during onboarding
3. **Release**: Disabled by default, opt-in only
4. **Post-Release**: Remove from non-dev builds entirely

## Priority: HIGH  
**Effort**: 1-2 days (leverage existing privacy infrastructure)
**Impact**: Critical for balance validation
**Risk**: Low (privacy framework exists)
**Timeline**: Pre-alpha (data collection critical)

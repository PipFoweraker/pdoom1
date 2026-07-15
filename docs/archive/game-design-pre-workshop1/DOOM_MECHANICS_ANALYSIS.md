# P(Doom) Mechanics Analysis and Tuning Guide

## Current Doom Mechanics Review

### Starting Conditions
- **Starting Doom**: 25 (from configs/default.json)
- **Maximum Doom**: 100 (game over trigger)
- **Effective Range**: 75 points until game over

### Primary Doom Sources (Per Turn)

#### 1. Base Doom Increase: **5 points/turn**
Location: `src/core/turn_manager.py:260`
```python
doom_rise = 5  # Base doom increase
```

#### 2. Opponent Doom Contributions: **~2-6 points/turn**
Location: `src/core/opponents.py:222-237`
- **Undiscovered opponents**: 0-2 points each (random)
- **Discovered opponents**: `capabilities_researchers * 0.2 * progress_multiplier * debt_multiplier`
- **3 opponents total** -> typical 2-6 points combined
- **Scales with opponent progress and technical debt**

#### 3. Capabilities Research: **3 points per researcher**
Location: `src/core/turn_manager.py:272-276`
```python
capabilities_doom = capabilities_researchers * 3.0
```

### Doom Reduction Sources

#### 1. Safety Research: **2.5 points per researcher**
Location: `src/core/turn_manager.py:265-268`
```python
doom_reduction = gs.research_staff * 2.5
```

#### 2. Research Actions: **Variable (typically 3-8 points)**
Location: `src/core/actions.py:215`
- Depends on action effectiveness and research quality

## Current Balance Analysis

### Turn-by-Turn Doom Progression (No Staff)
- **Turn 0**: 25 doom
- **Turn 1**: 25 + 5 (base) + ~3 (opponents) = **~33 doom** (+8)
- **Turn 2**: 33 + 8 = **~41 doom** (+8)
- **Turn 3**: 41 + 8 = **~49 doom** (+8)
- **Turn 4**: 49 + 8 + event_spike = **~64 doom** (+15 with event)
- **Turn 5**: 64 + 8 + scaling = **~76 doom** (+12)
- **Turn 6**: 76 + 8 + scaling = **~89 doom** (+13)
- **Turn 7**: 89 + 8 + scaling = **~100 doom** (+11) -> **GAME OVER**

### Key Issues
1. **Too Fast**: Game ends around turn 7-8 consistently
2. **High Base Rate**: 5 doom/turn base is aggressive for 75-point range
3. **Opponent Scaling**: Opponents get more dangerous over time
4. **Staff Barrier**: Need staff to counter doom but can't hire immediately

## Recommended Tuning Parameters

### Option 1: Conservative Adjustment (Extend to ~12-15 turns)
```python
# In turn_manager.py:
doom_rise = 3  # Reduced from 5 -> slower base progression

# In opponents.py:
base_doom = self.capabilities_researchers * 0.15  # Reduced from 0.2

# In turn_manager.py:
doom_reduction = gs.research_staff * 3.0  # Increased from 2.5 -> better payoff
```

### Option 2: Moderate Adjustment (Extend to ~10-12 turns)
```python
# In turn_manager.py:
doom_rise = 4  # Reduced from 5

# Keep opponent mechanics same
# Increase safety research effectiveness:
doom_reduction = gs.research_staff * 3.5  # Increased from 2.5
```

### Option 3: Aggressive Adjustment (Extend to ~15-20 turns)
```python
# In turn_manager.py:
doom_rise = 2  # Major reduction from 5

# In opponents.py:
base_doom = self.capabilities_researchers * 0.1  # Major reduction from 0.2

# Boost safety research significantly:
doom_reduction = gs.research_staff * 4.0  # Increased from 2.5
```

## Impact Analysis

### Current (7-8 turns):
- **Base**: 5 x 7 = 35 doom
- **Opponents**: ~3 x 7 = 21 doom  
- **Events**: ~15 doom
- **Total**: ~71 doom + 25 starting = **96 doom** at turn 7

### Option 1 (12-15 turns):
- **Base**: 3 x 12 = 36 doom
- **Opponents**: ~2.5 x 12 = 30 doom
- **Events**: ~20 doom
- **Safety Research**: -3 x 6 turns x average 2 staff = -36 doom
- **Net**: 50 doom + 25 starting = **75 doom** at turn 12

### Option 2 (10-12 turns):
- **Base**: 4 x 10 = 40 doom
- **Opponents**: ~3 x 10 = 30 doom  
- **Events**: ~18 doom
- **Safety Research**: -3.5 x 5 turns x average 2 staff = -35 doom
- **Net**: 53 doom + 25 starting = **78 doom** at turn 10

## Implementation Priority

### High Priority (Immediate Hotfix)
1. **Reduce base doom rise** from 5 to 3-4 points/turn
2. **Increase safety research effectiveness** from 2.5 to 3.0-3.5

### Medium Priority  
1. **Tune opponent doom contributions** (reduce by 20-25%)
2. **Add early game doom protection** (slower ramp in first 3 turns)

### Low Priority (Future Enhancement)
1. **Configurable doom rates** in economic config
2. **Difficulty-based scaling** 
3. **Dynamic doom based on player performance**

## Recommended Implementation

Start with **Option 2** for immediate hotfix:
- Balances challenge with playability
- Extends game to reasonable 10-12 turns
- Maintains tension without frustration
- Easy to implement and test

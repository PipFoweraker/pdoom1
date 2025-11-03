# Monolith Refactoring Strategy v3.0: Incremental & Safe

## Executive Summary

Based on lessons learned from the previous refactoring attempt, this strategy focuses on **incremental, validated refactoring** with **continuous testing** to avoid the critical issues encountered in the previous branch.

## Problems with Previous Approach

The `refactor/monolith-breakdown` branch had:
- **69 ASCII compliance failures** (Unicode characters introduced)
- **Syntax errors** from encoding issues
- **63 test failures** due to configuration balance changes  
- **Broken imports** and circular dependencies

## New Strategy: Incremental Wins

### Phase 1: Safe Extraction (Week 1)
**Target**: Extract 3-5 self-contained modules from `game_state.py` (6,239 lines)

#### Extraction Candidates (Minimal Risk)
1. **Constants & Enums** -> `src/core/game_constants.py` (~100 lines)
2. **Utility Functions** -> `src/core/game_utils.py` (~200 lines)  
3. **Validation Logic** -> `src/core/validators.py` (~300 lines)
4. **Display Helpers** -> `src/core/display_helpers.py` (~150 lines)
5. **Save/Load Logic** -> `src/core/persistence.py` (~400 lines)

**Success Metrics**: 
- Reduce `game_state.py` by 1,000+ lines (15-20%)
- **Zero test failures** after each extraction
- **Perfect ASCII compliance** maintained
- **All imports working** correctly

### Phase 2: Main Loop Reduction (Week 2)  
**Target**: Extract event handling from `main.py` (3,064 lines)

#### Extraction Candidates
1. **Input Processing** -> `src/core/input_handler.py` (~400 lines)
2. **Event Management** -> `src/core/event_manager.py` (~300 lines)
3. **Screen Management** -> `src/core/screen_manager.py` (~200 lines)

### Phase 3: UI Stabilization (Week 3)
**Target**: Stabilize existing UI extractions or create safer alternatives

## Implementation Protocol

### Micro-Step Validation
Each extraction follows this **mandatory sequence**:

1. **Create extraction branch**: `refactor/extract-{module-name}`
2. **Extract single module** (1-2 hours max)
3. **Run full test suite** (must pass 100%)
4. **Validate imports**: `python -c 'from src.core.game_state import GameState'`
5. **ASCII compliance check**: `python scripts/enforce_standards.py --check-all`
6. **Programmatic validation**: Basic game state operations  
7. **Commit & merge** if successful, **abandon** if issues

### Dead Code Removal First
Before extractions, remove dead code:
```bash
# Use autoflake for automated cleanup
python -m autoflake --remove-all-unused-imports --remove-unused-variables --check --recursive .
```

### Safe Extraction Pattern
```python
# 1. Create new module with clear interface
# src/core/game_constants.py
'''Game constants and enums extracted from game_state.py'''

# 2. Import in game_state.py 
from src.core.game_constants import *

# 3. Remove original code from game_state.py
# 4. Test immediately
```

## Risk Mitigation

### Rollback Strategy
- Each extraction is **one small branch**
- Failed extractions are **abandoned immediately**
- **Main branch stays stable** throughout process
- **No accumulating technical debt**

### Validation Requirements
- **Full test suite**: 507+ tests must pass
- **ASCII compliance**: No Unicode characters anywhere
- **Import validation**: All imports must work
- **Programmatic testing**: Basic GameState operations work
- **Performance**: No degradation in game startup time

### Success Criteria Per Phase
- **Phase 1**: 15-20% reduction in game_state.py (1,000+ lines)
- **Phase 2**: 20-30% reduction in main.py (600+ lines)  
- **Phase 3**: Stabilized UI system with no regressions

## Branch Management

### Branch Naming
```
refactor/extract-constants      # Single module extractions
refactor/extract-utils
refactor/extract-validators
refactor/extract-persistence
```

### Merge Policy
- **Individual branches** merge to main after validation
- **No long-lived refactoring branches**
- **Fast iteration cycle**: 1-2 hours per extraction

## Tools & Automation

### Validation Script
Create `scripts/validate_refactoring.py`:
```python
def validate_extraction():
    # 1. Run test suite
    # 2. Check ASCII compliance  
    # 3. Validate imports
    # 4. Basic game state test
    # 5. Generate extraction report
```

### Dev Blog Integration
Document each successful extraction:
```bash
python dev-blog/create_entry.py development-session extract-{module-name}
```

## Expected Timeline

### Week 1: Foundation Extractions
- Day 1-2: Constants, utils, validators
- Day 3-4: Display helpers, persistence
- Day 5: Documentation and consolidation

### Week 2: Main Loop Refactoring  
- Day 1-2: Input and event handling
- Day 3-4: Screen management
- Day 5: Integration and testing

### Week 3: Stabilization
- Day 1-3: Address any issues
- Day 4-5: Documentation and final validation

## Success Metrics

### Quantitative Goals
- **game_state.py**: 6,239 -> ~5,000 lines (20% reduction)
- **main.py**: 3,064 -> ~2,400 lines (20% reduction)
- **Total refactored**: ~1,500 lines moved to modular structure
- **Test coverage**: Maintained at 507+ tests
- **Performance**: No degradation in startup time

### Qualitative Goals
- **Improved maintainability**: Clearer module boundaries
- **Enhanced testability**: Smaller, focused modules
- **Better documentation**: Each module has clear purpose
- **Easier onboarding**: New developers can understand structure

## Fallback Plan

If any extraction causes issues:
1. **Abandon the branch immediately**
2. **Document what went wrong**
3. **Skip that extraction** for now
4. **Continue with next target**
5. **Return to difficult extractions later** with better understanding

---

This strategy prioritizes **safety and incremental progress** over aggressive refactoring, ensuring we make steady progress without breaking the codebase.

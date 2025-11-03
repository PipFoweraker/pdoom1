# Refactoring Priority List
# P(Doom) Monolith Breakdown Preparation

## Overview

This document prioritizes refactoring targets identified in the dead code analysis to support the upcoming monolith breakdown. Items are ordered by impact on refactoring difficulty and system reliability.

## P0 - Critical Priority (Must Complete Before Monolith Breakdown)

### 1. Deterministic RNG Migration
**Issue**: Non-deterministic randomness breaks competitive gameplay
**Scope**: 50+ instances across 20+ files
**Impact**: High - Affects core gameplay mechanics
**Complexity**: Medium - Well-defined replacement pattern
**Estimated Effort**: 6-9 hours across 2-3 sessions

**Key Files to Address**:
- `src/core/actions.py` - 15+ instances of `random.randint()`
- `src/core/opponents.py` - 20+ instances of `random.randint()`  
- `src/core/game_state.py` - Event handling randomness
- `src/core/researchers.py` - Character generation randomness
- All test files using `import random`

**Implementation Pattern**:
```python
# Replace this:
import random
amount = random.randint(40, 70)

# With this:
from src.services.deterministic_rng import get_rng
amount = get_rng().randint(40, 70, f'fundraise_turn_{gs.turn}')
```

### 2. Root-Level Workspace Cleanup
**Issue**: Debug utilities clutter workspace and create confusion
**Scope**: 6 root-level Python files
**Impact**: Medium - Improves developer experience
**Complexity**: Low - Simple file moves/deletions
**Estimated Effort**: 1-2 hours

**Actions**:
- Delete `debug_typography.py` (development debug script)
- Delete `test_minimal.py` (stub test file)
- Delete `ui_interaction_fixes.py` (debug module)
- Move `demo_technical_failures.py` to `tools/demos/`
- Move `party_demo.py` to `tools/demos/`
- Move `demo_settings.py` to `tools/demos/`

## P1 - High Priority (Complete Within 2 Weeks)

### 3. Documentation Import Path Updates
**Issue**: Documentation shows incorrect import paths
**Scope**: 5+ documentation files
**Impact**: Medium - Prevents developer confusion
**Complexity**: Low - Find/replace operations
**Estimated Effort**: 2-3 hours

**Files to Update**:
- `.github/copilot-instructions.md` - Update `from game_state import` references
- `docs/DEVELOPERGUIDE.md` - Update import examples
- `docs/RELEASE_CHECKLIST.md` - Update validation commands

### 4. Demo Script Organization
**Issue**: Demo scripts scattered, unclear maintenance status
**Scope**: 3-4 demo files
**Impact**: Medium - Improves project organization
**Complexity**: Low - Directory restructuring
**Estimated Effort**: 1-2 hours

**Actions**:
- Create `tools/demos/` directory structure
- Move all demo scripts with updated imports
- Create `tools/demos/README.md` with usage instructions
- Update any references in documentation

## P2 - Medium Priority (Complete Within 1 Month)

### 5. Magic Number Configuration Migration
**Issue**: Hardcoded balance values complicate monolith breakdown
**Scope**: Economic constants, UI positioning, event probabilities
**Impact**: Medium - Improves configurability
**Complexity**: Medium - Requires configuration system integration
**Estimated Effort**: 4-6 hours

**Target Areas**:
- Action cost/benefit ranges in `src/core/actions.py`
- Event probability thresholds in `src/core/events.py`
- UI positioning constants in remaining files
- Opponent balance parameters in `src/core/opponents.py`

### 6. Import Pattern Standardization
**Issue**: Inconsistent RNG import patterns across codebase
**Scope**: All files using randomness
**Impact**: Medium - Improves code consistency
**Complexity**: Medium - Requires systematic review
**Estimated Effort**: 3-4 hours

**Pattern to Establish**:
```python
# Standard pattern for all random operations
from src.services.deterministic_rng import get_rng

def some_function(gs):
    # Always include context for reproducibility
    rng = get_rng()  
    value = rng.randint(1, 10, f'function_name_turn_{gs.turn}')
```

## P3 - Low Priority (Complete as Time Permits)

### 7. Global State Dependency Injection
**Issue**: Global `deterministic_rng` variable could be improved
**Scope**: RNG initialization and access patterns
**Impact**: Low - Architectural improvement
**Complexity**: High - Requires significant refactoring
**Estimated Effort**: 6-8 hours

**Approach**: Consider passing RNG instance through GameState or using dependency injection pattern

### 8. Legacy Code Pattern Cleanup
**Issue**: Remnants of early monolithic architecture
**Scope**: Various files with outdated patterns
**Impact**: Low - Code quality improvement
**Complexity**: Variable - Case-by-case analysis
**Estimated Effort**: 4-6 hours

## Implementation Roadmap

### Week 1-2: Critical Priority (P0)
- [ ] Deterministic RNG migration (3 sessions)
- [ ] Root-level workspace cleanup (1 session)

### Week 3-4: High Priority (P1)  
- [ ] Documentation import updates (1 session)
- [ ] Demo script organization (1 session)

### Month 2: Medium Priority (P2)
- [ ] Magic number configuration (2 sessions)
- [ ] Import pattern standardization (1 session)

### Future Sprints: Low Priority (P3)
- [ ] Global state refactoring (when needed)
- [ ] Legacy pattern cleanup (continuous improvement)

## Success Metrics

1. **Deterministic Gameplay**: Same seed produces identical results across all systems
2. **Clean Workspace**: No debug/utility files in root directory
3. **Accurate Documentation**: All code examples work as written
4. **Test Coverage**: All refactored code maintains or improves test coverage
5. **Performance**: No regression in game performance
6. **Monolith Readiness**: Codebase ready for architectural breakdown

## Risk Mitigation

1. **Backup Strategy**: Work in feature branches with comprehensive testing
2. **Incremental Approach**: Complete one priority level before moving to next
3. **Regression Testing**: Run full test suite after each change
4. **Performance Monitoring**: Benchmark critical paths during RNG migration
5. **Documentation Validation**: Test all updated examples

This priority list ensures the codebase is optimally prepared for the monolith breakdown while maintaining system stability and competitive gameplay integrity.

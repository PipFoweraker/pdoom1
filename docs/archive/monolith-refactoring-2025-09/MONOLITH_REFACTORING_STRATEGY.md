# Monolith Refactoring Strategy v2.0

## Executive Summary

P(Doom) has successfully completed **Phase 1: UI Monolith Breakdown**, achieving a 47% reduction in ui.py size (4,982 -> 2,664 lines). This document outlines the next phases of systematic monolith reduction to improve maintainability, testability, and modularity.

## Current Monolith Status

### OK Phase 1 Complete: UI Breakdown
- **ui.py**: 4,982 -> 2,664 lines (47% reduction)  
- **Extracted modules**: `src/ui/` system with 20+ specialized modules
- **Status**: Ready for merge validation and Phase 2 initiation

### TARGET Remaining Monoliths (Priority Order)

1. **game_state.py**: 5,880 lines (current target - 6% initial reduction)
2. **main.py**: 2,749 lines (10% initial reduction) 
3. **actions.py**: 652 lines (medium priority)
4. **technical_failures.py**: 610 lines (good patterns established)

## Refactoring Attack Strategy

### Branch Naming Convention
```
refactor/monolith-{TARGET}-phase{N}
? refactor/monolith-game-state-phase1
? refactor/monolith-main-phase1  
? refactor/monolith-actions-phase1
```

### Success Metrics Per Phase
- **Quick Win**: 20-40% size reduction in evening session
- **Structural Win**: Extract 3-5 cohesive modules
- **Quality Win**: Improve testability and reduce dependencies
- **Integration Win**: Maintain all functionality and test coverage

### Phase Completion Criteria
1. OK All tests pass (507+ tests, 38s runtime)
2. OK Size reduction achieved (minimum 20%)
3. OK Modules follow established patterns (`src/features/`, `src/core/`, `src/ui/`)
4. OK Documentation updated (CHANGELOG.md, dev blog entry)
5. OK Programmatic validation successful

## Phase 2: Game State Monolith (5,880 lines)

### Target Extractions
- **State Management**: Core state manipulation, persistence
- **Turn Processing**: End turn logic, event processing
- **Resource Management**: Money, staff, reputation, doom calculations
- **Action Processing**: Action validation, execution, cost calculation
- **Milestone System**: Progress tracking, unlock logic

### Extraction Targets
```
src/core/
? game_state.py (core state only, ~2,000 lines target)
? turn_processor.py (turn logic extraction)
? resource_manager.py (resource calculations)
? action_processor.py (action validation/execution)
? milestone_system.py (progress tracking)
```

### Quick Win Opportunities
- Extract repetitive getter/setter patterns
- Move calculation methods to dedicated modules
- Separate concerns: state vs logic vs validation
- Remove dead code and deprecated methods

## Phase 3: Main Loop Monolith (2,749 lines)

### Target Extractions
- **Event Loop**: pygame event handling
- **Input Manager**: Keyboard/mouse input processing  
- **Game Flow**: State transitions, screen management
- **Rendering Coordination**: Display updates, frame timing

### Extraction Targets
```
src/core/
? main.py (core loop only, ~1,000 lines target)
? event_processor.py (pygame event handling)
? input_manager.py (input processing) 
? game_flow_manager.py (state transitions)
? render_coordinator.py (display management)
```

## Implementation Workflow

### Evening Session Protocol
1. **Create Phase Branch** (5 minutes)
   ```bash
   git checkout -b refactor/monolith-{target}-phase1
   ```

2. **Quick Analysis** (10 minutes)
   - Identify extraction targets
   - Plan module boundaries
   - Set session goals

3. **Aggressive Refactoring** (90 minutes)
   - Extract cohesive functionality
   - Create new modules following patterns
   - Update imports systematically
   - Remove dead code aggressively

4. **Validation Sprint** (30 minutes)
   - Run full test suite (38s)
   - Programmatic validation
   - Quick manual verification

5. **Documentation & Merge** (15 minutes)
   - Update CHANGELOG.md
   - Create dev blog entry
   - Merge to main if successful
   - Create GitHub issue for follow-up

### Success Patterns from Phase 1
- **Follow established patterns**: Copy from `src/features/economic_cycles.py`
- **Maintain integration points**: Clear interfaces between modules
- **Extract complete functions**: Don't leave partial extractions
- **Test early, test often**: Validate after each extraction
- **Document as you go**: Update imports and dependencies

## Technical Debt Management

### Acceptable Technical Debt
- Temporary coupling during extraction
- Import path adjustments
- Interface refinement needs

### Unacceptable Technical Debt
- Broken functionality
- Test failures
- Performance degradation
- Circular dependencies

## Risk Mitigation

### Rollback Strategy
- Each phase branch can be abandoned if unsuccessful
- Main branch remains stable throughout
- Feature branches allow parallel experimentation

### Validation Requirements
- All 507+ tests must pass
- Programmatic controller validation
- No performance regression
- Save game compatibility maintained

## Success Metrics

### Overall Goal: 50% Monolith Reduction
- **game_state.py**: 5,880 -> ~3,000 lines (50% reduction)
- **main.py**: 2,749 -> ~1,500 lines (45% reduction)
- **Total impact**: ~4,500 lines reorganized into modular structure

### Quality Improvements
- Increased test coverage granularity
- Improved separation of concerns
- Enhanced maintainability
- Better onboarding for new developers

## Next Steps

1. **Validate Phase 1**: Merge UI breakdown if ready
2. **Initiate Phase 2**: Create game_state refactoring branch
3. **Execute Evening Attack**: 2-hour focused refactoring session
4. **Validate & Iterate**: Merge successful changes, plan Phase 3

---

*This strategy builds on the successful UI monolith breakdown patterns and aims for systematic, sustainable code improvement through focused evening sessions.*

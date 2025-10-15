# Next-Day Action Plan: P(Doom) Stabilization Phase
## September 28, 2025 - Systematic Test Suite Recovery

### Strategic Overview
Following our 20% modular milestone achievement, we now face significant test suite regressions (79 failures, 91.5% pass rate) that require systematic repair. This session will focus on critical system restoration to achieve 95%+ test pass rate and restore core game functionality.

---

## Pre-Session Checklist (5 minutes)

### Environment Validation
- [ ] Activate virtual environment: `source .venv/Scripts/activate` 
- [ ] Verify Python dependencies: `pip list | grep pygame`
- [ ] Confirm current directory: `pwd` (should be in pdoom1 root)
- [ ] Check git status: `git status` (confirm clean working directory)

### Baseline Assessment  
- [ ] Run test suite: `python -m unittest discover tests -v` (expect ~79 failures, 28-30 second runtime)
- [ ] Check GitHub issues: `gh issue list --state open --label bug --limit 5`
- [ ] Verify ecosystem status: `gh workflow list` (confirm GitHub Actions functioning)
- [ ] Document starting failure count for progress tracking

---

## Session Hour 1: Critical System Repairs (60 minutes)
**Focus**: Action Point System and Turn Progression - Highest Impact Fixes

### Task 1.1: Action Point System Repair (20 minutes)
**Problem**: Staff scaling calculations broken, max AP not recalculating

```bash
# Investigation commands:
python -c '
from src.core.game_state import GameState
gs = GameState('test')
print('Initial AP:', gs.action_points, 'Max AP:', gs.max_action_points)
gs.staff = 7
gs.end_turn()
print('After turn with 7 staff - AP:', gs.action_points, 'Max AP:', gs.max_action_points)
'
```

**Target Files**: 
- `src/core/game_state.py` - `end_turn()` method and AP calculation
- `tests/test_action_points.py` - Examine failing test expectations

**Success Criteria**:
- [ ] `test_ap_recalculation_on_turn_end` passes
- [ ] Max AP properly recalculated based on staff count in `end_turn()`
- [ ] AP system maintains consistency across turn transitions

### Task 1.2: Turn Progression System Repair (20 minutes)  
**Problem**: Event log not clearing, message persistence across turns

```bash
# Investigation commands:
python -c '
from src.core.game_state import GameState
gs = GameState('test')
gs.messages.append('Test message')
print('Before turn end:', gs.messages)
gs.end_turn()
print('After turn end:', gs.messages)
'
```

**Target Files**:
- `src/core/game_state.py` - Message clearing logic in `end_turn()`
- `tests/test_game_state.py` - Event log behavior tests

**Success Criteria**:
- [ ] `test_event_log_clears_on_end_turn` passes
- [ ] Messages properly cleared between turns (when scrollable log disabled)
- [ ] Turn isolation maintained across game progression

### Task 1.3: Specialized Staff Hiring Fix (20 minutes)
**Problem**: Staff hiring costs showing as 0, dialog system integration broken

**Target Files**:
- `src/core/game_state.py` - Staff hiring cost calculation
- UI dialog integration for staff hiring

**Success Criteria**:
- [ ] `test_specialized_staff_hiring_via_dialog` passes  
- [ ] Staff hiring costs properly calculated and displayed
- [ ] Dialog system integration functional

---

## Session Hour 2: Game State Management (60 minutes)
**Focus**: Action Selection and Victory Conditions

### Task 2.1: Action Instance Management Repair (25 minutes)
**Problem**: Selected actions not clearing, instance tracking broken

```bash
# Investigation commands:
python -c '
from src.core.game_state import GameState
gs = GameState('test')
gs.select_action('Grow Community')
print('Selected actions:', len(gs.selected_gameplay_actions))
gs.end_turn()
print('After turn end:', len(gs.selected_gameplay_actions))
'
```

**Target Files**:
- `src/core/game_state.py` - Action selection and clearing logic
- `src/features/unified_action_handler.py` - Action instance management

**Success Criteria**:
- [ ] `test_action_instances_cleared_on_turn_end` passes
- [ ] Selected actions properly cleared at turn end
- [ ] Action instance tracking maintains UI consistency

### Task 2.2: Victory/Defeat Detection Repair (25 minutes)
**Problem**: Game over conditions not triggering properly

**Target Files**:
- `src/core/game_state.py` - Game over detection logic
- Victory condition checking in turn processing

**Success Criteria**:
- [ ] `test_opponent_victory_condition` passes
- [ ] Game over state properly triggered when opponents reach 100%
- [ ] End game transitions function correctly

### Task 2.3: Undo Functionality Restoration (10 minutes)
**Problem**: Action undo system not working properly

**Success Criteria**:
- [ ] `test_undoing_last_ap` and related undo tests pass
- [ ] Undo removes most recent action instance correctly
- [ ] AP restored properly when undoing actions

---

## Session Hour 3: System Integration Repairs (60 minutes)
**Focus**: Media/PR and Research System UI Integration

### Task 3.1: Media & PR System Integration (30 minutes)
**Problem**: Media actions not appearing in UI, operations not executing

```bash
# Investigation commands:
python -c '
from src.core.game_state import GameState
gs = GameState('test')
actions = gs.get_available_actions()
media_actions = [a for a in actions if 'Press Release' in a or 'Media' in a]
print('Available media actions:', media_actions)
'
```

**Target Files**:
- `src/core/game_state.py` - Media action availability
- `src/core/media_pr_system_manager.py` - Integration verification
- UI action list generation

**Success Criteria**:
- [ ] `test_media_actions_available` passes
- [ ] Press Release and other media actions appear in available actions
- [ ] Media operations execute properly when selected

### Task 3.2: Research Quality System Repair (30 minutes) 
**Problem**: Research actions missing from interface, debt consequences not triggering

**Target Files**:
- `src/core/game_state.py` - Research action integration  
- `src/core/research_system_manager.py` - Action availability logic
- Research quality setting functionality

**Success Criteria**:
- [ ] `test_research_actions_exist` passes
- [ ] Research quality actions available in UI
- [ ] Debt consequence system functioning properly

---

## Session Hour 4: Infrastructure and Compliance (60 minutes)
**Focus**: ASCII Compliance and Infrastructure Systems

### Task 4.1: ASCII Compliance Mass Repair (30 minutes)
**Problem**: 17 documentation files with Unicode characters

```bash
# Automated fix commands:
python scripts/ascii_compliance_fixer.py
python scripts/enforce_standards.py --check-all --fix
```

**Target Files**: All documentation with Unicode violations:
- `CHANGELOG.md` 
- `SESSION_COMPLETION_*.md`
- `docs/technical/*.md`

**Success Criteria**:
- [ ] All `test_documentation_files_ascii_only` tests pass
- [ ] Zero Unicode characters in documentation
- [ ] Cross-platform compatibility maintained

### Task 4.2: Infrastructure System Repairs (30 minutes)
**Problem**: Sound system, logging, UI navigation broken

#### Sound System:
- [ ] Fix Zabinga trigger integration
- [ ] `test_zabinga_sound_on_paper_completion` passes

#### Logging System:  
- [ ] Repair turn end logging functionality
- [ ] `test_turn_end_logging` passes  

#### UI Navigation:
- [ ] Fix end game menu state transitions
- [ ] Menu item order and functionality restored

---

## Session Hour 5: Validation and Documentation (60 minutes)
**Focus**: Integration Testing and Progress Documentation

### Task 5.1: Comprehensive Validation (30 minutes)

#### Test Suite Validation:
```bash
# Full test run with timing:
time python -m unittest discover tests -v

# Expected improvements:
# - Starting: ~79 failures (91.5% pass rate)  
# - Target: <45 failures (95%+ pass rate)
# - Critical systems: Action points, turn progression, media/research integration working
```

#### Game Functionality Validation:
```bash
# Programmatic functionality test:
python -c '
from src.core.game_state import GameState
print('=== P(Doom) v0.8.0+ Functionality Test ===')

# Basic game state
gs = GameState('validation-test')
print(f'v Game initializes: Turn {gs.turn}, AP {gs.action_points}/{gs.max_action_points}')

# Action selection and execution
actions = gs.get_available_actions()
print(f'v Available actions: {len(actions)} actions found')
print(f'v Sample actions: {actions[:3]}')

# Turn progression  
initial_turn = gs.turn
gs.select_action('Grow Community')
gs.end_turn()
print(f'v Turn progression: {initial_turn} -> {gs.turn}')
print(f'v Action clearing: {len(gs.selected_gameplay_actions)} selected actions remaining')

# System integration
media_available = any('Media' in action for action in actions)
research_available = any('Research' in action for action in actions) 
print(f'v Media system integration: {media_available}')
print(f'v Research system integration: {research_available}')

print('=== Validation Complete ===')
'
```

### Task 5.2: Progress Documentation (30 minutes)

#### Update Project Documentation:
```bash
# Update CHANGELOG.md with stabilization achievements
# Document systematic repair methodology  
# Create regression prevention guide
```

#### Create Session Summary:
- [ ] Document test failure reduction (79 -> target <45)
- [ ] List critical systems restored to functionality
- [ ] Identify remaining high-priority issues for next session
- [ ] Update dev blog with stabilization phase progress

#### Quality Metrics Documentation:
- [ ] Test pass rate improvement percentage
- [ ] Critical system functionality restoration status
- [ ] ASCII compliance resolution count
- [ ] Performance impact assessment

---

## Success Metrics and Exit Criteria

### Quantitative Targets:
- **Test Pass Rate**: 91.5% -> 95%+ (785/864 -> 820+/864 passing tests)
- **Critical System Failures**: 0 action point, turn progression, or game state failures
- **ASCII Compliance**: 0 Unicode violations in documentation  
- **Infrastructure Failures**: <5 remaining sound/logging/UI failures

### Functional Requirements:
- [ ] Action point system calculates and scales properly
- [ ] Turn progression clears messages and maintains isolation  
- [ ] Game over conditions trigger correctly
- [ ] Media and Research actions available and functional
- [ ] Staff hiring costs display correctly
- [ ] Action undo system operational

### Quality Assurance:
- [ ] No regressions introduced during repair work
- [ ] Core gameplay loop functions end-to-end
- [ ] Modular architecture remains intact
- [ ] Performance maintained within acceptable bounds

---

## Contingency Planning

### If Behind Schedule:
**Priority Order**: 
1. Action point system (highest impact)
2. Turn progression (core functionality)  
3. ASCII compliance (automated fix)
4. Media/Research integration (user-visible)
5. Infrastructure systems (lower priority)

### If Unexpected Issues:
- **Module Integration Problems**: Focus on delegation pattern validation
- **Performance Regressions**: Profile and optimize critical path functions
- **Test Environment Issues**: Validate virtual environment and dependencies

### Session Extension Options:
- **+30 minutes**: Complete infrastructure system repairs
- **+60 minutes**: Address additional system integration issues
- **+90 minutes**: Begin next session's high-priority GitHub issues

---

## Next Session Preparation

### Session Handoff Items:
- [ ] Final test failure count and categorization
- [ ] List of remaining high-priority issues
- [ ] Performance impact assessment from repairs
- [ ] Ecosystem integration validation status

### Follow-up Priorities (Next Session):
1. **Remaining Test Failures**: Address <45 remaining failures systematically
2. **GitHub Issue Backlog**: Begin UI/UX improvement issues (#370, #369, #368)
3. **Ecosystem Validation**: Verify cross-repository integration still functional
4. **Performance Optimization**: Address any performance regressions from repairs

This action plan provides structured approach to systematic test suite recovery while maintaining focus on critical game functionality and long-term project health.
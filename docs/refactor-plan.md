# P(Doom) Refactor Plan: Alpha Stabilisation

## Overview

This document outlines the systematic refactoring approach for P(Doom) during alpha stabilisation phase. The goal is to improve code organisation, maintainability, and prepare for beta release while maintaining backward compatibility.

## Principles

- **UK Spelling**: Use UK spelling throughout (organisation, behaviour, modularisation, initialise)
- **Conservative defaults**: Maintain existing behavior during transitions
- **Small, reviewable PRs**: Each change should be easily reviewable and reversible
- **Test discipline**: No regression in coverage; add tests as systems are extracted
- **Runtime compatibility**: Support legacy data paths during transition

## Current Structure Analysis

```
pdoom1/
├── main.py (2482 lines - MONOLITH)
├── ui.py (large UI functions)
├── src/
│   ├── core/game_state.py (3000+ lines - MONOLITH)
│   ├── services/ (config, sound, bug reporting)
│   ├── features/ (onboarding)
│   └── ui/ (overlay_manager, keybinding)
├── assets/
├── configs/
└── runtime files (logs, leaderboards, etc.)
```

## Target Structure

```
pdoom1/
├── __main__.py (entry point)
├── main.py (simplified game loop)
├── core/
│   ├── game_state/ (modular game state)
│   ├── engine/ (game loop, timing)
│   └── types/ (dataclasses for actions, events)
├── ui/
│   ├── components/ (reusable UI elements)
│   ├── screens/ (main menu, HUD, overlays)
│   └── facade.py (stable UI interface)
├── services/ (existing + improvements)
├── features/ (game features)
├── assets/ (game assets)
└── data/ (runtime data directory)
```

## Refactoring Phases

### Phase 1: Foundation (PRs 1-3)
- [x] **PR 1**: Documentation and process setup
- [ ] **PR 2**: Update .gitignore, establish coverage baseline
- [ ] **PR 3**: Runtime data directory with migration support

### Phase 2: UI Extraction (PRs 4-5)
- [ ] **PR 4**: Extract overlay_manager to pdoom1/ui, add ui/components/
- [ ] **PR 5**: Create ui/screens/ structure with facade

### Phase 3: Core Refactoring (PRs 6-7)
- [ ] **PR 6**: Extract economy + staff subsystems from GameState
- [ ] **PR 7**: Extract events + upgrades + persistence subsystems

### Phase 4: Type Safety (PRs 8-9)
- [ ] **PR 8**: Introduce dataclasses for Action, Upgrade, Event
- [ ] **PR 9**: Consolidate logging, remove unused error_tracker

### Phase 5: Cleanup (PRs 10-11)
- [ ] **PR 10**: Remove dead code, relocate examples/assets
- [ ] **PR 11**: Add package entry point, update imports to absolute

## Implementation Guidelines

### Facades and Adapters
During extraction, maintain compatibility through facades:
```python
# Old interface remains working
game_state = GameState()

# New modular structure underneath
game_state._economy = EconomySubsystem()
game_state._staff = StaffSubsystem()
```

### UK Spelling Migration
Gradually update to UK spelling:
- `initialize` → `initialise`
- `organization` → `organisation`
- `behavior` → `behaviour`
- `color` → `colour`

### Runtime Data Migration
Support both old and new paths:
```python
# Check new path first, fall back to old
new_path = get_app_data_dir() / "leaderboards"
old_path = "leaderboards"
if new_path.exists():
    load_from(new_path)
elif old_path.exists():
    load_from(old_path)
    migrate_to(new_path)
```

## Testing Strategy

- **Smoke tests**: Manual verification after each PR
  - Audio system functionality
  - Fullscreen/windowed mode switching
  - Basic game loop operation
  - Events and popups
  - Save/load with legacy path support
- **Coverage maintenance**: No regression in test coverage
- **Legacy compatibility**: Ensure old saves/configs still work

## Success Criteria

- [ ] Modular structure with clear separation of concerns
- [ ] GameState split into coherent subsystems
- [ ] UI components extracted and reusable
- [ ] Runtime data stored in appropriate OS directories
- [ ] Legacy data paths supported with migration notices
- [ ] Logging system consolidated
- [ ] Dead code removed
- [ ] Package installable with `python -m pdoom1`
- [ ] Documentation updated to reflect new structure

## Risk Mitigation

- **Small incremental changes**: Each PR changes one system at a time
- **Backward compatibility**: Old interfaces remain functional during transition
- **Rollback capability**: Each change is easily reversible
- **Test coverage**: No functionality lost during refactoring

---

*This document will be updated as refactoring progresses*

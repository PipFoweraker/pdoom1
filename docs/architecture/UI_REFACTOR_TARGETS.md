# UI Architecture Refactoring Targets

## Current State Analysis

### The Problem
- **Root-level monolith**: `ui.py` (4,818 lines) - massive legacy file
- **Modular system**: `src/ui/` directory with ~20 well-structured modules
- **Dual imports**: `main.py` imports from both systems causing confusion
- **Function duplication**: Same functions exist in multiple places

### Import Analysis
`main.py` currently imports from the monolith:
```python
from ui import draw_seed_prompt, draw_main_menu, draw_bug_report_form, 
    draw_bug_report_success, draw_end_game_menu, draw_first_time_help, 
    draw_pre_game_settings, draw_seed_selection, draw_tutorial_choice, 
    draw_new_player_experience, draw_popup_events, draw_turn_transition_overlay, 
    draw_audio_menu, draw_high_score_screen, draw_ui
```

## Refactoring Strategy

### Phase 1: Easy Wins (Immediate)
1. **Eliminate Function Duplication**
   - `draw_main_menu` exists in 3 places: `ui.py`, `src/ui/menus.py`, `src/ui/menu_system.py`
   - Pick the best implementation, redirect others
   
2. **Utility Function Migration**
   - Move `wrap_text()`, `render_text()` -> `src/ui/text.py` (already exists!)
   - Move `draw_resource_icon()` -> `src/ui/drawing_utils.py`
   - Move overlay functions -> `src/ui/overlay_system.py`

3. **Common Component Extraction**
   - `draw_version_footer/header()` -> `src/ui/components.py`
   - `draw_loading_screen()` -> `src/ui/screens.py`
   - `draw_back_button()` -> `src/ui/ui_elements.py`

### Phase 2: Menu System Consolidation
1. **Standardize Menu Imports**
   - Replace `from ui import draw_main_menu` with `from src.ui.menus import draw_main_menu`
   - Update all menu-related imports to use modular system

2. **Remove Redundant Implementations**
   - Keep the most feature-complete version of each function
   - Add deprecation warnings to old implementations

### Phase 3: Dialog System Cleanup
1. **Researcher Pool Fix** [EMOJI] (Already addressed)
2. **Dialog System Unification**
   - `src/ui/dialogs.py` vs `src/ui/dialog_system.py` - consolidate
   - Standardize dialog creation patterns

### Phase 4: Monolith Decomposition
1. **Game UI Extraction**
   - Move `draw_ui()` (main game interface) -> `src/ui/game_ui.py` (already exists!)
   - Update import in `main.py`

2. **Screen Rendering Consolidation**
   - All `draw_*_menu()` functions -> appropriate `src/ui/` modules
   - All `draw_*_screen()` functions -> `src/ui/screens.py`

## Easy Win Implementation Plan

### Win #1: Text Utilities (5 minutes)
```python
# Already exists: src/ui/text.py
# Action: Move wrap_text, render_text from ui.py, update imports
```

### Win #2: Main Menu Import Switch (2 minutes)
```python
# In main.py, change:
from ui import draw_main_menu
# To:
from src.ui.menus import draw_main_menu
```

### Win #3: Drawing Utils Consolidation (3 minutes)
```python
# Move draw_resource_icon from ui.py to src/ui/drawing_utils.py
# Update any imports
```

### Win #4: Version Display Components (2 minutes)
```python
# Move draw_version_* functions to src/ui/components.py
```

## Migration Benefits
- **Reduced complexity**: Break 4,818-line monolith into focused modules
- **Better maintainability**: Each module has single responsibility
- **Easier testing**: Modular components can be tested independently
- **Clear architecture**: Import paths reflect functionality
- **Type safety**: Modular files have better type annotations

## Risk Mitigation
- **Incremental migration**: Change one function at a time
- **Import redirection**: Keep old imports working during transition
- **Comprehensive testing**: Run full test suite after each change
- **Rollback plan**: Git branches for easy reversion

## Success Metrics
- [ ] `ui.py` reduced to <2000 lines
- [ ] All `main.py` imports use `src.ui.*` paths
- [ ] No duplicate function definitions
- [ ] All tests passing
- [ ] Type annotation coverage >90%

## Implementation Priority
1. **Immediate** (< 30 minutes): Easy wins - utility functions, simple imports
2. **Short-term** (1-2 hours): Menu system consolidation
3. **Medium-term** (4-6 hours): Dialog system cleanup
4. **Long-term** (8-12 hours): Complete monolith decomposition

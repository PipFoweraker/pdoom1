# Complete UI Monolith Breakdown - Phase 1 (Remaining Dialog Functions)\n\n## Overview
Complete the systematic breakdown of the remaining ~55 functions in the 5,000+ line ui.py monolith. 

## Progress Summary
- **COMPLETED**: Successfully extracted ~4 major dialog functions to src/ui/dialogs.py (~600 lines)
- **COMPLETED**: Context utilities, rendering utilities, layout functions extracted
- **REMAINING**: ~55 functions across multiple categories

## Phase 1: Priority Extraction Targets

### Large Dialog Functions (HIGH PRIORITY)
- [ ] draw_stepwise_tutorial_overlay() -> src/ui/tutorials.py
- [ ] draw_first_time_help() -> src/ui/tutorials.py  
- [ ] draw_tutorial_overlay() -> src/ui/tutorials.py
- [ ] draw_bug_report_form() -> src/ui/forms.py
- [ ] draw_seed_prompt() -> src/ui/forms.py
- [ ] draw_seed_selection() -> src/ui/forms.py

### Game UI Functions (HIGH PRIORITY)
- [ ] draw_ui() (main game interface) -> src/ui/game_ui.py
- [ ] draw_top_bar_info() -> src/ui/game_ui.py
- [ ] draw_employee_blobs() -> src/ui/game_ui.py
- [ ] draw_opponents_panel() -> src/ui/game_ui.py

### Panel Functions (MEDIUM PRIORITY)
- [ ] draw_deferred_events_zone() -> src/ui/panels.py (extend existing)
- [ ] draw_popup_events() -> src/ui/panels.py (extend existing)

### Menu Functions (MEDIUM PRIORITY)
- [ ] draw_end_game_menu() -> src/ui/menus.py (extend existing)
- [ ] draw_pre_game_settings() -> src/ui/menus.py (extend existing)
- [ ] draw_audio_menu() -> src/ui/menus.py (extend existing)
- [ ] draw_high_score_screen() -> src/ui/menus.py (extend existing)

### Animation Functions (LOW PRIORITY)
- [ ] draw_ui_transitions() -> src/ui/animations.py
- [ ] draw_upgrade_transition() -> src/ui/animations.py
- [ ] draw_turn_transition_overlay() -> src/ui/animations.py

## Established Pattern
1. Extract functions from monolithic ui.py to appropriate modular files
2. Update imports in main.py and other consumers
3. Test functionality to ensure no regressions
4. Remove functions from monolithic file once migration complete

## Acceptance Criteria
- [ ] All dialog functions extracted to src/ui/dialogs.py, src/ui/tutorials.py, src/ui/forms.py
- [ ] All game UI functions extracted to src/ui/game_ui.py
- [ ] All panel functions consolidated in src/ui/panels.py
- [ ] All menu functions consolidated in src/ui/menus.py
- [ ] All animation functions extracted to src/ui/animations.py
- [ ] Full test suite passes (38-second runtime)
- [ ] No functionality regressions
- [ ] Import statements updated across codebase

## Strategic Impact
- **Maintainability**: Find and modify specific UI components easily
- **Testing**: Individual modules can be tested in isolation
- **Beta Readiness**: Clean modular architecture for stable-beta release

**Priority**: HIGH - Critical for stable-beta milestone
**Effort**: ~6-8 hours systematic work  
**Branch**: refactor/monolith-breakdown (already created)\n\n<!-- GitHub Issue #301 -->
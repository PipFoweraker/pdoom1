[ROCKET] P(Doom) UI Refactoring - Phase 3: Continue Modular Extraction

**IMMEDIATE STATUS**: Major menu system extraction SUCCESS! Ready for Phase 3.

**Current State**:
[EMOJI] 1,150+ lines extracted from ui.py (2,930 lines remaining, down from ~4,000+ original)
[EMOJI] Created src/ui/dialog_system.py (713 lines) + src/ui/bug_report.py (276 lines)
[EMOJI] Created src/ui/menu_system.py (394 lines) with 4 core menu functions
[EMOJI] Achieved 30% monolith reduction with clean modular architecture
[EMOJI] All imports working, no circular dependencies
[EMOJI] Branch: refactor/monolith-breakdown (commit 2f889ae)

**Phase 3 Mission - Continue UI Extraction**:
1. **TARGET (30+ min)**: Extract overlay and window system functions (~300-400 lines)
   - draw_overlay, draw_window_with_header functions
   - draw_loading_screen, draw_version_footer, draw_dev_mode_indicator
2. **TARGET (20+ min)**: Extract drawing utility functions (~200-300 lines) 
   - draw_resource_icon, draw_mute_button functions
   - Text rendering and wrapping utilities
3. **TARGET (40+ min)**: Extract game state rendering functions (~400-500 lines)
   - draw_ui, draw_employee_blobs, draw_top_bar_info functions

**Validation Commands**: 
```bash
# Test current state
python -c 'from src.ui.menu_system import draw_main_menu; from src.ui.dialog_system import draw_fundraising_dialog; print('v All systems ready!')'

# Check current line count  
wc -l ui.py
```

**Established Patterns**:
- Extract function groups into logical modules (e.g., src/ui/overlay_system.py)
- Remove functions from ui.py, replace with comment placeholders
- Add imports to ui.py for extracted functions
- Test imports work before proceeding
- Commit each major extraction separately

**Next Targets**: 
- Overlay system: draw_overlay, draw_window_with_header (~150-200 lines)
- Utility functions: draw_resource_icon, draw_loading_screen (~150-200 lines)  
- Game rendering: draw_ui, draw_employee_blobs (~300-400 lines)

**Architecture Goal**: Continue proven modular extraction to achieve 50%+ reduction from ui.py monolith.

[TARGET] **Goal**: Additional 600-800+ line reduction from ui.py using successful extraction patterns, targeting final size under 2,000 lines.

**Success Metrics**: Clean modular structure, no circular imports, all functionality preserved, significant line count reduction.

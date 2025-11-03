# Enhanced Context Prompt for P(Doom) Development

## LIST **Core Project Context**

**Project**: P(Doom) - AI Safety Strategy Game  
**Language**: Python 3.9+ with pygame  
**Architecture**: Modular (6 extracted modules, 558 lines from monolith)  
**Current Version**: v0.8.0 'Alpha Release - Modular Architecture'  
**Development Phase**: Alpha Testing Ready  
**Repository**: GitHub - PipFoweraker/pdoom1  

## TARGET **Current Development State**

### **Architecture Status**
- **Modular Achievement**: 558 lines extracted from 6,240-line monolith (11.6% reduction)
- **6 Focused Modules**: game_constants.py, ui_utils.py, verbose_logging.py, employee_management.py, dialog_systems.py, utility_functions.py
- **Remaining Monolith**: 5,682 lines in game_state.py (down from 6,240)
- **Type Safety**: Comprehensive annotations maintained throughout refactoring
- **Zero Regressions**: All functionality preserved through systematic extraction

### **Documentation Organization**
- **Structure**: 5 organized subdirectories in docs/ (process/, issues/, game-design/, technical/, project-management/)
- **Modern README**: v0.8.0 achievements, screenshots, alpha testing focus
- **Session Handoffs**: Timestamped format `SESSION_HANDOFF_YYYY-MM-DD_HHMM.md`
- **Template System**: `SESSION_HANDOFF_TEMPLATE.md` for consistency

### **Alpha Testing Features**
- **Dev Mode**: F10 toggle, Ctrl+D UI diagnostics, Ctrl+E emergency recovery
- **Screenshot System**: `[` key capture with automatic timestamping
- **Verbose Logging**: Configurable detail levels for troubleshooting
- **Debug Overlays**: Real-time performance and state information

## TOOL **Technical Validation Requirements**

### **Pre-Session Validation**
```bash
# Always run before starting development
cd 'c:\Users\gday\Documents\A Local Code\pdoom1'
git status  # Should be clean
python -c 'from src.core.game_state import GameState; GameState('test')'
```

### **Module Import Validation**
```python
# Test all extracted modules
from src.core.game_constants import DEFAULT_STARTING_RESOURCES
from src.core.ui_utils import validate_rect
from src.core.verbose_logging import create_verbose_money_message
from src.core.employee_management import create_employee_blob
from src.core.dialog_systems import DialogManager
from src.core.utility_functions import is_upgrade_available
print('All 6 modules importing successfully')
```

### **Test Suite Standards**
- **Runtime**: ~500+ tests, 90+ second execution time
- **Timeout**: Set 90+ seconds, NEVER CANCEL early
- **Acceptable Failures**: <5 failures normal (unrelated to core functionality)
- **Command**: `python -m unittest discover tests -v`

## GAME **Gameplay Context**

### **Core Systems**
- **Turn-Based**: Players select actions, advance turns, manage resources
- **Resources**: Money ($100k start), staff, reputation, doom, action points, compute
- **Events**: Random events each turn affecting game state
- **Opponents**: 3 AI labs with different strategies and hidden information
- **Milestones**: Unlock new mechanics as lab grows

### **Alpha Testing Focus**
- **Community Feedback**: GitHub Discussions for alpha testing
- **Bug Reports**: Screenshots, logs, structured issue templates
- **Performance**: Startup time, memory usage, responsiveness baselines
- **Cross-Platform**: Windows/macOS/Linux compatibility validation

## LIST **Session Continuity Protocol**

### **Development Phase Awareness**
**Current Phase**: Alpha Testing (v0.8.0)  
**Community Status**: Ready for alpha testing feedback collection  
**Next Priorities**: Quality assurance, performance validation, community engagement  
**Repository Status**: All changes committed and pushed to GitHub main branch  

### **Session Handoff Context**
**Check for**: `SESSION_HANDOFF_YYYY-MM-DD_HHMM.md` files for recent session context  
**Technical Validation**: Always run module import validation before development  
**Documentation Structure**: Reference organized docs/ subdirectories  
**Git Status**: Verify working tree clean before starting new work  

### **Quality Metrics Context**
**Test Suite**: ~500+ tests, 90+ second runtime, <5 failures acceptable  
**Performance Baseline**: Document startup time and memory usage for regression detection  
**Type Coverage**: Comprehensive annotations maintained throughout refactoring  
**Cross-Platform**: Validate on multiple OS when architectural changes made  

## LAUNCH **Success Metrics and Standards**

### **Code Quality Standards**
- **Type Annotations**: Maintain comprehensive typing (pygame.Surface, Optional[Dict], Tuple[bool, str])
- **Import Validation**: Test `from src.core.game_state import GameState` after changes
- **ASCII Compliance**: All commits, documentation, and code comments ASCII-only
- **Regression Prevention**: Full test suite validation after architectural changes

### **Community Engagement Standards**
- **Alpha Documentation**: Clear testing scenarios and feedback collection methods
- **Performance Tracking**: Baseline measurements for regression detection
- **Issue Templates**: Structured bug reports with logs and screenshots
- **Testing Checklists**: Specific validation scenarios for community testers

### **Development Workflow Standards**
- **Session Documentation**: Use timestamped handoff format for continuity
- **Technical Context**: Preserve architecture state and extraction progress
- **Quality Assurance**: Pre/post session validation with comprehensive testing
- **Strategic Planning**: Document next refactoring targets and improvement areas

---

**Context Updated**: September 20, 2025  
**Architecture State**: 6 modules extracted, 558 lines, zero regressions  
**Community Readiness**: Alpha testing features complete, documentation organized  
**Next Focus**: Quality assurance, performance validation, community engagement  

**TARGET The project is in excellent shape for systematic development and community collaboration!**
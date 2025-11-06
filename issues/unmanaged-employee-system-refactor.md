# Refactor Unmanaged Employee Productivity System

## Issue Summary
The current unmanaged employee productivity penalty system has poor user experience and architectural issues that need to be addressed.

## Current Problems

### 1. **Poor User Experience**
- ERROR Employees become unproductive immediately with no warning
- ERROR Red X visual indicators appear suddenly without explanation
- ERROR No clear mechanism for players to understand or fix the issue
- ERROR No progressive warning system before penalties kick in

### 2. **Architectural Issues**
- ERROR Logic scattered across multiple files (`game_state.py`, `ui.py`, `ui_new/layouts/three_column.py`)
- ERROR Complex productivity calculations mixed with visual rendering
- ERROR Inconsistent implementation between UI systems
- ERROR Hard to maintain and modify

### 3. **Current System Functions to Refactor**

#### Core Logic (src/core/game_state.py)
```python
# Functions that need architectural review:
_update_employee_productivity()          # Line ~1311 - Core productivity calculation
get_researcher_productivity_effects()    # Multiple calls - Researcher-specific logic
```

#### Employee Data Structure Issues
```python
# Current employee blob structure has UI-specific fields mixed with game logic:
{
    'productivity': 0.0,                 # Game logic
    'unproductive_reason': None,         # UI-specific field in game data
    'productive_action_bonus': 1.0,      # Game logic
    # ... other mixed concerns
}
```

#### Visual Rendering (ui.py, ui_new/layouts/three_column.py)
- Red slash rendering logic embedded in UI rendering functions
- Inconsistent visual feedback between old and new UI systems

## Proposed Solution Architecture

### 1. **Separate Concerns**
```
Game Logic Layer (src/core/):
? Employee productivity calculations
? Management capacity rules
? Penalty application

UI Feedback Layer (src/ui/):
? Warning system (tooltips, notifications)
? Progressive visual indicators
? Management action suggestions

Event System Layer (src/events/):
? Management capacity warnings
? Productivity decline notifications
? Tutorial integration for new players
```

### 2. **Improved User Experience Flow**

#### Phase 1: Early Warning (at 8 employees)
- ? Yellow tooltip warning: 'Consider hiring management staff'
- NOTE Event message: 'Your team is growing! Management will help maintain productivity.'

#### Phase 2: Approaching Limit (at 9 employees)
- ? Orange notification: 'Management capacity reached. New hires may be less productive.'
- IDEA Action suggestion: 'Hire Admin Staff or promote experienced employees'

#### Phase 3: Over Limit (10+ employees)
- ? Clear notification: 'Unmanaged employees are 50% less productive'
- TOOLS Specific remediation options presented
- CHART Clear productivity impact shown in tooltips

### 3. **Clean Architecture Implementation**

#### New Structure:
```python
# src/core/management/productivity_system.py
class ProductivitySystem:
    def calculate_employee_productivity(self, employee, management_context)
    def get_management_capacity(self, admin_staff, experienced_employees)
    def apply_productivity_penalties(self, employees, management_capacity)

# src/ui/management/management_feedback.py  
class ManagementFeedback:
    def show_management_warnings(self, current_staff, management_capacity)
    def render_productivity_indicators(self, employees)
    def suggest_management_actions(self, context)

# src/events/management_events.py
class ManagementEvents:
    def trigger_capacity_warning(self, staff_count)
    def show_productivity_tutorial(self, player_context)
```

## Implementation Plan

### Phase 1: Remove Confusing Visuals OK
- [x] Remove red X/slash indicators from employee blobs
- [x] Keep core productivity penalty mechanic functional
- [x] Preserve existing game balance

### Phase 2: Implement Warning System
- [ ] Add progressive warning tooltips at 8, 9, 10+ employees
- [ ] Create management capacity calculation service
- [ ] Add tutorial integration for new players

### Phase 3: Refactor Architecture  
- [ ] Extract productivity logic to dedicated system
- [ ] Separate UI feedback from game logic
- [ ] Implement consistent behavior across UI systems

### Phase 4: Enhanced Management Tools
- [ ] Add management dashboard/overlay
- [ ] Provide clear remediation actions
- [ ] Show productivity impact in real-time

## Success Criteria

### User Experience
- OK Players understand why productivity penalties occur
- OK Clear warning system before penalties apply
- OK Obvious paths to remedy management issues
- OK Progressive feedback rather than sudden changes

### Code Quality
- OK Clear separation between game logic and UI
- OK Consistent implementation across UI systems
- OK Easy to maintain and extend
- OK Well-tested productivity calculations

## Files Affected

### Core Changes
- `src/core/game_state.py` - Extract productivity logic
- `src/core/management/` - New management system (to be created)

### UI Changes  
- `ui.py` - Remove red cross rendering, add warning tooltips
- `ui_new/layouts/three_column.py` - Consistent with main UI
- `src/ui/management/` - New feedback system (to be created)

### Event Integration
- `src/events/` - Management-related events and tutorials

## Related Issues
- Addresses user confusion about sudden productivity drops
- Improves new player onboarding for management mechanics
- Establishes pattern for other complex game systems

## Priority
**High** - Affects core gameplay experience and player retention

---
*Created: September 11, 2025*  
*Status: Planning*  
*Labels: enhancement, architecture, user-experience, management-system*

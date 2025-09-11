# Progressive Action Button Discovery System Implementation

**Created**: September 11, 2025  
**Type**: Feature Enhancement  
**Priority**: High  
**Status**: Open  
**Branch**: stable-alpha  

## Background

Based on detailed analysis in `issues/smart-action-button-discovery.md`, the current action button system shows all buttons immediately without progression or mystery. This creates cognitive overload and lacks the engaging progression feeling of games like Starcraft 2.

## Coding Implementation from Issue Analysis

The issue provides a detailed technical specification that can be directly implemented:

### 1. Core Button State System
```python
# src/ui/components/action_button.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Callable

class ActionButtonState(Enum):
    UNDISCOVERED = "undiscovered"    # Prerequisites not met
    DISCOVERED = "discovered"        # Prerequisites met, may be cost-blocked  
    AVAILABLE = "available"          # Can be used immediately

@dataclass
class ActionButtonConfig:
    action_id: str
    title: str
    description: str
    cost: Dict[str, int]
    prerequisites: List[Callable[[], bool]]
    discovery_hint: str
    icon_path: str
```

### 2. Prerequisites System
```python
# src/core/prerequisites.py
class PrerequisiteChecker:
    """Centralized system for checking action button prerequisites"""
    
    def __init__(self, game_state):
        self.game_state = game_state
        
    def check_research_prerequisites(self) -> bool:
        """Example: Research unlocked after hiring first employee"""
        return len(self.game_state.staff.employees) > 0
        
    def check_marketing_prerequisites(self) -> bool:
        """Example: Marketing unlocked after first research paper"""
        return self.game_state.research.papers_completed > 0
        
    def check_advanced_hiring_prerequisites(self) -> bool:
        """Example: Advanced hiring after reaching 5 employees"""
        return len(self.game_state.staff.employees) >= 5

    def get_all_unlocked_actions(self) -> List[str]:
        """Return list of action IDs that meet prerequisites"""
        prerequisites_map = {
            'research': self.check_research_prerequisites,
            'marketing': self.check_marketing_prerequisites,
            'advanced_hiring': self.check_advanced_hiring_prerequisites,
            # Add more actions as needed
        }
        
        return [action_id for action_id, check_func in prerequisites_map.items() 
                if check_func()]
```

### 3. Enhanced ActionButton Component
```python
# src/ui/components/enhanced_action_button.py
class EnhancedActionButton:
    """Action button with progressive discovery states"""
    
    def __init__(self, config: ActionButtonConfig, prerequisite_checker: PrerequisiteChecker):
        self.config = config
        self.prerequisite_checker = prerequisite_checker
        self._cached_state = None
        
    def get_current_state(self) -> ActionButtonState:
        """Determine current button state based on prerequisites and resources"""
        # Check prerequisites
        prerequisites_met = all(check() for check in self.config.prerequisites)
        
        if not prerequisites_met:
            return ActionButtonState.UNDISCOVERED
            
        # Check if player can afford action
        can_afford = self._check_affordability()
        
        if can_afford:
            return ActionButtonState.AVAILABLE
        else:
            return ActionButtonState.DISCOVERED
            
    def _check_affordability(self) -> bool:
        """Check if player has resources to perform action"""
        for resource, cost in self.config.cost.items():
            current_amount = getattr(self.game_state, resource, 0)
            if current_amount < cost:
                return False
        return True
        
    def render(self, surface, x: int, y: int) -> None:
        """Render button based on current state"""
        state = self.get_current_state()
        
        if state == ActionButtonState.UNDISCOVERED:
            self._render_undiscovered(surface, x, y)
        elif state == ActionButtonState.DISCOVERED:
            self._render_discovered(surface, x, y)
        else:  # AVAILABLE
            self._render_available(surface, x, y)
```

### 4. Visual States Implementation
```python
def _render_undiscovered(self, surface, x: int, y: int) -> None:
    """Render greyed-out mysterious button"""
    # Dark grey background
    button_color = (60, 60, 60)
    border_color = (40, 40, 40)
    
    # Draw button shape but dim
    pygame.draw.rect(surface, button_color, (x, y, self.width, self.height))
    pygame.draw.rect(surface, border_color, (x, y, self.width, self.height), 2)
    
    # Show only hint text, no full description
    hint_text = font.render(self.config.discovery_hint, True, (120, 120, 120))
    surface.blit(hint_text, (x + 10, y + 10))

def _render_discovered(self, surface, x: int, y: int) -> None:
    """Render highlighted but cost-blocked button"""
    # Bright border to show "discovered" state
    button_color = (80, 80, 120)
    border_color = (150, 150, 200)  # Bright blue border
    
    pygame.draw.rect(surface, button_color, (x, y, self.width, self.height))
    pygame.draw.rect(surface, border_color, (x, y, self.width, self.height), 3)
    
    # Show full title and description, but indicate cost blocking
    title_text = font.render(self.config.title, True, (200, 200, 200))
    cost_text = font.render(f"Cost: {self.config.cost}", True, (255, 100, 100))
    
    surface.blit(title_text, (x + 10, y + 10))
    surface.blit(cost_text, (x + 10, y + 30))

def _render_available(self, surface, x: int, y: int) -> None:
    """Render fully active clickable button"""
    # Full brightness, ready to use
    button_color = (100, 150, 100)
    border_color = (150, 255, 150)
    
    pygame.draw.rect(surface, button_color, (x, y, self.width, self.height))
    pygame.draw.rect(surface, border_color, (x, y, self.width, self.height), 2)
    
    # Show all information clearly
    title_text = font.render(self.config.title, True, (255, 255, 255))
    desc_text = font.render(self.config.description, True, (220, 220, 220))
    
    surface.blit(title_text, (x + 10, y + 10))
    surface.blit(desc_text, (x + 10, y + 30))
```

## Integration Plan

### Phase 1: Core System (3-4 days)
- [ ] Implement `ActionButtonState` enum and `ActionButtonConfig` dataclass
- [ ] Create `PrerequisiteChecker` class with basic prerequisites
- [ ] Add `EnhancedActionButton` component with state logic

### Phase 2: Visual Implementation (2-3 days) 
- [ ] Implement three visual states (undiscovered/discovered/available)
- [ ] Add smooth transitions between states
- [ ] Create discovery hint system
- [ ] Add visual feedback for state changes

### Phase 3: Game Integration (2-3 days)
- [ ] Replace existing action buttons with enhanced system
- [ ] Configure prerequisites for all current actions
- [ ] Add discovery notifications when actions unlock
- [ ] Test with existing game flow

### Phase 4: Polish and Testing (2 days)
- [ ] Add sound effects for discovery events
- [ ] Optimize rendering performance
- [ ] Add comprehensive tests
- [ ] Update documentation

## Testing Strategy

### Unit Tests
```python
def test_prerequisite_checking():
    """Test that prerequisites correctly determine button states"""
    # Test undiscovered state
    # Test discovered state  
    # Test available state

def test_state_transitions():
    """Test smooth transitions between button states"""
    # Test undiscovered -> discovered
    # Test discovered -> available
    # Test state caching behavior
```

### Integration Tests
```python  
def test_action_button_integration():
    """Test enhanced buttons work with existing UI"""
    # Test click handling in different states
    # Test tooltip display
    # Test performance with multiple buttons
```

## Expected Outcomes

### User Experience Improvements
1. **Progressive Discovery** - Players feel sense of unlocking new capabilities
2. **Reduced Cognitive Load** - Only relevant options shown initially  
3. **Clear Visual Hierarchy** - Obvious distinction between available/unavailable actions
4. **Enhanced Engagement** - Mystery and progression encourage continued play

### Technical Benefits
1. **Modular Design** - Easy to add new actions with prerequisites
2. **Performance Optimized** - State caching prevents redundant calculations
3. **Maintainable** - Clear separation of concerns between logic and rendering
4. **Testable** - Well-defined interfaces enable comprehensive testing

## Success Criteria

- [ ] All existing actions work with new button system
- [ ] Smooth visual transitions between states (< 100ms)
- [ ] No performance regression in UI rendering
- [ ] Players can easily understand progression system
- [ ] Full test coverage for button state logic

## References

- `issues/smart-action-button-discovery.md` - Complete specification
- Starcraft 2 tech tree system - Visual design inspiration
- Current action button implementation - Integration requirements

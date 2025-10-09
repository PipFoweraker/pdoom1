'''
General Submenu Manager - Consistent Submenu Behavior Across All UI Elements

Handles all submenu rendering and interaction logic with consistent behavior
while allowing for visual theming (colors, icons) per submenu type.

Using our 'slightly more verbose but clearer' naming approach for maintainability.
'''

from typing import List, Dict, Any, Optional, Tuple, Callable
from enum import Enum
import pygame


class SubmenuTheme(Enum):
    '''Visual themes for different submenu types with consistent behavior.'''
    RESEARCH = 'research'           # Greenish theme for research options
    HIRING = 'hiring'               # Blue theme for staff hiring
    FUNDING = 'funding'             # Gold theme for funding options
    GOVERNANCE = 'governance'       # Purple theme for policy/governance
    TECHNICAL = 'technical'         # Gray theme for technical options
    SAFETY = 'safety'               # Red theme for safety/emergency options
    DEFAULT = 'default'             # Standard theme for general use


class SubmenuButtonState:
    '''
    Complete state information for a submenu button with clear interaction rules.
    '''
    
    def __init__(self, option_data: Dict[str, Any], is_available: bool = True, 
                 is_affordable: bool = True, reason: str = ''):
        self.option_data = option_data
        self.is_available = is_available
        self.is_affordable = is_affordable
        self.reason = reason
        self.id = option_data.get('id', 'unknown')
        self.name = option_data.get('name', 'Unknown Option')
        self.description = option_data.get('description', '')
        self.cost = option_data.get('cost', 0)
        self.ap_cost = option_data.get('ap_cost', 0)
    
    @property
    def is_selectable(self) -> bool:
        '''Whether this option can be clicked/selected.'''
        return self.is_available and self.is_affordable
    
    @property
    def display_text(self) -> str:
        '''Main text to display on the button.'''
        cost_text = ''
        if self.cost > 0:
            cost_text += f' (${self.cost}k)'
        if self.ap_cost > 0:
            cost_text += f' ({self.ap_cost} AP)'
        return f'{self.name}{cost_text}'
    
    @property
    def status_text(self) -> str:
        '''Status text to show availability/affordability.'''
        if not self.is_available:
            return 'Not Available'
        elif not self.is_affordable:
            return 'Cannot Afford'
        else:
            return 'Available'


class SubmenuConfiguration:
    '''
    Configuration for a submenu with theme and behavior settings.
    '''
    
    def __init__(self, title: str, description: str, theme: SubmenuTheme = SubmenuTheme.DEFAULT,
                 max_selections: int = 1, allow_cancel: bool = True):
        self.title = title
        self.description = description
        self.theme = theme
        self.max_selections = max_selections  # 1 for single selection, >1 for multi-select
        self.allow_cancel = allow_cancel
        self.show_costs = True
        self.show_descriptions = True


class GeneralSubmenuManager:
    '''
    Centralized manager for all submenu rendering and interaction with
    consistent behavior across different submenu types.
    '''
    
    def __init__(self):
        self.active_submenu: Optional[Dict[str, Any]] = None
        self.selected_options: List[str] = []  # Track selected option IDs
        self.theme_colors = self._initialize_theme_colors()
    
    def create_submenu_state(self, config: SubmenuConfiguration, 
                           options: List[Dict[str, Any]], 
                           availability_checker: Callable[[Dict[str, Any]], Tuple[bool, bool, str]]) -> Dict[str, Any]:
        '''
        Create a complete submenu state with consistent button states.
        
        Args:
            config: Submenu configuration (title, theme, etc.)
            options: List of option dictionaries
            availability_checker: Function that returns (available, affordable, reason) for each option
            
        Returns:
            Complete submenu state ready for rendering
        '''
        button_states = []
        
        for option in options:
            is_available, is_affordable, reason = availability_checker(option)
            button_state = SubmenuButtonState(
                option_data=option,
                is_available=is_available,
                is_affordable=is_affordable,
                reason=reason
            )
            button_states.append(button_state)
        
        submenu_state = {
            'config': config,
            'button_states': button_states,
            'selected_options': self.selected_options.copy(),
            'theme_colors': self.theme_colors[config.theme.value],
            'is_active': True
        }
        
        self.active_submenu = submenu_state
        return submenu_state
    
    def create_research_quality_submenu(self, game_state) -> Dict[str, Any]:
        '''
        Create research quality submenu with all three options (Rushed, Normal, Thorough).
        '''
        from src.core.research_quality import ResearchQuality
        
        config = SubmenuConfiguration(
            title='Research Quality Selection',
            description='Choose your research approach - affects speed, quality, and technical debt',
            theme=SubmenuTheme.RESEARCH,
            max_selections=1,
            allow_cancel=True
        )
        
        # Define all three research quality options
        options = [
            {
                'id': 'research_quality_rushed',
                'name': 'Fast & Risky (Rushed)',
                'description': 'Move fast and break things - quicker results but higher doom risk and technical debt',
                'cost': 0,
                'ap_cost': 0,
                'quality_enum': ResearchQuality.RUSHED
            },
            {
                'id': 'research_quality_standard', 
                'name': 'Balanced (Standard)',
                'description': 'Steady progress with balanced trade-offs - the default research approach',
                'cost': 0,
                'ap_cost': 0,
                'quality_enum': ResearchQuality.STANDARD
            },
            {
                'id': 'research_quality_thorough',
                'name': 'Careful & Safe (Thorough)',
                'description': 'Take time to do it right - slower but safer with less doom risk and better quality',
                'cost': 0,
                'ap_cost': 0,
                'quality_enum': ResearchQuality.THOROUGH
            }
        ]
        
        def check_research_quality_availability(option: Dict[str, Any]) -> Tuple[bool, bool, str]:
            '''Check if research quality option is available.'''
            # Research quality options are always available once system is unlocked
            is_available = getattr(game_state, 'research_quality_unlocked', False)
            is_affordable = True  # No cost for changing research quality
            reason = '' if is_available else 'Research quality system not unlocked'
            return is_available, is_affordable, reason
        
        return self.create_submenu_state(config, options, check_research_quality_availability)
    
    def handle_submenu_selection(self, option_id: str, game_state) -> bool:
        '''
        Handle selection of a submenu option with type-specific logic.
        
        Args:
            option_id: ID of the selected option
            game_state: Current game state
            
        Returns:
            True if selection was successful, False otherwise
        '''
        if not self.active_submenu:
            return False
        
        # Find the selected option
        selected_button = None
        for button_state in self.active_submenu['button_states']:
            if button_state.id == option_id:
                selected_button = button_state
                break
        
        if not selected_button or not selected_button.is_selectable:
            return False
        
        # Handle research quality selection
        if option_id.startswith('research_quality_'):
            quality_enum = selected_button.option_data.get('quality_enum')
            if quality_enum:
                game_state.set_research_quality(quality_enum)
                self.close_submenu()
                return True
        
        # Add other submenu type handlers here (hiring, funding, etc.)
        
        return False
    
    def close_submenu(self) -> None:
        '''Close the active submenu and reset state.'''
        self.active_submenu = None
        self.selected_options.clear()
    
    def is_submenu_active(self) -> bool:
        '''Check if any submenu is currently active.'''
        return self.active_submenu is not None
    
    def get_active_submenu(self) -> Optional[Dict[str, Any]]:
        '''Get the current active submenu state.'''
        return self.active_submenu
    
    def _initialize_theme_colors(self) -> Dict[str, Dict[str, Tuple[int, int, int]]]:
        '''
        Initialize color schemes for different submenu themes.
        Consistent behavior with theme-appropriate colors.
        '''
        return {
            'research': {
                'primary': (100, 255, 150),      # Greenish for research
                'secondary': (80, 200, 120),
                'background': (20, 40, 30),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (120, 255, 170)
            },
            'hiring': {
                'primary': (150, 200, 255),      # Blue for hiring
                'secondary': (120, 170, 220),
                'background': (20, 30, 40),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (170, 220, 255)
            },
            'funding': {
                'primary': (255, 215, 100),      # Gold for funding
                'secondary': (220, 180, 80),
                'background': (40, 35, 20),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (255, 235, 120)
            },
            'governance': {
                'primary': (200, 150, 255),      # Purple for governance
                'secondary': (170, 120, 220),
                'background': (35, 20, 40),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (220, 170, 255)
            },
            'technical': {
                'primary': (200, 200, 200),      # Gray for technical
                'secondary': (160, 160, 160),
                'background': (30, 30, 30),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (220, 220, 220)
            },
            'safety': {
                'primary': (255, 150, 150),      # Red for safety/emergency
                'secondary': (220, 120, 120),
                'background': (40, 20, 20),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (255, 170, 170)
            },
            'default': {
                'primary': (255, 255, 255),      # Default white theme
                'secondary': (200, 200, 200),
                'background': (25, 25, 35),
                'text': (255, 255, 255),
                'disabled': (100, 100, 100),
                'hover': (220, 220, 220)
            }
        }


# Global submenu manager instance
general_submenu_manager = GeneralSubmenuManager()


def get_general_submenu_manager() -> GeneralSubmenuManager:
    '''Get the global submenu manager instance.'''
    return general_submenu_manager

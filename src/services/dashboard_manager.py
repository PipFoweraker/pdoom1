'''
Dashboard Manager for P(Doom) Game UI

Handles persistent dashboard elements like research quality selection, government style, 
and other configurable settings that affect turn processing but don't consume action points.

Research Quality Selection Submenu Bug Fix - Dashboard Implementation
'''

import pygame
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from src.core.research_quality import ResearchQuality


class DashboardElementType(Enum):
    '''Types of dashboard elements available.'''
    RESEARCH_QUALITY = 'research_quality'
    GOVERNMENT_STYLE = 'government_style'  # Future expansion
    ECONOMIC_POLICY = 'economic_policy'    # Future expansion


@dataclass
class DashboardElementConfig:
    '''Configuration for a dashboard element.'''
    element_type: DashboardElementType
    title: str
    position: Tuple[float, float]  # (x, y) relative to screen size (0.0-1.0)
    size: Tuple[float, float]      # (width, height) relative to screen size (0.0-1.0)
    is_visible: bool = True
    is_enabled: bool = True


class DashboardManager:
    '''
    Manages persistent dashboard elements for game configuration.
    
    Dashboard elements are UI widgets that:
    - Don't consume action points
    - Persist across turns
    - Configure how turn processing works
    - Are always accessible when unlocked
    '''
    
    def __init__(self):
        self.elements: Dict[DashboardElementType, DashboardElementConfig] = {}
        self.hovered_element: Optional[DashboardElementType] = None
        self._initialize_default_elements()
    
    def _initialize_default_elements(self) -> None:
        '''Initialize default dashboard element configurations.'''
        # Research Quality selector - appears under end turn button when unlocked
        self.elements[DashboardElementType.RESEARCH_QUALITY] = DashboardElementConfig(
            element_type=DashboardElementType.RESEARCH_QUALITY,
            title='Research Quality',
            position=(0.35, 0.85),  # Center-left of screen, below end turn button
            size=(0.30, 0.08),      # 30% width, 8% height
            is_visible=False,       # Initially hidden until unlocked
            is_enabled=True
        )
    
    def update_element_visibility(self, element_type: DashboardElementType, visible: bool) -> None:
        '''Update visibility of a dashboard element.'''
        if element_type in self.elements:
            self.elements[element_type].is_visible = visible
    
    def is_element_visible(self, element_type: DashboardElementType, game_state: Any) -> bool:
        '''Check if a dashboard element should be visible based on game state.'''
        if element_type not in self.elements:
            return False
        
        config = self.elements[element_type]
        if not config.is_visible:
            return False
        
        # Research quality is only visible when unlocked
        if element_type == DashboardElementType.RESEARCH_QUALITY:
            return hasattr(game_state, 'research_quality_unlocked') and game_state.research_quality_unlocked
        
        return True
    
    def draw_research_quality_selector(
        self, 
        screen: pygame.Surface, 
        game_state: Any, 
        w: int, 
        h: int
    ) -> List[Dict[str, Any]]:
        '''
        Draw the research quality selector dashboard element.
        
        Returns:
            List of clickable rects for interaction handling
        '''
        if not self.is_element_visible(DashboardElementType.RESEARCH_QUALITY, game_state):
            return []
        
        config = self.elements[DashboardElementType.RESEARCH_QUALITY]
        
        # Calculate actual screen coordinates
        element_x = int(w * config.position[0])
        element_y = int(h * config.position[1])
        element_width = int(w * config.size[0])
        element_height = int(h * config.size[1])
        
        # Main panel background - gentle orange theme
        panel_rect = pygame.Rect(element_x, element_y, element_width, element_height)
        pygame.draw.rect(screen, (60, 45, 35), panel_rect, border_radius=8)  # Dark orange-brown background
        pygame.draw.rect(screen, (220, 160, 100), panel_rect, width=2, border_radius=8)  # Gentle orange border
        
        # Title
        font = pygame.font.Font(None, int(h * 0.022))
        title_surface = font.render('Research Quality', True, (255, 200, 150))  # Light orange text
        title_rect = title_surface.get_rect(centerx=panel_rect.centerx, y=panel_rect.y + 8)
        screen.blit(title_surface, title_rect)
        
        # Quality options as horizontal buttons
        button_width = (element_width - 40) // 3  # Three buttons with spacing
        button_height = 28
        button_y = title_rect.bottom + 8
        
        clickable_rects = []
        qualities = [
            (ResearchQuality.RUSHED, 'Fast', 'Quick results, higher risk'),
            (ResearchQuality.STANDARD, 'Balanced', 'Default research approach'), 
            (ResearchQuality.THOROUGH, 'Careful', 'Slower but safer research')
        ]
        
        for i, (quality, short_name, _) in enumerate(qualities):
            button_x = element_x + 10 + i * (button_width + 10)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Determine button state
            is_current = game_state.current_research_quality == quality
            is_hovered = (self.hovered_element == DashboardElementType.RESEARCH_QUALITY and 
                         hasattr(game_state, '_dashboard_hovered_quality') and 
                         game_state._dashboard_hovered_quality == quality)
            
            # Button colors based on state
            if is_current:
                bg_color = (100, 75, 50)      # Selected: darker orange-brown
                border_color = (255, 200, 120) # Selected: bright orange
                text_color = (255, 220, 180)   # Selected: light orange
            elif is_hovered:
                bg_color = (80, 60, 40)       # Hovered: medium orange-brown
                border_color = (240, 180, 100) # Hovered: medium orange
                text_color = (255, 210, 160)   # Hovered: light orange
            else:
                bg_color = (70, 50, 35)       # Normal: dark orange-brown
                border_color = (180, 130, 80)  # Normal: muted orange
                text_color = (200, 160, 130)   # Normal: muted light orange
            
            # Draw button
            pygame.draw.rect(screen, bg_color, button_rect, border_radius=4)
            pygame.draw.rect(screen, border_color, button_rect, width=1, border_radius=4)
            
            # Button text
            button_font = pygame.font.Font(None, int(h * 0.018))
            text_surface = button_font.render(short_name, True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
            
            # Store clickable rect
            clickable_rects.append({
                'rect': button_rect,
                'type': 'research_quality_select',
                'quality': quality,
                'element_type': DashboardElementType.RESEARCH_QUALITY
            })
        
        return clickable_rects
    
    def handle_research_quality_selection(self, quality: ResearchQuality, game_state: Any) -> bool:
        '''
        Handle selection of a research quality option.
        
        Args:
            quality: The selected research quality
            game_state: Current game state
            
        Returns:
            True if selection was successful
        '''
        try:
            # Set the new research quality
            game_state.set_research_quality(quality)
            
            # Add feedback message
            quality_names = {
                ResearchQuality.RUSHED: 'Fast & Risky',
                ResearchQuality.STANDARD: 'Balanced', 
                ResearchQuality.THOROUGH: 'Careful & Safe'
            }
            
            quality_name = quality_names.get(quality, quality.value.title())
            game_state.add_message(f'Research quality set to: {quality_name}')
            
            return True
            
        except Exception as e:
            print(f'Error setting research quality: {e}')
            return False
    
    def handle_mouse_hover(self, mouse_pos: Tuple[int, int], game_state: Any, w: int, h: int) -> None:
        '''Handle mouse hover for dashboard elements.'''
        # Reset hover state
        self.hovered_element = None
        if hasattr(game_state, '_dashboard_hovered_quality'):
            delattr(game_state, '_dashboard_hovered_quality')
        
        # Check research quality element
        if self.is_element_visible(DashboardElementType.RESEARCH_QUALITY, game_state):
            config = self.elements[DashboardElementType.RESEARCH_QUALITY]
            element_x = int(w * config.position[0])
            element_y = int(h * config.position[1])
            element_width = int(w * config.size[0])
            element_height = int(h * config.size[1])
            
            panel_rect = pygame.Rect(element_x, element_y, element_width, element_height)
            if panel_rect.collidepoint(mouse_pos):
                self.hovered_element = DashboardElementType.RESEARCH_QUALITY
                
                # Check which quality button is hovered
                button_width = (element_width - 40) // 3
                button_height = 28
                button_y = element_y + 35  # Approximate button y position
                
                qualities = [ResearchQuality.RUSHED, ResearchQuality.STANDARD, ResearchQuality.THOROUGH]
                for i, quality in enumerate(qualities):
                    button_x = element_x + 10 + i * (button_width + 10)
                    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                    if button_rect.collidepoint(mouse_pos):
                        game_state._dashboard_hovered_quality = quality
                        break
    
    def draw_dashboard_elements(
        self, 
        screen: pygame.Surface, 
        game_state: Any, 
        w: int, 
        h: int
    ) -> List[Dict[str, Any]]:
        '''
        Draw all visible dashboard elements.
        
        Returns:
            List of all clickable rects for interaction handling
        '''
        all_clickable_rects = []
        
        # Draw research quality selector
        research_rects = self.draw_research_quality_selector(screen, game_state, w, h)
        all_clickable_rects.extend(research_rects)
        
        # Future dashboard elements can be added here
        
        return all_clickable_rects


# Singleton instance
_dashboard_manager = None

def get_dashboard_manager() -> DashboardManager:
    '''Get the global dashboard manager instance.'''
    global _dashboard_manager
    if _dashboard_manager is None:
        _dashboard_manager = DashboardManager()
    return _dashboard_manager

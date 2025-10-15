'''
Modular UI Overlay and Z-Order Management System for P(Doom)

This module provides a centralized system for managing UI overlays, popups, and windows
with proper z-order layering, minimization/expansion, and visual feedback.

Inspired by Papers Please, SimPark, and Starcraft 2 UI patterns.
'''

import pygame
from enum import Enum
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from src.services.error_tracker import ErrorTracker


class ZLayer(Enum):
    '''Z-order layers for UI elements, from bottom to top'''
    BACKGROUND = 0
    GAME_UI = 1
    TOOLTIPS = 2
    DIALOGS = 3
    MODALS = 4
    CRITICAL = 5


class UIState(Enum):
    '''States for UI elements'''
    HIDDEN = 'hidden'
    MINIMIZED = 'minimized'
    NORMAL = 'normal'
    EXPANDED = 'expanded'
    ANIMATING = 'animating'


@dataclass
class UIElement:
    '''Represents a managed UI element/overlay'''
    id: str
    layer: ZLayer
    rect: pygame.Rect
    state: UIState = UIState.NORMAL
    visible: bool = True
    clickable: bool = True
    
    # Content and rendering
    title: str = ''
    content: Any = None
    render_func: Optional[Callable] = None
    
    # Animation and transitions
    target_rect: Optional[pygame.Rect] = None
    animation_progress: float = 0.0
    animation_duration: int = 30  # frames
    
    # Visual feedback
    hover_state: bool = False
    pressed_state: bool = False
    last_interaction: int = 0
    
    # Minimization support
    minimized_rect: Optional[pygame.Rect] = None
    expanded_rect: Optional[pygame.Rect] = None
    
    # Drag support
    draggable: bool = True
    being_dragged: bool = False
    drag_offset: Tuple[int, int] = (0, 0)
    header_rect: Optional[pygame.Rect] = None  # Area that can be dragged
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


class OverlayManager:
    '''
    Central manager for UI overlays with z-order control and visual feedback.
    
    Features:
    - Hierarchical z-layer management
    - Element minimization/expansion
    - Standardized visual feedback
    - Animation system integration
    - Accessibility support
    '''
    
    def __init__(self):
        self.elements: Dict[str, UIElement] = {}
        self.z_order: Dict[ZLayer, List[str]] = {layer: [] for layer in ZLayer}
        self.active_element: Optional[str] = None
        self.hover_element: Optional[str] = None
        
        # Drag state management
        self.dragging_element: Optional[str] = None
        self.last_mouse_pos: Tuple[int, int] = (0, 0)
        
        # Visual feedback settings
        self.button_press_depth = 3
        self.hover_glow_intensity = 20
        self.animation_easing = 0.15
        
        # Error tracking system (centralized)
        self.error_tracker = ErrorTracker()
        
    def register_element(self, element: UIElement) -> bool:
        '''
        Register a new UI element with the overlay manager.
        
        Args:
            element: UIElement to register
            
        Returns:
            bool: True if successful, False if ID already exists
        '''
        if element.id in self.elements:
            return False
            
        self.elements[element.id] = element
        self.z_order[element.layer].append(element.id)
        
        # Sort by layer order within each layer
        self.z_order[element.layer].sort()
        
        return True
    
    def unregister_element(self, element_id: str) -> bool:
        '''
        Remove an element from management.
        
        Args:
            element_id: ID of element to remove
            
        Returns:
            bool: True if removed, False if not found
        '''
        if element_id not in self.elements:
            return False
            
        element = self.elements[element_id]
        self.z_order[element.layer].remove(element_id)
        del self.elements[element_id]
        
        # Clear references
        if self.active_element == element_id:
            self.active_element = None
        if self.hover_element == element_id:
            self.hover_element = None
            
        return True
    
    def set_element_state(self, element_id: str, state: UIState) -> bool:
        '''
        Change the state of an element (minimize, expand, etc.)
        
        Args:
            element_id: ID of element to modify
            state: New state to set
            
        Returns:
            bool: True if successful
        '''
        if element_id not in self.elements:
            return False
            
        element = self.elements[element_id]
        old_state = element.state
        element.state = state
        
        # Set up animations based on state transition
        if state == UIState.MINIMIZED and element.minimized_rect:
            element.target_rect = element.minimized_rect.copy()
            element.state = UIState.ANIMATING
            element.animation_progress = 0.0
        elif state == UIState.EXPANDED and element.expanded_rect:
            element.target_rect = element.expanded_rect.copy()
            element.state = UIState.ANIMATING
            element.animation_progress = 0.0
        elif state == UIState.NORMAL:
            # Return to original size if animating
            if old_state in [UIState.MINIMIZED, UIState.EXPANDED]:
                element.target_rect = element.rect.copy()
                element.state = UIState.ANIMATING
                element.animation_progress = 0.0
                
        return True
    
    def bring_to_front(self, element_id: str) -> bool:
        '''
        Bring an element to the front of its layer.
        
        Args:
            element_id: ID of element to bring forward
            
        Returns:
            bool: True if successful
        '''
        if element_id not in self.elements:
            return False
            
        element = self.elements[element_id]
        layer_list = self.z_order[element.layer]
        
        if element_id in layer_list:
            layer_list.remove(element_id)
            layer_list.append(element_id)
            
        self.active_element = element_id
        return True
    
    def handle_mouse_event(self, event: pygame.event.Event, screen_w: int, screen_h: int) -> Optional[str]:
        '''
        Handle mouse events for all managed elements with drag support.
        
        Args:
            event: pygame mouse event
            screen_w, screen_h: Screen dimensions
            
        Returns:
            Optional[str]: ID of element that handled the event, if any
        '''
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle mouse button release - stop any dragging
        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging_element:
                element = self.elements[self.dragging_element]
                element.being_dragged = False
                self.dragging_element = None
                return self.dragging_element
        
        # Handle mouse motion - update drag if active
        if event.type == pygame.MOUSEMOTION:
            if self.dragging_element:
                return self._handle_drag_motion(mouse_pos)
            
            # Update last mouse position for drag calculations
            self.last_mouse_pos = mouse_pos
        
        # Check elements from top layer to bottom
        for layer in reversed(ZLayer):
            for element_id in reversed(self.z_order[layer]):
                element = self.elements[element_id]
                
                if not element.visible or not element.clickable:
                    continue
                    
                current_rect = self._get_current_rect(element)
                
                if current_rect.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        return self._handle_element_click(element_id, mouse_pos)
                    elif event.type == pygame.MOUSEMOTION and not self.dragging_element:
                        return self._handle_element_hover(element_id, mouse_pos)
                        
        # Clear hover if no element is under mouse
        if event.type == pygame.MOUSEMOTION and not self.dragging_element:
            self._clear_hover()
            
        return None
    
    def handle_keyboard_event(self, event: pygame.event.Event) -> bool:
        '''
        Handle keyboard events for accessibility and navigation.
        
        Args:
            event: pygame keyboard event
            
        Returns:
            bool: True if event was handled
        '''
        if event.type == pygame.KEYDOWN:
            # Tab navigation between elements
            if event.key == pygame.K_TAB:
                return self._navigate_elements(forward=not (event.mod & pygame.KMOD_SHIFT))
            
            # Enter/Space to activate focused element
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.active_element:
                    element = self.elements.get(self.active_element)
                    if element and element.clickable:
                        # Only intercept space bar for explicitly clickable elements
                        # This prevents interference with main game space bar (end turn)
                        if event.key == pygame.K_SPACE:
                            # For space bar, only handle if element is truly interactive
                            # Otherwise let it pass through to main game for end turn
                            return self._activate_element(self.active_element)
                        else:
                            # Always handle Enter key for focused elements
                            return self._activate_element(self.active_element)
                    # For non-clickable elements, never intercept space bar
                    # Let it pass through to main game for end turn functionality
                    elif event.key == pygame.K_RETURN:
                        # But still handle Enter for accessibility
                        return self._activate_element(self.active_element)
            
            # Escape to close top-level modal
            elif event.key == pygame.K_ESCAPE:
                return self._close_top_modal()
                
        return False
    
    def update_animations(self) -> None:
        '''Update all element animations.'''
        for element in self.elements.values():
            if element.state == UIState.ANIMATING and element.target_rect:
                # Smooth easing animation
                element.animation_progress += self.animation_easing
                
                if element.animation_progress >= 1.0:
                    # Animation complete
                    element.animation_progress = 1.0
                    element.rect = element.target_rect.copy()
                    element.target_rect = None
                    
                    # Determine final state
                    if element.minimized_rect and element.rect == element.minimized_rect:
                        element.state = UIState.MINIMIZED
                    elif element.expanded_rect and element.rect == element.expanded_rect:
                        element.state = UIState.EXPANDED
                    else:
                        element.state = UIState.NORMAL
                else:
                    # Interpolate position during animation
                    start_rect = element.rect
                    target_rect = element.target_rect
                    progress = element.animation_progress
                    
                    # Smooth easing function
                    eased_progress = self._ease_in_out_cubic(progress)
                    
                    element.rect.x = int(start_rect.x + (target_rect.x - start_rect.x) * eased_progress)
                    element.rect.y = int(start_rect.y + (target_rect.y - start_rect.y) * eased_progress)
                    element.rect.width = int(start_rect.width + (target_rect.width - start_rect.width) * eased_progress)
                    element.rect.height = int(start_rect.height + (target_rect.height - start_rect.height) * eased_progress)
    
    def render_elements(self, screen: pygame.Surface) -> None:
        '''
        Render all visible elements in proper z-order.
        
        Args:
            screen: pygame surface to render to
        '''
        # Render from bottom layer to top
        for layer in ZLayer:
            for element_id in self.z_order[layer]:
                element = self.elements[element_id]
                
                if element.visible:
                    self._render_element(screen, element)
    
    def add_error(self, error_message: str, timestamp: int = None) -> bool:
        '''
        Track an error for the easter egg beep system.
        
        This method is kept for backward compatibility but now delegates to ErrorTracker.
        
        Args:
            error_message: Error message to track
            timestamp: Time of error (current frame if None)
            
        Returns:
            bool: True if this triggers the easter egg (3 repeated errors)
        '''
        # For backward compatibility, this just delegates to the error tracker
        # but only returns whether the threshold was reached (doesn't play sounds)
        current_count = self.error_tracker.get_error_count(error_message) + 1
        self.error_tracker.track_error(error_message, timestamp)
        return current_count >= self.error_tracker.error_repeat_threshold
    
    def get_elements_by_layer(self, layer: ZLayer) -> List[UIElement]:
        '''Get all elements in a specific layer.'''
        return [self.elements[eid] for eid in self.z_order[layer] if eid in self.elements]
    
    def get_visible_elements(self) -> List[UIElement]:
        '''Get all currently visible elements.'''
        return [element for element in self.elements.values() if element.visible]
    
    def clear_layer(self, layer: ZLayer) -> None:
        '''Remove all elements from a specific layer.'''
        for element_id in list(self.z_order[layer]):
            self.unregister_element(element_id)
    
    # Private helper methods
    
    def _get_current_rect(self, element: UIElement) -> pygame.Rect:
        '''Get the current display rectangle for an element.'''
        return element.rect
    
    def _handle_element_click(self, element_id: str, mouse_pos: Tuple[int, int]) -> str:
        '''Handle click on an element with drag support.'''
        element = self.elements[element_id]
        element.pressed_state = True
        element.last_interaction = pygame.time.get_ticks()
        
        # Bring to front when clicked
        self.bring_to_front(element_id)
        
        # Start drag if element is draggable and click is in drag area
        if element.draggable:
            self._start_drag(element_id, mouse_pos)
        
        return element_id
    
    def _handle_element_hover(self, element_id: str, mouse_pos: Tuple[int, int]) -> str:
        '''Handle hover on an element.'''
        # Clear previous hover
        if self.hover_element and self.hover_element != element_id:
            self.elements[self.hover_element].hover_state = False
            
        element = self.elements[element_id]
        element.hover_state = True
        self.hover_element = element_id
        
        return element_id
    
    def _clear_hover(self) -> None:
        '''Clear hover state from all elements.'''
        if self.hover_element:
            self.elements[self.hover_element].hover_state = False
            self.hover_element = None
    
    def _navigate_elements(self, forward: bool = True) -> bool:
        '''Navigate between focusable elements with Tab.'''
        focusable = [eid for eid, elem in self.elements.items() 
                    if elem.visible and elem.clickable]
        
        if not focusable:
            return False
            
        # Sort by layer and position
        focusable.sort(key=lambda eid: (self.elements[eid].layer.value, 
                                       self.elements[eid].rect.y, 
                                       self.elements[eid].rect.x))
        
        if self.active_element in focusable:
            current_index = focusable.index(self.active_element)
            if forward:
                next_index = (current_index + 1) % len(focusable)
            else:
                next_index = (current_index - 1) % len(focusable)
            self.active_element = focusable[next_index]
        else:
            # Focus first element
            self.active_element = focusable[0] if focusable else None
            
        return True
    
    def _activate_element(self, element_id: str) -> bool:
        '''Activate an element (simulate click).'''
        if element_id in self.elements:
            element = self.elements[element_id]
            element.pressed_state = True
            element.last_interaction = pygame.time.get_ticks()
            return True
        return False
    
    def _close_top_modal(self) -> bool:
        '''Close the topmost modal/dialog element.'''
        # Find topmost modal in critical or modal layers
        for layer in [ZLayer.CRITICAL, ZLayer.MODALS]:
            if self.z_order[layer]:
                top_element_id = self.z_order[layer][-1]
                self.unregister_element(top_element_id)
                return True
        return False
    
    def _ease_in_out_cubic(self, t: float) -> float:
        '''Cubic easing function for smooth animations.'''
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def _render_element(self, screen: pygame.Surface, element: UIElement) -> None:
        '''
        Render a single element with visual feedback.
        
        Args:
            screen: pygame surface to render to
            element: UIElement to render
        '''
        current_rect = self._get_current_rect(element)
        
        # Apply visual feedback effects
        render_rect = current_rect.copy()
        
        # Button depression effect when pressed
        if element.pressed_state:
            render_rect.x += self.button_press_depth
            render_rect.y += self.button_press_depth
            
            # Clear pressed state after short duration
            if pygame.time.get_ticks() - element.last_interaction > 150:
                element.pressed_state = False
        
        # Hover glow effect
        if element.hover_state:
            # Draw glow background
            glow_rect = render_rect.inflate(6, 6)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_color = (255, 255, 255, self.hover_glow_intensity)
            pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=8)
            screen.blit(glow_surface, glow_rect.topleft)
        
        # Render element content using custom render function if available
        if element.render_func:
            element.render_func(screen, element, render_rect)
        else:
            # Default rendering: simple colored rectangle with title
            bg_color = (60, 80, 100) if element.state != UIState.MINIMIZED else (40, 50, 60)
            border_color = (150, 200, 255) if element == self.elements.get(self.active_element) else (100, 150, 200)
            
            pygame.draw.rect(screen, bg_color, render_rect, border_radius=8)
            pygame.draw.rect(screen, border_color, render_rect, width=2, border_radius=8)
            
            # Render title if present
            if element.title:
                font = pygame.font.SysFont('Consolas', 16, bold=True)
                title_surface = font.render(element.title, True, (255, 255, 255))
                title_x = render_rect.x + (render_rect.width - title_surface.get_width()) // 2
                title_y = render_rect.y + 10
                screen.blit(title_surface, (title_x, title_y))
    
    def _handle_drag_motion(self, mouse_pos: Tuple[int, int]) -> str:
        '''Handle mouse motion during drag operation.'''
        if not self.dragging_element:
            return None
            
        element = self.elements[self.dragging_element]
        
        # Calculate drag delta from last position
        dx = mouse_pos[0] - self.last_mouse_pos[0]
        dy = mouse_pos[1] - self.last_mouse_pos[1]
        
        # Update element position
        element.rect.x += dx
        element.rect.y += dy
        
        # Update last mouse position
        self.last_mouse_pos = mouse_pos
        
        return self.dragging_element
    
    def _start_drag(self, element_id: str, mouse_pos: Tuple[int, int]) -> bool:
        '''Start dragging an element.'''
        if element_id not in self.elements:
            return False
            
        element = self.elements[element_id]
        
        if not element.draggable:
            return False
            
        # Check if click is in header area (if defined) or entire element
        drag_area = element.header_rect if element.header_rect else element.rect
        
        if not drag_area.collidepoint(mouse_pos):
            return False
            
        # Calculate offset from element's top-left to mouse position
        element.drag_offset = (mouse_pos[0] - element.rect.x, mouse_pos[1] - element.rect.y)
        element.being_dragged = True
        self.dragging_element = element_id
        self.last_mouse_pos = mouse_pos
        
        # Bring to front when starting drag
        self.bring_to_front(element_id)
        
        return True
    
    def toggle_minimize(self, element_id: str) -> bool:
        '''Toggle minimize state of an element.'''
        if element_id not in self.elements:
            return False
            
        element = self.elements[element_id]
        
        if element.state == UIState.MINIMIZED:
            # Restore from minimized
            self.set_element_state(element_id, UIState.NORMAL)
        else:
            # Minimize
            if not element.minimized_rect:
                # Calculate default minimized size (title bar only)
                element.minimized_rect = pygame.Rect(
                    element.rect.x, element.rect.y,
                    element.rect.width, 30  # Title bar height
                )
            self.set_element_state(element_id, UIState.MINIMIZED)
            
        return True


# Utility functions for creating common UI element types

def create_dialog(overlay_manager: OverlayManager, 
                 id: str, 
                 title: str, 
                 content: str,
                 x: int, y: int, 
                 width: int, height: int,
                 render_func: Optional[Callable] = None,
                 use_safe_positioning: bool = True) -> UIElement:
    '''
    Create a dialog overlay element with optional safe positioning.
    
    Args:
        use_safe_positioning: If True, use safe zone system to avoid UI overlap
    '''
    # Constrain overlay size to prevent excessive overlap with permanent UI
    max_width = min(width, 300)  # Max width to keep overlays compact
    max_height = min(height, 200)  # Max height to prevent covering too much UI
    
    initial_rect = pygame.Rect(x, y, max_width, max_height)
    
    # Apply safe positioning if requested
    if use_safe_positioning:
        try:
            # Import here to avoid circular imports
            from ui import get_ui_safe_zones, find_safe_overlay_position
            
            # Get current screen dimensions (use reasonable defaults if not available)
            screen_w, screen_h = 1024, 768  # Default dimensions
            # If pygame is available, try to get current display size
            try:
                display_info = pygame.display.get_surface()
                if display_info:
                    screen_w, screen_h = display_info.get_size()
            except:
                pass  # Use default dimensions if pygame not available
            
            safe_zones = get_ui_safe_zones(screen_w, screen_h)
            positioned_rect = find_safe_overlay_position(initial_rect, screen_w, screen_h, safe_zones)
            rect = positioned_rect
        except ImportError:
            # Fallback to original positioning if safe zone system not available
            rect = initial_rect
    else:
        rect = initial_rect
    
    element = UIElement(
        id=id,
        layer=ZLayer.DIALOGS,
        rect=rect,
        title=title,
        content=content,
        render_func=render_func,
        minimized_rect=pygame.Rect(rect.x, rect.y, width // 4, 30),  # Small title bar when minimized
        expanded_rect=pygame.Rect(rect.x - 50, rect.y - 50, width + 100, height + 100)  # Larger when expanded
    )
    
    overlay_manager.register_element(element)
    return element


def create_tooltip(overlay_manager: OverlayManager,
                  id: str,
                  text: str,
                  x: int, y: int,
                  render_func: Optional[Callable] = None) -> UIElement:
    '''Create a tooltip overlay element.'''
    # Calculate size based on text
    font = pygame.font.SysFont('Consolas', 14)
    text_surface = font.render(text, True, (255, 255, 255))
    width = text_surface.get_width() + 16
    height = text_surface.get_height() + 12
    
    rect = pygame.Rect(x, y, width, height)
    
    element = UIElement(
        id=id,
        layer=ZLayer.TOOLTIPS,
        rect=rect,
        content=text,
        render_func=render_func,
        clickable=False  # Tooltips are not clickable
    )
    
    overlay_manager.register_element(element)
    return element


def create_modal(overlay_manager: OverlayManager,
                id: str,
                title: str,
                content: Any,
                screen_w: int, screen_h: int,
                width_ratio: float = 0.6,
                height_ratio: float = 0.6,
                render_func: Optional[Callable] = None) -> UIElement:
    '''Create a modal overlay element that covers the screen.'''
    width = int(screen_w * width_ratio)
    height = int(screen_h * height_ratio)
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    
    rect = pygame.Rect(x, y, width, height)
    
    element = UIElement(
        id=id,
        layer=ZLayer.MODALS,
        rect=rect,
        title=title,
        content=content,
        render_func=render_func
    )
    
    overlay_manager.register_element(element)
    return element
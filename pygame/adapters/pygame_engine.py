"""
pygame/adapters/pygame_engine.py

Pygame implementation of IGameEngine interface.
Bridges pure game logic with pygame UI.
"""

import pygame
from typing import Dict, List, Tuple, Optional
from shared.core.engine_interface import (
    IGameEngine, MessageCategory, DialogOption, DialogResult
)

class PygameEngine(IGameEngine):
    """
    Pygame implementation of game engine interface.
    Wraps existing pygame UI code to work with pure logic.
    """
    
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        """
        Initialize pygame engine adapter.
        
        Args:
            screen: Pygame display surface
            fonts: Dict of font name -> pygame.font.Font
        """
        self.screen = screen
        self.fonts = fonts
        
        # Message log
        self.messages: List[Tuple[str, MessageCategory]] = []
        self.max_messages = 50
        
        # Current UI state
        self.current_resources: Dict[str, float] = {}
        self.current_turn: int = 0
        self.current_employees: Dict[str, int] = {}
        
        # Element states for interaction
        self.hovered_elements: set = set()
        self.clicked_elements: set = set()
        
        # Sound manager (optional)
        self.sound_manager = None
    
    def set_sound_manager(self, sound_manager):
        """Set sound manager for audio playback."""
        self.sound_manager = sound_manager
    
    # ========== Display Methods ==========
    
    def display_message(self, message: str, category: MessageCategory) -> None:
        """Add message to activity log."""
        self.messages.append((message, category))
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def update_resource_display(self, resources: Dict[str, float]) -> None:
        """Update cached resource values for display."""
        self.current_resources.update(resources)
    
    def update_turn_display(self, turn: int) -> None:
        """Update turn counter."""
        self.current_turn = turn
    
    def update_employee_display(self, employees: Dict[str, int]) -> None:
        """Update employee counts."""
        self.current_employees.update(employees)
    
    # ========== Dialog Methods ==========
    
    def show_dialog(
        self,
        title: str,
        description: str,
        options: List[DialogOption]
    ) -> DialogResult:
        """
        Show modal dialog using pygame UI.
        
        This is a blocking call that runs its own event loop
        until player makes a choice.
        """
        # Get screen dimensions
        w, h = self.screen.get_size()
        
        # Dialog state
        selected_option = 0
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return DialogResult(option_id="", cancelled=True)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option = max(0, selected_option - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_option = min(
                            len(options) - 1,
                            selected_option + 1
                        )
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if options[selected_option].enabled:
                            return DialogResult(
                                option_id=options[selected_option].id,
                                cancelled=False
                            )
                    elif event.key == pygame.K_ESCAPE:
                        return DialogResult(option_id="", cancelled=True)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if any option button was clicked
                    for i, rect in enumerate(self._get_dialog_option_rects(w, h, len(options))):
                        if rect.collidepoint(mouse_pos) and options[i].enabled:
                            return DialogResult(
                                option_id=options[i].id,
                                cancelled=False
                            )
            
            # Render dialog
            self._render_dialog(title, description, options, selected_option, w, h)
            pygame.display.flip()
            pygame.time.Clock().tick(30)
        
        return DialogResult(option_id="", cancelled=True)
    
    def _render_dialog(
        self,
        title: str,
        description: str,
        options: List[DialogOption],
        selected_idx: int,
        w: int,
        h: int
    ) -> None:
        """Render dialog UI."""
        # Semi-transparent overlay
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_w = int(w * 0.6)
        dialog_h = int(h * 0.5)
        dialog_x = (w - dialog_w) // 2
        dialog_y = (h - dialog_h) // 2
        
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_w, dialog_h)
        pygame.draw.rect(self.screen, (40, 40, 60), dialog_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 200, 100), dialog_rect, width=3, border_radius=10)
        
        # Title
        font_large = self.fonts.get('large', self.fonts.get('default'))
        title_surf = font_large.render(title, True, (255, 255, 100))
        title_x = dialog_x + (dialog_w - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, dialog_y + 20))
        
        # Description
        font_normal = self.fonts.get('normal', self.fonts.get('default'))
        desc_y = dialog_y + 70
        
        # Word wrap description
        words = description.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            if font_normal.size(test_line)[0] > dialog_w - 40:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines):
            line_surf = font_normal.render(line, True, (255, 255, 255))
            self.screen.blit(line_surf, (dialog_x + 20, desc_y + i * 25))
        
        # Options
        option_rects = self._get_dialog_option_rects(w, h, len(options))
        for i, (option, rect) in enumerate(zip(options, option_rects)):
            # Button background
            color = (100, 150, 200) if i == selected_idx else (60, 80, 100)
            if not option.enabled:
                color = (40, 40, 40)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, width=2, border_radius=5)
            
            # Button text
            text_color = (255, 255, 255) if option.enabled else (100, 100, 100)
            text_surf = font_normal.render(option.text, True, text_color)
            text_x = rect.x + (rect.width - text_surf.get_width()) // 2
            text_y = rect.y + (rect.height - text_surf.get_height()) // 2
            self.screen.blit(text_surf, (text_x, text_y))
    
    def _get_dialog_option_rects(
        self,
        w: int,
        h: int,
        num_options: int
    ) -> List[pygame.Rect]:
        """Calculate option button rectangles."""
        dialog_w = int(w * 0.6)
        dialog_h = int(h * 0.5)
        dialog_x = (w - dialog_w) // 2
        dialog_y = (h - dialog_h) // 2
        
        button_w = 150
        button_h = 40
        button_spacing = 20
        
        start_y = dialog_y + dialog_h - 80
        total_width = num_options * button_w + (num_options - 1) * button_spacing
        start_x = dialog_x + (dialog_w - total_width) // 2
        
        rects = []
        for i in range(num_options):
            x = start_x + i * (button_w + button_spacing)
            rects.append(pygame.Rect(x, start_y, button_w, button_h))
        
        return rects
    
    def show_event_popup(
        self,
        event_name: str,
        event_description: str,
        options: List[DialogOption]
    ) -> DialogResult:
        """Show event popup (uses same dialog system)."""
        return self.show_dialog(event_name, event_description, options)
    
    # ========== Audio Methods ==========
    
    def play_sound(self, sound_id: str) -> None:
        """Play sound effect through sound manager."""
        if self.sound_manager:
            try:
                self.sound_manager.play_sound(sound_id)
            except Exception:
                pass  # Silently fail if sound unavailable
    
    def set_volume(self, volume: float) -> None:
        """Set audio volume."""
        if self.sound_manager:
            self.sound_manager.set_volume(volume)
    
    # ========== Visual Feedback Methods ==========
    
    def highlight_element(self, element_id: str, duration: float = 1.0) -> None:
        """
        Highlight element (can be implemented with visual feedback system).
        For now, just logs the highlight request.
        """
        pass  # TODO: Integrate with visual_feedback.py
    
    def show_tooltip(self, element_id: str, text: str) -> None:
        """Show tooltip (can be implemented later)."""
        pass  # TODO: Implement tooltip system
    
    # ========== State Query Methods ==========
    
    def is_element_hovered(self, element_id: str) -> bool:
        """Check if element is hovered."""
        return element_id in self.hovered_elements
    
    def is_element_clicked(self, element_id: str) -> bool:
        """Check if element was clicked."""
        clicked = element_id in self.clicked_elements
        if clicked:
            self.clicked_elements.remove(element_id)  # Consume click
        return clicked
    
    def register_element_hover(self, element_id: str, hovered: bool) -> None:
        """Register element hover state (called by UI code)."""
        if hovered:
            self.hovered_elements.add(element_id)
        else:
            self.hovered_elements.discard(element_id)
    
    def register_element_click(self, element_id: str) -> None:
        """Register element click (called by UI code)."""
        self.clicked_elements.add(element_id)
    
    # ========== Utility Methods ==========
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        return self.screen.get_size()
    
    def request_refresh(self) -> None:
        """Request UI refresh (pygame handles this automatically)."""
        pass
    
    # ========== Helper Methods for Integration ==========
    
    def get_messages(self) -> List[Tuple[str, MessageCategory]]:
        """Get all messages for rendering in activity log."""
        return self.messages
    
    def get_latest_message(self) -> Optional[Tuple[str, MessageCategory]]:
        """Get most recent message."""
        return self.messages[-1] if self.messages else None
    
    def clear_messages(self) -> None:
        """Clear message log."""
        self.messages.clear()
    
    def get_resources(self) -> Dict[str, float]:
        """Get current resource values for UI rendering."""
        return self.current_resources.copy()
    
    def get_turn(self) -> int:
        """Get current turn for UI rendering."""
        return self.current_turn
    
    def get_employees(self) -> Dict[str, int]:
        """Get current employee counts for UI rendering."""
        return self.current_employees.copy()


# ========== Integration Helper ==========

def create_pygame_engine_from_existing(
    screen: pygame.Surface,
    sound_manager = None
) -> PygameEngine:
    """
    Create PygameEngine from existing pygame setup.
    
    Args:
        screen: Pygame display surface
        sound_manager: Optional sound manager
        
    Returns:
        Configured PygameEngine instance
    """
    # Create default fonts if none provided
    fonts = {
        'default': pygame.font.Font(None, 24),
        'normal': pygame.font.Font(None, 24),
        'large': pygame.font.Font(None, 36),
        'small': pygame.font.Font(None, 18),
    }
    
    engine = PygameEngine(screen, fonts)
    
    if sound_manager:
        engine.set_sound_manager(sound_manager)
    
    return engine
"""
Debug Console System for P(Doom)
Provides a collapsible debug overlay showing game state variables and calculations.
"""

import pygame
from typing import Any, Dict, List, Tuple, Optional
from src.services.config_manager import get_current_config


class DebugConsole:
    """
    A collapsible debug console that displays game state information.
    
    Features:
    - Toggle visibility with a button
    - Real-time game state variables
    - Action Points calculation breakdown
    - Staff composition details
    - Economic state tracking
    - Turn-by-turn information
    """
    
    def __init__(self):
        """Initialize the debug console."""
        self.visible = False
        self.collapsed = True  # Start collapsed
        self.toggle_button_rect = None
        self.console_rect = None
        self.font = None
        self.small_font = None
        
    def initialize_fonts(self, screen_height: int) -> None:
        """Initialize fonts based on screen size."""
        # Increased font sizes by 25% for better readability
        self.font = pygame.font.Font(None, max(20, int(screen_height * 0.025)))
        self.small_font = pygame.font.Font(None, max(16, int(screen_height * 0.019)))
    
    def get_debug_data(self, game_state: Any) -> Dict[str, Any]:
        """
        Extract debug information from game state.
        
        Args:
            game_state: Current game state object
            
        Returns:
            Dictionary containing organized debug information
        """
        # Get starting values from config for comparison with safe defaults
        config = get_current_config()
        starting_resources = config.get('starting_resources', {
            'money': 100, 'staff': 2, 'reputation': 5, 'doom': 25, 
            'action_points': 3, 'compute': 0
        })
        
        # Action Points calculation breakdown with starting comparison
        ap_breakdown = {
            'current': f"{game_state.action_points} (start: {starting_resources.get('action_points', 3)})",
            'max': game_state.max_action_points,
            'base': 3,  # From config
            'staff_bonus': game_state.staff * 0.5,
            'admin_bonus': game_state.admin_staff * 1.0,
            'calculated_max': game_state.calculate_max_ap(),
            'spent_this_turn': game_state.ap_spent_this_turn,
            'glow_timer': getattr(game_state, 'ap_glow_timer', 0)
        }
        
        # Staff composition with starting comparison
        staff_info = {
            'total_staff': f"{game_state.staff} (start: {starting_resources.get('staff', 2)})",
            'admin_staff': game_state.admin_staff,
            'research_staff': getattr(game_state, 'research_staff', 0),
            'ops_staff': getattr(game_state, 'ops_staff', 0),
            'employee_blobs': len(getattr(game_state, 'employee_blobs', [])),
            'managers': len([b for b in getattr(game_state, 'employee_blobs', []) if b.get('type') == 'manager']),
            'unmanaged': len([b for b in getattr(game_state, 'employee_blobs', []) if b.get('unproductive_reason') == 'no_manager'])
        }
        
        # Economic state with starting vs current comparison
        economic_info = {
            'money': f"{game_state.money} (start: {starting_resources.get('money', 100)})",
            'reputation': f"{game_state.reputation} (start: {starting_resources.get('reputation', 5)})",
            'doom': f"{game_state.doom}% (start: {starting_resources.get('doom', 25)}%)",
            'compute': f"{game_state.compute} (start: {starting_resources.get('compute', 0)})",
            'research_progress': getattr(game_state, 'research_progress', 0),
            'papers_published': getattr(game_state, 'papers_published', 0),
            'spending_this_turn': getattr(game_state, 'spending_this_turn', 0),
            'total_spending': getattr(game_state, 'total_spending', 0)
        }
        
        # Turn information
        turn_info = {
            'current_turn': game_state.turn,
            'selected_actions': len(game_state.selected_gameplay_actions),
            'available_actions': len([a for a in game_state.actions if not a.get('rules') or a['rules'](game_state)]),
            'game_over': game_state.game_over,
            'end_game_scenario': getattr(game_state, 'end_game_scenario', None)
        }
        
        # Milestones and special states
        milestone_info = {
            'manager_milestone': getattr(game_state, 'manager_milestone_triggered', False),
            'board_members': len([b for b in getattr(game_state, 'employee_blobs', []) if b.get('type') == 'board_member']),
            'upgrades_purchased': len([u for u in game_state.upgrades if u.get('purchased', False)]),
            'achievements_unlocked': len(getattr(game_state, 'unlocked_achievements', set()))
        }
        
        return {
            'action_points': ap_breakdown,
            'staff': staff_info,
            'economy': economic_info,
            'turn': turn_info,
            'milestones': milestone_info
        }
    
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """
        Handle mouse clicks on the debug console.
        
        Args:
            pos: Mouse click position (x, y)
            
        Returns:
            True if click was handled by the console
        """
        if self.toggle_button_rect and self.toggle_button_rect.collidepoint(pos):
            if self.visible:
                self.collapsed = not self.collapsed
            else:
                self.visible = True
                self.collapsed = False
            return True
        return False
    
    def get_debug_console_key_name(self) -> str:
        """Get the current debug console keybinding name for display."""
        try:
            from src.services.keybinding_manager import keybinding_manager
            key_code = keybinding_manager.get_key_for_action("debug_console")
            # Convert common key codes to readable names
            key_names = {
                96: "`",      # Backtick
                49: "1", 50: "2", 51: "3", 52: "4", 53: "5",
                54: "6", 55: "7", 56: "8", 57: "9", 48: "0",
                299: "F12", 292: "F5", 32: "Space", 27: "Esc",
                97: "A", 100: "D", 122: "Z", 120: "X", 99: "C"
            }
            return key_names.get(key_code, f"Key{key_code}")
        except ImportError:
            return "`"  # Fallback to backtick

    def handle_keypress(self, key: int) -> bool:
        """
        Handle keyboard shortcuts for the debug console.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True if keypress was handled
        """
        # Check if this key matches the configured debug console keybinding
        try:
            from src.services.keybinding_manager import keybinding_manager
            debug_key = keybinding_manager.get_key_for_action("debug_console")
            if key == debug_key:
                if self.visible:
                    self.collapsed = not self.collapsed
                else:
                    self.visible = True
                    self.collapsed = False
                return True
        except ImportError:
            # Fallback to hardcoded keys if keybinding system unavailable
            if key in [pygame.K_F12, pygame.K_BACKQUOTE]:
                if self.visible:
                    self.collapsed = not self.collapsed
                else:
                    self.visible = True
                    self.collapsed = False
                return True
        
        # Close with Escape (if visible)
        if key == pygame.K_ESCAPE and self.visible:
            self.visible = False
            return True
            
        return False
    
    def draw(self, screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
        """
        Draw the debug console on screen.
        
        Args:
            screen: Pygame surface to draw on
            game_state: Current game state
            w: Screen width
            h: Screen height
        """
        if not self.font:
            self.initialize_fonts(h)
        
        # Draw toggle button (always visible in bottom-left)
        button_size = 30
        button_x = 10
        button_y = h - button_size - 10
        self.toggle_button_rect = pygame.Rect(button_x, button_y, button_size, button_size)
        
        # Button background
        button_color = (60, 120, 60) if self.visible else (40, 40, 40)
        pygame.draw.rect(screen, button_color, self.toggle_button_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.toggle_button_rect, 2)
        
        # Button text - ASCII-only characters for compliance
        # Safety check: ensure font is initialized before rendering
        if self.font is None:
            screen_height = screen.get_height()
            self.initialize_fonts(screen_height)
            
        button_text = "D" if not self.visible else ("-" if not self.collapsed else "+")
        text_surface = self.font.render(button_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.toggle_button_rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw console panel if visible
        if self.visible:
            self._draw_console_panel(screen, game_state, w, h)
    
    def _draw_console_panel(self, screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
        """Draw the main console panel with debug information."""
        # Safety check: ensure fonts are initialized
        if self.font is None or self.small_font is None:
            screen_height = screen.get_height()
            self.initialize_fonts(screen_height)
            
        # Calculate console dimensions - 40% larger for better visibility
        if self.collapsed:
            console_width = 420  # Increased from 300 (40% larger)
            console_height = 56   # Increased from 40 (40% larger)
        else:
            console_width = min(700, w - 60)  # Increased from 500 (40% larger)
            console_height = min(560, h - 100)  # Increased from 400 (40% larger)
        
        console_x = 50
        console_y = h - console_height - 50
        self.console_rect = pygame.Rect(console_x, console_y, console_width, console_height)
        
        # Console background with transparency
        console_surface = pygame.Surface((console_width, console_height), pygame.SRCALPHA)
        console_surface.fill((20, 20, 30, 220))  # Dark blue with alpha
        screen.blit(console_surface, (console_x, console_y))
        
        # Console border
        pygame.draw.rect(screen, (100, 150, 200), self.console_rect, 2)
        
        if self.collapsed:
            # Collapsed state - just show title
            key_name = self.get_debug_console_key_name()
            title_text = self.font.render(f"Debug Console ({key_name} to expand)", True, (200, 200, 200))
            screen.blit(title_text, (console_x + 10, console_y + 10))
        else:
            # Expanded state - show full debug info
            self._draw_debug_info(screen, game_state, console_x, console_y, console_width, console_height)
    
    def _draw_debug_info(self, screen: pygame.Surface, game_state: Any, 
                        x: int, y: int, width: int, height: int) -> None:
        """Draw the detailed debug information."""
        debug_data = self.get_debug_data(game_state)
        
        # Header
        key_name = self.get_debug_console_key_name()
        header_text = self.font.render(f"Debug Console ({key_name} to collapse)", True, (255, 255, 255))
        screen.blit(header_text, (x + 10, y + 5))
        
        # Content area - optimized spacing for better real estate usage
        content_y = y + 25
        line_height = 18  # Increased from 16 for better readability with larger fonts
        col_width = width // 3
        
        # Column 1: Action Points & Staff - optimized spacing for larger console
        self._draw_section(screen, "ACTION POINTS", debug_data['action_points'], 
                          x + 10, content_y, col_width)
        
        self._draw_section(screen, "STAFF", debug_data['staff'], 
                          x + 10, content_y + 140, col_width)  # Increased from 120 to use more space
        
        # Column 2: Economy & Turn
        self._draw_section(screen, "ECONOMY", debug_data['economy'], 
                          x + col_width + 10, content_y, col_width)
        
        self._draw_section(screen, "TURN INFO", debug_data['turn'], 
                          x + col_width + 10, content_y + 140, col_width)  # Increased from 120
        
        # Column 3: Milestones
        self._draw_section(screen, "MILESTONES", debug_data['milestones'], 
                          x + col_width * 2 + 10, content_y, col_width)
    
    def _draw_section(self, screen: pygame.Surface, title: str, data: Dict[str, Any], 
                     x: int, y: int, width: int) -> None:
        """Draw a section of debug information."""
        # Section title
        title_surface = self.font.render(title, True, (255, 255, 100))
        screen.blit(title_surface, (x, y))
        
        # Section data
        data_y = y + 20
        for key, value in data.items():
            # Format the display
            if isinstance(value, float):
                display_value = f"{value:.1f}"
            elif isinstance(value, bool):
                display_value = "Y" if value else "N"  # ASCII-only compliance
            else:
                display_value = str(value)
            
            # Color coding for important values
            if key in ['current', 'money', 'doom', 'current_turn']:
                color = (255, 200, 100)  # Orange for key values
            elif key in ['max', 'calculated_max'] and value != data.get('current', -1):
                color = (255, 100, 100)  # Red for discrepancies
            elif 'unmanaged' in key and value > 0:
                color = (255, 100, 100)  # Red for problems
            else:
                color = (200, 200, 200)  # Gray for normal values
            
            # Draw the key-value pair with optimized spacing
            text = f"{key}: {display_value}"
            text_surface = self.small_font.render(text, True, color)
            screen.blit(text_surface, (x, data_y))
            data_y += 16  # Increased from 14 for better readability with larger fonts
            
            # Expanded overflow limit for larger console
            if data_y > y + 120:  # Increased from 100 to use more vertical space
                break


# Global debug console instance
debug_console = DebugConsole()


def handle_debug_console_click(pos: Tuple[int, int]) -> bool:
    """Handle clicks for the debug console."""
    return debug_console.handle_click(pos)


def handle_debug_console_keypress(key: int) -> bool:
    """Handle keypresses for the debug console."""
    return debug_console.handle_keypress(key)


def draw_debug_console(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """Draw the debug console overlay."""
    debug_console.draw(screen, game_state, w, h)

"""
Three-column layout system for P(Doom).

Implements a cleaner 3-column layout as requested:
- Left column: Repeating actions (hire, research, etc.)
- Middle column: Staff/employees, animations, context displays
- Right column: One-off actions (upgrades, settings, etc.)

This layout starts mostly empty and fills up as actions are unlocked,
providing a cleaner initial experience.
"""

import pygame
from typing import Any, List, Dict, Tuple, Optional
from ..components.colours import *
# from ..components.typography import font_manager  # Temporarily disabled
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle


class ThreeColumnLayout:
    """Manages the 3-column layout rendering and positioning."""
    
    def __init__(self):
        self.left_column_width = 0.28   # 28% for repeating actions
        self.middle_column_width = 0.44  # 44% for staff/animations
        self.right_column_width = 0.28   # 28% for one-off actions
        
        # Y positions
        self.header_height = 0.20        # 20% for resource header
        self.content_start = 0.22        # Content starts at 22%
        self.context_window_height = 0.10 # 10% for context window at bottom
        
        # Column content areas
        self.left_rect = None
        self.middle_rect = None
        self.right_rect = None
        
        # Keystroke system
        self.keybindings = {}           # Maps key -> action_data
        self.used_keys = set()          # Track used keybindings
        
        # Action categorization
        self.repeating_actions = [
            "hire_researchers", "conduct_research", "publish_papers",
            "hire_compute", "hire_managers", "train_staff"
        ]
        
        self.oneoff_actions = [
            "upgrade_", "buy_", "invest_", "lobby_", "audit_",
            "espionage", "scout_", "board_", "legal_"
        ]
    
    def calculate_layout(self, w: int, h: int) -> Dict[str, pygame.Rect]:
        """Calculate the layout rectangles for all columns."""
        # Header area (unchanged)
        header_rect = pygame.Rect(0, 0, w, int(h * self.header_height))
        
        # Content area calculations - leave more space above context window
        content_y = int(h * self.content_start)
        content_height = int(h * (1.0 - self.content_start - self.context_window_height - 0.02))  # 2% buffer
        
        # Left column (repeating actions)
        left_x = int(w * 0.02)  # 2% margin
        left_width = int(w * self.left_column_width)
        self.left_rect = pygame.Rect(left_x, content_y, left_width, content_height)
        
        # Middle column (staff/animations)
        middle_x = left_x + left_width + int(w * 0.01)  # 1% gap
        middle_width = int(w * self.middle_column_width)
        self.middle_rect = pygame.Rect(middle_x, content_y, middle_width, content_height)
        
        # Right column (one-off actions) - ensure proper spacing
        right_x = middle_x + middle_width + int(w * 0.01)  # 1% gap
        right_width = int(w * self.right_column_width) - int(w * 0.02)  # 2% margin from right edge
        self.right_rect = pygame.Rect(right_x, content_y, right_width, content_height)
        
        # Context window at bottom - reduced height
        context_y = int(h * (1.0 - self.context_window_height))
        context_rect = pygame.Rect(0, context_y, w, int(h * self.context_window_height))
        
        return {
            'header': header_rect,
            'left_column': self.left_rect,
            'middle_column': self.middle_rect,
            'right_column': self.right_rect,
            'context_window': context_rect
        }
    
    def categorize_action(self, action: Dict[str, Any]) -> str:
        """Categorize an action as 'repeating', 'oneoff', or 'middle'."""
        action_name = action.get('name', '').lower()
        action_id = action.get('id', '').lower()
        
        # Specific categorization for cleaner layout
        
        # Left column: Core repeating gameplay actions
        left_column_actions = [
            'grow community', 'fundraise', 'safety research', 'governance research',
            'buy compute', 'interpretability research', 'ai alignment research'
        ]
        
        # Right column: Strategic/one-time decisions  
        right_column_actions = [
            'lobby', 'board', 'audit', 'espionage', 'scout', 'invest',
            'legal', 'hire managers', 'buy servers', 'upgrade'
        ]
        
        # Check for exact matches first
        for left_action in left_column_actions:
            if left_action in action_name:
                return 'repeating'
        
        for right_action in right_column_actions:
            if right_action in action_name:
                return 'oneoff'
        
        # Middle column: Delegation and staff management
        if any(word in action_name for word in ['delegate', 'manage', 'assign', 'train']):
            return 'middle'
        
        # Default: most actions go to left column (core gameplay)
        return 'repeating'
    
    def filter_actions_by_column(self, actions: List[Dict[str, Any]], 
                                game_state: Any) -> Dict[str, List[Dict[str, Any]]]:
        """Filter and categorize actions by column with simplified initial display."""
        categorized = {
            'repeating': [],
            'oneoff': [],
            'middle': []
        }
        
        # For early game (first few turns), show only essential actions
        early_game_threshold = 3
        is_early_game = game_state.turn <= early_game_threshold
        
        # Essential actions for early game
        essential_early_actions = [
            "grow community", "fundraise", "safety research", "buy compute"
        ]
        
        for i, action in enumerate(actions):
            # Only show unlocked actions
            if action.get("rules") and not action["rules"](game_state):
                continue
            
            action_name = action.get('name', '').lower()
            
            # In early game, only show essential actions to reduce clutter
            if is_early_game:
                if not any(essential in action_name for essential in essential_early_actions):
                    continue
                
            category = self.categorize_action(action)
            action_with_index = action.copy()
            action_with_index['original_index'] = i
            categorized[category].append(action_with_index)
        
        return categorized
    
    def draw_column_headers(self, screen: pygame.Surface, layout_rects: Dict[str, pygame.Rect],
                           font: pygame.font.Font) -> None:
        """Draw shorter, cleaner headers for each column."""
        # Left column header
        left_header = font.render("CORE ACTIONS", True, NEON_GREEN)
        left_x = layout_rects['left_column'].centerx - left_header.get_width() // 2
        screen.blit(left_header, (left_x, layout_rects['left_column'].y - 25))
        
        # Middle column header  
        middle_header = font.render("RESEARCH TEAM", True, NEON_GREEN)
        middle_x = layout_rects['middle_column'].centerx - middle_header.get_width() // 2
        screen.blit(middle_header, (middle_x, layout_rects['middle_column'].y - 25))
        
        # Right column header
        right_header = font.render("STRATEGY", True, NEON_GREEN)
        right_x = layout_rects['right_column'].centerx - right_header.get_width() // 2
        screen.blit(right_header, (right_x, layout_rects['right_column'].y - 25))
    
    def draw_column_borders(self, screen: pygame.Surface, 
                           layout_rects: Dict[str, pygame.Rect]) -> None:
        """Draw subtle borders around columns."""
        border_color = (60, 120, 60, 128)  # Semi-transparent green
        
        for column_name in ['left_column', 'middle_column', 'right_column']:
            rect = layout_rects[column_name]
            # Draw subtle border
            pygame.draw.rect(screen, DARK_GREEN, rect, width=1, border_radius=8)
    
    def draw_repeating_actions(self, screen: pygame.Surface, actions: List[Dict[str, Any]],
                              layout_rect: pygame.Rect, game_state: Any, 
                              fonts: Dict[str, pygame.font.Font]) -> List[Tuple[pygame.Rect, int]]:
        """Draw repeating actions in the left column."""
        button_rects = []
        
        if not actions:
            # Show "No actions available" message
            empty_text = fonts['small'].render("Actions will appear here", True, (120, 120, 120))
            text_x = layout_rect.centerx - empty_text.get_width() // 2
            text_y = layout_rect.centery - empty_text.get_height() // 2
            screen.blit(empty_text, (text_x, text_y))
            return button_rects

        # Calculate button layout - smaller, tighter buttons
        button_height = 42  # Reduced from 50
        button_spacing = 4   # Reduced from 6
        start_y = layout_rect.y + 10
        
        for i, action in enumerate(actions):
            y_pos = start_y + i * (button_height + button_spacing)
            
            # Stop if we run out of space
            if y_pos + button_height > layout_rect.bottom - 10:
                break
            
            button_rect = pygame.Rect(layout_rect.x + 5, y_pos, 
                                    layout_rect.width - 10, button_height)
            
            # Determine button state
            original_idx = action['original_index']
            ap_cost = action.get("ap_cost", 1)
            
            if game_state.action_points < ap_cost:
                button_state = ButtonState.DISABLED
            elif original_idx in getattr(game_state, 'selected_actions', []):
                button_state = ButtonState.PRESSED
            elif (hasattr(game_state, 'hovered_action_idx') and 
                  game_state.hovered_action_idx == original_idx):
                button_state = ButtonState.HOVER
            else:
                button_state = ButtonState.NORMAL
            
            # Create shorter, cleaner button text
            action_name = action['name']
            
            # Shorten common long names for better fit
            name_shortcuts = {
                'Grow Community': 'Community',
                'Safety Research': 'Safety',
                'Governance Research': 'Governance', 
                'Buy Compute': 'Compute',
                'Interpretability Research': 'Interpret.',
                'AI Alignment Research': 'Alignment'
            }
            
            display_name = name_shortcuts.get(action_name, action_name)
            
            # Get unique keybinding for this action
            keybind = self._get_unique_keybind(display_name, [str(i+1)])
            self.keybindings[keybind.lower()] = action
            
            # Create button text with keybinding
            button_text = f"[{keybind}] {display_name}"
            
            # Truncate if still too long
            max_chars = 20  # Adjust based on column width
            if len(button_text) > max_chars:
                button_text = button_text[:max_chars-3] + "..."
            
            # Draw button with action-specific colors
            button_colors = self._get_action_specific_colors(action_name)
            visual_feedback.draw_button(
                screen, button_rect, button_text, button_state, FeedbackStyle.BUTTON, button_colors
            )
            
            # Draw usage indicators for repeated actions
            if hasattr(game_state, 'selected_action_instances'):
                action_count = sum(1 for inst in game_state.selected_action_instances 
                                 if inst['action_idx'] == original_idx)
                if action_count > 0:
                    self._draw_usage_indicators(screen, button_rect, action_count)
            
            button_rects.append((button_rect, original_idx))
        
        return button_rects
    
    def draw_middle_column(self, screen: pygame.Surface, layout_rect: pygame.Rect,
                          game_state: Any, fonts: Dict[str, pygame.font.Font]) -> None:
        """Draw the middle column with staff and animations."""
        # Draw employee blobs
        self._draw_employee_section(screen, layout_rect, game_state, fonts)
        
        # Draw delegation/management interface if unlocked
        if hasattr(game_state, 'delegation_unlocked') and game_state.delegation_unlocked:
            self._draw_delegation_interface(screen, layout_rect, game_state, fonts)
    
    def draw_strategic_actions(self, screen: pygame.Surface, actions: List[Dict[str, Any]],
                              layout_rect: pygame.Rect, game_state: Any,
                              fonts: Dict[str, pygame.font.Font]) -> List[Tuple[pygame.Rect, int]]:
        """Draw one-off/strategic actions in the right column."""
        button_rects = []
        
        if not actions:
            # Show "No strategic actions" message
            empty_text = fonts['small'].render("Strategic actions", True, (120, 120, 120))
            text_x = layout_rect.centerx - empty_text.get_width() // 2
            text_y = layout_rect.y + 20
            screen.blit(empty_text, (text_x, text_y))
            
            empty_text2 = fonts['small'].render("will appear here", True, (120, 120, 120))
            text_x2 = layout_rect.centerx - empty_text2.get_width() // 2
            screen.blit(empty_text2, (text_x2, text_y + 20))
            return button_rects
        
        # Calculate button layout - compact buttons for strategic actions
        button_height = 35  # Smaller than repeating actions
        button_spacing = 3   # Tighter spacing
        start_y = layout_rect.y + 10
        
        for i, action in enumerate(actions):
            y_pos = start_y + i * (button_height + button_spacing)
            
            # Stop if we run out of space
            if y_pos + button_height > layout_rect.bottom - 10:
                break
            
            button_rect = pygame.Rect(layout_rect.x + 5, y_pos,
                                    layout_rect.width - 10, button_height)
            
            # Determine button state (similar to repeating actions)
            original_idx = action['original_index']
            ap_cost = action.get("ap_cost", 1)
            
            if game_state.action_points < ap_cost:
                button_state = ButtonState.DISABLED
            elif original_idx in getattr(game_state, 'selected_actions', []):
                button_state = ButtonState.PRESSED
            elif (hasattr(game_state, 'hovered_action_idx') and 
                  game_state.hovered_action_idx == original_idx):
                button_state = ButtonState.HOVER
            else:
                button_state = ButtonState.NORMAL
            
            # Create clean button text for strategic actions - no overflow text
            action_name = action['name']
            
            # Strategic action shortcuts - clean names only
            strategic_shortcuts = {
                'Hire Managers': 'Managers',
                'Lobby Government': 'Lobby',
                'Board Meeting': 'Board',
                'Audit Finances': 'Audit',
                'Scout Opponents': 'Scout',
                'Espionage': 'Intel',
                'Buy Servers': 'Servers',
                'Upgrade Security': 'Security'
            }
            
            display_name = strategic_shortcuts.get(action_name, action_name)
            
            # Ensure text fits in right column width
            max_chars = 12  # Conservative for right column
            if len(display_name) > max_chars:
                display_name = display_name[:max_chars-1] + "."
            
            # Get unique keybinding for strategic actions
            keybind = self._get_unique_keybind(display_name)
            self.keybindings[keybind.lower()] = action
            
            button_text = f"[{keybind}] {display_name}"
            
            # Draw button with strategic action styling
            visual_feedback.draw_button(
                screen, button_rect, button_text, button_state, 
                FeedbackStyle.BUTTON, self._get_strategic_button_colors()
            )
            
            button_rects.append((button_rect, original_idx))
        
        return button_rects
    
    def _draw_usage_indicators(self, screen: pygame.Surface, button_rect: pygame.Rect, 
                              count: int) -> None:
        """Draw small indicators showing action usage."""
        indicator_size = 4
        indicator_color = (100, 255, 100)
        
        start_x = button_rect.right - (min(count, 5) * indicator_size * 2) - 5
        start_y = button_rect.top + 5
        
        for i in range(min(count, 5)):
            circle_x = start_x + (i * indicator_size * 2)
            circle_y = start_y + indicator_size
            pygame.draw.circle(screen, indicator_color, (circle_x, circle_y), indicator_size)
        
        # Show "+N" if more than 5
        if count > 5:
            font = pygame.font.SysFont('Consolas', 10)
            more_text = font.render(f"+{count-5}", True, indicator_color)
            screen.blit(more_text, (start_x + 5 * indicator_size * 2 + 2, start_y))
    
    def _draw_employee_section(self, screen: pygame.Surface, layout_rect: pygame.Rect,
                              game_state: Any, fonts: Dict[str, pygame.font.Font]) -> None:
        """Draw the employee/blob section in the middle column."""
        # Section header
        employee_header = fonts['font'].render("RESEARCH TEAM", True, NEON_GREEN)
        header_x = layout_rect.x + (layout_rect.width - employee_header.get_width()) // 2
        screen.blit(employee_header, (header_x, layout_rect.y + 5))
        
        # Employee count
        staff_count = fonts['small'].render(f"Staff: {game_state.staff}", True, STAFF_COLOUR)
        count_x = layout_rect.x + (layout_rect.width - staff_count.get_width()) // 2
        screen.blit(staff_count, (count_x, layout_rect.y + 25))
        
        # Employee visualization area
        blob_area = pygame.Rect(layout_rect.x + 10, layout_rect.y + 50,
                               layout_rect.width - 20, layout_rect.height - 60)
        
        # DEVELOPMENT NOTE: Employee blob animations temporarily disabled for cleaner playtest
        # Will be re-enabled in future build with improved positioning and animations
        # Original blob system available in legacy UI
        
        # Simplified staff display for playtesting
        if game_state.staff > 0:
            # Draw simple staff representation
            staff_text = fonts['small'].render(f"{game_state.staff} researchers working", True, STAFF_COLOUR)
            text_x = blob_area.centerx - staff_text.get_width() // 2
            text_y = blob_area.y + 20
            screen.blit(staff_text, (text_x, text_y))
            
            # Show productivity info if available
            if hasattr(game_state, 'compute') and game_state.compute > 0:
                compute_text = fonts['small'].render(f"Compute available: {game_state.compute}", True, COMPUTE_COLOUR)
                compute_x = blob_area.centerx - compute_text.get_width() // 2
                screen.blit(compute_text, (compute_x, text_y + 20))
            
            # Show research status
            if hasattr(game_state, 'research_progress'):
                progress_text = fonts['small'].render(f"Research: {game_state.research_progress}/100", True, RESEARCH_COLOUR)
                progress_x = blob_area.centerx - progress_text.get_width() // 2
                screen.blit(progress_text, (progress_x, text_y + 40))
        else:
            # Show "No employees" message
            no_staff_text = fonts['small'].render("Hire researchers to", True, (120, 120, 120))
            no_staff_text2 = fonts['small'].render("see your team here", True, (120, 120, 120))
            
            text_x = blob_area.centerx - no_staff_text.get_width() // 2
            text_y = blob_area.centery - 10
            screen.blit(no_staff_text, (text_x, text_y))
            screen.blit(no_staff_text2, (text_x, text_y + 15))
    
    def _draw_simplified_employee_blobs(self, screen: pygame.Surface, blob_area: pygame.Rect,
                                       game_state: Any) -> None:
        """Draw simplified employee blobs for the 3-column layout."""
        import math
        
        # Calculate grid layout for blobs
        blob_size = 25
        cols = blob_area.width // (blob_size + 10)
        rows = blob_area.height // (blob_size + 10)
        
        blob_count = min(len(game_state.employee_blobs), cols * rows)
        
        for i in range(blob_count):
            blob = game_state.employee_blobs[i]
            
            # Calculate grid position
            col = i % cols
            row = i // cols
            
            x = blob_area.x + col * (blob_size + 10) + blob_size // 2
            y = blob_area.y + row * (blob_size + 10) + blob_size // 2
            
            # Draw blob with simplified styling
            blob_color = (150, 200, 255) if blob.get('has_compute') else (100, 150, 200)
            
            pygame.draw.circle(screen, blob_color, (x, y), blob_size // 2)
            pygame.draw.circle(screen, (255, 255, 255), (x, y), blob_size // 2, 2)
            
            # Simple eyes
            eye_offset = 6
            pygame.draw.circle(screen, (50, 50, 100), (x - eye_offset, y - 3), 2)
            pygame.draw.circle(screen, (50, 50, 100), (x + eye_offset, y - 3), 2)
            
            # Productivity indicator
            if blob.get('productivity', 0) > 0:
                pygame.draw.circle(screen, (100, 255, 100), (x, y + 6), 3)
    
    def _draw_delegation_interface(self, screen: pygame.Surface, layout_rect: pygame.Rect,
                                  game_state: Any, fonts: Dict[str, pygame.font.Font]) -> None:
        """Draw delegation/management interface if unlocked."""
        # This is a placeholder for future delegation features
        delegation_y = layout_rect.bottom - 80
        delegation_rect = pygame.Rect(layout_rect.x + 10, delegation_y, 
                                    layout_rect.width - 20, 70)
        
        pygame.draw.rect(screen, DARK_GREEN, delegation_rect, width=1, border_radius=5)
        
        delegation_text = fonts['small'].render("Management Interface", True, NEON_GREEN)
        text_x = delegation_rect.centerx - delegation_text.get_width() // 2
        screen.blit(delegation_text, (text_x, delegation_rect.y + 5))
        
        # Placeholder for delegation controls
        placeholder_text = fonts['small'].render("(Coming in future update)", True, (120, 120, 120))
        placeholder_x = delegation_rect.centerx - placeholder_text.get_width() // 2
        screen.blit(placeholder_text, (placeholder_x, delegation_rect.y + 25))
    
    def _get_action_specific_colors(self, action_name: str) -> Dict[str, Dict[str, Any]]:
        """Get action-specific button colors for visual differentiation."""
        action_name_lower = action_name.lower()
        
        # Research actions - blue tint
        if 'research' in action_name_lower or 'safety' in action_name_lower:
            return {
                ButtonState.NORMAL: {
                    'bg': (60, 80, 120),
                    'border': (100, 140, 200),
                    'text': (255, 255, 255),
                    'shadow': (30, 40, 60)
                },
                ButtonState.HOVER: {
                    'bg': (80, 100, 140),
                    'border': (120, 160, 220),
                    'text': (255, 255, 255),
                    'shadow': (50, 60, 80),
                    'glow': (150, 180, 255, 40)
                }
            }
        
        # Economic actions - green tint
        elif any(word in action_name_lower for word in ['fundraise', 'community', 'compute']):
            return {
                ButtonState.NORMAL: {
                    'bg': (60, 100, 60),
                    'border': (100, 180, 100),
                    'text': (255, 255, 255),
                    'shadow': (30, 50, 30)
                },
                ButtonState.HOVER: {
                    'bg': (80, 120, 80),
                    'border': (120, 200, 120),
                    'text': (255, 255, 255),
                    'shadow': (50, 70, 50),
                    'glow': (150, 255, 150, 40)
                }
            }
        
        # Default colors
        return None
    
    def _get_strategic_button_colors(self) -> Dict[str, Dict[str, Any]]:
        """Get custom colors for strategic action buttons."""
        return {
            ButtonState.NORMAL: {
                'bg': (80, 80, 140),
                'border': (120, 120, 200),
                'text': (255, 255, 255),
                'shadow': (40, 40, 70)
            },
            ButtonState.HOVER: {
                'bg': (100, 100, 160),
                'border': (140, 140, 220),
                'text': (255, 255, 255),
                'shadow': (60, 60, 90),
                'glow': (180, 180, 255, 40)
            },
            ButtonState.PRESSED: {
                'bg': (60, 120, 60),
                'border': (100, 200, 100),
                'text': (255, 255, 255),
                'shadow': (30, 60, 30)
            },
            ButtonState.DISABLED: {
                'bg': (60, 60, 60),
                'border': (100, 100, 100),
                'text': (150, 150, 150),
                'shadow': (30, 30, 30)
            }
        }
    
    def handle_keypress(self, key: str) -> Optional[Dict[str, Any]]:
        """Handle keystroke input and return action if bound."""
        key_lower = key.lower()
        
        # Handle Enter/Return as space equivalent
        if key in ['return', 'enter']:
            key_lower = 'space'
            
        # Check for bound action
        if key_lower in self.keybindings:
            return self.keybindings[key_lower]
        return None
    
    def get_available_keybindings(self) -> Dict[str, str]:
        """Return current keybinding mappings for display."""
        return {k: v.get('name', 'Unknown') for k, v in self.keybindings.items()}
    
    def clear_keybindings(self) -> None:
        """Clear all current keybindings."""
        self.keybindings.clear()
        self.used_keys.clear()
    
    def _get_unique_keybind(self, action_name: str, preferred_keys: List[str] = None) -> str:
        """Get a unique keybinding for an action."""
        # Try preferred keys first
        if preferred_keys:
            for key in preferred_keys:
                if key.lower() not in self.used_keys:
                    self.used_keys.add(key.lower())
                    return key.upper()
        
        # Try first letter
        first_letter = action_name[0].lower()
        if first_letter not in self.used_keys:
            self.used_keys.add(first_letter)
            return first_letter.upper()
        
        # Try other letters in name
        for char in action_name.lower():
            if char.isalpha() and char not in self.used_keys:
                self.used_keys.add(char)
                return char.upper()
        
        # Fallback to numbers
        for i in range(10):
            key = str(i)
            if key not in self.used_keys:
                self.used_keys.add(key)
                return key
        
        # Ultimate fallback
        return "?"

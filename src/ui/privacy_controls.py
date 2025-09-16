"""
Privacy Controls UI Component for P(Doom)

This module provides user-facing privacy controls for the Game Run Logger system:
- Logging level selection (Disabled/Minimal/Standard/Verbose/Debug)
- Data summary display (disk usage, session count, cleanup info)
- Delete all data functionality with confirmation
- Transparency information and tooltips

Design Philosophy:
- Privacy by default: Logging starts disabled (opt-in required)
- Full transparency: Users see exactly what data is collected
- User control: Easy to change settings and delete data
- Educational: Clear explanations of each logging level
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from src.services.game_run_logger import GameRunLogger, LoggingLevel, get_game_logger
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle


class PrivacyUIState(Enum):
    """Privacy controls UI states."""
    MAIN = "main"           # Main privacy controls screen
    DELETE_CONFIRM = "delete_confirm"  # Delete confirmation dialog
    LEVEL_INFO = "level_info"         # Detailed logging level information


class PrivacyControls:
    """Privacy controls UI component for Game Run Logger configuration."""
    
    def __init__(self):
        """Initialize privacy controls with default state."""
        self.current_state = PrivacyUIState.MAIN
        self.selected_item = 0
        self.logger = None
        self.user_data_summary = None
        self.show_tooltip = False
        self.tooltip_text = ""
        self.show_first_time_info = False
        
        # Initialize logger for privacy controls
        self._refresh_logger_data()
        
        # Check if this is the first time accessing privacy controls
        self._check_first_time_access()
    
    def _refresh_logger_data(self) -> None:
        """Refresh logger instance and user data summary."""
        try:
            # Get current logger instance
            self.logger = get_game_logger()
            if self.logger:
                self.user_data_summary = self.logger.get_user_data_summary()
            else:
                self.user_data_summary = None
        except Exception:
            # Graceful fallback if logger not available
            self.logger = None
            self.user_data_summary = None
    
    def _check_first_time_access(self) -> None:
        """Check if this is the first time user is accessing privacy controls."""
        try:
            if self.logger and self.logger.privacy_manager:
                settings = self.logger.privacy_manager.settings
                # If logging_level is not explicitly set, show first-time info
                if 'logging_level' not in settings:
                    self.show_first_time_info = True
        except Exception:
            pass
    
    def get_logging_level_options(self) -> List[Tuple[int, str, str]]:
        """Get available logging levels with names and descriptions."""
        return [
            (LoggingLevel.DISABLED, "Disabled", "No data collection - complete privacy"),
            (LoggingLevel.MINIMAL, "Minimal", "Basic session info only - no gameplay details"),
            (LoggingLevel.STANDARD, "Standard", "Key actions and milestones - balanced approach"),
            (LoggingLevel.VERBOSE, "Verbose", "Detailed gameplay tracking - comprehensive analysis"),
            (LoggingLevel.DEBUG, "Debug", "Complete technical logging - full transparency")
        ]
    
    def get_current_logging_level(self) -> int:
        """Get current logging level from logger."""
        if self.logger:
            return self.logger.logging_level
        return LoggingLevel.DISABLED
    
    def set_logging_level(self, level: int) -> bool:
        """Set new logging level and persist to config."""
        try:
            if self.logger:
                self.logger.configure_logging_level(level)
                self._refresh_logger_data()
                # Dismiss first-time info after user makes a choice
                self.show_first_time_info = False
                return True
        except Exception:
            pass
        return False
    
    def delete_all_data(self) -> bool:
        """Delete all collected data."""
        try:
            if self.logger:
                self.logger.delete_all_data()
                self._refresh_logger_data()
                return True
        except Exception:
            pass
        return False
    
    def draw_main_screen(self, screen: pygame.Surface, w: int, h: int) -> None:
        """Draw the main privacy controls screen."""
        # Clear background
        screen.fill((40, 45, 55))
        
        # Title
        title_font = pygame.font.SysFont('Consolas', int(h * 0.055), bold=True)
        title_text = title_font.render("PRIVACY CONTROLS", True, (220, 240, 255))
        title_x = w // 2 - title_text.get_width() // 2
        title_y = int(h * 0.08)
        screen.blit(title_text, (title_x, title_y))
        
        # Subtitle
        subtitle_font = pygame.font.SysFont('Consolas', int(h * 0.025))
        subtitle_text = subtitle_font.render("Game Run Logger Configuration & Data Management", True, (180, 200, 220))
        subtitle_x = w // 2 - subtitle_text.get_width() // 2
        subtitle_y = title_y + title_text.get_height() + 8
        screen.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # Current status section
        current_level = self.get_current_logging_level()
        status_y = subtitle_y + 40
        
        status_font = pygame.font.SysFont('Consolas', int(h * 0.03), bold=True)
        
        # Convert level int to name
        level_names = {
            LoggingLevel.DISABLED: "Disabled",
            LoggingLevel.MINIMAL: "Minimal", 
            LoggingLevel.STANDARD: "Standard",
            LoggingLevel.VERBOSE: "Verbose",
            LoggingLevel.DEBUG: "Debug"
        }
        level_name = level_names.get(current_level, "Unknown")
        status_text = f"Current Setting: {level_name}"
        
        # Color-code the status
        if current_level == LoggingLevel.DISABLED:
            status_color = (100, 255, 100)  # Green for private
        elif current_level in [LoggingLevel.MINIMAL, LoggingLevel.STANDARD]:
            status_color = (255, 255, 100)  # Yellow for balanced
        else:
            status_color = (255, 150, 100)  # Orange for detailed
        
        status_surface = status_font.render(status_text, True, status_color)
        status_x = w // 2 - status_surface.get_width() // 2
        screen.blit(status_surface, (status_x, status_y))
        
        # First-time information (if applicable)
        content_start_y = status_y + 50
        if self.show_first_time_info:
            content_start_y = self._draw_first_time_info(screen, w, h, content_start_y)
        
        # Data summary section (if data exists)
        if self.user_data_summary and self.user_data_summary.get('session_count', 0) > 0:
            self._draw_data_summary(screen, w, h, content_start_y)
            content_start_y += 120
        
        # Logging level selection
        self._draw_logging_level_selection(screen, w, h, content_start_y)
        
        # Action buttons
        self._draw_action_buttons(screen, w, h)
    
    def _draw_data_summary(self, screen: pygame.Surface, w: int, h: int, start_y: int) -> None:
        """Draw current data summary information."""
        if not self.user_data_summary:
            return
        
        # Data summary header
        header_font = pygame.font.SysFont('Consolas', int(h * 0.028), bold=True)
        header_text = header_font.render("Current Data Summary:", True, (200, 220, 240))
        header_x = w // 2 - header_text.get_width() // 2
        screen.blit(header_text, (header_x, start_y))
        
        # Summary details
        detail_font = pygame.font.SysFont('Consolas', int(h * 0.022))
        details = [
            f"Sessions logged: {self.user_data_summary.get('session_count', 0)}",
            f"Disk usage: {self.user_data_summary.get('disk_usage_mb', 0):.1f} MB",
            f"Data retention: {self.user_data_summary.get('retention_days', 90)} days"
        ]
        
        for i, detail in enumerate(details):
            detail_surface = detail_font.render(detail, True, (180, 200, 220))
            detail_x = w // 2 - detail_surface.get_width() // 2
            detail_y = start_y + 35 + (i * 25)
            screen.blit(detail_surface, (detail_x, detail_y))
    
    def _draw_first_time_info(self, screen: pygame.Surface, w: int, h: int, start_y: int) -> int:
        """Draw first-time setup information and return the next y position."""
        # Info box background
        box_width = int(w * 0.8)
        box_height = int(h * 0.2)
        box_x = w // 2 - box_width // 2
        box_y = start_y
        
        # Draw info box with border
        pygame.draw.rect(screen, (50, 70, 100), pygame.Rect(box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (150, 200, 255), pygame.Rect(box_x, box_y, box_width, box_height), 2)
        
        # Title
        title_font = pygame.font.SysFont('Consolas', int(h * 0.025), bold=True)
        title_text = title_font.render("Welcome to Privacy Controls", True, (200, 220, 255))
        title_x = w // 2 - title_text.get_width() // 2
        title_y = box_y + 15
        screen.blit(title_text, (title_x, title_y))
        
        # Information text
        info_font = pygame.font.SysFont('Consolas', int(h * 0.02))
        info_lines = [
            "P(Doom) respects your privacy. All logging is disabled by default.",
            "Choose your preferred level below - you can change this anytime.",
            "Data is stored locally only and never shared without your consent."
        ]
        
        for i, line in enumerate(info_lines):
            line_surface = info_font.render(line, True, (180, 200, 220))
            line_x = w // 2 - line_surface.get_width() // 2
            line_y = title_y + 35 + (i * 25)
            screen.blit(line_surface, (line_x, line_y))
        
        return box_y + box_height + 20
    
    def _draw_logging_level_selection(self, screen: pygame.Surface, w: int, h: int, start_y: int) -> None:
        """Draw logging level selection dropdown."""
        # Section header
        header_font = pygame.font.SysFont('Consolas', int(h * 0.028), bold=True)
        header_text = header_font.render("Select Logging Level:", True, (200, 220, 240))
        header_x = w // 2 - header_text.get_width() // 2
        screen.blit(header_text, (header_x, start_y))
        
        # Logging level options
        levels = self.get_logging_level_options()
        current_level = self.get_current_logging_level()
        
        button_width = int(w * 0.6)
        button_height = int(h * 0.05)
        level_start_y = start_y + 40
        
        for i, (level, name, description) in enumerate(levels):
            button_y = level_start_y + (i * (button_height + 5))
            button_x = w // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Determine button state
            if i == self.selected_item and self.current_state == PrivacyUIState.MAIN:
                button_state = ButtonState.FOCUSED
            elif level == current_level:
                button_state = ButtonState.PRESSED  # Use pressed state for selected level
            else:
                button_state = ButtonState.NORMAL
            
            # Button text
            button_text = f"{name}: {description}"
            
            # Draw button
            visual_feedback.draw_button(
                screen, button_rect, button_text, button_state
            )
    
    def _draw_action_buttons(self, screen: pygame.Surface, w: int, h: int) -> None:
        """Draw action buttons (Delete Data, Back)."""
        button_width = int(w * 0.25)
        button_height = int(h * 0.06)
        button_y = int(h * 0.85)
        
        # Delete Data button
        delete_x = w // 2 - button_width - 20
        delete_rect = pygame.Rect(delete_x, button_y, button_width, button_height)
        
        delete_state = ButtonState.FOCUSED if self.selected_item == 5 else ButtonState.NORMAL
        if self.user_data_summary and self.user_data_summary.get('session_count', 0) > 0:
            delete_text = "Delete All Data"
        else:
            delete_text = "No Data to Delete"
            delete_state = ButtonState.DISABLED
        
        visual_feedback.draw_button(
            screen, delete_rect, delete_text, delete_state
        )
        
        # Back button
        back_x = w // 2 + 20
        back_rect = pygame.Rect(back_x, button_y, button_width, button_height)
        
        back_state = ButtonState.FOCUSED if self.selected_item == 6 else ButtonState.NORMAL
        visual_feedback.draw_button(
            screen, back_rect, "Back to Settings", back_state
        )
    
    def draw_delete_confirmation(self, screen: pygame.Surface, w: int, h: int) -> None:
        """Draw delete confirmation dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((w, h))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = int(w * 0.6)
        dialog_height = int(h * 0.4)
        dialog_x = w // 2 - dialog_width // 2
        dialog_y = h // 2 - dialog_height // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        pygame.draw.rect(screen, (60, 65, 75), dialog_rect)
        pygame.draw.rect(screen, (200, 220, 240), dialog_rect, 3)
        
        # Warning title
        title_font = pygame.font.SysFont('Consolas', int(h * 0.04), bold=True)
        title_text = title_font.render("DELETE ALL DATA", True, (255, 100, 100))
        title_x = dialog_x + dialog_width // 2 - title_text.get_width() // 2
        title_y = dialog_y + 20
        screen.blit(title_text, (title_x, title_y))
        
        # Warning message
        msg_font = pygame.font.SysFont('Consolas', int(h * 0.025))
        messages = [
            "This will permanently delete all collected game data.",
            "This action cannot be undone.",
            "",
            "Are you sure you want to proceed?"
        ]
        
        for i, msg in enumerate(messages):
            if msg:  # Skip empty lines
                msg_surface = msg_font.render(msg, True, (200, 220, 240))
                msg_x = dialog_x + dialog_width // 2 - msg_surface.get_width() // 2
                msg_y = title_y + 60 + (i * 30)
                screen.blit(msg_surface, (msg_x, msg_y))
        
        # Confirmation buttons
        button_width = 120
        button_height = 40
        button_y = dialog_y + dialog_height - 60
        
        # Delete button
        delete_x = dialog_x + dialog_width // 2 - button_width - 10
        delete_rect = pygame.Rect(delete_x, button_y, button_width, button_height)
        delete_state = ButtonState.FOCUSED if self.selected_item == 0 else ButtonState.NORMAL
        visual_feedback.draw_button(
            screen, delete_rect, "DELETE", delete_state
        )
        
        # Cancel button
        cancel_x = dialog_x + dialog_width // 2 + 10
        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        cancel_state = ButtonState.FOCUSED if self.selected_item == 1 else ButtonState.NORMAL
        visual_feedback.draw_button(
            screen, cancel_rect, "Cancel", cancel_state
        )
    
    def handle_mouse_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle mouse clicks and return action if any."""
        mx, my = mouse_pos
        
        if self.current_state == PrivacyUIState.DELETE_CONFIRM:
            return self._handle_delete_confirm_click(mx, my, w, h)
        else:
            return self._handle_main_screen_click(mx, my, w, h)
    
    def _handle_main_screen_click(self, mx: int, my: int, w: int, h: int) -> Optional[str]:
        """Handle clicks on main screen."""
        # Check logging level buttons
        levels = self.get_logging_level_options()
        button_width = int(w * 0.6)
        button_height = int(h * 0.05)
        level_start_y = int(h * 0.45)  # Approximate start position
        
        for i, (level, _name, _description) in enumerate(levels):
            button_y = level_start_y + (i * (button_height + 5))
            button_x = w // 2 - button_width // 2
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(mx, my):
                self.selected_item = i
                if self.set_logging_level(level):
                    return "level_changed"
        
        # Check action buttons
        button_width = int(w * 0.25)
        button_height = int(h * 0.06)
        button_y = int(h * 0.85)
        
        # Delete button
        delete_x = w // 2 - button_width - 20
        delete_rect = pygame.Rect(delete_x, button_y, button_width, button_height)
        if delete_rect.collidepoint(mx, my):
            if self.user_data_summary and self.user_data_summary.get('session_count', 0) > 0:
                self.current_state = PrivacyUIState.DELETE_CONFIRM
                self.selected_item = 1  # Default to Cancel
                return "delete_prompt"
        
        # Back button
        back_x = w // 2 + 20
        back_rect = pygame.Rect(back_x, button_y, button_width, button_height)
        if back_rect.collidepoint(mx, my):
            return "back"
        
        return None
    
    def _handle_delete_confirm_click(self, mx: int, my: int, w: int, h: int) -> Optional[str]:
        """Handle clicks on delete confirmation dialog."""
        dialog_width = int(w * 0.6)
        dialog_height = int(h * 0.4)
        dialog_x = w // 2 - dialog_width // 2
        dialog_y = h // 2 - dialog_height // 2
        
        button_width = 120
        button_height = 40
        button_y = dialog_y + dialog_height - 60
        
        # Delete button
        delete_x = dialog_x + dialog_width // 2 - button_width - 10
        delete_rect = pygame.Rect(delete_x, button_y, button_width, button_height)
        if delete_rect.collidepoint(mx, my):
            if self.delete_all_data():
                self.current_state = PrivacyUIState.MAIN
                return "data_deleted"
        
        # Cancel button
        cancel_x = dialog_x + dialog_width // 2 + 10
        cancel_rect = pygame.Rect(cancel_x, button_y, button_width, button_height)
        if cancel_rect.collidepoint(mx, my):
            self.current_state = PrivacyUIState.MAIN
            return "delete_cancelled"
        
        return None
    
    def handle_key_press(self, key: int) -> Optional[str]:
        """Handle keyboard input and return action if any."""
        if self.current_state == PrivacyUIState.DELETE_CONFIRM:
            return self._handle_delete_confirm_keys(key)
        else:
            return self._handle_main_screen_keys(key)
    
    def _handle_main_screen_keys(self, key: int) -> Optional[str]:
        """Handle keyboard input on main screen."""
        if key == pygame.K_UP:
            self.selected_item = max(0, self.selected_item - 1)
        elif key == pygame.K_DOWN:
            max_items = len(self.get_logging_level_options()) + 2  # levels + delete + back
            self.selected_item = min(max_items - 1, self.selected_item + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            return self._handle_main_screen_action()
        elif key == pygame.K_ESCAPE:
            return "back"
        
        return None
    
    def _handle_delete_confirm_keys(self, key: int) -> Optional[str]:
        """Handle keyboard input on delete confirmation."""
        if key == pygame.K_LEFT or key == pygame.K_RIGHT:
            self.selected_item = 1 - self.selected_item  # Toggle between 0 and 1
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.selected_item == 0:  # Delete
                if self.delete_all_data():
                    self.current_state = PrivacyUIState.MAIN
                    return "data_deleted"
            else:  # Cancel
                self.current_state = PrivacyUIState.MAIN
                return "delete_cancelled"
        elif key == pygame.K_ESCAPE:
            self.current_state = PrivacyUIState.MAIN
            return "delete_cancelled"
        
        return None
    
    def _handle_main_screen_action(self) -> Optional[str]:
        """Handle action selection on main screen."""
        levels = self.get_logging_level_options()
        
        if self.selected_item < len(levels):
            # Logging level selection
            level, _name, _description = levels[self.selected_item]
            if self.set_logging_level(level):
                return "level_changed"
        elif self.selected_item == len(levels):
            # Delete data
            if self.user_data_summary and self.user_data_summary.get('session_count', 0) > 0:
                self.current_state = PrivacyUIState.DELETE_CONFIRM
                self.selected_item = 1  # Default to Cancel
                return "delete_prompt"
        elif self.selected_item == len(levels) + 1:
            # Back
            return "back"
        
        return None
    
    def draw(self, screen: pygame.Surface, w: int, h: int) -> None:
        """Main draw method - dispatches to appropriate screen."""
        if self.current_state == PrivacyUIState.DELETE_CONFIRM:
            self.draw_main_screen(screen, w, h)  # Draw main screen first
            self.draw_delete_confirmation(screen, w, h)  # Then overlay dialog
        else:
            self.draw_main_screen(screen, w, h)
    
    def reset(self) -> None:
        """Reset to initial state."""
        self.current_state = PrivacyUIState.MAIN
        self.selected_item = 0
        self._refresh_logger_data()


# Global instance for use throughout the application
privacy_controls = PrivacyControls()

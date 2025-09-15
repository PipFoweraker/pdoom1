"""
Modular Menu Components
Reusable UI components for building dynamic, responsive menus.
Replaces hardcoded positioning with flexible layout management.
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class LayoutConfig:
    """Configuration for dynamic layout calculations"""
    screen_width: int
    screen_height: int
    margin_factor: float = 0.05  # Percentage of screen for margins
    spacing_factor: float = 0.02  # Percentage of screen for spacing between elements
    
    @property
    def margin(self) -> int:
        return int(self.screen_height * self.margin_factor)
    
    @property
    def spacing(self) -> int:
        return int(self.screen_height * self.spacing_factor)
    
    @property
    def content_width(self) -> int:
        return self.screen_width - (2 * self.margin)
    
    @property
    def content_height(self) -> int:
        return self.screen_height - (2 * self.margin)


@dataclass
class MenuButton:
    """Represents a menu button with dynamic positioning"""
    text: str
    index: int
    selected: bool = False
    enabled: bool = True
    rect: Optional[pygame.Rect] = None
    
    def get_colors(self) -> Dict[str, Tuple[int, int, int]]:
        """Get button colors based on state"""
        if not self.enabled:
            return {
                'bg': (40, 40, 40),
                'border': (80, 80, 80),
                'text': (120, 120, 120)
            }
        elif self.selected:
            return {
                'bg': (70, 130, 180),
                'border': (100, 200, 255),
                'text': (255, 255, 255)
            }
        else:
            return {
                'bg': (60, 60, 100),
                'border': (180, 180, 180),
                'text': (180, 180, 180)
            }


class MenuLayoutManager:
    """Manages dynamic layout for menu components"""
    
    def __init__(self, layout_config: LayoutConfig):
        self.config = layout_config
        self.current_y = layout_config.margin
        
    def reset_position(self):
        """Reset layout position to top"""
        self.current_y = self.config.margin
        
    def reserve_space(self, height: int) -> int:
        """Reserve vertical space and return the starting Y position"""
        start_y = self.current_y
        self.current_y += height + self.config.spacing
        return start_y
        
    def center_rect(self, width: int, height: int) -> pygame.Rect:
        """Create a centered rectangle with given dimensions"""
        x = (self.config.screen_width - width) // 2
        y = self.reserve_space(height)
        return pygame.Rect(x, y, width, height)
        
    def get_button_layout(self, button_count: int, button_height: int) -> List[pygame.Rect]:
        """Calculate layout for a series of buttons"""
        button_width = int(self.config.screen_width * 0.35)
        buttons = []
        
        for i in range(button_count):
            rect = self.center_rect(button_width, button_height)
            buttons.append(rect)
            
        return buttons


class EndGameMenuRenderer:
    """Renders end game menu components with dynamic layout"""
    
    def __init__(self, layout_config: LayoutConfig):
        self.config = layout_config
        self.layout = MenuLayoutManager(layout_config)
        
        # Dynamic font sizes based on screen height
        self.fonts = {
            'title': pygame.font.SysFont('Consolas', int(layout_config.screen_height * 0.05), bold=True),
            'subtitle': pygame.font.SysFont('Consolas', int(layout_config.screen_height * 0.035)),
            'stats': pygame.font.SysFont('Consolas', int(layout_config.screen_height * 0.025)),
            'menu': pygame.font.SysFont('Consolas', int(layout_config.screen_height * 0.03), bold=True),
            'small': pygame.font.SysFont('Consolas', int(layout_config.screen_height * 0.02)),
            'celebration': pygame.font.SysFont('Consolas', int(layout_config.screen_height * 0.04), bold=True)
        }
        
        # Color palette
        self.colors = {
            'title': (255, 100, 100),
            'subtitle': (255, 220, 220),
            'stats': (240, 255, 255),
            'celebration': (255, 255, 100),
            'celebration_glow': (255, 200, 0),
            'stats_box_bg': (40, 40, 70),
            'stats_box_border': (130, 190, 255),
            'stats_box_celebration_bg': (60, 80, 40),
            'stats_box_celebration_border': (150, 255, 100),
            'analysis_bg': (50, 30, 30),
            'analysis_border': (200, 100, 100),
            'analysis_text': (255, 200, 200),
            'analysis_content': (255, 220, 220),
            'legacy_bg': (30, 50, 30),
            'legacy_border': (100, 200, 100),
            'legacy_text': (200, 255, 200),
            'legacy_content': (220, 255, 220),
            'leaderboard_bg': (30, 30, 60),
            'leaderboard_celebration_bg': (30, 60, 30),
            'leaderboard_border': (100, 150, 255),
            'leaderboard_celebration_border': (100, 255, 100),
            'instructions': (200, 200, 200)
        }
    
    def render_title_section(self, surface: pygame.Surface, game_state: Any) -> None:
        """Render the title and scenario description"""
        self.layout.reset_position()
        
        # Main title
        if game_state.end_game_scenario:
            title_text = game_state.end_game_scenario.title
        else:
            title_text = "GAME OVER"
            
        title_surface = self.fonts['title'].render(title_text, True, self.colors['title'])
        title_height = title_surface.get_height()
        title_y = self.layout.reserve_space(title_height)
        title_x = (self.config.screen_width - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, title_y))
        
        # Scenario description or fallback message
        if game_state.end_game_scenario:
            description_lines = self._wrap_text(
                game_state.end_game_scenario.description, 
                self.fonts['subtitle'], 
                int(self.config.content_width * 0.8)
            )
            for line in description_lines[:4]:  # Limit to 4 lines
                desc_surface = self.fonts['subtitle'].render(line, True, self.colors['subtitle'])
                desc_height = desc_surface.get_height()
                desc_y = self.layout.reserve_space(desc_height)
                desc_x = (self.config.screen_width - desc_surface.get_width()) // 2
                surface.blit(desc_surface, (desc_x, desc_y))
        else:
            # Fallback message
            end_message = game_state.messages[-1] if game_state.messages else "Game ended"
            subtitle_surface = self.fonts['subtitle'].render(end_message, True, self.colors['subtitle'])
            subtitle_height = subtitle_surface.get_height()
            subtitle_y = self.layout.reserve_space(subtitle_height)
            subtitle_x = (self.config.screen_width - subtitle_surface.get_width()) // 2
            surface.blit(subtitle_surface, (subtitle_x, subtitle_y))
    
    def render_celebration_section(self, surface: pygame.Surface, is_new_record: bool, current_rank: Optional[int]) -> None:
        """Render celebration section for new records"""
        if not (is_new_record and current_rank == 1):
            return
            
        celebration_text = "NEW HIGH SCORE!"
        celebration_surface = self.fonts['celebration'].render(celebration_text, True, self.colors['celebration'])
        glow_surface = self.fonts['celebration'].render(celebration_text, True, self.colors['celebration_glow'])
        
        celebration_height = celebration_surface.get_height()
        celebration_y = self.layout.reserve_space(celebration_height)
        celebration_x = (self.config.screen_width - celebration_surface.get_width()) // 2
        
        # Glow effect
        surface.blit(glow_surface, (celebration_x + 2, celebration_y + 2))
        surface.blit(celebration_surface, (celebration_x, celebration_y))
    
    def render_stats_section(self, surface: pygame.Surface, game_state: Any, current_rank: Optional[int], is_new_record: bool) -> None:
        """Render game statistics in a box"""
        # Box dimensions
        box_width = int(self.config.content_width * 0.67)
        box_height = int(self.config.screen_height * 0.24)
        box_rect = self.layout.center_rect(box_width, box_height)
        
        # Box styling
        box_color = self.colors['stats_box_celebration_bg' if is_new_record else 'stats_box_bg']
        border_color = self.colors['stats_box_celebration_border' if is_new_record else 'stats_box_border']
        
        pygame.draw.rect(surface, box_color, box_rect, border_radius=12)
        pygame.draw.rect(surface, border_color, box_rect, width=3, border_radius=12)
        
        # Statistics content
        stats_lines = [
            f"Lab: {game_state.lab_name}",
            f"Survived {game_state.turn} turns",
            f"Final Staff: {game_state.staff} researchers",
            f"Final Money: ${game_state.money:,}",
            f"Final Reputation: {game_state.reputation}",
            f"Final p(Doom): {game_state.doom}%"
        ]
        
        # Add rank information
        if current_rank:
            rank_suffix = {1: "st", 2: "nd", 3: "rd"}.get(current_rank, "th")
            rank_line = f"Leaderboard Rank: #{current_rank}{rank_suffix} for seed '{game_state.seed}'"
            stats_lines.append(rank_line)
        else:
            stats_lines.append(f"Seed: '{game_state.seed}'")
        
        # Add high score comparison
        if hasattr(game_state, 'highscore') and game_state.highscore > 0:
            if game_state.turn > game_state.highscore:
                stats_lines.append(f"Previous Best: {game_state.highscore} turns (BEATEN!)")
            else:
                stats_lines.append(f"Personal Best: {game_state.highscore} turns")
        
        # Render stats text
        line_height = int(self.config.screen_height * 0.025)
        for i, line in enumerate(stats_lines):
            stats_surface = self.fonts['stats'].render(line, True, self.colors['stats'])
            surface.blit(stats_surface, (box_rect.x + 20, box_rect.y + 15 + i * line_height))
    
    def render_scenario_analysis(self, surface: pygame.Surface, game_state: Any) -> None:
        """Render cause analysis and legacy sections if available"""
        if not game_state.end_game_scenario:
            return
            
        # Cause Analysis
        if game_state.end_game_scenario.cause_analysis:
            analysis_width = int(self.config.content_width * 0.67)
            analysis_height = int(self.config.screen_height * 0.12)
            analysis_rect = self.layout.center_rect(analysis_width, analysis_height)
            
            pygame.draw.rect(surface, self.colors['analysis_bg'], analysis_rect, border_radius=8)
            pygame.draw.rect(surface, self.colors['analysis_border'], analysis_rect, width=2, border_radius=8)
            
            # Analysis title
            title_surface = self.fonts['small'].render("What Went Wrong:", True, self.colors['analysis_text'])
            surface.blit(title_surface, (analysis_rect.x + 15, analysis_rect.y + 8))
            
            # Analysis text
            analysis_lines = self._wrap_text(
                game_state.end_game_scenario.cause_analysis, 
                self.fonts['small'], 
                analysis_width - 30
            )
            for i, line in enumerate(analysis_lines[:3]):
                line_surface = self.fonts['small'].render(line, True, self.colors['analysis_content'])
                surface.blit(line_surface, (analysis_rect.x + 15, analysis_rect.y + 25 + i * 16))
        
        # Legacy Note
        if game_state.end_game_scenario.legacy_note:
            legacy_width = int(self.config.content_width * 0.67)
            legacy_height = int(self.config.screen_height * 0.08)
            legacy_rect = self.layout.center_rect(legacy_width, legacy_height)
            
            pygame.draw.rect(surface, self.colors['legacy_bg'], legacy_rect, border_radius=8)
            pygame.draw.rect(surface, self.colors['legacy_border'], legacy_rect, width=2, border_radius=8)
            
            # Legacy title
            title_surface = self.fonts['small'].render("Your Legacy:", True, self.colors['legacy_text'])
            surface.blit(title_surface, (legacy_rect.x + 15, legacy_rect.y + 8))
            
            # Legacy text
            legacy_lines = self._wrap_text(
                game_state.end_game_scenario.legacy_note, 
                self.fonts['small'], 
                legacy_width - 30
            )
            for i, line in enumerate(legacy_lines[:2]):
                line_surface = self.fonts['small'].render(line, True, self.colors['legacy_content'])
                surface.blit(line_surface, (legacy_rect.x + 15, legacy_rect.y + 25 + i * 16))
    
    def render_menu_buttons(self, surface: pygame.Surface, buttons: List[MenuButton]) -> None:
        """Render menu buttons with dynamic layout"""
        button_height = int(self.config.screen_height * 0.055)
        button_rects = self.layout.get_button_layout(len(buttons), button_height)
        
        for i, button in enumerate(buttons):
            if i < len(button_rects):
                button.rect = button_rects[i]
                colors = button.get_colors()
                
                # Draw button background and border
                pygame.draw.rect(surface, colors['bg'], button.rect, border_radius=8)
                pygame.draw.rect(surface, colors['border'], button.rect, width=3 if button.selected else 2, border_radius=8)
                
                # Draw button text
                text_surface = self.fonts['menu'].render(button.text, True, colors['text'])
                text_rect = text_surface.get_rect(center=button.rect.center)
                surface.blit(text_surface, text_rect)
    
    def render_instructions(self, surface: pygame.Surface) -> None:
        """Render keyboard instructions at bottom"""
        instruction_text = "Use arrow keys to navigate, Enter to select, Escape for Main Menu"
        instruction_surface = self.fonts['small'].render(instruction_text, True, self.colors['instructions'])
        
        # Position at bottom with margin
        instruction_y = self.config.screen_height - self.config.margin - instruction_surface.get_height()
        instruction_x = (self.config.screen_width - instruction_surface.get_width()) // 2
        surface.blit(instruction_surface, (instruction_x, instruction_y))
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines

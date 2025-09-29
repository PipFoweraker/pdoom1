"""
Game screen rendering for P(Doom).

Contains the main in-game UI rendering functionality with new 3-column layout.
Implements the requested design: repeating actions left, staff middle, strategic actions right.
"""

import pygame
import sys
import os
from typing import Any, Dict

# Import visual feedback system (existing)
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle

# Import new components
from ...modular_components.colours import *
from ..layouts import three_column_layout
# from ...modular_components.typography import get_font_manager  # Temporarily disabled

# Temporary fallback font manager
class TempFontManager:
    def get_font(self, size, bold=False):
        try:
            import pygame
            return pygame.font.Font(None, size)
        except:
            return None
    def get_title_font(self, h): return self.get_font(int(h * 0.045))
    def get_big_font(self, h): return self.get_font(int(h * 0.033)) 
    def get_normal_font(self, h): return self.get_font(int(h * 0.025))
    def get_small_font(self, h): return self.get_font(int(h * 0.02))

def get_font_manager():
    return TempFontManager()
from ..layouts.three_column import ThreeColumnLayout

# Global layout manager
three_column_layout = ThreeColumnLayout()

def should_show_ui_element(game_state: Any, element_id: str) -> bool:
    """
    Determine if a UI element should be shown based on game state and tutorial progress.
    
    Args:
        game_state: Current game state
        element_id: ID of the UI element to check
        
    Returns:
        bool: True if the element should be shown
    """
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import should_show_ui_element as legacy_should_show
    return legacy_should_show(game_state, element_id)


def draw_resource_header(screen: pygame.Surface, game_state: Any, w: int, h: int,
                        fonts: Dict[str, pygame.font.Font]) -> None:
    """Draw the resource header at the top of the screen."""
    # Get fonts
    title_font = fonts['title']
    big_font = fonts['big']
    fonts['font']
    small_font = fonts['small']
    
    # Title - retro neon style
    title = title_font.render("P(DOOM): BUREAUCRACY STRATEGY", True, TITLE_COLOUR)
    screen.blit(title, (int(w*0.04), int(h*0.03)))
    
    # Resources (top bar) - with retro styling and improved layout
    current_x = int(w*0.04)
    y_pos = int(h*0.11)
    spacing = int(w*0.12)  # Fixed spacing for better alignment
    
    # Money (always show)
    money_text = big_font.render(f"${game_state.money}", True, MONEY_COLOUR)
    screen.blit(money_text, (current_x, y_pos))
    current_x += spacing
    
    # Staff (always show)
    staff_text = big_font.render(f"Staff: {game_state.staff}", True, STAFF_COLOUR)
    screen.blit(staff_text, (current_x, y_pos))
    current_x += spacing
    
    # Reputation (always show)
    reputation_text = big_font.render(f"Rep: {game_state.reputation}", True, REPUTATION_COLOUR)
    screen.blit(reputation_text, (current_x, y_pos))
    current_x += spacing
    
    # Action Points with glow effect
    ap_color = ACTION_POINTS_COLOUR
    if hasattr(game_state, 'ap_glow_timer') and game_state.ap_glow_timer > 0:
        glow_intensity = int(127 * (game_state.ap_glow_timer / 30))
        ap_color = (min(255, 255 + glow_intensity), min(255, 255 + glow_intensity), min(255, 100 + glow_intensity))
    
    ap_text = big_font.render(f"AP: {game_state.action_points}/{game_state.max_action_points}", True, ap_color)
    screen.blit(ap_text, (current_x, y_pos))
    current_x += spacing
    
    # Doom
    doom_text = big_font.render(f"p(Doom): {game_state.doom}%", True, DOOM_COLOUR)
    screen.blit(doom_text, (current_x, y_pos))
    
    # Second line of resources
    current_x = int(w*0.04)
    y_pos_2 = int(h*0.135)
    
    compute_text = big_font.render(f"Compute: {game_state.compute}", True, COMPUTE_COLOUR)
    screen.blit(compute_text, (current_x, y_pos_2))
    current_x += spacing
    
    research_text = big_font.render(f"Research: {game_state.research_progress}/100", True, RESEARCH_COLOUR)
    screen.blit(research_text, (current_x, y_pos_2))
    current_x += spacing
    
    papers_text = big_font.render(f"Papers: {game_state.papers_published}", True, PAPERS_COLOUR)
    screen.blit(papers_text, (current_x, y_pos_2))
    
    # Turn and seed info (top right)
    screen.blit(small_font.render(f"Turn: {game_state.turn}", True, TEXT_COLOUR), (int(w*0.88), int(h*0.03)))
    screen.blit(small_font.render(f"Seed: {game_state.seed}", True, (140, 200, 160)), (int(w*0.75), int(h*0.03)))
    
    # Doom bar (under resources)
    doom_bar_x, doom_bar_y = int(w*0.04), int(h*0.17)
    doom_bar_width, doom_bar_height = int(w*0.6), int(h*0.015)
    pygame.draw.rect(screen, (70, 50, 50), (doom_bar_x, doom_bar_y, doom_bar_width, doom_bar_height))
    filled = int(doom_bar_width * (game_state.doom / game_state.max_doom))
    pygame.draw.rect(screen, DOOM_COLOUR, (doom_bar_x, doom_bar_y, filled, doom_bar_height))


def render_game_screen(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """
    Render the main game screen using the new 3-column layout.
    
    Args:
        screen: The pygame surface to render on
        game_state: Current game state object
        w: Screen width
        h: Screen height
    """
    # Clear background with retro dark theme
    screen.fill(DARK_BG)
    
    # Initialize font manager
    font_manager = get_font_manager()
    
    # Get fonts from font manager
    fonts = {
        'title': font_manager.get_font('title', h),
        'big': font_manager.get_font('big', h),
        'font': font_manager.get_font('normal', h),
        'small': font_manager.get_font('small', h)
    }
    
    # Calculate 3-column layout
    layout_rects = three_column_layout.calculate_layout(w, h)
    
    # Draw resource header
    draw_resource_header(screen, game_state, w, h, fonts)
    
    # Draw column borders and headers
    three_column_layout.draw_column_borders(screen, layout_rects)
    three_column_layout.draw_column_headers(screen, layout_rects, fonts['font'])
    
    # Filter and categorize actions
    categorized_actions = three_column_layout.filter_actions_by_column(game_state.actions, game_state)
    
    # Draw left column (repeating actions)
    left_button_rects = three_column_layout.draw_repeating_actions(
        screen, categorized_actions['repeating'], layout_rects['left_column'], 
        game_state, fonts
    )
    
    # Draw middle column (staff/employees)
    three_column_layout.draw_middle_column(
        screen, layout_rects['middle_column'], game_state, fonts
    )
    
    # Draw right column (strategic actions)
    right_button_rects = three_column_layout.draw_strategic_actions(
        screen, categorized_actions['oneoff'], layout_rects['right_column'],
        game_state, fonts
    )
    
    # Combine button rects for click handling
    all_button_rects = left_button_rects + right_button_rects
    
    # Store button rects in game state for click handling
    game_state.three_column_button_rects = all_button_rects
    game_state.three_column_layout_rects = layout_rects
    
    # Draw context window at bottom
    draw_context_window_3column(screen, game_state, layout_rects['context_window'], fonts)
    
    # Draw end turn button (bottom right of context area)
    draw_end_turn_button_3column(screen, game_state, layout_rects['context_window'], fonts)
    
    # Draw activity log (bottom left of context area) 
    draw_activity_log_3column(screen, game_state, layout_rects['context_window'], fonts)
    
    # Draw version footer
    draw_version_footer_3column(screen, w, h, fonts['small'])


def draw_context_window_3column(screen: pygame.Surface, game_state: Any, 
                               context_rect: pygame.Rect, fonts: Dict[str, pygame.font.Font]) -> None:
    """Draw the context window for the 3-column layout."""
    # Import context functions from legacy UI for now
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    try:
        from ui import draw_context_window, create_action_context_info, get_default_context_info
    except ImportError:
        # Fallback to simple context display if import fails
        draw_simple_context_window(screen, game_state, context_rect, fonts)
        return
    
    # Generate context info based on hover state
    context_info = None
    if hasattr(game_state, 'hovered_action_idx') and game_state.hovered_action_idx is not None:
        if game_state.hovered_action_idx < len(game_state.actions):
            action = game_state.actions[game_state.hovered_action_idx]
            context_info = create_action_context_info(action, game_state, game_state.hovered_action_idx)
    elif hasattr(game_state, 'current_context_info') and game_state.current_context_info:
        context_info = game_state.current_context_info
    else:
        context_info = get_default_context_info(game_state)
    
    # Draw context window if we have info
    if context_info:
        context_minimized = getattr(game_state, 'context_window_minimized', False)
        config = getattr(game_state, 'config', None)
        
        # Adjust context window to fit in our allocated space
        w = context_rect.width
        h = context_rect.height + context_rect.y  # Full screen height for legacy function
        
        context_window_rect, button_rect = draw_context_window(
            screen, context_info, w, h, context_minimized, config
        )
        
        # Store for click handling
        game_state.context_window_rect = context_window_rect
        game_state.context_window_button_rect = button_rect


def draw_simple_context_window(screen: pygame.Surface, game_state: Any,
                              context_rect: pygame.Rect, fonts: Dict[str, pygame.font.Font]) -> None:
    """Draw a simple fallback context window."""
    # Draw background
    pygame.draw.rect(screen, PANEL_BG, context_rect, border_radius=5)
    pygame.draw.rect(screen, BORDER_COLOR, context_rect, width=1, border_radius=5)
    
    # Default context text
    context_text = fonts['small'].render("CONTEXT: Hover over actions for details", True, NEON_GREEN)
    text_x = context_rect.x + 10
    text_y = context_rect.y + 5
    screen.blit(context_text, (text_x, text_y))


def draw_end_turn_button_3column(screen: pygame.Surface, game_state: Any,
                                context_rect: pygame.Rect, fonts: Dict[str, pygame.font.Font]) -> None:
    """Draw the end turn button in the 3-column layout."""
    from src.services.keybinding_manager import keybinding_manager
    
    # Position in bottom right of context area with proportional sizing
    button_width = int(context_rect.width * 0.2)  # 20% of context width
    button_height = int(context_rect.height * 0.4)  # 40% of context height
    margin = int(context_rect.width * 0.01)  # 1% margin
    button_x = context_rect.right - button_width - margin
    button_y = context_rect.y + margin
    
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Determine button state
    endturn_state = ButtonState.HOVER if (hasattr(game_state, 'endturn_hovered') and 
                                         game_state.endturn_hovered) else ButtonState.NORMAL
    
    # Get shortcut key
    shortcut_display = keybinding_manager.get_action_display_key("end_turn")
    
    # Custom colors for end turn button
    custom_colors = {
        ButtonState.NORMAL: {
            'bg': END_TURN_NORMAL_BG,
            'border': END_TURN_BORDER,
            'text': END_TURN_TEXT_COLOUR,
            'shadow': (60, 40, 40)
        },
        ButtonState.HOVER: {
            'bg': END_TURN_HOVER_BG,
            'border': END_TURN_BORDER,
            'text': (255, 255, 255),
            'shadow': (80, 60, 60),
            'glow': (255, 200, 200, 40)
        }
    }
    
    visual_feedback.draw_button(
        screen, button_rect, f"END TURN ({shortcut_display})", endturn_state,
        FeedbackStyle.BUTTON, custom_colors.get(endturn_state)
    )
    
    # Store rect for click handling
    game_state.endturn_rect = button_rect


def draw_activity_log_3column(screen: pygame.Surface, game_state: Any,
                             context_rect: pygame.Rect, fonts: Dict[str, pygame.font.Font]) -> None:
    """Draw a compact activity log in the 3-column layout."""
    # Position on right side of context area for better visibility
    log_width = int(context_rect.width * 0.4)  # 40% of context area width
    log_height = int(context_rect.height * 0.95)  # 95% of context area height
    margin = int(context_rect.width * 0.01)  # 1% margin
    log_x = context_rect.right - log_width - margin  # Right-aligned with proportional margin
    log_y = context_rect.y + margin
    
    # Draw compact log background
    log_rect = pygame.Rect(log_x, log_y, log_width, log_height)
    pygame.draw.rect(screen, PANEL_BG, log_rect, border_radius=5)
    pygame.draw.rect(screen, BORDER_COLOR, log_rect, width=1, border_radius=5)
    
    # Log title with proportional positioning
    title_margin = int(log_width * 0.02)  # 2% of log width
    title_y_offset = int(log_height * 0.03)  # 3% of log height
    log_title = fonts['small'].render("ACTIVITY LOG", True, NEON_GREEN)
    screen.blit(log_title, (log_x + title_margin, log_y + title_y_offset))
    
    # Show last few messages with proportional spacing
    messages = getattr(game_state, 'messages', [])
    if messages:
        line_height = int(log_height * 0.04)  # 4% of log height per line
        header_space = int(log_height * 0.08)  # 8% for header space
        max_lines = (log_height - header_space) // line_height
        start_idx = max(0, len(messages) - max_lines)
        
        # Calculate character limit based on log width
        char_limit = int(log_width * 0.12)  # Approximately 0.12 characters per pixel width
        
        for i, msg in enumerate(messages[start_idx:start_idx + max_lines]):
            if len(msg) > char_limit:
                msg = msg[:char_limit-3] + "..."
            
            msg_text = fonts['small'].render(msg, True, TEXT_COLOUR)
            screen.blit(msg_text, (log_x + title_margin, log_y + header_space + i * line_height))


def draw_version_footer_3column(screen: pygame.Surface, w: int, h: int, 
                               font: pygame.font.Font) -> None:
    """Draw version information in the bottom right corner."""
    try:
        from src.services.version import get_display_version
        version_text = get_display_version()
    except ImportError:
        version_text = "dev"
    
    # Position in bottom right corner
    margin = 10
    version_surf = font.render(version_text, True, (120, 120, 120))
    
    version_x = w - version_surf.get_width() - margin
    version_y = h - version_surf.get_height() - margin
    
    screen.blit(version_surf, (version_x, version_y))

def render_game_screen(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """
    Render the main game screen using the new 3-column layout.
    
    This is the main entry point for the new UI system. It replaces the legacy
    draw_ui function with a cleaner 3-column approach as requested.
    
    Args:
        screen: The pygame surface to render on
        game_state: Current game state object
        w: Screen width
        h: Screen height
    """
    # Clear background with retro dark theme
    screen.fill(DARK_BG)
    
    # Initialize font manager
    font_manager = get_font_manager()
    
    # Get fonts from font manager
    fonts = {
        'title': font_manager.get_font('title', h),
        'big': font_manager.get_font('big', h),
        'font': font_manager.get_font('normal', h),
        'small': font_manager.get_font('small', h)
    }
    
    # Calculate 3-column layout
    layout_rects = three_column_layout.calculate_layout(w, h)
    
    # Draw resource header
    draw_resource_header(screen, game_state, w, h, fonts)
    
    # Draw column borders and headers
    three_column_layout.draw_column_borders(screen, layout_rects)
    three_column_layout.draw_column_headers(screen, layout_rects, fonts['font'])
    
    # Filter and categorize actions
    categorized_actions = three_column_layout.filter_actions_by_column(game_state.actions, game_state)
    
    # Draw left column (repeating actions)
    left_button_rects = three_column_layout.draw_repeating_actions(
        screen, categorized_actions['repeating'], layout_rects['left_column'], 
        game_state, fonts
    )
    
    # Draw middle column (staff/employees)
    three_column_layout.draw_middle_column(
        screen, layout_rects['middle_column'], game_state, fonts
    )
    
    # Draw right column (strategic actions)
    right_button_rects = three_column_layout.draw_strategic_actions(
        screen, categorized_actions['oneoff'], layout_rects['right_column'],
        game_state, fonts
    )
    
    # Combine button rects for click handling
    all_button_rects = left_button_rects + right_button_rects
    
    # Store button rects in game state for click handling
    game_state.three_column_button_rects = all_button_rects
    game_state.three_column_layout_rects = layout_rects
    
    # Draw context window at bottom
    draw_context_window_3column(screen, game_state, layout_rects['context_window'], fonts)
    
    # Draw end turn button (bottom right of context area)
    draw_end_turn_button_3column(screen, game_state, layout_rects['context_window'], fonts)
    
    # Draw activity log (bottom left of context area) 
    draw_activity_log_3column(screen, game_state, layout_rects['context_window'], fonts)
    
    # Draw version footer
    draw_version_footer_3column(screen, w, h, fonts['small'])
    
    # Draw popup events and overlays (on top of everything)
    draw_overlays_3column(screen, game_state, w, h, fonts)


def draw_overlays_3column(screen: pygame.Surface, game_state: Any, w: int, h: int,
                         fonts: Dict[str, pygame.font.Font]) -> None:
    """Draw overlays like popup events, tutorials, etc."""
    # Import legacy overlay functions for now
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_popup_events, draw_tutorial_overlay
    
    # Draw popup events if any
    if hasattr(game_state, 'pending_popup_events') and game_state.pending_popup_events:
        popup_button_rects = draw_popup_events(screen, game_state, w, h, fonts['font'], fonts['big'])
        game_state.popup_button_rects = popup_button_rects
    
    # Draw tutorial overlay if active
    if hasattr(game_state, 'tutorial_message') and game_state.tutorial_message:
        tutorial_dismiss_rect = draw_tutorial_overlay(screen, game_state.tutorial_message, w, h)
        game_state.tutorial_dismiss_rect = tutorial_dismiss_rect
        sys.path.insert(0, parent_dir)
    
    from ui import draw_opponents_panel as legacy_draw_opponents
    legacy_draw_opponents(screen, game_state, w, h, fonts['font'], fonts['small'])


def draw_employee_blobs(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """Draw employee blobs with dynamic positioning."""
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_employee_blobs as legacy_draw_blobs
    legacy_draw_blobs(screen, game_state, w, h)


def draw_deferred_events_zone(screen: pygame.Surface, game_state: Any, w: int, h: int,
                             small_font: pygame.font.Font) -> None:
    """Draw the deferred events zone."""
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_deferred_events_zone as legacy_draw_deferred
    legacy_draw_deferred(screen, game_state, w, h, small_font)


def draw_mute_button(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """Draw the mute button."""
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_mute_button as legacy_draw_mute
    legacy_draw_mute(screen, game_state, w, h)


def draw_version_footer(screen: pygame.Surface, w: int, h: int) -> None:
    """Draw the version footer."""
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_version_footer as legacy_draw_version
    legacy_draw_version(screen, w, h)


def draw_ui_transitions(screen: pygame.Surface, game_state: Any, w: int, h: int,
                       big_font: pygame.font.Font) -> None:
    """Draw UI transition animations."""
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_ui_transitions as legacy_draw_transitions
    legacy_draw_transitions(screen, game_state, w, h, big_font)


def draw_popup_events(screen: pygame.Surface, game_state: Any, w: int, h: int,
                     font: pygame.font.Font, big_font: pygame.font.Font) -> None:
    """Draw popup events overlay."""
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from ui import draw_popup_events as legacy_draw_popup
    legacy_draw_popup(screen, game_state, w, h, font, big_font)


def render_game_screen(screen: pygame.Surface, game_state: Any, w: int, h: int) -> None:
    """
    Render the main in-game screen.
    
    This is the migrated version of the draw_ui function, maintaining exact
    behavioural compatibility while using the new component architecture.
    
    Args:
        screen: The pygame surface to render on
        game_state: Current game state object
        w: Screen width
        h: Screen height
    """
    # Initialize font manager
    font_manager = get_font_manager()
    
    # Fonts, scaled by screen size using new typography system
    title_font = font_manager.get_title_font(h)
    big_font = font_manager.get_big_font(h)
    font = font_manager.get_normal_font(h)
    small_font = font_manager.get_small_font(h)

    # Title
    title = title_font.render("P(Doom): Bureaucracy Strategy", True, TITLE_COLOUR)
    screen.blit(title, (int(w*0.04), int(h*0.03)))

    # Resources (top bar) - controlled by tutorial visibility
    if should_show_ui_element(game_state, 'money_display'):
        screen.blit(big_font.render(f"Money: ${game_state.money}", True, MONEY_COLOUR), (int(w*0.04), int(h*0.11)))
        
        # Cash flow indicator if accounting software is purchased
        if hasattr(game_state, 'accounting_software_bought') and game_state.accounting_software_bought:
            if hasattr(game_state, 'last_balance_change') and game_state.last_balance_change != 0:
                change_color = BALANCE_POSITIVE_COLOUR if game_state.last_balance_change > 0 else BALANCE_NEGATIVE_COLOUR
                change_sign = "+" if game_state.last_balance_change > 0 else ""
                change_text = f"({change_sign}${game_state.last_balance_change})"
                screen.blit(font.render(change_text, True, change_color), (int(w*0.04), int(h*0.13)))
    
    if should_show_ui_element(game_state, 'staff_display'):
        screen.blit(big_font.render(f"Staff: {game_state.staff}", True, STAFF_COLOUR), (int(w*0.21), int(h*0.11)))
    
    if should_show_ui_element(game_state, 'reputation_display'):
        screen.blit(big_font.render(f"Reputation: {game_state.reputation}", True, REPUTATION_COLOUR), (int(w*0.35), int(h*0.11)))
    
    # Action Points with glow effect
    ap_color = ACTION_POINTS_COLOUR  # Yellow base colour for AP
    if hasattr(game_state, 'ap_glow_timer') and game_state.ap_glow_timer > 0:
        # Add glow/pulse effect when AP is spent
        glow_intensity = int(127 * (game_state.ap_glow_timer / 30))  # Fade over 30 frames
        ap_color = (min(255, 255 + glow_intensity), min(255, 255 + glow_intensity), min(255, 100 + glow_intensity))
    
    screen.blit(big_font.render(f"AP: {game_state.action_points}/{game_state.max_action_points}", True, ap_color), (int(w*0.49), int(h*0.11)))
    
    screen.blit(big_font.render(f"p(Doom): {game_state.doom}/{game_state.max_doom}", True, DOOM_COLOUR), (int(w*0.62), int(h*0.11)))
    screen.blit(font.render(f"Opponent progress: {game_state.known_opp_progress if game_state.known_opp_progress is not None else '???'}/100", True, (240, 200, 160)), (int(w*0.84), int(h*0.11)))
    # Second line of resources
    screen.blit(big_font.render(f"Compute: {game_state.compute}", True, COMPUTE_COLOUR), (int(w*0.04), int(h*0.135)))
    screen.blit(big_font.render(f"Research: {game_state.research_progress}/100", True, RESEARCH_COLOUR), (int(w*0.21), int(h*0.135)))
    screen.blit(big_font.render(f"Papers: {game_state.papers_published}", True, PAPERS_COLOUR), (int(w*0.38), int(h*0.135)))
    
    # Board member and audit risk display (if applicable)
    if hasattr(game_state, 'board_members') and game_state.board_members > 0:
        screen.blit(font.render(f"Board Members: {game_state.board_members}", True, (255, 150, 150)), (int(w*0.55), int(h*0.135)))
        if hasattr(game_state, 'audit_risk_level') and game_state.audit_risk_level > 0:
            risk_color = (255, 200, 100) if game_state.audit_risk_level <= 5 else (255, 100, 100)
            screen.blit(font.render(f"Audit Risk: {game_state.audit_risk_level}", True, risk_color), (int(w*0.72), int(h*0.135)))
    
    screen.blit(small_font.render(f"Turn: {game_state.turn}", True, TEXT_COLOUR), (int(w*0.91), int(h*0.03)))
    screen.blit(small_font.render(f"Seed: {game_state.seed}", True, (140, 200, 160)), (int(w*0.77), int(h*0.03)))

    # Doom bar
    doom_bar_x, doom_bar_y = int(w*0.62), int(h*0.16)
    doom_bar_width, doom_bar_height = int(w*0.28), int(h*0.025)
    pygame.draw.rect(screen, (70, 50, 50), (doom_bar_x, doom_bar_y, doom_bar_width, doom_bar_height))
    filled = int(doom_bar_width * (game_state.doom / game_state.max_doom))
    pygame.draw.rect(screen, (255, 60, 60), (doom_bar_x, doom_bar_y, filled, doom_bar_height))

    # Opponents information panel (between resources and actions)
    # Import legacy function for now to maintain compatibility
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from ui import draw_opponents_panel
    draw_opponents_panel(screen, game_state, w, h, font, small_font)

    # Action buttons (left) - Enhanced with visual feedback
    action_rects = game_state._get_action_rects(w, h)
    for idx, rect_tuple in enumerate(action_rects):
        action = game_state.actions[idx]
        ap_cost = action.get("ap_cost", 1)
        
        # Convert tuple to pygame.Rect
        rect = pygame.Rect(rect_tuple)
        
        # Determine button state for visual feedback
        if game_state.action_points < ap_cost:
            button_state = ButtonState.DISABLED
        elif idx in game_state.selected_gameplay_actions:
            button_state = ButtonState.PRESSED
        elif hasattr(game_state, 'hovered_action_idx') and game_state.hovered_action_idx == idx:
            button_state = ButtonState.HOVER
        else:
            button_state = ButtonState.NORMAL
        
        # Use visual feedback system for consistent styling
        # Include keyboard shortcut in button text for first 9 actions
        button_text = action["name"]
        if idx < 9:  # Only first 9 actions get keyboard shortcuts (1-9 keys)
            shortcut_key = str(idx + 1)
            button_text = f"[{shortcut_key}] {action['name']}"
        
        visual_feedback.draw_button(
            screen, rect, button_text, button_state, FeedbackStyle.BUTTON
        )
        
        # Draw action usage indicators (circles for repeatables)
        if hasattr(game_state, 'selected_action_instances'):
            action_count = sum(1 for inst in game_state.selected_action_instances if inst['action_idx'] == idx)
            if action_count > 0:
                # Draw usage indicators as small circles
                indicator_size = int(min(w, h) * 0.008)  # Small circles
                indicator_color = (100, 255, 100) if button_state != ButtonState.DISABLED else (60, 120, 60)
                
                # Position indicators in top-right of button
                start_x = rect.right - (action_count * indicator_size * 2) - 5
                start_y = rect.top + 5
                
                for i in range(min(action_count, 5)):  # Max 5 indicators to avoid clutter
                    circle_x = start_x + (i * indicator_size * 2)
                    circle_y = start_y + indicator_size
                    pygame.draw.circle(screen, indicator_color, (circle_x, circle_y), indicator_size)
                    
                # If more than 5, show "+N" text
                if action_count > 5:
                    more_text = font.render(f"+{action_count-5}", True, indicator_color)
                    screen.blit(more_text, (start_x + 5 * indicator_size * 2 + 2, start_y))
        
        # Draw description text below button
        desc_color = (190, 210, 255) if game_state.action_points >= ap_cost else (140, 150, 160)
        desc_text = font.render(f"{action['desc']} (Cost: ${action['cost']}, AP: {ap_cost})", True, desc_color)
        screen.blit(desc_text, (rect.x + int(w*0.01), rect.y + int(h*0.04)))

    # Upgrades (right: purchased as icons at top right, available as buttons) - Enhanced with visual feedback
    upgrade_rects = game_state._get_upgrade_rects(w, h)
    for idx, rect_tuple in enumerate(upgrade_rects):
        # Skip None rects (unavailable upgrades)
        if rect_tuple is None:
            continue
            
        upg = game_state.upgrades[idx]
        
        # Convert tuple to pygame.Rect
        rect = pygame.Rect(rect_tuple)
        
        if upg.get("purchased", False):
            # Draw as small icon using visual feedback system
            visual_feedback.draw_icon_button(screen, rect, upg["name"][0], ButtonState.NORMAL)
        else:
            # Determine button state
            if upg['cost'] > game_state.money:
                button_state = ButtonState.DISABLED
            elif hasattr(game_state, 'hovered_upgrade_idx') and game_state.hovered_upgrade_idx == idx:
                button_state = ButtonState.HOVER
            else:
                button_state = ButtonState.NORMAL
            
            # Draw upgrade button with consistent styling
            visual_feedback.draw_button(
                screen, rect, upg["name"], button_state, FeedbackStyle.BUTTON
            )
            
            # Draw description and status
            desc_color = (200, 255, 200) if button_state != ButtonState.DISABLED else (120, 150, 120)
            desc = small_font.render(upg["desc"] + f" (Cost: ${upg['cost']})", True, desc_color)
            status = small_font.render("AVAILABLE", True, desc_color)
            screen.blit(desc, (rect.x + int(w*0.01), rect.y + int(h*0.04)))
            screen.blit(status, (rect.x + int(w*0.24), rect.y + int(h*0.04)))

    # --- Balance change display (after buying accounting software) ---
    # If accounting software was bought, show last balance change under Money
    if hasattr(game_state, "accounting_software_bought") and game_state.accounting_software_bought:
        # Show the last balance change if available
        change = getattr(game_state, "last_balance_change", 0)
        sign = "+" if change > 0 else ""
        # Render in green if positive, red if negative
        screen.blit(
            font.render(f"({sign}{change})", True, BALANCE_POSITIVE_COLOUR if change >= 0 else BALANCE_NEGATIVE_COLOUR),
            (int(w*0.18), int(h*0.135))
        )
        # Optionally, always show the "monthly costs" indicator here as well


    # Draw UI transitions (on top of everything else)
    draw_ui_transitions(screen, game_state, w, h, big_font)

    # End Turn button (bottom center) - Enhanced with visual feedback
    endturn_rect_tuple = game_state._get_endturn_rect(w, h)
    endturn_rect = pygame.Rect(endturn_rect_tuple)
    
    # Determine button state
    endturn_state = ButtonState.HOVER if hasattr(game_state, 'endturn_hovered') and game_state.endturn_hovered else ButtonState.NORMAL
    
    # Use visual feedback system with custom colours for end turn button
    if endturn_state == ButtonState.HOVER:
        custom_colors = {
            'bg': (180, 120, 120),
            'border': (210, 110, 110),
            'text': (255, 240, 240),
            'shadow': (100, 60, 60),
            'glow': (255, 200, 200, 40)
        }
    else:
        custom_colors = {
            'bg': (140, 90, 90),
            'border': (210, 110, 110),
            'text': (255, 240, 240),
            'shadow': (100, 60, 60)
        }
    
    visual_feedback.draw_button(
        screen, endturn_rect, "END TURN (Space)", endturn_state, 
        FeedbackStyle.BUTTON, custom_colors
    )


    # Messages log (bottom left) - Enhanced with scrollable history and minimize option
    # Use current position (including any drag offset)
    if hasattr(game_state, '_get_activity_log_current_position'):
        log_x, log_y = game_state._get_activity_log_current_position(w, h)
    else:
        # Improved fallback positioning with better alignment
        log_x, log_y = int(w*0.04), int(h*0.74)  # Keep existing position for compatibility

    
    # Check if activity log is minimized (only available with compact activity display upgrade)
    if (hasattr(game_state, 'activity_log_minimized') and 
        game_state.activity_log_minimized and 
        "compact_activity_display" in game_state.upgrade_effects):
        
        # Show minimize header bar only
        header_height = int(h * 0.03)
        log_width = int(w * 0.44)
        
        # Header background
        pygame.draw.rect(screen, (50, 50, 60), (log_x, log_y, log_width, header_height))
        pygame.draw.rect(screen, (120, 120, 140), (log_x, log_y, log_width, header_height), 1)
        
        # Title and expand button
        header_text = small_font.render("Activity Log (Click to expand)", True, (180, 180, 200))
        screen.blit(header_text, (log_x + 8, log_y + 5))
        
        # Expand button (+ symbol)
        expand_x = log_x + log_width - 20
        expand_y = log_y + header_height // 2
        pygame.draw.line(screen, (180, 255, 180), (expand_x - 5, expand_y), (expand_x + 5, expand_y), 2)
        pygame.draw.line(screen, (180, 255, 180), (expand_x, expand_y - 5), (expand_x, expand_y + 5), 2)
        
    elif "compact_activity_display" in game_state.upgrade_effects:
        # Enhanced activity log with scrolling and additional features
        log_width = int(w * 0.44)
        header_height = int(h * 0.03)
        content_height = int(h * 0.19)  # Slightly taller for better readability
        total_height = header_height + content_height
        
        # Background for entire log area
        pygame.draw.rect(screen, (40, 40, 50), (log_x, log_y, log_width, total_height))
        pygame.draw.rect(screen, (120, 120, 140), (log_x, log_y, log_width, total_height), 2)
        
        # Header with title and minimize button
        pygame.draw.rect(screen, (50, 50, 60), (log_x, log_y, log_width, header_height))
        pygame.draw.rect(screen, (120, 120, 140), (log_x, log_y, log_width, header_height), 1)
        
        header_text = small_font.render("Activity Log", True, (200, 200, 220))
        screen.blit(header_text, (log_x + 8, log_y + 5))
        
        # Minimize button (- symbol)
        minimize_x = log_x + log_width - 20
        minimize_y = log_y + header_height // 2
        pygame.draw.line(screen, (255, 180, 180), (minimize_x - 5, minimize_y), (minimize_x + 5, minimize_y), 2)
        
        # Content area
        content_y = log_y + header_height
        
        # Get messages with scroll offset
        scroll_offset = getattr(game_state, 'activity_log_scroll', 0)
        max_visible_lines = 6  # Number of lines that fit in content area
        start_idx = max(0, len(game_state.messages) - max_visible_lines - scroll_offset)
        end_idx = start_idx + max_visible_lines
        visible_messages = game_state.messages[start_idx:end_idx]
        
        # Draw messages
        for i, msg in enumerate(visible_messages):
            # Truncate long messages
            if len(msg) > 50:
                msg = msg[:47] + "..."
            
            msg_color = (220, 220, 240) if i % 2 == 0 else (200, 200, 220)  # Alternate colours
            msg_text = small_font.render(msg, True, msg_color)
            msg_y = content_y + 5 + i * int(h * 0.025)
            screen.blit(msg_text, (log_x + 8, msg_y))
        
        # Scroll indicators
        if scroll_offset > 0:
            # Up arrow indicator
            up_arrow = small_font.render("?", True, (180, 255, 180))
            screen.blit(up_arrow, (log_x + log_width - 25, content_y + 5))
        
        if len(game_state.messages) > max_visible_lines + scroll_offset:
            # Down arrow indicator
            down_arrow = small_font.render("?", True, (180, 255, 180))
            screen.blit(down_arrow, (log_x + log_width - 25, content_y + content_height - 20))
            
            
    else:
        # Original simple event log (for backward compatibility)
        screen.blit(font.render("Activity Log:", True, (255, 255, 180)), (log_x, log_y))
        for i, msg in enumerate(game_state.messages[-7:]):
            msg_text = small_font.render(msg, True, (255, 255, 210))
            screen.blit(msg_text, (log_x + int(w*0.01), log_y + int(h*0.035) + i * int(h*0.03)))

    # Draw employee blobs (lower middle area)
    draw_employee_blobs(screen, game_state, w, h)
    
    # Draw deferred events zone (lower right)
    draw_deferred_events_zone(screen, game_state, w, h, small_font)
    
    # Draw mute button (bottom right)
    draw_mute_button(screen, game_state, w, h)
    
    # Draw version in bottom right corner (unobtrusive)
    draw_version_footer(screen, w, h)
    
    # Draw popup events (overlay, drawn last to be on top)
    draw_popup_events(screen, game_state, w, h, font, big_font)
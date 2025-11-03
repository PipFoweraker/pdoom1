'''
Refactored End Game Menu
Modular, dynamic replacement for the monolithic draw_end_game_menu function.
'''

import pygame
from typing import Optional, Any
from .menu_components import EndGameMenuRenderer, LayoutConfig, MenuButton


def draw_end_game_menu_modular(screen: pygame.Surface, w: int, h: int, selected_item: int, game_state: Any, seed: str) -> None:
    '''
    Draw the end-of-game menu with modular components and dynamic layout.
    
    This replaces the monolithic draw_end_game_menu function with a cleaner,
    more maintainable approach using modular components.
    
    Args:
        screen: pygame surface to draw on
        w, h: screen width and height for responsive layout
        selected_item: index of currently selected menu item (for keyboard navigation)
        game_state: GameState object for displaying final stats
        seed: Game seed used for this session
    '''
    # Create layout configuration and renderer
    layout_config = LayoutConfig(w, h)
    renderer = EndGameMenuRenderer(layout_config)
    
    # Get leaderboard data for celebration (optional)
    current_rank = None
    is_new_record = False
    try:
        from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
        leaderboard_manager = EnhancedLeaderboardManager()
        leaderboard = leaderboard_manager.get_leaderboard_for_seed(game_state.seed)
        
        if leaderboard.entries:
            for i, entry in enumerate(leaderboard.entries):
                if entry.player_name == game_state.lab_name and entry.score == game_state.turn:
                    current_rank = i + 1
                    is_new_record = (i == 0)
                    break
    except:
        pass  # Graceful fallback if leaderboard fails
    
    # Render sections in order
    renderer.render_title_section(screen, game_state)
    renderer.render_celebration_section(screen, is_new_record, current_rank)
    renderer.render_stats_section(screen, game_state, current_rank, is_new_record)
    renderer.render_scenario_analysis(screen, game_state)
    
    # Render leaderboard preview if available
    _render_leaderboard_preview(screen, renderer, game_state, current_rank, is_new_record)
    
    # Create and render menu buttons
    menu_items = ['View Full Leaderboard', 'Play Again', 'Main Menu', 'Settings', 'Submit Feedback']
    buttons = []
    for i, item in enumerate(menu_items):
        button = MenuButton(
            text=item,
            index=i,
            selected=(i == selected_item),
            enabled=True
        )
        buttons.append(button)
    
    renderer.render_menu_buttons(screen, buttons)
    renderer.render_instructions(screen)


def _render_leaderboard_preview(screen: pygame.Surface, renderer: EndGameMenuRenderer, 
                               game_state: Any, current_rank: Optional[int], is_new_record: bool) -> None:
    '''Render mini leaderboard preview section'''
    if not current_rank:
        return
        
    try:
        from src.scores.enhanced_leaderboard import EnhancedLeaderboardManager
        leaderboard_manager = EnhancedLeaderboardManager()
        leaderboard = leaderboard_manager.get_leaderboard_for_seed(game_state.seed)
        
        if not leaderboard.entries:
            return
            
        # Create leaderboard box
        leaderboard_width = int(renderer.config.screen_width * 0.5)
        leaderboard_height = int(renderer.config.screen_height * 0.15)
        leaderboard_rect = renderer.layout.center_rect(leaderboard_width, leaderboard_height)
        
        # Box styling
        bg_color = renderer.colors['leaderboard_celebration_bg' if is_new_record else 'leaderboard_bg']
        border_color = renderer.colors['leaderboard_celebration_border' if is_new_record else 'leaderboard_border']
        
        pygame.draw.rect(screen, bg_color, leaderboard_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, leaderboard_rect, width=2, border_radius=10)
        
        # Title
        title_color = (150, 255, 150) if is_new_record else (150, 200, 255)
        title_text = f'Leaderboard for '{game_state.seed}''
        title_surface = renderer.fonts['stats'].render(title_text, True, title_color)
        title_x = leaderboard_rect.centerx - title_surface.get_width() // 2
        screen.blit(title_surface, (title_x, leaderboard_rect.y + 15))
        
        # Show top entries
        entry_y = leaderboard_rect.y + 35
        shown_entries = 0
        
        for i, entry in enumerate(leaderboard.entries[:5]):
            if shown_entries >= 3:
                break
                
            rank_num = i + 1
            is_current_player = (entry.player_name == game_state.lab_name and entry.score == game_state.turn)
            
            if is_current_player:
                # Highlight current player
                highlight_color = (255, 255, 100) if is_new_record else (100, 255, 255)
                entry_text = f'#{rank_num}. {entry.player_name}: {entry.score} turns <- YOU!'
                text_color = (0, 0, 0) if is_new_record else (255, 255, 255)
                
                text_surface = renderer.fonts['small'].render(entry_text, True, text_color)
                highlight_rect = pygame.Rect(
                    leaderboard_rect.x + 10, entry_y - 2, 
                    text_surface.get_width() + 10, text_surface.get_height() + 4
                )
                pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=4)
            else:
                entry_text = f'#{rank_num}. {entry.player_name}: {entry.score} turns'
                text_color = (200, 255, 200) if is_new_record else (200, 200, 255)
            
            entry_surface = renderer.fonts['small'].render(entry_text, True, text_color)
            screen.blit(entry_surface, (leaderboard_rect.x + 15, entry_y))
            entry_y += 22
            shown_entries += 1
        
        # Total entries count
        total_text = f'({len(leaderboard.entries)} total entries for this seed)'
        total_color = (150, 200, 150) if is_new_record else (150, 150, 200)
        total_surface = renderer.fonts['small'].render(total_text, True, total_color)
        total_x = leaderboard_rect.centerx - total_surface.get_width() // 2
        screen.blit(total_surface, (total_x, leaderboard_rect.bottom - 15))
        
        # Hint text
        if is_new_record:
            hint_text = 'Press ENTER to view full leaderboard and celebrate your achievement!'
            hint_color = (255, 255, 150)
        else:
            hint_text = 'Press ENTER to view full leaderboard and see all competitors'
            hint_color = (200, 200, 255)
            
        hint_surface = renderer.fonts['small'].render(hint_text, True, hint_color)
        hint_x = renderer.config.screen_width // 2 - hint_surface.get_width() // 2
        hint_y = leaderboard_rect.bottom + renderer.config.spacing
        screen.blit(hint_surface, (hint_x, hint_y))
        
    except Exception:
        pass  # Graceful fallback

'''
Utility validation and processing functions extracted from game_state.py

This module contains pure utility functions for validation, upgrade availability
checking, and achievements processing that have minimal game state dependencies.
'''

from typing import Dict, Any, List, Tuple, Union, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.core.game_state import GameState


def is_upgrade_available(upgrade: Dict[str, Any], opponents: List[Any]) -> bool:
    '''Check if an upgrade should be visible based on its unlock conditions.'''
    unlock_condition = upgrade.get('unlock_condition')
    if not unlock_condition:
        return True  # No condition means always available
    
    if unlock_condition == 'palandir_discovered':
        # Check if Palandir opponent has been discovered
        for opponent in opponents:
            if opponent.name == 'Palandir' and opponent.discovered:
                return True
        return False
    
    return True  # Default to available for unknown conditions


def check_point_in_rect(pt: Tuple[int, int], rect: Union[Tuple[int, int, int, int], pygame.Rect]) -> bool:
    '''Check if point is within rectangle, with graceful error handling.'''
    from src.core.ui_utils import validate_rect
    
    if not validate_rect(rect, 'check_point_in_rect'):
        return False
    
    try:
        x, y = pt
        if isinstance(rect, pygame.Rect):
            return rect.collidepoint(x, y)
        else:
            rx, ry, rw, rh = rect
            return rx <= x <= rx+rw and ry <= y <= ry+rh
    except (TypeError, ValueError):
        return False


def process_achievement_notifications(game_state: 'GameState', achievements_system: Any) -> None:
    '''Process and display achievement notifications.'''
    try:
        # Update achievements system with current turn for warning tracking
        achievements_system._current_turn = game_state.turn
        
        # Check for newly unlocked achievements
        new_achievements = achievements_system.check_new_achievements(game_state)
        
        # Display achievement notifications
        for achievement in new_achievements:
            # Add achievement to player's unlocked set
            game_state.unlocked_achievements.add(achievement.id)
            
            # Display achievement notification with rarity styling
            rarity_indicators = {
                'common': '[TARGET]',
                'uncommon': '[STAR]', 
                'rare': '[TROPHY]',
                'legendary': '?'
            }
            indicator = rarity_indicators.get(achievement.rarity, '[TARGET]')
            
            game_state.messages.append(f'{indicator} ACHIEVEMENT UNLOCKED: {achievement.name}')
            game_state.messages.append(f'? {achievement.description}')
            
            # Play achievement sound based on rarity
            if hasattr(game_state, 'sound_manager'):
                if achievement.rarity in ['legendary', 'rare']:
                    game_state.sound_manager.play_sound('zabinga')  # Special celebratory sound
                else:
                    game_state.sound_manager.play_sound('popup_accept')  # Regular achievement sound
    
    except Exception as e:
        # Defensive programming - achievements system should never crash the game
        try:
            import logging
            logging.error(f'Error in achievement notifications: {e}')
        except:
            pass  # Even logging errors shouldn't crash the game


def process_critical_warnings(game_state: 'GameState', achievements_system: Any) -> None:
    '''Process and display critical warnings.'''
    try:
        # Check for critical warnings that need immediate attention
        warnings = achievements_system.check_critical_warnings(game_state)
        
        # Display critical warnings at start of turn
        for warning in warnings:
            severity_indicators = {
                'WARNING': '[WARNING]?',
                'CRITICAL': '[ALERT]', 
                'SEVERE': '[SKULL]',
                'EXTREME': '[RADIATION]?',
                'EMERGENCY': '[FIRE]',
                'IMMINENT': '[EXPLOSION]'
            }
            indicator = severity_indicators.get(warning['severity'], '[WARNING]?')
            
            game_state.messages.append(f'{indicator} {warning['title']}')
            game_state.messages.append(f'[LIST] {warning['message']}')
            
            # Play warning sound for critical situations
            if (hasattr(game_state, 'sound_manager') and 
                warning['severity'] in ['CRITICAL', 'SEVERE', 'EXTREME', 'EMERGENCY', 'IMMINENT']):
                game_state.sound_manager.play_sound('error_beep')
    
    except Exception as e:
        # Defensive programming - warnings system should never crash the game
        try:
            import logging
            logging.error(f'Error in critical warnings: {e}')
        except:
            pass


def check_victory_conditions(game_state: 'GameState') -> bool:
    '''Check for victory conditions and handle victory state.'''
    try:
        # Check for victory conditions (Issue #195 primary goal)
        if game_state.doom <= 0 and not game_state.game_over:
            # Ultimate victory achieved!
            game_state.game_over = True
            game_state.messages.append('[CELEBRATION] ULTIMATE VICTORY: P(Doom) eliminated! AI alignment problem solved!')
            
            # Play victory sound
            if hasattr(game_state, 'sound_manager'):
                game_state.sound_manager.play_sound('zabinga')
            
            return True
    
    except Exception as e:
        # Defensive programming - victory check should never crash the game
        try:
            import logging
            logging.error(f'Error in victory conditions check: {e}')
        except:
            pass
    
    return False


def process_achievements_and_warnings_complete(game_state: 'GameState', achievements_system: Any) -> None:
    '''Complete achievements and warnings processing.'''
    process_achievement_notifications(game_state, achievements_system)
    process_critical_warnings(game_state, achievements_system)
    check_victory_conditions(game_state)


def filter_available_upgrades(upgrades: List[Dict[str, Any]], opponents: List[Any]) -> List[Tuple[int, Dict[str, Any]]]:
    '''Filter upgrades based on availability conditions.'''
    return [(i, u) for i, u in enumerate(upgrades) if is_upgrade_available(u, opponents)]


def get_milestone_check_functions() -> Dict[str, str]:
    '''Get mapping of milestone types to their check function names.'''
    return {
        'board_member': '_check_board_member_milestone',
        'funding_round': '_check_funding_milestone', 
        'research_breakthrough': '_check_research_milestone',
        'staff_expansion': '_check_staff_milestone'
    }

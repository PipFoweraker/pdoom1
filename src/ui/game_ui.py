'''
Game UI functions for the P(Doom) main game interface.

This module contains the main game UI drawing functions extracted from the 
monolithic ui.py draw_ui function. These functions handle resource displays,
action buttons, upgrades, activity log, and other core game interface elements.
'''

import pygame
from typing import Any, Dict, Optional, Tuple

# Import required modules
from src.features.visual_feedback import visual_feedback, ButtonState, FeedbackStyle
from src.ui.rendering import draw_resource_icon
from src.ui.context import create_action_context_info, create_upgrade_context_info, get_default_context_info


def draw_resource_display(screen: pygame.Surface, game_state: Any, w: int, h: int, 
                         big_font: pygame.font.Font, font: pygame.font.Font, 
                         small_font: pygame.font.Font) -> None:
    '''
    Draw the main resource display including money, staff, reputation, action points,
    doom, compute, research, and papers with proper icons and positioning.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        big_font, font, small_font: font objects for different text sizes
    '''
    # Resources (top bar) - with 8-bit style icons and better alignment
    # Always show resource display regardless of tutorial state for better UX
    current_x = int(w*0.04)  # Starting position
    y_pos = int(h*0.11)
    icon_size = 16
    text_offset_x = icon_size + 8  # Space between icon and text
    
    # Money icon + value (always show)
    draw_resource_icon(screen, 'money', current_x, y_pos + 4, icon_size)
    money_text = big_font.render(f'${game_state.money}', True, (255, 230, 60))
    screen.blit(money_text, (current_x + text_offset_x, y_pos))
    current_x += text_offset_x + money_text.get_width() + int(w*0.03)  # Add spacing
    
    # Cash flow indicator if accounting software is purchased
    if hasattr(game_state, 'accounting_software_bought') and game_state.accounting_software_bought:
        if hasattr(game_state, 'last_balance_change') and game_state.last_balance_change != 0:
            change_color = (100, 255, 100) if game_state.last_balance_change > 0 else (255, 100, 100)
            change_sign = '+' if game_state.last_balance_change > 0 else ''
            change_text = f'({change_sign}${game_state.last_balance_change})'
            screen.blit(font.render(change_text, True, change_color), (int(w*0.04), int(h*0.13)))
    
    # Staff icon (person symbol) + value (always show)
    pygame.draw.circle(screen, (255, 210, 180), (current_x + 8, y_pos + 6), 4)  # Head
    pygame.draw.rect(screen, (255, 210, 180), (current_x + 6, y_pos + 10, 4, 8))  # Body
    staff_text = big_font.render(f'{game_state.staff}', True, (255, 210, 180))
    screen.blit(staff_text, (current_x + text_offset_x, y_pos))
    current_x += text_offset_x + staff_text.get_width() + int(w*0.03)  # Add spacing
    
    # Reputation icon (star) + value (always show)
    star_points = [(current_x + 8, y_pos + 4), (current_x + 10, y_pos + 10), 
                  (current_x + 16, y_pos + 10), (current_x + 12, y_pos + 14),
                  (current_x + 14, y_pos + 20), (current_x + 8, y_pos + 16),
                  (current_x + 2, y_pos + 20), (current_x + 4, y_pos + 14),
                  (current_x, y_pos + 10), (current_x + 6, y_pos + 10)]
    pygame.draw.polygon(screen, (180, 210, 255), star_points)
    reputation_text = big_font.render(f'{game_state.reputation}', True, (180, 210, 255))
    screen.blit(reputation_text, (current_x + text_offset_x, y_pos))
    current_x += text_offset_x + reputation_text.get_width() + int(w*0.035)  # Add slightly more spacing
    
    # Action Points with glow effect and energy icon (always show)
    ap_color = (255, 255, 100)  # Yellow base color for AP
    if hasattr(game_state, 'ap_glow_timer') and game_state.ap_glow_timer > 0:
        # Add glow/pulse effect when AP is spent
        glow_intensity = int(127 * (game_state.ap_glow_timer / 30))  # Fade over 30 frames
        ap_color = (min(255, 255 + glow_intensity), min(255, 255 + glow_intensity), min(255, 100 + glow_intensity))
    
    # Energy/lightning bolt icon for AP
    lightning_points = [(current_x + 6, y_pos + 4), (current_x + 10, y_pos + 4), 
                       (current_x + 8, y_pos + 10), (current_x + 12, y_pos + 10),
                       (current_x + 6, y_pos + 18), (current_x + 10, y_pos + 12), 
                       (current_x + 8, y_pos + 12)]
    pygame.draw.polygon(screen, ap_color, lightning_points)
    
    ap_text = big_font.render(f'{game_state.action_points}/{game_state.max_action_points}', True, ap_color)
    screen.blit(ap_text, (current_x + text_offset_x, y_pos))
    current_x += text_offset_x + ap_text.get_width() + int(w*0.035)  # Add spacing
    
    # Doom with skull icon (always show)
    skull_color = (255, 80, 80)
    pygame.draw.circle(screen, skull_color, (current_x + 8, y_pos + 8), 6)  # Skull
    pygame.draw.rect(screen, skull_color, (current_x + 5, y_pos + 6, 2, 2))  # Eye 1
    pygame.draw.rect(screen, skull_color, (current_x + 9, y_pos + 6, 2, 2))  # Eye 2
    pygame.draw.rect(screen, skull_color, (current_x + 6, y_pos + 10, 4, 1))  # Mouth
    
    doom_text = big_font.render(f'{game_state.doom}/{game_state.max_doom}', True, skull_color)
    screen.blit(doom_text, (current_x + text_offset_x, y_pos))
    current_x += text_offset_x + doom_text.get_width() + int(w*0.03)  # Add spacing
    
    # Opponent progress (smaller font, positioned at the end)
    if current_x + 200 < w:  # Only show if there's enough space
        screen.blit(font.render(f'Opponent progress: {game_state.known_opp_progress if game_state.known_opp_progress is not None else '???'}/100', True, (240, 200, 160)), (current_x, y_pos + 5))


def draw_secondary_resources(screen: pygame.Surface, game_state: Any, w: int, h: int,
                           big_font: pygame.font.Font, font: pygame.font.Font,
                           small_font: pygame.font.Font) -> None:
    '''
    Draw the second line of resources including compute, research progress, papers,
    and advanced resource tracking systems.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        big_font, font, small_font: font objects for different text sizes
    '''
    # Second line of resources with improved spacing and icons
    current_x = int(w*0.04)  # Reset to starting position
    y_pos_2 = int(h*0.135)
    icon_size = 16
    text_offset_x = icon_size + 8  # Space between icon and text
    
    # Compute with exponential icon
    draw_resource_icon(screen, 'compute', current_x, y_pos_2 + 4, icon_size)
    compute_text = big_font.render(f'{game_state.compute}', True, (100, 255, 150))
    screen.blit(compute_text, (current_x + text_offset_x, y_pos_2))
    current_x += text_offset_x + compute_text.get_width() + int(w*0.03)  # Add spacing
    
    # Research with light bulb icon
    draw_resource_icon(screen, 'research', current_x, y_pos_2 + 4, icon_size)
    research_text = big_font.render(f'{game_state.research_progress}/100', True, (150, 200, 255))
    screen.blit(research_text, (current_x + text_offset_x, y_pos_2))
    current_x += text_offset_x + research_text.get_width() + int(w*0.03)  # Add spacing
    
    # Papers with document icon
    draw_resource_icon(screen, 'papers', current_x, y_pos_2 + 4, icon_size)
    papers_text = big_font.render(f'{game_state.papers_published}', True, (255, 200, 100))
    screen.blit(papers_text, (current_x + text_offset_x, y_pos_2))
    current_x += text_offset_x + papers_text.get_width() + int(w*0.03)  # Add spacing
    
    # Board member and audit risk display (if applicable)
    if hasattr(game_state, 'board_members') and game_state.board_members > 0:
        screen.blit(font.render(f'Board Members: {game_state.board_members}', True, (255, 150, 150)), (int(w*0.55), int(h*0.135)))
        if hasattr(game_state, 'audit_risk_level') and game_state.audit_risk_level > 0:
            risk_color = (255, 200, 100) if game_state.audit_risk_level <= 5 else (255, 100, 100)
            screen.blit(font.render(f'Audit Risk: {game_state.audit_risk_level}', True, risk_color), (int(w*0.72), int(h*0.135)))


def draw_research_quality_system(screen: pygame.Surface, game_state: Any, w: int, h: int,
                                font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    '''
    Draw the research quality system display including current quality setting,
    technical debt tracking, and research effectiveness modifiers.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        font, small_font: font objects for text rendering
    '''
    # Research Quality System - Technical Debt Display (if unlocked)
    if hasattr(game_state, 'research_quality_unlocked') and game_state.research_quality_unlocked:
        # Third line for research quality info
        y_pos = int(h * 0.16)
        
        # Current research quality
        quality_text = f'Research: {game_state.current_research_quality.value.title()}'
        quality_color = {
            'rushed': (255, 180, 100),    # Orange for rushed
            'standard': (200, 200, 200),  # Gray for standard  
            'thorough': (100, 255, 180)   # Green for thorough
        }.get(game_state.current_research_quality.value, (200, 200, 200))
        screen.blit(font.render(quality_text, True, quality_color), (int(w*0.04), y_pos))
        
        # Technical debt with warning colors
        debt_total = game_state.technical_debt.accumulated_debt
        debt_color = (200, 200, 200)  # Default gray
        if debt_total >= 20:
            debt_color = (255, 100, 100)  # Red for critical debt
        elif debt_total >= 11:
            debt_color = (255, 180, 100)  # Orange for high debt
        elif debt_total >= 6:
            debt_color = (255, 255, 100)  # Yellow for medium debt
        
        debt_text = f'Tech Debt: {debt_total}'
        screen.blit(font.render(debt_text, True, debt_color), (int(w*0.21), y_pos))
        
        # Research effectiveness penalty (if any)
        effectiveness = game_state.get_research_effectiveness_modifier()
        if effectiveness < 1.0:
            penalty_percent = int((1.0 - effectiveness) * 100)
            penalty_text = f'Research -{penalty_percent}%'
            screen.blit(font.render(penalty_text, True, (255, 150, 150)), (int(w*0.35), y_pos))
        
        # Debt consequences indicators
        if debt_total >= 11:  # Show accident chance
            accident_chance = int(game_state.technical_debt.get_accident_chance() * 100)
            if accident_chance > 0:
                accident_text = f'Accident Risk: {accident_chance}%'
                screen.blit(small_font.render(accident_text, True, (255, 200, 100)), (int(w*0.50), y_pos))
        
        # System failure warning for very high debt
        if game_state.technical_debt.can_trigger_system_failure():
            failure_text = '!! SYSTEM FAILURE RISK'
            screen.blit(small_font.render(failure_text, True, (255, 100, 100)), (int(w*0.70), y_pos))


def draw_action_buttons(screen: pygame.Surface, game_state: Any, w: int, h: int,
                       small_font: pygame.font.Font) -> None:
    '''
    Draw the action buttons with support for both compact and traditional UI modes,
    including visual feedback and usage indicators.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        small_font: font object for small text
    '''
    # Action buttons (left) - Enhanced with visual feedback
    # Check if we should use compact UI mode
    use_compact_ui = not getattr(game_state, 'tutorial_enabled', True)
    
    # Always filter actions to only show available ones (hide locked actions)
    # This should work regardless of tutorial mode for cleaner interface
    available_actions = []
    available_action_indices = []
    for idx, action in enumerate(game_state.actions):
        # Check if action is unlocked (no rules or rules return True)
        if not action.get('rules') or action['rules'](game_state):
            available_actions.append(action)
            available_action_indices.append(idx)
    
    # Store the mapping for click handling
    game_state.display_to_action_index_map = available_action_indices
    
    if use_compact_ui:
        # Import compact UI functions
        from src.ui.compact_ui import get_compact_action_rects, draw_compact_action_button
        
        # Use compact layout with filtered actions
        action_rects = get_compact_action_rects(w, h, len(available_actions))
    else:
        # Use traditional layout with filtered actions - calculate rects manually
        count = len(available_actions)
        base_x = int(w * 0.04)
        base_y = int(h * 0.28)  # Moved down from 0.16 to 0.28
        # Compact action buttons - reduced size for cleaner layout
        width = int(w * 0.25)  # Reduced from 0.30 to 0.25 (25%)
        height = int(h * 0.045)  # Reduced from 0.055 to 0.045 (4.5%)
        gap = int(h * 0.008)  # Reduced from 0.015 to 0.008 (0.8%)
        action_rects = [
            pygame.Rect(base_x, base_y + i * (height + gap), width, height)
            for i in range(count)
        ]
    
    # Store the action rects for click handling (with display indices)
    game_state.filtered_action_rects = action_rects
    
    # Hard clamp: ensure buttons don't extend below context window top
    try:
        context_top = game_state._get_context_window_top(h)
    except Exception:
        context_top = int(h * 0.90) - 5

    for display_idx, rect in enumerate(action_rects):
        if display_idx >= len(available_actions):
            break
            
        action = available_actions[display_idx]
        original_idx = available_action_indices[display_idx]  # Original index in game_state.actions
        ap_cost = action.get('ap_cost', 1)
        
        # Determine button state for visual feedback
        if game_state.action_points < ap_cost:
            button_state = ButtonState.DISABLED
        elif original_idx in game_state.selected_gameplay_actions:  # Use original index for selection check
            button_state = ButtonState.PRESSED
        elif hasattr(game_state, 'hovered_action_idx') and game_state.hovered_action_idx == original_idx:
            button_state = ButtonState.HOVER
        else:
            button_state = ButtonState.NORMAL
        
        if use_compact_ui:
            # Clamp for compact mode where rect is a tuple
            rx, ry, rw0, rh0 = rect
            if ry + rh0 > context_top:
                rh0 = max(0, context_top - ry - 2)
            if rh0 <= 0:
                continue
            # Draw compact button with icon and shortcut key
            from src.ui.compact_ui import draw_compact_action_button
            draw_compact_action_button(screen, (rx, ry, rw0, rh0), action, original_idx, button_state)
        else:
            # Clamp rect height if it would overlap the context window (pygame.Rect)
            if rect.bottom > context_top:
                rect.height = max(0, context_top - rect.top - 2)
            if rect.height <= 0:
                continue
            # Traditional button with text (shorter in non-tutorial mode)
            from src.services.keybinding_manager import keybinding_manager
            
            # Use shorter text for cleaner interface - context window provides details
            button_text = action['name']
            if original_idx < 9:  # Only first 9 actions get keyboard shortcuts
                shortcut_key = keybinding_manager.get_action_display_key(f'action_{original_idx + 1}')
                button_text = f'[{shortcut_key}] {action['name']}'
            
            visual_feedback.draw_button(
                screen, rect, button_text, button_state, FeedbackStyle.BUTTON
            )
            
            # Description text is now shown in context window instead of cluttering buttons
            # This eliminates text overflow issues
        
        # Draw action usage indicators (circles for repeatables) - works for both modes
        if hasattr(game_state, 'selected_action_instances'):
            action_count = sum(1 for inst in game_state.selected_action_instances if inst['action_idx'] == original_idx)
            if action_count > 0:
                # Draw usage indicators as small circles
                indicator_size = int(min(w, h) * 0.008)  # Small circles
                indicator_color = (100, 255, 100) if button_state != ButtonState.DISABLED else (60, 120, 60)
                
                # Position indicators in top-left of button for compact mode, top-right for traditional
                if use_compact_ui:
                    start_x = rect.left + 5
                    start_y = rect.top + 5
                else:
                    start_x = rect.right - (action_count * indicator_size * 2) - 5
                    start_y = rect.top + 5
                
                for i in range(min(action_count, 5)):  # Max 5 indicators to avoid clutter
                    circle_x = start_x + (i * indicator_size * 2)
                    circle_y = start_y + indicator_size
                    pygame.draw.circle(screen, indicator_color, (circle_x, circle_y), indicator_size)
                    
                # If more than 5, show '+N' text
                if action_count > 5:
                    more_text = small_font.render(f'+{action_count-5}', True, indicator_color)
                    screen.blit(more_text, (start_x + 5 * indicator_size * 2 + 2, start_y))


def draw_upgrade_buttons(screen: pygame.Surface, game_state: Any, w: int, h: int,
                        small_font: pygame.font.Font) -> None:
    '''
    Draw the upgrade buttons with support for both compact and traditional UI modes,
    showing purchased upgrades as icons and available upgrades as buttons.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        small_font: font object for small text
    '''
    # Upgrades (right: purchased as icons at top right, available as buttons) - Enhanced with visual feedback
    use_compact_ui = not getattr(game_state, 'tutorial_enabled', True)
    
    if use_compact_ui:
        # Import compact UI functions
        from src.ui.compact_ui import get_compact_upgrade_rects, draw_compact_upgrade_button
        
        # Count purchased upgrades
        num_purchased = sum(1 for upg in game_state.upgrades if upg.get('purchased', False))
        
        # Use compact layout
        upgrade_rects = get_compact_upgrade_rects(w, h, len(game_state.upgrades), num_purchased)
    else:
        # Use traditional layout
        upgrade_rect_tuples = game_state._get_upgrade_rects(w, h)
        upgrade_rects = []
        for rect_tuple in upgrade_rect_tuples:
            if rect_tuple is not None:
                upgrade_rects.append(pygame.Rect(rect_tuple))
            else:
                upgrade_rects.append(None)  # Keep None for unavailable upgrades
    
    for idx, rect in enumerate(upgrade_rects):
        if idx >= len(game_state.upgrades) or rect is None:
            continue  # Skip unavailable upgrades
            
        upg = game_state.upgrades[idx]
        is_purchased = upg.get('purchased', False)
        
        if use_compact_ui:
            # Clamp for compact mode where rect is a tuple
            rx, ry, rw0, rh0 = rect
            try:
                context_top = game_state._get_context_window_top(h)
            except Exception:
                context_top = int(h * 0.90) - 5
            if ry + rh0 > context_top:
                rh0 = max(0, context_top - ry - 2)
            if rh0 <= 0:
                continue
            # Determine button state for compact mode
            if not is_purchased and upg['cost'] > game_state.money:
                button_state = ButtonState.DISABLED
            elif hasattr(game_state, 'hovered_upgrade_idx') and game_state.hovered_upgrade_idx == idx:
                button_state = ButtonState.HOVER
            else:
                button_state = ButtonState.NORMAL
            
            # Draw compact upgrade button
            draw_compact_upgrade_button(screen, (rx, ry, rw0, rh0), upg, idx, button_state, is_purchased)
        else:
            # Clamp rect height for traditional mode (pygame.Rect)
            try:
                context_top = game_state._get_context_window_top(h)
            except Exception:
                context_top = int(h * 0.90) - 5
            if rect.bottom > context_top:
                rect.height = max(0, context_top - rect.top - 2)
            if rect.height <= 0:
                continue
            # Traditional upgrade display
            if is_purchased:
                # Draw as small icon using visual feedback system
                visual_feedback.draw_icon_button(screen, rect, upg['name'][0], ButtonState.NORMAL)
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
                    screen, rect, upg['name'], button_state, FeedbackStyle.BUTTON
                )
                
                # Only draw description and status in tutorial mode
                if getattr(game_state, 'tutorial_enabled', True):
                    desc_color = (200, 255, 200) if button_state != ButtonState.DISABLED else (120, 150, 120)
                    desc = small_font.render(upg['desc'] + f' (Cost: ${upg['cost']})', True, desc_color)
                    status = small_font.render('AVAILABLE', True, desc_color)
                    screen.blit(desc, (rect.x + int(w*0.01), rect.y + int(h*0.04)))
                    screen.blit(status, (rect.x + int(w*0.24), rect.y + int(h*0.04)))


def draw_end_turn_button(screen: pygame.Surface, game_state: Any, w: int, h: int) -> pygame.Rect:
    '''
    Draw the end turn button with visual feedback support for both compact
    and traditional UI modes.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        
    Returns:
        pygame.Rect: The rect of the end turn button for click detection
    '''
    # End Turn button (bottom center) - Enhanced with visual feedback
    # Determine button state (common for both modes)
    endturn_state = ButtonState.HOVER if hasattr(game_state, 'endturn_hovered') and game_state.endturn_hovered else ButtonState.NORMAL
    use_compact_ui = not getattr(game_state, 'tutorial_enabled', True)
    
    if use_compact_ui:
        # Use compact end turn button
        from src.ui.compact_ui import draw_compact_end_turn_button
        endturn_rect = draw_compact_end_turn_button(screen, w, h, endturn_state)
    else:
        # Traditional end turn button
        endturn_rect_tuple = game_state._get_endturn_rect(w, h)
        endturn_rect = pygame.Rect(endturn_rect_tuple)
        
        # Use visual feedback system with custom colors for end turn button
        custom_colors = {
            ButtonState.NORMAL: {
                'bg': (140, 90, 90),
                'border': (210, 110, 110),
                'text': (255, 240, 240),
                'shadow': (60, 40, 40)
            },
            ButtonState.HOVER: {
                'bg': (160, 110, 110),
                'border': (230, 130, 130),
                'text': (255, 255, 255),
                'shadow': (80, 60, 60),
                'glow': (255, 200, 200, 40)
            }
        }
        
        # Get shortcut key for traditional mode
        from src.services.keybinding_manager import keybinding_manager
        shortcut_display = keybinding_manager.get_action_display_key('end_turn')
        
        visual_feedback.draw_button(
            screen, endturn_rect, f'END TURN ({shortcut_display})', endturn_state, 
            FeedbackStyle.BUTTON, custom_colors.get(endturn_state)
        )
    
    return endturn_rect


def draw_activity_log(screen: pygame.Surface, game_state: Any, w: int, h: int,
                     font: pygame.font.Font, small_font: pygame.font.Font) -> None:
    '''
    Draw the activity log with support for scrollable history, minimize functionality,
    and different display modes based on available upgrades.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        font, small_font: font objects for text rendering
    '''
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
        'compact_activity_display' in game_state.upgrade_effects):
        # Draw minimized activity log as a small title bar with expand button
        title_text = font.render('Activity Log', True, (255, 255, 180))
        title_width = title_text.get_width()
        
        # Draw small background bar
        bar_height = int(h * 0.04)
        bar_rect = pygame.Rect(log_x - 5, log_y - 5, title_width + 50, bar_height)
        pygame.draw.rect(screen, (60, 80, 100), bar_rect, border_radius=4)
        pygame.draw.rect(screen, (120, 140, 180), bar_rect, width=1, border_radius=4)
        
        screen.blit(title_text, (log_x, log_y))
        
        # Draw expand button (plus icon)
        expand_button_x = log_x + title_width + 10
        expand_button_y = log_y
        expand_button_size = int(h * 0.025)
        
        pygame.draw.rect(screen, (100, 120, 150), 
                        (expand_button_x, expand_button_y, expand_button_size, expand_button_size),
                        border_radius=2)
        
        # Plus icon
        plus_font = pygame.font.SysFont('Consolas', int(h * 0.02), bold=True)
        plus_text = plus_font.render('+', True, (255, 255, 255))
        plus_rect = plus_text.get_rect(center=(expand_button_x + expand_button_size//2, 
                                               expand_button_y + expand_button_size//2))
        screen.blit(plus_text, plus_rect)
        
    elif game_state.scrollable_event_log_enabled:
        # Enhanced scrollable event log with border and visual indicators
        log_width = int(w * 0.22)  # Reduced from 0.44 to 0.22 to avoid upgrade button overlap
        log_height = int(h * 0.14)  # Reduced to account for context window at bottom
        
        # Draw border around the event log area
        border_rect = pygame.Rect(log_x - 5, log_y - 5, log_width + 10, log_height + 10)
        pygame.draw.rect(screen, (80, 100, 120), border_rect, border_radius=8)
        pygame.draw.rect(screen, (120, 140, 180), border_rect, width=2, border_radius=8)
        
        # Event log title with scroll indicator and minimize button
        title_text = font.render('Activity Log (Scrollable)', True, (255, 255, 180))
        screen.blit(title_text, (log_x, log_y))
        
        # Add minimize button if compact display upgrade is available
        if 'compact_activity_display' in game_state.upgrade_effects:
            minimize_button_x = log_x + log_width - 30
            minimize_button_y = log_y
            minimize_button_size = int(h * 0.025)
            
            pygame.draw.rect(screen, (100, 120, 150), 
                            (minimize_button_x, minimize_button_y, minimize_button_size, minimize_button_size),
                            border_radius=2)
            
            # Minus icon
            minus_font = pygame.font.SysFont('Consolas', int(h * 0.02), bold=True)
            minus_text = minus_font.render('-', True, (255, 255, 255))
            minus_rect = minus_text.get_rect(center=(minimize_button_x + minimize_button_size//2, 
                                                   minimize_button_y + minimize_button_size//2))
            screen.blit(minus_text, minus_rect)
        
        # Scroll indicator
        if len(game_state.event_log_history) > 0 or len(game_state.messages) > 0:
            scroll_info = small_font.render('Up/Down or mouse wheel to scroll', True, (200, 200, 255))
            scroll_x = log_x + log_width - scroll_info.get_width()
            if 'compact_activity_display' in game_state.upgrade_effects:
                scroll_x -= 35  # Make room for minimize button
            screen.blit(scroll_info, (scroll_x, log_y))
        
        # Calculate visible area for messages
        content_y = log_y + int(h * 0.04)
        content_height = log_height - int(h * 0.05)
        line_height = int(h * 0.025)
        max_visible_lines = content_height // line_height
        
        # Combine history and current messages for display
        all_messages = list(game_state.event_log_history) + game_state.messages
        
        # Calculate scrolling - Auto-scroll to bottom by default for new content
        total_lines = len(all_messages)
        
        # Check if we should auto-scroll to bottom (when there are more lines than visible)
        if total_lines > max_visible_lines:
            # If scroll offset is 0 or close to max (user at bottom), keep at bottom
            max_scroll_offset = total_lines - max_visible_lines
            if game_state.event_log_scroll_offset <= 1 or game_state.event_log_scroll_offset >= max_scroll_offset - 1:
                game_state.event_log_scroll_offset = max_scroll_offset
        
        start_line = max(0, min(game_state.event_log_scroll_offset, total_lines - max_visible_lines))
        
        # Draw messages with scrolling
        for i in range(max_visible_lines):
            msg_index = start_line + i
            if msg_index < len(all_messages):
                msg = all_messages[msg_index]
                y_pos = content_y + i * line_height
                
                # Different colors for turn headers vs regular messages
                if msg.startswith('=== Turn'):
                    color = (255, 220, 120)  # Yellow for turn headers
                    font_to_use = font
                else:
                    color = (255, 255, 210)  # White for regular messages
                    font_to_use = small_font
                
                # Truncate long messages to fit width
                max_chars = log_width // 8  # Rough estimate
                if len(msg) > max_chars:
                    msg = msg[:max_chars-3] + '...'
                
                msg_text = font_to_use.render(msg, True, color)
                screen.blit(msg_text, (log_x + int(w*0.01), y_pos))
        
        # Draw scroll indicators if needed
        if start_line > 0:
            # Up arrow indicator
            up_arrow = small_font.render('^', True, (180, 255, 180))
            screen.blit(up_arrow, (log_x + log_width - 25, content_y))
        
        if start_line + max_visible_lines < total_lines:
            # Down arrow indicator
            down_arrow = small_font.render('v', True, (180, 255, 180))
            screen.blit(down_arrow, (log_x + log_width - 25, content_y + content_height - 20))
            
    else:
        # Original simple event log (for backward compatibility)
        screen.blit(font.render('Activity Log:', True, (255, 255, 180)), (log_x, log_y))
        for i, msg in enumerate(game_state.messages[-7:]):
            msg_text = small_font.render(msg, True, (255, 255, 210))
            screen.blit(msg_text, (log_x + int(w*0.01), log_y + int(h*0.035) + i * int(h*0.03)))


def draw_game_context_window(screen: pygame.Surface, game_state: Any, w: int, h: int) -> Tuple[Optional[pygame.Rect], Optional[pygame.Rect]]:
    '''
    Draw the context window with action/upgrade details and hover information.
    
    Args:
        screen: pygame surface to draw on
        game_state: current game state object
        w, h: screen width and height
        
    Returns:
        Tuple of (context_window_rect, context_button_rect) for click detection
    '''
    # Always show context window (persistent at bottom)
    # Context window should always be visible to show action details
    # This replaces the old text overflow on action buttons
    use_compact_ui = not getattr(game_state, 'tutorial_enabled', True)
    context_info = None
    
    # Check if context window should be shown based on configuration
    show_context_window = True  # Always show context window for better UX
    if hasattr(game_state, 'config') and game_state.config:
        ctx_config = game_state.config.get('ui', {}).get('context_window', {})
        show_context_window = ctx_config.get('enabled', True)
        always_visible = ctx_config.get('always_visible', True)
    else:
        always_visible = True
    
    # Always show context window (regardless of tutorial mode) for action details
    if show_context_window:
        # Generate context info based on hover state or provide default
        if hasattr(game_state, 'hovered_action_idx') and game_state.hovered_action_idx is not None:
            # Show action context
            if game_state.hovered_action_idx < len(game_state.actions):
                action = game_state.actions[game_state.hovered_action_idx]
                context_info = create_action_context_info(action, game_state, game_state.hovered_action_idx)
        elif hasattr(game_state, 'hovered_upgrade_idx') and game_state.hovered_upgrade_idx is not None:
            # Show upgrade context
            if game_state.hovered_upgrade_idx < len(game_state.upgrades):
                upgrade = game_state.upgrades[game_state.hovered_upgrade_idx]
                context_info = create_upgrade_context_info(upgrade, game_state, game_state.hovered_upgrade_idx)
        
        # Fall back to default context if no hover info and always_visible is true
        if not context_info and always_visible:
            context_info = get_default_context_info(game_state)
    elif hasattr(game_state, 'current_context_info') and game_state.current_context_info:
        # In tutorial mode, only show context if explicitly set
        context_info = game_state.current_context_info
    
    # Draw context window if we have context info
    if context_info:
        context_minimized = getattr(game_state, 'context_window_minimized', False)
        config = getattr(game_state, 'config', None)
        # Import draw_context_window from ui module
        from ui import draw_context_window
        context_rect, context_button_rect = draw_context_window(
            screen, context_info, w, h, context_minimized, config
        )
        
        return context_rect, context_button_rect
    else:
        return None, None

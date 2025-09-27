"""
Input management system extracted from game_state.py

This module handles all mouse input processing including clicks, motion, and hover detection.
Provides clean separation of input handling concerns from core game logic.
"""

from typing import Tuple, Dict, Any, Optional, List, Union, TYPE_CHECKING
import pygame
from src.services.deterministic_rng import get_rng
from src.core.utility_functions import check_point_in_rect
from src.core.ui_utils import (
    get_action_rects, get_upgrade_rects, get_upgrade_icon_rect, get_context_window_top,
    get_endturn_rect, get_mute_button_rect, get_activity_log_minimize_button_rect,
    get_activity_log_expand_button_rect, get_activity_log_rect, get_activity_log_base_position,
    get_activity_log_current_position
)

if TYPE_CHECKING:
    from src.core.game_state import GameState


class InputManager:
    """Handles all mouse input processing for the game interface."""
    
    def __init__(self, game_state: Any):
        """Initialize the input manager with a reference to the game state."""
        self.game_state = game_state
    
    def handle_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Main entry point for handling mouse clicks."""
        # Check if using 3-column layout
        use_three_column = False
        if hasattr(self.game_state, 'config') and self.game_state.config:
            ui_config = self.game_state.config.get('ui', {})
            use_three_column = ui_config.get('enable_three_column_layout', False)
        
        if use_three_column:
            return self._handle_three_column_click(mouse_pos, w, h)
        else:
            return self._handle_legacy_click(mouse_pos, w, h)
    
    def _handle_three_column_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle clicks for the new 3-column layout."""
        gs = self.game_state
        
        # Check context window minimize/maximize button FIRST
        if (hasattr(gs, 'context_window_button_rect') and 
            gs.context_window_button_rect and 
            check_point_in_rect(mouse_pos, gs.context_window_button_rect)):
            gs.context_window_minimized = not getattr(gs, 'context_window_minimized', False)
            return None
        
        # Check End Turn button
        if hasattr(gs, 'endturn_rect') and gs.endturn_rect and check_point_in_rect(mouse_pos, gs.endturn_rect):
            if not gs.game_over:
                gs.end_turn()
                return None
        
        # Check 3-column action buttons
        if hasattr(gs, 'three_column_button_rects'):
            for button_rect, original_idx in gs.three_column_button_rects:
                if check_point_in_rect(mouse_pos, button_rect):
                    if not gs.game_over and original_idx < len(gs.gameplay_actions):
                        # Check for undo (if action is already selected, try to undo it)
                        is_undo = original_idx in gs.selected_gameplay_actions
                        
                        result = gs.attempt_action_selection(original_idx, is_undo)
                        
                        # Return play_sound flag for main.py to handle sound
                        return 'play_sound' if result['play_sound'] else None
                    return None
        
        # Handle popup events if active
        if hasattr(gs, 'popup_button_rects'):
            for button_rect, action, event in gs.popup_button_rects:
                if check_point_in_rect(mouse_pos, button_rect):
                    gs._handle_popup_action(action, event)
                    return None
        
        # Handle tutorial dismiss if active
        if hasattr(gs, 'tutorial_dismiss_rect') and gs.tutorial_dismiss_rect:
            if check_point_in_rect(mouse_pos, gs.tutorial_dismiss_rect):
                gs.dismiss_tutorial_message()
                return None
        
        return None
    
    def _handle_legacy_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Handle clicks for the legacy UI layout."""
        gs = self.game_state
        
        # Check context window minimize/maximize button FIRST
        if (hasattr(gs, 'context_window_button_rect') and 
            gs.context_window_button_rect and 
            check_point_in_rect(mouse_pos, gs.context_window_button_rect)):
            gs.context_window_minimized = not getattr(gs, 'context_window_minimized', False)
            return None
        
        # Check End Turn button FIRST for reliability (Issue #3 requirement)
        btn_rect = get_endturn_rect(w, h)
        if check_point_in_rect(mouse_pos, btn_rect) and not gs.game_over:
            # Try to end turn, sound feedback handled in end_turn method
            gs.end_turn()
            return None
        
        # Activity log drag functionality - Handle after end turn check
        activity_log_rect = get_activity_log_rect(w, h)
        if check_point_in_rect(mouse_pos, activity_log_rect):
            # Don't start drag if clicking on minimize/expand buttons
            if "compact_activity_display" in gs.upgrade_effects:
                if hasattr(gs, 'activity_log_minimized') and gs.activity_log_minimized:
                    expand_rect = get_activity_log_expand_button_rect(w, h)
                    if check_point_in_rect(mouse_pos, expand_rect):
                        gs.activity_log_minimized = False
                        gs.messages.append("Activity log expanded.")
                        return None  # Button click handled
                elif gs.scrollable_event_log_enabled:
                    minimize_rect = get_activity_log_minimize_button_rect(w, h)
                    if check_point_in_rect(mouse_pos, minimize_rect):
                        gs.activity_log_minimized = True
                        gs.messages.append("Activity log minimized.")
                        return None  # Button click handled
            
            # Start dragging the activity log
            log_x, log_y = get_activity_log_base_position(w, h)
            gs.activity_log_being_dragged = True
            gs.activity_log_drag_offset = (mouse_pos[0] - (log_x + gs.activity_log_position[0]), 
                                           mouse_pos[1] - (log_y + gs.activity_log_position[1]))
            return None

        # Actions (left) - Handle filtered actions with display mapping
        if hasattr(gs, 'filtered_action_rects') and hasattr(gs, 'display_to_action_index_map'):
            # Use filtered action rects if available (when UI shows only unlocked actions)
            action_rects = gs.filtered_action_rects
            for display_idx, rect in enumerate(action_rects):
                if check_point_in_rect(mouse_pos, rect):
                    if not gs.game_over and display_idx < len(gs.display_to_action_index_map):
                        original_idx = gs.display_to_action_index_map[display_idx]
                        # Check for undo (if action is already selected, try to undo it)
                        is_undo = original_idx in gs.selected_gameplay_actions
                        
                        result = gs.attempt_action_selection(original_idx, is_undo)
                        
                        # Return play_sound flag for main.py to handle sound
                        return 'play_sound' if result['play_sound'] else None
                    return None
        else:
            # Fallback to original action handling (show all actions)
            a_rects = get_action_rects(w, h)
            for idx, rect in enumerate(a_rects):
                if check_point_in_rect(mouse_pos, rect):
                    if not gs.game_over:
                        # Check for undo (if action is already selected, try to undo it)
                        is_undo = idx in gs.selected_gameplay_actions
                        
                        result = gs.attempt_action_selection(idx, is_undo)
                        
                        # Return play_sound flag for main.py to handle sound
                        return 'play_sound' if result['play_sound'] else None
                    return None

        # Upgrades (right, as icons or buttons)
        u_rects = get_upgrade_rects(w, h)
        for idx, rect in enumerate(u_rects):
            # Skip None rectangles (unavailable/hidden upgrades)
            if rect is None:
                continue
            # Bounds check: ensure we don't access beyond available upgrades
            if idx >= len(gs.upgrades):
                continue
            if check_point_in_rect(mouse_pos, rect):
                upg = gs.upgrades[idx]
                if not upg.get("purchased", False):
                    if gs.money >= upg["cost"]:
                        gs._add('money', -upg["cost"])  # Use _add to track spending
                        upg["purchased"] = True
                        gs.upgrade_effects.add(upg["effect_key"])
                        
                        # Trigger first-time help for upgrade purchase
                        if gs.onboarding.should_show_mechanic_help('first_upgrade_purchase'):
                            gs.onboarding.mark_mechanic_seen('first_upgrade_purchase')
                        
                        # Special handling for custom effects
                        if upg.get("custom_effect") == "buy_accounting_software":
                            gs.accounting_software_bought = True
                            gs.messages.append(f"Upgrade purchased: {upg['name']} - Cash flow tracking enabled, board oversight blocked!")
                        elif upg.get("custom_effect") == "buy_compact_activity_display":
                            # Allow toggle functionality for the activity log
                            gs.messages.append(f"Upgrade purchased: {upg['name']} - Activity log can now be minimized! Click the minimize button.")
                        elif upg.get("custom_effect") == "buy_magical_orb_seeing":
                            # Enable enhanced intelligence gathering capabilities
                            gs.magical_orb_active = True
                            gs.messages.append(f"Upgrade purchased: {upg['name']} - Enhanced global surveillance capabilities now active!")
                            gs.messages.append("The orb reveals detailed intelligence on all competitors and their activities...")
                            gs.messages.append("Intelligence gathering actions now provide comprehensive insights!")
                        elif upg.get("effect_key") == "hpc_cluster":
                            gs._add('compute', 20)
                            gs.messages.append(f"Upgrade purchased: {upg['name']} - Massive compute boost! Research effectiveness increased.")
                        elif upg.get("effect_key") == "research_automation":
                            gs.messages.append(f"Upgrade purchased: {upg['name']} - Research actions now benefit from available compute resources.")
                        else:
                            gs.messages.append(f"Upgrade purchased: {upg['name']}")
                        
                        # Log upgrade purchase
                        gs.logger.log_upgrade(upg["name"], upg["cost"], gs.turn)
                        
                        # Create smooth transition animation from button to icon
                        icon_rect = get_upgrade_icon_rect(idx, w, h)
                        gs._create_upgrade_transition(idx, rect, icon_rect)
                    else:
                        error_msg = f"Not enough money for {upg['name']} (need ${upg['cost']}, have ${gs.money})."
                        gs.messages.append(error_msg)
                        
                        # Track error for easter egg detection
                        gs.track_error(f"Insufficient money: {upg['name']}")
                else:
                    gs.messages.append(f"{upg['name']} already purchased.")
                    
                    # Track error for easter egg detection
                    gs.track_error(f"Already purchased: {upg['name']}")
                return None

        # Mute button (bottom right)
        mute_rect = get_mute_button_rect(w, h)
        if check_point_in_rect(mouse_pos, mute_rect):
            new_state = gs.sound_manager.toggle()
            status = "enabled" if new_state else "disabled"
            gs.messages.append(f"Sound {status}")
            return None

        # Office cat petting interaction - enhanced dev engagement feature
        if getattr(gs, 'office_cat_adopted', False):
            if self.pet_office_cat(mouse_pos):
                return None  # Cat was petted, interaction handled

        return None

    def handle_mouse_motion(self, mouse_pos: Tuple[int, int], w: int, h: int) -> None:
        """Handle mouse motion events for dragging functionality"""
        gs = self.game_state
        
        if gs.activity_log_being_dragged:
            # Update activity log position based on mouse movement
            new_x = mouse_pos[0] - gs.activity_log_drag_offset[0]
            new_y = mouse_pos[1] - gs.activity_log_drag_offset[1]
            
            # Get base position to calculate offset
            base_x, base_y = get_activity_log_base_position(w, h)
            
            # Constrain position to stay within screen bounds
            log_width = int(w * 0.44)
            log_height = int(h * 0.22)
            
            # Calculate new position with constraints
            new_offset_x = max(-base_x, min(w - log_width - base_x, new_x - base_x))
            new_offset_y = max(-base_y, min(h - log_height - base_y, new_y - base_y))
            
            gs.activity_log_position = (new_offset_x, new_offset_y)

    def handle_mouse_release(self, mouse_pos: Tuple[int, int], w: int, h: int) -> bool:
        """Handle mouse release events to stop dragging"""
        gs = self.game_state
        
        if gs.activity_log_being_dragged:
            gs.activity_log_being_dragged = False
            gs.activity_log_drag_offset = (0, 0)
            return True  # Indicate that a drag operation was completed
        return False

    def check_hover(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Check for UI element hover with robust error handling and provide context information."""
        gs = self.game_state
        
        try:
            # Reset all hover states
            gs.hovered_upgrade_idx = None
            gs.hovered_action_idx = None
            gs.endturn_hovered = False
            gs.current_context_info = None  # Reset context info
            
            # Check activity log area for hover FIRST (highest priority for specific interactions)
            activity_log_rect = get_activity_log_rect(w, h)
            if check_point_in_rect(mouse_pos, activity_log_rect):
                # Show context about activity log
                if "compact_activity_display" not in gs.upgrade_effects:
                    gs.current_context_info = {
                        'title': 'Activity Log',
                        'description': 'Shows recent events and actions. Shows events from the current turn only and clears automatically when you end your turn.',
                        'details': [
                            'Upgrade available: Compact Activity Display ($150)',
                            'Upgrade adds minimize button for better screen space management'
                        ]
                    }
                    return "You may purchase the ability to minimise this for $150!"
                elif hasattr(gs, 'activity_log_minimized') and gs.activity_log_minimized:
                    gs.current_context_info = {
                        'title': 'Activity Log (Minimized)',
                        'description': 'Activity log is currently minimized to save screen space.',
                        'details': ['Click expand button to show full log', 'Shows current turn events when expanded']
                    }
                    return "Activity Log (minimized) - Click expand button to show full log"
                else:
                    gs.current_context_info = {
                        'title': 'Activity Log',
                        'description': 'Shows recent events and actions from the current turn. Clears automatically when you end your turn.',
                        'details': ['Click minimize button to reduce screen space', 'Enhanced mode available later for full history']
                    }
                    return "Activity Log - Click minimize button to reduce screen space"
            
            # Check action buttons for hover - Handle filtered actions
            hovered_action = None
            if hasattr(gs, 'filtered_action_rects') and hasattr(gs, 'display_to_action_index_map'):
                # Use filtered action rects if available (when UI shows only unlocked actions)
                action_rects = gs.filtered_action_rects
                for display_idx, rect in enumerate(action_rects):
                    if check_point_in_rect(mouse_pos, rect):
                        if display_idx < len(gs.display_to_action_index_map):
                            original_idx = gs.display_to_action_index_map[display_idx]
                            gs.hovered_action_idx = original_idx
                            hovered_action = gs.gameplay_actions[original_idx]
                        break
            else:
                # Fallback to original action handling (show all actions)
                action_rects = get_action_rects(w, h)
                for idx, rect in enumerate(action_rects):
                    if check_point_in_rect(mouse_pos, rect):
                        gs.hovered_action_idx = idx
                        hovered_action = gs.gameplay_actions[idx]
                        break
            
            # Build context info for hovered action
            if hovered_action:
                action = hovered_action
                
                # Determine delegation status
                delegate_info = ""
                if action.get("delegatable", False) and gs.can_delegate_action(action):
                    delegate_ap = action.get("delegate_ap_cost", action.get("ap_cost", 1))
                    delegate_eff = action.get("delegate_effectiveness", 1.0)
                    if delegate_ap < action.get("ap_cost", 1):
                        delegate_info = f"Can delegate: {delegate_ap} AP, {int(delegate_eff*100)}% effectiveness"
                    else:
                        delegate_info = f"Can delegate: {int(delegate_eff*100)}% effectiveness"
                        
                # Get action requirements
                requirements = []
                if action.get("rules") and not action["rules"](gs):
                    requirements.append("Requirements not met")
                
                ap_cost = action.get("ap_cost", 1)
                if action['cost'] > gs.money:
                    requirements.append(f"Need ${action['cost']} (have ${gs.money})")
                if ap_cost > gs.action_points:
                    requirements.append(f"Need {ap_cost} AP (have {gs.action_points})")
                
                # Build context info
                details = []
                cost_str = f"${action['cost']}" if action['cost'] > 0 else "Free"
                ap_str = f"{ap_cost} AP" if ap_cost > 1 else "1 AP"
                details.append(f"Cost: {cost_str}, {ap_str}")
                
                if delegate_info:
                    details.append(delegate_info)
                if requirements:
                    details.extend(requirements)
                else:
                    details.append("[OK] Available to execute")
                
                gs.current_context_info = {
                    'title': action['name'],
                    'description': action['desc'],
                    'details': details
                }
                
                # Return legacy tooltip for compatibility
                affordable = action['cost'] <= gs.money and ap_cost <= gs.action_points
                status = "[OK] Available" if affordable else "[FAIL] Cannot afford"
                return f"{action['name']}: {action['desc']} (Cost: {cost_str}, {ap_str}) - {status}"
            
            # Check upgrade buttons for hover
            u_rects = get_upgrade_rects(w, h)
            for idx, rect in enumerate(u_rects):
                # Skip None rectangles (unavailable/hidden upgrades)
                if rect is None:
                    continue
                if check_point_in_rect(mouse_pos, rect):
                    gs.hovered_upgrade_idx = idx
                    upgrade = gs.upgrades[idx]
                    
                    # Build upgrade context
                    details = []
                    if not upgrade.get("purchased", False):
                        details.append(f"Cost: ${upgrade['cost']}")
                        if upgrade['cost'] <= gs.money:
                            details.append("[OK] Can afford")
                        else:
                            details.append(f"[FAIL] Need ${upgrade['cost'] - gs.money} more")
                        
                        # Add unlock requirements if any
                        if upgrade.get("turn_req") and gs.turn < upgrade["turn_req"]:
                            details.append(f"Unlocks turn {upgrade['turn_req']}")
                        if upgrade.get("staff_req") and gs.staff < upgrade["staff_req"]:
                            details.append(f"Requires {upgrade['staff_req']} staff")
                    else:
                        details.append("[OK] Purchased and active")
                        # Show effect details for purchased upgrades
                        if "effect" in upgrade:
                            details.append("Providing passive benefits")
                    
                    gs.current_context_info = {
                        'title': upgrade['name'],
                        'description': upgrade['desc'],
                        'details': details
                    }
                    
                    # Return legacy tooltip
                    if not upgrade.get("purchased", False):
                        affordable = upgrade['cost'] <= gs.money
                        status = "[OK] Available" if affordable else "[FAIL] Cannot afford"
                        return f"{upgrade['name']}: {upgrade['desc']} (Cost: ${upgrade['cost']}) - {status}"
                    else:
                        return f"{upgrade['name']}: {upgrade['desc']} (Purchased)"
            
            # Check end turn button for hover
            endturn_rect = get_endturn_rect(w, h)
            if check_point_in_rect(mouse_pos, endturn_rect):
                gs.endturn_hovered = True
                ap_remaining = gs.action_points
                
                details = []
                if ap_remaining > 0:
                    details.append(f"Warning: {ap_remaining} AP will be wasted")
                    details.append("Consider taking more actions this turn")
                else:
                    details.append("All AP spent efficiently")
                
                details.append("Advances to next turn")
                details.append("Processes selected actions and events")
                
                gs.current_context_info = {
                    'title': 'End Turn',
                    'description': 'Complete the current turn and advance to the next. All selected actions will be executed.',
                    'details': details
                }
                
                if ap_remaining > 0:
                    return f"End Turn ({ap_remaining} AP remaining - these will be wasted!)"
                else:
                    return "End Turn (All AP spent efficiently)"
            
            # Check resource area for hover
            # Money area
            money_rect = pygame.Rect(int(w*0.04), int(h*0.11), int(w*0.15), int(h*0.03))
            if check_point_in_rect(mouse_pos, money_rect):
                details = [f"Current: ${gs.money}"]
                if hasattr(gs, 'accounting_software_bought') and gs.accounting_software_bought:
                    change = getattr(gs, 'last_balance_change', 0)
                    if change != 0:
                        sign = "+" if change > 0 else ""
                        details.append(f"Last change: {sign}${change}")
                
                gs.current_context_info = {
                    'title': 'Money',
                    'description': 'Funds for actions, upgrades, and staff salaries. Earned through research progress.',
                    'details': details
                }
            
            # Staff area
            staff_rect = pygame.Rect(int(w*0.21), int(h*0.11), int(w*0.12), int(h*0.03))
            if check_point_in_rect(mouse_pos, staff_rect):
                details = [f"Total Staff: {gs.staff}"]
                if hasattr(gs, 'admin_staff'):
                    details.append(f"Admin: {gs.admin_staff}")
                if hasattr(gs, 'research_staff'):
                    details.append(f"Research: {gs.research_staff}")
                if hasattr(gs, 'ops_staff'):
                    details.append(f"Operations: {gs.ops_staff}")
                    
                gs.current_context_info = {
                    'title': 'Staff',
                    'description': 'Team members providing action points. Each staff member gives +0.5 AP per turn.',
                    'details': details
                }
            
            # Reputation area
            rep_rect = pygame.Rect(int(w*0.35), int(h*0.11), int(w*0.13), int(h*0.03))
            if check_point_in_rect(mouse_pos, rep_rect):
                gs.current_context_info = {
                    'title': 'Reputation',
                    'description': 'Public trust affecting funding opportunities. Gained through good decisions.',
                    'details': [f"Current: {gs.reputation}", "Higher reputation unlocks opportunities", "Can be lost through poor choices"]
                }
            
            # Action Points area
            ap_rect = pygame.Rect(int(w*0.49), int(h*0.11), int(w*0.12), int(h*0.03))
            if check_point_in_rect(mouse_pos, ap_rect):
                max_ap = gs.max_action_points
                details = [
                    f"Current: {gs.action_points}/{max_ap}",
                    f"Base: 3 + Staff bonus: {max_ap - 3}",
                    "Resets to maximum each turn"
                ]
                
                gs.current_context_info = {
                    'title': 'Action Points (AP)',
                    'description': 'Actions you can take this turn. Most actions cost 1 AP each.',
                    'details': details
                }
            
            # P(Doom) area
            doom_rect = pygame.Rect(int(w*0.62), int(h*0.11), int(w*0.18), int(h*0.03))
            if check_point_in_rect(mouse_pos, doom_rect):
                gs.current_context_info = {
                    'title': 'P(Doom)',
                    'description': 'Probability of existential catastrophe. Keep this low while making progress.',
                    'details': [
                        f"Current: {gs.doom}/{gs.max_doom}",
                        "Reduced by safety research",
                        "Game ends if it reaches maximum"
                    ]
                }
            
            # Compute area (second row)
            compute_rect = pygame.Rect(int(w*0.04), int(h*0.135), int(w*0.12), int(h*0.03))
            if check_point_in_rect(mouse_pos, compute_rect):
                details = [f"Current: {gs.compute}"]
                if hasattr(gs, 'employee_blobs') and gs.employee_blobs:
                    productive_employees = sum(1 for blob in gs.employee_blobs if blob.get('has_compute', False))
                    if productive_employees > 0:
                        details.append(f"Assigned to {productive_employees} employees")
                    else:
                        details.append("No employees currently assigned")
                
                gs.current_context_info = {
                    'title': 'Compute',
                    'description': 'Computational resources for research and employee productivity.',
                    'details': details
                }
            
            # No tooltip text for areas with context info only
            return None
            
        except Exception as e:
            # Log the error with context for debugging
            if hasattr(gs, 'game_logger'):
                gs.game_logger.log(f"Error in check_hover: mouse_pos={mouse_pos}, w={w}, h={h}, error={e}")
            # Return None gracefully so game continues to work
            return None

    def pet_office_cat(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle office cat petting interaction - core dev engagement feature!"""
        gs = self.game_state
        
        if not getattr(gs, 'office_cat_adopted', False):
            return False

        # Check if click is near the cat
        cat_x, cat_y = getattr(gs, 'office_cat_position', (400, 300))
        mx, my = mouse_pos

        # Cat is clickable in a 64x64 area
        if abs(mx - cat_x) <= 32 and abs(my - cat_y) <= 32:
            # Pet the cat! This is the main dev reward system
            gs.office_cat_total_pets = getattr(gs, 'office_cat_total_pets', 0) + 1
            gs.office_cat_last_petted = gs.turn

            # Show love emoji for 60 frames (2 seconds at 30 FPS)
            gs.office_cat_love_emoji_timer = 60
            gs.office_cat_love_emoji_pos = (cat_x + 16, cat_y - 20)

            # Small temporary morale boost - dev engagement reward
            if get_rng().random(f"cat_pet_doom_reduction_{gs.turn}_{gs.office_cat_total_pets}") < 0.2:
                gs._add('doom', -1)
                gs.messages.append("[HEART] Petting the cat provides immediate stress relief!")
            
            # Play cat sound if available
            if hasattr(gs, 'sound_manager'):
                gs.sound_manager.play_sound('blob')  # Reuse existing sound
            
            return True

        return False
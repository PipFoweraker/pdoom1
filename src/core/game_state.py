import random
import json
import os
import pygame
from typing import Tuple
from src.core.actions import ACTIONS
from src.core.upgrades import UPGRADES
from src.core.events import EVENTS
from src.services.game_logger import GameLogger
from src.services.sound_manager import SoundManager
from src.core.opponents import create_default_opponents
from src.features.event_system import Event, DeferredEventQueue, EventType, EventAction
from src.features.onboarding import onboarding
from src.ui.overlay_manager import OverlayManager
from src.services.error_tracker import ErrorTracker
from src.services.config_manager import get_current_config
from src.core.employee_subtypes import get_available_subtypes, apply_subtype_effects, get_hiring_complexity_level
from src.core.productive_actions import (get_employee_category, get_available_actions, 
                               check_action_requirements, get_default_action_index)
from src.features.end_game_scenarios import end_game_scenarios

SCORE_FILE = "local_highscore.json"

class GameState:
    def _add(self, attr, val):
        """
        Adds val to the given attribute, clamping where appropriate.
        Also records last_balance_change for 'money' for use in UI,
        if accounting software has been purchased.
        """
        if attr == 'money':
            # Track spending for board member trigger (only negative amounts)
            if val < 0:
                self.spend_this_turn += abs(val)
                # Play money spend sound for happy feedback
                self.sound_manager.play_money_spend_sound()
            
            # Only record balance change if accounting software is bought
            if hasattr(self, "accounting_software_bought") and self.accounting_software_bought:
                self.last_balance_change = val
            self.money = max(self.money + val, 0)
        elif attr == 'doom':
            old_doom = self.doom
            self.doom = min(max(self.doom + val, 0), self.max_doom)
            # Trigger high doom warning
            if old_doom < 70 and self.doom >= 70 and onboarding.should_show_mechanic_help('high_doom_warning'):
                onboarding.mark_mechanic_seen('high_doom_warning')
        elif attr == 'reputation':
            self.reputation = max(self.reputation + val, 0)
        elif attr == 'staff':
            old_staff = self.staff
            self.staff = max(self.staff + val, 0)
            # Update employee blobs when staff changes
            if val > 0:  # Hiring
                self._add_employee_blobs(val)
                # Trigger first-time help for staff hiring
                if old_staff <= 2 and self.staff > 2:  # First staff hire beyond starting staff
                    onboarding.mark_mechanic_seen('first_staff_hire')
            elif val < 0:  # Staff leaving
                self._remove_employee_blobs(old_staff - self.staff)
        elif attr == 'compute':
            self.compute = max(self.compute + val, 0)
        elif attr == 'research_progress':
            self.research_progress = max(self.research_progress + val, 0)
        elif attr == 'admin_staff':
            self.admin_staff = max(self.admin_staff + val, 0)
        elif attr == 'research_staff':
            self.research_staff = max(self.research_staff + val, 0)
        elif attr == 'ops_staff':
            self.ops_staff = max(self.ops_staff + val, 0)
        return None

# Ensure last_balance_change gets set on any direct subtraction/addition to money:
# For example, in end_turn, after maintenance:
# self._add('money', -maintenance_cost)
# (Replace raw self.money -= maintenance_cost with self._add('money', -maintenance_cost))

# In __init__, initialize:

    def __init__(self, seed):
        # Get current configuration
        config = get_current_config()
        starting_resources = config['starting_resources']
        ap_config = config['action_points']
        limits_config = config['resource_limits']
        milestones_config = config['milestones']
        
        self.last_balance_change = 0
        self.accounting_software_bought = False  # So the flag always exists
        
        # Core resources (from config)
        self.money = starting_resources['money']
        self.staff = starting_resources['staff']
        self.reputation = starting_resources['reputation']
        self.doom = starting_resources['doom']
        self.compute = starting_resources.get('compute', 0)
        self.research_progress = 0  # Track research progress for paper generation
        self.papers_published = 0  # Count of research papers published
        
        # Action Points system (from config)
        self.action_points = starting_resources['action_points']
        self.max_action_points = ap_config['base_ap_per_turn']
        self.ap_spent_this_turn = False  # Track if AP was spent for UI glow effects
        self.ap_glow_timer = 0  # Timer for AP glow animation
        
        # Phase 2: Staff-Based AP Scaling
        self.admin_staff = 0  # Admin assistants: +1.0 AP each
        self.research_staff = 0  # Research staff: Enable research action delegation
        self.ops_staff = 0  # Operations staff: Enable operational action delegation
        
        self.turn = 0
        self.max_doom = limits_config['max_doom']
        self.selected_actions = []
        self.selected_action_instances = []  # Track individual action instances for undo
        self.action_clicks_this_turn = {}  # Track clicks per action per turn
        self.staff_maintenance = 15
        self.seed = seed
        self.upgrades = [dict(u) for u in UPGRADES]
        self.upgrade_effects = set()
        self.messages = ["Game started! Select actions, then End Turn."]
        self.game_over = False
        self.end_game_scenario = None  # Will hold the EndGameScenario when game ends
        self.highscore = self.load_highscore()
        
        # Initialize opponents system (replaces simple opp_progress)
        self.opponents = create_default_opponents()
        self.known_opp_progress = None  # Legacy compatibility for UI

        # Employee blob system
        self.employee_blobs = []  # List of employee blob objects with positions and states
        self.sound_manager = SoundManager()  # Sound system
        
        # Manager system for milestone-driven special events
        self.managers = []  # List of manager blob objects
        self.manager_milestone_triggered = False  # Track if 9th employee milestone was triggered
        self.spend_this_turn = 0  # Track spending per turn for board member trigger
        
        # Board member system for spend threshold milestone
        self.board_members = 0  # Number of board members installed
        self.board_milestone_triggered = False  # Track if board member milestone was triggered
        self.audit_risk_level = 0  # Audit risk accumulation for compliance penalties
        
        # Onboarding system integration
        self.onboarding_started = False  # Track if tutorial has been offered
        
        # For hover/tooltip (which upgrade is hovered)
        self.hovered_upgrade_idx = None
        self.hovered_action_idx = None
        self.endturn_hovered = False

        # Scrollable event log feature
        self.scrollable_event_log_enabled = False
        self.event_log_history = []  # Full history of all messages
        self.event_log_scroll_offset = 0
        
        # Activity log minimization feature
        self.activity_log_minimized = False  # Whether activity log is currently minimized
        
        # Activity log drag/move functionality
        self.activity_log_being_dragged = False  # Whether activity log is being dragged
        self.activity_log_drag_offset = (0, 0)  # Offset from mouse to log position when dragging starts
        self.activity_log_position = (0, 0)  # Custom position offset for activity log (default 0,0 means original position)

        # Tutorial and onboarding system
        self.tutorial_enabled = True  # Whether tutorial is enabled (default True for new players)
        self.tutorial_shown_milestones = set()  # Track which milestone tutorials have been shown
        self.pending_tutorial_message = None  # Current tutorial message waiting to be shown
        self.first_game_launch = True  # Track if this is the first game launch
        
        # Employee hiring dialog system
        self.pending_hiring_dialog = None  # Current hiring dialog waiting for player selection

        # Copy modular content
        self.actions = [dict(a) for a in ACTIONS]
        self.events = [dict(e) for e in EVENTS]
        
        # Enhanced event system (from config)
        gameplay_config = config.get('gameplay', {})
        self.deferred_events = DeferredEventQueue()
        self.pending_popup_events = []  # Events waiting for player action
        self.enhanced_events_enabled = gameplay_config.get('enhanced_events_enabled', False)  # Flag to enable new event types
        
        # Initialize game logger
        self.logger = GameLogger(seed)
        
        # Initialize UI overlay management system
        self.overlay_manager = OverlayManager()
        
        # Initialize error tracking system (replaces duplicate error tracking logic)
        self.error_tracker = ErrorTracker(
            sound_manager=self.sound_manager,
            message_callback=lambda msg: self.messages.append(msg)
        )
        self.logger = GameLogger(seed)
        
        # UI Transition System for smooth visual feedback
        self.ui_transitions = []  # List of active UI transition animations
        self.upgrade_transitions = {}  # Track transitions for individual upgrades
        
        # Turn Processing State for reliable input handling
        self.turn_processing = False  # True during turn transition
        self.turn_processing_timer = 0  # Timer for turn transition duration
        self.turn_processing_duration = 30  # Frames for turn transition (1 second at 30 FPS)
        
        # Game Flow Improvements
        self.delayed_actions = []  # Actions that resolve after N turns
        self.daily_news = []  # News feed for turn feedback
        self.spend_this_turn_display_shown = False  # Track if spend display has been shown
        self.spend_display_permanent = False  # Whether spend display is permanently visible
        
        # Initialize employee blobs for starting staff
        self._initialize_employee_blobs()
        
        # Load tutorial settings (after initialization)
        self.load_tutorial_settings()

    def calculate_max_ap(self):
        """
        Calculate maximum Action Points per turn based on staff composition.
        
        Uses configuration values for:
        - Base AP per turn
        - Staff AP bonus per regular staff member  
        - Admin AP bonus per admin assistant
        - Maximum AP cap to prevent excessive accumulation
        
        Returns:
            int: Maximum action points for the current turn
        """
        config = get_current_config()
        ap_config = config['action_points']
        
        base = ap_config['base_ap_per_turn']
        staff_bonus = self.staff * ap_config['staff_ap_bonus']
        admin_bonus = self.admin_staff * ap_config['admin_ap_bonus']
        calculated_ap = base + staff_bonus + admin_bonus
        
        # Apply maximum cap
        max_cap = ap_config['max_ap_per_turn']
        return int(min(calculated_ap, max_cap))
    
    def add_delayed_action(self, action_name: str, delay_turns: int, effects: dict):
        """
        Add an action that will resolve after a specified delay.
        
        Args:
            action_name: Name of the delayed action
            delay_turns: Number of turns to wait before resolving
            effects: Dictionary of effects to apply when resolved
        """
        delayed_action = {
            'action_name': action_name,
            'resolve_turn': self.turn + delay_turns,
            'effects': effects,
            'added_turn': self.turn
        }
        self.delayed_actions.append(delayed_action)
        
        # Add feedback message
        self.messages.append(f"{action_name} will complete in {delay_turns} turn{'s' if delay_turns != 1 else ''}.")
    
    def process_delayed_actions(self):
        """Process and resolve any delayed actions that are ready."""
        resolved_actions = []
        
        for action in self.delayed_actions[:]:  # Use slice copy to avoid modification during iteration
            if action['resolve_turn'] <= self.turn:
                # Apply the delayed effects
                effects = action['effects']
                
                for resource, value in effects.items():
                    if hasattr(self, resource):
                        if resource in ['money', 'doom', 'reputation', 'staff', 'admin_staff']:
                            self._add(resource, value)
                        else:
                            setattr(self, resource, getattr(self, resource) + value)
                
                # Add completion message
                self.messages.append(f"✓ {action['action_name']} completed!")
                
                resolved_actions.append(action)
                self.delayed_actions.remove(action)
        
        return resolved_actions
    
    def get_daily_news(self) -> str:
        """Generate daily news feed content for the current turn."""
        news_items = [
            "AI Research Quarterly reports steady progress across the industry.",
            "New safety protocols under consideration by regulatory bodies.",
            "Tech giants announce increased AI safety investments.",
            "Academic conference highlights latest alignment research.",
            "Public opinion polls show growing AI awareness.",
            "Government panel reviews AI development guidelines.",
            "Industry leaders call for responsible AI development.",
            "Research community debates next-generation safety measures.",
            "International cooperation on AI safety standards discussed.",
            "Breakthrough in interpretability research announced.",
            "New funding opportunities for safety research unveiled.",
            "Ethics review board examines AI deployment policies."
        ]
        
        # Use turn number to ensure consistent news per turn
        random.seed(f"news_{self.seed}_{self.turn}")
        selected_news = random.choice(news_items)
        random.seed()  # Reset to normal randomness
        
        return f"📰 Day {self.turn + 1}: {selected_news}"
    
    def update_spend_tracking(self):
        """Update spend tracking display logic."""
        if self.spend_this_turn > 0:
            if not self.spend_this_turn_display_shown:
                # First time spending multiple actions in a turn
                spend_actions_count = len([a for a in self.selected_actions if any(cost > 0 for cost in [a.get('money_cost', 0), a.get('reputation_cost', 0)])])
                
                if spend_actions_count > 1:
                    self.spend_this_turn_display_shown = True
                    self.messages.append(f"💰 Total spend this turn: ${self.spend_this_turn}")
                    
                    # If this happens again, make display permanent
                    if hasattr(self, '_previous_multi_spend'):
                        self.spend_display_permanent = True
                        self.messages.append("💰 Spend tracking enabled permanently.")
                    else:
                        self._previous_multi_spend = True

    def can_delegate_action(self, action):
        """
        Check if an action can be delegated based on staff requirements.
        
        Args:
            action (dict): The action to check for delegation
            
        Returns:
            bool: True if action can be delegated, False otherwise
        """
        if not action.get("delegatable", False):
            return False
            
        delegate_staff_req = action.get("delegate_staff_req", 0)
        
        # Check if we have enough specialized staff based on action type
        # Research actions require research staff
        if action["name"] in ["Safety Research", "Governance Research"]:
            return self.research_staff >= delegate_staff_req
        # Operational actions require operations staff  
        elif action["name"] in ["Buy Compute"]:
            return self.ops_staff >= delegate_staff_req
        
        return False
    
    def execute_action_with_delegation(self, action_idx, delegate=False):
        """
        Execute an action with optional delegation.
        
        Args:
            action_idx (int): Index of the action to execute
            delegate (bool): Whether to delegate the action
            
        Returns:
            bool: True if action was executed, False if not enough resources
        """
        action = self.actions[action_idx]
        
        # Determine AP cost and effectiveness
        if delegate and self.can_delegate_action(action):
            ap_cost = action.get("delegate_ap_cost", action.get("ap_cost", 1))
            effectiveness = action.get("delegate_effectiveness", 1.0)
            delegation_info = " (delegated)"
        else:
            ap_cost = action.get("ap_cost", 1)
            effectiveness = 1.0
            delegation_info = ""
            delegate = False  # Can't delegate if requirements not met
        
        # Check if we have enough AP and money
        if self.action_points < ap_cost:
            error_msg = f"Not enough Action Points for {action['name']} (need {ap_cost}, have {self.action_points})."
            self.messages.append(error_msg)
            
            # Track error for easter egg detection
            self.track_error(f"Insufficient AP: {action['name']}")
            
            # Trigger first-time help for AP exhaustion
            if onboarding.should_show_mechanic_help('action_points_exhausted'):
                onboarding.mark_mechanic_seen('action_points_exhausted')
            return False
        
        if self.money < action["cost"]:
            error_msg = f"Not enough money for {action['name']} (need ${action['cost']}, have ${self.money})."
            self.messages.append(error_msg)
            
            # Track error for easter egg detection
            self.track_error(f"Insufficient money: {action['name']}")
            
            return False
        
        # Execute the action
        self.selected_actions.append(action_idx)
        self.messages.append(f"Selected: {action['name']}{delegation_info}")
        
        # Store delegation info for end_turn processing
        if not hasattr(self, '_action_delegations'):
            self._action_delegations = {}
        self._action_delegations[action_idx] = {
            'delegated': delegate,
            'effectiveness': effectiveness,
            'ap_cost': ap_cost
        }
        
        return True

    def execute_action_by_keyboard(self, action_idx):
        """
        Execute an action via keyboard shortcut (1-9 keys).
        Now routes through unified action handler.
        
        Args:
            action_idx (int): Index of the action to execute (0-8 for keys 1-9)
            
        Returns:
            bool: True if action was executed successfully, False otherwise
        """
        if self.game_over:
            return False
            
        # Check for undo (if action is already selected, try to undo it)
        is_undo = action_idx in self.selected_actions
        
        result = self.attempt_action_selection(action_idx, is_undo)
        
        if result['message']:
            # Message is already added by attempt_action_selection, but we need to handle error tracking
            if not result['success'] and "Not enough Action Points" in result['message']:
                # Error tracking for easter egg
                if self.track_error(result['message']):
                    self.sound_manager.play_error_beep()
        
        return result['success']

    def attempt_action_selection(self, action_idx, is_undo=False):
        """
        Unified handler for all action selection attempts (both keyboard and mouse).
        
        Args:
            action_idx (int): Index of the action to select/unselect
            is_undo (bool): True if this is an undo operation
            
        Returns:
            dict: Result with 'success', 'message', 'play_sound' keys
        """
        if action_idx >= len(self.actions) or action_idx < 0:
            return {'success': False, 'message': None, 'play_sound': False}
            
        action = self.actions[action_idx]
        
        if is_undo:
            return self._handle_action_undo(action_idx, action)
        else:
            return self._handle_action_selection(action_idx, action)
    
    def _handle_action_selection(self, action_idx, action):
        """Handle selecting (clicking) an action."""
        # Check max clicks per action per turn (only if specified in action)
        if 'max_clicks_per_turn' in action:
            max_clicks = action['max_clicks_per_turn']
            current_clicks = self.action_clicks_this_turn.get(action_idx, 0)
            
            if current_clicks >= max_clicks:
                error_msg = f"{action['name']} already used maximum times this turn ({max_clicks})."
                self.messages.append(error_msg)
                return {
                    'success': False,
                    'message': error_msg,
                    'play_sound': False
                }
        
        # Check if action is available (rules constraint)
        if action.get("rules") and not action["rules"](self):
            error_msg = f"{action['name']} is not available yet."
            self.messages.append(error_msg)
            return {
                'success': False, 
                'message': error_msg,
                'play_sound': False
            }
        
        # Check if delegation would be beneficial (lower AP cost)
        delegate = False
        if (action.get("delegatable", False) and 
            self.can_delegate_action(action) and
            action.get("delegate_ap_cost", action.get("ap_cost", 1)) < action.get("ap_cost", 1)):
            delegate = True
        
        # Determine AP cost and effectiveness
        if delegate:
            ap_cost = action.get("delegate_ap_cost", action.get("ap_cost", 1))
            effectiveness = action.get("delegate_effectiveness", 1.0)
            delegation_info = " (delegated)"
        else:
            ap_cost = action.get("ap_cost", 1)
            effectiveness = 1.0
            delegation_info = ""
        
        # Check AP availability
        if self.action_points < ap_cost:
            error_msg = f"Not enough Action Points for {action['name']} (need {ap_cost}, have {self.action_points})."
            self.messages.append(error_msg)
            # Track error for easter egg detection
            self.track_error(f"Insufficient AP: {action['name']}")
            return {
                'success': False,
                'message': error_msg,
                'play_sound': False
            }
        
        # Check money availability
        if self.money < action["cost"]:
            error_msg = f"Not enough money for {action['name']} (need ${action['cost']}, have ${self.money})."
            self.messages.append(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'play_sound': False
            }
        
        # Create action instance for tracking
        action_instance = {
            'action_idx': action_idx,
            'delegated': delegate,
            'ap_cost': ap_cost,
            'effectiveness': effectiveness,
            'instance_id': len(self.selected_action_instances)  # Unique identifier
        }
        
        # Add to selected actions (immediate deduction)
        self.selected_actions.append(action_idx)
        self.selected_action_instances.append(action_instance)
        
        # Track clicks per action per turn (only if action has limits)
        if 'max_clicks_per_turn' in action:
            self.action_clicks_this_turn[action_idx] = self.action_clicks_this_turn.get(action_idx, 0) + 1
        
        # Immediate AP deduction
        self.action_points -= ap_cost
        self.ap_spent_this_turn = True
        self.ap_glow_timer = 30
        
        # Store delegation info for end_turn processing
        if not hasattr(self, '_action_delegations'):
            self._action_delegations = {}
        self._action_delegations[action_idx] = {
            'delegated': delegate,
            'effectiveness': effectiveness,
            'ap_cost': ap_cost
        }
        
        success_msg = f"Selected: {action['name']}{delegation_info}"
        self.messages.append(success_msg)
        
        return {
            'success': True,
            'message': success_msg,
            'play_sound': True
        }
    
    def _handle_action_undo(self, action_idx, action):
        """Handle unselecting (undoing) an action."""
        # Find the most recent instance of this action
        action_instance = None
        instance_index = None
        
        for i in range(len(self.selected_action_instances) - 1, -1, -1):
            if self.selected_action_instances[i]['action_idx'] == action_idx:
                action_instance = self.selected_action_instances[i]
                instance_index = i
                break
        
        if action_instance is None:
            return {
                'success': False,
                'message': f"No selected instance of {action['name']} to undo.",
                'play_sound': False
            }
        
        # Remove the action instance
        self.selected_action_instances.pop(instance_index)
        
        # Remove from selected_actions (remove last occurrence)
        for i in range(len(self.selected_actions) - 1, -1, -1):
            if self.selected_actions[i] == action_idx:
                self.selected_actions.pop(i)
                break
        
        # Refund AP
        self.action_points += action_instance['ap_cost']
        
        # Clean up delegation info if no more instances of this action
        if action_idx not in [inst['action_idx'] for inst in self.selected_action_instances]:
            if hasattr(self, '_action_delegations') and action_idx in self._action_delegations:
                del self._action_delegations[action_idx]
        
        delegation_suffix = " (delegated)" if action_instance['delegated'] else ""
        undo_msg = f"Undid: {action['name']}{delegation_suffix} (refunded {action_instance['ap_cost']} AP)"
        self.messages.append(undo_msg)
        
        return {
            'success': True,
            'message': undo_msg,
            'play_sound': False  # No sound on undo as required
        }

    def _execute_action_with_effectiveness(self, action, effect_type, effectiveness):
        """
        Execute an action effect with reduced effectiveness.
        
        Args:
            action (dict): The action to execute
            effect_type (str): Either "upside" or "downside"
            effectiveness (float): Effectiveness multiplier (0.0 to 1.0)
        """
        if effect_type not in action:
            return
            
        # Store original values to restore after execution
        original_doom = self.doom
        original_reputation = self.reputation
        original_money = self.money
        original_staff = self.staff
        original_compute = self.compute
        original_research_progress = self.research_progress
        
        # Execute the effect
        action[effect_type](self)
        
        # Apply effectiveness reduction to the changes
        if effectiveness < 1.0:
            # Calculate the changes that occurred
            doom_change = self.doom - original_doom
            rep_change = self.reputation - original_reputation
            money_change = self.money - original_money
            staff_change = self.staff - original_staff
            compute_change = self.compute - original_compute
            research_change = self.research_progress - original_research_progress
            
            # Restore original values
            self.doom = original_doom
            self.reputation = original_reputation
            self.money = original_money
            self.staff = original_staff
            self.compute = original_compute
            self.research_progress = original_research_progress
            
            # Apply reduced changes
            if doom_change != 0:
                self._add('doom', int(doom_change * effectiveness))
            if rep_change != 0:
                self._add('reputation', int(rep_change * effectiveness))
            if money_change != 0:
                self._add('money', int(money_change * effectiveness))
            if staff_change != 0:
                self._add('staff', int(staff_change * effectiveness))
            if compute_change != 0:
                self._add('compute', int(compute_change * effectiveness))
            if research_change != 0:
                self._add('research_progress', int(research_change * effectiveness))
            
            # Add message about reduced effectiveness
            if effectiveness < 1.0:
                self.messages.append(f"Delegated action had {int(effectiveness * 100)}% effectiveness.")

    def _initialize_employee_blobs(self):
        """Initialize employee blobs for starting staff with improved positioning"""
        import math
        for i in range(self.staff):
            # Use improved positioning that avoids UI overlap
            target_x, target_y = self._calculate_blob_position(i)
            
            blob = {
                'id': i,
                'x': target_x,
                'y': target_y, 
                'target_x': target_x,
                'target_y': target_y,
                'has_compute': False,
                'productivity': 0.0,
                'animation_progress': 1.0,  # Already positioned
                'type': 'employee',  # Track blob type
                'managed_by': None,  # Which manager manages this employee (None if unmanaged)
                'unproductive_reason': None,  # Reason for being unproductive (for overlay display)
                'subtype': 'generalist',  # Default employee subtype
                'productive_action_index': 0,  # Default to first action
                'productive_action_bonus': 1.0,  # Current productivity bonus
                'productive_action_active': False  # Whether productive action is active
            }
            self.employee_blobs.append(blob)
    
    def _add_employee_blobs(self, count):
        """Add new employee blobs with animation from side and improved positioning"""
        import math
        for i in range(count):
            blob_id = len(self.employee_blobs)
            # Use improved positioning that avoids UI overlap
            target_x, target_y = self._calculate_blob_position(blob_id)
            
            blob = {
                'id': blob_id,
                'x': -50,  # Start off-screen left
                'y': target_y,
                'target_x': target_x, 
                'target_y': target_y,
                'has_compute': False,
                'productivity': 0.0,
                'animation_progress': 0.0,  # Will animate in
                'type': 'employee',  # Track blob type
                'managed_by': None,  # Which manager manages this employee (None if unmanaged)
                'unproductive_reason': None,  # Reason for being unproductive (for overlay display)
                'subtype': 'generalist',  # Default employee subtype
                'productive_action_index': 0,  # Default to first action
                'productive_action_bonus': 1.0,  # Current productivity bonus
                'productive_action_active': False  # Whether productive action is active
            }
            self.employee_blobs.append(blob)
            
            # Play sound for new employee
            self.sound_manager.play_blob_sound()
    
    def _calculate_blob_position(self, blob_index, screen_w=1200, screen_h=800):
        """
        Calculate initial blob position in the center of screen.
        Blobs will then dynamically move away from UI elements through collision detection.
        
        Args:
            blob_index (int): Index of the blob (for initial positioning variation)
            screen_w (int): Screen width (default 1200 for backward compatibility) 
            screen_h (int): Screen height (default 800 for backward compatibility)
            
        Returns:
            tuple: (x, y) initial position for the blob (centered with small variation)
        """
        import math
        
        # Start all blobs in the center of the screen
        center_x = screen_w // 2
        center_y = screen_h // 2
        
        # Add small initial variation to prevent all blobs from being exactly on top of each other
        # Use a spiral pattern for initial positioning
        if blob_index == 0:
            return center_x, center_y
        
        # Create a spiral outward from center for initial positioning
        angle = blob_index * 2.4  # Golden angle for nice spiral distribution
        radius = blob_index * 15   # Increase radius for each blob
        
        x = center_x + int(radius * math.cos(angle)) 
        y = center_y + int(radius * math.sin(angle))
        
        # Ensure positions stay within screen bounds
        blob_radius = 25
        x = max(blob_radius, min(screen_w - blob_radius, x))
        y = max(blob_radius, min(screen_h - blob_radius, y))
        
        return x, y
    
    def _get_ui_element_rects(self, screen_w=1200, screen_h=800):
        """
        Get rectangles of all UI elements that employee blobs should avoid.
        
        Args:
            screen_w (int): Screen width
            screen_h (int): Screen height
            
        Returns:
            list: List of (x, y, width, height) rectangles representing UI elements
        """
        ui_rects = []
        
        # Action buttons (left side)
        action_rects = self._get_action_rects(screen_w, screen_h)
        ui_rects.extend(action_rects)
        
        # Upgrade buttons and icons (right side)
        upgrade_rects = self._get_upgrade_rects(screen_w, screen_h)
        for rect in upgrade_rects:
            if rect is not None:  # Some upgrades might not have rects if purchased
                ui_rects.append(rect)
        
        # End turn button (bottom center)
        endturn_rect = self._get_endturn_rect(screen_w, screen_h)
        ui_rects.append(endturn_rect)
        
        # Resource display area (top)
        resource_rect = (0, 0, screen_w, int(screen_h * 0.25))
        ui_rects.append(resource_rect)
        
        # Message log area (bottom left)
        log_rect = (int(screen_w*0.04), int(screen_h*0.74), int(screen_w * 0.44), int(screen_h * 0.22))
        ui_rects.append(log_rect)
        
        # Opponents panel (between resources and actions)
        opponents_rect = (int(screen_w * 0.04), int(screen_h * 0.19), int(screen_w * 0.92), int(screen_h * 0.08))
        ui_rects.append(opponents_rect)
        
        # Mute button (bottom right)
        mute_rect = self._get_mute_button_rect(screen_w, screen_h)
        ui_rects.append(mute_rect)
        
        return ui_rects
    
    def _check_blob_ui_collision(self, blob_x, blob_y, blob_radius, ui_rects):
        """
        Check if a blob collides with any UI element.
        
        Args:
            blob_x (float): Blob center x position
            blob_y (float): Blob center y position
            blob_radius (float): Blob radius
            ui_rects (list): List of UI element rectangles
            
        Returns:
            tuple: (collides, repulsion_force_x, repulsion_force_y)
        """
        total_repulsion_x = 0
        total_repulsion_y = 0
        collides = False
        
        for rect in ui_rects:
            rx, ry, rw, rh = rect
            
            # Find closest point on rectangle to blob center
            closest_x = max(rx, min(blob_x, rx + rw))
            closest_y = max(ry, min(blob_y, ry + rh))
            
            # Calculate distance from blob center to closest point
            dx = blob_x - closest_x
            dy = blob_y - closest_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            # If distance is less than blob radius, there's a collision
            if distance < blob_radius + 10:  # Add 10px buffer zone
                collides = True
                
                # Calculate repulsion force
                if distance > 0:
                    # Normalize direction and apply repulsion strength
                    repulsion_strength = (blob_radius + 20 - distance) * 0.1
                    repulsion_x = (dx / distance) * repulsion_strength
                    repulsion_y = (dy / distance) * repulsion_strength
                else:
                    # If blob is exactly on the edge, push away from rectangle center
                    rect_center_x = rx + rw / 2
                    rect_center_y = ry + rh / 2
                    repulsion_x = (blob_x - rect_center_x) * 0.1
                    repulsion_y = (blob_y - rect_center_y) * 0.1
                
                total_repulsion_x += repulsion_x
                total_repulsion_y += repulsion_y
        
        return collides, total_repulsion_x, total_repulsion_y
    
    def _update_blob_positions_dynamically(self, screen_w=1200, screen_h=800):
        """
        Update blob positions dynamically to avoid UI elements.
        This method should be called every frame to ensure continuous movement.
        
        Args:
            screen_w (int): Screen width
            screen_h (int): Screen height
        """
        if not self.employee_blobs:
            return
        
        ui_rects = self._get_ui_element_rects(screen_w, screen_h)
        blob_radius = 25
        
        # Update each blob's position
        for i, blob in enumerate(self.employee_blobs):
            # Skip if blob is still animating in from the side
            if blob['animation_progress'] < 1.0:
                continue
            
            current_x = blob['x']
            current_y = blob['y']
            
            # Check for UI collisions
            collides, repulsion_x, repulsion_y = self._check_blob_ui_collision(
                current_x, current_y, blob_radius, ui_rects
            )
            
            # Apply blob-to-blob repulsion to prevent clustering
            for j, other_blob in enumerate(self.employee_blobs):
                if i != j and other_blob['animation_progress'] >= 1.0:
                    other_x = other_blob['x']
                    other_y = other_blob['y']
                    
                    dx = current_x - other_x
                    dy = current_y - other_y
                    distance = (dx * dx + dy * dy) ** 0.5
                    
                    min_distance = blob_radius * 2 + 5  # Minimum distance between blobs
                    if distance < min_distance and distance > 0:
                        # Apply repulsion between blobs
                        repulsion_strength = (min_distance - distance) * 0.05
                        repulsion_x += (dx / distance) * repulsion_strength
                        repulsion_y += (dy / distance) * repulsion_strength
            
            # Apply slight attraction to screen center to prevent blobs from drifting too far
            center_x = screen_w / 2
            center_y = screen_h / 2
            center_attraction = 0.002
            repulsion_x += (center_x - current_x) * center_attraction
            repulsion_y += (center_y - current_y) * center_attraction
            
            # Apply movement with damping
            if abs(repulsion_x) > 0.1 or abs(repulsion_y) > 0.1:
                # Cap maximum movement speed
                max_speed = 2.0
                speed = (repulsion_x * repulsion_x + repulsion_y * repulsion_y) ** 0.5
                if speed > max_speed:
                    repulsion_x = (repulsion_x / speed) * max_speed
                    repulsion_y = (repulsion_y / speed) * max_speed
                
                # Update blob position
                new_x = current_x + repulsion_x
                new_y = current_y + repulsion_y
                
                # Keep blobs within screen bounds
                new_x = max(blob_radius, min(screen_w - blob_radius, new_x))
                new_y = max(blob_radius, min(screen_h - blob_radius, new_y))
                
                blob['x'] = new_x
                blob['y'] = new_y
                
                # Update target position to current position for smooth animation
                blob['target_x'] = new_x
                blob['target_y'] = new_y
            
    def _add_manager_blob(self):
        """Add a new manager blob with animation from side"""
        import math
        blob_id = len(self.employee_blobs)
        # Position managers slightly offset from regular employees
        target_x = 350 + (len(self.managers) % 2) * 300  # Alternate sides
        target_y = 450 + (len(self.managers) // 2) * 120  # Stack down
        
        manager_blob = {
            'id': blob_id,
            'x': -50,  # Start off-screen left
            'y': target_y,
            'target_x': target_x,
            'target_y': target_y,
            'has_compute': True,  # Managers always have access
            'productivity': 1.0,
            'animation_progress': 0.0,  # Will animate in
            'type': 'manager',  # Manager type
            'managed_employees': [],  # List of employee IDs this manager oversees
            'management_capacity': 9,  # Can manage up to 9 employees
            'subtype': 'manager',  # Manager subtype
            'productive_action_index': 0,  # Default to first action
            'productive_action_bonus': 1.0,  # Current productivity bonus
            'productive_action_active': False  # Whether productive action is active
        }
        
        # Add to both general blobs and specific managers list
        self.employee_blobs.append(manager_blob)
        self.managers.append(manager_blob)
        
        # Play special sound effect for manager hire
        self.sound_manager.play_blob_sound()
        
        # Reassign employee management after adding new manager
        self._reassign_employee_management()
        
    def _reassign_employee_management(self):
        """Reassign employees to managers based on capacity and efficiency"""
        # Reset all employee assignments
        employees = [blob for blob in self.employee_blobs if blob['type'] == 'employee']
        managers = [blob for blob in self.employee_blobs if blob['type'] == 'manager']
        
        # Clear previous assignments
        for employee in employees:
            employee['managed_by'] = None
            employee['unproductive_reason'] = None
        for manager in managers:
            manager['managed_employees'] = []
        
        # Assign employees to managers (max 9 per manager)
        manager_idx = 0
        for i, employee in enumerate(employees):
            if manager_idx < len(managers):
                manager = managers[manager_idx]
                if len(manager['managed_employees']) < manager['management_capacity']:
                    # Assign this employee to current manager
                    employee['managed_by'] = manager['id']
                    manager['managed_employees'].append(employee['id'])
                else:
                    # Current manager is full, move to next
                    manager_idx += 1
                    if manager_idx < len(managers):
                        manager = managers[manager_idx]
                        employee['managed_by'] = manager['id']
                        manager['managed_employees'].append(employee['id'])
                    else:
                        # No more managers available - employee becomes unmanaged
                        employee['unproductive_reason'] = 'no_manager'
            else:
                # No managers available for this employee
                employee['unproductive_reason'] = 'no_manager'
                
    def _hire_manager(self):
        """Hire a new manager to oversee employees"""
        # Add manager blob to the system
        self._add_manager_blob()
        
        # Increment staff count for the manager
        self.staff += 1
        
        # Add success message
        self.messages.append(f"Manager hired! Now managing {len(self.managers)} team cluster(s).")
        
        # Check if this is the first manager hire (milestone)
        if len(self.managers) == 1 and not self.manager_milestone_triggered:
            self.manager_milestone_triggered = True
            self.messages.append("MILESTONE: First manager hired! Teams beyond 9 employees now need management to stay productive.")
            
            # Show tutorial for manager system
            self.show_tutorial_message(
                "manager_system",
                "Manager System Unlocked!",
                "You've hired your first manager! This unlocks the management system:\n\n"
                "• Each manager can oversee up to 9 employees\n"
                "• Unmanaged employees beyond 9 become unproductive (shown with red slash)\n"
                "• Managers appear as green blobs vs blue employee blobs\n"
                "• Manager hiring costs 1.5x normal employee cost\n\n"
                "Plan your team structure carefully as you scale!"
            )
        
        return None
        
    def _check_board_member_milestone(self):
        """Check if board member milestone should be triggered"""
        # Only trigger if not already triggered and no accounting software
        if (not self.board_milestone_triggered and 
            not self.accounting_software_bought and 
            self.spend_this_turn > 10000):
            
            # Install 2 board members
            self.board_members = 2
            self.board_milestone_triggered = True
            
            self.messages.append("MILESTONE: Excessive spending without accounting oversight!")
            self.messages.append("Board has installed 2 Board Members for compliance monitoring.")
            self.messages.append("Search action unlocked. Audit risk penalties now active until compliant.")
            
            # Show tutorial for board member system
            self.show_tutorial_message(
                "board_member_system",
                "Board Member Oversight Activated!",
                "Your spending exceeded $10,000 without accounting software!\n\n"
                "Board members have been installed with oversight powers:\n\n"
                "• 2 board members now monitor your compliance\n"
                "• Search action unlocked (20% success rate for various benefits)\n"
                "• Audit risk accumulates until you become compliant\n"
                "• Purchase accounting software to prevent future oversight\n\n"
                "Manage your finances carefully to avoid penalties!"
            )
            
            # Start accumulating audit risk
            self.audit_risk_level = 1
            
        # Apply static effects if board members are active
        if self.board_members > 0 and not self.accounting_software_bought:
            # Accumulate audit risk
            self.audit_risk_level += 1
            
            # Apply penalties based on audit risk level
            if self.audit_risk_level > 5:
                # Reputation penalty for non-compliance
                rep_penalty = min(3, self.audit_risk_level - 5)
                self._add('reputation', -rep_penalty)
                self.messages.append(f"Compliance audit failed! Reputation penalty: -{rep_penalty}")
                
            if self.audit_risk_level > 10:
                # Financial penalty for severe non-compliance
                fine = min(5000, (self.audit_risk_level - 10) * 1000)
                self._add('money', -fine)
                self.messages.append(f"Regulatory fine imposed: ${fine} for non-compliance!")
                
        return None
        
    def _board_search(self):
        """Perform board-mandated search action with 20% success rate"""
        if random.random() < 0.2:  # 20% success rate
            # Successful search - find something valuable
            search_results = [
                ("regulatory compliance", lambda: self._add('reputation', 3)),
                ("cost savings opportunity", lambda: self._add('money', random.randint(200, 500))),
                ("process efficiency", lambda: self._add('doom', -2)),
                ("staff optimization", lambda: None)  # Just a message
            ]
            
            result_name, result_effect = random.choice(search_results)
            result_effect()
            self.messages.append(f"Search successful! Discovered {result_name}.")
            
            # Reduce audit risk on successful search
            if self.audit_risk_level > 0:
                self.audit_risk_level = max(0, self.audit_risk_level - 2)
                self.messages.append("Successful search reduces audit risk.")
                
        else:
            # Failed search
            search_failures = [
                "No significant findings in this search.",
                "Search yielded minimal actionable intelligence.",
                "Investigation remains ongoing with no conclusive results.",
                "Search parameters require refinement for better outcomes."
            ]
            self.messages.append(random.choice(search_failures))
            
        return None
            
    def _remove_employee_blobs(self, count):
        """Remove employee blobs when staff leave"""
        for _ in range(min(count, len(self.employee_blobs))):
            if self.employee_blobs:
                self.employee_blobs.pop()
                
    def _update_employee_productivity(self):
        """Update employee productivity based on compute availability, management, and productive actions each week"""
        productive_employees = 0
        research_gained = 0
        
        # Reset all employees' compute status
        for blob in self.employee_blobs:
            blob['has_compute'] = False
            blob['productivity'] = 0.0
            blob['productive_action_active'] = False
            blob['productive_action_bonus'] = 1.0
            
        # Apply management assignments and check for unmanaged penalties
        self._reassign_employee_management()
        
        # Count employees (excluding managers)
        employees = [blob for blob in self.employee_blobs if blob['type'] == 'employee']
        managers = [blob for blob in self.employee_blobs if blob['type'] == 'manager']
        
        # Apply management static effects (productivity penalties for unmanaged employees beyond 9)
        unmanaged_penalty_count = 0
        if len(employees) > 9 and self.manager_milestone_triggered:
            for employee in employees:
                if employee['unproductive_reason'] == 'no_manager':
                    unmanaged_penalty_count += 1
                    # Unmanaged employees beyond 9 become unproductive
                    employee['productivity'] = 0.0
                    
        # Calculate available compute per employee
        total_employees = len(employees) + len(managers)
        compute_per_employee = self.compute / max(total_employees, 1) if total_employees > 0 else 0
        
        # Assign compute to productive employees and apply productive actions
        compute_assigned = 0
        productive_action_messages = []
        
        for blob in self.employee_blobs:
            if blob['type'] == 'manager':
                # Managers always have compute and are productive
                blob['has_compute'] = True
                blob['productivity'] = 1.0
                
                # Apply manager productive actions
                category = get_employee_category(blob['subtype'])
                if category:
                    actions = get_available_actions(category)
                    if actions and blob['productive_action_index'] < len(actions):
                        action = actions[blob['productive_action_index']]
                        requirements_met, failure_reason = check_action_requirements(action, self, compute_per_employee)
                        
                        if requirements_met:
                            blob['productive_action_active'] = True
                            blob['productive_action_bonus'] = action['effectiveness_bonus']
                            productive_action_messages.append(
                                f"Manager performing {action['name']} (+{int((action['effectiveness_bonus'] - 1) * 100)}% effectiveness)"
                            )
                        else:
                            blob['productive_action_active'] = False
                            blob['productive_action_bonus'] = 0.9  # 10% penalty for unmet requirements
                            productive_action_messages.append(
                                f"Manager unable to perform {action['name']}: {failure_reason} (-10% effectiveness)"
                            )
                
                productive_employees += 1
                
            elif blob['type'] == 'employee':
                # For employees, check if they should be productive
                should_be_productive = True
                
                # If we have managers and more than 9 employees, check management status
                if len(employees) > 9 and self.manager_milestone_triggered:
                    if blob['unproductive_reason'] == 'no_manager':
                        should_be_productive = False
                
                # Assign compute if employee should be productive and compute is available
                if should_be_productive and compute_assigned < self.compute:
                    blob['has_compute'] = True
                    blob['productivity'] = 1.0
                    compute_assigned += 1
                    
                    # Apply employee productive actions
                    category = get_employee_category(blob['subtype'])
                    if category:
                        actions = get_available_actions(category)
                        if actions and blob['productive_action_index'] < len(actions):
                            action = actions[blob['productive_action_index']]
                            requirements_met, failure_reason = check_action_requirements(action, self, compute_per_employee)
                            
                            if requirements_met:
                                blob['productive_action_active'] = True
                                blob['productive_action_bonus'] = action['effectiveness_bonus']
                                productive_action_messages.append(
                                    f"{blob['subtype'].title()} performing {action['name']} (+{int((action['effectiveness_bonus'] - 1) * 100)}% effectiveness)"
                                )
                            else:
                                blob['productive_action_active'] = False
                                blob['productive_action_bonus'] = 0.9  # 10% penalty for unmet requirements
                                productive_action_messages.append(
                                    f"{blob['subtype'].title()} unable to perform {action['name']}: {failure_reason} (-10% effectiveness)"
                                )
                    
                    productive_employees += 1
                    
        # Generate research from productive employees with productive action bonuses
        total_research_bonus = 1.0
        active_bonuses = 0
        for blob in self.employee_blobs:
            if blob['productivity'] > 0:
                # Each productive employee has a chance to contribute to research
                if random.random() < 0.3:  # 30% chance per productive employee
                    base_research = random.randint(1, 3)
                    # Apply productive action bonus
                    bonus_research = int(base_research * blob['productive_action_bonus'])
                    research_gained += bonus_research
                
                # Track active bonuses for messaging
                if blob['productive_action_active']:
                    total_research_bonus *= blob['productive_action_bonus']
                    active_bonuses += 1
                    
        # Apply penalties for unproductive employees
        unproductive_count = len(self.employee_blobs) - productive_employees
        if unproductive_count > 0:
            # Small doom increase for unproductive employees
            doom_penalty = unproductive_count * 0.5
            self._add('doom', int(doom_penalty))
            
            # Different messages based on reason for unproductivity
            if unmanaged_penalty_count > 0:
                self.messages.append(f"{unmanaged_penalty_count} employees unproductive due to lack of management (doom +{int(doom_penalty)})")
            else:
                self.messages.append(f"{unproductive_count} employees lacked compute resources (doom +{int(doom_penalty)})")
            
        # Update research progress
        if research_gained > 0:
            self._add('research_progress', research_gained)
            research_message = f"Research progress: +{research_gained} (total: {self.research_progress})"
            if active_bonuses > 0:
                research_message += f" [+{int((total_research_bonus - 1) * 100)}% from {active_bonuses} productive actions]"
            self.messages.append(research_message)
            
        # Display productive action status messages (limited to avoid spam)
        if productive_action_messages:
            # Group similar messages and show summary
            action_summary = {}
            for msg in productive_action_messages:
                # Extract action type for grouping
                if "performing" in msg:
                    action_type = "active"
                else:
                    action_type = "failed"
                action_summary[action_type] = action_summary.get(action_type, 0) + 1
            
            if action_summary.get("active", 0) > 0:
                self.messages.append(f"Productive Actions: {action_summary['active']} employees performing specialized tasks")
            if action_summary.get("failed", 0) > 0:
                self.messages.append(f"Productivity Issues: {action_summary['failed']} employees unable to perform specialized tasks")
            
        # Check if research threshold reached for paper publication
        if self.research_progress >= 100:
            papers_to_publish = self.research_progress // 100
            self.papers_published += papers_to_publish
            self.research_progress = self.research_progress % 100
            self._add('reputation', papers_to_publish * 5)  # Papers boost reputation
            self.messages.append(f"Research paper{'s' if papers_to_publish > 1 else ''} published! (+{papers_to_publish}, total: {self.papers_published})")
            # Play Zabinga sound for paper completion
            self.sound_manager.play_zabinga_sound()
            
        # Update compute consumption
        self.compute = max(0, self.compute - compute_assigned)
        if compute_assigned > 0:
            self.messages.append(f"Compute consumed: {compute_assigned} (remaining: {self.compute})")
            
        return productive_employees



    def _scout_opponent(self):
        """Scout a specific opponent - unlocked after turn 5"""
        discovered_opponents = [opp for opp in self.opponents if opp.discovered]
        
        if not discovered_opponents:
            # Try to discover a new opponent
            undiscovered = [opp for opp in self.opponents if not opp.discovered]
            if undiscovered:
                target = random.choice(undiscovered)
                target.discover()
                self.messages.append(f"Scouting: Discovered new competitor '{target.name}'!")
                self.messages.append(f"'{target.description}'")
            else:
                self.messages.append("Scouting: All competitors already discovered.")
            return None
            
        # Choose a discovered opponent to scout
        target = random.choice(discovered_opponents)
        
        # Choose what to scout based on what's still unknown
        unknown_stats = [stat for stat, discovered in target.discovered_stats.items() if not discovered]
        
        if unknown_stats:
            stat_to_scout = random.choice(unknown_stats)
        else:
            # All stats known, scout progress for an update
            stat_to_scout = 'progress'
            
        success, value, message = target.scout_stat(stat_to_scout)
        self.messages.append(f"Scouting: {message}")
        
        # Update legacy known_opp_progress for UI compatibility if scouting progress
        if stat_to_scout == 'progress' and success:
            self.known_opp_progress = value
            
    def _spy(self):
        """Legacy espionage method - now scouts random opponents"""
        discovered_opponents = [opp for opp in self.opponents if opp.discovered]
        
        if not discovered_opponents:
            # Try to discover a new opponent
            undiscovered = [opp for opp in self.opponents if not opp.discovered]
            if undiscovered:
                target = random.choice(undiscovered)
                target.discover()
                self.messages.append(f"Espionage: Discovered new competitor '{target.name}'!")
            else:
                self.messages.append("Espionage: No new competitors to discover.")
            return None
            
        # Scout a random stat from a discovered opponent
        target = random.choice(discovered_opponents)
        stats = ['progress', 'budget', 'capabilities_researchers', 'lobbyists', 'compute']
        stat_to_scout = random.choice(stats)
        
        success, value, message = target.scout_stat(stat_to_scout)
        self.messages.append(f"Espionage: {message}")
        
        # Update legacy known_opp_progress for UI compatibility
        if stat_to_scout == 'progress' and success:
            self.known_opp_progress = value
            
        return None
            
        return None

    def _espionage_risk(self):
        if random.random() < 0.25:
            self._add('reputation', -2)
            self.messages.append("Espionage scandal! Reputation dropped.")
        elif random.random() < 0.15:
            self._add('doom', 5)
            self.messages.append("Espionage backfired! Doom increased.")
        return None
        
    def _hire_manager(self):
        """Hire a new manager to oversee employees"""
        # Add manager blob to the system
        self._add_manager_blob()
        
        # Increment staff count for the manager
        self.staff += 1
        
        # Add success message
        self.messages.append(f"Manager hired! Now managing {len(self.managers)} team cluster(s).")
        
        # Check if this is the first manager hire (milestone)
        if len(self.managers) == 1 and not self.manager_milestone_triggered:
            self.manager_milestone_triggered = True
            self.messages.append("MILESTONE: First manager hired! Teams beyond 9 employees now need management to stay productive.")
            
            # Show tutorial for manager system
            self.show_tutorial_message(
                "manager_system",
                "Manager System Unlocked!",
                "You've hired your first manager! This unlocks the management system:\n\n"
                "• Each manager can oversee up to 9 employees\n"
                "• Unmanaged employees beyond 9 become unproductive (shown with red slash)\n"
                "• Managers appear as green blobs vs blue employee blobs\n"
                "• Manager hiring costs 1.5x normal employee cost\n\n"
                "Plan your team structure carefully as you scale!"
            )
        
        return None

    def _breakthrough_event(self):
        if "secure_cloud" in self.upgrade_effects:
            spike = random.randint(2, 5)
            self.messages.append("Lab breakthrough! Secure cloud softened doom spike.")
        else:
            spike = random.randint(6, 13)
            self.messages.append("Lab breakthrough! Doom spikes!")
        self._add('doom', spike)

    def handle_click(self, mouse_pos, w, h):
        # Check End Turn button FIRST for reliability (Issue #3 requirement)
        btn_rect = self._get_endturn_rect(w, h)
        if self._in_rect(mouse_pos, btn_rect) and not self.game_over:
            # Try to end turn, sound feedback handled in end_turn method
            self.end_turn()
            return None
        
        # Activity log drag functionality - Handle after end turn check
        activity_log_rect = self._get_activity_log_rect(w, h)
        if self._in_rect(mouse_pos, activity_log_rect):
            # Don't start drag if clicking on minimize/expand buttons
            if "compact_activity_display" in self.upgrade_effects:
                if hasattr(self, 'activity_log_minimized') and self.activity_log_minimized:
                    expand_rect = self._get_activity_log_expand_button_rect(w, h)
                    if self._in_rect(mouse_pos, expand_rect):
                        self.activity_log_minimized = False
                        self.messages.append("Activity log expanded.")
                        return None  # Button click handled
                elif self.scrollable_event_log_enabled:
                    minimize_rect = self._get_activity_log_minimize_button_rect(w, h)
                    if self._in_rect(mouse_pos, minimize_rect):
                        self.activity_log_minimized = True
                        self.messages.append("Activity log minimized.")
                        return None  # Button click handled
            
            # Start dragging the activity log
            log_x, log_y = self._get_activity_log_base_position(w, h)
            self.activity_log_being_dragged = True
            self.activity_log_drag_offset = (mouse_pos[0] - (log_x + self.activity_log_position[0]), 
                                           mouse_pos[1] - (log_y + self.activity_log_position[1]))
            return None

        # Actions (left)
        a_rects = self._get_action_rects(w, h)
        for idx, rect in enumerate(a_rects):
            if self._in_rect(mouse_pos, rect):
                if not self.game_over:
                    # Check for undo (if action is already selected, try to undo it)
                    is_undo = idx in self.selected_actions
                    
                    result = self.attempt_action_selection(idx, is_undo)
                    
                    # Return play_sound flag for main.py to handle sound
                    return 'play_sound' if result['play_sound'] else None
                return None

        # Upgrades (right, as icons or buttons)
        u_rects = self._get_upgrade_rects(w, h)
        for idx, rect in enumerate(u_rects):
            if self._in_rect(mouse_pos, rect):
                upg = self.upgrades[idx]
                if not upg.get("purchased", False):
                    if self.money >= upg["cost"]:
                        self._add('money', -upg["cost"])  # Use _add to track spending
                        upg["purchased"] = True
                        self.upgrade_effects.add(upg["effect_key"])
                        
                        # Trigger first-time help for upgrade purchase
                        if onboarding.should_show_mechanic_help('first_upgrade_purchase'):
                            onboarding.mark_mechanic_seen('first_upgrade_purchase')
                        
                        # Special handling for custom effects
                        if upg.get("custom_effect") == "buy_accounting_software":
                            self.accounting_software_bought = True
                            self.messages.append(f"Upgrade purchased: {upg['name']} - Cash flow tracking enabled, board oversight blocked!")
                        elif upg.get("custom_effect") == "buy_compact_activity_display":
                            # Allow toggle functionality for the activity log
                            self.messages.append(f"Upgrade purchased: {upg['name']} - Activity log can now be minimized! Click the minimize button.")
                        elif upg.get("effect_key") == "hpc_cluster":
                            self._add('compute', 20)
                            self.messages.append(f"Upgrade purchased: {upg['name']} - Massive compute boost! Research effectiveness increased.")
                        elif upg.get("effect_key") == "research_automation":
                            self.messages.append(f"Upgrade purchased: {upg['name']} - Research actions now benefit from available compute resources.")
                        else:
                            self.messages.append(f"Upgrade purchased: {upg['name']}")
                        
                        # Log upgrade purchase
                        self.logger.log_upgrade(upg["name"], upg["cost"], self.turn)
                        
                        # Create smooth transition animation from button to icon
                        icon_rect = self._get_upgrade_icon_rect(idx, w, h)
                        self._create_upgrade_transition(idx, rect, icon_rect)
                    else:
                        error_msg = f"Not enough money for {upg['name']} (need ${upg['cost']}, have ${self.money})."
                        self.messages.append(error_msg)
                        
                        # Track error for easter egg detection
                        self.track_error(f"Insufficient money: {upg['name']}")
                else:
                    self.messages.append(f"{upg['name']} already purchased.")
                    
                    # Track error for easter egg detection
                    self.track_error(f"Already purchased: {upg['name']}")
                return None

        # Mute button (bottom right)
        mute_rect = self._get_mute_button_rect(w, h)
        if self._in_rect(mouse_pos, mute_rect):
            new_state = self.sound_manager.toggle()
            status = "enabled" if new_state else "disabled"
            self.messages.append(f"Sound {status}")
            return None

        return None

    def handle_mouse_motion(self, mouse_pos, w, h):
        """Handle mouse motion events for dragging functionality"""
        if self.activity_log_being_dragged:
            # Update activity log position based on mouse movement
            new_x = mouse_pos[0] - self.activity_log_drag_offset[0]
            new_y = mouse_pos[1] - self.activity_log_drag_offset[1]
            
            # Get base position to calculate offset
            base_x, base_y = self._get_activity_log_base_position(w, h)
            
            # Constrain position to stay within screen bounds
            log_width = int(w * 0.44)
            log_height = int(h * 0.22)
            
            # Calculate new position with constraints
            new_offset_x = max(-base_x, min(w - log_width - base_x, new_x - base_x))
            new_offset_y = max(-base_y, min(h - log_height - base_y, new_y - base_y))
            
            self.activity_log_position = (new_offset_x, new_offset_y)

    def handle_mouse_release(self, mouse_pos, w, h):
        """Handle mouse release events to stop dragging"""
        if self.activity_log_being_dragged:
            self.activity_log_being_dragged = False
            self.activity_log_drag_offset = (0, 0)
            return True  # Indicate that a drag operation was completed
        return False

    def check_hover(self, mouse_pos, w, h):
        # Reset all hover states
        self.hovered_upgrade_idx = None
        self.hovered_action_idx = None
        self.endturn_hovered = False
        
        # Check activity log area for hover FIRST (highest priority for specific interactions)
        activity_log_rect = self._get_activity_log_rect(w, h)
        if self._in_rect(mouse_pos, activity_log_rect):
            # Show tooltip about minimization upgrade if not purchased
            if "compact_activity_display" not in self.upgrade_effects:
                return "You may purchase the ability to minimise this for $150!"
            elif hasattr(self, 'activity_log_minimized') and self.activity_log_minimized:
                return "Activity Log (minimized) - Click expand button to show full log"
            else:
                return "Activity Log - Click minimize button to reduce screen space"
        
        # Check action buttons for hover
        action_rects = self._get_action_rects(w, h)
        for idx, rect in enumerate(action_rects):
            if self._in_rect(mouse_pos, rect):
                self.hovered_action_idx = idx
                action = self.actions[idx]
                # Show enhanced tooltip with cost and requirements
                ap_cost = action.get("ap_cost", 1)
                cost_str = f"${action['cost']}" if action['cost'] > 0 else "Free"
                ap_str = f"{ap_cost} AP" if ap_cost > 1 else "1 AP"
                
                # Check if action is affordable
                affordable = action['cost'] <= self.money and ap_cost <= self.action_points
                status = "✓ Available" if affordable else "✗ Cannot afford"
                
                return f"{action['name']}: {action['desc']} (Cost: {cost_str}, {ap_str}) - {status}"
        
        # Check upgrade buttons for hover
        u_rects = self._get_upgrade_rects(w, h)
        for idx, rect in enumerate(u_rects):
            if self._in_rect(mouse_pos, rect):
                self.hovered_upgrade_idx = idx
                upgrade = self.upgrades[idx]
                if not upgrade.get("purchased", False):
                    # Enhanced tooltip for unpurchased upgrades
                    affordable = upgrade['cost'] <= self.money
                    status = "✓ Available" if affordable else "✗ Cannot afford"
                    return f"{upgrade['name']}: {upgrade['desc']} (Cost: ${upgrade['cost']}) - {status}"
                else:
                    return f"{upgrade['name']}: {upgrade['desc']} (Purchased)"
        
        # Check end turn button for hover
        endturn_rect = self._get_endturn_rect(w, h)
        if self._in_rect(mouse_pos, endturn_rect):
            self.endturn_hovered = True
            ap_remaining = self.action_points
            if ap_remaining > 0:
                return f"End Turn ({ap_remaining} AP remaining - these will be wasted!)"
            else:
                return "End Turn (All AP spent efficiently)"
        
        return None

    def _get_action_rects(self, w, h):
        # Place actions as tall buttons on left (moved down to accommodate opponents panel)
        count = len(self.actions)
        base_x = int(w * 0.04)
        base_y = int(h * 0.28)  # Moved down from 0.16 to 0.28
        width = int(w * 0.32)
        height = int(h * 0.065)  # Made slightly smaller to fit more actions
        gap = int(h * 0.02)  # Reduced gap slightly
        return [
            (base_x, base_y + i * (height + gap), width, height)
            for i in range(count)
        ]

    def _get_upgrade_rects(self, w, h):
        # Display upgrades as icons/buttons on right
        n = len(self.upgrades)
        # Purchased upgrades shrink to small icon row at top right
        purchased = [i for i, u in enumerate(self.upgrades) if u.get("purchased", False)]
        not_purchased = [i for i, u in enumerate(self.upgrades) if not u.get("purchased", False)]

        icon_w, icon_h = int(w*0.045), int(w*0.045)
        # Purchased: row at top right, but respect UI boundaries
        # Info panel extends to about w*0.84, so ensure icons don't overlap
        max_icons_per_row = max(1, int((w - w*0.84) / icon_w))  # Available space for icons
        
        purchased_rects = []
        for j, i in enumerate(purchased):
            row = j // max_icons_per_row
            col = j % max_icons_per_row
            x = w - icon_w*(col+1)
            y = int(h*0.08) + row * (icon_h + 5)  # Stack vertically if needed
            purchased_rects.append((x, y, icon_w, icon_h))
        # Not purchased: buttons down right (moved down to accommodate opponents panel)
        base_x = int(w*0.63)
        base_y = int(h*0.28)  # Moved down from 0.18 to 0.28
        btn_w, btn_h = int(w*0.29), int(h*0.08)
        gap = int(h*0.022)
        not_purchased_rects = [
            (base_x, base_y + k*(btn_h+gap), btn_w, btn_h)
            for k in range(len(not_purchased))
        ]
        # Merge and return in upgrade order
        out = [None]*n
        for j, i in enumerate(purchased): out[i] = purchased_rects[j]
        for k, i in enumerate(not_purchased): out[i] = not_purchased_rects[k]
        return out
    
    def _get_upgrade_icon_rect(self, upgrade_idx, w, h):
        """Get the icon rectangle for a purchased upgrade."""
        # Calculate where this upgrade will appear as an icon
        purchased = [i for i, u in enumerate(self.upgrades) if u.get("purchased", False)]
        
        # Find position of this upgrade in the purchased list
        if upgrade_idx in purchased:
            j = purchased.index(upgrade_idx)
        else:
            # Estimate position if it was purchased (for animation target)
            purchased_count = len(purchased) + 1  # +1 for the upgrade being purchased
            j = purchased_count - 1
        
        icon_w, icon_h = int(w*0.045), int(w*0.045)
        x = w - icon_w*(j+1) - 10  # Small margin from right edge
        y = int(h*0.08)
        
        return (x, y, icon_w, icon_h)

    def _get_endturn_rect(self, w, h):
        return (int(w*0.39), int(h*0.88), int(w*0.22), int(h*0.07))

    def _get_mute_button_rect(self, w, h):
        button_size = int(min(w, h) * 0.04)
        button_x = w - button_size - 20
        button_y = h - button_size - 20
        return (button_x, button_y, button_size, button_size)

    def _get_activity_log_minimize_button_rect(self, w, h):
        """Get rectangle for the activity log minimize button (only when scrollable log is enabled)"""
        log_x, log_y = self._get_activity_log_current_position(w, h)
        log_width = int(w * 0.44)
        button_size = int(h * 0.025)
        button_x = log_x + log_width - 30
        button_y = log_y
        return (button_x, button_y, button_size, button_size)

    def _get_activity_log_expand_button_rect(self, w, h):
        """Get rectangle for the activity log expand button (only when log is minimized)"""
        log_x, log_y = self._get_activity_log_current_position(w, h)
        
        # Estimate title width based on character count (avoiding pygame dependency in tests)
        title_width = len("Activity Log") * int(h*0.015)  # Rough character width estimate
        
        button_size = int(h * 0.025)
        button_x = log_x + title_width + 10
        button_y = log_y
        return (button_x, button_y, button_size, button_size)

    def _get_activity_log_rect(self, w, h):
        """Get rectangle for the entire activity log area for hover detection"""
        log_x, log_y = self._get_activity_log_current_position(w, h)
        
        if (hasattr(self, 'activity_log_minimized') and 
            self.activity_log_minimized and 
            "compact_activity_display" in self.upgrade_effects):
            # Minimized log - small title bar area
            title_width = len("Activity Log") * int(h*0.015)
            bar_height = int(h * 0.04)
            return (log_x - 5, log_y - 5, title_width + 50, bar_height)
        else:
            # Full log area
            log_width = int(w * 0.44)
            log_height = int(h * 0.22)
            return (log_x - 5, log_y - 5, log_width + 10, log_height + 10)

    def _get_activity_log_base_position(self, w, h):
        """Get the base position of activity log (before any drag offset)"""
        return (int(w*0.04), int(h*0.74))

    def _get_activity_log_current_position(self, w, h):
        """Get the current position of activity log (including drag offset)"""
        base_x, base_y = self._get_activity_log_base_position(w, h)
        return (base_x + self.activity_log_position[0], base_y + self.activity_log_position[1])

    def _in_rect(self, pt, rect):
        x, y = pt
        rx, ry, rw, rh = rect
        return rx <= x <= rx+rw and ry <= y <= ry+rh

    def end_turn(self):
        # Prevent multiple end turn calls during processing
        if self.turn_processing:
            # Play error sound for rejected input
            if hasattr(self, 'sound_manager'):
                self.sound_manager.play_sound('error_beep')
            return False
            
        # Start turn processing
        self.turn_processing = True
        self.turn_processing_timer = self.turn_processing_duration
        
        # Play accepted sound
        if hasattr(self, 'sound_manager'):
            self.sound_manager.play_sound('popup_accept')  # Reuse accept sound for turn confirmation
        # Clear event log at start of turn to show only current-turn events
        # But first store previous messages if scrollable log was already enabled
        if self.scrollable_event_log_enabled and self.messages:
            # Add turn delimiter and store messages from previous turn
            turn_header = f"=== Turn {self.turn + 1} ==="
            self.event_log_history.append(turn_header)
            self.event_log_history.extend(self.messages)
            
        self.messages = []
        
        # Perform all selected actions
        for idx in self.selected_actions:
            action = self.actions[idx]
            
            # Get delegation info if available
            delegation_info = getattr(self, '_action_delegations', {}).get(idx, {
                'delegated': False,
                'effectiveness': 1.0,
                'ap_cost': action.get("ap_cost", 1)
            })
            
            ap_cost = delegation_info['ap_cost']
            effectiveness = delegation_info['effectiveness']
            
            # Deduct Action Points
            self.action_points -= ap_cost
            self.ap_spent_this_turn = True  # Track for UI glow effects
            self.ap_glow_timer = 30  # 30 frames of glow effect
            
            # Deduct money cost using _add to track spending
            self._add('money', -action["cost"])
            
            # Log the action
            action_name = action["name"]
            if delegation_info['delegated']:
                action_name += " (delegated)"
            self.logger.log_action(action_name, action["cost"], self.turn)
            
            # Execute action effects with effectiveness modifier
            if action.get("upside"):
                if effectiveness < 1.0:
                    # For delegated actions, we need to modify the effectiveness
                    # This is a simplified approach - in practice, you might need
                    # more sophisticated effectiveness handling per action type
                    self._execute_action_with_effectiveness(action, "upside", effectiveness)
                else:
                    action["upside"](self)
                    
            if action.get("downside"): 
                action["downside"](self)
            if action.get("rules"): 
                action["rules"](self)
        
        # Clear delegation info for next turn
        if hasattr(self, '_action_delegations'):
            self._action_delegations = {}
        self.selected_actions = []
        self.selected_action_instances = []  # Clear action instances for next turn
        self.action_clicks_this_turn = {}  # Reset click tracking for new turn

        # Staff maintenance - scale up costs and add overheads after first employee
        if self.staff == 0:
            maintenance_cost = 0
        elif self.staff == 1:
            # First employee, just base cost (scaled up from 15 to 25)
            maintenance_cost = 25
        else:
            # Multiple employees - base cost plus overhead per additional employee
            base_cost = 25  # Scaled up from 15
            overhead_per_additional = 10  # Overhead cost for each employee after the first
            maintenance_cost = base_cost + (self.staff - 1) * (base_cost + overhead_per_additional)
        money_before_maintenance = self.money
        self._add('money', -maintenance_cost)  # Use _add to track spending
        
        # Check if we couldn't afford maintenance (money went negative before clamping)
        if money_before_maintenance < maintenance_cost:
            if "comfy_chairs" in self.upgrade_effects and random.random() < 0.75:
                self.messages.append("Comfy chairs helped staff endure unpaid turn.")
            else:
                lost = random.randint(1, max(1, self.staff // 2))
                self.staff = max(0, self.staff - lost)
                self.messages.append(f"Could not pay staff! {lost} staff left.")

        # Update employee productivity and compute consumption (weekly cycle)
        self._update_employee_productivity()

        # Doom rises over time, faster with more staff
        doom_rise = 2 + self.staff // 5 + (1 if self.doom > 60 else 0)
        
        # Opponents take their turns and contribute to doom
        opponent_doom = 0
        for opponent in self.opponents:
            messages = opponent.take_turn()
            self.messages.extend(messages)
            opponent_doom += opponent.get_impact_on_doom()
            
        # Add opponent doom contribution
        doom_rise += opponent_doom
        self.doom = min(self.max_doom, self.doom + doom_rise)

        self.trigger_events()
        
        # Check for board member milestone trigger (>$10K spend without accounting software)
        self._check_board_member_milestone()
        
        # Handle deferred events (tick expiration and auto-execute expired ones)
        if hasattr(self, 'deferred_events'):
            expired_events = self.deferred_events.tick_all_events(self)
        
        self.turn += 1
        
        # Reset Action Points for new turn (Phase 2: Staff-Based AP Scaling)
        self.max_action_points = self.calculate_max_ap()
        self.action_points = self.max_action_points
        self.ap_spent_this_turn = False  # Reset glow flag for new turn
        
        # Reset spend tracking for new turn
        self.spend_this_turn = 0
        
        # Decrease glow timer
        if self.ap_glow_timer > 0:
            self.ap_glow_timer -= 1
        
        # Store current turn messages if scrollable event log is now enabled
        # (This handles the case where the feature was enabled during this turn)
        if self.scrollable_event_log_enabled and self.messages:
            # Check if we already added a header for the current turn (before increment)
            current_turn_header = f"=== Turn {self.turn} ==="
            if not (self.event_log_history and current_turn_header in self.event_log_history[-5:]):
                self.event_log_history.append(current_turn_header)
            self.event_log_history.extend(self.messages)

        # Log turn summary before checking game over conditions
        self.logger.log_turn_summary(self.turn, self.money, self.staff, self.reputation, self.doom)

        # Win/lose conditions
        game_end_reason = None
        if self.doom >= self.max_doom:
            self.game_over = True
            game_end_reason = "p(Doom) reached maximum"
            self.messages.append("p(Doom) has reached maximum! The world is lost.")
        else:
            # Check if any opponent has reached 100% progress
            for opponent in self.opponents:
                if opponent.progress >= 100:
                    self.game_over = True
                    game_end_reason = f"{opponent.name} deployed dangerous AGI"
                    self.messages.append(f"{opponent.name} has deployed dangerous AGI. Game over!")
                    break
                    
        if not self.game_over and self.staff == 0:
            self.game_over = True
            game_end_reason = "All staff left"
            self.messages.append("All your staff have left. Game over!")

        self.staff = max(0, self.staff)
        self.reputation = max(0, self.reputation)
        self.money = max(self.money, 0)

        # If game ended, get detailed scenario and log final state
        if self.game_over and game_end_reason:
            # Get detailed end game scenario
            self.end_game_scenario = end_game_scenarios.get_scenario(self)
            
            # Update the message with the scenario title
            if self.end_game_scenario:
                self.messages.append(f"GAME OVER: {self.end_game_scenario.title}")
            
            final_resources = {
                'money': self.money,
                'staff': self.staff,
                'reputation': self.reputation,
                'doom': self.doom
            }
            self.logger.log_game_end(game_end_reason, self.turn, final_resources)
            log_path = self.logger.write_log_file()
            if log_path:
                self.messages.append(f"Game log saved to: {log_path}")

        # Save high score if achieved
        self.save_highscore()
        
        # Process delayed actions
        resolved_actions = self.process_delayed_actions()
        
        # Add daily news feed for turn impact feedback
        daily_news = self.get_daily_news()
        self.messages.append(daily_news)
        
        # Update spend tracking display
        self.update_spend_tracking()
        
        # Reset spend tracking for next turn
        self.spend_this_turn = 0
        
        # Update UI transitions - animations advance each frame/turn
        self._update_ui_transitions()
        
        # Reset turn processing state (processing will be handled by timer in main loop)
        # The timer will count down and reset turn_processing to False
        return True  # Indicate successful turn end
    
    def update_turn_processing(self):
        """Update turn processing timer and handle transition effects."""
        if self.turn_processing:
            self.turn_processing_timer -= 1
            if self.turn_processing_timer <= 0:
                self.turn_processing = False
                self.turn_processing_timer = 0

    def trigger_events(self):
        """Trigger events using both the original and enhanced event systems."""
        # Handle original events (backward compatibility)
        for event_dict in self.events:
            if event_dict["trigger"](self):
                event_dict["effect"](self)
                event_message = f"Event: {event_dict['name']} - {event_dict['desc']}"
                self.messages.append(event_message)
                # Log the event
                self.logger.log_event(event_dict["name"], event_dict["desc"], self.turn)
        
        # Handle enhanced events (if enabled)
        if self.enhanced_events_enabled:
            self._trigger_enhanced_events()
    
    def _trigger_enhanced_events(self):
        """Trigger enhanced events with popup/deferred support."""
        from src.features.event_system import create_enhanced_events
        
        # Get enhanced events (in a real implementation, these would be stored)
        enhanced_events = create_enhanced_events()
        
        for event in enhanced_events:
            if event.trigger(self):
                if event.event_type == EventType.POPUP:
                    # Add to pending popup events for UI handling
                    self.pending_popup_events.append(event)
                else:
                    # Handle normal/deferred events immediately
                    self._handle_triggered_event(event)
    
    def _handle_triggered_event(self, event):
        """Handle a triggered event based on its type."""
        if event.event_type == EventType.NORMAL:
            # Execute immediately like original events
            event.execute_effect(self, EventAction.ACCEPT)
            event_message = f"Event: {event.name} - {event.desc}"
            self.messages.append(event_message)
            self.logger.log_event(event.name, event.desc, self.turn)
        elif event.event_type == EventType.DEFERRED:
            # For now, auto-defer deferred events (UI will handle choice later)
            if event.defer(self.turn):
                self.deferred_events.add_deferred_event(event)
                self.messages.append(f"Deferred: {event.name} - {event.desc}")
                self.logger.log_event(f"Deferred: {event.name}", event.desc, self.turn)
    
    def handle_popup_event_action(self, event, action: EventAction):
        """Handle player action on a popup event."""
        if action == EventAction.DEFER and event.can_be_deferred():
            if event.defer(self.turn):
                self.deferred_events.add_deferred_event(event)
                self.messages.append(f"Deferred: {event.name}")
        else:
            event.execute_effect(self, action)
        
        # Remove from pending popup events
        if event in self.pending_popup_events:
            self.pending_popup_events.remove(event)
        
        # Log the action
        self.logger.log_event(f"Player {action.value}: {event.name}", event.desc, self.turn)
    
    def handle_deferred_event_action(self, event, action: EventAction):
        """Handle player action on a deferred event."""
        event.execute_effect(self, action)
        self.deferred_events.remove_event(event)
        self.logger.log_event(f"Resolved deferred: {event.name}", f"Action: {action.value}", self.turn)

    # --- High score --- #
    def load_highscore(self):
        try:
            with open(SCORE_FILE, "r") as f:
                data = json.load(f)
            if self.seed in data:
                return data[self.seed]
            return max(data.values(), default=0)
        except Exception:
            return 0

    def save_highscore(self):
        try:
            if not self.game_over:
                return
            score = self.turn
            if os.path.exists(SCORE_FILE):
                with open(SCORE_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            prev = data.get(self.seed, 0)
            if score > prev:
                data[self.seed] = score
                with open(SCORE_FILE, "w") as f:
                    json.dump(data, f)
                self.highscore = score
        except Exception:
            pass

    # --- Tutorial settings --- #
    TUTORIAL_SETTINGS_FILE = "tutorial_settings.json"
    
    def load_tutorial_settings(self):
        """Load tutorial settings from file."""
        try:
            with open(self.TUTORIAL_SETTINGS_FILE, "r") as f:
                data = json.load(f)
            self.tutorial_enabled = data.get("tutorial_enabled", True)
            self.tutorial_shown_milestones = set(data.get("tutorial_shown_milestones", []))
            self.first_game_launch = data.get("first_game_launch", True)
        except Exception:
            # Use defaults for first-time players
            self.tutorial_enabled = True
            self.tutorial_shown_milestones = set()
            self.first_game_launch = True
    
    def save_tutorial_settings(self):
        """Save tutorial settings to file."""
        try:
            data = {
                "tutorial_enabled": self.tutorial_enabled,
                "tutorial_shown_milestones": list(self.tutorial_shown_milestones),
                "first_game_launch": False  # No longer first launch after this save
            }
            with open(self.TUTORIAL_SETTINGS_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass
    
    def show_tutorial_message(self, milestone_id, title, content):
        """Queue a tutorial message to be shown."""
        if self.tutorial_enabled and milestone_id not in self.tutorial_shown_milestones:
            self.pending_tutorial_message = {
                "milestone_id": milestone_id,
                "title": title,
                "content": content
            }
    
    def get_employee_productive_actions(self, employee_id):
        """
        Get available productive actions for a specific employee.
        
        Args:
            employee_id (int): The ID of the employee blob
            
        Returns:
            dict: Information about the employee's productive actions, or None if not found
        """
        # Find the employee blob
        employee_blob = None
        for blob in self.employee_blobs:
            if blob['id'] == employee_id:
                employee_blob = blob
                break
        
        if not employee_blob:
            return None
        
        category = get_employee_category(employee_blob['subtype'])
        if not category:
            return None
        
        actions = get_available_actions(category)
        if not actions:
            return None
        
        # Check requirements for each action
        total_employees = len([b for b in self.employee_blobs if b['type'] in ['employee', 'manager']])
        compute_per_employee = self.compute / max(total_employees, 1) if total_employees > 0 else 0
        
        action_info = []
        for i, action in enumerate(actions):
            requirements_met, failure_reason = check_action_requirements(action, self, compute_per_employee)
            action_info.append({
                'index': i,
                'name': action['name'],
                'description': action['description'],
                'effectiveness_bonus': action['effectiveness_bonus'],
                'requirements_met': requirements_met,
                'failure_reason': failure_reason,
                'is_selected': i == employee_blob['productive_action_index']
            })
        
        return {
            'employee_id': employee_id,
            'employee_subtype': employee_blob['subtype'],
            'category': category,
            'current_action_index': employee_blob['productive_action_index'],
            'current_action_active': employee_blob.get('productive_action_active', False),
            'current_action_bonus': employee_blob.get('productive_action_bonus', 1.0),
            'available_actions': action_info
        }
    
    def set_employee_productive_action(self, employee_id, action_index):
        """
        Set the productive action for a specific employee.
        
        Args:
            employee_id (int): The ID of the employee blob
            action_index (int): The index of the action to set
            
        Returns:
            tuple: (success (bool), message (str))
        """
        # Find the employee blob
        employee_blob = None
        for blob in self.employee_blobs:
            if blob['id'] == employee_id:
                employee_blob = blob
                break
        
        if not employee_blob:
            return False, f"Employee {employee_id} not found"
        
        category = get_employee_category(employee_blob['subtype'])
        if not category:
            return False, f"No productive actions available for {employee_blob['subtype']}"
        
        actions = get_available_actions(category)
        if not actions or action_index < 0 or action_index >= len(actions):
            return False, f"Invalid action index {action_index}"
        
        # Set the new action
        employee_blob['productive_action_index'] = action_index
        action_name = actions[action_index]['name']
        
        self.messages.append(f"{employee_blob['subtype'].title()} (ID:{employee_id}) assigned to: {action_name}")
        
        return True, f"Action set to {action_name}"
    
    def get_all_employee_productive_actions_summary(self):
        """
        Get a summary of all employees' productive actions for debugging/logging.
        
        Returns:
            list: List of employee productive action summaries
        """
        summary = []
        
        for blob in self.employee_blobs:
            if blob['type'] in ['employee', 'manager']:
                category = get_employee_category(blob['subtype'])
                if category:
                    actions = get_available_actions(category)
                    if actions and blob['productive_action_index'] < len(actions):
                        current_action = actions[blob['productive_action_index']]
                        summary.append({
                            'id': blob['id'],
                            'type': blob['type'],
                            'subtype': blob['subtype'],
                            'category': category,
                            'current_action': current_action['name'],
                            'action_index': blob['productive_action_index'],
                            'is_active': blob.get('productive_action_active', False),
                            'bonus': blob.get('productive_action_bonus', 1.0),
                            'productivity': blob.get('productivity', 0.0)
                        })
        
        return summary

    def dismiss_tutorial_message(self):
        """Dismiss the current tutorial message and mark milestone as shown."""
        if self.pending_tutorial_message:
            milestone_id = self.pending_tutorial_message["milestone_id"]
            self.tutorial_shown_milestones.add(milestone_id)
            self.pending_tutorial_message = None
            self.save_tutorial_settings()
    
    def _hire_employee_subtype(self, subtype_id):
        """Hire an employee of a specific subtype using the employee subtypes system."""
        from src.core.employee_subtypes import EMPLOYEE_SUBTYPES, apply_subtype_effects
        
        if subtype_id not in EMPLOYEE_SUBTYPES:
            self.messages.append(f"Unknown employee subtype: {subtype_id}")
            return
        
        subtype = EMPLOYEE_SUBTYPES[subtype_id]
        
        # Check unlock condition if it exists
        if subtype.get("unlock_condition") and not subtype["unlock_condition"](self):
            self.messages.append(f"{subtype['name']} is not available yet.")
            return
        
        # Apply the subtype effects using the employee subtypes system
        success, message = apply_subtype_effects(self, subtype_id)
        
        if success:
            self.messages.append(message)
        else:
            self.messages.append(f"Failed to hire {subtype['name']}: {message}")
    
    def _scout_opponents(self):
        """Scout competing labs to gather intelligence on their capabilities."""
        messages = []
        discoveries = 0
        
        # First, check if any opponents can be discovered
        undiscovered_opponents = [opp for opp in self.opponents if not opp.discovered]
        
        if undiscovered_opponents and random.random() < 0.6:  # 60% chance to discover a new lab
            # Discover a new opponent
            new_opponent = random.choice(undiscovered_opponents)
            new_opponent.discover()
            discoveries += 1
            messages.append(f"Intelligence breakthrough! Discovered new competing lab: {new_opponent.name}")
            messages.append(f"→ {new_opponent.description}")
        
        # Scout stats from known opponents
        discovered_opponents = [opp for opp in self.opponents if opp.discovered]
        
        if discovered_opponents:
            target_opponent = random.choice(discovered_opponents)
            
            # Try to scout a random stat
            stats_to_scout = ['budget', 'capabilities_researchers', 'lobbyists', 'compute', 'progress']
            stat_to_scout = random.choice(stats_to_scout)
            
            success, value, message = target_opponent.scout_stat(stat_to_scout)
            messages.append(message)
            
            if success:
                discoveries += 1
        
        # Add intelligence gained message
        if discoveries > 0:
            messages.append(f"Intelligence gathering successful! ({discoveries} new insights)")
            # Small reputation gain for successful intelligence work
            self._add('reputation', 1)
        else:
            messages.append("Intelligence gathering yielded limited results this time.")
        
        # Add all messages to game state
        for msg in messages:
            self.messages.append(msg)
    
    def _trigger_competitor_discovery(self):
        """Trigger discovery of a new competitor through intelligence."""
        undiscovered_opponents = [opp for opp in self.opponents if not opp.discovered]
        
        if undiscovered_opponents:
            new_opponent = random.choice(undiscovered_opponents)
            new_opponent.discover()
            self.messages.append(f"INTELLIGENCE ALERT: New competitor detected - {new_opponent.name}")
            self.messages.append(f"→ {new_opponent.description}")
            self.messages.append("Use 'Scout Opponents' action to gather more intelligence on their capabilities.")
        else:
            self.messages.append("Intelligence reports suggest all major competitors are now known.")
    
    def _provide_competitor_update(self):
        """Provide an intelligence update on known competitors."""
        discovered_opponents = [opp for opp in self.opponents if opp.discovered]
        
        if discovered_opponents:
            target = random.choice(discovered_opponents)
            
            # Generate a random intelligence snippet
            snippets = [
                f"{target.name} has been recruiting aggressively this quarter.",
                f"Sources report {target.name} secured additional funding recently.", 
                f"{target.name} was spotted at a major AI conference last week.",
                f"Technical staff departures reported at {target.name}.",
                f"{target.name} has increased their compute infrastructure.",
                f"Regulatory filings suggest {target.name} is preparing for new announcements."
            ]
            
            selected_snippet = random.choice(snippets)
            self.messages.append(f"INTELLIGENCE UPDATE: {selected_snippet}")
            self.messages.append("Consider using 'Scout Opponents' for detailed intelligence gathering.")
    
    def _trigger_expense_request(self):
        """Trigger an employee expense request event that requires player decision."""
        from src.features.event_system import Event, EventType, EventAction
        
        # Define different types of expense requests
        expense_types = [
            {
                "type": "training",
                "employee": "Research Staff",
                "item": "AI Safety Conference Registration", 
                "cost": 75,
                "approve_effect": lambda gs: (gs._add('money', -75), gs._add('reputation', 2), gs._add('research_staff', 1)),
                "deny_effect": lambda gs: (gs.messages.append("Employee morale slightly affected by denied training request."),),
                "description": "Professional development opportunity to enhance research capabilities"
            },
            {
                "type": "equipment",
                "employee": "Operations Specialist",
                "item": "Upgraded Development Workstation",
                "cost": 120,
                "approve_effect": lambda gs: (gs._add('money', -120), gs._add('compute', 5)),
                "deny_effect": lambda gs: (gs.messages.append("Operations efficiency may be impacted by outdated equipment."),),
                "description": "Hardware upgrade to improve operational efficiency and compute resources"
            },
            {
                "type": "research_materials",
                "employee": "Data Scientist", 
                "item": "Research Dataset License",
                "cost": 90,
                "approve_effect": lambda gs: (gs._add('money', -90), gs._add('research_progress', 5)),
                "deny_effect": lambda gs: (gs.messages.append("Research progress may slow without access to key datasets."),),
                "description": "Access to proprietary datasets for advanced research projects"
            },
            {
                "type": "collaboration",
                "employee": "Manager",
                "item": "Industry Networking Event",
                "cost": 60,
                "approve_effect": lambda gs: (gs._add('money', -60), gs._add('reputation', 3)),
                "deny_effect": lambda gs: (gs.messages.append("Missed networking opportunities may limit future collaborations."),),
                "description": "Professional networking to build industry relationships"
            }
        ]
        
        # Select a random expense request
        expense = random.choice(expense_types)
        
        # Create the popup event
        event_name = f"Expense Request: {expense['item']}"
        event_desc = (f"{expense['employee']} requests approval for: {expense['item']} (${expense['cost']})\n\n"
                     f"Purpose: {expense['description']}\n\n"
                     f"Approve the expense or deny the request?")
        
        def approve_expense(gs):
            if gs.money >= expense['cost']:
                expense['approve_effect'](gs)
                gs.messages.append(f"Approved: {expense['item']} (${expense['cost']})")
                return f"Expense approved. {expense['employee']} appreciates the investment."
            else:
                gs.messages.append(f"Insufficient funds to approve {expense['item']} (need ${expense['cost']}, have ${gs.money})")
                return "Insufficient funds for approval."
        
        def deny_expense(gs):
            expense['deny_effect'](gs)
            gs.messages.append(f"Denied: {expense['item']}")
            return f"Expense request denied. {expense['employee']} understands the budget constraints."
        
        # Create event with approve/deny options
        popup_event = Event(
            name=event_name,
            desc=event_desc,
            trigger=lambda gs: True,  # Already triggered
            effect=approve_expense,   # Default effect is approval
            event_type=EventType.POPUP,
            available_actions=[EventAction.ACCEPT, EventAction.DISMISS],
            reduce_effect=deny_expense
        )
        
        # Add to popup event queue if enhanced events are enabled
        if getattr(self, 'enhanced_events_enabled', False):
            if not hasattr(self, 'pending_popup_events'):
                self.pending_popup_events = []
            self.pending_popup_events.append(popup_event)
        else:
            # Fallback to simple message-based system
            self.messages.append(f"EXPENSE REQUEST: {expense['employee']} requests {expense['item']} (${expense['cost']})")
            self.messages.append(f"Purpose: {expense['description']}")
            self.messages.append("Enhanced event system required for interactive expense approval.")
    
    def _trigger_hiring_dialog(self):
        """Trigger the employee hiring dialog with available employee subtypes."""
        from src.core.employee_subtypes import get_available_subtypes, get_hiring_complexity_level
        
        # Get available employee subtypes based on current game state
        available_subtypes = get_available_subtypes(self)
        complexity_level = get_hiring_complexity_level(self)
        
        if not available_subtypes:
            self.messages.append("No employees available for hiring at this time.")
            return
        
        # Set up the hiring dialog state
        self.pending_hiring_dialog = {
            "available_subtypes": available_subtypes,
            "complexity_level": complexity_level,
            "title": f"Hire Employee - {complexity_level['description']}",
            "description": complexity_level['complexity_note']
        }
    
    def select_employee_subtype(self, subtype_id):
        """Handle player selection of an employee subtype."""
        if not self.pending_hiring_dialog:
            return False, "No hiring dialog active."
        
        # Find the selected subtype
        selected_subtype = None
        for subtype_info in self.pending_hiring_dialog["available_subtypes"]:
            if subtype_info["id"] == subtype_id:
                selected_subtype = subtype_info
                break
        
        if not selected_subtype:
            return False, f"Invalid employee subtype: {subtype_id}"
        
        if not selected_subtype["affordable"]:
            return False, f"Cannot afford {selected_subtype['data']['name']} - need ${selected_subtype['data']['cost']} and {selected_subtype['data']['ap_cost']} AP"
        
        # Deduct costs
        subtype_data = selected_subtype["data"]
        self.money -= subtype_data["cost"]
        self.action_points -= subtype_data["ap_cost"]
        
        # Apply employee effects
        from src.core.employee_subtypes import apply_subtype_effects
        success, message = apply_subtype_effects(self, subtype_id)
        
        if success:
            self.messages.append(message)
            # Clear the hiring dialog
            self.pending_hiring_dialog = None
            return True, message
        else:
            # Refund if something went wrong
            self.money += subtype_data["cost"]
            self.action_points += subtype_data["ap_cost"]
            return False, message
    
    def dismiss_hiring_dialog(self):
        """Dismiss the hiring dialog without making a selection."""
        if self.pending_hiring_dialog:
            self.pending_hiring_dialog = None
    
    def _create_upgrade_transition(self, upgrade_idx, start_rect, end_rect):
        """Create a smooth transition animation for an upgrade moving from button to icon."""
        transition = {
            'type': 'upgrade_transition',
            'upgrade_idx': upgrade_idx,
            'start_rect': start_rect,
            'end_rect': end_rect,
            'progress': 0.0,
            'duration': 45,  # Longer duration for more elegant motion (1.5 seconds)
            'trail_points': [],  # For visual trail effect
            'particle_trail': [],  # Enhanced particle system for more dramatic effect
            'glow_timer': 90,  # Extended glow time for better visual feedback
            'glow_intensity': 0,  # Current glow intensity for smooth fade-in
            'completed': False,
            'arc_height': 80,  # More dramatic arc height
            'ease_type': 'cubic_out'  # Smooth deceleration easing
        }
        self.ui_transitions.append(transition)
        self.upgrade_transitions[upgrade_idx] = transition
        return transition
    
    def _update_ui_transitions(self):
        """Update all active UI transitions."""
        transitions_to_remove = []
        
        for transition in self.ui_transitions:
            if transition['type'] == 'upgrade_transition':
                self._update_upgrade_transition(transition)
                
                # Mark completed transitions for removal
                if transition['completed'] and transition['glow_timer'] <= 0:
                    transitions_to_remove.append(transition)
        
        # Remove completed transitions
        for transition in transitions_to_remove:
            self.ui_transitions.remove(transition)
            if transition['upgrade_idx'] in self.upgrade_transitions:
                del self.upgrade_transitions[transition['upgrade_idx']]
    
    def _update_upgrade_transition(self, transition):
        """Update a single upgrade transition animation with enhanced effects."""
        if not transition['completed']:
            # Advance animation progress with configurable easing
            transition['progress'] = min(1.0, transition['progress'] + (1.0 / transition['duration']))
            
            # Calculate eased progress for smoother motion
            eased_progress = self._apply_easing(transition['progress'], transition.get('ease_type', 'cubic_out'))
            
            # Add trail point for current position
            current_pos = self._interpolate_position(
                transition['start_rect'], 
                transition['end_rect'], 
                eased_progress,
                transition.get('arc_height', 80)
            )
            
            # Enhanced trail system with varying properties
            transition['trail_points'].append({
                'pos': current_pos,
                'alpha': 255,
                'age': 0,
                'size': 12,  # Larger initial size
                'color_variation': random.randint(-20, 20)  # Color variation for organic feel
            })
            
            # Add particle effects for more dramatic visual impact
            if len(transition['trail_points']) % 3 == 0:  # Every 3rd frame
                self._add_particle_to_trail(transition, current_pos)
            
            # Limit trail length for performance
            if len(transition['trail_points']) > 15:  # Longer trail
                transition['trail_points'].pop(0)
            
            # Mark as completed when progress reaches 1.0
            if transition['progress'] >= 1.0:
                transition['completed'] = True
        
        # Update trail points with enhanced fading
        for point in transition['trail_points']:
            point['age'] += 1
            # Smoother alpha fade with size reduction
            fade_factor = max(0, 1.0 - (point['age'] / 20.0))
            point['alpha'] = int(255 * fade_factor)
            point['size'] = max(2, int(point['size'] * fade_factor))
        
        # Update particle trail
        for particle in transition.get('particle_trail', []):
            particle['age'] += 1
            particle['alpha'] = max(0, 180 - (particle['age'] * 12))
            # Add slight drift to particles
            particle['pos'][0] += particle['velocity'][0]
            particle['pos'][1] += particle['velocity'][1]
            particle['velocity'][1] += 0.2  # Gravity effect
        
        # Remove fully faded elements
        transition['trail_points'] = [p for p in transition['trail_points'] if p['alpha'] > 0]
        transition['particle_trail'] = [p for p in transition.get('particle_trail', []) if p['alpha'] > 0]
        
        # Enhanced glow system with smooth fade-in and pulsing
        if transition['completed']:
            if transition['glow_timer'] > 0:
                transition['glow_timer'] -= 1
                # Smooth glow intensity changes
                max_intensity = 255
                fade_duration = 30
                if transition['glow_timer'] > fade_duration:
                    transition['glow_intensity'] = min(max_intensity, transition['glow_intensity'] + 8)
                else:
                    # Fade out
                    transition['glow_intensity'] = int(max_intensity * (transition['glow_timer'] / fade_duration))
        else:
            # Building up glow as transition progresses
            transition['glow_intensity'] = int(100 * transition['progress'])
    
    def _interpolate_position(self, start_rect, end_rect, progress, arc_height=80):
        """Interpolate position between start and end rectangles with enhanced curved motion."""
        # Use easeOutCubic for smooth deceleration
        eased_progress = 1 - (1 - progress) ** 3
        
        start_x = start_rect[0] + start_rect[2] // 2  # Center of start rect
        start_y = start_rect[1] + start_rect[3] // 2
        end_x = end_rect[0] + end_rect[2] // 2  # Center of end rect  
        end_y = end_rect[1] + end_rect[3] // 2
        
        # Create more dramatic curved arc path
        mid_x = (start_x + end_x) / 2
        # Dynamic arc height based on distance and direction
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        dynamic_arc_height = min(arc_height, distance * 0.3)  # Scale with distance
        mid_y = min(start_y, end_y) - dynamic_arc_height
        
        # Enhanced Bezier curve with control points for more elegant motion
        t = eased_progress
        
        # Use cubic Bezier for even smoother curves
        control1_x = start_x + (mid_x - start_x) * 0.5
        control1_y = start_y - dynamic_arc_height * 0.3
        control2_x = end_x - (end_x - mid_x) * 0.5  
        control2_y = end_y - dynamic_arc_height * 0.3
        
        # Cubic Bezier interpolation for ultra-smooth motion
        x = ((1-t)**3 * start_x + 
             3*(1-t)**2*t * control1_x + 
             3*(1-t)*t**2 * control2_x + 
             t**3 * end_x)
        y = ((1-t)**3 * start_y + 
             3*(1-t)**2*t * control1_y + 
             3*(1-t)*t**2 * control2_y + 
             t**3 * end_y)
        
        return (int(x), int(y))
    
    def _apply_easing(self, t, ease_type='cubic_out'):
        """Apply easing function for smoother animations."""
        if ease_type == 'cubic_out':
            return 1 - (1 - t) ** 3
        elif ease_type == 'elastic_out':
            import math
            if t == 0 or t == 1:
                return t
            return (2 ** (-10 * t)) * math.sin((t - 0.1) * 2 * math.pi / 0.4) + 1
        elif ease_type == 'back_out':
            c1 = 1.70158
            c3 = c1 + 1
            return 1 + c3 * ((t - 1) ** 3) + c1 * ((t - 1) ** 2)
        else:
            return t  # Linear fallback
    
    def _add_particle_to_trail(self, transition, position):
        """Add particle effects to transition trail."""
        if 'particle_trail' not in transition:
            transition['particle_trail'] = []
        
        # Create multiple particles for richer effect
        for _ in range(2):
            particle = {
                'pos': [position[0] + random.randint(-5, 5), position[1] + random.randint(-5, 5)],
                'velocity': [random.uniform(-1, 1), random.uniform(-2, 0)],
                'alpha': 180,
                'age': 0,
                'size': random.randint(3, 8),
                'color_shift': random.randint(-30, 30)
            }
            transition['particle_trail'].append(particle)
    
    def track_error(self, error_message: str) -> bool:
        """
        Track an error for the easter egg beep system.
        
        Args:
            error_message: The error message that occurred
            
        Returns:
            bool: True if this triggers the easter egg (3 repeated identical errors)
        """
        return self.error_tracker.track_error(error_message)
    
    def log_ui_interaction(self, interaction_type: str, element_id: str, details: dict = None):
        """
        Log UI interactions for accessibility and debugging.
        
        Args:
            interaction_type: Type of interaction (click, hover, keyboard, etc.)
            element_id: ID of the UI element
            details: Additional details about the interaction
        """
        log_data = {
            'type': interaction_type,
            'element': element_id,
            'turn': self.turn,
            'timestamp': getattr(pygame.time, 'get_ticks', lambda: 0)()
        }
        
        if details:
            log_data.update(details)
            
        # Could extend this to write to accessibility logs if needed
        # For now, just track in memory for potential error detection
        if hasattr(self, 'ui_interaction_log'):
            self.ui_interaction_log.append(log_data)
        else:
            self.ui_interaction_log = [log_data]
    
    def handle_insufficient_resources(self, resource_type: str, required: int, available: int) -> bool:
        """
        Handle cases where player tries to perform action without sufficient resources.
        Provides standardized error messages and tracking.
        
        Args:
            resource_type: Type of resource (money, action_points, staff, etc.)
            required: Amount required
            available: Amount available
            
        Returns:
            bool: True if error was tracked (for potential easter egg)
        """
        error_msg = f"Insufficient {resource_type}: need {required}, have {available}"
        
        # Add user-friendly message to game log
        if resource_type == "money":
            self.messages.append(f"Need ${required}, but only have ${available}")
        elif resource_type == "action_points":
            self.messages.append(f"Need {required} AP, but only have {available} remaining")
        elif resource_type == "staff":
            self.messages.append(f"Need {required} staff, but only have {available}")
        else:
            self.messages.append(f"Need {required} {resource_type}, but only have {available}")
        
        # Track for easter egg detection
        return self.track_error(error_msg)
    
    def validate_action_requirements(self, action_index: int) -> Tuple[bool, str]:
        """
        Validate if an action can be performed, with detailed error reporting.
        
        Args:
            action_index: Index of action to validate
            
        Returns:
            Tuple[bool, str]: (can_perform, error_message)
        """
        if action_index >= len(self.actions):
            return False, "Invalid action"
            
        action = self.actions[action_index]
        
        # Check money requirement
        cost = action.get("cost", 0)
        if cost > self.money:
            self.handle_insufficient_resources("money", cost, self.money)
            return False, f"Insufficient money: need ${cost}, have ${self.money}"
        
        # Check action points requirement
        ap_cost = action.get("ap_cost", 1)
        if ap_cost > self.action_points:
            self.handle_insufficient_resources("action_points", ap_cost, self.action_points)
            return False, f"Insufficient action points: need {ap_cost}, have {self.action_points}"
        
        # Check if action is available (using action rules system)
        from src.core.action_rules import ActionRules
        action_rules = ActionRules()
        if not action_rules.is_action_available(action["name"], self):
            error_msg = f"Action '{action['name']}' not available"
            self.track_error(error_msg)
            return False, error_msg
        
        return True, "OK"

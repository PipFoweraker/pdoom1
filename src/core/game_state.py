from src.services.deterministic_rng import get_rng
import json
import os
import pygame

from typing import Tuple, Dict, Any, Optional, List, Union, Callable, TYPE_CHECKING

from src.core.actions import ACTIONS
from src.core.upgrades import UPGRADES
from src.core.events import EVENTS
from src.services.game_logger import GameLogger
from src.services.game_run_logger import GameRunLogger, LoggingLevel, init_game_logger
from src.services.sound_manager import SoundManager
from src.services.game_clock import GameClock
from src.services.deterministic_rng import init_deterministic_rng, get_rng
from src.services.verbose_logging import init_verbose_logging, LogLevel
from src.services.leaderboard import init_leaderboard_system
from src.core.opponents import create_default_opponents
from src.features.event_system import DeferredEventQueue, EventType, EventAction, Event
from src.features.onboarding import onboarding
from src.features.achievements_endgame import achievements_endgame_system
from src.ui.overlay_manager import OverlayManager
from src.services.error_tracker import ErrorTracker
from src.services.config_manager import get_current_config
from src.core.productive_actions import (get_employee_category, get_available_actions, 
                               check_action_requirements)
# End game scenarios now handled by TurnManager - import removed to avoid conflicts
from src.core.research_quality import TechnicalDebt, ResearchQuality, ResearchProject
from src.core.economic_config import EconomicConfig
from src.core.turn_manager import TurnManager
from src.core.game_constants import (
    SCORE_FILE, DEFAULT_STARTING_RESOURCES, HIGH_DOOM_WARNING_THRESHOLD,
    DEFAULT_STAFF_MAINTENANCE, HIGH_REPUTATION_THRESHOLD, LOW_REPUTATION_THRESHOLD,
    HIGH_TRUST_VALUE, LOW_TRUST_VALUE, DEFAULT_ACTION_POINTS
)
from src.core.ui_utils import (
    get_action_rects, get_upgrade_rects, get_upgrade_icon_rect, get_context_window_top,
    get_endturn_rect, get_mute_button_rect, get_activity_log_minimize_button_rect,
    get_activity_log_expand_button_rect, get_activity_log_rect, get_activity_log_base_position,
    get_activity_log_current_position, validate_rect
)
from src.core.verbose_logging import (
    create_verbose_money_message, create_verbose_staff_message, 
    create_verbose_reputation_message, create_verbose_compute_message
)
from src.core.employee_management import (
    reset_employee_productivity, separate_employees_and_managers,
    apply_management_assignments, calculate_compute_per_employee
)
from src.core.dialog_systems import (
    DialogManager, FundraisingDialogBuilder, ResearchDialogBuilder, DialogValidator
)
from src.core.input_manager import InputManager
from src.core.employee_blob_manager import EmployeeBlobManager
from src.core.ui_transition_manager import UITransitionManager
from src.core.deterministic_event_manager import DeterministicEventManager
from src.core.utility_functions import (
    is_upgrade_available, check_point_in_rect, process_achievements_and_warnings_complete,
    filter_available_upgrades, get_milestone_check_functions
)

class GameState:
    def _get_action_cost(self, action: Dict[str, Any]) -> int:
        """
        Helper method to evaluate action cost, handling both static costs and callable costs.
        """
        cost = action["cost"]
        if callable(cost):
            return cost(self)
        return cost
    
    def _get_action_ap_cost(self, action: Dict[str, Any]) -> int:
        """
        Helper method to calculate AP cost based on action type.
        Setting actions (research speed) cost 0 AP, others use ap_cost field.
        """
        action_type = action.get("action_type", "action")
        if action_type == "setting":
            return 0
        return action.get("ap_cost", 1)
    
    def _add(self, attr: str, val: float, reason: str = "") -> None:
        """
        Adds val to the given attribute, clamping where appropriate.
        Also records last_balance_change for 'money' for use in UI,
        if accounting software has been purchased.
        """
        # Log resource change for debugging and verification
        old_value = getattr(self, attr, 0)
        
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
            
            # Track minimum money for strategic analysis
            if self.money < self.min_money_reached:
                self.min_money_reached = self.money
            
            # Add verbose activity log message for money changes
            if val != 0:
                self._add_verbose_money_message(val, reason)
        elif attr == 'doom':
            old_doom = self.doom
            self.doom = min(max(self.doom + val, 0), self.max_doom)
            
            # Track peak doom for strategic analysis
            if self.doom > self.max_doom_reached:
                self.max_doom_reached = self.doom
            
            # Add doom change to activity log with attribution
            if val != 0:
                change_str = f"+{val}" if val > 0 else str(val)
                reason_text = reason or "unspecified cause"
                self.messages.append(f"p(Doom) {change_str}: {reason_text}")
            
            # Trigger high doom warning (existing system)
            if old_doom < HIGH_DOOM_WARNING_THRESHOLD and self.doom >= HIGH_DOOM_WARNING_THRESHOLD and onboarding.should_show_mechanic_help('high_doom_warning'):
                onboarding.mark_mechanic_seen('high_doom_warning')
                
        elif attr == 'reputation':
            self.reputation = max(self.reputation + val, 0)
            
            # Track peak reputation for strategic analysis
            if self.reputation > self.peak_reputation:
                self.peak_reputation = self.reputation
            
            # Add verbose activity log message for reputation changes
            if val != 0:
                self._add_verbose_reputation_message(val, reason)
        elif attr == 'staff':
            old_staff = self.staff
            self.staff = max(self.staff + val, 0)
            # Update employee blobs when staff changes
            if val > 0:  # Hiring
                self._add_employee_blobs(val)
                # FIXED: Only mark first staff hire as seen when we actually hire BEYOND starting staff
                # Check if this is first manual hire (from starting count)
                from src.services.config_manager import get_current_config
                starting_staff = get_current_config().get('starting_resources', {}).get('staff', 2)
                if old_staff == starting_staff and val > 0:
                    # This is the first manual hire - mark as seen so hint won't show again
                    onboarding.mark_mechanic_seen('first_staff_hire')
            elif val < 0:  # Staff leaving
                self._remove_employee_blobs(old_staff - self.staff)
            
            # Add verbose activity log message for staff changes
            if val != 0:
                self._add_verbose_staff_message(val, reason)
        elif attr == 'compute':
            self.compute = max(self.compute + val, 0)
            
            # Add verbose activity log message for compute changes
            if val != 0:
                self._add_verbose_compute_message(val, reason)
        elif attr == 'research_progress':
            self.research_progress = max(self.research_progress + val, 0)
        elif attr == 'admin_staff':
            self.admin_staff = max(self.admin_staff + val, 0)
        elif attr == 'research_staff':
            self.research_staff = max(self.research_staff + val, 0)
        elif attr == 'ops_staff':
            self.ops_staff = max(self.ops_staff + val, 0)
        
        # Log the change for debugging and verification
        new_value = getattr(self, attr, 0)
        if hasattr(self, 'turn'):
            try:
                from src.services.verbose_logging import get_logger, is_logging_enabled
                if is_logging_enabled():
                    logger = get_logger()
                    reason_for_log = reason or f"_add({attr}, {val})"
                    logger.log_resource_change(
                        self.turn, attr, old_value, new_value, reason_for_log
                    )
            except Exception:
                pass  # Don't break game if logging fails
        
        return None

# Ensure last_balance_change gets set on any direct subtraction/addition to money:
# For example, in end_turn, after maintenance:
# self._add('money', -maintenance_cost)
# (Replace raw self.money -= maintenance_cost with self._add('money', -maintenance_cost))

# In __init__, initialize:

    def __init__(self, seed: str) -> None:
        # Get current configuration with safe defaults
        config = get_current_config()
        
        # Safe configuration access with defaults
        starting_resources = config.get('starting_resources', DEFAULT_STARTING_RESOURCES)
        ap_config = config.get('action_points', {'base_ap_per_turn': 3})
        limits_config = config.get('resource_limits', {})
        milestones_config = config.get('milestones', {})
        
        # Initialize deterministic systems first
        init_deterministic_rng(seed)
        
        # Initialize verbose logging if enabled in config
        log_level = LogLevel.STANDARD  # Default
        if config.get('advanced', {}).get('debug_mode', False):
            log_level = LogLevel.DEBUG
        elif config.get('advanced', {}).get('verbose_logging', False):
            log_level = LogLevel.VERBOSE
            
        init_verbose_logging(seed, log_level)
        
        # Initialize leaderboard system
        init_leaderboard_system()
        
        # Lab identity for pseudonymous gameplay
        from src.services.lab_name_manager import get_lab_name_manager
        lab_name_manager = get_lab_name_manager()
        self.lab_name = lab_name_manager.get_random_lab_name(seed)
        
        # Player identity (separate from lab branding)
        self.player_name = "Anonymous"  # Can be customized by player
        
        # Initialize economic configuration system
        self.economic_config = EconomicConfig()
        
        self.last_balance_change = 0
        self.accounting_software_bought = False  # So the flag always exists
        
        # Research Quality System - Technical Debt vs. Speed Trade-offs
        self.technical_debt = TechnicalDebt()  # Track accumulated technical debt
        self.current_research_quality = ResearchQuality.STANDARD  # Default research approach
        self.active_research_projects = []  # List of ongoing research projects
        self.completed_research_projects = []  # History of completed projects
        self.research_quality_unlocked = False  # Unlocks after first research action
        
        # Core resources (from config with safe defaults)
        self.money = starting_resources.get('money', 100)
        self.staff = starting_resources.get('staff', 2)
        self.reputation = starting_resources.get('reputation', 5)
        self.doom = starting_resources.get('doom', 25)
        self.compute = starting_resources.get('compute', 0)
        self.research_progress = 0  # Track research progress for paper generation
        self.papers_published = 0  # Count of research papers published
        
        # Action Points system (from config with safe defaults)
        self.action_points = starting_resources.get('action_points', 3)
        self.max_action_points = ap_config.get('base_ap_per_turn', 3)
        self.ap_spent_this_turn = False  # Track if AP was spent for UI glow effects
        self.ap_glow_timer = 0  # Timer for AP glow animation
        
        # Phase 2: Staff-Based AP Scaling
        self.admin_staff = 0  # Admin assistants: +1.0 AP each
        self.research_staff = 0  # Research staff: Enable research action delegation
        self.ops_staff = 0  # Operations staff: Enable operational action delegation
        
        self.turn = 0
        self.max_doom = limits_config['max_doom']
        self.selected_gameplay_actions = []
        self.selected_gameplay_action_instances = []  # Track individual action instances for undo
        self.gameplay_action_clicks_this_turn = {}  # Track clicks per action per turn
        self.staff_maintenance = DEFAULT_STAFF_MAINTENANCE
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
        
        # Game clock system - tracks game time and advances weekly
        self.game_clock = GameClock()  # Initialize game clock starting at first Monday in April 2016
        
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
        
        # Achievements & Endgame System (Issue #195)
        self.unlocked_achievements = set()  # Achievement IDs that have been unlocked
        self.achievement_notifications = []  # Queue of achievement notifications to display
        self.peak_reputation = self.reputation  # Track highest reputation achieved
        self.min_money_reached = self.money    # Track lowest money reached (for crisis analysis)
        self.max_doom_reached = self.doom      # Track highest doom reached (for analysis)
        
        # Enhanced Personnel System
        self.researchers = []  # List of individual Researcher objects
        self.available_researchers = []  # Researchers available for hiring this turn
        self.researcher_hiring_pool_refreshed = False  # Track if hiring pool was refreshed
        
        # Researcher Assignment System for Issue #190
        self.researcher_assignments = {}  # Maps researcher_id -> assigned_task_name
        self.task_quality_overrides = {}  # Maps task_name -> ResearchQuality override
        self.researcher_default_quality = {}  # Maps researcher_id -> default ResearchQuality
        
        # Economic Cycles & Funding Volatility System for Issue #192
        from src.features.economic_cycles import EconomicCycles
        self.economic_cycles = EconomicCycles(self)
        self.funding_round_cooldown = 0  # Prevent excessive fundraising
        self.emergency_measures_available = True  # Track if emergency options are still available
        
        # Technical Failure Cascades System for Issue #193
        from src.features.technical_failures import TechnicalFailureCascades
        self.technical_failures = TechnicalFailureCascades(self)
        
        # Enhanced Leaderboard System for v0.4.1
        from src.scores.enhanced_leaderboard import leaderboard_manager
        self.leaderboard_manager = leaderboard_manager
        self.leaderboard_manager.start_game_session(self)
        
        # Context window tracking
        self.context_window_minimized = False
        self.current_context_info = None
        
        # For hover/tooltip (which upgrade is hovered)
        self.hovered_upgrade_idx = None
        self.hovered_gameplay_action_idx = None
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
        
        # Input management system
        self.input_manager = InputManager(self)
        self.employee_blob_manager = EmployeeBlobManager(self)
        
        # UI transition system for smooth visual feedback
        self.ui_transition_manager = UITransitionManager(self)
        
        # Deterministic event system for competitive gameplay
        self.deterministic_event_manager = DeterministicEventManager(self)
        
        # Research system management for quality, debt, and assignments
        if TYPE_CHECKING:
            from src.core.research_system_manager import ResearchSystemManager
            from src.core.intelligence_system_manager import IntelligenceSystemManager
            from src.core.media_pr_system_manager import MediaPRSystemManager
        else:
            from src.core.research_system_manager import ResearchSystemManager
            from src.core.intelligence_system_manager import IntelligenceSystemManager
            from src.core.media_pr_system_manager import MediaPRSystemManager
        self.research_system = ResearchSystemManager(self)
        self.intelligence_system = IntelligenceSystemManager(self)
        self.media_pr_system = MediaPRSystemManager(self)

        # Tutorial and onboarding system
        self.tutorial_enabled = True  # Whether tutorial is enabled (default True for new players)
        self.tutorial_shown_milestones = set()  # Track which milestone tutorials have been shown
        self.pending_tutorial_message = None  # Current tutorial message waiting to be shown
        self.first_game_launch = True  # Track if this is the first game launch
        
        # Employee hiring dialog system
        self.pending_hiring_dialog = None  # Current hiring dialog waiting for player selection
        # Fundraising dialog system
        self.pending_fundraising_dialog = None  # Current fundraising dialog waiting for player selection
        # Research dialog system
        self.pending_research_dialog = None  # Current research dialog waiting for player selection
        # Intelligence dialog system
        self.pending_intelligence_dialog = None  # Current intelligence dialog waiting for player selection
        # Media & PR dialog system
        self.pending_media_dialog = None  # Current media dialog waiting for player selection
        # Infrastructure dialog system
        self.pending_infrastructure_dialog = None  # Current infrastructure dialog waiting for player selection
        # Technical debt dialog system
        self.pending_technical_debt_dialog = None  # Current technical debt dialog waiting for player selection
        # Advanced funding dialog system
        self.pending_advanced_funding_dialog = None  # Current advanced funding dialog waiting for player selection
        # Operations dialog system
        self.pending_operations_dialog = None  # Current operations dialog waiting for player selection
        self._pending_first_time_help = None  # Track pending first-time help to show

        # Copy modular content
        self.gameplay_actions = [dict(a) for a in ACTIONS]
        self.game_events = [dict(e) for e in EVENTS]
        
        # Enhanced event system (from config)
        gameplay_config = config.get('gameplay', {})
        self.deferred_events = DeferredEventQueue()
        self.pending_popup_events = []  # Events waiting for player action
        self.enhanced_events_enabled = gameplay_config.get('enhanced_events_enabled', False)  # Flag to enable new event types
        
        # Public Opinion & Media System
        from src.features.public_opinion import PublicOpinion
        from src.features.media_system import MediaSystem
        self.company_name = "Your Lab"  # Default player organization name
        self.public_opinion = PublicOpinion()
        self.media_system = MediaSystem(self.public_opinion)
        
        # Initialize public opinion based on starting reputation
        if self.reputation > HIGH_REPUTATION_THRESHOLD:
            self.public_opinion.trust_in_player = HIGH_TRUST_VALUE
        elif self.reputation < LOW_REPUTATION_THRESHOLD:
            self.public_opinion.trust_in_player = LOW_TRUST_VALUE
        
        # Initialize game logger (original system for basic events)
        self.logger = GameLogger(seed)
        
        # Initialize game run logger (new privacy-respecting analytics system)
        # Enable by default for alpha testing - collect comprehensive strategy data
        self.run_logger = init_game_logger(LoggingLevel.STANDARD, enabled_by_default=True)
        
        # Initialize UI overlay management system
        self.overlay_manager = OverlayManager()
        
        # Initialize error tracking system (replaces duplicate error tracking logic)
        self.error_tracker = ErrorTracker(
            sound_manager=self.sound_manager,
            message_callback=lambda msg: self.messages.append(msg)
        )
        
        # UI Transition System now handled by UITransitionManager
        
        # Turn Processing State for reliable input handling
        self.turn_processing = False  # True during turn transition
        self.turn_processing_timer = 0  # Timer for turn transition duration
        self.turn_processing_duration = 3  # Frames for turn transition (minimal delay, extensible)
        
        # Game Flow Improvements
        self.delayed_actions = []  # Actions that resolve after N turns
        self.daily_news = []  # News feed for turn feedback
        self.spend_this_turn_display_shown = False  # Track if spend display has been shown
        self.spend_display_permanent = False  # Whether spend display is permanently visible
        
        # Turn Processing Manager (extracted from monolithic end_turn method)
        self.turn_manager = TurnManager(self)
        
        # Initialize employee blobs for starting staff
        self.employee_blob_manager.initialize_employee_blobs()
        
        # Office Cat System - Enhanced interactive pet mechanics for dev engagement
        self.office_cat_adopted = False  # Whether any cats have been adopted
        self.office_cats_adopted = False  # Legacy compatibility with existing event system
        self.office_cat_position = (0, 0)  # Current cat position on screen
        self.office_cat_target_position = (400, 300)  # Where cat should be
        self.office_cat_last_petted = 0  # Turn when cat was last petted
        self.office_cat_love_emoji_timer = 0  # Timer for love emoji display
        self.office_cat_love_emoji_pos = (0, 0)  # Position for love emoji
        self.office_cat_total_food_cost = 0  # Total spent on cat food (for stats)
        self.office_cat_total_pets = 0  # Total times cat was petted (for stats)
        self.office_cat_turns_with_5_staff = 0  # Track consecutive turns with 5+ staff
        self.office_cat_adoption_offered = False  # Track if adoption event was already shown
        
        # Load tutorial settings (after initialization)
        self.load_tutorial_settings()

    @property
    def actions(self) -> List[Dict[str, Any]]:
        """Alias for gameplay_actions for UI compatibility."""
        return self.gameplay_actions

    def calculate_max_ap(self) -> int:
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
    
    def add_delayed_action(self, action_name: str, delay_turns: int, effects: Dict[str, Any]) -> None:
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
    
    def process_delayed_actions(self) -> List[Dict[str, Any]]:
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
                self.messages.append(f"[OK] {action['action_name']} completed!")
                
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
        
        # Use deterministic RNG for consistent news per turn
        selected_news = get_rng().choice(news_items, f"news_generation_turn_{self.turn}")
        
        return f"[NEWS] Day {self.turn + 1}: {selected_news}"
    
    def update_spend_tracking(self) -> None:
        """Update spend tracking display logic."""
        if self.spend_this_turn > 0:
            if not self.spend_this_turn_display_shown:
                # First time spending multiple actions in a turn
                spend_actions_count = len([a for a in self.selected_gameplay_actions if any(cost > 0 for cost in [a.get('money_cost', 0), a.get('reputation_cost', 0)])])
                
                if spend_actions_count > 1:
                    self.spend_this_turn_display_shown = True
                    self.messages.append(f"? Total spend this turn: ${self.spend_this_turn}")
                    
                    # If this happens again, make display permanent
                    if hasattr(self, '_previous_multi_spend'):
                        self.spend_display_permanent = True
                        self.messages.append("? Spend tracking enabled permanently.")
                    else:
                        self._previous_multi_spend = True

    def add_message(self, message: str) -> None:
        """
        Add a message to the game's message log with overflow protection.
        
        Args:
            message (str): The message to add
        """
        self.messages.append(message)
        
        # Too Many Messages Bug Fix: Implement message cap to prevent UI overflow
        max_messages_per_turn = 50  # Reasonable limit for readability
        if len(self.messages) > max_messages_per_turn:
            # Keep most recent messages and add overflow indicator
            overflow_count = len(self.messages) - max_messages_per_turn + 1
            self.messages = self.messages[-max_messages_per_turn + 1:]
            self.messages.insert(0, f"... {overflow_count} older messages hidden to prevent overflow ...")

    def can_delegate_action(self, action: Dict[str, Any]) -> bool:
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
    
    def execute_gameplay_action_with_delegation(self, action_idx: int, delegate: bool = False) -> bool:
        """
        Execute a gameplay action with optional delegation.
        
        Args:
            action_idx (int): Index of the gameplay action to execute
            delegate (bool): Whether to delegate the action
            
        Returns:
            bool: True if action was executed, False if not enough resources
        """
        action = self.gameplay_actions[action_idx]
        
        # Determine AP cost and effectiveness
        if delegate and self.can_delegate_action(action):
            ap_cost = action.get("delegate_ap_cost", self._get_action_ap_cost(action))
            effectiveness = action.get("delegate_effectiveness", 1.0)
            delegation_info = " (delegated)"
        else:
            ap_cost = self._get_action_ap_cost(action)
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
        
        action_cost = self._get_action_cost(action)
        if self.money < action_cost:
            error_msg = f"Not enough money for {action['name']} (need ${action_cost}, have ${self.money})."
            self.messages.append(error_msg)
            
            # Track error for easter egg detection
            self.track_error(f"Insufficient money: {action['name']}")
            
            return False
        
        # Execute the action
        self.selected_gameplay_actions.append(action_idx)
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

    def execute_gameplay_action_by_keyboard(self, action_idx: int) -> bool:
        """
        Execute a gameplay action via keyboard shortcut (1-9 keys).
        Now routes through unified action handler.
        
        Args:
            action_idx (int): Index of the gameplay action to execute (0-8 for keys 1-9)
            
        Returns:
            bool: True if action was executed successfully, False otherwise
        """
        if self.game_over:
            return False
            
        # Check for undo (if action is already selected, try to undo it)
        is_undo = action_idx in self.selected_gameplay_actions
        
        result = self.attempt_action_selection(action_idx, is_undo)
        
        if result['message']:
            # Message is already added by attempt_action_selection, but we need to handle error tracking
            if not result['success'] and "Not enough Action Points" in result['message']:
                # Error tracking for easter egg
                if self.track_error(result['message']):
                    self.sound_manager.play_error_beep()
        
        return result['success']

    def attempt_action_selection(self, action_idx: int, is_undo: bool = False) -> Dict[str, Any]:
        """
        Unified handler for all action selection attempts (both keyboard and mouse).
        
        Args:
            action_idx (int): Index of the action to select/unselect
            is_undo (bool): True if this is an undo operation
            
        Returns:
            dict: Result with 'success', 'message', 'play_sound' keys
        """
        if action_idx >= len(self.gameplay_actions) or action_idx < 0:
            return {'success': False, 'message': None, 'play_sound': False}
            
        action = self.gameplay_actions[action_idx]
        
        if is_undo:
            return self._handle_action_undo(action_idx, action)
        else:
            return self._handle_action_selection(action_idx, action)
    
    def _handle_action_selection(self, action_idx: int, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle selecting (clicking) an action."""
        # Check max clicks per action per turn (only if specified in action)
        if 'max_clicks_per_turn' in action:
            max_clicks = action['max_clicks_per_turn']
            current_clicks = self.gameplay_action_clicks_this_turn.get(action_idx, 0)
            
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
            action.get("delegate_ap_cost", self._get_action_ap_cost(action)) < self._get_action_ap_cost(action)):
            delegate = True
        
        # Determine AP cost and effectiveness
        if delegate:
            ap_cost = action.get("delegate_ap_cost", self._get_action_ap_cost(action))
            effectiveness = action.get("delegate_effectiveness", 1.0)
            delegation_info = " (delegated)"
        else:
            ap_cost = self._get_action_ap_cost(action)
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
        action_cost = self._get_action_cost(action)
        if self.money < action_cost:
            error_msg = f"Not enough money for {action['name']} (need ${action_cost}, have ${self.money})."
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
            'instance_id': len(self.selected_gameplay_action_instances)  # Unique identifier
        }
        
        # Add to selected actions (immediate deduction)
        self.selected_gameplay_actions.append(action_idx)
        self.selected_gameplay_action_instances.append(action_instance)
        
        # Track clicks per action per turn (only if action has limits)
        if 'max_clicks_per_turn' in action:
            self.gameplay_action_clicks_this_turn[action_idx] = self.gameplay_action_clicks_this_turn.get(action_idx, 0) + 1
        
        # Immediate AP deduction
        self.action_points -= ap_cost
        self.ap_spent_this_turn = True
        self.ap_glow_timer = 30
        
        # Invalidate action availability cache after AP change (Action Point Display Bug fix)
        from src.services.action_availability_manager import get_action_availability_manager
        get_action_availability_manager().invalidate_cache()
        
        # Handle immediate actions that should execute right away (like dialogs)
        # Check if this is a submenu action or known dialog action
        is_submenu_action = (
            action.get('action_type') == 'submenu' or
            action['name'] in ['Hire Staff', 'Intelligence']  # Special dialog actions without action_type
        )
        
        if is_submenu_action:
            # Execute immediately instead of deferring to end_turn
            try:
                # Remove from selected actions since it's executed immediately
                self.selected_gameplay_actions.pop()  # Remove the action we just added
                self.selected_gameplay_action_instances.pop()  # Remove the instance we just added
                
                action['upside'](self)
                success_msg = f"Executed: {action['name']}{delegation_info}"
                self.messages.append(success_msg)
                return {
                    'success': True,
                    'message': success_msg,
                    'play_sound': True
                }
            except Exception as e:
                # If immediate execution fails, restore AP and show error
                self.action_points += ap_cost
                # Also remove from selected actions list
                if self.selected_gameplay_actions and self.selected_gameplay_actions[-1] == action_idx:
                    self.selected_gameplay_actions.pop()
                if self.selected_gameplay_action_instances:
                    self.selected_gameplay_action_instances.pop()
                error_msg = f"Failed to execute {action['name']}: {str(e)}"
                self.messages.append(error_msg)
                return {
                    'success': False,
                    'message': error_msg,
                    'play_sound': False
                }
        
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
    
    def _handle_action_undo(self, action_idx: int, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unselecting (undoing) an action."""
        # Find the most recent instance of this action
        action_instance = None
        instance_index = None
        
        for i in range(len(self.selected_gameplay_action_instances) - 1, -1, -1):
            if self.selected_gameplay_action_instances[i]['action_idx'] == action_idx:
                action_instance = self.selected_gameplay_action_instances[i]
                instance_index = i
                break
        
        if action_instance is None:
            return {
                'success': False,
                'message': f"No selected instance of {action['name']} to undo.",
                'play_sound': False
            }
        
        # Remove the action instance
        self.selected_gameplay_action_instances.pop(instance_index)
        
        # Remove from selected_gameplay_actions (remove last occurrence)
        for i in range(len(self.selected_gameplay_actions) - 1, -1, -1):
            if self.selected_gameplay_actions[i] == action_idx:
                self.selected_gameplay_actions.pop(i)
                break
        
        # Refund AP
        self.action_points += action_instance['ap_cost']
        
        # Clean up delegation info if no more instances of this action
        if action_idx not in [inst['action_idx'] for inst in self.selected_gameplay_action_instances]:
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

    def _execute_action_with_effectiveness(self, action: Dict[str, Any], effect_type: str, effectiveness: float) -> None:
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
            
            # Apply effectiveness reduction to the changes
            if doom_change != 0:
                # Apply researcher doom effects for research actions
                if hasattr(self, 'researchers') and self.researchers and doom_change < 0:  # Doom reduction
                    researcher_effects = self.get_researcher_productivity_effects()
                    doom_bonus = researcher_effects.get('doom_reduction_bonus', 0)
                    doom_change = int(doom_change * effectiveness * (1 + doom_bonus))
                else:
                    doom_change = int(doom_change * effectiveness)
                self._add('doom', doom_change, "action effectiveness adjustment")
                
            if rep_change != 0:
                # Apply researcher reputation bonuses
                if hasattr(self, 'researchers') and self.researchers:
                    researcher_effects = self.get_researcher_productivity_effects()
                    rep_bonus = researcher_effects.get('reputation_bonus', 0)
                    rep_change = int(rep_change * effectiveness) + rep_bonus
                else:
                    rep_change = int(rep_change * effectiveness)
                self._add('reputation', rep_change)
                
            if money_change != 0:
                self._add('money', int(money_change * effectiveness))
            if staff_change != 0:
                self._add('staff', int(staff_change * effectiveness))
            if compute_change != 0:
                self._add('compute', int(compute_change * effectiveness))
                
            if research_change != 0:
                # Apply researcher research speed bonuses
                if hasattr(self, 'researchers') and self.researchers:
                    researcher_effects = self.get_researcher_productivity_effects()
                    speed_modifier = researcher_effects.get('research_speed_modifier', 1.0)
                    research_change = int(research_change * effectiveness * speed_modifier)
                else:
                    research_change = int(research_change * effectiveness)
                self._add('research_progress', research_change)
            
            # Add message about reduced effectiveness
            if effectiveness < 1.0:
                self.messages.append(f"Delegated action had {int(effectiveness * 100)}% effectiveness.")

    def _initialize_employee_blobs(self) -> None:
        """Initialize employee blobs for starting staff with improved positioning"""
        return self.employee_blob_manager.initialize_employee_blobs()
    
    def _add_employee_blobs(self, count: int) -> None:
        """Add new employee blobs with animation from side and improved positioning"""
        return self.employee_blob_manager.add_employee_blobs(count)
    
    def _calculate_blob_position(self, blob_index: int, screen_w: int = 1200, screen_h: int = 800) -> Tuple[int, int]:
        """Calculate initial blob position in the employee pen area."""
        return self.employee_blob_manager.calculate_blob_position(blob_index, screen_w, screen_h)
    
    def _get_ui_element_rects(self, screen_w: int = 1200, screen_h: int = 800) -> List[Tuple[int, int, int, int]]:
        """Get rectangles of all UI elements that employee blobs should avoid."""
        return self.employee_blob_manager.get_ui_element_rects(screen_w, screen_h)
    
    def _check_blob_ui_collision(self, blob_x: int, blob_y: int, blob_radius: int, ui_rects: List[Tuple[int, int, int, int]]) -> Tuple[bool, float, float]:
        """Check if a blob collides with any UI element (delegates to ui_utils)."""
        return self.employee_blob_manager.check_blob_ui_collision(blob_x, blob_y, blob_radius, ui_rects)
    
    def _update_blob_positions_dynamically(self, screen_w: int = 1200, screen_h: int = 800) -> None:
        """Update blob positions dynamically to avoid UI elements."""
        return self.employee_blob_manager.update_blob_positions_dynamically(screen_w, screen_h)
            
    def _add_manager_blob(self) -> None:
        """Add a new manager blob with animation from side"""
        return self.employee_blob_manager.add_manager_blob()
        
    def _reassign_employee_management(self) -> None:
        """Reassign employees to managers based on capacity and efficiency"""
        return self.employee_blob_manager.reassign_employee_management()
                
    def _hire_manager(self) -> None:
        """Hire a new manager to oversee employees"""
        # Add manager blob to the system
        self._add_manager_blob()
        
        # Increment staff count for the manager
        self.staff += 1
        
        # Play staff hiring sound
        if hasattr(self, 'sound_manager') and self.sound_manager.is_enabled():
            self.sound_manager.play_sound('popup_close')
        
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
                "? Each manager can oversee up to 9 employees\n"
                "? Unmanaged employees beyond 9 become unproductive (shown with red slash)\n"
                "? Managers appear as green blobs vs blue employee blobs\n"
                "? Manager hiring costs 1.5x normal employee cost\n\n"
                "Plan your team structure carefully as you scale!"
            )
        
        return None
        
    def _check_board_member_milestone(self) -> None:
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
                "? 2 board members now monitor your compliance\n"
                "? Search action unlocked (20% success rate for various benefits)\n"
                "? Audit risk accumulates until you become compliant\n"
                "? Purchase accounting software to prevent future oversight\n\n"
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
        
    def _board_search(self) -> None:
        """Perform board-mandated search action with 20% success rate"""
        if get_rng().random(f"board_search_success_turn_{self.turn}") < 0.2:  # 20% success rate
            # Successful search - find something valuable
            search_results = [
                ("regulatory compliance", lambda: self._add('reputation', 3)),
                ("cost savings opportunity", lambda: self._add('money', get_rng().randint(200, 500, f"board_search_money_turn_{self.turn}"))),
                ("process efficiency", lambda: self._add('doom', -2, "board search found process improvement")),
                ("staff optimization", lambda: None)  # Just a message
            ]
            
            result_name, result_effect = get_rng().choice(search_results, f"board_search_result_turn_{self.turn}")
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
            self.messages.append(get_rng().choice(search_failures, f"board_search_failure_turn_{self.turn}"))
            
        return None
            
    def _remove_employee_blobs(self, count: int) -> None:
        """Remove employee blobs when staff leave"""
        return self.employee_blob_manager.remove_employee_blobs(count)
                
    def _update_employee_productivity(self) -> None:
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
                blob_id = blob.get('id', len(self.employee_blobs))  # Use blob ID for deterministic context
                if get_rng().random(f"employee_research_chance_turn_{self.turn}_blob_{blob_id}") < 0.3:  # 30% chance per productive employee
                    base_research = get_rng().randint(1, 3, f"employee_research_amount_turn_{self.turn}_blob_{blob_id}")
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
            self._add('doom', int(doom_penalty), f"{unproductive_count} unproductive employees")
            
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
            
        # Update compute consumption
        self.compute = max(0, self.compute - compute_assigned)
        if compute_assigned > 0:
            self.messages.append(f"Compute consumed: {compute_assigned} (remaining: {self.compute})")
            
        return productive_employees



    def _scout_opponent(self) -> None:
        """Scout a specific opponent - delegated to intelligence system manager."""
        return self.intelligence_system.scout_opponent()
            
    def _spy(self) -> None:
        """Legacy espionage method - delegated to intelligence system manager."""
        return self.intelligence_system.spy()

    def _general_news_reading(self) -> None:
        """PLACEHOLDER: General news reading for market intelligence"""
        self.messages.append("PLACEHOLDER: Reading industry news and market reports...")
        # TODO: Implement news reading mechanics
        # - Gain market intelligence
        # - Learn about competitor moves
        # - Discover emerging trends
        # - Small reputation boost from staying informed
        
    def _general_networking(self) -> None:
        """PLACEHOLDER: General networking for business connections"""
        self.messages.append("PLACEHOLDER: Attending conferences and networking events...")
        # TODO: Implement networking mechanics
        # - Build industry connections
        # - Potential staff recruitment leads
        # - Reputation boost from visibility
        # - Chance to learn competitor information

    def _espionage_risk(self) -> Optional[str]:
        """Handle espionage risks - delegated to intelligence system manager."""
        return self.intelligence_system.espionage_risk()
        
    def _hire_manager(self) -> None:
        """Hire a new manager to oversee employees"""
        # Add manager blob to the system
        self._add_manager_blob()
        
        # Increment staff count for the manager
        self.staff += 1
        
        # Play staff hiring sound
        if hasattr(self, 'sound_manager') and self.sound_manager.is_enabled():
            self.sound_manager.play_sound('popup_close')
        
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
                "? Each manager can oversee up to 9 employees\n"
                "? Unmanaged employees beyond 9 become unproductive (shown with red slash)\n"
                "? Managers appear as green blobs vs blue employee blobs\n"
                "? Manager hiring costs 1.5x normal employee cost\n\n"
                "Plan your team structure carefully as you scale!"
            )
        
        return None

    def _breakthrough_event(self) -> None:
        if "secure_cloud" in self.upgrade_effects:
            spike = get_rng().randint(1, 2, f"breakthrough_spike_secure_turn_{self.turn}")
            self.messages.append("Lab breakthrough! Secure cloud softened doom spike.")
        else:
            spike = get_rng().randint(2, 4, f"breakthrough_spike_normal_turn_{self.turn}")  # Reduced from 6-13 for longer gameplay
            self.messages.append("Lab breakthrough! Doom spikes!")
        self._add('doom', spike, "AI lab breakthrough event")

    def handle_click(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Delegate mouse click handling to the input manager."""
        return self.input_manager.handle_click(mouse_pos, w, h)
    def handle_mouse_motion(self, mouse_pos: Tuple[int, int], w: int, h: int) -> None:
        """Delegate mouse motion handling to the input manager."""
        return self.input_manager.handle_mouse_motion(mouse_pos, w, h)

    def handle_mouse_release(self, mouse_pos: Tuple[int, int], w: int, h: int) -> bool:
        """Delegate mouse release handling to the input manager."""
        return self.input_manager.handle_mouse_release(mouse_pos, w, h)

    def check_hover(self, mouse_pos: Tuple[int, int], w: int, h: int) -> Optional[str]:
        """Delegate hover checking to the input manager."""
        return self.input_manager.check_hover(mouse_pos, w, h)

    def _get_action_rects(self, w: int, h: int) -> List[pygame.Rect]:
        # Place actions as tall buttons on left (moved down to accommodate opponents panel)
        count = len(self.gameplay_actions)
        base_x = int(w * 0.04)
        base_y = int(h * 0.28)  # Moved down from 0.16 to 0.28
        # Shrink width/height and reduce gaps to fit more buttons comfortably
        width = int(w * 0.30)
        height = int(h * 0.055)
        gap = int(h * 0.015)
        rects = [
            (base_x, base_y + i * (height + gap), width, height)
            for i in range(count)
        ]
        # Hard clamp: ensure buttons don't extend below context window top
        context_top = self._get_context_window_top(h)
        clamped = []
        for (x, y, w0, h0) in rects:
            max_h = max(0, context_top - y - 2)  # 2px safety
            clamped_h = min(h0, max_h)
            clamped.append((x, y, w0, clamped_h))
        return clamped



    def _get_upgrade_rects(self, w: int, h: int) -> List[Optional[pygame.Rect]]:
        # Filter upgrades based on availability conditions
        available_upgrades = filter_available_upgrades(self.upgrades, self.opponents)
        
        # Display upgrades as icons/buttons on right
        len(available_upgrades)
        # Purchased upgrades shrink to small icon row at top right
        purchased = [(i, u) for i, u in available_upgrades if u.get("purchased", False)]
        not_purchased = [(i, u) for i, u in available_upgrades if not u.get("purchased", False)]
        # Slightly smaller purchased icons to free up vertical space
        icon_w, icon_h = int(w*0.04), int(w*0.04)
        # Purchased: row at top right, but respect UI boundaries
        # Info panel extends to about w*0.84, so ensure icons don't overlap
        max_icons_per_row = max(1, int((w - w*0.84) / icon_w))  # Available space for icons
        
        purchased_rects = []
        for j, (original_idx, upgrade) in enumerate(purchased):
            row = j // max_icons_per_row
            col = j % max_icons_per_row
            x = w - icon_w*(col+1)
            y = int(h*0.08) + row * (icon_h + 5)  # Stack vertically if needed
            purchased_rects.append((x, y, icon_w, icon_h))
        # Not purchased: buttons down right (moved down to accommodate opponents panel)
        base_x = int(w*0.63)
        base_y = int(h*0.28)  # Moved down from 0.18 to 0.28
        # Shrink upgrade buttons a bit to create more breathing room
        btn_w, btn_h = int(w*0.27), int(h*0.07)
        gap = int(h*0.018)
        # Clamp upgrade buttons to avoid overlapping the context window
        context_top = self._get_context_window_top(h)
        not_purchased_rects = []
        for k in range(len(not_purchased)):
            y = base_y + k * (btn_h + gap)
            max_h = max(0, context_top - y - 2)
            not_purchased_rects.append((base_x, y, btn_w, min(btn_h, max_h)))
        # Merge and return in upgrade order (for ALL upgrades, with None for unavailable ones)
        out = [None] * len(self.upgrades)
        for j, (original_idx, upgrade) in enumerate(purchased): 
            rect = purchased_rects[j]
            if validate_rect(rect, f"purchased upgrade {original_idx}"):
                out[original_idx] = rect
            else:
                out[original_idx] = None
        for k, (original_idx, upgrade) in enumerate(not_purchased): 
            rect = not_purchased_rects[k]
            if validate_rect(rect, f"unpurchased upgrade {original_idx}"):
                out[original_idx] = rect
            else:
                out[original_idx] = None
        return out

    def _get_context_window_top(self, h: int) -> int:
        """Compute the y-coordinate of the top of the bottom context window.

        Uses config percentages and minimized state to determine the visible
        context window height and returns the top boundary to clamp UI elements.
        """
        try:
            ctx_cfg = {}
            if hasattr(self, 'config') and self.config:
                ctx_cfg = self.config.get('ui', {}).get('context_window', {})
            expanded = ctx_cfg.get('height_percent', 0.10)
            minimized_p = ctx_cfg.get('minimized_height_percent', 0.05)
            minimized = getattr(self, 'context_window_minimized', False)
            window_h = int(h * (minimized_p if minimized else expanded))
            # draw_context_window uses a 5px bottom margin
            return h - window_h - 5
        except Exception:
            # Safe fallback: assume 10% context window
            return int(h * 0.90) - 5
    
    def _get_upgrade_icon_rect(self, upgrade_idx: int, w: int, h: int) -> Optional[Tuple[int, int, int, int]]:
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

    def _get_endturn_rect(self, w: int, h: int) -> Tuple[int, int, int, int]:
        return get_endturn_rect(w, h)

    def _get_mute_button_rect(self, w: int, h: int) -> Tuple[int, int, int, int]:
        return get_mute_button_rect(w, h)

    def _get_activity_log_minimize_button_rect(self, w: int, h: int) -> Tuple[int, int, int, int]:
        """Get rectangle for the activity log minimize button (only when scrollable log is enabled)"""
        log_x, log_y = self._get_activity_log_current_position(w, h)
        log_width = int(w * 0.44)
        button_size = int(h * 0.025)
        button_x = log_x + log_width - 30
        button_y = log_y
        return (button_x, button_y, button_size, button_size)

    def _get_activity_log_expand_button_rect(self, w: int, h: int) -> Tuple[int, int, int, int]:
        """Get rectangle for the activity log expand button (only when log is minimized)"""
        log_x, log_y = self._get_activity_log_current_position(w, h)
        
        # Estimate title width based on character count (avoiding pygame dependency in tests)
        title_width = len("Activity Log") * int(h*0.015)  # Rough character width estimate
        
        button_size = int(h * 0.025)
        button_x = log_x + title_width + 10
        button_y = log_y
        return (button_x, button_y, button_size, button_size)

    def _get_activity_log_rect(self, w: int, h: int) -> Tuple[int, int, int, int]:
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
            # Full log area - one-third screen width for clean UI
            log_width = int(w * 0.33)
            log_height = int(h * 0.25)
            return (log_x - 5, log_y - 5, log_width + 10, log_height + 10)

    def _get_activity_log_base_position(self, w: int, h: int) -> Tuple[int, int]:
        """Get the base position of activity log (delegates to ui_utils)"""
        from src.core.ui_utils import get_activity_log_base_position
        return get_activity_log_base_position(w, h)

    def _get_activity_log_current_position(self, w: int, h: int) -> Tuple[int, int]:
        """Get the current position of activity log (includes drag offset)"""
        from src.core.ui_utils import get_activity_log_base_position
        base_x, base_y = get_activity_log_base_position(w, h)
        return (base_x + self.activity_log_position[0], base_y + self.activity_log_position[1])

    def _safe_ui_operation(self, operation_name: str, operation_func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Safely execute a UI operation with error handling and logging."""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            if hasattr(self, 'game_logger'):
                self.game_logger.log(f"Error in {operation_name}: {e}, args={args}")
            # Return a safe default value depending on the operation
            if 'hover' in operation_name.lower():
                return None  # For hover operations, return None (no tooltip)
            elif 'click' in operation_name.lower():
                return None  # For click operations, return None (no action taken)
            else:
                return False  # For other operations, return False
    




    def end_turn(self) -> bool:
        """Process end of turn using TurnManager for proper state management."""
        # Use TurnManager if available, otherwise fall back to legacy processing
        if hasattr(self, 'turn_manager'):
            return self.turn_manager.process_turn()
        
        # Legacy turn processing (fallback)
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
        
        # CRITICAL FIX: Process events BEFORE executing actions
        # This ensures players see events before committing to actions
        self.deterministic_event_manager.trigger_events()
        
        # Update economic cycles and display news if phase changed
        if hasattr(self, 'economic_cycles'):
            economic_news = self.economic_cycles.update_for_turn(self.turn + 1)  # Next turn
            if economic_news:
                self.messages.append(f"[NEWS] ECONOMIC NEWS: {economic_news}")
        
        # Check for technical failure cascades
        if hasattr(self, 'technical_failures'):
            self.technical_failures.check_for_cascades()
        
        # Check if there are pending popup events that need resolution
        if (hasattr(self, 'enhanced_events_enabled') and self.enhanced_events_enabled and
            hasattr(self, 'deferred_events') and hasattr(self.deferred_events, 'pending_popup_events') and
            self.deferred_events.pending_popup_events):
            # Events need to be resolved before turn can complete
            # Reset turn processing state and let events be handled
            self.turn_processing = False
            self.turn_processing_timer = 0
            return False
            
        # Fix Too Many Messages Bug: Clear messages from previous turn to prevent accumulation
        # Store previous messages in history if scrollable log is enabled
        if self.scrollable_event_log_enabled and self.messages:
            # Add turn delimiter and store messages from previous turn
            turn_header = f"=== Turn {self.turn} ==="  # Current turn finishing
            self.event_log_history.append(turn_header)
            self.event_log_history.extend(self.messages)
        
        # Always clear messages at start of each turn to prevent accumulation
        # This ensures each turn starts with a clean message slate
        self.messages = []
        
        # Perform all selected actions
        for idx in self.selected_gameplay_actions:
            action = self.gameplay_actions[idx]
            
            # Get delegation info if available
            delegation_info = getattr(self, '_action_delegations', {}).get(idx, {
                'delegated': False,
                'effectiveness': 1.0,
                'ap_cost': action.get("ap_cost", 1)
            })
            
            ap_cost = delegation_info['ap_cost']
            effectiveness = delegation_info['effectiveness']
            
            # NOTE: AP is already deducted during action selection (_handle_action_selection)
            # No need to deduct again here - this was causing double deduction bug
            # Just track for UI glow effects
            self.ap_spent_this_turn = True  # Track for UI glow effects
            self.ap_glow_timer = 30  # 30 frames of glow effect
            
            # Invalidate action availability cache after AP change (Action Point Display Bug fix)
            from src.services.action_availability_manager import get_action_availability_manager
            get_action_availability_manager().invalidate_cache()
            
            # Deduct money cost using _add to track spending
            action_cost = self._get_action_cost(action)
            self._add('money', -action_cost)
            
            # Log the action
            action_name = action["name"]
            if delegation_info['delegated']:
                action_name += " (delegated)"
            self.logger.log_action(action_name, action_cost, self.turn)
            
            # Log to GameRunLogger for analytics
            if hasattr(self, 'run_logger') and self.run_logger:
                self.run_logger.log_action(action_name, action_cost, self.turn)
            
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
        self.selected_gameplay_actions = []
        self.selected_gameplay_action_instances = []  # Clear action instances for next turn
        self.gameplay_action_clicks_this_turn = {}  # Reset click tracking for new turn

        # Staff maintenance - bootstrap AI safety lab economic model
        maintenance_cost = self.economic_config.get_staff_maintenance_cost(self.staff)
        money_before_maintenance = self.money
        self._add('money', -maintenance_cost)  # Use _add to track spending
        
        # Check if we couldn't afford maintenance (money went negative before clamping)
        if money_before_maintenance < maintenance_cost:
            if "comfy_chairs" in self.upgrade_effects and get_rng().random(f"comfy_chairs_help_turn_{self.turn}") < 0.75:
                self.messages.append("Comfy chairs helped staff endure unpaid turn.")
            else:
                lost = get_rng().randint(1, max(1, self.staff // 2), f"staff_leaving_turn_{self.turn}")
                self.staff = max(0, self.staff - lost)
                self.messages.append(f"Could not pay staff! {lost} staff left.")

        # Update employee productivity and compute consumption (weekly cycle)
        self._update_employee_productivity()

        # Check if research threshold reached for paper publication
        if self.research_progress >= 100:
            papers_to_publish = self.research_progress // 100
            self.papers_published += papers_to_publish
            self.research_progress = self.research_progress % 100
            self._add('reputation', papers_to_publish * 5)  # Papers boost reputation
            self.messages.append(f"Research paper{'s' if papers_to_publish > 1 else ''} published! (+{papers_to_publish}, total: {self.papers_published})")
            # Play Zabinga sound for paper completion
            self.sound_manager.play_zabinga_sound()

        # Doom rises over time, faster with more staff
        doom_rise = 2 + self.staff // 5 + (1 if self.doom > 60 else 0)
        
        # Apply researcher effects to doom calculation
        if hasattr(self, 'researchers') and self.researchers:
            researcher_effects = self.get_researcher_productivity_effects()
            
            # Apply doom reduction from safety specialists
            if researcher_effects.get('doom_reduction_bonus', 0) > 0:
                doom_reduction = doom_rise * researcher_effects['doom_reduction_bonus']
                doom_rise = max(0, doom_rise - doom_reduction)
                self.messages.append(f"Safety researchers reduced doom increase by {doom_reduction:.1f}")
            
            # Apply doom increase from capabilities research
            if researcher_effects.get('doom_per_research', 0) > 0 and self.research_progress > 0:
                capabilities_doom = self.research_progress * researcher_effects['doom_per_research']
                doom_rise += capabilities_doom
                if capabilities_doom > 0.5:  # Only show message if significant
                    self.messages.append(f"Capabilities research increased doom risk by {capabilities_doom:.1f}")
        
        # Opponents take their turns and contribute to doom
        opponent_doom = 0
        for opponent in self.opponents:
            messages = opponent.take_turn(self.turn)
            self.messages.extend(messages)
            opponent_doom += opponent.get_impact_on_doom()
            
        # Add opponent doom contribution
        doom_rise += opponent_doom
        self.doom = min(self.max_doom, self.doom + doom_rise)

        # Advance researchers (handle burnout, loyalty, traits)
        if hasattr(self, 'researchers') and self.researchers:
            self.advance_researchers()

        # NOTE: trigger_events() moved to beginning of end_turn() for proper sequencing
        # Events now happen BEFORE action execution so players can respond appropriately
        
        # Check for board member milestone trigger (>$10K spend without accounting software)
        self._check_board_member_milestone()
        
        # Handle deferred events (tick expiration and auto-execute expired ones)
        if hasattr(self, 'deferred_events'):
            self.deferred_events.tick_all_events(self)
        
        self.turn += 1
        
        # Update deterministic RNG with current turn for context-aware seeding
        get_rng().set_turn(self.turn)
        
        # Advance economic systems (Moore's Law compute cost reduction)
        self.economic_config.advance_compute_cost_reduction()
        
        # Advance game clock by one week and display new date
        self.game_clock.tick()
        formatted_date = self.game_clock.get_formatted_date()
        self.messages.append(f"Week of {formatted_date} (Mon)")
        
        # Issue #195: Check for achievements and critical warnings at start of new turn
        process_achievements_and_warnings_complete(self, achievements_endgame_system)
        
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
                    
        # Check staff loss condition only if enabled in config
        if not self.game_over and self.staff == 0:
            config = get_current_config()
            staff_loss_enabled = config.get('resource_limits', {}).get('enable_staff_loss_condition', False)
            
            if staff_loss_enabled:
                self.game_over = True
                game_end_reason = "All staff left"
                self.messages.append("All your staff have left. Game over!")

        self.staff = max(0, self.staff)
        self.reputation = max(0, self.reputation)
        self.money = max(self.money, 0)

        # End game scenarios now handled by TurnManager during turn processing
        # Game logging still handled here for legacy compatibility
        if self.game_over and game_end_reason:
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
                
            # Log to GameRunLogger for analytics
            if hasattr(self, 'run_logger') and self.run_logger:
                self.run_logger.log_game_end(game_end_reason, self.turn, final_resources)

        # Save high score if achieved (legacy system)
        self.save_highscore()
        
        # Save to enhanced leaderboard system
        if hasattr(self, 'leaderboard_manager') and self.leaderboard_manager.current_session:
            try:
                is_high_score, rank, session_data = self.leaderboard_manager.end_game_session(self)
                if is_high_score:
                    self.messages.append(f"New high score! Ranked #{rank} for seed '{self.seed}'")
                else:
                    self.messages.append(f"Game complete! Ranked #{rank} for seed '{self.seed}'")
            except Exception as e:
                self.messages.append(f"Warning: Could not save to leaderboard: {e}")
        
        # Process delayed actions
        self.process_delayed_actions()
        
        # Add daily news feed for turn impact feedback
        daily_news = self.get_daily_news()
        self.messages.append(daily_news)
        
        # Update spend tracking display
        self.update_spend_tracking()
        
        # Check technical debt consequences (accidents, reputation risks, system failures)
        self.check_debt_consequences()
        
        # Reset spend tracking for next turn
        self.spend_this_turn = 0
        
        # Update funding cooldowns
        if hasattr(self, 'funding_round_cooldown') and self.funding_round_cooldown > 0:
            self.funding_round_cooldown -= 1
        
        # Update Public Opinion & Media System
        self.public_opinion.update_turn(self.turn + 1)  # Use next turn for media stories
        new_stories = self.media_system.update_turn(self)
        
        # Report new media stories
        if new_stories:
            for story in new_stories:
                self.messages.append(f"[NEWS] {story.headline}")
        
        # Update UI transitions - animations advance each frame/turn
        self.ui_transition_manager.update_ui_transitions()
        
        # Reset turn processing state immediately to prevent stuck turns
        # This ensures turn processing doesn't get stuck if update_turn_processing() isn't called
        self.turn_processing = False
        self.turn_processing_timer = 0
        
        return True  # Indicate successful turn end
    
    def update_turn_processing(self) -> None:
        """Update turn processing timer and handle transition effects."""
        if self.turn_processing:
            self.turn_processing_timer -= 1
            if self.turn_processing_timer <= 0:
                self.turn_processing = False
                self.turn_processing_timer = 0

    # ========== DETERMINISTIC EVENT SYSTEM DELEGATION ==========
    # All event system functionality delegated to DeterministicEventManager
    
    def trigger_events(self) -> None:
        """Delegate to deterministic event manager."""
        self.deterministic_event_manager.trigger_events()
    
    def handle_popup_event_action(self, event: Event, action: EventAction) -> None:
        """Delegate to deterministic event manager."""
        return self.deterministic_event_manager.handle_popup_event_action(event, action)
    
    def clear_stuck_popup_events(self) -> bool:
        """Delegate to deterministic event manager."""
        return self.deterministic_event_manager.clear_stuck_popup_events()

    def _update_ui_transitions(self) -> None:
        """Delegate to UI transition manager."""
        self.ui_transition_manager.update_ui_transitions()

    def _interpolate_position(self, start_rect: Tuple[int, int, int, int], end_rect: Tuple[int, int, int, int], progress: float, arc_height: int = 80) -> Tuple[int, int]:
        """Delegate to UI transition manager."""
        return self.ui_transition_manager.interpolate_position(start_rect, end_rect, progress, arc_height)

    def _in_rect(self, pt: Tuple[int, int], rect: Union[Tuple[int, int, int, int], pygame.Rect]) -> bool:
        """Check if point is inside rectangle. Simple utility method."""
        if rect is None:
            return False
        try:
            if hasattr(rect, 'collidepoint'):  # pygame.Rect
                return rect.collidepoint(pt)
            else:  # tuple format (x, y, w, h)
                rx, ry, rw, rh = rect
                return rx <= pt[0] <= rx + rw and ry <= pt[1] <= ry + rh
        except (TypeError, ValueError):
            return False

    def _is_upgrade_available(self, upgrade: Dict[str, Any]) -> bool:
        """Check if upgrade should be visible based on unlock conditions."""
        from src.core.utility_functions import is_upgrade_available
        return is_upgrade_available(upgrade, self.opponents)

    # --- High score --- #
    def load_highscore(self) -> int:
        try:
            with open(SCORE_FILE, "r") as f:
                data = json.load(f)
            if self.seed in data:
                # Handle both new format (dict) and legacy format (number)
                if isinstance(data[self.seed], dict):
                    return data[self.seed].get('score', 0)
                else:
                    return data[self.seed]
            # Return the highest score from all records
            max_score = 0
            for value in data.values():
                if isinstance(value, dict):
                    max_score = max(max_score, value.get('score', 0))
                else:
                    max_score = max(max_score, value)
            return max_score
        except Exception:
            return 0

    def save_highscore(self) -> None:
        try:
            if not self.game_over:
                return
            score = self.turn
            if os.path.exists(SCORE_FILE):
                with open(SCORE_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            prev_score = 0
            if self.seed in data:
                if isinstance(data[self.seed], dict):
                    prev_score = data[self.seed].get('score', 0)
                else:
                    # Legacy format - just a number
                    prev_score = data[self.seed]
            
            if score > prev_score:
                # Save both score and lab name for pseudonymous leaderboard
                data[self.seed] = {
                    'score': score,
                    'lab_name': getattr(self, 'lab_name', 'Unknown Labs'),
                    'timestamp': pygame.time.get_ticks()  # For sorting by recency if needed
                }
                with open(SCORE_FILE, "w") as f:
                    json.dump(data, f)
                self.highscore = score
        except Exception:
            pass
    
    # --- Research Quality System (Delegated) --- #
    
    def set_research_quality(self, quality: ResearchQuality) -> None:
        """Set research quality approach - delegated to research system."""
        return self.research_system.set_research_quality(quality)
    
    def create_research_project(self, name: str, base_cost: int, base_duration: int) -> ResearchProject:
        """Create research project - delegated to research system."""
        return self.research_system.create_research_project(name, base_cost, base_duration)
    
    def complete_research_project(self, project: ResearchProject) -> None:
        """Complete research project - delegated to research system."""
        return self.research_system.complete_research_project(project)
    
    def execute_debt_reduction_action(self, action_name: str) -> bool:
        """Execute debt reduction action - delegated to research system."""
        return self.research_system.execute_debt_reduction_action(action_name)
    
    def _execute_debt_reduction_action_original(self, action_name: str) -> bool:
        """
        Execute a technical debt reduction action.
        
        Args:
            action_name: Name of the debt reduction action to execute
            
        Returns:
            True if action was successfully executed, False otherwise
        """
        from src.core.research_quality import get_debt_reduction_actions
        
        debt_actions = get_debt_reduction_actions()
        action = next((a for a in debt_actions if a["name"] == action_name), None)
        
        if not action:
            return False
        
        # Check cost requirements
        if action.get("cost", 0) > self.money:
            self.messages.append(f"? Insufficient funds for {action_name}")
            return False
        
        # Check staff requirements
        if action.get("requires_staff", False):
            staff_type = action.get("staff_type", "research_staff")
            min_staff = action.get("min_staff", 1)
            available_staff = getattr(self, staff_type, 0)
            
            if available_staff < min_staff:
                self.messages.append(f"? Need {min_staff} {staff_type.replace('_', ' ')} for {action_name}")
                return False
        
        # Check action points
        ap_cost = action.get("ap_cost", 1)
        if self.action_points < ap_cost:
            self.messages.append(f"? Need {ap_cost} Action Points for {action_name}")
            return False
        
        # Execute the action
        self.action_points -= ap_cost
        
        if action_name == "Refactoring Sprint":
            cost = self._get_action_cost(action)
            self._add('money', -cost)
            debt_reduction = get_rng().randint(*action["debt_reduction"], "randint_context")
            reduced = self.technical_debt.reduce_debt(debt_reduction)
            self.messages.append(f"? Refactoring sprint completed! Reduced technical debt by {reduced} points")
            
        elif action_name == "Safety Audit":
            cost = self._get_action_cost(action)
            self._add('money', -cost)
            reduced = self.technical_debt.reduce_debt(action["debt_reduction"][0])
            rep_bonus = action.get("reputation_bonus", 0)
            if rep_bonus > 0:
                self._add('reputation', rep_bonus)
            self.messages.append(f"[SHIELD]? Safety audit completed! Reduced debt by {reduced} points, gained reputation")
            
        elif action_name == "Code Review":
            available_researchers = getattr(self, "research_staff", 0)
            cost_per = action["cost_per_researcher"]
            total_cost = cost_per * available_researchers
            
            if self.money < total_cost:
                self.messages.append(f"? Need ${total_cost}k for full code review")
                return False
                
            self._add('money', -total_cost)
            debt_reduction_per = action["debt_reduction_per_researcher"]
            total_reduction = debt_reduction_per * available_researchers
            reduced = self.technical_debt.reduce_debt(total_reduction)
            self.messages.append(f"? Code review with {available_researchers} researchers completed! Reduced debt by {reduced} points")
        
        return True
    
    def execute_technical_debt_audit(self) -> Dict[str, Any]:
        """
        Execute a technical debt audit requiring Administrator staff.
        Reveals exact debt numbers and provides detailed breakdown.
        
        Returns:
            Dict with audit results, or empty dict if audit cannot be performed
        """
        # Check if administrator is available
        if self.admin_staff < 1:
            self.messages.append("? Technical debt audit requires at least 1 Administrator")
            return {}
        
        # Check action points cost
        audit_ap_cost = 2
        if self.action_points < audit_ap_cost:
            self.messages.append(f"? Technical debt audit requires {audit_ap_cost} Action Points")
            return {}
        
        # Perform the audit
        self.action_points -= audit_ap_cost
        
        # Get detailed debt breakdown
        debt_summary = self.technical_debt.get_debt_summary()
        
        # Calculate risk assessment
        speed_penalty = self.technical_debt.get_research_speed_penalty()
        accident_chance = self.technical_debt.get_accident_chance()
        reputation_risk = self.technical_debt.has_reputation_risk()
        system_failure_risk = self.technical_debt.can_trigger_system_failure()
        
        # Determine risk level for UI display
        total_debt = debt_summary["total"]
        if total_debt <= 5:
            risk_level = "Low Risk"
            risk_color = "green"
        elif total_debt <= 15:
            risk_level = "Medium Risk" 
            risk_color = "yellow"
        else:
            risk_level = "High Risk"
            risk_color = "red"
        
        # Generate audit report
        audit_results = {
            "total_debt": total_debt,
            "debt_breakdown": debt_summary,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "speed_penalty_percent": int((1.0 - speed_penalty) * 100),
            "accident_chance_percent": int(accident_chance * 100),
            "reputation_risk": reputation_risk,
            "system_failure_risk": system_failure_risk,
            "recommendations": []
        }
        
        # Add specific recommendations
        if total_debt > 20:
            audit_results["recommendations"].append("CRITICAL: Execute emergency refactoring sprint immediately")
            audit_results["recommendations"].append("Consider halting new development until debt is reduced")
        elif total_debt > 15:
            audit_results["recommendations"].append("HIGH PRIORITY: Schedule comprehensive safety audit")
            audit_results["recommendations"].append("Reduce research pace and focus on quality")
        elif total_debt > 10:
            audit_results["recommendations"].append("MODERATE: Plan refactoring sprint within 3 turns")
            audit_results["recommendations"].append("Monitor for system failures")
        elif total_debt > 5:
            audit_results["recommendations"].append("LOW: Consider code review sessions")
            audit_results["recommendations"].append("Maintain current quality standards")
        else:
            audit_results["recommendations"].append("EXCELLENT: Technical debt well-managed")
            audit_results["recommendations"].append("Current practices are sustainable")
        
        # Add per-category analysis
        category_analysis = []
        for category, debt in debt_summary.items():
            if category != "total" and debt > 0:
                category_analysis.append(f"{category.replace('_', ' ').title()}: {debt} points")
        
        if category_analysis:
            audit_results["category_breakdown"] = category_analysis
        
        # Log the audit
        self.messages.append(f"[CHART] Technical Debt Audit completed by Administrator")
        self.messages.append(f"[TARGET] Risk Assessment: {risk_level} ({total_debt} total debt points)")
        
        if audit_results["recommendations"]:
            self.messages.append(f"[LIST] Top Recommendation: {audit_results['recommendations'][0]}")
        
        # Store audit results for UI display
        if not hasattr(self, 'last_audit_results'):
            self.last_audit_results = {}
        self.last_audit_results = audit_results
        
        return audit_results
    
    def get_debt_risk_indicator(self) -> str:
        """
        Get simplified debt risk indicator for UI without requiring audit.
        Returns 'Low Risk', 'Medium Risk', or 'High Risk'.
        """
        total_debt = self.technical_debt.accumulated_debt
        
        if total_debt <= 5:
            return "Low Risk"
        elif total_debt <= 15:
            return "Medium Risk"
        else:
            return "High Risk"
    
    def get_research_effectiveness_modifier(self) -> float:
        """
        Get the current research effectiveness modifier based on technical debt.
        
        Returns:
            Multiplier for research effectiveness (0.85 = 15% penalty)
        """
        return self.technical_debt.get_research_speed_penalty()
    
    def check_debt_consequences(self) -> None:
        """
        Check and apply consequences of accumulated technical debt.
        Called during end_turn processing.
        """
        self.technical_debt.accumulated_debt
        
        # Check for accident events
        accident_chance = self.technical_debt.get_accident_chance()
        if accident_chance > 0 and get_rng().random("random_context") < accident_chance:
            self._trigger_debt_accident()
        
        # Check for reputation risks
        if self.technical_debt.has_reputation_risk() and get_rng().random("random_context") < 0.1:
            rep_loss = get_rng().randint(1, 3, "randint_context")
            self._add('reputation', -rep_loss)
            self.messages.append(f"[NEWS] Technical debt issues exposed in media! Lost {rep_loss} reputation")
        
        # Check for system failure events
        if self.technical_debt.can_trigger_system_failure() and get_rng().random("random_context") < 0.05:
            self._trigger_system_failure()
    
    # Researcher Assignment System for Issue #190
    def assign_researcher_to_task(self, researcher_id: str, task_name: str, 
                                  quality_override: Optional[ResearchQuality] = None) -> bool:
        """
        Assign a specific researcher to a specific task.
        
        Args:
            researcher_id: Unique identifier for the researcher
            task_name: Name of the research task/action
            quality_override: Optional quality level override for this task
            
        Returns:
            True if assignment was successful, False otherwise
        """
        # Find the researcher
        researcher = self.get_researcher_by_id(researcher_id)
        if not researcher:
            self.messages.append(f"? Researcher {researcher_id} not found")
            return False
        
        # Check if researcher is already assigned
        if researcher_id in self.researcher_assignments:
            old_task = self.researcher_assignments[researcher_id]
            self.messages.append(f"[LIST] {researcher.name} reassigned from {old_task} to {task_name}")
        
        # Make the assignment
        self.researcher_assignments[researcher_id] = task_name
        
        # Set quality override if provided
        if quality_override:
            self.task_quality_overrides[task_name] = quality_override
        
        self.messages.append(f"? {researcher.name} assigned to {task_name}")
        return True
    
    def unassign_researcher(self, researcher_id: str) -> bool:
        """
        Remove assignment for a specific researcher.
        
        Args:
            researcher_id: Unique identifier for the researcher
            
        Returns:
            True if unassignment was successful, False otherwise
        """
        researcher = self.get_researcher_by_id(researcher_id)
        if not researcher:
            return False
        
        if researcher_id in self.researcher_assignments:
            task_name = self.researcher_assignments[researcher_id]
            del self.researcher_assignments[researcher_id]
            self.messages.append(f"[LIST] {researcher.name} unassigned from {task_name}")
            return True
        
        return False
    
    def set_researcher_default_quality(self, researcher_id: str, quality: ResearchQuality) -> bool:
        """
        Set the default research quality preference for a researcher.
        
        Args:
            researcher_id: Unique identifier for the researcher
            quality: Default quality level for this researcher
            
        Returns:
            True if setting was successful, False otherwise
        """
        researcher = self.get_researcher_by_id(researcher_id)
        if not researcher:
            return False
        
        self.researcher_default_quality[researcher_id] = quality
        quality_name = quality.value.title()
        self.messages.append(f"?? {researcher.name}'s default quality set to {quality_name}")
        return True
    
    def get_researcher_by_id(self, researcher_id: str) -> Optional[Any]:
        """
        Get a researcher by their unique identifier.
        
        Args:
            researcher_id: Unique identifier for the researcher
            
        Returns:
            Researcher object if found, None otherwise
        """
        for researcher in self.researchers:
            if getattr(researcher, 'id', researcher.name) == researcher_id:
                return researcher
        return None
    
    def get_task_quality_setting(self, task_name: str, assigned_researcher_id: str = None) -> ResearchQuality:
        """
        Get the effective quality setting for a task.
        
        Args:
            task_name: Name of the research task
            assigned_researcher_id: ID of researcher assigned to this task
            
        Returns:
            Effective ResearchQuality level for the task
        """
        # Check task-specific override first
        if task_name in self.task_quality_overrides:
            return self.task_quality_overrides[task_name]
        
        # Check researcher default if researcher is assigned
        if assigned_researcher_id and assigned_researcher_id in self.researcher_default_quality:
            return self.researcher_default_quality[assigned_researcher_id]
        
        # Fall back to organization default
        return self.current_research_quality
    
    def get_researcher_assignments_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current researcher assignments for UI display.
        
        Returns:
            Dictionary with assignment information
        """
        summary = {
            "assigned": {},
            "unassigned": [],
            "task_qualities": {}
        }
        
        # Track assigned researchers
        for researcher_id, task_name in self.researcher_assignments.items():
            researcher = self.get_researcher_by_id(researcher_id)
            if researcher:
                summary["assigned"][researcher_id] = {
                    "name": researcher.name,
                    "task": task_name,
                    "specialization": researcher.specialization,
                    "quality_setting": self.get_task_quality_setting(task_name, researcher_id).value
                }
        
        # Track unassigned researchers
        assigned_ids = set(self.researcher_assignments.keys())
        for researcher in self.researchers:
            researcher_id = getattr(researcher, 'id', researcher.name)
            if researcher_id not in assigned_ids:
                summary["unassigned"].append({
                    "id": researcher_id,
                    "name": researcher.name,
                    "specialization": researcher.specialization,
                    "default_quality": self.researcher_default_quality.get(researcher_id, self.current_research_quality).value
                })
        
        return summary
    
    def _trigger_debt_accident(self) -> None:
        """Trigger a technical debt-related accident."""
        accident_types = [
            ("Research setback due to buggy code", lambda: self._add('research_progress', -get_rng().randint(5, 15, "randint_context"))),
            ("Security breach from poor validation", lambda: self._add('reputation', -get_rng().randint(2, 4, "randint_context"))),
            ("Compute system crash from technical debt", lambda: self._add('compute', -get_rng().randint(5, 10, "randint_context"))),
        ]
        
        accident_name, accident_effect = get_rng().choice(accident_types, "choice_context")
        accident_effect()
        self.messages.append(f"[EXPLOSION] ACCIDENT: {accident_name}")
    
    def _trigger_system_failure(self) -> None:
        """Trigger a major system failure due to excessive technical debt."""
        failure_types = [
            ("Critical system failure! Major research setback", 
             lambda: (self._add('research_progress', -get_rng().randint(20, 40, "randint_context")),
                     self._add('reputation', -get_rng().randint(3, 6, "randint_context")))),
            ("Catastrophic infrastructure collapse! Financial and reputation damage",
             lambda: (self._add('money', -get_rng().randint(50, 100, "randint_context")),
                     self._add('reputation', -get_rng().randint(4, 8, "randint_context")))),
            ("Major safety incident due to accumulated shortcuts!",
             lambda: (self._add('doom', get_rng().randint(10, 20, "randint_context"), "technical debt cascade failure"),
                     self._add('reputation', -get_rng().randint(5, 10, "randint_context")))),
        ]
        
        failure_name, failure_effect = get_rng().choice(failure_types, "choice_context")
        failure_effect()
        self.messages.append(f"[ALERT] SYSTEM FAILURE: {failure_name}")
        
        # Reduce some technical debt after a major failure (lessons learned)
        reduced = self.technical_debt.reduce_debt(get_rng().randint(3, 7, "randint_context"))
        self.messages.append(f"Lessons learned from failure. Technical debt reduced by {reduced} points.")
    
    def get_debt_summary_for_ui(self) -> Dict[str, int]:
        """
        Get technical debt summary for UI display.
        
        Returns:
            Dictionary with debt information for UI rendering
        """
        summary = self.technical_debt.get_debt_summary()
        summary["research_penalty"] = int((1.0 - self.get_research_effectiveness_modifier()) * 100)
        summary["accident_chance"] = int(self.technical_debt.get_accident_chance() * 100)
        summary["has_reputation_risk"] = self.technical_debt.has_reputation_risk()
        summary["can_system_failure"] = self.technical_debt.can_trigger_system_failure()
        return summary

    # --- Tutorial settings --- #
    TUTORIAL_SETTINGS_FILE = "tutorial_settings.json"
    
    def load_tutorial_settings(self) -> None:
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

    def save_tutorial_settings(self) -> None:
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
    
    def show_tutorial_message(self, milestone_id: str, title: str, content: str) -> None:
        """Queue a tutorial message to be shown."""
        if self.tutorial_enabled and milestone_id not in self.tutorial_shown_milestones:
            self.pending_tutorial_message = {
                "milestone_id": milestone_id,
                "title": title,
                "content": content
            }
    
    def get_employee_productive_actions(self, employee_id: int) -> Optional[Dict[str, Any]]:
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
    
    def set_employee_productive_action(self, employee_id: int, action_index: int) -> Tuple[bool, str]:
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
    
    def get_all_employee_productive_actions_summary(self) -> List[Dict[str, Any]]:
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

    def dismiss_tutorial_message(self) -> None:
        """Dismiss the current tutorial message and mark milestone as shown."""
        if self.pending_tutorial_message:
            milestone_id = self.pending_tutorial_message["milestone_id"]
            self.tutorial_shown_milestones.add(milestone_id)
            self.pending_tutorial_message = None
            self.save_tutorial_settings()
    
    def _hire_employee_subtype(self, subtype_id: str) -> None:
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
    
    def _scout_opponents(self) -> None:
        """Scout competing labs - delegated to intelligence system manager."""
        return self.intelligence_system.scout_opponents()
    
    def _trigger_intelligence_dialog(self) -> None:
        """Trigger intelligence dialog - delegated to intelligence system manager."""
        return self.intelligence_system.trigger_intelligence_dialog()
    
    def select_intelligence_option(self, option_id: str) -> Tuple[bool, str]:
        """Handle intelligence option selection - delegated to intelligence system manager."""
        return self.intelligence_system.select_intelligence_option(option_id)
    
    def _trigger_media_dialog(self) -> None:
        """Trigger media dialog - delegated to media PR system manager."""
        return self.media_pr_system.trigger_media_dialog()
    
    def select_media_option(self, option_id: str) -> Tuple[bool, str]:
        """Handle media option selection - delegated to media PR system manager."""
        return self.media_pr_system.select_media_option(option_id)

    def _trigger_technical_debt_dialog(self) -> None:
        """Trigger the technical debt dialog with available debt management options."""
        debt_options = []
        
        # Check current technical debt level
        current_debt = getattr(self.technical_debt, 'accumulated_debt', 0) if hasattr(self, 'technical_debt') else 0
        
        # Refactoring Sprint
        debt_options.append({
            "id": "refactoring_sprint",
            "name": "Refactoring Sprint",
            "description": "Intensive code refactoring to reduce technical debt and improve maintainability.", 
            "cost": self.economic_config.get_technical_debt_cost('refactoring_sprint') if hasattr(self, 'economic_config') else 250,
            "ap_cost": 2,
            "available": current_debt >= 5,  # Need significant debt to justify
            "details": f"Requires 5+ debt (current: {current_debt}). Major debt reduction effort."
        })
        
        # Technical Debt Audit (Safety Audit)
        debt_options.append({
            "id": "technical_debt_audit",
            "name": "Technical Debt Audit",
            "description": "External safety audit to identify and assess technical debt risks.",
            "cost": self.economic_config.get_technical_debt_cost('safety_audit_external') if hasattr(self, 'economic_config') else 400,
            "ap_cost": 1,
            "available": current_debt >= 3,  # Need some debt to audit
            "details": f"Requires 3+ debt (current: {current_debt}). Professional assessment of risks."
        })
        
        # Code Review
        debt_options.append({
            "id": "code_review", 
            "name": "Code Review",
            "description": "Systematic peer code review to prevent technical debt accumulation.",
            "cost": 80,
            "ap_cost": 1,
            "available": self.research_staff >= 1 and current_debt >= 1,
            "details": f"Requires 1+ research staff and 1+ debt. Staff: {self.research_staff}, Debt: {current_debt}"
        })
        
        self.pending_technical_debt_dialog = {
            "options": debt_options,
            "title": "Technical Debt Management",
            "description": "Select a technical debt management operation to execute."
        }
    
    def select_technical_debt_option(self, option_id: str) -> Tuple[bool, str]:
        """Handle player selection of a technical debt option."""
        if not self.pending_technical_debt_dialog:
            return False, "No technical debt dialog active."
        
        # Find the selected option
        selected_option = None
        for option in self.pending_technical_debt_dialog["options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Invalid technical debt option: {option_id}"
        
        if not selected_option["available"]:
            return False, f"Technical debt option not available: {selected_option['name']}"
        
        # Check costs
        if self.money < selected_option["cost"]:
            return False, f"Insufficient funds. Need ${selected_option['cost']}, have ${self.money}."
        
        if self.action_points < selected_option["ap_cost"]:
            return False, f"Insufficient action points. Need {selected_option['ap_cost']}, have {self.action_points}."
        
        # Execute the selected technical debt option
        if option_id == "refactoring_sprint":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute refactoring sprint functionality
            self.execute_debt_reduction_action("Refactoring Sprint")
            
        elif option_id == "technical_debt_audit":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute technical debt audit functionality
            self.execute_debt_reduction_action("Safety Audit")
            
        elif option_id == "code_review":
            # Deduct costs
            self.money -= selected_option["cost"] 
            self.action_points -= selected_option["ap_cost"]
            
            # Execute code review functionality
            self.execute_debt_reduction_action("Code Review")
            
        else:
            return False, f"Unknown technical debt option: {option_id}"
        
        # Clear the technical debt dialog
        self.pending_technical_debt_dialog = None
        return True, "Technical debt management operation complete."

    def _trigger_advanced_funding_dialog(self) -> None:
        """Trigger the advanced funding dialog with available funding options."""
        funding_options = []
        
        # Series A Funding
        funding_options.append({
            "id": "series_a_funding",
            "name": "Series A Funding",
            "description": "Pursue institutional venture capital funding for large-scale growth.",
            "cost": 0,
            "ap_cost": 2,  # More complex than basic fundraising
            "available": self.reputation >= 15,
            "details": f"Requires 15+ reputation (current: {self.reputation}). High-impact institutional funding."
        })
        
        # Government Grant Application
        funding_options.append({
            "id": "government_grant",
            "name": "Government Grant Application",
            "description": "Apply for government AI safety research grants with counter-cyclical funding.",
            "cost": 10,  # Application costs
            "ap_cost": 1,
            "available": self.reputation >= 8,
            "details": f"Requires 8+ reputation (current: {self.reputation}). Stable government funding source."
        })
        
        # Corporate Partnership
        funding_options.append({
            "id": "corporate_partnership",
            "name": "Corporate Partnership",
            "description": "Form strategic partnership with established corporation for funding and resources.",
            "cost": 0,
            "ap_cost": 2,
            "available": self.reputation >= 12,
            "details": f"Requires 12+ reputation (current: {self.reputation}). Strategic business alliance."
        })
        
        # Revenue Diversification
        funding_options.append({
            "id": "revenue_diversification",
            "name": "Revenue Diversification",
            "description": "Develop alternative revenue streams through consulting and licensing.",
            "cost": 0,
            "ap_cost": 1,
            "available": self.reputation >= 10 and self.staff >= 5,
            "details": f"Requires 10+ reputation and 5+ staff. Current: {self.reputation} reputation, {self.staff} staff."
        })
        
        self.pending_advanced_funding_dialog = {
            "options": funding_options,
            "title": "Advanced Funding Options",
            "description": "Select an advanced funding strategy to execute."
        }
    
    def select_advanced_funding_option(self, option_id: str) -> Tuple[bool, str]:
        """Handle player selection of an advanced funding option."""
        if not self.pending_advanced_funding_dialog:
            return False, "No advanced funding dialog active."
        
        # Find the selected option
        selected_option = None
        for option in self.pending_advanced_funding_dialog["options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Invalid advanced funding option: {option_id}"
        
        if not selected_option["available"]:
            return False, f"Advanced funding option not available: {selected_option['name']}"
        
        # Check costs
        if self.money < selected_option["cost"]:
            return False, f"Insufficient funds. Need ${selected_option['cost']}, have ${self.money}."
        
        if self.action_points < selected_option["ap_cost"]:
            return False, f"Insufficient action points. Need {selected_option['ap_cost']}, have {self.action_points}."
        
        # Import funding functions
        from src.core.actions import (
            execute_series_a_funding,
            execute_government_grant_application,
            execute_corporate_partnership,
            execute_revenue_diversification
        )
        from src.services.rng_service import get_rng
        
        # Execute the selected advanced funding option
        if option_id == "series_a_funding":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute series A funding functionality
            execute_series_a_funding(self)
            # Apply potential reputation risk
            if get_rng().random("random_context") < 0.4:
                self._add('reputation', -1)
            
        elif option_id == "government_grant":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute government grant functionality
            execute_government_grant_application(self)
            
        elif option_id == "corporate_partnership":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute corporate partnership functionality
            execute_corporate_partnership(self)
            # Apply potential reputation risk
            if get_rng().random("random_context") < 0.3:
                self._add('reputation', -2)
            
        elif option_id == "revenue_diversification":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute revenue diversification functionality
            execute_revenue_diversification(self)
            
        else:
            return False, f"Unknown advanced funding option: {option_id}"
        
        # Clear the advanced funding dialog
        self.pending_advanced_funding_dialog = None
        return True, "Advanced funding operation complete."

    def _trigger_infrastructure_dialog(self) -> None:
        """Trigger the infrastructure dialog with available system upgrade options."""
        infrastructure_options = []
        
        # Check technical failures system availability
        has_tech_failures = hasattr(self, 'technical_failures')
        
        # Incident Response Training
        current_incident_level = getattr(self.technical_failures, 'incident_response_level', 0) if has_tech_failures else 0
        incident_cost = (current_incident_level + 1) * 30 if has_tech_failures else 30
        
        # Demo hotfix: Add Buy Compute to Infrastructure menu
        compute_cost = self.economic_config.get_compute_cost(10) if hasattr(self, 'economic_config') else 50
        infrastructure_options.append({
            "id": "buy_compute",
            "name": "Buy Compute",
            "description": "Purchase compute resources. Cost decreases over time (Moore's Law).",
            "cost": compute_cost,
            "ap_cost": 1,
            "available": True,
            "details": f"Adds 10 compute units. Current: {self.compute}"
        })
        
        infrastructure_options.append({
            "id": "incident_response_training",
            "name": "Incident Response Training",
            "description": "Upgrade incident response capabilities to prevent failure cascades and improve crisis management.",
            "cost": incident_cost,
            "ap_cost": 1,
            "available": (current_incident_level < 5) if has_tech_failures else True,
            "details": f"Current level: {current_incident_level}/5. Systematic emergency response preparation."
        })
        
        # Monitoring Systems
        current_monitoring = getattr(self.technical_failures, 'monitoring_systems', 0) if has_tech_failures else 0
        monitoring_cost = (current_monitoring + 1) * 40 if has_tech_failures else 40
        
        infrastructure_options.append({
            "id": "monitoring_systems",
            "name": "Monitoring Systems",
            "description": "Deploy advanced monitoring systems for early failure detection and system health tracking.",
            "cost": monitoring_cost,
            "ap_cost": 1,
            "available": (current_monitoring < 5) if has_tech_failures else True,
            "details": f"Current level: {current_monitoring}/5. Proactive system surveillance and alerting."
        })
        
        # Communication Protocols
        current_protocols = getattr(self.technical_failures, 'communication_protocols', 0) if has_tech_failures else 0
        protocols_cost = (current_protocols + 1) * 25 if has_tech_failures else 25
        
        infrastructure_options.append({
            "id": "communication_protocols",
            "name": "Communication Protocols",
            "description": "Standardize crisis communication and coordination procedures for effective team response.",
            "cost": protocols_cost,
            "ap_cost": 1,
            "available": (current_protocols < 5) if has_tech_failures else True,
            "details": f"Current level: {current_protocols}/5. Clear crisis communication frameworks."
        })
        
        self.pending_infrastructure_dialog = {
            "options": infrastructure_options,
            "title": "Infrastructure Systems",
            "description": "Select an infrastructure upgrade to implement."
        }
    
    def select_infrastructure_option(self, option_id: str) -> Tuple[bool, str]:
        """Handle player selection of an infrastructure option."""
        if not self.pending_infrastructure_dialog:
            return False, "No infrastructure dialog active."
        
        # Find the selected option
        selected_option = None
        for option in self.pending_infrastructure_dialog["options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Invalid infrastructure option: {option_id}"
        
        if not selected_option["available"]:
            return False, f"Infrastructure option not available: {selected_option['name']}"
        
        # Check costs
        if self.money < selected_option["cost"]:
            return False, f"Insufficient funds. Need ${selected_option['cost']}, have ${self.money}."
        
        if self.action_points < selected_option["ap_cost"]:
            return False, f"Insufficient action points. Need {selected_option['ap_cost']}, have {self.action_points}."
        
        # Import infrastructure functions
        from src.core.actions import (
            execute_incident_response_upgrade,
            execute_monitoring_systems_upgrade,
            execute_communication_protocols_upgrade
        )
        
        # Execute the selected infrastructure option
        if option_id == "buy_compute":
            # Demo hotfix: Handle buy compute in infrastructure dialog
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            self._add('compute', 10)
            self.pending_infrastructure_dialog = None
            return True, f"Purchased 10 compute units for ${selected_option['cost']}."
            
        elif option_id == "incident_response_training":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute incident response upgrade functionality
            execute_incident_response_upgrade(self)
            
        elif option_id == "monitoring_systems":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute monitoring systems upgrade functionality
            execute_monitoring_systems_upgrade(self)
            
        elif option_id == "communication_protocols":
            # Deduct costs
            self.money -= selected_option["cost"]
            self.action_points -= selected_option["ap_cost"]
            
            # Execute communication protocols upgrade functionality
            execute_communication_protocols_upgrade(self)
            
        else:
            return False, f"Unknown infrastructure option: {option_id}"
        
        # Clear the infrastructure dialog
        self.pending_infrastructure_dialog = None
        return True, "Infrastructure upgrade complete."

    def _trigger_competitor_discovery(self) -> None:
        """Trigger discovery of a new competitor through intelligence."""
        undiscovered_opponents = [opp for opp in self.opponents if not opp.discovered]
        
        if undiscovered_opponents:
            new_opponent = get_rng().choice(undiscovered_opponents, "choice_context")
            new_opponent.discover()
            self.messages.append(f"INTELLIGENCE ALERT: New competitor detected - {new_opponent.name}")
            self.messages.append(f"? {new_opponent.description}")
            self.messages.append("Use 'Intelligence' action to gather more intelligence on their capabilities.")
        else:
            self.messages.append("Intelligence reports suggest all major competitors are now known.")
    
    def _provide_competitor_update(self) -> None:
        """Provide an intelligence update on known competitors."""
        discovered_opponents = [opp for opp in self.opponents if opp.discovered]
        
        if discovered_opponents:
            target = get_rng().choice(discovered_opponents, f"competitor_update_target_turn_{self.turn}")
            
            # Generate a random intelligence snippet
            snippets = [
                f"{target.name} has been recruiting aggressively this quarter.",
                f"Sources report {target.name} secured additional funding recently.", 
                f"{target.name} was spotted at a major AI conference last week.",
                f"Technical staff departures reported at {target.name}.",
                f"{target.name} has increased their compute infrastructure.",
                f"Regulatory filings suggest {target.name} is preparing for new announcements."
            ]
            
            selected_snippet = get_rng().choice(snippets, "choice_context")
            self.messages.append(f"INTELLIGENCE UPDATE: {selected_snippet}")
            self.messages.append("Consider using 'Scout Opponents' for detailed intelligence gathering.")
    
    def _trigger_expense_request(self) -> None:
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
        expense = get_rng().choice(expense_types, "choice_context")
        
        # Create the popup event
        event_name = f"Expense Request: {expense['item']}"
        event_desc = (f"{expense['employee']} requests approval for: {expense['item']} (${expense['cost']})\n\n"
                     f"Purpose: {expense['description']}\n\n"
                     f"Accept the expense or deny the request?")
        
        def approve_expense(gs: 'GameState') -> str:
            if gs.money >= expense['cost']:
                expense['approve_effect'](gs)
                gs.messages.append(f"Accepted: {expense['item']} (${expense['cost']})")
                return f"Expense accepted. {expense['employee']} appreciates the investment."
            else:
                gs.messages.append(f"Insufficient funds to accept {expense['item']} (need ${expense['cost']}, have ${gs.money})")
                return "Insufficient funds for acceptance."
        
        def deny_expense(gs: 'GameState') -> str:
            expense['deny_effect'](gs)
            gs.messages.append(f"Denied: {expense['item']}")
            return f"Expense request denied. {expense['employee']} understands the budget constraints."
        
        # Create event with accept/deny options
        popup_event = Event(
            name=event_name,
            desc=event_desc,
            trigger=lambda gs: True,  # Already triggered
            effect=approve_expense,   # Default effect is approval
            event_type=EventType.POPUP,
            available_actions=[EventAction.ACCEPT, EventAction.DENY],
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
    
    def _trigger_stray_cat_adoption(self) -> None:
        """Handle the stray cat adoption event - Enhanced interactive office cat system for dev engagement."""
        # Mark that the event has occurred so it doesn't repeat
        self.office_cats_adopted = True
        self.office_cat_adopted = True  # Enable full interactive system
        self.office_cat_adoption_offered = True
        
        # Set initial cat position in a nice corner
        self.office_cat_position = (350, 280)
        self.office_cat_target_position = (350, 280)
        
        # Responsible pet ownership costs
        flea_treatment_cost = 50
        self._add('money', -flea_treatment_cost)
        
        # Positive effects: small morale boost through reputation gain
        reputation_boost = 2
        self.reputation += reputation_boost  # Direct assignment to avoid verbose messaging for cat adoption
        
        # Fun message for the player with interaction hints
        self.messages.append("[CAT] SPECIAL EVENT: A box of adorable kittens was left outside your office!")
        self.messages.append("Your staff has unanimously decided to adopt them as official office cats.")
        self.messages.append(f"Responsible pet ownership: Flea treatment purchased for ${flea_treatment_cost}")
        self.messages.append(f"The office atmosphere has improved significantly! +{reputation_boost} reputation")
        self.messages.append("[IDEA] TIP: Click on the office cat to pet them for morale boosts!")
        self.messages.append("The cats seem particularly interested in the server room...")
    
    def _trigger_hiring_dialog(self) -> None:
        """Trigger the employee hiring dialog with available employee subtypes."""
        from src.core.employee_subtypes import get_available_subtypes, get_hiring_complexity_level
        from src.features.onboarding import onboarding
        from src.services.config_manager import get_current_config
        
        # Check if this is the first time attempting to hire staff and hints are enabled
        config = get_current_config()
        starting_staff = config.get('starting_resources', {}).get('staff', 2)
        
        # Only show hint if:
        # 1. This is the first manual hire attempt (still at starting staff count)
        # 2. Hints haven't been seen before (Factorio-style)
        if (self.staff == starting_staff and 
            onboarding.should_show_hint('first_staff_hire')):
            # Store the mechanic to show help later in main loop 
            self._pending_first_time_help = 'first_staff_hire'
        
        # Get available employee subtypes based on current game state
        available_subtypes = get_available_subtypes(self)
        complexity_level = get_hiring_complexity_level(self)
        
        if not available_subtypes:
            self.messages.append("No employees available for hiring at this time.")
            return
        
        # Set up the hiring dialog state using dialog manager
        self.pending_hiring_dialog = DialogManager.create_hiring_dialog_state(available_subtypes, complexity_level)
    
    def select_employee_subtype(self, subtype_id: str) -> Tuple[bool, str]:
        """Handle player selection of an employee subtype."""
        if not self.pending_hiring_dialog:
            return False, "No hiring dialog active."
        
        # Special case: specialist researcher opens researcher pool
        if subtype_id == "specialist_researcher":
            # Ensure researcher pool is available
            if not hasattr(self, 'available_researchers') or not self.available_researchers:
                # Auto-refresh if empty
                self.refresh_researcher_hiring_pool()
            
            # Switch to researcher hiring mode
            self.pending_hiring_dialog["mode"] = "researcher_pool"
            self.pending_hiring_dialog["selected_subtype"] = subtype_id
            return True, "Showing available specialist researchers."
        
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
    
    def select_researcher_from_pool(self, researcher_index: int) -> Tuple[bool, str]:
        """Handle player selection of a researcher from the hiring pool."""
        if not self.pending_hiring_dialog or self.pending_hiring_dialog.get("mode") != "researcher_pool":
            return False, "No researcher pool dialog active."
        
        # Hire the selected researcher
        success, message = self.hire_researcher(researcher_index)
        
        if success:
            # Clear the hiring dialog
            self.pending_hiring_dialog = None
            return True, message
        else:
            return False, message
    
    def dismiss_hiring_dialog(self) -> None:
        """Dismiss the hiring dialog without making a selection."""
        from .dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self, 'hiring')
    
    def dismiss_intelligence_dialog(self) -> None:
        """Dismiss the intelligence dialog without making a selection."""
        from .dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self, 'intelligence')

    def dismiss_media_dialog(self) -> None:
        """Dismiss the media dialog without making a selection."""
        from .dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self, 'media')

    def dismiss_technical_debt_dialog(self) -> None:
        """Dismiss the technical debt dialog without making a selection."""
        from .dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self, 'technical_debt')
    
    def _create_upgrade_transition(self, upgrade_idx: int, start_rect: pygame.Rect, end_rect: pygame.Rect) -> Dict[str, Any]:
        """Create a smooth transition animation for an upgrade moving from button to icon."""
        return self.ui_transition_manager.create_upgrade_transition(upgrade_idx, start_rect, end_rect)
    

    
    # UI Transition methods now handled by UITransitionManager
    
    def track_error(self, error_message: str) -> bool:
        """
        Track an error for the easter egg beep system.
        
        Args:
            error_message: The error message that occurred
            
        Returns:
            bool: True if this triggers the easter egg (3 repeated identical errors)
        """
        return self.error_tracker.track_error(error_message)
    
    def log_ui_interaction(self, interaction_type: str, element_id: str, details: Optional[Dict[str, Any]] = None) -> None:
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
        if action_index >= len(self.gameplay_actions):
            return False, "Invalid action"
            
        action = self.gameplay_actions[action_index]
        
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
    
    # Enhanced Personnel System Methods
    
    def refresh_researcher_hiring_pool(self) -> None:
        """Refresh the pool of available researchers for hiring."""
        from src.core.researchers import generate_researcher, SPECIALIZATIONS
        
        # Clear current pool
        self.available_researchers = []
        
        # Generate 3-5 new researchers with varied specializations
        num_researchers = get_rng().randint(3, 5, "randint_context")
        specializations = list(SPECIALIZATIONS.keys())
        
        for _ in range(num_researchers):
            # Ensure variety in specializations
            specialization = get_rng().choice(specializations, "choice_context")
            researcher = generate_researcher(specialization)
            self.available_researchers.append(researcher)
        
        self.researcher_hiring_pool_refreshed = True
        self.messages.append(f"New researcher applications received: {num_researchers} candidates available for hiring.")
    
    def hire_researcher(self, researcher_index: int) -> Tuple[bool, str]:
        """Hire a researcher from the available pool."""
        if researcher_index >= len(self.available_researchers):
            return False, "Invalid researcher selection."
        
        researcher = self.available_researchers[researcher_index]
        cost = researcher.salary_expectation
        
        # Check if can afford
        if self.money < cost:
            return False, f"Cannot afford {researcher.name}'s salary of ${cost}. Have ${self.money}."
        
        if self.action_points < 2:  # Hiring costs 2 AP
            return False, "Need 2 action points to hire researcher."
        
        # Hire the researcher
        self._add('money', -cost)
        self.action_points -= 2  # Direct action point deduction
        self._add('staff', 1)
        self._add('research_staff', 1)
        
        # Add to researchers list
        self.researchers.append(researcher)
        
        # Remove from available pool
        self.available_researchers.pop(researcher_index)
        
        # Configure the employee blob created by _add('staff', 1) above
        if self.employee_blobs:
            # Set the newest blob as specialist researcher
            newest_blob = self.employee_blobs[-1]
            newest_blob['subtype'] = 'specialist_researcher'
            newest_blob['researcher_id'] = len(self.researchers) - 1  # Index of researcher
            newest_blob['productive_action_index'] = 0  # Default action
        
        specialization_name = researcher.specialization.replace('_', ' ').title()
        traits_str = ', '.join(researcher.traits) if researcher.traits else 'None'
        
        message = (f"Hired {researcher.name}! Specialization: {specialization_name}, "
                  f"Skill: {researcher.skill_level}/10, Traits: {traits_str}")
        
        return True, message
    
    def get_researcher_productivity_effects(self) -> Dict[str, float]:
        """Calculate total productivity effects from all researchers."""
        effects = {
            'research_speed_modifier': 1.0,
            'doom_reduction_bonus': 0.0,
            'doom_per_research': 0.0,
            'negative_event_reduction': 0.0,
            'team_productivity_bonus': 0.0,
            'reputation_bonus': 0
        }
        
        # Check for team player bonus
        has_team_player = any('team_player' in r.traits for r in self.researchers)
        
        for researcher in self.researchers:
            researcher_effects = researcher.get_specialization_effects()
            productivity = researcher.get_effective_productivity()
            
            # Apply specialization effects scaled by productivity
            for effect_type, value in researcher_effects.items():
                if effect_type == 'research_speed_modifier':
                    # Multiplicative bonus
                    speed_bonus = (value - 1.0) * productivity
                    effects[effect_type] *= (1.0 + speed_bonus)
                else:
                    # Additive bonuses
                    if effect_type in effects:
                        effects[effect_type] += value * productivity
            
            # Apply trait effects
            for trait in researcher.traits:
                if trait == 'team_player' and has_team_player:
                    effects['team_productivity_bonus'] += 0.10
                elif trait == 'media_savvy':
                    effects['reputation_bonus'] += 1
                elif trait == 'safety_conscious':
                    effects['doom_reduction_bonus'] += 0.10 * productivity
        
        return effects
    
    def advance_researchers(self) -> None:
        """Advance all researchers by one turn (called during end_turn)."""
        for researcher in self.researchers:
            researcher.advance_turn()
        
        # Check for leak events
        for researcher in self.researchers:
            if 'leak_prone' in researcher.traits:
                if get_rng().random("random_context") < 0.05:  # 5% chance
                    self.messages.append(f"[WARNING]? {researcher.name} accidentally leaked research to competitors!")
                    # Give small advantage to random opponent
                    discovered_opponents = [opp for opp in self.opponents if opp.discovered]
                    if discovered_opponents:
                        target = get_rng().choice(discovered_opponents, "choice_context")
                        target.progress = min(target.progress + 2, 100)
                        self.messages.append(f"Competitor {target.name} gained research advantage.")
    
    def conduct_researcher_management_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """Conduct management actions for researchers."""
        from src.core.researchers import adjust_researcher_salary, conduct_team_building, conduct_performance_review
        
        if action_type == "salary_review":
            researcher_id = kwargs.get('researcher_id')
            new_salary = kwargs.get('new_salary')
            
            if researcher_id >= len(self.researchers):
                return {"success": False, "message": "Invalid researcher."}
            
            researcher = self.researchers[researcher_id]
            cost_difference = new_salary - researcher.current_salary
            
            if cost_difference > 0 and self.money < cost_difference:
                return {"success": False, "message": f"Cannot afford salary increase. Need ${cost_difference}."}
            
            result = adjust_researcher_salary(researcher, new_salary)
            if result["success"] and cost_difference != 0:
                self._add('money', -cost_difference)
            
            return result
        
        elif action_type == "team_building":
            cost = kwargs.get('cost', 50)
            # Note: Cost is already deducted by the action system, so we don't deduct it again here
            return conduct_team_building(self.researchers, cost)
        
        elif action_type == "performance_review":
            researcher_id = kwargs.get('researcher_id')
            if researcher_id >= len(self.researchers):
                return {"success": False, "message": "Invalid researcher."}
            
            researcher = self.researchers[researcher_id]
            return conduct_performance_review(researcher)
        
        return {"success": False, "message": "Unknown management action."}
    
    # Enhanced Personnel System Event Handlers
    
    def _researcher_breakthrough(self) -> None:
        """Handle researcher breakthrough event."""
        if not self.researchers:
            return
        
        # Select a random researcher for the breakthrough
        researcher = get_rng().choice(self.researchers, "choice_context")
        
        # Breakthrough effects based on specialization
        if researcher.specialization == "safety":
            doom_reduction = get_rng().randint(3, 6, "randint_context")
            rep_gain = get_rng().randint(2, 4, "randint_context")
            self._add('doom', -doom_reduction, f"{researcher.name} safety breakthrough")
            self._add('reputation', rep_gain)
            self.messages.append(f"? {researcher.name} achieved a major safety breakthrough! -{doom_reduction} doom, +{rep_gain} reputation")
        elif researcher.specialization == "capabilities":
            research_boost = get_rng().randint(8, 12, "randint_context")
            doom_risk = get_rng().randint(1, 3, "randint_context")
            self._add('research_progress', research_boost)
            self._add('doom', doom_risk, f"{researcher.name} capabilities breakthrough")
            self.messages.append(f"[LIGHTNING] {researcher.name} developed advanced AI capabilities! +{research_boost} research, +{doom_risk} doom risk")
        elif researcher.specialization == "interpretability":
            rep_gain = get_rng().randint(3, 5, "randint_context")
            self._add('reputation', rep_gain)
            # Reveal competitor information
            self._provide_competitor_update()
            self.messages.append(f"? {researcher.name} created breakthrough interpretability tools! +{rep_gain} reputation, competitor insights gained")
        elif researcher.specialization == "alignment":
            rep_gain = get_rng().randint(2, 4, "randint_context")
            self._add('reputation', rep_gain)
            # Reduce negative event chance temporarily (handled by existing alignment effect)
            self.messages.append(f"[TARGET] {researcher.name} solved a critical alignment problem! +{rep_gain} reputation, improved stability")
        
        # Boost researcher's loyalty and reduce burnout
        researcher.loyalty = min(researcher.loyalty + 15, 100)
        researcher.burnout = max(researcher.burnout - 10, 0)
    
    def _researcher_burnout_crisis(self) -> None:
        """Handle researcher burnout crisis event."""
        burnt_out_researchers = [r for r in self.researchers if r.burnout > 60]
        if not burnt_out_researchers:
            return
        
        # Apply crisis effects
        for researcher in burnt_out_researchers:
            researcher.burnout = min(researcher.burnout + 10, 100)
            researcher.loyalty = max(researcher.loyalty - 10, 0)
        
        self.messages.append(f"[WARNING]? Burnout crisis affects {len(burnt_out_researchers)} researchers! Productivity decreased.")
        self.messages.append("Consider team building or reducing workload to address burnout.")
    
    def _researcher_poaching_attempt(self) -> None:
        """Handle competitor poaching attempt."""
        if not self.researchers:
            return
        
        # Target researcher with lowest loyalty
        target = min(self.researchers, key=lambda r: r.loyalty)
        competitor_names = ["TechCorp AI", "Future Systems", "Meta Labs", "DeepMind Rivals"]
        competitor = get_rng().choice(competitor_names, "choice_context")
        
        # Calculate poaching success chance based on loyalty
        success_chance = max(0.1, (100 - target.loyalty) / 100 * 0.7)
        
        if get_rng().random("random_context") < success_chance:
            # Poaching successful
            self.researchers.remove(target)
            self._add('staff', -1)
            self._add('research_staff', -1)
            self.messages.append(f"? {competitor} successfully poached {target.name}! Lost key researcher.")
            
            # Remove corresponding employee blob
            if self.employee_blobs:
                for blob in self.employee_blobs:
                    if blob.get('subtype') == 'specialist_researcher':
                        self.employee_blobs.remove(blob)
                        break
        else:
            # Poaching failed, but loyalty is affected
            target.loyalty = max(target.loyalty - 5, 0)
            self.messages.append(f"[SHIELD]? {competitor} attempted to poach {target.name}, but they remained loyal!")
            self.messages.append("Consider salary adjustments to improve researcher loyalty.")
    
    def _research_ethics_concern(self) -> None:
        """Handle research ethics concern event."""
        capabilities_researchers = [r for r in self.researchers if r.specialization == 'capabilities']
        if not capabilities_researchers:
            return
        
        researcher = get_rng().choice(capabilities_researchers, "choice_context")
        
        # Ethical researcher may quit or reduce productivity
        if get_rng().random("random_context") < 0.3:  # 30% chance they quit
            self.researchers.remove(researcher)
            self._add('staff', -1) 
            self._add('research_staff', -1)
            self.messages.append(f"?? {researcher.name} quit due to ethical concerns about capabilities research!")
            self.messages.append("Consider focusing more on safety research to prevent future departures.")
        else:
            researcher.productivity *= 0.8  # 20% productivity reduction
            researcher.loyalty = max(researcher.loyalty - 15, 0)
            self.messages.append(f"?? {researcher.name} raised ethical concerns. Their productivity and loyalty declined.")
            self.messages.append("Address these concerns to maintain team cohesion.")
    
    def _researcher_conference_invitation(self) -> None:
        """Handle researcher conference invitation."""
        media_savvy_researchers = [r for r in self.researchers if 'media_savvy' in r.traits]
        if not media_savvy_researchers:
            # Fallback to any researcher
            if not self.researchers:
                return
            researcher = get_rng().choice(self.researchers, "choice_context")
        else:
            researcher = get_rng().choice(media_savvy_researchers, f"conference_researcher_turn_{self.turn}")
        
        # Conference provides reputation boost
        rep_gain = get_rng().randint(3, 6, "randint_context")
        self._add('reputation', rep_gain)
        
        # Small chance for networking opportunities (money)
        if get_rng().random("random_context") < 0.4:
            money_gain = get_rng().randint(50, 100, "randint_context")
            self._add('money', money_gain)
            self.messages.append(f"? {researcher.name} presented at a major conference! +{rep_gain} reputation, +${money_gain} from networking")
        else:
            self.messages.append(f"? {researcher.name} presented at a major conference! +{rep_gain} reputation")
        
        researcher.loyalty = min(researcher.loyalty + 10, 100)
    
    def _collaborative_research_opportunity(self) -> None:
        """Handle collaborative research opportunity."""
        if len(self.researchers) < 2:
            return
        
        # Requires investment but provides significant benefits
        cost = get_rng().randint(100, 200, "randint_context")
        
        if self.money >= cost:
            research_gain = get_rng().randint(15, 25, "randint_context")
            rep_gain = get_rng().randint(4, 7, "randint_context")
            
            self._add('money', -cost)
            self._add('research_progress', research_gain)
            self._add('reputation', rep_gain)
            
            self.messages.append(f"? Collaborative research project launched! Cost: ${cost}")
            self.messages.append(f"Benefits: +{research_gain} research progress, +{rep_gain} reputation")
            
            # Boost loyalty of participating researchers
            for researcher in get_rng().sample(self.researchers, min(2, len(self.researchers))):
                researcher.loyalty = min(researcher.loyalty + 8, 100)
        else:
            self.messages.append(f"? Collaborative research opportunity available, but need ${cost} to participate")
    
    def _researcher_loyalty_crisis(self) -> None:
        """Handle researcher loyalty crisis."""
        low_loyalty_researchers = [r for r in self.researchers if r.loyalty < 30]
        if len(low_loyalty_researchers) < 2:
            return
        
        # Crisis affects all low-loyalty researchers
        departures = 0
        for researcher in low_loyalty_researchers:
            if get_rng().random("random_context") < 0.4:  # 40% chance each leaves
                self.researchers.remove(researcher)
                self._add('staff', -1)
                self._add('research_staff', -1)
                departures += 1
            else:
                researcher.loyalty = max(researcher.loyalty - 10, 0)
        
        if departures > 0:
            self.messages.append(f"? Loyalty crisis! {departures} researchers left the organization.")
            # Remove corresponding employee blobs
            for _ in range(departures):
                for blob in self.employee_blobs:
                    if blob.get('subtype') == 'specialist_researcher':
                        self.employee_blobs.remove(blob)
                        break
        else:
            self.messages.append("? Loyalty crisis among researchers! Morale significantly decreased.")
        
        self.messages.append("Consider salary increases and team building to restore loyalty.")

    # Research Quality Event Handlers for Issue #190
    def _trigger_safety_shortcut_event(self) -> None:
        """
        Event where a researcher suggests cutting corners on safety validation.
        Player can choose response affecting technical debt and research speed.
        """
        from src.features.event_system import Event, EventType, EventAction
        
        # Find an assigned researcher for the story
        if not self.researcher_assignments:
            return
        
        researcher_id = get_rng().choice(list(self.researcher_assignments.keys()), "choice_context")
        researcher = self.get_researcher_by_id(researcher_id)
        task_name = self.researcher_assignments[researcher_id]
        
        if not researcher:
            return
        
        # Create an enhanced event with multiple options
        event_desc = (f"{researcher.name} suggests: \"We could skip some safety validation steps "
                     f"for {task_name} and finish 40% faster. The risk is probably minimal...\"")
        
        def handle_maintain_standards(gs: 'GameState') -> None:
            gs.messages.append(f"? {researcher.name}: \"You're right, safety first. I'll maintain full validation.\"")
            gs._add('reputation', 1)  # Reputation for safety-conscious approach
            
        def handle_calculated_risk(gs: 'GameState') -> None:
            gs.messages.append(f"[WARNING]? {researcher.name}: \"Understood. I'll reduce some checks but keep the critical ones.\"")
            gs.technical_debt.add_debt(1)  # Small debt increase
            # Speed up current research slightly (placeholder - would need research tracking)
            
        def handle_rush_it(gs: 'GameState') -> None:
            gs.messages.append(f"[ALERT] {researcher.name}: \"Alright, cutting corners to hit the deadline. Hope nothing goes wrong...\"")
            gs.technical_debt.add_debt(3)  # Significant debt increase
            gs._add('doom', 1, f"{researcher.name} cut safety corners")  # Small doom increase for risky approach
            
        # Use enhanced events if available, otherwise simple choice
        if hasattr(self, 'enhanced_events_enabled') and self.enhanced_events_enabled:
            enhanced_event = Event(
                name="Safety Shortcut Temptation",
                desc=event_desc,
                trigger=lambda gs: True,
                effect=handle_maintain_standards,  # Default action
                event_type=EventType.POPUP,
                available_actions=[EventAction.ACCEPT, EventAction.DEFER, EventAction.DISMISS]
            )
            
            # Add custom action handlers
            enhanced_event.action_handlers = {
                "maintain_standards": handle_maintain_standards,
                "calculated_risk": handle_calculated_risk,
                "rush_it": handle_rush_it
            }
            
            if hasattr(self, 'pending_popup_events'):
                self.pending_popup_events.append(enhanced_event)
            else:
                handle_maintain_standards(self)  # Fallback
        else:
            # Simple implementation - randomly choose response for now
            responses = [handle_maintain_standards, handle_calculated_risk, handle_rush_it]
            choice = get_rng().choice(responses, "choice_context")
            choice(self)
    
    def _trigger_technical_debt_warning(self) -> None:
        """
        Event warning player about accumulated technical debt consequences.
        """
        debt_level = self.technical_debt.accumulated_debt
        
        if debt_level < 10:
            self.messages.append("[WARNING]? Lead Researcher: \"We're accumulating some technical shortcuts. Should keep an eye on that.\"")
        elif debt_level < 15:
            self.messages.append("? Lead Researcher: \"Our technical debt is getting concerning. We should schedule refactoring soon.\"")
        else:
            self.messages.append("[ALERT] Lead Researcher: \"Critical warning: Our technical debt could trigger system failures!\"")
            
        # Offer debt reduction suggestion
        self.messages.append("Consider using 'Refactoring Sprint' or 'Safety Audit' actions to reduce technical debt.")
    
    def _trigger_quality_speed_dilemma(self) -> None:
        """
        Event presenting a critical deadline where player must choose quality vs speed.
        """
        scenarios = [
            "Conference deadline approaches",
            "Investor presentation next turn", 
            "Regulatory review incoming",
            "Competitor announcement imminent"
        ]
        
        scenario = get_rng().choice(scenarios, "choice_context")
        
        # Offer quality choice for all active research
        self.messages.append(f"? Critical: {scenario}! How should researchers adjust their approach?")
        
        def set_all_rushed() -> None:
            for researcher_id in self.researcher_assignments:
                self.researcher_default_quality[researcher_id] = ResearchQuality.RUSHED
            self.messages.append("? All researchers switched to RUSHED mode for speed!")
            self.technical_debt.add_debt(len(self.researcher_assignments))
            
        def set_all_thorough() -> None:
            for researcher_id in self.researcher_assignments:
                self.researcher_default_quality[researcher_id] = ResearchQuality.THOROUGH
            self.messages.append("? All researchers switched to THOROUGH mode for quality!")
            self._add('reputation', 1)
            
        def maintain_current() -> None:
            self.messages.append("?? Maintaining current research quality approaches.")
            
        # Simple random choice for now - in full implementation would be player choice
        choices = [set_all_rushed, set_all_thorough, maintain_current]
        weights = [0.3, 0.3, 0.4]  # Slight preference for maintaining current
        choice = get_rng().choices(choices, weights=weights)[0]
        choice()
    
    def _trigger_competitor_shortcut_discovery(self) -> None:
        """
        Event revealing that competitors are taking dangerous shortcuts.
        """
        if not hasattr(self, 'opponents') or not self.opponents:
            return
            
        # Find competitor with high technical debt (simulated)
        competitor_names = ["NeuralDyne", "QuantumLogic", "CyberBrain Corp"]
        competitor = get_rng().choice(competitor_names, "choice_context")
        
        discovery_types = [
            "Intelligence gathering reveals",
            "Whistleblower reports",
            "Academic paper analysis shows",
            "Industry rumors suggest"
        ]
        
        discovery = get_rng().choice(discovery_types, "choice_context")
        
        consequences = [
            "skipping safety validations entirely",
            "using untested architectures in production",
            "ignoring alignment research protocols",
            "rushing capability development without safeguards"
        ]
        
        consequence = get_rng().choice(consequences, "choice_context")
        
        self.messages.append(f"?? {discovery} {competitor} is {consequence}!")
        self.messages.append(f"This could give them a speed advantage but increases global risk.")
        
        # Player organization gains reputation for being more careful
        if self.technical_debt.accumulated_debt < 5:
            self._add('reputation', 1)
            self.messages.append("? Your careful approach gains recognition in contrast!")
        
        # Increase global doom slightly due to competitor shortcuts
        self._add('doom', get_rng().randint(1, 3, "randint_context"), f"competitor {competitor} taking dangerous shortcuts")
    
    # Economic Cycles & Funding Volatility Event Handlers for Issue #192
    
    def _trigger_funding_drought_event(self) -> None:
        """Handle venture capital drought during economic downturns."""
        if not hasattr(self, 'economic_cycles'):
            return
            
        self.messages.append("? Venture capital funding has become extremely scarce!")
        self.messages.append("[IDEA] Consider government grants or corporate partnerships instead.")
        
        # Extend funding cooldown during drought
        if hasattr(self, 'funding_round_cooldown'):
            self.funding_round_cooldown = max(self.funding_round_cooldown, 2)
        
        # Small reputation boost for surviving the drought
        self._add('reputation', 1)
    
    def _trigger_bubble_warning_event(self) -> None:
        """Handle AI bubble burst warnings."""
        self.messages.append("[WARNING]? Market analysts warn AI valuations are unsustainable!")
        self.messages.append("? Consider securing funding now before conditions worsen.")
        
        # Temporary funding bonus for those who act quickly
        if not hasattr(self, 'bubble_warning_bonus'):
            self.bubble_warning_bonus = 3  # 3 turns to act
    
    def _trigger_government_funding_event(self) -> None:
        """Handle government AI initiative announcements."""
        self.messages.append("?? Government announces major AI research funding initiative!")
        
        if self.reputation >= 10:
            grant_amount = get_rng().randint(80, 150, "randint_context")
            self._add('money', grant_amount)
            self.messages.append(f"Your organization qualifies for ${grant_amount}k government grant!")
        else:
            self.messages.append("Build more reputation to qualify for government funding programs.")
    
    def _trigger_corporate_partnership_event(self) -> None:
        """Handle corporate partnership opportunities during downturns."""
        corp_names = ["TechGiant Inc", "DataCorp Systems", "Innovation Dynamics"]
        corp = get_rng().choice(corp_names, "choice_context")
        
        self.messages.append(f"? {corp} seeks AI partnerships during the economic downturn!")
        
        partnership_amount = get_rng().randint(60, 120, "randint_context")
        self._add('money', partnership_amount)
        self.messages.append(f"Secured ${partnership_amount}k corporate partnership!")
        
        # Corporate partnerships provide stability but may limit reputation growth
        self._add('reputation', get_rng().randint(0, 2, "randint_context"))
    
    def _trigger_emergency_measures_event(self) -> None:
        """Handle emergency cost-cutting measures during severe economic stress."""
        if not hasattr(self, 'emergency_measures_available') or not self.emergency_measures_available:
            return
            
        self.messages.append("[ALERT] Economic conditions require immediate cost reduction!")
        
        # Emergency measures: reduce staff costs temporarily
        if self.staff > 1:
            staff_reduction = min(2, self.staff // 3)
            self._add('staff', -staff_reduction)
            savings = staff_reduction * 30
            self._add('money', savings)
            self.messages.append(f"Emergency layoffs: -{staff_reduction} staff, +${savings}k cash flow relief")
        
        # Mark emergency measures as used
        self.emergency_measures_available = False
        self._add('reputation', -2)  # Reputation hit for layoffs
    
    def _trigger_competitor_funding_event(self) -> None:
        """Handle competitor funding announcements during boom periods."""
        if not hasattr(self, 'opponents') or not self.opponents:
            return
            
        discovered_opponents = [opp for opp in self.opponents if opp.discovered]
        if not discovered_opponents:
            return
            
        competitor = get_rng().choice(discovered_opponents, "choice_context")
        funding_amounts = ["$50M", "$100M", "$200M", "$500M"]
        amount = get_rng().choice(funding_amounts, "choice_context")
        
        self.messages.append(f"[NEWS] {competitor.name} announces {amount} funding round!")
        self.messages.append("Competitive pressure increases - consider accelerating your own fundraising.")
        
        # Increase doom slightly due to competitor advancement
        self._add('doom', get_rng().randint(1, 3, "randint_context"), f"competitor {competitor.name} funding acceleration")
        
        # Create urgency for player fundraising
        if hasattr(self, 'funding_round_cooldown'):
            self.funding_round_cooldown = max(0, self.funding_round_cooldown - 1)
    
    def _trigger_ai_winter_warning_event(self) -> None:
        """Handle AI winter warnings when doom is high."""
        self.messages.append("?? Industry veterans warn of potential 'AI Winter' if promises don't materialize!")
        self.messages.append("[TARGET] Focus on demonstrable safety progress to maintain investor confidence.")
        
        # If safety research progress is low, more severe consequences
        if self.reputation < 15:
            funding_impact = get_rng().randint(20, 40, "randint_context")
            self._add('money', -funding_impact)
            self.messages.append(f"Investor confidence drops: -${funding_impact}k funding withdrawn")
    
    # Technical Failure Cascade Event Handlers for Issue #193
    

    
    def _trigger_near_miss_averted_event(self) -> None:
        """Handle near-miss events that were successfully averted."""
        if hasattr(self, 'technical_failures'):
            self.technical_failures.near_miss_count += 1
            
        near_miss_types = [
            "Advanced monitoring detected system anomaly before critical failure",
            "Cross-team communication prevented potential coordination breakdown",
            "Early warning systems identified security vulnerability before breach",
            "Incident response protocols contained developing infrastructure issue"
        ]
        
        near_miss = get_rng().choice(near_miss_types, "choice_context")
        self.messages.append(f"[WARNING]? NEAR MISS AVERTED: {near_miss}")
        self.messages.append("? Team conducts post-incident review to strengthen prevention capabilities")
        
        # Reward for good prevention systems
        self._add('reputation', 1)
        
        # Improve prevention systems slightly from lessons learned
        if hasattr(self, 'technical_failures') and get_rng().random("random_context") < 0.5:
            improvement_types = ['incident_response_level', 'monitoring_systems', 'communication_protocols']
            improvement = get_rng().choice(improvement_types, "choice_context")
            current_level = getattr(self.technical_failures, improvement, 0)
            if current_level < 5:
                setattr(self.technical_failures, improvement, current_level + 1)
                self.messages.append(f"? {improvement.replace('_', ' ').title()} improved from lessons learned!")
    
    def _trigger_cover_up_exposed_event(self) -> None:
        """Handle the exposure of past cover-ups."""
        if not hasattr(self, 'technical_failures'):
            return
            
        cover_up_severity = min(10, self.technical_failures.cover_up_debt)
        
        exposure_scenarios = [
            "Whistleblower reveals pattern of unreported incidents",
            "Regulatory audit uncovers hidden technical failures",
            "Former employee testimonies expose safety shortcuts",
            "Data leak reveals internal incident suppression policies"
        ]
        
        scenario = get_rng().choice(exposure_scenarios, "choice_context")
        self.messages.append(f"[ALERT] COVER-UP EXPOSED: {scenario}")
        
        # Severe reputation damage based on cover-up debt
        reputation_loss = get_rng().randint(cover_up_severity // 2, cover_up_severity, "randint_context")
        self._add('reputation', -reputation_loss)
        self.messages.append(f"? Reputation severely damaged: -{reputation_loss} points")
        
        # Financial penalties for regulatory violations
        financial_penalty = get_rng().randint(50, 100, "randint_context") + (cover_up_severity * 10)
        self._add('money', -financial_penalty)
        self.messages.append(f"? Regulatory fines and legal costs: -${financial_penalty}k")
        
        # Reduce cover-up debt (consequences have been paid)
        self.technical_failures.cover_up_debt = max(0, self.technical_failures.cover_up_debt - cover_up_severity)
        
        # Force improved transparency going forward
        self.messages.append("[LIST] Organization forced to adopt mandatory transparency policies")
        if hasattr(self, 'technical_debt'):
            self.technical_debt.add_debt(3)  # Increased oversight creates some operational debt
    
    def _trigger_transparency_dividend_event(self) -> None:
        """Handle recognition for transparent failure handling."""
        if not hasattr(self, 'technical_failures'):
            return
            
        recognition_types = [
            "Industry safety consortium recognizes transparent incident reporting",
            "Academic researchers cite organization as model for failure learning",
            "Regulatory agencies praise proactive safety communication",
            "Peer organizations request best practice sharing sessions"
        ]
        
        recognition = get_rng().choice(recognition_types, "choice_context")
        self.messages.append(f"[TROPHY] TRANSPARENCY RECOGNIZED: {recognition}")
        
        # Reputation boost
        reputation_gain = get_rng().randint(2, 4, "randint_context")
        self._add('reputation', reputation_gain)
        self.messages.append(f"? Industry respect grows: +{reputation_gain} reputation")
        
        # Funding opportunities from transparency
        if get_rng().random("random_context") < 0.6:
            funding_opportunity = get_rng().randint(30, 60, "randint_context")
            self._add('money', funding_opportunity)
            self.messages.append(f"? Safety-focused funding secured: +${funding_opportunity}k")
        
        # Improve staff morale (represented as temporary benefit)
        self.messages.append("? Staff morale improves from working at an ethical organization")
        
        # Reset transparency reputation to prevent repeated triggers
        self.technical_failures.transparency_reputation = max(0, 
                                                            self.technical_failures.transparency_reputation - 2.0)
    
    def _trigger_cascade_prevention_event(self) -> None:
        """Handle successful prevention of failure cascades."""
        if not hasattr(self, 'technical_failures'):
            return
            
        prevention_scenarios = [
            "Rapid incident response prevents system failure from spreading",
            "Cross-team coordination contains potential research setback cascade",
            "Advanced monitoring isolates infrastructure issue before propagation",
            "Communication protocols prevent crisis from escalating across departments"
        ]
        
        scenario = get_rng().choice(prevention_scenarios, "choice_context")
        self.messages.append(f"[SHIELD]? CASCADE PREVENTED: {scenario}")
        
        # Calculate what the cascade would have cost
        estimated_damage = get_rng().randint(40, 80, "randint_context")
        self.messages.append(f"[IDEA] Estimated damage prevented: ${estimated_damage}k and significant reputation loss")
        
        # Reward effective prevention
        reputation_gain = get_rng().randint(2, 3, "randint_context")
        self._add('reputation', reputation_gain)
        self.messages.append(f"? Stakeholder confidence in crisis management: +{reputation_gain} reputation")
        
        # Staff learning from successful prevention
        if hasattr(self, 'technical_debt') and get_rng().random("random_context") < 0.4:
            debt_reduction = get_rng().randint(1, 3, "randint_context")
            self.technical_debt.reduce_debt(debt_reduction)
            self.messages.append(f"? Prevention success improves practices: -{debt_reduction} technical debt")
        
        # Industry recognition
        if self.technical_failures.incident_response_level >= 4:
            self.messages.append("? Industry peers request consultation on incident response best practices")
        else:
            self.messages.append("Your strong safety reputation provides some protection from market fears.")
            self._add('reputation', 2)
    
    # ======= VERBOSE ACTIVITY LOGGING METHODS =======
    # For "old school turn by turn RPG details" style logging
    
    def _add_verbose_money_message(self, val: float, reason: str = "") -> None:
        """Add detailed, flavorful messages for money changes like an RPG combat log."""
        messages = create_verbose_money_message(val, reason, self.money)
        self.messages.extend(messages)
    
    def _add_verbose_staff_message(self, val: float, reason: str = "") -> None:
        """Add detailed, flavorful messages for staff changes like an RPG party management log."""
        messages = create_verbose_staff_message(val, reason, self.staff)
        self.messages.extend(messages)
    
    def _add_verbose_reputation_message(self, val: float, reason: str = "") -> None:
        """Add detailed, flavorful messages for reputation changes."""
        messages = create_verbose_reputation_message(val, reason, self.reputation)
        self.messages.extend(messages)
    
    def _add_verbose_compute_message(self, val: float, reason: str = "") -> None:
        """Add detailed, flavorful messages for compute resource changes."""
        messages = create_verbose_compute_message(val, reason, self.compute)
        self.messages.extend(messages)
    
    # ======= FUNDRAISING DIALOG SYSTEM =======
    # Similar to hiring dialog but for fundraising options
    
    def _trigger_fundraising_dialog(self) -> None:
        """Trigger the fundraising options dialog with multiple strategic choices."""
        # Get available fundraising options based on current game state
        available_options = self._get_available_fundraising_options()
        
        if not available_options:
            self.messages.append("No fundraising options available at this time.")
            return
        
        # Set up the fundraising dialog state using dialog manager
        self.pending_fundraising_dialog = DialogManager.create_fundraising_dialog_state(available_options)
    
    def _get_available_fundraising_options(self) -> List[Dict[str, Any]]:
        """Get available fundraising options based on current game state."""
        advanced_funding_unlocked = hasattr(self, 'advanced_funding_unlocked') and self.advanced_funding_unlocked
        return FundraisingDialogBuilder.build_fundraising_options(
            self.economic_config, self.reputation, advanced_funding_unlocked
        )
    
    def dismiss_fundraising_dialog(self) -> None:
        """Dismiss the fundraising dialog without making a selection."""
        from .dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self, 'fundraising')
    
    def select_fundraising_option(self, option_id: str) -> Tuple[bool, str]:
        """Execute a selected fundraising option and dismiss the dialog."""
        if not self.pending_fundraising_dialog:
            return False, "No fundraising dialog active"
        
        # Find the selected option
        selected_option = None
        for option in self.pending_fundraising_dialog["available_options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Unknown fundraising option: {option_id}"
        
        if not selected_option["available"]:
            return False, f"{selected_option['name']} is not available yet"
        
        # Execute the fundraising option
        self._execute_fundraising_option(selected_option)
        
        # Dismiss the dialog
        self.dismiss_fundraising_dialog()
        
        return True, f"Successfully executed: {selected_option['name']}"
    
    def _execute_fundraising_option(self, option: Dict[str, Any]) -> bool:
        """Execute a specific fundraising option with detailed verbose logging."""
        option_id = option["id"]
        
        if option_id == "fundraise_small":
            return self._execute_small_fundraising(option)
        elif option_id == "fundraise_big": 
            return self._execute_big_fundraising(option)
        elif option_id == "borrow_money":
            return self._execute_borrowing(option)
        elif option_id == "alternative_funding":
            return self._execute_alternative_funding(option)
        else:
            self.messages.append(f"Unknown fundraising option: {option_id}")
            return False
    
    def _execute_small_fundraising(self, option: Dict[str, Any]) -> bool:
        """Execute conservative small fundraising."""
        amount = get_rng().randint(option["min_amount"], option["max_amount"], "randint_context")
        # Reputation bonus helps
        amount += min(self.reputation // 2, 15)  # Max +15k from reputation
        
        self._add('money', amount, f"small fundraising round")
        
        # Minimal reputation risk
        if get_rng().random("random_context") < option["reputation_risk"]:
            self._add('reputation', -1, "fundraising complications")
        
        return True
    
    def _execute_big_fundraising(self, option: Dict[str, Any]) -> bool:
        """Execute aggressive big fundraising."""
        base_amount = get_rng().randint(option["min_amount"], option["max_amount"], "randint_context")
        # Reputation significantly affects big rounds
        reputation_multiplier = 1.0 + (self.reputation / 50.0)  # Up to +40% at 20 rep
        amount = int(base_amount * reputation_multiplier)
        
        self._add('money', amount, f"major fundraising round")
        
        # Higher reputation risk
        if get_rng().random("random_context") < option["reputation_risk"]:
            self._add('reputation', -2, "aggressive fundraising backlash")
        else:
            # Success can boost reputation
            if amount > 120:
                self._add('reputation', 1, "successful major fundraising")
        
        return True
    
    def _execute_borrowing(self, option: Dict[str, Any]) -> bool:
        """Execute debt-based funding."""
        amount = get_rng().randint(option["min_amount"], option["max_amount"], "randint_context")
        
        self._add('money', amount, f"debt financing")
        
        # Create future debt obligation (simplified - could be enhanced later)
        if not hasattr(self, 'debt_obligations'):
            self.debt_obligations = []
        
        # Debt payment due in 3-5 turns
        payment_due = self.turn + get_rng().randint(3, 5, "randint_context")
        payment_amount = int(amount * 1.2)  # 20% interest
        
        self.debt_obligations.append({
            'amount': payment_amount,
            'due_turn': payment_due,
            'description': f"Debt repayment from Turn {self.turn}"
        })
        
        self.messages.append(f"? Debt obligation: ${payment_amount}k due by Turn {payment_due}")
        
        return True
    
    def _execute_alternative_funding(self, option: Dict[str, Any]) -> bool:
        """Execute alternative funding sources.""" 
        sources = ["government grants", "strategic partnerships", "customer revenue", "research grants"]
        source = get_rng().choice(sources, "choice_context")
        
        amount = get_rng().randint(option["min_amount"], option["max_amount"], "randint_context")
        
        # Alternative funding often comes with constraints or benefits
        if source == "government grants":
            amount += 20  # Government grants are larger but...
            self.messages.append("? Government oversight increases - expect compliance requirements")
        elif source == "strategic partnerships":
            self._add('reputation', 1, "partnership credibility boost")
        elif source == "customer revenue":
            self._add('reputation', 2, "market validation from paying customers")
        
        self._add('money', amount, f"alternative funding: {source}")
        
        # Very low reputation risk
        if get_rng().random("random_context") < option["reputation_risk"]:
            self._add('reputation', -1, "alternative funding complications")
        
        return True

    # =================== RESEARCH DIALOG SYSTEM ===================
    
    def _trigger_research_dialog(self) -> None:
        """Trigger research type selection dialog with available research approaches."""
        # Get available research options
        available_options = self._get_available_research_options()
        
        # Create research dialog state using dialog manager
        self.pending_research_dialog = DialogManager.create_research_dialog_state(available_options)
        
        # Ensure research quality system is also unlocked for quality settings
        if not self.research_quality_unlocked:
            self.research_quality_unlocked = True
            self.add_message("? Research Quality Dashboard unlocked! Use the panel below End Turn to change research approach.")
        else:
            self.add_message("? Use the Research Quality panel below End Turn to change your research approach.")
    
    def _get_available_research_options(self) -> List[Dict[str, Any]]:
        """Get available research options based on current game state."""
        return ResearchDialogBuilder.build_research_options(self.money, self.reputation)
    
    def dismiss_research_dialog(self) -> None:
        """Dismiss the research dialog."""
        from .dialog_manager import DialogManager
        DialogManager.dismiss_dialog(self, 'research')
    
    def select_research_option(self, option_id: str) -> Tuple[bool, str]:
        """Execute the selected research option."""
        if not self.pending_research_dialog:
            return False, "No research dialog active"
        
        # Find the selected option
        selected_option = None
        for option in self.pending_research_dialog["available_options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, "Invalid research option"
            
        if not selected_option["available"]:
            return False, f"Research option not available: {selected_option['requirements']}"
            
        if not selected_option["affordable"]:
            return False, f"Cannot afford research: {selected_option['requirements']}"
        
        # Execute the research
        success = self._execute_research_option(selected_option)
        if success:
            self.dismiss_research_dialog()
            return True, f"Successfully executed: {selected_option['name']}"
        else:
            return False, "Research execution failed"
    
    def _execute_research_option(self, option: Dict[str, Any]) -> bool:
        """Execute a research option with appropriate effects."""
        # Deduct cost
        self._add('money', -option["cost"])
        
        # Calculate doom reduction with upgrades
        base_reduction = get_rng().randint(option["min_doom_reduction"], option["max_doom_reduction"], "randint_context")
        
        # Apply upgrade bonuses
        upgrade_bonus = 0
        if 'better_computers' in self.upgrade_effects:
            upgrade_bonus += 1
        if 'hpc_cluster' in self.upgrade_effects:
            upgrade_bonus += 2
        if 'research_automation' in self.upgrade_effects and self.compute >= 10:
            upgrade_bonus += 1
            
        final_reduction = base_reduction + upgrade_bonus
        
        # Apply doom reduction
        self._add('doom', -final_reduction)
        
        # Apply reputation gain
        self._add('reputation', option["reputation_gain"])
        
        # Handle technical debt based on research type
        if option["id"] == "rush_research":
            if hasattr(self, 'technical_debt'):
                # Add technical debt for rush research
                debt_increase = get_rng().randint(1, 3, "randint_context")
                # Fixed: correct argument order (amount, category) and use proper DebtCategory enum
                from src.core.research_quality import DebtCategory
                self.technical_debt.add_debt(debt_increase, DebtCategory.VALIDATION)
                self.messages.append(f"? Technical debt increased: {debt_increase} points from rushed methodology")
        elif option["id"] == "quality_research":
            if hasattr(self, 'technical_debt'):
                # Quality research reduces technical debt
                debt_reduction = get_rng().randint(1, 2, "randint_context")
                # Fixed: correct argument order (amount, category) and use proper DebtCategory enum
                from src.core.research_quality import DebtCategory
                self.technical_debt.reduce_debt(debt_reduction, DebtCategory.VALIDATION)
                self.messages.append(f"? Technical debt reduced: {debt_reduction} points from thorough methodology")
        
        # Unlock quality research after first research action
        if not hasattr(self, 'research_quality_unlocked'):
            self.research_quality_unlocked = True
        elif not self.research_quality_unlocked:
            self.research_quality_unlocked = True
            self.messages.append("? Quality Research unlocked - thorough methodology now available")
        
        # Add verbose logging message
        option["name"].replace(" Research", "").lower()
        self._add_verbose_research_message(option["name"], final_reduction, option["reputation_gain"])
        
        return True
    
    def _add_verbose_research_message(self, research_type: str, doom_reduction: int, rep_gain: int) -> None:
        """Add detailed research progress message."""
        research_messages = [
            f"? Research breakthrough: {research_type} advances reduce P(Doom) by {doom_reduction}%",
            f"? Publication success: {research_type} findings boost reputation (+{rep_gain})",
            f"? Laboratory progress: {research_type} methodology shows {doom_reduction}% safety improvement",
            f"? Academic recognition: {research_type} work gains {rep_gain} reputation in safety community",
            f"? Research milestone: {research_type} delivers {doom_reduction}% risk reduction, +{rep_gain} standing"
        ]
        
        selected_message = get_rng().choice(research_messages, "choice_context")
        self.messages.append(selected_message)

    def _execute_standalone_safety_research(self) -> None:
        """Execute standalone Safety Research action (for backward compatibility with tests)."""
        # Create a safety research option using the same logic as the research dialog
        safety_option = {
            "id": "safety_research",
            "name": "Safety Research",
            "min_doom_reduction": 2,
            "max_doom_reduction": 6,
            "reputation_gain": 2,
            "cost": 40
        }
        
        # Use the existing research execution method
        success = self._execute_research_option(safety_option)
        
        if success:
            # Add specific safety research message for standalone execution
            self.messages.append("Research team focuses on AI safety fundamentals - interpretability and alignment techniques")

    def _has_revealed_opponents(self) -> bool:
        """Check for revealed opponents - delegated to intelligence system manager."""
        return self.intelligence_system.has_revealed_opponents()

    def _investigate_specific_opponent(self) -> None:
        """Deep opponent investigation - delegated to intelligence system manager."""
        return self.intelligence_system.investigate_specific_opponent()

    def pet_office_cat(self, mouse_pos: Tuple[int, int]) -> bool:
        """Delegate office cat petting to the input manager."""
        return self.input_manager.pet_office_cat(mouse_pos)

    def get_cat_doom_stage(self) -> int:
        """Get the current doom stage of the office cat for visual representation."""
        if not getattr(self, 'office_cat_adopted', False):
            return 0

        # Cat gets more ominous as doom increases - visual feedback system
        doom_percentage = self.doom / self.max_doom

        if doom_percentage < 0.2:
            return 0  # Happy, normal cat
        elif doom_percentage < 0.4:
            return 1  # Slightly concerned cat
        elif doom_percentage < 0.6:
            return 2  # Alert cat with glowing eyes
        elif doom_percentage < 0.8:
            return 3  # Ominous cat with red eyes
        else:
            return 4  # Terrifying doom cat with laser eyes

    def update_cat_position(self, screen_w: int, screen_h: int) -> None:
        """Update office cat position and animation."""
        if not getattr(self, 'office_cat_adopted', False):
            return

        # Cat likes to stay in the bottom-right area, avoiding UI elements
        target_x = screen_w - 150  # Stay away from right edge UI
        target_y = screen_h - 120  # Stay away from bottom UI

        # Slowly move towards target position (smooth movement)
        current_x, current_y = getattr(self, 'office_cat_position', (target_x, target_y))
        
        # Move 10% of the way to target each frame
        new_x = current_x + (target_x - current_x) * 0.1
        new_y = current_y + (target_y - current_y) * 0.1

        self.office_cat_position = (int(new_x), int(new_y))
    
    # UI Transition Manager Delegation Properties
    @property
    def ui_transitions(self) -> List[Dict[str, Any]]:
        """Delegate to UITransitionManager for backward compatibility."""
        return self.ui_transition_manager.get_ui_transitions()
    
    @property
    def upgrade_transitions(self) -> Dict[int, Dict[str, Any]]:
        """Delegate to UITransitionManager for backward compatibility."""
        return self.ui_transition_manager.get_upgrade_transitions()

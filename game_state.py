import random
import json
import os
from typing import Tuple
from actions import ACTIONS
from upgrades import UPGRADES
from events import EVENTS
from game_logger import GameLogger
from sound_manager import SoundManager
from opponents import create_default_opponents
from event_system import Event, DeferredEventQueue, EventType, EventAction
from onboarding import onboarding
from overlay_manager import OverlayManager

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
        self.last_balance_change = 0
        self.accounting_software_bought = False  # So the flag always exists
        # Core resources
        self.money = 100000  # Increased starting funding as required
        self.staff = 2
        self.reputation = 15
        self.doom = 12  # Out of 100
        self.compute = 0  # New compute resource, starts at 0
        self.research_progress = 0  # Track research progress for paper generation
        self.papers_published = 0  # Count of research papers published
        
        # Action Points system (Phase 1 & 2)
        self.action_points = 3  # Current available action points
        self.max_action_points = 3  # Maximum action points per turn (will be calculated dynamically)
        self.ap_spent_this_turn = False  # Track if AP was spent for UI glow effects
        self.ap_glow_timer = 0  # Timer for AP glow animation
        
        # Phase 2: Staff-Based AP Scaling
        self.admin_staff = 0  # Admin assistants: +1.0 AP each
        self.research_staff = 0  # Research staff: Enable research action delegation
        self.ops_staff = 0  # Operations staff: Enable operational action delegation
        
        self.turn = 0
        self.max_doom = 100
        self.selected_actions = []
        self.staff_maintenance = 15
        self.seed = seed
        self.upgrades = [dict(u) for u in UPGRADES]
        self.upgrade_effects = set()
        self.messages = ["Game started! Select actions, then End Turn."]
        self.game_over = False
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

        # Tutorial and onboarding system
        self.tutorial_enabled = True  # Whether tutorial is enabled (default True for new players)
        self.tutorial_shown_milestones = set()  # Track which milestone tutorials have been shown
        self.pending_tutorial_message = None  # Current tutorial message waiting to be shown
        self.first_game_launch = True  # Track if this is the first game launch

        # Copy modular content
        self.actions = [dict(a) for a in ACTIONS]
        self.events = [dict(e) for e in EVENTS]
        
        # Enhanced event system
        self.deferred_events = DeferredEventQueue()
        self.pending_popup_events = []  # Events waiting for player action
        self.enhanced_events_enabled = False  # Flag to enable new event types
        
        # Initialize game logger
        self.logger = GameLogger(seed)
        
        # Initialize UI overlay management system
        self.overlay_manager = OverlayManager()
        
        # Error tracking for easter egg beep system
        self.error_history = []  # Track recent errors for pattern detection
        self.last_error_beep_time = 0  # Prevent spam beeping
        self.logger = GameLogger(seed)
        
        # UI Transition System for smooth visual feedback
        self.ui_transitions = []  # List of active UI transition animations
        self.upgrade_transitions = {}  # Track transitions for individual upgrades
        
        # Initialize employee blobs for starting staff
        self._initialize_employee_blobs()
        
        # Load tutorial settings (after initialization)
        self.load_tutorial_settings()

    def calculate_max_ap(self):
        """
        Calculate maximum Action Points per turn based on staff composition.
        
        Base AP: 3 per turn
        Staff bonus: +0.5 AP per regular staff member
        Admin bonus: +1.0 AP per admin assistant
        
        Returns:
            int: Maximum action points for the current turn
        """
        base = 3
        staff_bonus = self.staff * 0.5
        admin_bonus = self.admin_staff * 1.0
        return int(base + staff_bonus + admin_bonus)

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
        """Initialize employee blobs for starting staff"""
        import math
        for i in range(self.staff):
            # Position blobs in lower middle area, clustered
            base_x = 400 + (i % 3) * 60  # 3 blobs per row
            base_y = 500 + (i // 3) * 60  # Stack rows
            
            blob = {
                'id': i,
                'x': base_x,
                'y': base_y, 
                'target_x': base_x,
                'target_y': base_y,
                'has_compute': False,
                'productivity': 0.0,
                'animation_progress': 1.0,  # Already positioned
                'type': 'employee',  # Track blob type
                'managed_by': None,  # Which manager manages this employee (None if unmanaged)
                'unproductive_reason': None  # Reason for being unproductive (for overlay display)
            }
            self.employee_blobs.append(blob)
    
    def _add_employee_blobs(self, count):
        """Add new employee blobs with animation from side"""
        import math
        for i in range(count):
            blob_id = len(self.employee_blobs)
            # Calculate target position in cluster
            target_x = 400 + (blob_id % 3) * 60
            target_y = 500 + (blob_id // 3) * 60
            
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
                'unproductive_reason': None  # Reason for being unproductive (for overlay display)
            }
            self.employee_blobs.append(blob)
            
            # Play blob sound effect for new hire
            self.sound_manager.play_blob_sound()
            
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
            'management_capacity': 9  # Can manage up to 9 employees
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
        """Update employee productivity based on compute availability and management each week"""
        productive_employees = 0
        research_gained = 0
        
        # Reset all employees' compute status
        for blob in self.employee_blobs:
            blob['has_compute'] = False
            blob['productivity'] = 0.0
            
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
                    
        # Assign compute to productive employees (1 compute per employee if available)
        compute_assigned = 0
        for blob in self.employee_blobs:
            if blob['type'] == 'manager':
                # Managers always have compute and are productive
                blob['has_compute'] = True
                blob['productivity'] = 1.0
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
                    productive_employees += 1
                    
        # Generate research from productive employees
        for blob in self.employee_blobs:
            if blob['productivity'] > 0:
                # Each productive employee has a chance to contribute to research
                if random.random() < 0.3:  # 30% chance per productive employee
                    research_gained += random.randint(1, 3)
                    
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
            self.messages.append(f"Research progress: +{research_gained} (total: {self.research_progress})")
            
        # Check if research threshold reached for paper publication
        if self.research_progress >= 100:
            papers_to_publish = self.research_progress // 100
            self.papers_published += papers_to_publish
            self.research_progress = self.research_progress % 100
            self._add('reputation', papers_to_publish * 5)  # Papers boost reputation
            self.messages.append(f"Research paper{'s' if papers_to_publish > 1 else ''} published! (+{papers_to_publish}, total: {self.papers_published})")
            
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
        # Actions (left)
        a_rects = self._get_action_rects(w, h)
        for idx, rect in enumerate(a_rects):
            if self._in_rect(mouse_pos, rect):
                if not self.game_over:
                    action = self.actions[idx]
                    # Check if action is available (rules constraint)
                    if action.get("rules") and not action["rules"](self):
                        self.messages.append(f"{action['name']} is not available yet.")
                        return None
                    
                    # Check if delegation would be beneficial (lower AP cost)
                    delegate = False
                    if (action.get("delegatable", False) and 
                        self.can_delegate_action(action) and
                        action.get("delegate_ap_cost", action.get("ap_cost", 1)) < action.get("ap_cost", 1)):
                        delegate = True
                    
                    # Try to execute the action (with auto-delegation if beneficial)
                    if self.execute_action_with_delegation(idx, delegate):
                        pass  # Success message already handled in execute_action_with_delegation
                    # Error messages also handled in execute_action_with_delegation
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

        # End Turn button (bottom center)
        btn_rect = self._get_endturn_rect(w, h)
        if self._in_rect(mouse_pos, btn_rect) and not self.game_over:
            self.end_turn()
            return None

        # Mute button (bottom right)
        mute_rect = self._get_mute_button_rect(w, h)
        if self._in_rect(mouse_pos, mute_rect):
            new_state = self.sound_manager.toggle()
            status = "enabled" if new_state else "disabled"
            self.messages.append(f"Sound {status}")
            return None

        # Activity log minimize/expand button (if compact display upgrade is purchased)
        if "compact_activity_display" in self.upgrade_effects:
            if hasattr(self, 'activity_log_minimized') and self.activity_log_minimized:
                # Expand button
                expand_rect = self._get_activity_log_expand_button_rect(w, h)
                if self._in_rect(mouse_pos, expand_rect):
                    self.activity_log_minimized = False
                    self.messages.append("Activity log expanded.")
                    return None
            elif self.scrollable_event_log_enabled:
                # Minimize button
                minimize_rect = self._get_activity_log_minimize_button_rect(w, h)
                if self._in_rect(mouse_pos, minimize_rect):
                    self.activity_log_minimized = True
                    self.messages.append("Activity log minimized.")
                    return None

        return None

    def check_hover(self, mouse_pos, w, h):
        # Reset all hover states
        self.hovered_upgrade_idx = None
        self.hovered_action_idx = None
        self.endturn_hovered = False
        
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
        # Purchased: row at top right
        purchased_rects = [
            (w - icon_w*(len(purchased)-j+1), int(h*0.08), icon_w, icon_h)
            for j, i in enumerate(purchased)
        ]
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
        log_x = int(w*0.04)
        log_y = int(h*0.74)
        log_width = int(w * 0.44)
        button_size = int(h * 0.025)
        button_x = log_x + log_width - 30
        button_y = log_y
        return (button_x, button_y, button_size, button_size)

    def _get_activity_log_expand_button_rect(self, w, h):
        """Get rectangle for the activity log expand button (only when log is minimized)"""
        log_x = int(w*0.04)
        log_y = int(h*0.74)
        
        # Estimate title width based on character count (avoiding pygame dependency in tests)
        title_width = len("Activity Log") * int(h*0.015)  # Rough character width estimate
        
        button_size = int(h * 0.025)
        button_x = log_x + title_width + 10
        button_y = log_y
        return (button_x, button_y, button_size, button_size)

    def _in_rect(self, pt, rect):
        x, y = pt
        rx, ry, rw, rh = rect
        return rx <= x <= rx+rw and ry <= y <= ry+rh

    def end_turn(self):
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

        # Staff maintenance
        maintenance_cost = self.staff * self.staff_maintenance
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

        # If game ended, log final state and write log file
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

        # Save high score if achieved
        self.save_highscore()
        
        # Update UI transitions - animations advance each frame/turn
        self._update_ui_transitions()

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
        from event_system import create_enhanced_events
        
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
    
    def dismiss_tutorial_message(self):
        """Dismiss the current tutorial message and mark milestone as shown."""
        if self.pending_tutorial_message:
            milestone_id = self.pending_tutorial_message["milestone_id"]
            self.tutorial_shown_milestones.add(milestone_id)
            self.pending_tutorial_message = None
            self.save_tutorial_settings()
    
    def _create_upgrade_transition(self, upgrade_idx, start_rect, end_rect):
        """Create a smooth transition animation for an upgrade moving from button to icon."""
        transition = {
            'type': 'upgrade_transition',
            'upgrade_idx': upgrade_idx,
            'start_rect': start_rect,
            'end_rect': end_rect,
            'progress': 0.0,
            'duration': 30,  # 30 frames for 1 second at 30fps
            'trail_points': [],  # For visual trail effect
            'glow_timer': 60,  # Extra glow time after transition completes
            'completed': False
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
        """Update a single upgrade transition animation."""
        if not transition['completed']:
            # Advance animation progress
            transition['progress'] = min(1.0, transition['progress'] + (1.0 / transition['duration']))
            
            # Add trail point for current position
            current_pos = self._interpolate_position(
                transition['start_rect'], 
                transition['end_rect'], 
                transition['progress']
            )
            transition['trail_points'].append({
                'pos': current_pos,
                'alpha': 255,
                'age': 0
            })
            
            # Limit trail length
            if len(transition['trail_points']) > 10:
                transition['trail_points'].pop(0)
            
            # Mark as completed when progress reaches 1.0
            if transition['progress'] >= 1.0:
                transition['completed'] = True
        
        # Update trail points (fade them out)
        for point in transition['trail_points']:
            point['age'] += 1
            point['alpha'] = max(0, 255 - (point['age'] * 25))
        
        # Remove fully faded trail points
        transition['trail_points'] = [p for p in transition['trail_points'] if p['alpha'] > 0]
        
        # Update glow timer
        if transition['glow_timer'] > 0:
            transition['glow_timer'] -= 1
    
    def _interpolate_position(self, start_rect, end_rect, progress):
        """Interpolate position between start and end rectangles with smooth easing."""
        # Use easeOutCubic for smooth deceleration
        eased_progress = 1 - (1 - progress) ** 3
        
        start_x = start_rect[0] + start_rect[2] // 2  # Center of start rect
        start_y = start_rect[1] + start_rect[3] // 2
        end_x = end_rect[0] + end_rect[2] // 2  # Center of end rect  
        end_y = end_rect[1] + end_rect[3] // 2
        
        # Create curved arc path (slightly upward curve)
        mid_x = (start_x + end_x) / 2
        mid_y = min(start_y, end_y) - 50  # Arc 50 pixels above the midpoint
        
        # Quadratic Bezier curve interpolation
        t = eased_progress
        x = (1-t)**2 * start_x + 2*(1-t)*t * mid_x + t**2 * end_x
        y = (1-t)**2 * start_y + 2*(1-t)*t * mid_y + t**2 * end_y
        
        return (int(x), int(y))
    
    def track_error(self, error_message: str) -> bool:
        """
        Track an error for the easter egg beep system.
        
        Args:
            error_message: The error message that occurred
            
        Returns:
            bool: True if this triggers the easter egg (3 repeated identical errors)
        """
        import pygame
        
        current_time = pygame.time.get_ticks()
        
        # Add error to overlay manager (which handles the logic)
        should_beep = self.overlay_manager.add_error(error_message, current_time // (1000 // 30))
        
        # Play easter egg beep if triggered and enough time has passed
        if should_beep and (current_time - self.last_error_beep_time) > 2000:  # 2 second cooldown
            self.sound_manager.play_error_beep()
            self.last_error_beep_time = current_time
            self.messages.append("🔊 Error pattern detected! (Easter egg activated)")
            return True
            
        return False
    
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
        from action_rules import ActionRules
        action_rules = ActionRules()
        if not action_rules.is_action_available(action["name"], self):
            error_msg = f"Action '{action['name']}' not available"
            self.track_error(error_msg)
            return False, error_msg
        
        return True, "OK"

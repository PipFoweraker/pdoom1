import random
import json
import os
from actions import ACTIONS
from upgrades import UPGRADES
from events import EVENTS
from game_logger import GameLogger
from sound_manager import SoundManager
from opponents import create_default_opponents
from event_system import Event, DeferredEventQueue, EventType, EventAction

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
            self.doom = min(max(self.doom + val, 0), self.max_doom)
        elif attr == 'reputation':
            self.reputation = max(self.reputation + val, 0)
        elif attr == 'staff':
            old_staff = self.staff
            self.staff = max(self.staff + val, 0)
            # Update employee blobs when staff changes
            if val > 0:  # Hiring
                self._add_employee_blobs(val)
            elif val < 0:  # Staff leaving
                self._remove_employee_blobs(old_staff - self.staff)
        elif attr == 'compute':
            self.compute = max(self.compute + val, 0)
        elif attr == 'research_progress':
            self.research_progress = max(self.research_progress + val, 0)
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
        
        # Action Points system (Phase 1)
        self.action_points = 3  # Current available action points
        self.max_action_points = 3  # Maximum action points per turn
        self.ap_spent_this_turn = False  # Track if AP was spent for UI glow effects
        self.ap_glow_timer = 0  # Timer for AP glow animation
        
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
        
        # For hover/tooltip (which upgrade is hovered)
        self.hovered_upgrade_idx = None

        # Scrollable event log feature
        self.scrollable_event_log_enabled = False
        self.event_log_history = []  # Full history of all messages
        self.event_log_scroll_offset = 0

        # Copy modular content
        self.actions = [dict(a) for a in ACTIONS]
        self.events = [dict(e) for e in EVENTS]
        
        # Enhanced event system
        self.deferred_events = DeferredEventQueue()
        self.pending_popup_events = []  # Events waiting for player action
        self.enhanced_events_enabled = False  # Flag to enable new event types
        
        # Initialize game logger
        self.logger = GameLogger(seed)
        
        # Initialize employee blobs for starting staff
        self._initialize_employee_blobs()

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

    def _add(self, attr, val):
        if attr == 'doom':
            self.doom = min(max(self.doom + val, 0), self.max_doom)
        elif attr == 'money':
            self.money = max(self.money + val, 0)
        elif attr == 'reputation':
            self.reputation = max(self.reputation + val, 0)
        elif attr == 'staff':
            old_staff = self.staff
            self.staff = max(self.staff + val, 0)
            # Update employee blobs when staff changes
            if val > 0:  # Hiring
                self._add_employee_blobs(val)
            elif val < 0:  # Staff leaving
                self._remove_employee_blobs(old_staff - self.staff)
        elif attr == 'compute':
            self.compute = max(self.compute + val, 0)
        elif attr == 'research_progress':
            self.research_progress = max(self.research_progress + val, 0)
        return None

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
                    
                    # Check Action Points availability
                    ap_cost = action.get("ap_cost", 1)  # Default AP cost is 1
                    if self.action_points < ap_cost:
                        self.messages.append(f"Not enough Action Points for {action['name']} (need {ap_cost}, have {self.action_points}).")
                        return None
                    
                    # Check money availability
                    if self.money >= action["cost"]:
                        self.selected_actions.append(idx)
                        self.messages.append(f"Selected: {action['name']}")
                    else:
                        self.messages.append("Not enough money for that action.")
                return None

        # Upgrades (right, as icons or buttons)
        u_rects = self._get_upgrade_rects(w, h)
        for idx, rect in enumerate(u_rects):
            if self._in_rect(mouse_pos, rect):
                upg = self.upgrades[idx]
                if not upg.get("purchased", False):
                    if self.money >= upg["cost"]:
                        self.money -= upg["cost"]
                        upg["purchased"] = True
                        self.upgrade_effects.add(upg["effect_key"])
                        self.messages.append(f"Upgrade purchased: {upg['name']}")
                        # Log upgrade purchase
                        self.logger.log_upgrade(upg["name"], upg["cost"], self.turn)
                    else:
                        self.messages.append("Not enough money for upgrade.")
                else:
                    self.messages.append("Already purchased.")
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

        return None

    def check_hover(self, mouse_pos, w, h):
        # Only check upgrades (for tooltip)
        u_rects = self._get_upgrade_rects(w, h)
        for idx, rect in enumerate(u_rects):
            if self._in_rect(mouse_pos, rect):
                self.hovered_upgrade_idx = idx
                return self.upgrades[idx]["desc"]
        self.hovered_upgrade_idx = None
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

    def _get_endturn_rect(self, w, h):
        return (int(w*0.39), int(h*0.88), int(w*0.22), int(h*0.07))

    def _get_mute_button_rect(self, w, h):
        button_size = int(min(w, h) * 0.04)
        button_x = w - button_size - 20
        button_y = h - button_size - 20
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
            ap_cost = action.get("ap_cost", 1)  # Default AP cost is 1
            
            # Deduct Action Points
            self.action_points -= ap_cost
            self.ap_spent_this_turn = True  # Track for UI glow effects
            self.ap_glow_timer = 30  # 30 frames of glow effect
            
            # Deduct money cost
            self.money -= action["cost"]
            
            # Log the action
            self.logger.log_action(action["name"], action["cost"], self.turn)
            
            # Execute action effects
            if action.get("upside"): action["upside"](self)
            if action.get("downside"): action["downside"](self)
            if action.get("rules"): action["rules"](self)
        self.selected_actions = []

        # Staff maintenance
        maintenance_cost = self.staff * self.staff_maintenance
        self.money -= maintenance_cost
        if self.money < 0:
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
        
        # Handle deferred events (tick expiration and auto-execute expired ones)
        if hasattr(self, 'deferred_events'):
            expired_events = self.deferred_events.tick_all_events(self)
        
        self.turn += 1
        
        # Reset Action Points for new turn
        self.action_points = self.max_action_points
        self.ap_spent_this_turn = False  # Reset glow flag for new turn
        
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

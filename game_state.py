import random
import json
import os
from actions import ACTIONS
from upgrades import UPGRADES
from events import EVENTS
from game_logger import GameLogger
from sound_manager import SoundManager

SCORE_FILE = "local_highscore.json"

class GameState:
    def _add(self, attr, val):
        """
        Adds val to the given attribute, clamping where appropriate.
        Also records last_balance_change for 'money' for use in UI,
        if accounting software has been purchased.
        """
        if attr == 'money':
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
        self.opp_progress = random.randint(15, 40)
        self.known_opp_progress = None

        # Employee blob system
        self.employee_blobs = []  # List of employee blob objects with positions and states
        self.sound_manager = SoundManager()  # Sound system
        
        # For hover/tooltip (which upgrade is hovered)
        self.hovered_upgrade_idx = None

        # Scrollable event log feature
        self.scrollable_event_log_enabled = False
        self.event_log_history = []  # Full history of all messages
        self.event_log_scroll_offset = 0

        # Copy modular content
        self.actions = [dict(a) for a in ACTIONS]
        self.events = [dict(e) for e in EVENTS]
        
        # Initialize game logger
        self.logger = GameLogger(seed, "P(Doom) v3")
        
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
                'animation_progress': 1.0  # Already positioned
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
                'animation_progress': 0.0  # Will animate in
            }
            self.employee_blobs.append(blob)
            
            # Play blob sound effect for new hire
            self.sound_manager.play_blob_sound()
            
    def _remove_employee_blobs(self, count):
        """Remove employee blobs when staff leave"""
        for _ in range(min(count, len(self.employee_blobs))):
            if self.employee_blobs:
                self.employee_blobs.pop()
                
    def _update_employee_productivity(self):
        """Update employee productivity based on compute availability each week"""
        productive_employees = 0
        research_gained = 0
        
        # Reset all employees' compute status
        for blob in self.employee_blobs:
            blob['has_compute'] = False
            blob['productivity'] = 0.0
            
        # Assign compute to employees (1 compute per employee if available)
        compute_assigned = 0
        for blob in self.employee_blobs:
            if compute_assigned < self.compute:
                blob['has_compute'] = True
                blob['productivity'] = 1.0
                compute_assigned += 1
                productive_employees += 1
                
                # Each productive employee has a chance to contribute to research
                if random.random() < 0.3:  # 30% chance per productive employee
                    research_gained += random.randint(1, 3)
                    
        # Employees without compute suffer penalty
        unproductive_count = len(self.employee_blobs) - productive_employees
        if unproductive_count > 0:
            # Small doom increase for unproductive employees
            doom_penalty = unproductive_count * 0.5
            self._add('doom', int(doom_penalty))
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

    def _spy(self):
        if random.random() < 0.7:
            self.known_opp_progress = self.opp_progress + random.randint(-3, 3)
            self.messages.append(f"Espionage: You estimate opponent progress at {self.known_opp_progress}/100.")
        else:
            self.messages.append("Espionage failed! No new info.")
        return None

    def _espionage_risk(self):
        if random.random() < 0.25:
            self._add('reputation', -2)
            self.messages.append("Espionage scandal! Reputation dropped.")
        elif random.random() < 0.15:
            self._add('doom', 5)
            self.messages.append("Espionage backfired! Doom increased.")
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
        # Place actions as tall buttons on left
        count = len(self.actions)
        base_x = int(w * 0.04)
        base_y = int(h * 0.16)
        width = int(w * 0.32)
        height = int(h * 0.075)
        gap = int(h * 0.025)
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
        # Not purchased: buttons down right
        base_x = int(w*0.63)
        base_y = int(h*0.18)
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
            self.money -= action["cost"]
            # Log the action
            self.logger.log_action(action["name"], action["cost"], self.turn)
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
        self.doom = min(self.max_doom, self.doom + doom_rise)
        self.opp_progress += random.randint(2, 5)

        self.trigger_events()
        self.turn += 1
        
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
        elif self.opp_progress >= 100:
            self.game_over = True
            game_end_reason = "Opponent deployed dangerous AGI"
            self.messages.append("Frontier lab has deployed dangerous AGI. Game over!")
        elif self.staff == 0:
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
        for event in self.events:
            if event["trigger"](self):
                event["effect"](self)
                event_message = f"Event: {event['name']} - {event['desc']}"
                self.messages.append(event_message)
                # Log the event
                self.logger.log_event(event["name"], event["desc"], self.turn)

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

import random
import json
import os
from actions import ACTIONS
from upgrades import UPGRADES
from events import EVENTS
from game_logger import GameLogger

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
            self.staff = max(self.staff + val, 0)
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
        self.money = 300
        self.staff = 2
        self.reputation = 15
        self.doom = 12  # Out of 100
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

        # For hover/tooltip (which upgrade is hovered)
        self.hovered_upgrade_idx = None

        # Copy modular content
        self.actions = [dict(a) for a in ACTIONS]
        self.events = [dict(e) for e in EVENTS]
        
        # Initialize game logger
        self.logger = GameLogger(seed, "P(Doom) v3")

    def _add(self, attr, val):
        if attr == 'doom':
            self.doom = min(max(self.doom + val, 0), self.max_doom)
        elif attr == 'money':
            self.money = max(self.money + val, 0)
        elif attr == 'reputation':
            self.reputation = max(self.reputation + val, 0)
        elif attr == 'staff':
            self.staff = max(self.staff + val, 0)
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

    def _in_rect(self, pt, rect):
        x, y = pt
        rx, ry, rw, rh = rect
        return rx <= x <= rx+rw and ry <= y <= ry+rh

    def end_turn(self):
        # Clear event log at start of turn to show only current-turn events
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

        # Doom rises over time, faster with more staff
        doom_rise = 2 + self.staff // 5 + (1 if self.doom > 60 else 0)
        self.doom = min(self.max_doom, self.doom + doom_rise)
        self.opp_progress += random.randint(2, 5)

        self.trigger_events()
        self.turn += 1

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

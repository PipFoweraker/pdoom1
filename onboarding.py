"""
Onboarding and tutorial system for P(Doom).

This module handles:
- First-time player detection
- Tutorial progression tracking  
- Context-sensitive help triggers
- Tooltip and help overlay management
"""

import json
import os
from typing import Dict, List, Optional, Set

ONBOARDING_FILE = "onboarding_progress.json"

class OnboardingSystem:
    """Manages onboarding state and tutorial progression."""
    
    def __init__(self):
        """Initialize onboarding system and load existing progress."""
        self.progress = self._load_progress()
        self.tutorial_enabled = self.progress.get('tutorial_enabled', True)
        self.is_first_time = self.progress.get('is_first_time', True)
        self.completed_steps = set(self.progress.get('completed_steps', []))
        self.seen_mechanics = set(self.progress.get('seen_mechanics', []))
        self.tutorial_dismissed = self.progress.get('tutorial_dismissed', False)
        
        # Current tutorial state
        self.current_tutorial_step = None
        self.current_step_index = 0
        self.show_tutorial_overlay = False
        self.pending_tooltips = []
        
        # Stepwise tutorial state
        self.revealed_elements = set()  # Track which UI elements are visible
        self.tutorial_navigation_history = []  # For back button functionality
        
    def _load_progress(self) -> Dict:
        """Load onboarding progress from file."""
        try:
            if os.path.exists(ONBOARDING_FILE):
                with open(ONBOARDING_FILE, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {}
    
    def _save_progress(self):
        """Save current onboarding progress to file."""
        progress_data = {
            'tutorial_enabled': self.tutorial_enabled,
            'is_first_time': self.is_first_time,
            'completed_steps': list(self.completed_steps),
            'seen_mechanics': list(self.seen_mechanics),
            'tutorial_dismissed': self.tutorial_dismissed
        }
        try:
            with open(ONBOARDING_FILE, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception:
            pass  # Silently fail if we can't save
    
    def should_show_tutorial(self) -> bool:
        """Check if tutorial should be shown."""
        return (self.tutorial_enabled and 
                self.is_first_time and 
                not self.tutorial_dismissed)
    
    def start_tutorial(self):
        """Start the tutorial sequence (using new stepwise system)."""
        self.start_stepwise_tutorial()
    
    def start_stepwise_tutorial(self):
        """Start the new stepwise tutorial sequence."""
        if self.should_show_tutorial():
            self.show_tutorial_overlay = True
            self.current_step_index = 0
            self.revealed_elements = set()
            self.tutorial_navigation_history = []
            tutorial_sequence = self.get_stepwise_tutorial_sequence()
            if tutorial_sequence:
                self.current_tutorial_step = tutorial_sequence[0]['id']
                self._reveal_current_step_elements()
    
    def advance_stepwise_tutorial(self):
        """Advance to the next step in the stepwise tutorial."""
        tutorial_sequence = self.get_stepwise_tutorial_sequence()
        
        # Save current state to history for back navigation
        self.tutorial_navigation_history.append({
            'step_index': self.current_step_index,
            'revealed_elements': self.revealed_elements.copy()
        })
        
        self.current_step_index += 1
        
        if self.current_step_index >= len(tutorial_sequence):
            self.complete_tutorial()
            return
        
        current_step = tutorial_sequence[self.current_step_index]
        self.current_tutorial_step = current_step['id']
        self._reveal_current_step_elements()
        
        # Mark step as completed
        self.completed_steps.add(current_step['id'])
        self._save_progress()
    
    def go_back_stepwise_tutorial(self):
        """Go back to the previous step in the stepwise tutorial."""
        if not self.tutorial_navigation_history:
            return  # Can't go back from first step
        
        # Restore previous state
        previous_state = self.tutorial_navigation_history.pop()
        self.current_step_index = previous_state['step_index']
        self.revealed_elements = previous_state['revealed_elements']
        
        tutorial_sequence = self.get_stepwise_tutorial_sequence()
        if self.current_step_index < len(tutorial_sequence):
            current_step = tutorial_sequence[self.current_step_index]
            self.current_tutorial_step = current_step['id']
    
    def _reveal_current_step_elements(self):
        """Reveal UI elements for the current tutorial step."""
        tutorial_sequence = self.get_stepwise_tutorial_sequence()
        if self.current_step_index < len(tutorial_sequence):
            current_step = tutorial_sequence[self.current_step_index]
            
            # Add new elements to revealed set
            for element in current_step['reveal_elements']:
                if element == 'all_elements':
                    # Special case: reveal everything
                    all_elements = [
                        'money_display', 'staff_display', 'doom_display', 'reputation_display',
                        'action_points_display', 'actions_panel', 'hire_staff_action',
                        'research_action', 'safety_action', 'upgrades_panel', 'first_upgrade',
                        'activity_log', 'end_turn_button', 'opponents_info'
                    ]
                    self.revealed_elements.update(all_elements)
                else:
                    self.revealed_elements.add(element)
    
    def should_show_ui_element(self, element_id: str) -> bool:
        """Check if a UI element should be visible based on tutorial progress."""
        if not self.show_tutorial_overlay:
            return True  # Show all elements when tutorial is not active
        
        return element_id in self.revealed_elements
    
    def get_current_stepwise_tutorial_data(self) -> Optional[Dict]:
        """Get data for the current stepwise tutorial step."""
        if not self.show_tutorial_overlay:
            return None
        
        tutorial_sequence = self.get_stepwise_tutorial_sequence()
        if self.current_step_index < len(tutorial_sequence):
            step_data = tutorial_sequence[self.current_step_index]
            
            # Add navigation info
            step_data['can_go_back'] = len(self.tutorial_navigation_history) > 0
            step_data['can_go_forward'] = self.current_step_index < len(tutorial_sequence) - 1
            step_data['step_number'] = self.current_step_index + 1
            step_data['total_steps'] = len(tutorial_sequence)
            
            return step_data
        
        return None
    
    def complete_tutorial(self):
        """Mark tutorial as completed."""
        self.show_tutorial_overlay = False
        self.current_tutorial_step = None
        self.is_first_time = False
        self._save_progress()
    
    def dismiss_tutorial(self):
        """Allow user to dismiss/skip tutorial."""
        self.tutorial_dismissed = True
        self.show_tutorial_overlay = False
        self.current_tutorial_step = None
        self._save_progress()
    
    def enable_tutorial(self, enabled: bool):
        """Enable or disable tutorial system."""
        self.tutorial_enabled = enabled
        self._save_progress()
    
    def mark_mechanic_seen(self, mechanic: str):
        """Mark a game mechanic as seen (for first-time help)."""
        if mechanic not in self.seen_mechanics:
            self.seen_mechanics.add(mechanic)
            self._save_progress()
            return True  # First time seeing this mechanic
        return False
    
    def should_show_mechanic_help(self, mechanic: str) -> bool:
        """Check if first-time help should be shown for a mechanic."""
        return (self.tutorial_enabled and 
                mechanic not in self.seen_mechanics)
    
    def get_mechanic_help(self, mechanic: str) -> Optional[Dict]:
        """
        Get help content for a specific game mechanic.
        
        Args:
            mechanic: The mechanic name to get help for
            
        Returns:
            Dict with 'title' and 'content' keys for valid mechanics, None for invalid ones
            
        Note: This is currently a stub implementation. Consider adding more comprehensive
        help content and removing the warning when fully implemented.
        """
        import logging
        
        # Log warning as requested for stub implementation
        logging.warning(f"get_mechanic_help called for mechanic: {mechanic}. This is a stub implementation.")
        
        # Handle invalid inputs gracefully
        if not isinstance(mechanic, str) or not mechanic:
            return None
        
        # Define help content for core mechanics
        mechanic_help = {
            'first_staff_hire': {
                'title': 'Hiring Your First Staff Member',
                'content': 'Great choice! Hiring staff increases your action points per turn, allowing you to take more actions. Each staff member you hire gives you one additional action point. More staff means faster progress, but it also costs money each turn for salaries.'
            },
            'first_upgrade_purchase': {
                'title': 'Your First Laboratory Upgrade',
                'content': 'Excellent! Lab upgrades improve your research efficiency and capabilities. Some upgrades reduce research costs, others unlock new research options, and some provide safety improvements. Choose upgrades that align with your strategy.'
            },
            'action_points_exhausted': {
                'title': 'No Action Points Remaining',
                'content': 'You\'ve used all your action points for this turn. Click "End Turn" to proceed to the next turn, where your action points will be refreshed. Consider hiring more staff to get additional action points per turn.'
            },
            'high_doom_warning': {
                'title': 'Warning: High P(Doom)',
                'content': 'Your probability of doom is getting dangerously high! Focus on safety research and avoid risky projects. If P(Doom) reaches 100%, the game ends. Consider taking safety measures or upgrading your containment protocols.'
            }
        }
        
        return mechanic_help.get(mechanic)
    
    def get_stepwise_tutorial_sequence(self):
        """Get the complete stepwise tutorial sequence with UI element visibility control."""
        return [
            {
                'id': 'welcome',
                'title': 'Welcome to P(Doom)!',
                'content': 'Welcome to P(Doom), a strategy game about managing an AI safety lab! This tutorial will introduce each part of the interface step by step.',
                'reveal_elements': [],  # No UI elements revealed yet
                'focus_area': None
            },
            {
                'id': 'money_display',
                'title': 'Your Money',
                'content': 'This shows your current funds. You start with $1,000. You\'ll need money to hire staff and purchase upgrades.',
                'reveal_elements': ['money_display'],
                'focus_area': 'top_panel'
            },
            {
                'id': 'staff_display',
                'title': 'Your Staff',
                'content': 'This shows your current team size. You start with 2 staff members. More staff = more action points!',
                'reveal_elements': ['staff_display'],
                'focus_area': 'top_panel'
            },
            {
                'id': 'doom_display',
                'title': 'P(Doom) Meter',
                'content': 'This critical meter shows the probability of doom. Keep this low! High doom leads to game over.',
                'reveal_elements': ['doom_display'],
                'focus_area': 'top_panel'
            },
            {
                'id': 'reputation_display',
                'title': 'Your Reputation',
                'content': 'Reputation affects funding opportunities and public trust. Balance reputation with progress.',
                'reveal_elements': ['reputation_display'],
                'focus_area': 'top_panel'
            },
            {
                'id': 'action_points_display',
                'title': 'Action Points',
                'content': 'Action Points (AP) limit how many actions you can take per turn. You start with 3 AP per turn.',
                'reveal_elements': ['action_points_display'],
                'focus_area': 'top_panel'
            },
            {
                'id': 'actions_panel',
                'title': 'Actions Panel',
                'content': 'Here you\'ll take actions like hiring staff, conducting research, and improving safety.',
                'reveal_elements': ['actions_panel'],
                'focus_area': 'left_panel'
            },
            {
                'id': 'hire_staff_action',
                'title': 'Hire Staff Action',
                'content': 'This action lets you hire new team members. More staff means more action points per turn!',
                'reveal_elements': ['hire_staff_action'],
                'focus_area': 'left_panel'
            },
            {
                'id': 'research_action',
                'title': 'Conduct Research',
                'content': 'Research advances your capabilities but may increase p(Doom). Choose research carefully.',
                'reveal_elements': ['research_action'],
                'focus_area': 'left_panel'
            },
            {
                'id': 'safety_action',
                'title': 'Safety Measures',
                'content': 'Safety actions help reduce p(Doom). Balance progress with caution.',
                'reveal_elements': ['safety_action'],
                'focus_area': 'left_panel'
            },
            {
                'id': 'upgrades_panel',
                'title': 'Upgrades Panel',
                'content': 'Purchase upgrades to improve your lab\'s capabilities and efficiency.',
                'reveal_elements': ['upgrades_panel'],
                'focus_area': 'right_panel'
            },
            {
                'id': 'first_upgrade',
                'title': 'Lab Equipment',
                'content': 'Your first upgrade! Lab equipment improves research efficiency.',
                'reveal_elements': ['first_upgrade'],
                'focus_area': 'right_panel'
            },
            {
                'id': 'activity_log',
                'title': 'Activity Log',
                'content': 'This log shows what happens each turn. Keep an eye on events and results here.',
                'reveal_elements': ['activity_log'],
                'focus_area': 'center_panel'
            },
            {
                'id': 'end_turn_button',
                'title': 'End Turn Button',
                'content': 'Click here when you\'re done taking actions. This advances time and triggers events.',
                'reveal_elements': ['end_turn_button'],
                'focus_area': 'bottom_panel'
            },
            {
                'id': 'opponents_info',
                'title': 'Competitor Labs',
                'content': 'Other labs are also working on AI. Monitor their progress and try to stay ahead!',
                'reveal_elements': ['opponents_info'],
                'focus_area': 'bottom_panel'
            },
            {
                'id': 'full_interface',
                'title': 'Complete Interface',
                'content': 'Now you can see the full interface! Take some actions, then end your turn to see what happens.',
                'reveal_elements': ['all_elements'],
                'focus_area': None
            },
            {
                'id': 'tutorial_complete',
                'title': 'Tutorial Complete!',
                'content': 'You\'re ready to manage your AI safety lab! Remember: balance progress with caution, and keep p(Doom) low. Good luck!',
                'reveal_elements': ['all_elements'],
                'focus_area': None
            }
        ]
        self.show_tutorial_overlay = False
        self.current_tutorial_step = None
        self._save_progress()

# Global onboarding instance
onboarding = OnboardingSystem()
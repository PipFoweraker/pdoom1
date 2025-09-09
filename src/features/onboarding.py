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
            
        Note: This implementation is defensive to prevent any crashes that could prevent game launch.
        """
        try:
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
            
        except Exception as e:
            # Defensive coding: never let onboarding system crash the game
            try:
                import logging
                logging.error(f"Error in get_mechanic_help for mechanic '{mechanic}': {e}")
            except:
                pass  # Even logging errors shouldn't crash
            return None  # Return None to gracefully handle any errors
    
    def add_tooltip(self, message: str, priority: int = 1):
        """
        Add a tooltip to the pending tooltip queue.
        
        Args:
            message: The tooltip message to display
            priority: Priority level (higher number = higher priority)
        """
        import logging
        logging.warning(f"add_tooltip called with message: {message}, priority: {priority}. This is a stub implementation.")
        
        self.pending_tooltips.append({
            'message': message,
            'priority': priority
        })
        # Sort by priority (highest first)
        self.pending_tooltips.sort(key=lambda x: x['priority'], reverse=True)
    
    def get_next_tooltip(self) -> Optional[str]:
        """
        Get the next tooltip message from the queue.
        
        Returns:
            The next tooltip message or None if queue is empty
        """
        if self.pending_tooltips:
            return self.pending_tooltips.pop(0)['message']
        return None
    
    def clear_tooltips(self):
        """Clear all pending tooltips."""
        self.pending_tooltips.clear()
    
    def get_tutorial_content(self, step_id: str) -> Optional[Dict]:
        """
        Get tutorial content for a specific step.
        
        Args:
            step_id: The tutorial step identifier
            
        Returns:
            Dict with tutorial content or None if step not found
        """
        import logging
        logging.warning(f"get_tutorial_content called for step: {step_id}. This is a stub implementation.")
        
        tutorial_content = {
            'welcome': {
                'title': 'Welcome to P(Doom)!',
                'content': 'Welcome to P(Doom), where you manage an AI safety laboratory. Your goal is to advance AI capabilities while keeping the probability of doom low.',
                'next_step': 'resources'
            },
            'resources': {
                'title': 'Understanding Resources',
                'content': 'Monitor your money, staff, reputation, and doom probability. These resources determine what actions you can take.',
                'next_step': 'actions'
            },
            'actions': {
                'title': 'Taking Actions',
                'content': 'Use the action panel to hire staff, conduct research, implement safety measures, and purchase upgrades.',
                'next_step': 'action_points'
            },
            'action_points': {
                'title': 'Action Points',
                'content': 'Action points limit how many actions you can take per turn. Hire more staff to get more action points.',
                'next_step': 'end_turn'
            },
            'end_turn': {
                'title': 'Ending Your Turn',
                'content': 'Click "End Turn" when you\'re done taking actions. This advances time and triggers events.',
                'next_step': 'events'
            },
            'events': {
                'title': 'Events and Consequences',
                'content': 'Your actions have consequences. Watch the activity log to see what happens as a result of your decisions.',
                'next_step': 'upgrades'
            },
            'upgrades': {
                'title': 'Laboratory Upgrades',
                'content': 'Purchase upgrades to improve your lab\'s capabilities and unlock new strategies.',
                'next_step': 'complete'
            },
            'complete': {
                'title': 'Tutorial Complete!',
                'content': 'You\'re ready to manage your AI safety lab. Remember: balance progress with caution, and keep P(Doom) low!',
                'next_step': None
            }
        }
        
        return tutorial_content.get(step_id)
    
    def advance_tutorial_step(self, current_step: str):
        """
        Advance to the next tutorial step.
        
        Args:
            current_step: The current step being completed
        """
        import logging
        logging.warning(f"advance_tutorial_step called for step: {current_step}. This is a stub implementation.")
        
        # Mark current step as completed
        self.completed_steps.add(current_step)
        
        # Get the next step
        content = self.get_tutorial_content(current_step)
        if content and content.get('next_step'):
            self.current_tutorial_step = content['next_step']
        else:
            # Tutorial is complete
            self.current_tutorial_step = None
            self.complete_tutorial()
        
        self._save_progress()
    
    def get_stepwise_tutorial_sequence(self):
        """Get the complete stepwise tutorial sequence with UI element visibility control."""
        return [
            {
                'id': 'welcome',
                'title': 'Welcome to P(Doom)!',
                'content': 'Welcome to P(Doom), a strategy game about managing an AI safety lab!\n\nYour goal: Advance AI capabilities while keeping the probability of doom low. You compete against reckless frontier labs who prioritize speed over safety.\n\nThis tutorial will introduce the interface progressively. Press S to skip at any time.',
                'reveal_elements': [],  # Start with black screen
                'focus_area': None
            },
            {
                'id': 'resources_overview',
                'title': 'Your Resources',
                'content': 'MONEY: $1,000 starting funds for hiring and upgrades\nSTAFF: 2 team members (more staff = more action points)\nREPUTATION: 50 public trust (affects funding opportunities)\nACTION POINTS: 3 per turn (your main constraint)\nP(DOOM): 25% probability of catastrophic failure (KEEP LOW!)\n\nManage these carefully - they determine your success.',
                'reveal_elements': ['money_display', 'staff_display', 'reputation_display', 'action_points_display', 'doom_display'],
                'focus_area': 'top_panel'
            },
            {
                'id': 'actions_and_strategy',
                'title': 'Actions & Strategy',
                'content': 'ACTIONS PANEL (Left): Take actions to manage your lab\n? Hire Staff: More team = more action points per turn\n? Conduct Research: Advance capabilities (may increase doom)\n? Safety Measures: Reduce p(Doom) and improve reputation\n? Public Relations: Boost reputation and unlock funding\n\nUPGRADES PANEL (Right): Purchase permanent improvements\n? Lab Equipment: Boost research efficiency\n? Security Systems: Reduce risks\n? Better Facilities: More staff capacity\n\nBalance progress with caution!',
                'reveal_elements': ['actions_panel', 'hire_staff_action', 'research_action', 'safety_action', 'upgrades_panel', 'first_upgrade'],
                'focus_area': 'left_right_panels'
            },
            {
                'id': 'game_flow_and_competition',
                'title': 'Game Flow & Competition',
                'content': 'ACTIVITY LOG: Shows your actions and random events\nEND TURN: Advance time and trigger events when ready\nCOMPETITOR LABS: Monitor rival labs\' progress\n\nEach turn:\n1. Spend action points on actions\n2. Check activity log for results\n3. End turn when ready\n4. Random events occur\n5. Competitors advance\n\nWatch p(Doom) carefully - if it hits 100%, you lose!\nPress SPACEBAR to end turns quickly.',
                'reveal_elements': ['activity_log', 'end_turn_button', 'opponents_info'],
                'focus_area': 'bottom_center'
            },
            {
                'id': 'ready_to_play',
                'title': 'Ready to Play!',
                'content': 'You now see the complete interface!\n\nKEY CONTROLS:\n? Numbers 1-9: Quick action selection\n? SPACEBAR: End turn\n? H: Help guide\n? ESC: Pause menu\n\nREMEMBER:\n? Balance speed vs. safety\n? More staff = more action points\n? Keep p(Doom) below 80% (warning thresholds)\n? Watch competitors but don\'t panic\n\nGood luck saving the world!',
                'reveal_elements': ['all_elements'],
                'focus_area': None
            }
        ]
        self.show_tutorial_overlay = False
        self.current_tutorial_step = None
        self._save_progress()

    def are_hints_enabled(self) -> bool:
        """Check if hints are enabled in the current configuration."""
        from src.services.config_manager import get_current_config
        config = get_current_config()
        return config.get('tutorial', {}).get('first_time_help', True)

    def are_tutorials_enabled(self) -> bool:
        """Check if tutorials are enabled in the current configuration."""
        from src.services.config_manager import get_current_config
        config = get_current_config()
        return config.get('tutorial', {}).get('tutorial_enabled', True)

    def reset_all_hints(self):
        """Reset all hints so they will show again (Factorio-style reset)."""
        # Clear all seen mechanics so hints will show again
        self.seen_mechanics.clear()
        self._save_progress()
        
        # Add log message for confirmation
        import logging
        logging.info("All hints reset - they will show again for new actions")

    def reset_specific_hint(self, mechanic: str):
        """Reset a specific hint so it will show again."""
        if mechanic in self.seen_mechanics:
            self.seen_mechanics.remove(mechanic)
            self._save_progress()
            
            # Add log message for confirmation
            import logging
            logging.info(f"Hint '{mechanic}' reset - will show again")

    def get_hint_status(self) -> Dict[str, bool]:
        """Get the status of all available hints."""
        available_mechanics = ['first_staff_hire', 'first_upgrade_purchase', 'action_points_exhausted', 'high_doom_warning']
        return {
            mechanic: mechanic in self.seen_mechanics
            for mechanic in available_mechanics
        }

    def should_show_hint(self, mechanic: str) -> bool:
        """
        Check if a hint should be shown (Factorio-style behavior).
        
        Returns True if:
        1. Hints are enabled in config
        2. This specific hint hasn't been seen before
        """
        return (self.are_hints_enabled() and 
                self.should_show_mechanic_help(mechanic))

# Global onboarding instance
onboarding = OnboardingSystem()
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
        self.show_tutorial_overlay = False
        self.pending_tooltips = []
        
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
        """Start the tutorial sequence."""
        if self.should_show_tutorial():
            self.show_tutorial_overlay = True
            self.current_tutorial_step = 'welcome'
    
    def advance_tutorial_step(self, step_id: str):
        """Advance to the next tutorial step."""
        if step_id in self.completed_steps:
            return
            
        self.completed_steps.add(step_id)
        self._save_progress()
        
        # Determine next step
        tutorial_sequence = [
            'welcome',
            'resources',
            'actions', 
            'action_points',
            'end_turn',
            'events',
            'upgrades',
            'complete'
        ]
        
        try:
            current_index = tutorial_sequence.index(step_id)
            if current_index < len(tutorial_sequence) - 1:
                self.current_tutorial_step = tutorial_sequence[current_index + 1]
            else:
                self.complete_tutorial()
        except ValueError:
            pass
    
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
    
    def get_tutorial_content(self, step_id: str) -> Dict:
        """Get tutorial content for a specific step."""
        tutorial_content = {
            'welcome': {
                'title': 'Welcome to P(Doom)!',
                'content': """Welcome to P(Doom), a strategy game about managing an AI safety lab!

Your goal is to navigate the challenges of AI development while keeping the probability of doom (p(Doom)) as low as possible.

Let's walk through the basics:

• Monitor your resources in the top panel
• Take actions using the left panel  
• Purchase upgrades in the right panel
• End your turn and handle events

Click 'Next' to learn about your resources, or 'Skip' to start playing immediately.""",
                'next_step': 'resources'
            },
            'resources': {
                'title': 'Understanding Your Resources',
                'content': """Your lab has several key resources to manage:

💰 **Money**: Used for actions and upgrades
👥 **Staff**: Your team (costs money each turn)
⭐ **Reputation**: Affects fundraising and events  
⚡ **Action Points (AP)**: Limits actions per turn (starts at 3)
☢️ **p(Doom)**: AI catastrophe risk (game over at 100%)
🖥️ **Compute**: Powers research and productivity

Keep an eye on these resources - they'll determine your success!""",
                'next_step': 'actions'
            },
            'actions': {
                'title': 'Taking Actions',
                'content': """The left panel shows available actions you can take:

• **Fundraise**: Gain money based on reputation
• **Hire Staff**: Expand your team
• **Safety Research**: Reduce p(Doom) risk
• **Buy Compute**: Increase computational resources
• **Espionage**: Learn about competitors

Each action costs Action Points (AP) and may cost money.
You start with 3 AP per turn, but can gain more by hiring staff!""",
                'next_step': 'action_points'
            },
            'action_points': {
                'title': 'Action Points System',
                'content': """Action Points (AP) are crucial for strategy:

• You start with 3 AP per turn
• Each action costs 1-3 AP (shown on buttons)
• Regular staff give +0.5 AP each
• Admin assistants give +1.0 AP each
• Specialized staff can delegate certain actions

Plan your actions carefully - you can't take more actions than you have AP!""",
                'next_step': 'end_turn'
            },
            'end_turn': {
                'title': 'Ending Your Turn',
                'content': """When you're ready to proceed:

• Click 'END TURN' or press Spacebar
• Pay staff maintenance costs
• Handle any random events
• Your AP will reset for the next turn

Events can be opportunities or challenges. Some can be deferred for strategic timing!""",
                'next_step': 'events'
            },
            'events': {
                'title': 'Events and Milestones',
                'content': """Random events will test your decision-making:

• **Normal Events**: Immediate effects
• **Popup Events**: Critical situations requiring choice
• **Deferred Events**: Can postpone for strategic timing

Watch for milestone events as your lab grows:
• Manager hiring at 9+ employees
• Board oversight at high spending
• Enhanced event system unlocks over time""",
                'next_step': 'upgrades'
            },
            'upgrades': {
                'title': 'Upgrades and Growth',
                'content': """The right panel shows permanent upgrades:

• **Accounting Software**: Track cash flow
• **Compact Activity Display**: Better UI
• **Research Stations**: Boost productivity
• **Security Systems**: Reduce risks

Upgrades are one-time purchases that provide lasting benefits.
Choose upgrades that match your strategy!""",
                'next_step': 'complete'
            },
            'complete': {
                'title': 'Ready to Begin!',
                'content': """You're ready to manage your AI safety lab!

**Remember:**
• Balance resources carefully
• Plan your AP usage strategically  
• Adapt to events and opportunities
• Keep p(Doom) as low as possible

**Getting Help:**
• Press 'H' anytime for help
• Hover over buttons for tooltips
• Check the Player Guide in the main menu

Good luck, and try to save humanity!""",
                'next_step': None
            }
        }
        
        return tutorial_content.get(step_id, {
            'title': 'Tutorial Step',
            'content': f'Tutorial content for {step_id}',
            'next_step': None
        })
    
    def get_mechanic_help(self, mechanic: str) -> Optional[Dict]:
        """Get first-time help content for a specific mechanic."""
        mechanic_help = {
            'first_staff_hire': {
                'title': 'Staff Management',
                'content': 'Great! You hired your first staff member. Staff cost money each turn but provide +0.5 Action Points. Manage your team size carefully!'
            },
            'first_upgrade_purchase': {
                'title': 'Upgrade Purchased',
                'content': 'Excellent! Upgrades provide permanent benefits. This upgrade will help you throughout the game.'
            },
            'first_event': {
                'title': 'Event Occurred',
                'content': 'Events happen randomly and present choices. Consider the consequences carefully - some events can be deferred for better timing!'
            },
            'first_milestone': {
                'title': 'Milestone Reached',
                'content': 'You\'ve reached a milestone! These unlock new mechanics and challenges as your organization grows.'
            },
            'action_points_exhausted': {
                'title': 'Out of Action Points',
                'content': 'You\'ve used all your Action Points for this turn. Hire more staff to increase your AP for future turns!'
            },
            'high_doom_warning': {
                'title': 'High p(Doom) Warning',
                'content': 'Your p(Doom) is getting dangerously high! Focus on Safety Research and careful decision-making to reduce the risk.'
            }
        }
        
        return mechanic_help.get(mechanic)
    
    def add_tooltip(self, text: str, priority: int = 1):
        """Add a tooltip to be shown."""
        self.pending_tooltips.append({
            'text': text,
            'priority': priority,
            'shown': False
        })
    
    def get_next_tooltip(self) -> Optional[str]:
        """Get the next tooltip to show."""
        if not self.pending_tooltips:
            return None
            
        # Sort by priority and return highest priority unshown tooltip
        self.pending_tooltips.sort(key=lambda x: x['priority'], reverse=True)
        for tooltip in self.pending_tooltips:
            if not tooltip['shown']:
                tooltip['shown'] = True
                return tooltip['text']
        
        return None
    
    def clear_tooltips(self):
        """Clear all pending tooltips."""
        self.pending_tooltips.clear()

# Global onboarding instance
onboarding = OnboardingSystem()
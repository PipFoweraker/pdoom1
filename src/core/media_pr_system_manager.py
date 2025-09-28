"""
Media & PR System Manager - Handles media operations, public relations, and communication strategy.

This module extracts media and public relations functionality from the main GameState class,
providing a focused interface for all media operations and communication management.

Key functionality:
- Media dialog system for operation selection
- Press releases and public statements  
- Exclusive interviews and media engagement
- Crisis management and damage control
- Social media campaigns and community outreach
"""

from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game_state import GameState


class MediaPRSystemManager:
    """Manages all media and public relations operations."""
    
    def __init__(self, game_state: 'GameState') -> None:
        """Initialize the media & PR system manager.
        
        Args:
            game_state: Reference to the main game state for accessing game data
        """
        self.game_state = game_state
    
    def trigger_media_dialog(self) -> None:
        """Trigger the media & PR dialog with available communication options."""
        media_options = []
        
        # Press Release
        media_options.append({
            "id": "press_release",
            "name": "Press Release",
            "description": "Issue official press release to announce achievements or respond to events.",
            "cost": 100,
            "ap_cost": 1,
            "available": True,
            "details": "Controlled messaging to media outlets for reputation management."
        })
        
        # Exclusive Interview
        media_options.append({
            "id": "exclusive_interview",
            "name": "Exclusive Interview", 
            "description": "Grant exclusive interview to major media outlet for deep coverage.",
            "cost": 150,
            "ap_cost": 2,
            "available": self.game_state.reputation >= 10,  # Need some reputation for interviews
            "details": f"Requires 10+ reputation (current: {self.game_state.reputation}). High-impact media engagement."
        })
        
        # Damage Control (Crisis Response)
        media_options.append({
            "id": "damage_control",
            "name": "Damage Control (Crisis Response)",
            "description": "Rapid response to negative publicity or crisis situations.",
            "cost": 200,
            "ap_cost": 1,
            "available": True,
            "details": "Emergency PR response for reputation recovery and crisis management."
        })
        
        # Social Media Campaign
        media_options.append({
            "id": "social_media_campaign",
            "name": "Social Media Campaign",
            "description": "Launch coordinated social media campaign to build public awareness.",
            "cost": 75,
            "ap_cost": 1,
            "available": True,
            "details": "Digital outreach campaign for community engagement and reputation building."
        })
        
        # Public Statement
        media_options.append({
            "id": "public_statement",
            "name": "Public Statement",
            "description": "Make formal public statement on AI safety position or industry developments.",
            "cost": 50,
            "ap_cost": 1,
            "available": True,
            "details": "Official position statement for thought leadership and transparency."
        })
        
        self.game_state.pending_media_dialog = {
            "options": media_options,
            "title": "Media & PR Operations",
            "description": "Select a media and public relations operation to execute."
        }
    
    def select_media_option(self, option_id: str) -> Tuple[bool, str]:
        """Handle player selection of a media & PR option."""
        if not self.game_state.pending_media_dialog:
            return False, "No media dialog active."
        
        # Find the selected option
        selected_option = None
        for option in self.game_state.pending_media_dialog["options"]:
            if option["id"] == option_id:
                selected_option = option
                break
        
        if not selected_option:
            return False, f"Invalid media option: {option_id}"
        
        if not selected_option["available"]:
            return False, f"Media option not available: {selected_option['name']}"
        
        # Check costs
        if self.game_state.money < selected_option["cost"]:
            return False, f"Insufficient funds. Need ${selected_option['cost']}, have ${self.game_state.money}."
        
        if self.game_state.action_points < selected_option["ap_cost"]:
            return False, f"Insufficient action points. Need {selected_option['ap_cost']}, have {self.game_state.action_points}."
        
        # Execute the selected media option
        if option_id == "press_release":
            # Deduct costs
            self.game_state.money -= selected_option["cost"]
            self.game_state.action_points -= selected_option["ap_cost"]
            
            # Execute press release functionality
            self._press_release()
            
        elif option_id == "exclusive_interview":
            # Deduct costs
            self.game_state.money -= selected_option["cost"]
            self.game_state.action_points -= selected_option["ap_cost"]
            
            # Execute exclusive interview functionality
            self._exclusive_interview()
            
        elif option_id == "damage_control":
            # Deduct costs
            self.game_state.money -= selected_option["cost"]
            self.game_state.action_points -= selected_option["ap_cost"]
            
            # Execute damage control functionality
            self._damage_control()
            
        elif option_id == "social_media_campaign":
            # Deduct costs
            self.game_state.money -= selected_option["cost"]
            self.game_state.action_points -= selected_option["ap_cost"]
            
            # Execute social media campaign functionality
            self._social_media_campaign()
            
        elif option_id == "public_statement":
            # Deduct costs
            self.game_state.money -= selected_option["cost"]
            self.game_state.action_points -= selected_option["ap_cost"]
            
            # Execute public statement functionality
            self._public_statement()
            
        else:
            return False, f"Unknown media option: {option_id}"
        
        # Clear the media dialog
        self.game_state.pending_media_dialog = None
        return True, "Media & PR operation complete."
    
    def _press_release(self) -> None:
        """Execute press release operation - controlled messaging to media outlets."""
        # TODO: Implement press release mechanics
        # - Reputation improvement based on current achievements
        # - Public awareness increase
        # - Potential media coverage events
        self.game_state.messages.append("Press release issued! Media outlets reporting on lab developments.")
        # Placeholder: Small reputation boost
        self.game_state.reputation += 2
        self.game_state.messages.append("Reputation improved through controlled messaging.")
    
    def _exclusive_interview(self) -> None:
        """Execute exclusive interview operation - high-impact media engagement."""
        # TODO: Implement exclusive interview mechanics
        # - Major reputation boost for high-reputation labs
        # - Detailed coverage of AI safety position
        # - Potential industry influence increase
        self.game_state.messages.append("Exclusive interview granted! Major media coverage secured.")
        # Placeholder: Significant reputation boost for established labs
        reputation_gain = 5 if self.game_state.reputation >= 20 else 3
        self.game_state.reputation += reputation_gain
        self.game_state.messages.append(f"Reputation significantly improved through media engagement (+{reputation_gain}).")
    
    def _damage_control(self) -> None:
        """Execute damage control operation - crisis response and reputation recovery."""
        # TODO: Implement damage control mechanics
        # - Reputation recovery after negative events
        # - Crisis mitigation strategies
        # - Public reassurance messaging
        self.game_state.messages.append("Damage control activated! Crisis response team deployed.")
        # Placeholder: Reputation stabilization (reduce negative effects)
        if self.game_state.reputation < 50:
            self.game_state.reputation += 3
            self.game_state.messages.append("Crisis management efforts showing positive results (+3 reputation).")
        else:
            self.game_state.messages.append("Preventive PR measures implemented to maintain reputation.")
    
    def _social_media_campaign(self) -> None:
        """Execute social media campaign operation - community engagement and awareness."""
        # TODO: Implement social media campaign mechanics
        # - Community engagement increase
        # - Public awareness of AI safety mission
        # - Potential talent recruitment boost
        self.game_state.messages.append("Social media campaign launched! Digital engagement increasing.")
        # Placeholder: Modest reputation boost and community engagement
        self.game_state.reputation += 1
        self.game_state.messages.append("Online community engagement improved (+1 reputation).")
    
    def _public_statement(self) -> None:
        """Execute public statement operation - thought leadership and transparency."""
        # TODO: Implement public statement mechanics
        # - AI safety position clarification
        # - Industry thought leadership
        # - Transparency and trust building
        self.game_state.messages.append("Public statement released! AI safety position clarified.")
        # Placeholder: Small reputation boost for transparency
        self.game_state.reputation += 1
        self.game_state.messages.append("Transparency and thought leadership enhanced (+1 reputation).")
"""
Game State Manager - Clean Game State Transitions

Handles proper initialization, reset, and transition of game states to prevent
end game data from persisting into new games.

Using our "slightly more verbose but clearer" naming approach for better maintainability.
"""

from typing import Optional, Dict, Any
from src.core.game_state import GameState


class GameStateManager:
    """
    Manages game state lifecycle and transitions with clear separation between
    game sessions to prevent state contamination between games.
    """
    
    def __init__(self):
        self.current_game_state: Optional[GameState] = None
        self.last_game_stats: Optional[Dict[str, Any]] = None
        
    def create_fresh_game_state(self, seed: str) -> GameState:
        """
        Create a completely fresh game state with no contamination from previous games.
        
        Args:
            seed: Game seed for the new game
            
        Returns:
            Clean GameState instance ready for new game
        """
        # Store stats from previous game if it exists
        if self.current_game_state and self.current_game_state.game_over:
            self.last_game_stats = self._extract_game_completion_stats(self.current_game_state)
        
        # Create completely fresh game state
        self.current_game_state = GameState(seed)
        
        return self.current_game_state
    
    def restart_game_with_same_seed(self) -> GameState:
        """
        Restart current game with the same seed but fresh state.
        
        Returns:
            Clean GameState instance with same seed as previous game
            
        Raises:
            ValueError: If no current game exists to restart
        """
        if not self.current_game_state:
            raise ValueError("Cannot restart game - no current game state exists")
            
        current_seed = self.current_game_state.seed
        return self.create_fresh_game_state(current_seed)
    
    def get_current_game_state(self) -> Optional[GameState]:
        """Get the current active game state."""
        return self.current_game_state
    
    def is_game_in_progress(self) -> bool:
        """Check if there's an active game that's not finished."""
        return (self.current_game_state is not None and 
                not getattr(self.current_game_state, 'game_over', True))
    
    def is_game_finished(self) -> bool:
        """Check if current game is finished/ended."""
        return (self.current_game_state is not None and 
                getattr(self.current_game_state, 'game_over', False))
    
    def get_last_game_completion_stats(self) -> Optional[Dict[str, Any]]:
        """Get stats from the last completed game."""
        return self.last_game_stats
    
    def _extract_game_completion_stats(self, game_state: GameState) -> Dict[str, Any]:
        """
        Extract key stats from a completed game for reference.
        
        Args:
            game_state: Finished game state to extract stats from
            
        Returns:
            Dictionary of key completion statistics
        """
        return {
            'seed': game_state.seed,
            'final_turn': game_state.turn,
            'final_money': game_state.money,
            'final_staff': game_state.staff,
            'final_reputation': game_state.reputation,
            'final_doom': game_state.doom,
            'research_progress': game_state.research_progress,
            'papers_published': game_state.papers_published,
            'end_game_scenario': getattr(game_state, 'end_game_scenario', None),
            'completion_timestamp': getattr(game_state, 'game_over_timestamp', None)
        }


# Global game state manager instance
game_state_manager = GameStateManager()


def get_game_state_manager() -> GameStateManager:
    """Get the global game state manager instance."""
    return game_state_manager

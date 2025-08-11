"""
Local leaderboard storage for PDoom1.

Provides versioned JSON leaderboard with atomic writes and score sorting.
Maintains top scores locally with optional player names.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ..services.data_paths import get_leaderboard_file


class ScoreEntry:
    """Represents a single score entry."""
    
    def __init__(self, 
                 score: int,
                 player_name: str = "Anonymous",
                 date: Optional[datetime] = None,
                 level_reached: int = 1,
                 game_mode: str = "normal",
                 duration_seconds: float = 0.0,
                 entry_uuid: Optional[str] = None):
        """
        Initialize a score entry.
        
        Args:
            score: Final score achieved
            player_name: Player name (defaults to "Anonymous")
            date: Date achieved (defaults to now)
            level_reached: Highest level reached
            game_mode: Game mode played
            duration_seconds: Time taken to achieve score
            entry_uuid: Unique identifier for this entry
        """
        self.score = score
        self.player_name = player_name
        self.date = date or datetime.now()
        self.level_reached = level_reached
        self.game_mode = game_mode
        self.duration_seconds = duration_seconds
        self.entry_uuid = entry_uuid or str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score,
            "player_name": self.player_name,
            "date": self.date.isoformat(),
            "level_reached": self.level_reached,
            "game_mode": self.game_mode,
            "duration_seconds": self.duration_seconds,
            "entry_uuid": self.entry_uuid
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScoreEntry":
        """Create ScoreEntry from dictionary."""
        return cls(
            score=data["score"],
            player_name=data.get("player_name", "Anonymous"),
            date=datetime.fromisoformat(data["date"]),
            level_reached=data.get("level_reached", 1),
            game_mode=data.get("game_mode", "normal"),
            duration_seconds=data.get("duration_seconds", 0.0),
            entry_uuid=data.get("entry_uuid")
        )
    
    def __str__(self) -> str:
        """String representation of the score entry."""
        return f"{self.player_name}: {self.score} (Level {self.level_reached})"
    
    def __lt__(self, other: "ScoreEntry") -> bool:
        """Compare scores for sorting (higher scores come first)."""
        return self.score > other.score


class LocalLeaderboard:
    """
    Local leaderboard with persistent JSON storage.
    
    Features:
    - Versioned JSON schema for forward compatibility
    - Atomic writes to prevent corruption
    - Configurable maximum number of entries
    - Score sorting and ranking
    - Game mode filtering
    """
    
    CURRENT_VERSION = "1.0.0"
    DEFAULT_MAX_ENTRIES = 100
    
    def __init__(self, 
                 leaderboard_file: Optional[Path] = None,
                 max_entries: int = DEFAULT_MAX_ENTRIES):
        """
        Initialize local leaderboard.
        
        Args:
            leaderboard_file: Custom path to leaderboard file
            max_entries: Maximum number of entries to keep
        """
        self.leaderboard_file = leaderboard_file or get_leaderboard_file()
        self.max_entries = max_entries
        self.entries: List[ScoreEntry] = []
        
        self._load_leaderboard()
    
    def _load_leaderboard(self) -> None:
        """Load leaderboard from file or create empty one."""
        if not self.leaderboard_file.exists():
            self._create_empty_leaderboard()
            return
        
        try:
            with open(self.leaderboard_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate version
            version = data.get("version", "0.0.0")
            if version != self.CURRENT_VERSION:
                data = self._migrate_leaderboard(data)
            
            # Load entries
            self.entries = [
                ScoreEntry.from_dict(entry_data)
                for entry_data in data.get("entries", [])
            ]
            
            # Sort by score (highest first)
            self.entries.sort()
            
        except (json.JSONDecodeError, KeyError, ValueError, IOError) as e:
            print(f"Warning: Invalid leaderboard file, creating new one. Error: {e}")
            self._create_empty_leaderboard()
    
    def _create_empty_leaderboard(self) -> None:
        """Create an empty leaderboard."""
        self.entries = []
        self._save_leaderboard()
    
    def _migrate_leaderboard(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate leaderboard from older versions."""
        # For now, just update version
        data["version"] = self.CURRENT_VERSION
        return data
    
    def _save_leaderboard(self) -> None:
        """Atomically save leaderboard to file."""
        leaderboard_data = {
            "version": self.CURRENT_VERSION,
            "created": datetime.now().isoformat(),
            "max_entries": self.max_entries,
            "entries": [entry.to_dict() for entry in self.entries]
        }
        
        # Atomic write
        temp_file = self.leaderboard_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(leaderboard_data, f, indent=2, ensure_ascii=False)
            
            # Atomic move (platform-specific)
            if os.name == 'nt':  # Windows
                if self.leaderboard_file.exists():
                    os.remove(self.leaderboard_file)
                os.rename(temp_file, self.leaderboard_file)
            else:  # Unix-like systems
                os.rename(temp_file, self.leaderboard_file)
                
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                os.remove(temp_file)
            raise e
    
    def add_score(self, score_entry: ScoreEntry) -> Tuple[bool, int]:
        """
        Add a score to the leaderboard.
        
        Args:
            score_entry: ScoreEntry to add
            
        Returns:
            Tuple of (was_added, rank) where rank is 1-based (0 if not added)
        """
        # Add the entry
        self.entries.append(score_entry)
        
        # Sort by score (highest first)
        self.entries.sort()
        
        # Find the rank (1-based)
        try:
            rank = self.entries.index(score_entry) + 1
        except ValueError:
            rank = 0
        
        # Limit to max entries
        if len(self.entries) > self.max_entries:
            removed_entries = self.entries[self.max_entries:]
            self.entries = self.entries[:self.max_entries]
            
            # Check if the new entry was removed
            if score_entry in removed_entries:
                return False, 0
        
        # Save to file
        self._save_leaderboard()
        
        return True, rank
    
    def get_top_scores(self, count: int = 10, game_mode: Optional[str] = None) -> List[ScoreEntry]:
        """
        Get top scores from the leaderboard.
        
        Args:
            count: Number of scores to return
            game_mode: Filter by game mode (None for all modes)
            
        Returns:
            List of top ScoreEntry objects
        """
        filtered_entries = self.entries
        
        if game_mode:
            filtered_entries = [
                entry for entry in self.entries 
                if entry.game_mode == game_mode
            ]
        
        return filtered_entries[:count]
    
    def get_rank(self, score: int, game_mode: Optional[str] = None) -> int:
        """
        Get the rank a score would have on the leaderboard.
        
        Args:
            score: Score to check
            game_mode: Filter by game mode (None for all modes)
            
        Returns:
            Rank (1-based, 0 if wouldn't make the leaderboard)
        """
        filtered_entries = self.entries
        
        if game_mode:
            filtered_entries = [
                entry for entry in self.entries 
                if entry.game_mode == game_mode
            ]
        
        # Count how many scores are higher
        higher_scores = sum(1 for entry in filtered_entries if entry.score > score)
        
        # Rank is position + 1 (if it would make the leaderboard)
        rank = higher_scores + 1
        
        # Check if it would make the leaderboard
        if len(filtered_entries) >= self.max_entries and rank > self.max_entries:
            return 0
        
        return rank
    
    def is_high_score(self, score: int, game_mode: Optional[str] = None) -> bool:
        """
        Check if a score would make it to the leaderboard.
        
        Args:
            score: Score to check
            game_mode: Filter by game mode (None for all modes)
            
        Returns:
            True if score would make the leaderboard
        """
        return self.get_rank(score, game_mode) > 0
    
    def get_player_best(self, player_name: str, game_mode: Optional[str] = None) -> Optional[ScoreEntry]:
        """
        Get the best score for a specific player.
        
        Args:
            player_name: Player to search for
            game_mode: Filter by game mode (None for all modes)
            
        Returns:
            Best ScoreEntry for the player, or None if not found
        """
        player_entries = [
            entry for entry in self.entries 
            if entry.player_name == player_name
        ]
        
        if game_mode:
            player_entries = [
                entry for entry in player_entries 
                if entry.game_mode == game_mode
            ]
        
        return player_entries[0] if player_entries else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get leaderboard statistics."""
        if not self.entries:
            return {
                "total_entries": 0,
                "highest_score": 0,
                "average_score": 0,
                "unique_players": 0,
                "game_modes": []
            }
        
        scores = [entry.score for entry in self.entries]
        players = {entry.player_name for entry in self.entries}
        game_modes = {entry.game_mode for entry in self.entries}
        
        return {
            "total_entries": len(self.entries),
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "average_score": sum(scores) / len(scores),
            "unique_players": len(players),
            "game_modes": sorted(list(game_modes))
        }
    
    def clear_leaderboard(self) -> int:
        """
        Clear all entries from the leaderboard.
        
        Returns:
            Number of entries that were cleared
        """
        count = len(self.entries)
        self.entries = []
        self._save_leaderboard()
        return count
    
    def remove_entry(self, entry_uuid: str) -> bool:
        """
        Remove a specific entry by UUID.
        
        Args:
            entry_uuid: UUID of entry to remove
            
        Returns:
            True if entry was found and removed
        """
        for i, entry in enumerate(self.entries):
            if entry.entry_uuid == entry_uuid:
                del self.entries[i]
                self._save_leaderboard()
                return True
        return False
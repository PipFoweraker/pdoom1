"""
Enhanced Leaderboard Manager for P(Doom) v0.4.1+

Provides seed-specific, versioned leaderboards with graceful migration and 
comprehensive game metadata tracking for the bootstrap economic system.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from src.scores.local_store import LocalLeaderboard, ScoreEntry
from src.services.data_paths import get_leaderboard_file
from src.services.version import get_display_version


@dataclass
class GameSession:
    """Represents a complete game session with comprehensive metadata."""
    
    # Core game data
    seed: str
    final_turn: int
    final_score: int
    game_version: str
    economic_model: str
    
    # Session metadata  
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    player_name: str
    
    # Game state at end
    final_money: float
    final_staff: int
    final_reputation: float
    final_doom: float
    final_compute: float
    
    # Economic model stats (v0.4.1+)
    total_staff_maintenance_paid: float
    total_research_spending: float
    total_fundraising_gained: float
    moore_law_savings: float
    
    # Performance metrics
    actions_taken: int
    average_ap_per_turn: float
    research_papers_published: int
    technical_debt_accumulated: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert datetime objects to ISO strings
        result['start_time'] = self.start_time.isoformat()
        result['end_time'] = self.end_time.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        """Create from dictionary, handling datetime parsing."""
        # Parse datetime strings back to datetime objects
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['end_time'] = datetime.fromisoformat(data['end_time'])
        return cls(**data)
    
    def get_config_hash(self) -> str:
        """Generate hash of game configuration for leaderboard segregation."""
        config_string = f"{self.economic_model}_{self.game_version}"
        return hashlib.md5(config_string.encode()).hexdigest()[:8]


class EnhancedLeaderboardManager:
    """
    Manages multiple leaderboards with seed-specific tracking and versioning.
    
    Features:
    - Seed-specific leaderboards with configuration hashing
    - Graceful migration between game versions
    - Bootstrap economic model metadata tracking
    - Local-only storage with optional export
    - Season/version-based leaderboard segmentation
    """
    
    CURRENT_SCHEMA_VERSION = "2.0.0"  # Enhanced for v0.4.1 bootstrap system
    DEFAULT_MAX_ENTRIES = 50  # Per seed/config combination
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize leaderboard manager."""
        self.base_path = base_path or Path.cwd() / "leaderboards"
        self.base_path.mkdir(exist_ok=True)
        
        # Cache of loaded leaderboards by seed+config hash
        self._leaderboard_cache: Dict[str, LocalLeaderboard] = {}
        
        # Session tracking
        self.current_session: Optional[GameSession] = None
        self.session_start_time: Optional[datetime] = None
    
    def start_game_session(self, game_state) -> None:
        """Start tracking a new game session."""
        self.session_start_time = datetime.now()
        
        # Initialize session with starting values
        self.current_session = GameSession(
            seed=game_state.seed,
            final_turn=0,
            final_score=0,
            game_version=get_display_version(),
            economic_model="Bootstrap_v0.4.1",
            
            start_time=self.session_start_time,
            end_time=self.session_start_time,  # Will be updated on end
            duration_minutes=0.0,
            player_name=getattr(game_state, 'lab_name', 'Anonymous Labs'),
            
            final_money=game_state.money,
            final_staff=game_state.staff,
            final_reputation=game_state.reputation,
            final_doom=game_state.doom,
            final_compute=game_state.compute,
            
            total_staff_maintenance_paid=0.0,
            total_research_spending=0.0,
            total_fundraising_gained=0.0,
            moore_law_savings=0.0,
            
            actions_taken=0,
            average_ap_per_turn=3.0,
            research_papers_published=getattr(game_state, 'research_papers_published', 0),
            technical_debt_accumulated=getattr(game_state, 'technical_debt', 0)
        )
    
    def end_game_session(self, game_state) -> Tuple[bool, int, GameSession]:
        """
        End the current game session and save to appropriate leaderboard.
        
        Returns:
            (is_high_score, rank, session_data)
        """
        if not self.current_session:
            raise ValueError("No active game session to end")
        
        # Update final session data
        end_time = datetime.now()
        self.current_session.end_time = end_time
        self.current_session.duration_minutes = (end_time - self.session_start_time).total_seconds() / 60
        
        # Update with final game state
        self.current_session.final_turn = game_state.turn
        self.current_session.final_score = game_state.turn  # Survival scoring
        self.current_session.final_money = game_state.money
        self.current_session.final_staff = game_state.staff
        self.current_session.final_reputation = game_state.reputation
        self.current_session.final_doom = game_state.doom
        self.current_session.final_compute = game_state.compute
        
        # Calculate economic stats if available
        if hasattr(game_state, 'economic_config'):
            # Estimate maintenance paid (weekly * turns)
            weeks_played = max(1, game_state.turn / 7)  # Approximate weeks
            self.current_session.total_staff_maintenance_paid = weeks_played * game_state.economic_config.get_staff_maintenance_cost(game_state.staff)
        
        # Handle technical debt safely (might be object or number)
        technical_debt_value = 0
        try:
            if hasattr(game_state, 'technical_debt'):
                td = getattr(game_state, 'technical_debt', 0)
                if hasattr(td, 'total_debt'):
                    technical_debt_value = int(td.total_debt)
                elif isinstance(td, (int, float)):
                    technical_debt_value = int(td)
        except (AttributeError, TypeError, ValueError):
            technical_debt_value = 0
        
        self.current_session.technical_debt_accumulated = technical_debt_value
        
        # Get appropriate leaderboard
        leaderboard = self._get_leaderboard_for_session(self.current_session)
        
        # Create score entry
        score_entry = ScoreEntry(
            score=self.current_session.final_score,
            player_name=self.current_session.player_name,
            date=end_time,
            level_reached=self.current_session.final_turn,
            game_mode=self.current_session.economic_model,
            duration_seconds=self.current_session.duration_minutes * 60
        )
        
        # Add to leaderboard
        was_added, rank = leaderboard.add_score(score_entry)
        
        # Save session metadata
        self._save_session_metadata(self.current_session)
        
        session_data = self.current_session
        self.current_session = None  # Clear current session
        
        return was_added, rank, session_data
    
    def _get_leaderboard_for_session(self, session: GameSession) -> LocalLeaderboard:
        """Get the appropriate leaderboard for a game session."""
        # Create unique identifier for seed + config combination
        config_hash = session.get_config_hash()
        leaderboard_key = f"{session.seed}_{config_hash}"
        
        if leaderboard_key not in self._leaderboard_cache:
            # Create leaderboard file path
            safe_seed = "".join(c for c in session.seed if c.isalnum() or c in "._-")[:50]
            filename = f"leaderboard_{safe_seed}_{config_hash}.json"
            leaderboard_path = self.base_path / filename
            
            # Create leaderboard
            self._leaderboard_cache[leaderboard_key] = LocalLeaderboard(
                leaderboard_file=leaderboard_path,
                max_entries=self.DEFAULT_MAX_ENTRIES
            )
        
        return self._leaderboard_cache[leaderboard_key]
    
    def _save_session_metadata(self, session: GameSession) -> None:
        """Save detailed session metadata for analysis."""
        config_hash = session.get_config_hash()
        safe_seed = "".join(c for c in session.seed if c.isalnum() or c in "._-")[:50]
        
        # Create metadata directory
        metadata_dir = self.base_path / "sessions"
        metadata_dir.mkdir(exist_ok=True)
        
        # Save session data
        session_filename = f"session_{safe_seed}_{config_hash}_{session.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        session_path = metadata_dir / session_filename
        
        with open(session_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_leaderboard_for_seed(self, seed: str, economic_model: str = "Bootstrap_v0.4.1") -> LocalLeaderboard:
        """Get leaderboard for specific seed and economic model."""
        # Create temporary session for hash calculation
        temp_session = GameSession(
            seed=seed,
            economic_model=economic_model,
            game_version=get_display_version(),
            # Fill required fields with defaults
            final_turn=0, final_score=0, start_time=datetime.now(), end_time=datetime.now(),
            duration_minutes=0, player_name="", final_money=0, final_staff=0,
            final_reputation=0, final_doom=0, final_compute=0,
            total_staff_maintenance_paid=0, total_research_spending=0,
            total_fundraising_gained=0, moore_law_savings=0, actions_taken=0,
            average_ap_per_turn=0, research_papers_published=0, technical_debt_accumulated=0
        )
        
        return self._get_leaderboard_for_session(temp_session)
    
    def get_all_leaderboards(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all existing leaderboards."""
        leaderboards = {}
        
        for file_path in self.base_path.glob("leaderboard_*.json"):
            try:
                # Parse filename to extract seed and config hash
                filename = file_path.stem
                parts = filename.replace("leaderboard_", "").split("_")
                if len(parts) >= 2:
                    seed = "_".join(parts[:-1])
                    config_hash = parts[-1]
                    
                    # Load leaderboard
                    leaderboard = LocalLeaderboard(leaderboard_file=file_path)
                    
                    leaderboards[seed] = {
                        'config_hash': config_hash,
                        'entry_count': len(leaderboard.entries),
                        'top_score': leaderboard.entries[0].score if leaderboard.entries else 0,
                        'file_path': str(file_path)
                    }
                    
            except Exception as e:
                print(f"Warning: Could not load leaderboard {file_path}: {e}")
        
        return leaderboards
    
    def migrate_legacy_scores(self) -> int:
        """Migrate scores from legacy local_highscore.json format."""
        legacy_file = Path("local_highscore.json")
        if not legacy_file.exists():
            return 0
        
        migrated_count = 0
        
        try:
            with open(legacy_file, 'r') as f:
                legacy_data = json.load(f)
            
            for seed, score_data in legacy_data.items():
                # Handle both old format (number) and newer format (dict)
                if isinstance(score_data, dict):
                    score = score_data.get('score', 0)
                    turn = score_data.get('turn', score)
                else:
                    score = turn = score_data
                
                if score > 0:
                    # Create session for migration
                    migration_session = GameSession(
                        seed=seed,
                        final_turn=turn,
                        final_score=score,
                        game_version="pre-v0.4.1",
                        economic_model="Legacy",
                        
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        duration_minutes=0,
                        player_name="Migrated",
                        
                        # Default values for missing data
                        final_money=0, final_staff=0, final_reputation=0,
                        final_doom=0, final_compute=0, total_staff_maintenance_paid=0,
                        total_research_spending=0, total_fundraising_gained=0,
                        moore_law_savings=0, actions_taken=0, average_ap_per_turn=0,
                        research_papers_published=0, technical_debt_accumulated=0
                    )
                    
                    # Get appropriate leaderboard and add entry
                    leaderboard = self._get_leaderboard_for_session(migration_session)
                    score_entry = ScoreEntry(
                        score=score,
                        player_name="Migrated Player",
                        level_reached=turn,
                        game_mode="Legacy"
                    )
                    
                    leaderboard.add_score(score_entry)
                    migrated_count += 1
            
            # Backup and remove legacy file
            backup_path = Path(f"local_highscore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            legacy_file.rename(backup_path)
            
        except Exception as e:
            print(f"Warning: Could not migrate legacy scores: {e}")
        
        return migrated_count


# Global leaderboard manager instance
leaderboard_manager = EnhancedLeaderboardManager()

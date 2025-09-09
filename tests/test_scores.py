"""
Tests for scoring functionality.
"""

import tempfile
from datetime import datetime
from pathlib import Path

from src.scores.local_store import ScoreEntry, LocalLeaderboard
from src.scores.remote_store_stub import RemoteLeaderboard, RemoteStoreManager


class TestScoreEntry:
    """Test cases for ScoreEntry class."""
    
    def test_default_initialization(self):
        """Test ScoreEntry initializes with correct defaults."""
        entry = ScoreEntry(score=1000)
        
        assert entry.score == 1000
        assert entry.player_name == "Anonymous"
        assert isinstance(entry.date, datetime)
        assert entry.level_reached == 1
        assert entry.game_mode == "normal"
        assert entry.duration_seconds == 0.0
        assert isinstance(entry.entry_uuid, str)
        assert len(entry.entry_uuid) == 36  # UUID length
    
    def test_custom_initialization(self):
        """Test ScoreEntry with custom values."""
        test_date = datetime(2014, 7, 15)
        entry = ScoreEntry(
            score=5000,
            player_name="TestPlayer",
            date=test_date,
            level_reached=10,
            game_mode="hard",
            duration_seconds=120.5,
            entry_uuid="test-uuid-1234"
        )
        
        assert entry.score == 5000
        assert entry.player_name == "TestPlayer"
        assert entry.date == test_date
        assert entry.level_reached == 10
        assert entry.game_mode == "hard"
        assert entry.duration_seconds == 120.5
        assert entry.entry_uuid == "test-uuid-1234"
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        test_date = datetime(2014, 7, 15, 14, 30, 0)
        entry = ScoreEntry(
            score=2500,
            player_name="Player1",
            date=test_date,
            level_reached=5,
            game_mode="normal",
            duration_seconds=75.25,
            entry_uuid="test-uuid"
        )
        
        data = entry.to_dict()
        
        assert data["score"] == 2500
        assert data["player_name"] == "Player1"
        assert data["date"] == "2014-07-15T14:30:00"
        assert data["level_reached"] == 5
        assert data["game_mode"] == "normal"
        assert data["duration_seconds"] == 75.25
        assert data["entry_uuid"] == "test-uuid"
    
    def test_from_dict_conversion(self):
        """Test creation from dictionary."""
        data = {
            "score": 3000,
            "player_name": "Player2",
            "date": "2014-07-20T10:15:30",
            "level_reached": 8,
            "game_mode": "hard",
            "duration_seconds": 90.75,
            "entry_uuid": "test-uuid-2"
        }
        
        entry = ScoreEntry.from_dict(data)
        
        assert entry.score == 3000
        assert entry.player_name == "Player2"
        assert entry.date == datetime(2014, 7, 20, 10, 15, 30)
        assert entry.level_reached == 8
        assert entry.game_mode == "hard"
        assert entry.duration_seconds == 90.75
        assert entry.entry_uuid == "test-uuid-2"
    
    def test_score_comparison(self):
        """Test score comparison for sorting."""
        entry1 = ScoreEntry(score=1000)
        entry2 = ScoreEntry(score=2000)
        entry3 = ScoreEntry(score=1500)
        
        # Higher scores should sort first (entry < other means entry comes first)
        assert entry2 < entry1  # 2000 > 1000, so entry2 comes first
        assert entry2 < entry3  # 2000 > 1500, so entry2 comes first
        assert entry3 < entry1  # 1500 > 1000, so entry3 comes first
        
        # Test with list sorting
        entries = [entry1, entry2, entry3]
        entries.sort()
        assert entries[0] == entry2  # Highest score first
        assert entries[1] == entry3
        assert entries[2] == entry1  # Lowest score last
    
    def test_string_representation(self):
        """Test string representation."""
        entry = ScoreEntry(score=1500, player_name="TestPlayer", level_reached=7)
        str_repr = str(entry)
        
        assert "TestPlayer" in str_repr
        assert "1500" in str_repr
        assert "7" in str_repr


class TestLocalLeaderboard:
    """Test cases for LocalLeaderboard class."""
    
    def test_empty_initialization(self):
        """Test leaderboard initializes empty."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            assert len(leaderboard.entries) == 0
            assert leaderboard.max_entries == 100
            assert leaderboard_file.exists()
    
    def test_add_single_score(self):
        """Test adding a single score."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            entry = ScoreEntry(score=1000, player_name="Player1")
            was_added, rank = leaderboard.add_score(entry)
            
            assert was_added is True
            assert rank == 1
            assert len(leaderboard.entries) == 1
            assert leaderboard.entries[0] == entry
    
    def test_score_sorting(self):
        """Test scores are sorted correctly (highest first)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add scores in random order
            scores = [500, 2000, 1000, 1500]
            entries = []
            
            for score in scores:
                entry = ScoreEntry(score=score, player_name=f"Player{score}")
                entries.append(entry)
                leaderboard.add_score(entry)
            
            # Check they're sorted highest first
            assert leaderboard.entries[0].score == 2000
            assert leaderboard.entries[1].score == 1500
            assert leaderboard.entries[2].score == 1000
            assert leaderboard.entries[3].score == 500
    
    def test_ranking(self):
        """Test ranking calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add scores and check ranks
            entry1 = ScoreEntry(score=1000, player_name="Player1")
            entry2 = ScoreEntry(score=2000, player_name="Player2")
            entry3 = ScoreEntry(score=500, player_name="Player3")
            
            _, rank1 = leaderboard.add_score(entry1)
            _, rank2 = leaderboard.add_score(entry2)
            _, rank3 = leaderboard.add_score(entry3)
            
            assert rank1 == 1  # First score added gets rank 1
            assert rank2 == 1  # Higher score takes rank 1
            assert rank3 == 3  # Lower score gets rank 3
    
    def test_max_entries_limit(self):
        """Test leaderboard respects max entries limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file, max_entries=3)
            
            # Add 5 scores
            scores = [1000, 2000, 500, 1500, 800]
            for i, score in enumerate(scores):
                entry = ScoreEntry(score=score, player_name=f"Player{i}")
                leaderboard.add_score(entry)
            
            # Should only keep top 3
            assert len(leaderboard.entries) == 3
            assert leaderboard.entries[0].score == 2000
            assert leaderboard.entries[1].score == 1500
            assert leaderboard.entries[2].score == 1000
    
    def test_persistence(self):
        """Test leaderboard persistence across instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            
            # Create first leaderboard and add scores
            leaderboard1 = LocalLeaderboard(leaderboard_file)
            entry1 = ScoreEntry(score=1000, player_name="Player1")
            entry2 = ScoreEntry(score=2000, player_name="Player2")
            leaderboard1.add_score(entry1)
            leaderboard1.add_score(entry2)
            
            # Create second leaderboard - should load saved data
            leaderboard2 = LocalLeaderboard(leaderboard_file)
            assert len(leaderboard2.entries) == 2
            assert leaderboard2.entries[0].score == 2000
            assert leaderboard2.entries[1].score == 1000
    
    def test_get_top_scores(self):
        """Test getting top scores with count limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add multiple scores
            scores = [100, 500, 300, 800, 200, 600]
            for score in scores:
                entry = ScoreEntry(score=score, player_name=f"Player{score}")
                leaderboard.add_score(entry)
            
            # Get top 3 scores
            top_3 = leaderboard.get_top_scores(count=3)
            assert len(top_3) == 3
            assert top_3[0].score == 800
            assert top_3[1].score == 600
            assert top_3[2].score == 500
    
    def test_game_mode_filtering(self):
        """Test filtering by game mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add scores for different game modes
            normal_entry = ScoreEntry(score=1000, player_name="NormalPlayer", game_mode="normal")
            hard_entry = ScoreEntry(score=800, player_name="HardPlayer", game_mode="hard")
            normal_entry2 = ScoreEntry(score=1200, player_name="NormalPlayer2", game_mode="normal")
            
            leaderboard.add_score(normal_entry)
            leaderboard.add_score(hard_entry)
            leaderboard.add_score(normal_entry2)
            
            # Test filtering by game mode
            normal_scores = leaderboard.get_top_scores(count=10, game_mode="normal")
            hard_scores = leaderboard.get_top_scores(count=10, game_mode="hard")
            
            assert len(normal_scores) == 2
            assert len(hard_scores) == 1
            assert normal_scores[0].score == 1200  # Highest normal score first
            assert hard_scores[0].score == 800
    
    def test_rank_calculation(self):
        """Test rank calculation for hypothetical scores."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add some scores
            scores = [1000, 800, 600, 400]
            for score in scores:
                entry = ScoreEntry(score=score, player_name=f"Player{score}")
                leaderboard.add_score(entry)
            
            # Test rank calculation
            assert leaderboard.get_rank(1200) == 1  # Would be #1
            assert leaderboard.get_rank(900) == 2   # Would be #2
            assert leaderboard.get_rank(700) == 3   # Would be #3
            assert leaderboard.get_rank(500) == 4   # Would be #4
            assert leaderboard.get_rank(300) == 5   # Would be #5
    
    def test_high_score_check(self):
        """Test checking if a score would make the leaderboard."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file, max_entries=3)
            
            # Fill leaderboard to capacity
            scores = [1000, 800, 600]
            for score in scores:
                entry = ScoreEntry(score=score, player_name=f"Player{score}")
                leaderboard.add_score(entry)
            
            # Test high score checks
            assert leaderboard.is_high_score(1200) is True   # Would make it
            assert leaderboard.is_high_score(700) is True    # Would make it
            assert leaderboard.is_high_score(500) is False   # Would not make it
    
    def test_player_best_score(self):
        """Test getting a player's best score."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add multiple scores for same player
            entry1 = ScoreEntry(score=800, player_name="TestPlayer")
            entry2 = ScoreEntry(score=1200, player_name="TestPlayer")
            entry3 = ScoreEntry(score=1000, player_name="TestPlayer")
            entry4 = ScoreEntry(score=500, player_name="OtherPlayer")
            
            leaderboard.add_score(entry1)
            leaderboard.add_score(entry2)
            leaderboard.add_score(entry3)
            leaderboard.add_score(entry4)
            
            # Should get the highest score for TestPlayer
            best = leaderboard.get_player_best("TestPlayer")
            assert best is not None
            assert best.score == 1200
            
            # Test non-existent player
            none_best = leaderboard.get_player_best("NonExistentPlayer")
            assert none_best is None
    
    def test_statistics(self):
        """Test leaderboard statistics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add some scores
            scores_data = [
                (1000, "Player1", "normal"),
                (800, "Player2", "hard"),
                (1200, "Player1", "normal"),  # Same player, different score
                (600, "Player3", "normal")
            ]
            
            for score, player, mode in scores_data:
                entry = ScoreEntry(score=score, player_name=player, game_mode=mode)
                leaderboard.add_score(entry)
            
            stats = leaderboard.get_statistics()
            
            assert stats["total_entries"] == 4
            assert stats["highest_score"] == 1200
            assert stats["lowest_score"] == 600
            assert stats["average_score"] == 900.0  # (1000+800+1200+600)/4
            assert stats["unique_players"] == 3
            assert sorted(stats["game_modes"]) == ["hard", "normal"]
    
    def test_clear_leaderboard(self):
        """Test clearing all entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add some scores
            for score in [1000, 800, 600]:
                entry = ScoreEntry(score=score, player_name=f"Player{score}")
                leaderboard.add_score(entry)
            
            assert len(leaderboard.entries) == 3
            
            # Clear leaderboard
            cleared_count = leaderboard.clear_leaderboard()
            
            assert cleared_count == 3
            assert len(leaderboard.entries) == 0
    
    def test_remove_entry(self):
        """Test removing specific entry by UUID."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            leaderboard = LocalLeaderboard(leaderboard_file)
            
            # Add scores
            entry1 = ScoreEntry(score=1000, player_name="Player1", entry_uuid="uuid-1")
            entry2 = ScoreEntry(score=800, player_name="Player2", entry_uuid="uuid-2")
            entry3 = ScoreEntry(score=600, player_name="Player3", entry_uuid="uuid-3")
            
            leaderboard.add_score(entry1)
            leaderboard.add_score(entry2)
            leaderboard.add_score(entry3)
            
            assert len(leaderboard.entries) == 3
            
            # Remove middle entry
            removed = leaderboard.remove_entry("uuid-2")
            
            assert removed is True
            assert len(leaderboard.entries) == 2
            assert leaderboard.entries[0].entry_uuid == "uuid-1"  # Highest score
            assert leaderboard.entries[1].entry_uuid == "uuid-3"  # Lowest score
            
            # Try to remove non-existent entry
            not_removed = leaderboard.remove_entry("non-existent-uuid")
            assert not_removed is False


class TestRemoteLeaderboard:
    """Test cases for RemoteLeaderboard stub."""
    
    def test_stub_initialization(self):
        """Test RemoteLeaderboard stub initializes correctly."""
        remote = RemoteLeaderboard()
        
        assert remote.api_endpoint == "https://api.pdoom1.com/scores"
        assert remote.api_key is None
        assert remote.is_enabled is False
    
    def test_stub_availability(self):
        """Test stub is never available."""
        remote = RemoteLeaderboard()
        assert remote.is_available() is False
    
    def test_stub_submit_score(self):
        """Test stub score submission returns mock response."""
        remote = RemoteLeaderboard()
        entry = ScoreEntry(score=1000, player_name="TestPlayer")
        
        result = remote.submit_score(entry)
        
        assert result["success"] is False
        assert "not implemented" in result["message"]
        assert result["rank"] is None
        assert "submitted_at" in result
    
    def test_stub_methods_return_mock_data(self):
        """Test all stub methods return appropriate mock responses."""
        remote = RemoteLeaderboard()
        
        # Test various methods
        leaderboard_result = remote.get_global_leaderboard()
        assert leaderboard_result["success"] is False
        assert leaderboard_result["entries"] == []
        
        rank_result = remote.get_player_rank("TestPlayer")
        assert rank_result["success"] is False
        assert rank_result["rank"] is None
        
        validation_result = remote.validate_connection()
        assert validation_result["success"] is False
        assert validation_result["authenticated"] is False


class TestRemoteStoreManager:
    """Test cases for RemoteStoreManager."""
    
    def test_manager_initialization(self):
        """Test RemoteStoreManager initializes correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            local = LocalLeaderboard(leaderboard_file)
            manager = RemoteStoreManager(local)
            
            assert manager.local == local
            assert isinstance(manager.remote, RemoteLeaderboard)
    
    def test_submit_score_local_and_remote(self):
        """Test score submission to both local and remote stores."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            local = LocalLeaderboard(leaderboard_file)
            manager = RemoteStoreManager(local)
            
            entry = ScoreEntry(score=1000, player_name="TestPlayer")
            result = manager.submit_score(entry)
            
            # Should have local and remote results
            assert "local" in result
            assert "remote" in result
            assert result["local"]["success"] is True
            assert result["local"]["rank"] == 1
            assert result["remote"]["success"] is False  # Stub always fails
            
            # Local leaderboard should be updated
            assert len(local.entries) == 1
            assert local.entries[0].score == 1000
    
    def test_combined_leaderboard(self):
        """Test getting combined local and remote leaderboard."""
        with tempfile.TemporaryDirectory() as temp_dir:
            leaderboard_file = Path(temp_dir) / "test_leaderboard.json"
            local = LocalLeaderboard(leaderboard_file)
            manager = RemoteStoreManager(local)
            
            # Add local scores
            entry = ScoreEntry(score=1000, player_name="LocalPlayer")
            local.add_score(entry)
            
            result = manager.get_combined_leaderboard()
            
            assert "local_scores" in result
            assert "remote_scores" in result
            assert result["remote_available"] is False
            assert len(result["local_scores"]) == 1
            assert result["local_scores"][0]["score"] == 1000
            assert result["remote_scores"] == []  # Stub returns empty
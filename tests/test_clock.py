"""
Tests for GameClock functionality.
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.services.game_clock import GameClock


class TestGameClock:
    """Test cases for GameClock service."""
    
    def test_default_initialization(self):
        """Test GameClock initializes with correct defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Should start at April 4, 2016 (updated default date)
            assert clock.get_current_date() == datetime(2016, 4, 4)
            assert clock.get_tick_count() == 0
            assert clock.advance_weeks == 1
    
    def test_formatted_date(self):
        """Test date formatting as DD/Mon/YYYYY."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Initial date should be 04/Apr/02016 (5-digit year format)
            assert clock.get_formatted_date() == "04/Apr/02016"
            
            # Test with different date
            clock.set_date(datetime(2014, 12, 25))
            assert clock.get_formatted_date() == "25/Dec/02014"
            
            # Test year rollover
            clock.set_date(datetime(2015, 1, 1))
            assert clock.get_formatted_date() == "01/Jan/02015"
    
    def test_tick_advancement(self):
        """Test clock advancement by ticks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Initial state
            initial_date = clock.get_current_date()
            assert clock.get_tick_count() == 0
            
            # First tick should advance by 1 week
            clock.tick()
            expected_date = initial_date + timedelta(weeks=1)
            assert clock.get_current_date() == expected_date
            assert clock.get_tick_count() == 1
            assert clock.get_formatted_date() == "11/Apr/02016"
            
            # Second tick
            clock.tick()
            expected_date = initial_date + timedelta(weeks=2)
            assert clock.get_current_date() == expected_date
            assert clock.get_tick_count() == 2
            assert clock.get_formatted_date() == "18/Apr/02016"
    
    def test_custom_advancement_rate(self):
        """Test clock with custom advancement rate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(advance_weeks=2, state_file=str(state_file))
            
            initial_date = clock.get_current_date()
            
            # Should advance by 2 weeks per tick
            clock.tick()
            expected_date = initial_date + timedelta(weeks=2)
            assert clock.get_current_date() == expected_date
            assert clock.get_formatted_date() == "18/Apr/02016"
    
    def test_persistence(self):
        """Test clock state persistence across instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            
            # Create first clock instance and advance it
            clock1 = GameClock(state_file=str(state_file))
            clock1.tick()
            clock1.tick()
            date_after_ticks = clock1.get_current_date()
            tick_count = clock1.get_tick_count()
            
            # Create second clock instance - should load saved state
            clock2 = GameClock(state_file=str(state_file))
            assert clock2.get_current_date() == date_after_ticks
            assert clock2.get_tick_count() == tick_count
            assert clock2.get_formatted_date() == "18/Apr/02016"
    
    def test_manual_date_setting(self):
        """Test manual date setting and tick count calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Set date to 4 weeks after start
            future_date = datetime(2016, 5, 2)  # 4 weeks after April 4, 2016
            clock.set_date(future_date)
            
            assert clock.get_current_date() == future_date
            assert clock.get_tick_count() == 4  # Should calculate correct tick count
            assert clock.get_formatted_date() == "02/May/02016"
    
    def test_advance_by_days(self):
        """Test advancing by specific number of days."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            initial_date = clock.get_current_date()
            
            # Advance by 10 days
            result_date = clock.advance_by_days(10)
            expected_date = initial_date + timedelta(days=10)
            
            assert result_date == expected_date
            assert clock.get_current_date() == expected_date
            assert clock.get_formatted_date() == "14/Apr/02016"
    
    def test_time_calculations(self):
        """Test time calculation methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Advance by several weeks
            clock.tick()  # +1 week
            clock.tick()  # +2 weeks total
            clock.tick()  # +3 weeks total
            
            # Test time since start
            time_since_start = clock.get_time_since_start()
            assert time_since_start == timedelta(weeks=3)
            
            # Test weeks since start
            weeks_since_start = clock.get_weeks_since_start()
            assert weeks_since_start == 3
    
    def test_reset(self):
        """Test clock reset functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Advance the clock
            clock.tick()
            clock.tick()
            assert clock.get_tick_count() == 2
            
            # Reset should go back to start
            clock.reset()
            assert clock.get_current_date() == datetime(2016, 4, 4)
            assert clock.get_tick_count() == 0
            assert clock.get_formatted_date() == "04/Apr/02016"
    
    def test_date_parsing(self):
        """Test parsing both DD/Mon/YY and DD/Mon/YYYYY formatted dates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Test 2-digit year parsing (backward compatibility)
            parsed_date = clock.parse_formatted_date("25/Dec/14")
            expected_date = datetime(2014, 12, 25)
            assert parsed_date == expected_date
            
            # Test 2-digit year handling
            parsed_date = clock.parse_formatted_date("01/Jan/20")
            expected_date = datetime(2020, 1, 1)
            assert parsed_date == expected_date
            
            # Test 5-digit year parsing (new format)
            parsed_date = clock.parse_formatted_date("04/Apr/02016")
            expected_date = datetime(2016, 4, 4)
            assert parsed_date == expected_date
            
            parsed_date = clock.parse_formatted_date("25/Dec/02025")
            expected_date = datetime(2025, 12, 25)
            assert parsed_date == expected_date
            
            # Test invalid date format
            with pytest.raises(ValueError):
                clock.parse_formatted_date("invalid")
            
            with pytest.raises(ValueError):
                clock.parse_formatted_date("32/Jan/14")  # Invalid day
    
    def test_format_arbitrary_date(self):
        """Test formatting arbitrary dates with 5-digit years."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Test various dates (now with 5-digit years)
            test_dates = [
                (datetime(2014, 1, 1), "01/Jan/02014"),
                (datetime(2014, 12, 31), "31/Dec/02014"),
                (datetime(2020, 2, 29), "29/Feb/02020"),  # Leap year
                (datetime(1999, 7, 4), "04/Jul/01999"),
                (datetime(2025, 5, 21), "21/May/02025"),  # Future longtermist date
            ]
            
            for date, expected_format in test_dates:
                assert clock.format_date(date) == expected_format
    
    def test_corrupted_state_file(self):
        """Test handling of corrupted state file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            
            # Create corrupted state file
            with open(state_file, 'w') as f:
                f.write("invalid json content")
            
            # Clock should handle corruption gracefully and reset
            clock = GameClock(state_file=str(state_file))
            assert clock.get_current_date() == datetime(2016, 4, 4)
            assert clock.get_tick_count() == 0
    
    def test_string_representations(self):
        """Test string representation methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = Path(temp_dir) / "test_clock.json"
            clock = GameClock(state_file=str(state_file))
            
            # Test __str__ method (now with 5-digit years)
            str_repr = str(clock)
            assert "04/Apr/02016" in str_repr
            assert "tick=0" in str_repr
            
            # Test __repr__ method
            repr_str = repr(clock)
            assert "GameClock" in repr_str
            assert "current_date=" in repr_str
            assert "tick_count=" in repr_str
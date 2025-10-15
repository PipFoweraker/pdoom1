'''
Game clock for PDoom1.

Provides configurable game time that starts at 04/Apr/02016 and advances +1 week per tick.
Formats dates as DD/Mon/YYYYY (longtermist 5-digit years) and persists current time state.
'''

from datetime import datetime, timedelta
from typing import Optional
import json
from pathlib import Path
from src.services.data_paths import get_data_dir


class GameClock:
    '''
    Game time management with configurable start date and advancement rate.
    
    Features:
    - Starts at April 4, 2016 (04/Apr/02016) - First Monday in April 2016
    - Advances by 1 week per tick by default
    - Formats dates as DD/Mon/YYYYY (e.g., '04/Apr/02016') - Longtermist 5-digit years
    - Persistent state across game sessions
    - Configurable advancement rate
    '''
    
    # Default start date: April 4, 2016 (First Monday in April 2016)
    DEFAULT_START_DATE = datetime(2016, 4, 4)
    
    # Month abbreviations for DD/Mon/YY format
    MONTH_ABBREVS = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    
    def __init__(self, 
                 start_date: Optional[datetime] = None,
                 advance_weeks: int = 1,
                 state_file: Optional[str] = None):
        '''
        Initialize game clock.
        
        Args:
            start_date: Starting date for the game clock (defaults to April 4, 2016)
            advance_weeks: Number of weeks to advance per tick (default: 1)
            state_file: Custom state file path or filename (defaults to clock_state.json in data dir)
        '''
        self.start_date = start_date or self.DEFAULT_START_DATE
        self.advance_weeks = advance_weeks
        
        if state_file and ('/' in state_file or '\\' in state_file):
            # Full path provided
            self.state_file = Path(state_file)
        else:
            # Just filename provided, use data directory
            self.state_file = get_data_dir() / (state_file or 'clock_state.json')
        
        # Load or initialize current state
        self._load_state()
    
    def _load_state(self) -> None:
        '''Load clock state from file or initialize to start date.'''
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    
                # Parse the stored date
                self.current_date = datetime.fromisoformat(state['current_date'])
                self.tick_count = state.get('tick_count', 0)
            else:
                # First run - start at the beginning
                self.current_date = self.start_date
                self.tick_count = 0
                self._save_state()
                
        except (json.JSONDecodeError, KeyError, ValueError, IOError) as e:
            print(f'Warning: Could not load clock state, resetting: {e}')
            self.current_date = self.start_date
            self.tick_count = 0
            self._save_state()
    
    def _save_state(self) -> None:
        '''Save current clock state to file.'''
        try:
            state = {
                'current_date': self.current_date.isoformat(),
                'tick_count': self.tick_count,
                'start_date': self.start_date.isoformat(),
                'advance_weeks': self.advance_weeks
            }
            
            # Atomic write
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            
            # Atomic move
            temp_file.replace(self.state_file)
            
        except IOError as e:
            print(f'Warning: Could not save clock state: {e}')
    
    def tick(self) -> datetime:
        '''
        Advance the game clock by the configured amount.
        
        Returns:
            The new current date after advancing
        '''
        weeks_delta = timedelta(weeks=self.advance_weeks)
        self.current_date += weeks_delta
        self.tick_count += 1
        
        self._save_state()
        return self.current_date
    
    def get_current_date(self) -> datetime:
        '''Get the current game date.'''
        return self.current_date
    
    def get_formatted_date(self) -> str:
        '''
        Get the current date formatted as DD/Mon/YYYYY.
        
        Returns:
            Formatted date string (e.g., '01/Jul/02014')
        '''
        day = self.current_date.day
        # Bounds checking to prevent IndexError: ensure month is 1-12
        month_index = max(0, min(11, self.current_date.month - 1))
        month_abbrev = self.MONTH_ABBREVS[month_index]
        year = self.current_date.year  # Full 5-digit year with leading zeros
        
        return f'{day:02d}/{month_abbrev}/{year:05d}'
    
    def get_tick_count(self) -> int:
        '''Get the number of ticks since game start.'''
        return self.tick_count
    
    def set_date(self, date: datetime) -> None:
        '''
        Set the current game date manually.
        
        Args:
            date: The date to set as current
        '''
        self.current_date = date
        # Calculate tick count based on difference from start
        delta = date - self.start_date
        self.tick_count = max(0, int(delta.days // (7 * self.advance_weeks)))
        
        self._save_state()
    
    def reset(self) -> None:
        '''Reset the clock to the start date.'''
        self.current_date = self.start_date
        self.tick_count = 0
        self._save_state()
    
    def advance_by_days(self, days: int) -> datetime:
        '''
        Advance the clock by a specific number of days.
        
        Args:
            days: Number of days to advance
            
        Returns:
            The new current date
        '''
        self.current_date += timedelta(days=days)
        # Update tick count (approximate)
        self.tick_count += max(1, days // (7 * self.advance_weeks))
        
        self._save_state()
        return self.current_date
    
    def get_time_since_start(self) -> timedelta:
        '''Get the time elapsed since the start date.'''
        return self.current_date - self.start_date
    
    def get_weeks_since_start(self) -> int:
        '''Get the number of weeks elapsed since the start date.'''
        delta = self.get_time_since_start()
        return int(delta.days // 7)
    
    def format_date(self, date: datetime) -> str:
        '''
        Format any datetime as DD/Mon/YYYYY.
        
        Args:
            date: Date to format
            
        Returns:
            Formatted date string
        '''
        day = date.day
        # Bounds checking to prevent IndexError: ensure month is 1-12
        month_index = max(0, min(11, date.month - 1))
        month_abbrev = self.MONTH_ABBREVS[month_index]
        year = date.year  # Full 5-digit year with leading zeros
        
        return f'{day:02d}/{month_abbrev}/{year:05d}'
    
    def parse_formatted_date(self, date_str: str) -> datetime:
        '''
        Parse a DD/Mon/YY formatted date string.
        
        Args:
            date_str: Date string in DD/Mon/YY format
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If date string is invalid
        '''
        try:
            parts = date_str.split('/')
            if len(parts) != 3:
                raise ValueError('Invalid date format')
            
            day = int(parts[0])
            month_abbrev = parts[1]
            year = int(parts[2])
            
            # Handle both 2-digit and 5-digit years
            if year < 100:
                # 2-digit year - convert to 4-digit (assume 2000s for compatibility)
                if year < 50:
                    year += 2000
                else:
                    year += 1900
            # 5-digit years (02016, 02025, etc.) are used as-is
            
            # Find month number
            try:
                month = self.MONTH_ABBREVS.index(month_abbrev) + 1
            except ValueError:
                raise ValueError(f'Invalid month abbreviation: {month_abbrev}')
            
            return datetime(year, month, day)
            
        except (ValueError, IndexError) as e:
            raise ValueError(f'Invalid date format \'{date_str}\': {e}')
    
    def __str__(self) -> str:
        '''String representation of the current game time.'''
        return f'GameClock(current={self.get_formatted_date()}, tick={self.tick_count})'
    
    def __repr__(self) -> str:
        '''Detailed string representation.'''
        return (f'GameClock(current_date={self.current_date}, '
                f'tick_count={self.tick_count}, '
                f'advance_weeks={self.advance_weeks})')
'''
Game logging system for P(Doom) - captures all meaningful in-game actions and events.

This module provides a persistent logging system that stores game events in memory
during play and writes them to uniquely named text files on game end.
'''

import os
import platform
import datetime
from typing import List, Dict, Any, Optional
from src.services.version import get_display_version


class GameLogger:
    '''
    Handles logging of all game events and actions for debugging and analysis.
    
    Features:
    - In-memory log storage during gameplay
    - Unique file naming with timestamps
    - Privacy-conscious system info collection
    - Graceful file writing on game end or crash
    '''
    
    def __init__(self, seed: str, game_version: str = None):
        '''
        Initialize the game logger.
        
        Args:
            seed: The game seed being used
            game_version: Version of the game (defaults to current version)
        '''
        self.seed = seed
        self.game_version = game_version or get_display_version()
        self.start_time = datetime.datetime.now()
        self.log_entries: List[str] = []
        self.logs_dir = 'logs'
        
        # Ensure logs directory exists
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Log game start with minimal system info
        self._log_game_start()
    
    def _log_game_start(self):
        '''Log the initial game state and system information.'''
        timestamp = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Minimal, privacy-conscious OS info
        os_type = platform.system()  # e.g., 'Linux', 'Windows', 'Darwin'
        
        self.log_entries.extend([
            f'=== GAME START ===',
            f'Timestamp: {timestamp}',
            f'Game Version: {self.game_version}',
            f'Seed: {self.seed}',
            f'OS: {os_type}',
            f'=================='
        ])
    
    def log_action(self, action_name: str, cost: int, turn: int):
        '''Log a player action.'''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_entries.append(f'[{timestamp}] Turn {turn}: Action \'{action_name}\' (cost: {cost})')
    
    def log_upgrade(self, upgrade_name: str, cost: int, turn: int):
        '''Log an upgrade purchase.'''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_entries.append(f'[{timestamp}] Turn {turn}: Upgrade \'{upgrade_name}\' purchased (cost: {cost})')
    
    def log_event(self, event_name: str, description: str, turn: int):
        '''Log a game event.'''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_entries.append(f'[{timestamp}] Turn {turn}: Event \'{event_name}\' - {description}')
    
    def log_turn_summary(self, turn: int, money: int, staff: int, reputation: int, doom: int):
        '''Log end-of-turn resource summary.'''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_entries.append(
            f'[{timestamp}] Turn {turn} End: Money={money}, Staff={staff}, '
            f'Reputation={reputation}, Doom={doom}/100'
        )
    
    def log_game_end(self, reason: str, turn: int, final_resources: Dict[str, Any]):
        '''Log game ending with reason and final state.'''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        
        self.log_entries.extend([
            f'',
            f'=== GAME END ===',
            f'Timestamp: {timestamp}',
            f'Reason: {reason}',
            f'Final Turn: {turn}',
            f'Final Money: {final_resources.get('money', 0)}',
            f'Final Staff: {final_resources.get('staff', 0)}',
            f'Final Reputation: {final_resources.get('reputation', 0)}',
            f'Final Doom: {final_resources.get('doom', 0)}/100',
            f'================'
        ])
    
    def log_message(self, message: str, turn: int):
        '''Log a general game message.'''
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_entries.append(f'[{timestamp}] Turn {turn}: {message}')
    
    def get_log_filename(self) -> str:
        '''Generate unique log filename with web-safe format.'''
        timestamp_str = self.start_time.strftime('%Y%m%d_%H%M%S')
        return f'gamelog_{timestamp_str}.txt'
    
    def write_log_file(self) -> Optional[str]:
        '''
        Write the current log to a file.
        
        Returns:
            The path to the written file, or None if writing failed
        '''
        try:
            filename = self.get_log_filename()
            filepath = os.path.join(self.logs_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for entry in self.log_entries:
                    f.write(entry + '\n')
            
            return filepath
        except Exception as e:
            # Attempt to write to a fallback location if the primary fails
            try:
                fallback_path = f'emergency_{self.get_log_filename()}'
                with open(fallback_path, 'w', encoding='utf-8') as f:
                    f.write(f'# Log write failed to {self.logs_dir}, using fallback\n')
                    f.write(f'# Error: {str(e)}\n\n')
                    for entry in self.log_entries:
                        f.write(entry + '\n')
                return fallback_path
            except Exception:
                return None
    
    def get_log_summary(self) -> str:
        '''Get a summary of what's currently logged (for testing/debugging).'''
        return f'Logger for seed \'{self.seed}\': {len(self.log_entries)} entries'
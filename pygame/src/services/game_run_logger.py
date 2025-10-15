'''
Game Run Logger - Privacy-Respecting Player Analytics

A modular service for collecting game run data to improve game balance and player experience.
Designed to extract logging functionality from monolithic game state management.

Key Design Principles:
- Privacy-first: User controls data collection level
- Modular: Separate from core game logic to reduce monoliths  
- Local-first: Data stored locally, cloud submission optional
- Anonymized: No personally identifiable information
- Performance: Minimal impact on game performance

Architecture Goals:
- Reduce GameState monolith by extracting logging concerns
- Provide clean interface for UI integration
- Enable data-driven game balance improvements
'''

import json
import os
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class SimplePrivacyManager:
    '''Simple privacy manager for UI compatibility.'''
    
    def __init__(self):
        self.settings = {}


class LoggingLevel(Enum):
    '''Privacy-respecting logging levels with clear user descriptions.'''
    
    DISABLED = 'disabled'
    MINIMAL = 'minimal' 
    STANDARD = 'standard'
    VERBOSE = 'verbose'
    DEBUG = 'debug'
    
    @property
    def display_name(self) -> str:
        '''User-friendly display names.'''
        names = {
            LoggingLevel.DISABLED: 'Disabled',
            LoggingLevel.MINIMAL: 'Minimal', 
            LoggingLevel.STANDARD: 'Standard',
            LoggingLevel.VERBOSE: 'Verbose',
            LoggingLevel.DEBUG: 'Debug'
        }
        return names[self]
    
    @property
    def description(self) -> str:
        '''Detailed descriptions for user education.'''
        descriptions = {
            LoggingLevel.DISABLED: 'No data collection. Complete privacy.',
            LoggingLevel.MINIMAL: 'Basic game completion stats only. Anonymous.', 
            LoggingLevel.STANDARD: 'Action patterns and resource flow. Helps improve game balance.',
            LoggingLevel.VERBOSE: 'Detailed strategy analysis. Enables advanced balance improvements.',
            LoggingLevel.DEBUG: 'Full diagnostic data. For development and testing only.'
        }
        return descriptions[self]
    
    @property
    def data_collected(self) -> List[str]:
        '''What data is collected at this level.'''
        data_types = {
            LoggingLevel.DISABLED: [],
            LoggingLevel.MINIMAL: ['Game completion', 'Victory/defeat', 'Play time'],
            LoggingLevel.STANDARD: ['Action choices', 'Resource progression', 'Turn timing'],
            LoggingLevel.VERBOSE: ['Decision alternatives', 'Strategy patterns', 'Milestone timing'],
            LoggingLevel.DEBUG: ['Full game state', 'Performance metrics', 'Error diagnostics']
        }
        return data_types[self]


class GameRunLogger:
    '''
    Privacy-first game run logger for balance analytics.
    
    Designed as a modular service to reduce GameState monolith complexity
    by extracting data collection concerns into a focused component.
    '''
    
    def __init__(self, logging_level: LoggingLevel = LoggingLevel.DISABLED):
        '''Initialize logger with specified privacy level.'''
        self.logging_level = logging_level
        self.session_id = self._generate_session_id()
        self.start_time = time.time()
        
        # Simple privacy manager simulation for UI compatibility
        self.privacy_manager = SimplePrivacyManager()
        
        # Modular data storage - each aspect separated for clarity
        self.run_data = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.start_time,
                'logging_level': logging_level.value
            },
            'actions': [],           # Player decision tracking
            'state_changes': [],     # Resource flow analysis  
            'milestones': [],        # Progress markers
            'performance': [],       # Technical metrics
            'metadata': {}           # Game configuration data
        }
        
        # Ensure logging directory exists
        self.log_dir = Path('game_logs')
        self.log_dir.mkdir(exist_ok=True)
    
    def _generate_session_id(self) -> str:
        '''Generate unique session identifier.'''
        return f'session_{int(time.time())}_{os.getpid()}'
    
    def is_enabled(self) -> bool:
        '''Check if logging is enabled at any level.'''
        return self.logging_level != LoggingLevel.DISABLED
    
    def should_log(self, required_level: LoggingLevel) -> bool:
        '''Check if current logging level includes specified level.'''
        if not self.is_enabled():
            return False
            
        level_hierarchy = {
            LoggingLevel.DISABLED: 0,
            LoggingLevel.MINIMAL: 1,
            LoggingLevel.STANDARD: 2, 
            LoggingLevel.VERBOSE: 3,
            LoggingLevel.DEBUG: 4
        }
        
        return level_hierarchy[self.logging_level] >= level_hierarchy[required_level]
    
    def log_action(self, action_type: str, ap_cost: int, result: str, 
                   alternatives: Optional[List[str]] = None, turn: int = 0) -> None:
        '''
        Log player action for strategy analysis.
        
        Helps identify dominant strategies and balance issues by tracking
        player decision patterns separate from core game logic.
        '''
        if not self.should_log(LoggingLevel.STANDARD):
            return
            
        action_data = {
            'timestamp': time.time(),
            'turn': turn,
            'action_type': action_type,
            'ap_cost': ap_cost,
            'result': result
        }
        
        # Include decision alternatives at verbose level
        if self.should_log(LoggingLevel.VERBOSE) and alternatives:
            action_data['alternatives'] = alternatives
            
        self.run_data['actions'].append(action_data)
    
    def log_state_change(self, resource: str, old_value: Union[int, float], 
                        new_value: Union[int, float], cause: str, turn: int = 0) -> None:
        '''
        Log resource state changes for balance analysis.
        
        Tracks resource flow patterns to identify balance issues
        without cluttering core game state management.
        '''
        if not self.should_log(LoggingLevel.STANDARD):
            return
            
        change_data = {
            'timestamp': time.time(),
            'turn': turn,
            'resource': resource,
            'old_value': old_value,
            'new_value': new_value,
            'delta': new_value - old_value,
            'cause': cause
        }
        
        self.run_data['state_changes'].append(change_data)
    
    def log_milestone(self, milestone_type: str, turn: int, details: Optional[Dict] = None) -> None:
        '''
        Log game milestones for progression analysis.
        
        Tracks key game events to understand player progression patterns
        and identify difficulty spikes or pacing issues.
        '''
        if not self.should_log(LoggingLevel.MINIMAL):
            return
            
        milestone_data = {
            'timestamp': time.time(),
            'turn': turn,
            'milestone_type': milestone_type,
            'details': details or {}
        }
        
        self.run_data['milestones'].append(milestone_data)
    
    def log_performance(self, metric: str, value: float, context: str = '') -> None:
        '''Log performance metrics for optimization analysis.'''
        if not self.should_log(LoggingLevel.DEBUG):
            return
            
        perf_data = {
            'timestamp': time.time(),
            'metric': metric,
            'value': value,
            'context': context
        }
        
        self.run_data['performance'].append(perf_data)
    
    def set_metadata(self, key: str, value: Any) -> None:
        '''Set session metadata for context.'''
        if not self.is_enabled():
            return
            
        self.run_data['metadata'][key] = value
    
    def finalize_session(self, outcome: str, final_stats: Optional[Dict] = None) -> str:
        '''
        Finalize and save session data.
        
        Returns the path to the saved log file for user reference.
        Enables clean session lifecycle management separate from game logic.
        '''
        if not self.is_enabled():
            return ''
            
        # Add session completion data
        end_time = time.time()
        self.run_data['session_info'].update({
            'end_time': end_time,
            'duration': end_time - self.start_time,
            'outcome': outcome,
            'final_stats': final_stats or {}
        })
        
        # Save to file
        filename = f'{self.session_id}_{outcome.lower()}.json'
        filepath = self.log_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.run_data, f, indent=2, default=str)
            return str(filepath)
        except Exception as e:
            print(f'Warning: Failed to save game log: {e}')
            return ''
    
    def get_data_summary(self) -> Dict[str, Any]:
        '''
        Get summary of collected data for user transparency.
        
        Enables privacy controls UI to show users exactly what
        data has been collected in their current session.
        '''
        if not self.is_enabled():
            return {'status': 'disabled', 'data_points': 0}
            
        summary = {
            'status': 'active',
            'logging_level': self.logging_level.display_name,
            'session_duration': time.time() - self.start_time,
            'data_points': {
                'actions': len(self.run_data['actions']),
                'state_changes': len(self.run_data['state_changes']),
                'milestones': len(self.run_data['milestones']),
                'performance_metrics': len(self.run_data['performance'])
            },
            'data_types': self.logging_level.data_collected
        }
        
        return summary
    
    def clear_session_data(self) -> None:
        '''Clear current session data for privacy.'''
        self.run_data = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.start_time,
                'logging_level': self.logging_level.value
            },
            'actions': [],
            'state_changes': [],
            'milestones': [],
            'performance': [],
            'metadata': {}
        }
    
    def configure_logging_level(self, level: LoggingLevel) -> None:
        '''Configure the logging level for this session.'''
        self.logging_level = level
        self.run_data['session_info']['logging_level'] = level.value
        
    def delete_all_data(self) -> bool:
        '''Delete all stored logging data.'''
        try:
            deleted_count = delete_all_game_logs()
            self.clear_session_data()
            return deleted_count > 0
        except Exception:
            return False
    
    def get_user_data_summary(self) -> Dict[str, Any]:
        '''Get summary of user data for privacy controls display.'''
        storage_info = get_log_storage_info()
        
        return {
            'session_count': storage_info['log_count'],
            'disk_usage_mb': storage_info['total_size_bytes'] / (1024 * 1024),
            'retention_days': 90,  # Default retention period
            'current_session_data_points': sum([
                len(self.run_data['actions']),
                len(self.run_data['state_changes']),
                len(self.run_data['milestones']),
                len(self.run_data['performance'])
            ])
        }

    # ==========================================
    # GameLogger Compatibility Methods
    # ==========================================
    # These methods provide backward compatibility with the existing GameLogger interface
    # used throughout the codebase, enabling gradual migration to the new system.
    
    def log_event(self, event_name: str, description: str, turn: int) -> None:
        '''Log a game event (GameLogger compatibility).'''
        if not self.should_log(LoggingLevel.STANDARD):
            return
            
        self.run_data['actions'].append({
            'type': 'event',
            'name': event_name,
            'description': description,
            'turn': turn,
            'timestamp': time.time() - self.start_time
        })
    
    def log_upgrade(self, upgrade_name: str, cost: int, turn: int) -> None:
        '''Log an upgrade purchase (GameLogger compatibility).'''
        if not self.should_log(LoggingLevel.STANDARD):
            return
            
        self.run_data['actions'].append({
            'type': 'upgrade',
            'name': upgrade_name,
            'cost': cost,
            'turn': turn,
            'timestamp': time.time() - self.start_time
        })
    
    def log_turn_summary(self, turn: int, money: int, staff: int, reputation: int, doom: int) -> None:
        '''Log end-of-turn resource summary (GameLogger compatibility).'''
        if not self.should_log(LoggingLevel.MINIMAL):
            return
            
        self.run_data['state_changes'].append({
            'type': 'turn_summary',
            'turn': turn,
            'resources': {
                'money': money,
                'staff': staff, 
                'reputation': reputation,
                'doom': doom
            },
            'timestamp': time.time() - self.start_time
        })
    
    def log_game_end(self, victory: bool, reason: str, final_stats: Dict[str, Any]) -> None:
        '''Log game end conditions (GameLogger compatibility).'''
        if not self.should_log(LoggingLevel.MINIMAL):
            return
            
        self.run_data['metadata']['game_end'] = {
            'victory': victory,
            'reason': reason,
            'final_stats': final_stats,
            'timestamp': time.time() - self.start_time,
            'total_duration': time.time() - self.start_time
        }
        
        # Auto-finalize session on game end
        self.finalize_session()
    
    def log_message(self, message: str) -> None:
        '''Log a general message (GameLogger compatibility).'''
        if not self.should_log(LoggingLevel.DEBUG):
            return
            
        self.run_data['performance'].append({
            'type': 'message',
            'content': message,
            'timestamp': time.time() - self.start_time
        })
    
    def get_log_filename(self) -> str:
        '''Get log filename (GameLogger compatibility).'''
        return f'game_run_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json'
    
    def get_log_summary(self) -> Dict[str, Any]:
        '''Get log summary (GameLogger compatibility).'''
        return self.get_data_summary()
    
    def write_log_file(self) -> str:
        '''Write log file and return filename (GameLogger compatibility).'''
        return self.finalize_session()


# Global logger instance for easy access
_global_logger: Optional[GameRunLogger] = None


def init_game_logger(logging_level: LoggingLevel = LoggingLevel.DISABLED, 
                     enabled_by_default: bool = False) -> GameRunLogger:
    '''
    Initialize the global game logger.
    
    Provides clean initialization separate from game state setup,
    reducing coupling and improving modularity.
    
    Args:
        logging_level: Specific logging level to use
        enabled_by_default: If True, defaults to STANDARD level (backward compatibility)
    '''
    global _global_logger
    
    # Handle backward compatibility
    if enabled_by_default and logging_level == LoggingLevel.DISABLED:
        logging_level = LoggingLevel.STANDARD
        
    _global_logger = GameRunLogger(logging_level)
    return _global_logger


def get_game_logger() -> Optional[GameRunLogger]:
    '''
    Get the global game logger instance.
    
    Returns None if logger hasn't been initialized, allowing
    graceful degradation when logging is disabled.
    '''
    return _global_logger


def delete_all_game_logs() -> int:
    '''
    Delete all stored game logs for privacy.
    
    Returns the number of files deleted.
    Provides user control over their data storage.
    '''
    log_dir = Path('game_logs')
    if not log_dir.exists():
        return 0
        
    deleted_count = 0
    try:
        for log_file in log_dir.glob('*.json'):
            log_file.unlink()
            deleted_count += 1
    except Exception as e:
        print(f'Warning: Error deleting log files: {e}')
        
    return deleted_count


def get_log_storage_info() -> Dict[str, Any]:
    '''
    Get information about log storage for user transparency.
    
    Enables privacy controls to show users what data is stored
    and how much space it uses.
    '''
    log_dir = Path('game_logs')
    if not log_dir.exists():
        return {
            'log_count': 0,
            'total_size_bytes': 0,
            'storage_location': str(log_dir)
        }
    
    log_files = list(log_dir.glob('*.json'))
    total_size = sum(f.stat().st_size for f in log_files)
    
    return {
        'log_count': len(log_files),
        'total_size_bytes': total_size,
        'storage_location': str(log_dir.absolute()),
        'recent_sessions': [f.stem for f in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]]
    }


# Convenience functions for common logging operations
def log_action(action_type: str, ap_cost: int, result: str, **kwargs) -> None:
    '''Convenience function for action logging.'''
    logger = get_game_logger()
    if logger:
        logger.log_action(action_type, ap_cost, result, **kwargs)


def log_state_change(resource: str, old_value: Union[int, float], 
                    new_value: Union[int, float], cause: str, **kwargs) -> None:
    '''Convenience function for state change logging.'''
    logger = get_game_logger()
    if logger:
        logger.log_state_change(resource, old_value, new_value, cause, **kwargs)


def log_milestone(milestone_type: str, turn: int, details: Optional[Dict] = None) -> None:
    '''Convenience function for milestone logging.'''
    logger = get_game_logger()
    if logger:
        logger.log_milestone(milestone_type, turn, details)

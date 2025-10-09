'''
Verbose Logging System for P(Doom)

Provides comprehensive logging for debugging, balancing, and competitive verification.
All game actions, decisions, and state changes are logged for transparency.
'''

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    '''Logging detail levels.'''
    MINIMAL = 'minimal'      # Only critical events (wins, losses, major milestones)
    STANDARD = 'standard'    # Standard gameplay logging (actions, resource changes)
    VERBOSE = 'verbose'      # Detailed logging (all calculations, RNG calls)
    DEBUG = 'debug'         # Everything (internal state, performance metrics)


@dataclass
class GameAction:
    '''Structured representation of a game action.'''
    turn: int
    action_name: str
    cost: int
    ap_cost: int
    result: Dict[str, Any]
    timestamp: str
    rng_context: Optional[str] = None
    
    
@dataclass
class ResourceChange:
    '''Structured representation of resource changes.'''
    turn: int
    resource: str
    old_value: int
    new_value: int
    change: int
    reason: str
    timestamp: str


@dataclass
class RandomEvent:
    '''Structured representation of random events and RNG calls.'''
    turn: int
    context: str
    rng_function: str
    parameters: Dict[str, Any]
    result: Any
    seed_info: Dict[str, Any]
    timestamp: str


class VerboseLogger:
    '''
    Comprehensive logging system for game transparency and debugging.
    
    Features:
    - Structured JSON logging for machine processing
    - Human-readable summary logs
    - Configurable verbosity levels
    - Privacy-respecting data collection
    - Competitive verification support
    '''
    
    def __init__(self, 
                 game_seed: str,
                 log_level: LogLevel = LogLevel.STANDARD,
                 enable_human_readable: bool = True,
                 enable_json_export: bool = True):
        '''Initialize logging system.'''
        self.game_seed = game_seed
        self.log_level = log_level
        self.enable_human_readable = enable_human_readable
        self.enable_json_export = enable_json_export
        
        # Create logs directory
        self.logs_dir = 'logs'
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize log storage
        self.actions_log: List[GameAction] = []
        self.resource_changes_log: List[ResourceChange] = []
        self.random_events_log: List[RandomEvent] = []
        self.game_metadata = {
            'game_seed': game_seed,
            'log_level': log_level.value,
            'start_time': datetime.now().isoformat(),
            'version': self._get_game_version()
        }
        
        # Set up file logging
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_filename = f'game_{game_seed}_{timestamp}'
        
        if enable_human_readable:
            self._setup_human_readable_logger()
    
    def _get_game_version(self) -> str:
        '''Get current game version.'''
        try:
            from src.services.version import get_display_version
            return get_display_version()
        except ImportError:
            return 'unknown'
    
    def _setup_human_readable_logger(self):
        '''Set up human-readable logging.'''
        log_file = os.path.join(self.logs_dir, f'{self.log_filename}.log')
        
        # Configure logger
        self.logger = logging.getLogger(f'pdoom_{self.game_seed}')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s [T%(turn)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log_action(self, 
                   turn: int,
                   action_name: str, 
                   cost: int, 
                   ap_cost: int, 
                   result: Dict[str, Any],
                   rng_context: Optional[str] = None):
        '''Log a game action.'''
        action = GameAction(
            turn=turn,
            action_name=action_name,
            cost=cost,
            ap_cost=ap_cost,
            result=result,
            timestamp=datetime.now().isoformat(),
            rng_context=rng_context
        )
        
        self.actions_log.append(action)
        
        if self.enable_human_readable and self.log_level.value in ['standard', 'verbose', 'debug']:
            self.logger.info(
                f'Action: {action_name} (${cost}, {ap_cost}AP) -> {result}',
                extra={'turn': turn}
            )
    
    def log_resource_change(self,
                           turn: int,
                           resource: str,
                           old_value: int,
                           new_value: int,
                           reason: str):
        '''Log a resource change.'''
        change = ResourceChange(
            turn=turn,
            resource=resource,
            old_value=old_value,
            new_value=new_value,
            change=new_value - old_value,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
        
        self.resource_changes_log.append(change)
        
        if self.enable_human_readable and self.log_level.value in ['verbose', 'debug']:
            change_str = f'+{change.change}' if change.change >= 0 else str(change.change)
            self.logger.debug(
                f'Resource: {resource} {old_value} -> {new_value} ({change_str}) [{reason}]',
                extra={'turn': turn}
            )
    
    def log_random_event(self,
                        turn: int,
                        context: str,
                        rng_function: str,
                        parameters: Dict[str, Any],
                        result: Any,
                        seed_info: Dict[str, Any]):
        '''Log a random number generation event.'''
        event = RandomEvent(
            turn=turn,
            context=context,
            rng_function=rng_function,
            parameters=parameters,
            result=result,
            seed_info=seed_info,
            timestamp=datetime.now().isoformat()
        )
        
        self.random_events_log.append(event)
        
        if self.enable_human_readable and self.log_level.value in ['debug']:
            self.logger.debug(
                f'RNG: {rng_function}({parameters}) = {result} [ctx: {context}]',
                extra={'turn': turn}
            )
    
    def log_game_event(self, turn: int, level: str, message: str, data: Dict[str, Any] = None):
        '''Log a general game event.'''
        if not self.enable_human_readable:
            return
            
        # Map level to logging levels
        level_map = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }
        
        log_level = level_map.get(level, logging.INFO)
        
        if data:
            message = f'{message} | Data: {data}'
            
        self.logger.log(log_level, message, extra={'turn': turn})
    
    def export_json_logs(self) -> str:
        '''Export all logs as JSON for analysis.'''
        if not self.enable_json_export:
            return ''
            
        export_data = {
            'metadata': self.game_metadata,
            'actions': [asdict(action) for action in self.actions_log],
            'resource_changes': [asdict(change) for change in self.resource_changes_log],
            'random_events': [asdict(event) for event in self.random_events_log]
        }
        
        json_file = os.path.join(self.logs_dir, f'{self.log_filename}.json')
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return json_file
    
    def get_game_summary(self) -> Dict[str, Any]:
        '''Generate summary statistics for competitive verification.'''
        return {
            'seed': self.game_seed,
            'total_actions': len(self.actions_log),
            'total_turns': max((a.turn for a in self.actions_log), default=0),
            'action_breakdown': self._get_action_breakdown(),
            'resource_summary': self._get_resource_summary(),
            'rng_calls': len(self.random_events_log),
            'log_checksum': self._calculate_log_checksum()
        }
    
    def _get_action_breakdown(self) -> Dict[str, int]:
        '''Get count of each action type.'''
        breakdown = {}
        for action in self.actions_log:
            breakdown[action.action_name] = breakdown.get(action.action_name, 0) + 1
        return breakdown
    
    def _get_resource_summary(self) -> Dict[str, Dict[str, int]]:
        '''Get resource change summary.'''
        summary = {}
        for change in self.resource_changes_log:
            if change.resource not in summary:
                summary[change.resource] = {'total_change': 0, 'transactions': 0}
            summary[change.resource]['total_change'] += change.change
            summary[change.resource]['transactions'] += 1
        return summary
    
    def _calculate_log_checksum(self) -> str:
        '''Calculate checksum for log integrity verification.'''
        import hashlib
        
        # Create deterministic string representation of logs
        log_string = json.dumps({
            'actions': [asdict(a) for a in self.actions_log],
            'resources': [asdict(r) for r in self.resource_changes_log],
            'rng': [asdict(e) for e in self.random_events_log]
        }, sort_keys=True)
        
        return hashlib.sha256(log_string.encode()).hexdigest()[:16]

    def close(self):
        '''Close all file handlers properly.'''
        try:
            # Close all file handlers
            for handler in self.logger.handlers[:]:
                if hasattr(handler, 'close'):
                    handler.close()
                self.logger.removeHandler(handler)
            
            if self.game_log_file:
                try:
                    self.game_log_file.close()
                except:
                    pass
                self.game_log_file = None
                
        except Exception as e:
            # Fail silently - cleanup is best effort
            pass


# Global logger instance
verbose_logger: Optional[VerboseLogger] = None


def init_verbose_logging(game_seed: str, 
                        log_level: LogLevel = LogLevel.STANDARD,
                        enable_human_readable: bool = True,
                        enable_json_export: bool = True):
    '''Initialize verbose logging system.'''
    global verbose_logger
    verbose_logger = VerboseLogger(
        game_seed=game_seed,
        log_level=log_level,
        enable_human_readable=enable_human_readable,
        enable_json_export=enable_json_export
    )


def get_logger() -> VerboseLogger:
    '''Get current verbose logger instance.'''
    if verbose_logger is None:
        raise RuntimeError('Verbose logger not initialized. Call init_verbose_logging() first.')
    return verbose_logger


def is_logging_enabled() -> bool:
    '''Check if verbose logging is enabled.'''
    return verbose_logger is not None

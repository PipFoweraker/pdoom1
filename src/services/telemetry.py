'''
Telemetry and logging service for PDoom1.

Provides JSONL logging with automatic size management and retention.
Respects user privacy settings and provides opt-out functionality.
'''

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.services.data_paths import get_logs_dir
from src.services.settings import Settings


class TelemetryLogger:
    '''
    Privacy-conscious telemetry logger with automatic log rotation.
    
    Features:
    - JSONL format for easy parsing
    - 10MB total log size cap with automatic cleanup
    - Respects user opt-out preferences
    - Automatic log file rotation
    - Device UUID association for analytics
    '''
    
    MAX_TOTAL_SIZE = 10 * 1024 * 1024  # 10MB total cap
    MAX_SINGLE_LOG_SIZE = 2 * 1024 * 1024  # 2MB per file before rotation
    LOG_FILE_PREFIX = 'telemetry_'
    
    def __init__(self, settings: Optional[Settings] = None):
        '''
        Initialize telemetry logger.
        
        Args:
            settings: Settings instance (creates new one if None)
        '''
        self.settings = settings or Settings()
        self.logs_dir = get_logs_dir()
        self.current_log_file = self._get_current_log_file()
        
        # Clean up old logs if over size limit
        self._cleanup_logs()
    
    def _get_current_log_file(self) -> Path:
        '''Get the current log file path.'''
        timestamp = datetime.now().strftime('%Y%m%d')
        return self.logs_dir / f'{self.LOG_FILE_PREFIX}{timestamp}.jsonl'
    
    def _get_log_files(self) -> List[Path]:
        '''Get all telemetry log files, sorted by modification time (oldest first).'''
        log_files = list(self.logs_dir.glob(f'{self.LOG_FILE_PREFIX}*.jsonl'))
        return sorted(log_files, key=lambda f: f.stat().st_mtime)
    
    def _get_total_log_size(self) -> int:
        '''Calculate total size of all log files.'''
        total_size = 0
        for log_file in self._get_log_files():
            try:
                total_size += log_file.stat().st_size
            except OSError:
                pass  # File might have been deleted
        return total_size
    
    def _cleanup_logs(self) -> None:
        '''Remove oldest log files if over the size limit.'''
        log_files = self._get_log_files()
        total_size = self._get_total_log_size()
        
        # Remove oldest files until under limit
        while total_size > self.MAX_TOTAL_SIZE and log_files:
            oldest_file = log_files.pop(0)
            try:
                file_size = oldest_file.stat().st_size
                oldest_file.unlink()
                total_size -= file_size
                print(f'Removed old log file: {oldest_file.name}')
            except OSError as e:
                print(f'Warning: Could not remove log file {oldest_file}: {e}')
    
    def _rotate_log_if_needed(self) -> None:
        '''Rotate to a new log file if current one is too large.'''
        if not self.current_log_file.exists():
            return
            
        try:
            if self.current_log_file.stat().st_size > self.MAX_SINGLE_LOG_SIZE:
                # Force new log file with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                self.current_log_file = self.logs_dir / f'{self.LOG_FILE_PREFIX}{timestamp}.jsonl'
        except OSError:
            pass  # Continue with current file
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        '''
        Log a telemetry event.
        
        Args:
            event_type: Type of event (e.g., 'game_start', 'level_complete')
            data: Event data to log
            
        Returns:
            True if event was logged successfully
        '''
        # Check if telemetry is enabled
        if not self.settings.is_telemetry_enabled():
            return False
        
        # Prepare log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'device_uuid': self.settings.get_device_uuid(),
            'data': data
        }
        
        try:
            # Rotate log if needed
            self._rotate_log_if_needed()
            
            # Append to current log file
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, separators=(',', ':')) + '\n')
            
            # Cleanup if over size limit
            if self._get_total_log_size() > self.MAX_TOTAL_SIZE:
                self._cleanup_logs()
            
            return True
            
        except (IOError, OSError) as e:
            print(f'Warning: Could not write telemetry event: {e}')
            return False
    
    def log_game_start(self, game_mode: str, difficulty: str) -> bool:
        '''Log game start event.'''
        return self.log_event('game_start', {
            'game_mode': game_mode,
            'difficulty': difficulty
        })
    
    def log_game_end(self, duration_seconds: float, score: int, reason: str) -> bool:
        '''Log game end event.'''
        return self.log_event('game_end', {
            'duration_seconds': duration_seconds,
            'score': score,
            'reason': reason  # 'completed', 'quit', 'died', etc.
        })
    
    def log_level_complete(self, level: int, time_seconds: float, score: int) -> bool:
        '''Log level completion event.'''
        return self.log_event('level_complete', {
            'level': level,
            'time_seconds': time_seconds,
            'score': score
        })
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None) -> bool:
        '''Log error event.'''
        return self.log_event('error', {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        })
    
    def log_settings_change(self, setting: str, old_value: Any, new_value: Any) -> bool:
        '''Log settings change event.'''
        return self.log_event('settings_change', {
            'setting': setting,
            'old_value': old_value,
            'new_value': new_value
        })
    
    def log_performance_metric(self, metric_name: str, value: float, context: Dict[str, Any] = None) -> bool:
        '''Log performance metric.'''
        return self.log_event('performance_metric', {
            'metric_name': metric_name,
            'value': value,
            'context': context or {}
        })
    
    def get_log_summary(self) -> Dict[str, Any]:
        '''Get summary information about current logs.'''
        log_files = self._get_log_files()
        total_size = self._get_total_log_size()
        
        return {
            'total_files': len(log_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'size_limit_mb': round(self.MAX_TOTAL_SIZE / (1024 * 1024), 2),
            'telemetry_enabled': self.settings.is_telemetry_enabled(),
            'oldest_log': log_files[0].name if log_files else None,
            'newest_log': log_files[-1].name if log_files else None
        }
    
    def clear_all_logs(self) -> int:
        '''
        Clear all telemetry logs.
        
        Returns:
            Number of files deleted
        '''
        log_files = self._get_log_files()
        deleted_count = 0
        
        for log_file in log_files:
            try:
                log_file.unlink()
                deleted_count += 1
            except OSError as e:
                print(f'Warning: Could not delete log file {log_file}: {e}')
        
        # Reset current log file
        self.current_log_file = self._get_current_log_file()
        
        return deleted_count
    
    def export_logs(self, output_file: Path) -> bool:
        '''
        Export all logs to a single file.
        
        Args:
            output_file: Path to output file
            
        Returns:
            True if export was successful
        '''
        if not self.settings.is_telemetry_enabled():
            return False
        
        try:
            log_files = self._get_log_files()
            
            with open(output_file, 'w', encoding='utf-8') as out_f:
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as in_f:
                            for line in in_f:
                                out_f.write(line)
                    except OSError as e:
                        print(f'Warning: Could not read log file {log_file}: {e}')
            
            return True
            
        except OSError as e:
            print(f'Error exporting logs: {e}')
            return False
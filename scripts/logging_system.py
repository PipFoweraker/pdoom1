# !/usr/bin/env python3
'''
P(Doom) Centralized Logging System

Provides structured logging for all development tools, CI/CD workflows,
and quality enforcement processes. Designed for industrial-grade
automation and debugging.

Features:
- Structured JSON logging for CI/CD parsing
- Human-readable console output
- File rotation and retention
- Integration with GitHub Actions
- Debug/verbose modes
'''

import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum

class LogLevel(Enum):
    '''Standard log levels with industrial naming.'''
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR' 
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    TRACE = 'TRACE'

class LogCategory(Enum):
    '''Categorized logging for different subsystems.
    
    Logging Directory Structure:
    - logs/quality/   : QUALITY, ASCII, STANDARDS (code quality enforcement)
    - logs/release/   : VERSION, BUILD (release and deployment processes)  
    - logs/testing/   : TESTS (test execution and validation)
    - logs/docs/      : DOCS (documentation generation and processing)
    - logs/dev/       : GENERAL (general development activities)
    '''
    QUALITY = 'QUALITY'      # Quality checks and enforcement
    ASCII = 'ASCII'          # ASCII compliance tools
    STANDARDS = 'STANDARDS'  # Development standards
    VERSION = 'VERSION'      # Version management
    TESTS = 'TESTS'          # Test execution
    BUILD = 'BUILD'          # Build and deployment
    DOCS = 'DOCS'            # Documentation processing
    GENERAL = 'GENERAL'      # General purpose


class PDoomLogger:
    '''Centralized logger for P(Doom) development tools.'''
    
    def __init__(self, 
                 tool_name: str,
                 category: LogCategory = LogCategory.GENERAL,
                 log_level: LogLevel = LogLevel.INFO,
                 log_to_file: bool = True,
                 log_directory: Optional[Path] = None,
                 structured_output: bool = False):
        '''
        Initialize P(Doom) logger.
        
        Args:
            tool_name: Name of the tool using this logger
            category: Log category for filtering/routing
            log_level: Minimum log level to output
            log_to_file: Whether to write to log files
            log_directory: Directory for log files (default: project_root/logs)
            structured_output: Use JSON structured logging
        '''
        self.tool_name = tool_name
        self.category = category
        self.structured_output = structured_output
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Detect project root
        self.project_root = self._find_project_root()
        
        # Set up log directory with category-based subdirectories
        if log_directory is None:
            log_directory = self.project_root / 'logs'
        
        # Create category-specific subdirectories for organized logging
        if category in [LogCategory.QUALITY, LogCategory.ASCII, LogCategory.STANDARDS]:
            # Quality enforcement tools
            log_directory = log_directory / 'quality'
        elif category in [LogCategory.VERSION, LogCategory.BUILD]:
            # Release and deployment processes
            log_directory = log_directory / 'release'
        elif category == LogCategory.TESTS:
            # Test execution and validation
            log_directory = log_directory / 'testing'
        elif category == LogCategory.DOCS:
            # Documentation generation and processing
            log_directory = log_directory / 'docs'
        else:
            # General development logs
            log_directory = log_directory / 'dev'
        
        log_directory.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger(f'pdoom.{tool_name}')
        self.logger.setLevel(getattr(logging, log_level.value))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Console handler with custom formatting
        console_handler = logging.StreamHandler(sys.stdout)
        if structured_output:
            console_handler.setFormatter(self._get_json_formatter())
        else:
            console_handler.setFormatter(self._get_console_formatter())
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if log_to_file:
            log_file = log_directory / f'{tool_name}_{self.session_id}.log'
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB files, keep 5
            )
            file_handler.setFormatter(self._get_json_formatter())
            self.logger.addHandler(file_handler)
            
            # Also create a daily log for aggregation
            daily_log = log_directory / f'daily_{datetime.now().strftime('%Y%m%d')}.log'
            daily_handler = logging.handlers.RotatingFileHandler(
                daily_log, maxBytes=50*1024*1024, backupCount=30  # 50MB daily files
            )
            daily_handler.setFormatter(self._get_json_formatter())
            self.logger.addHandler(daily_handler)
        
        # Log session start
        self._log_session_start()
    
    def _find_project_root(self) -> Path:
        '''Find the project root directory.'''
        current = Path(__file__).parent
        while current != current.parent:
            if (current / '.git').exists() or (current / 'main.py').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _get_console_formatter(self) -> logging.Formatter:
        '''Get human-readable console formatter.'''
        return logging.Formatter(
            fmt='[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _get_json_formatter(self) -> logging.Formatter:
        '''Get structured JSON formatter for file output.'''
        class JsonFormatter(logging.Formatter):
            def __init__(self, category, session_id):
                super().__init__()
                self.category = category
                self.session_id = session_id
            
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'tool': record.name,
                    'category': self.category.value,
                    'session_id': self.session_id,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # Add exception info if present
                if record.exc_info:
                    log_entry['exception'] = self.formatException(record.exc_info)
                
                # Add extra fields if present
                if hasattr(record, 'extra_data'):
                    log_entry['extra'] = record.extra_data
                
                return json.dumps(log_entry)
        
        return JsonFormatter(self.category, self.session_id)
    
    def _log_session_start(self):
        '''Log session initialization.'''
        self.info('Logging session started', extra_data={
            'tool_name': self.tool_name,
            'category': self.category.value,
            'session_id': self.session_id,
            'project_root': str(self.project_root),
            'python_version': sys.version,
            'platform': sys.platform
        })
    
    # Standard logging methods with extra context
    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log critical error.'''
        self._log_with_extra(logging.CRITICAL, message, extra_data)
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log error.'''
        self._log_with_extra(logging.ERROR, message, extra_data)
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log warning.'''
        self._log_with_extra(logging.WARNING, message, extra_data)
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log info.'''
        self._log_with_extra(logging.INFO, message, extra_data)
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log debug.'''
        self._log_with_extra(logging.DEBUG, message, extra_data)
    
    def trace(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log trace (debug level with trace marker).'''
        message = f'[TRACE] {message}'
        self._log_with_extra(logging.DEBUG, message, extra_data)
    
    def _log_with_extra(self, level: int, message: str, extra_data: Optional[Dict[str, Any]]):
        '''Internal method to log with extra data.'''
        if extra_data:
            # Create a LogRecord with extra data
            record = self.logger.makeRecord(
                self.logger.name, level, __file__, 0, message, (), None
            )
            record.extra_data = extra_data
            self.logger.handle(record)
        else:
            self.logger.log(level, message)
    
    # Specialized logging methods for common CI/CD scenarios
    def step_start(self, step_name: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log the start of a processing step.'''
        extra = {'step_name': step_name, 'step_status': 'STARTED'}
        if extra_data:
            extra.update(extra_data)
        self.info(f'STEP START: {step_name}', extra_data=extra)
    
    def step_success(self, step_name: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log successful step completion.'''
        extra = {'step_name': step_name, 'step_status': 'SUCCESS'}
        if extra_data:
            extra.update(extra_data)
        self.info(f'STEP SUCCESS: {step_name}', extra_data=extra)
    
    def step_failure(self, step_name: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log step failure.'''
        extra = {'step_name': step_name, 'step_status': 'FAILURE'}
        if extra_data:
            extra.update(extra_data)
        self.error(f'STEP FAILURE: {step_name}', extra_data=extra)
    
    def metrics(self, metric_name: str, value: Union[int, float, str], 
                unit: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None):
        '''Log metrics for monitoring.'''
        metric_data = {
            'metric_name': metric_name,
            'metric_value': value,
            'metric_unit': unit or 'count'
        }
        if extra_data:
            metric_data.update(extra_data)
        
        self.info(f'METRIC: {metric_name} = {value} {unit or ''}', extra_data=metric_data)
    
    def performance(self, operation: str, duration_ms: float, 
                   extra_data: Optional[Dict[str, Any]] = None):
        '''Log performance data.'''
        perf_data = {
            'operation': operation,
            'duration_ms': duration_ms,
            'performance_category': 'timing'
        }
        if extra_data:
            perf_data.update(extra_data)
        
        self.info(f'PERFORMANCE: {operation} took {duration_ms:.2f}ms', extra_data=perf_data)
    
    def command_start(self, command: str, args: Optional[Dict[str, Any]] = None):
        '''Log command execution start.'''
        cmd_data = {'command': command, 'command_status': 'STARTED'}
        if args:
            cmd_data['command_args'] = args
        self.info(f'COMMAND START: {command}', extra_data=cmd_data)
    
    def command_result(self, command: str, exit_code: int, 
                      stdout: Optional[str] = None, stderr: Optional[str] = None):
        '''Log command execution result.'''
        cmd_data = {
            'command': command,
            'exit_code': exit_code,
            'command_status': 'SUCCESS' if exit_code == 0 else 'FAILURE'
        }
        
        if stdout:
            cmd_data['stdout'] = stdout[-1000:]  # Last 1000 chars
        if stderr:
            cmd_data['stderr'] = stderr[-1000:]  # Last 1000 chars
        
        if exit_code == 0:
            self.info(f'COMMAND SUCCESS: {command}', extra_data=cmd_data)
        else:
            self.error(f'COMMAND FAILURE: {command} (exit code {exit_code})', extra_data=cmd_data)
    
    def file_operation(self, operation: str, file_path: str, 
                      result: str, extra_data: Optional[Dict[str, Any]] = None):
        '''Log file operations.'''
        file_data = {
            'file_operation': operation,
            'file_path': file_path,
            'operation_result': result
        }
        if extra_data:
            file_data.update(extra_data)
        
        self.info(f'FILE {operation.upper()}: {file_path} - {result}', extra_data=file_data)
    
    def github_action_output(self, name: str, value: str):
        '''Output GitHub Actions workflow variables.'''
        # GitHub Actions output format
        print(f'::set-output name={name}::{value}')
        
        # Also log normally
        self.info(f'GitHub Action Output: {name} = {value}', extra_data={
            'github_output_name': name,
            'github_output_value': value
        })
    
    def github_action_error(self, message: str, file_path: Optional[str] = None, 
                           line: Optional[int] = None):
        '''Output GitHub Actions error annotation.'''
        annotation = f'::error'
        if file_path:
            annotation += f' file={file_path}'
        if line:
            annotation += f',line={line}'
        annotation += f'::{message}'
        
        print(annotation)
        self.error(f'GitHub Action Error: {message}', extra_data={
            'github_annotation': True,
            'file_path': file_path,
            'line_number': line
        })
    
    def github_action_warning(self, message: str, file_path: Optional[str] = None, 
                             line: Optional[int] = None):
        '''Output GitHub Actions warning annotation.'''
        annotation = f'::warning'
        if file_path:
            annotation += f' file={file_path}'
        if line:
            annotation += f',line={line}'
        annotation += f'::{message}'
        
        print(annotation)
        self.warning(f'GitHub Action Warning: {message}', extra_data={
            'github_annotation': True,
            'file_path': file_path,
            'line_number': line
        })
    
    def session_summary(self, success: bool, extra_data: Optional[Dict[str, Any]] = None):
        '''Log session completion summary.'''
        session_data = {
            'session_success': success,
            'session_id': self.session_id,
            'session_duration': 'calculated_by_log_parser'  # Post-processing
        }
        if extra_data:
            session_data.update(extra_data)
        
        if success:
            self.info('Session completed successfully', extra_data=session_data)
        else:
            self.error('Session completed with failures', extra_data=session_data)


def get_logger(tool_name: str, 
               category: LogCategory = LogCategory.GENERAL,
               verbose: bool = False,
               structured: bool = False) -> PDoomLogger:
    '''
    Convenience function to get a configured logger.
    
    Args:
        tool_name: Name of the tool requesting the logger
        category: Category for log filtering
        verbose: Enable debug/trace logging
        structured: Use JSON structured output to console
    
    Returns:
        Configured PDoomLogger instance
    '''
    log_level = LogLevel.DEBUG if verbose else LogLevel.INFO
    
    # Check for CI environment
    is_ci = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
    if is_ci:
        structured = True  # Force structured logging in CI
    
    return PDoomLogger(
        tool_name=tool_name,
        category=category,
        log_level=log_level,
        structured_output=structured
    )


# Context manager for timed operations
class TimedOperation:
    '''Context manager for timing operations with automatic logging.'''
    
    def __init__(self, logger: PDoomLogger, operation_name: str, 
                 extra_data: Optional[Dict[str, Any]] = None):
        self.logger = logger
        self.operation_name = operation_name
        self.extra_data = extra_data or {}
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.step_start(self.operation_name, self.extra_data)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration_ms = (time.time() - self.start_time) * 1000
        
        result_data = {**self.extra_data, 'duration_ms': duration_ms}
        
        if exc_type is None:
            self.logger.step_success(self.operation_name, result_data)
            self.logger.performance(self.operation_name, duration_ms)
        else:
            result_data['exception_type'] = exc_type.__name__ if exc_type else None
            result_data['exception_message'] = str(exc_val) if exc_val else None
            self.logger.step_failure(self.operation_name, result_data)


if __name__ == '__main__':
    # Test the logging system
    logger = get_logger('test_logging', LogCategory.QUALITY, verbose=True)
    
    logger.info('Testing P(Doom) logging system')
    
    with TimedOperation(logger, 'test_operation'):
        import time
        time.sleep(0.1)  # Simulate work
    
    logger.metrics('test_metric', 42, 'items')
    logger.performance('test_perf', 123.45)
    logger.session_summary(True, {'tests_run': 10, 'tests_passed': 10})
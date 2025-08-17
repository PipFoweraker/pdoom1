"""
Runtime paths facade for PDoom1.

Provides simple access to save and log paths with automatic migration handling.
This module serves as the primary interface for accessing runtime data locations.
"""

import logging
from pathlib import Path
from typing import Optional

from pdoom1.services.data_paths import get_data_dir, get_save_dir, get_log_dir
from pdoom1.services.migration import MigrationAdapter


# Global migration adapter instance
_migration_adapter: Optional[MigrationAdapter] = None


def _get_migration_adapter() -> MigrationAdapter:
    """Get or create the global migration adapter."""
    global _migration_adapter
    if _migration_adapter is None:
        _migration_adapter = MigrationAdapter()
    return _migration_adapter


def _ensure_migration() -> None:
    """
    Ensure migration has been performed if needed.
    
    This function is called automatically by path accessors to ensure
    legacy data is migrated before first use.
    """
    adapter = _get_migration_adapter()
    
    if adapter.needs_migration():
        try:
            result = adapter.migrate(copy_instead_of_move=True)
            
            # Log migration completion - single notice only
            if result.files_copied > 0:
                logger = logging.getLogger(__name__)
                logger.info(f"MIGRATION: Successfully copied {result.files_copied} legacy file(s) to {result.target_dir}")
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Migration failed: {e}")


def get_save_path(name: str) -> Path:
    """
    Get the full path for a save file.
    
    Args:
        name: Name of the save file (without extension)
        
    Returns:
        Path to the save file
    """
    _ensure_migration()
    save_dir = get_save_dir()
    
    # Add .json extension if not present
    if not name.endswith('.json'):
        name = f"{name}.json"
    
    return save_dir / name


def get_log_path(name: str) -> Path:
    """
    Get the full path for a log file.
    
    Args:
        name: Name of the log file (with or without extension)
        
    Returns:
        Path to the log file
    """
    _ensure_migration()
    log_dir = get_log_dir()
    
    # Add .txt extension if no extension present
    if '.' not in name:
        name = f"{name}.txt"
    
    return log_dir / name


def get_data_path(name: str) -> Path:
    """
    Get the full path for a data file in the root data directory.
    
    Args:
        name: Name of the data file
        
    Returns:
        Path to the data file
    """
    _ensure_migration()
    return get_data_dir() / name


# Convenience aliases for backwards compatibility
def get_data_directory() -> Path:
    """Get the data directory (alias for get_data_dir)."""
    _ensure_migration()
    return get_data_dir()


def get_save_directory() -> Path:
    """Get the save directory (alias for get_save_dir)."""
    _ensure_migration()
    return get_save_dir()


def get_log_directory() -> Path:
    """Get the log directory (alias for get_log_dir)."""
    _ensure_migration()
    return get_log_dir()
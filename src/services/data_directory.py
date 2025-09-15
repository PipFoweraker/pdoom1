"""Runtime Data Directory Management

This module provides OS-appropriate data directory management for P(Doom)
with support for legacy file migration.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import platform

logger = logging.getLogger(__name__)


class DataDirectoryManager:
    """Manages runtime data storage with OS-appropriate directories."""
    
    def __init__(self):
        """Initialise the data directory manager."""
        self._app_name = "pdoom1"
        self._data_dir = self._get_data_directory()
        self._ensure_data_directory()
        
    def _get_data_directory(self) -> Path:
        """Get OS-appropriate data directory for P(Doom)."""
        # Check for development override first
        if 'PDOOM1_DATA_DIR' in os.environ:
            return Path(os.environ['PDOOM1_DATA_DIR'])
            
        system = platform.system()
        
        if system == "Windows":
            # Use AppData/Local for Windows
            base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
            return Path(base) / self._app_name
            
        elif system == "Darwin":  # macOS
            # Use Application Support for macOS
            return Path.home() / "Library" / "Application Support" / self._app_name
            
        else:  # Linux and other Unix systems
            # Use XDG Base Directory Specification
            xdg_data_home = os.environ.get('XDG_DATA_HOME')
            if xdg_data_home:
                return Path(xdg_data_home) / self._app_name
            else:
                return Path.home() / ".local" / "share" / self._app_name
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['configs', 'logs', 'leaderboards', 'sessions', 'saves']
        for subdir in subdirs:
            (self._data_dir / subdir).mkdir(exist_ok=True)
            
        logger.info(f"Data directory initialised: {self._data_dir}")
    
    def get_data_path(self, filename: str) -> Path:
        """Get the full path for a data file in the runtime directory."""
        return self._data_dir / filename
    
    def get_legacy_path(self, filename: str) -> Path:
        """Get the legacy path (relative to game directory)."""
        return Path.cwd() / filename
    
    def migrate_file_if_needed(self, filename: str, 
                              show_migration_notice: bool = True) -> Path:
        """
        Get the appropriate path for a file, migrating from legacy location if needed.
        
        Args:
            filename: Name of the file (e.g., 'onboarding_progress.json')
            show_migration_notice: Whether to show a one-time migration notice
            
        Returns:
            Path to use for the file (always in new location after migration)
        """
        new_path = self.get_data_path(filename)
        legacy_path = self.get_legacy_path(filename)
        
        # If new path exists, use it
        if new_path.exists():
            return new_path
            
        # If legacy path exists, migrate it
        if legacy_path.exists():
            try:
                # Copy the file to new location
                shutil.copy2(legacy_path, new_path)
                
                # Show migration notice if requested
                if show_migration_notice:
                    self._show_migration_notice(filename, legacy_path, new_path)
                
                logger.info(f"Migrated {filename} from {legacy_path} to {new_path}")
                
                # Note: We don't delete the legacy file immediately for safety
                # User can clean up manually after verifying migration worked
                
            except Exception as e:
                logger.error(f"Failed to migrate {filename}: {e}")
                # Fall back to legacy path if migration fails
                return legacy_path
        
        # Return new path (which may not exist yet - that's OK for new files)
        return new_path
    
    def _show_migration_notice(self, filename: str, old_path: Path, new_path: Path):
        """Show a one-time migration notice to the user."""
        notice_file = self._data_dir / ".migration_notices_shown"
        
        # Track which notices we've shown
        shown_notices = set()
        if notice_file.exists():
            try:
                with open(notice_file, 'r') as f:
                    shown_notices = set(json.load(f))
            except:
                pass
        
        # Only show notice once per file
        if filename not in shown_notices:
            print(f"\n📁 Data Migration Notice:")
            print(f"   Moved {filename}")
            print(f"   From: {old_path}")
            print(f"   To:   {new_path}")
            print(f"   (This ensures your data is stored in the appropriate system location)")
            
            # Record that we've shown this notice
            shown_notices.add(filename)
            try:
                with open(notice_file, 'w') as f:
                    json.dump(list(shown_notices), f)
            except:
                pass  # Don't fail if we can't save the notice record
    
    def get_config_path(self, config_name: str = "default.json") -> Path:
        """Get path for configuration file."""
        return self.migrate_file_if_needed(f"configs/{config_name}")
    
    def get_save_path(self, save_name: str) -> Path:
        """Get path for save file."""
        return self.get_data_path(f"saves/{save_name}")
    
    def get_log_path(self, log_name: str) -> Path:
        """Get path for log file."""
        return self.get_data_path(f"logs/{log_name}")
    
    def get_leaderboard_path(self, leaderboard_name: str = "leaderboard.json") -> Path:
        """Get path for leaderboard file."""
        return self.migrate_file_if_needed(f"leaderboards/{leaderboard_name}")
    
    def get_session_path(self, session_name: str) -> Path:
        """Get path for session file."""
        return self.get_data_path(f"sessions/{session_name}")
    
    def get_settings_path(self, settings_name: str) -> Path:
        """Get path for settings file."""
        return self.migrate_file_if_needed(settings_name)
    
    @property
    def data_directory(self) -> Path:
        """Get the main data directory path."""
        return self._data_dir
    
    def cleanup_legacy_files(self, confirm: bool = False) -> int:
        """
        Clean up legacy files after successful migration.
        
        Args:
            confirm: If True, actually delete files. If False, just return count.
            
        Returns:
            Number of legacy files that would be/were deleted
        """
        legacy_files = [
            "onboarding_progress.json",
            "tutorial_settings.json", 
            "local_highscore.json",
            "configs/default.json"
        ]
        
        count = 0
        for filename in legacy_files:
            legacy_path = self.get_legacy_path(filename)
            if legacy_path.exists():
                if confirm:
                    try:
                        legacy_path.unlink()
                        logger.info(f"Deleted legacy file: {legacy_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete {legacy_path}: {e}")
                count += 1
        
        return count


# Global instance
_data_manager: Optional[DataDirectoryManager] = None


def get_data_manager() -> DataDirectoryManager:
    """Get the global data directory manager instance."""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataDirectoryManager()
    return _data_manager


def get_data_path(filename: str) -> Path:
    """Convenience function to get a data file path."""
    return get_data_manager().get_data_path(filename)


def migrate_file_if_needed(filename: str) -> Path:
    """Convenience function to migrate a file if needed."""
    return get_data_manager().migrate_file_if_needed(filename)

"""
Legacy data migration utilities for PDoom1.

Handles discovery and migration of legacy save and log files to the new
standardised data directory structure.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

from .data_paths import get_data_dir, get_save_dir, get_log_dir


class MigrationResult(NamedTuple):
    """Result of a migration operation."""
    files_copied: int
    legacy_paths_found: List[Path]
    target_dir: Path
    marker_created: bool


def locate_legacy_paths(base_cwd: Optional[Path] = None) -> List[Path]:
    """
    Locate likely legacy file and directory locations.
    
    Args:
        base_cwd: Base directory to search for legacy paths (defaults to cwd)
        
    Returns:
        List of Path objects representing legacy files and directories
    """
    if base_cwd is None:
        base_cwd = Path.cwd()
    
    legacy_paths = []
    
    # Legacy directory patterns to search for
    legacy_dirs = ["saves", "save", "logs", "runtime"]
    
    for dir_name in legacy_dirs:
        legacy_path = base_cwd / dir_name
        if legacy_path.exists() and legacy_path.is_dir():
            legacy_paths.append(legacy_path)
    
    # Legacy files in repo root
    legacy_files = [
        "local_highscore.json",
        "onboarding_progress.json",
        "tutorial_settings.json",
        "game_settings.json"
    ]
    
    for file_name in legacy_files:
        legacy_file = base_cwd / file_name
        if legacy_file.exists() and legacy_file.is_file():
            legacy_paths.append(legacy_file)
    
    return legacy_paths


class MigrationAdapter:
    """
    Adapter for migrating legacy data to new directory structure.
    
    Handles discovery, copying (not moving), and tracking of migration status.
    """
    
    MARKER_FILE = ".migration_done"
    
    def __init__(self, base_cwd: Optional[Path] = None):
        """
        Initialise migration adapter.
        
        Args:
            base_cwd: Base directory to search for legacy files
        """
        self.base_cwd = base_cwd or Path.cwd()
        self.data_dir = get_data_dir()
        self.save_dir = get_save_dir()
        self.log_dir = get_log_dir()
        self.logger = logging.getLogger(__name__)
    
    def needs_migration(self) -> bool:
        """
        Check if migration is needed.
        
        Returns:
            True if legacy files exist and migration hasn't been completed
        """
        # If already migrated, no need to migrate again
        if self.is_migrated():
            return False
        
        # Check if any legacy paths exist
        legacy_paths = locate_legacy_paths(self.base_cwd)
        return len(legacy_paths) > 0
    
    def is_migrated(self) -> bool:
        """
        Check if migration has already been completed.
        
        Returns:
            True if migration marker exists
        """
        marker_path = self.data_dir / self.MARKER_FILE
        return marker_path.exists()
    
    def migrate(self, copy_instead_of_move: bool = True) -> MigrationResult:
        """
        Perform migration of legacy files to new data directory.
        
        Args:
            copy_instead_of_move: If True, copy files instead of moving them
            
        Returns:
            MigrationResult with details of the migration
        """
        legacy_paths = locate_legacy_paths(self.base_cwd)
        files_copied = 0
        
        if not legacy_paths:
            self.logger.info("No legacy files found to migrate")
            return MigrationResult(0, [], self.data_dir, False)
        
        # If already migrated, don't migrate again
        if self.is_migrated():
            self.logger.debug("Migration already completed, skipping")
            return MigrationResult(0, legacy_paths, self.data_dir, False)
        
        # Log migration start
        self.logger.info(f"MIGRATION: Copying {len(legacy_paths)} legacy file(s) to {self.data_dir}")
        
        for legacy_path in legacy_paths:
            try:
                if legacy_path.is_file():
                    files_copied += self._migrate_file(legacy_path, copy_instead_of_move)
                elif legacy_path.is_dir():
                    files_copied += self._migrate_directory(legacy_path, copy_instead_of_move)
            except Exception as e:
                self.logger.warning(f"Failed to migrate {legacy_path}: {e}")
        
        # Create migration marker
        marker_created = self._create_migration_marker(files_copied, legacy_paths)
        
        return MigrationResult(files_copied, legacy_paths, self.data_dir, marker_created)
    
    def _migrate_file(self, legacy_file: Path, copy_mode: bool) -> int:
        """
        Migrate a single file.
        
        Args:
            legacy_file: Path to legacy file
            copy_mode: If True, copy instead of move
            
        Returns:
            Number of files processed (0 or 1)
        """
        # Determine target location based on file type
        if legacy_file.name.endswith('.json'):
            # JSON files go to data directory root
            target_path = self.data_dir / legacy_file.name
        else:
            # Other files go to data directory
            target_path = self.data_dir / legacy_file.name
        
        # Don't overwrite existing files
        if target_path.exists():
            self.logger.debug(f"Skipping {legacy_file} - target already exists")
            return 0
        
        if copy_mode:
            shutil.copy2(legacy_file, target_path)
        else:
            shutil.move(str(legacy_file), str(target_path))
        
        return 1
    
    def _migrate_directory(self, legacy_dir: Path, copy_mode: bool) -> int:
        """
        Migrate a directory and its contents.
        
        Args:
            legacy_dir: Path to legacy directory
            copy_mode: If True, copy instead of move
            
        Returns:
            Number of files processed
        """
        files_copied = 0
        
        # Determine target directory based on name
        if legacy_dir.name in ["logs", "log"]:
            target_dir = self.log_dir
        elif legacy_dir.name in ["saves", "save"]:
            target_dir = self.save_dir
        else:
            # Generic runtime directory
            target_dir = self.data_dir / legacy_dir.name
            target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files from legacy directory
        for file_path in legacy_dir.iterdir():
            if file_path.is_file():
                target_file = target_dir / file_path.name
                
                # Don't overwrite existing files
                if target_file.exists():
                    self.logger.debug(f"Skipping {file_path} - target already exists")
                    continue
                
                if copy_mode:
                    shutil.copy2(file_path, target_file)
                else:
                    shutil.move(str(file_path), str(target_file))
                
                files_copied += 1
        
        return files_copied
    
    def _create_migration_marker(self, files_copied: int, legacy_paths: List[Path]) -> bool:
        """
        Create migration completion marker file.
        
        Args:
            files_copied: Number of files that were copied
            legacy_paths: List of legacy paths that were processed
            
        Returns:
            True if marker was created successfully
        """
        try:
            marker_path = self.data_dir / self.MARKER_FILE
            timestamp = datetime.now().isoformat()
            
            marker_content = [
                f"# PDoom1 Migration Completed",
                f"# Timestamp: {timestamp}",
                f"# Files copied: {files_copied}",
                f"# Legacy paths processed: {len(legacy_paths)}",
                ""
            ]
            
            for path in legacy_paths:
                marker_content.append(f"# {path}")
            
            marker_path.write_text("\n".join(marker_content))
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to create migration marker: {e}")
            return False
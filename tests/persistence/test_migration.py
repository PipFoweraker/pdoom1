"""Tests for legacy data migration functionality."""

import json
import logging
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pdoom1.services.migration import MigrationAdapter, locate_legacy_paths


class TestLegacyMigration(unittest.TestCase):
    """Test legacy data migration functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directories."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        
        # Set up isolated data directory for testing
        self.data_dir = self.base_path / "data"
        os.environ["PDOOM1_DATA_DIR"] = str(self.data_dir)
        
        self.adapter = MigrationAdapter(base_cwd=self.base_path)
        
        # Capture log output
        self.log_capture = []
        handler = logging.StreamHandler()
        handler.emit = lambda record: self.log_capture.append(record.getMessage())
        
        logger = logging.getLogger("pdoom1.services.migration")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def tearDown(self):
        """Clean up test environment."""
        self.temp_dir.cleanup()
        if "PDOOM1_DATA_DIR" in os.environ:
            del os.environ["PDOOM1_DATA_DIR"]
    
    def create_legacy_file(self, path: Path, content: str = "test content"):
        """Helper to create a legacy file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    def create_legacy_json(self, path: Path, data: dict):
        """Helper to create a legacy JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
    
    def test_locate_legacy_paths_empty(self):
        """Test legacy path discovery with no legacy files."""
        result = locate_legacy_paths(self.base_path)
        self.assertEqual(result, [])
    
    def test_locate_legacy_paths_directories(self):
        """Test legacy path discovery with legacy directories."""
        # Create legacy directories
        (self.base_path / "saves").mkdir()
        (self.base_path / "logs").mkdir()
        (self.base_path / "runtime").mkdir()
        
        result = locate_legacy_paths(self.base_path)
        
        expected_names = {"saves", "logs", "runtime"}
        result_names = {path.name for path in result}
        
        self.assertEqual(result_names, expected_names)
    
    def test_locate_legacy_paths_files(self):
        """Test legacy path discovery with legacy files."""
        # Create legacy files
        self.create_legacy_json(
            self.base_path / "local_highscore.json",
            {"scores": []}
        )
        self.create_legacy_json(
            self.base_path / "onboarding_progress.json",
            {"tutorial_enabled": True}
        )
        
        result = locate_legacy_paths(self.base_path)
        
        expected_names = {"local_highscore.json", "onboarding_progress.json"}
        result_names = {path.name for path in result}
        
        self.assertEqual(result_names, expected_names)
    
    def test_needs_migration_no_legacy(self):
        """Test needs_migration when no legacy files exist."""
        self.assertFalse(self.adapter.needs_migration())
    
    def test_needs_migration_with_legacy(self):
        """Test needs_migration when legacy files exist."""
        # Create a legacy file
        self.create_legacy_file(self.base_path / "local_highscore.json")
        
        self.assertTrue(self.adapter.needs_migration())
    
    def test_needs_migration_already_migrated(self):
        """Test needs_migration when migration already completed."""
        # Create legacy file
        self.create_legacy_file(self.base_path / "local_highscore.json")
        
        # Create migration marker
        marker_path = self.data_dir / MigrationAdapter.MARKER_FILE
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text("# Migration completed")
        
        self.assertFalse(self.adapter.needs_migration())
    
    def test_is_migrated_false(self):
        """Test is_migrated when no marker exists."""
        self.assertFalse(self.adapter.is_migrated())
    
    def test_is_migrated_true(self):
        """Test is_migrated when marker exists."""
        # Create migration marker
        marker_path = self.data_dir / MigrationAdapter.MARKER_FILE
        marker_path.parent.mkdir(parents=True, exist_ok=True)
        marker_path.write_text("# Migration completed")
        
        self.assertTrue(self.adapter.is_migrated())
    
    def test_migrate_single_file(self):
        """Test migration of a single legacy file."""
        # Create legacy file
        legacy_file = self.base_path / "local_highscore.json"
        test_data = {"scores": [{"name": "Test", "score": 100}]}
        self.create_legacy_json(legacy_file, test_data)
        
        result = self.adapter.migrate()
        
        # Check result
        self.assertEqual(result.files_copied, 1)
        self.assertEqual(len(result.legacy_paths_found), 1)
        self.assertTrue(result.marker_created)
        
        # Check file was copied
        target_file = self.data_dir / "local_highscore.json"
        self.assertTrue(target_file.exists())
        
        # Check content is correct
        copied_data = json.loads(target_file.read_text())
        self.assertEqual(copied_data, test_data)
        
        # Check original file still exists (copy, not move)
        self.assertTrue(legacy_file.exists())
    
    def test_migrate_directory_logs(self):
        """Test migration of legacy logs directory."""
        # Create legacy logs directory with files
        legacy_logs = self.base_path / "logs"
        legacy_logs.mkdir()
        
        log1 = legacy_logs / "game_20240101.txt"
        log2 = legacy_logs / "game_20240102.txt"
        
        self.create_legacy_file(log1, "Game log 1")
        self.create_legacy_file(log2, "Game log 2")
        
        result = self.adapter.migrate()
        
        # Check result
        self.assertEqual(result.files_copied, 2)
        self.assertTrue(result.marker_created)
        
        # Check files were copied to log directory
        target_log_dir = self.data_dir / "logs"
        self.assertTrue(target_log_dir.exists())
        
        target_log1 = target_log_dir / "game_20240101.txt"
        target_log2 = target_log_dir / "game_20240102.txt"
        
        self.assertTrue(target_log1.exists())
        self.assertTrue(target_log2.exists())
        self.assertEqual(target_log1.read_text(), "Game log 1")
        self.assertEqual(target_log2.read_text(), "Game log 2")
    
    def test_migrate_directory_saves(self):
        """Test migration of legacy saves directory."""
        # Create legacy saves directory with files
        legacy_saves = self.base_path / "saves"
        legacy_saves.mkdir()
        
        save1 = legacy_saves / "game1.json"
        save2 = legacy_saves / "game2.json"
        
        self.create_legacy_json(save1, {"turn": 1, "money": 100})
        self.create_legacy_json(save2, {"turn": 5, "money": 500})
        
        result = self.adapter.migrate()
        
        # Check result
        self.assertEqual(result.files_copied, 2)
        
        # Check files were copied to save directory
        target_save_dir = self.data_dir / "saves"
        self.assertTrue(target_save_dir.exists())
        
        target_save1 = target_save_dir / "game1.json"
        target_save2 = target_save_dir / "game2.json"
        
        self.assertTrue(target_save1.exists())
        self.assertTrue(target_save2.exists())
    
    def test_migrate_no_overwrite(self):
        """Test that migration doesn't overwrite existing files."""
        # Create legacy file
        legacy_file = self.base_path / "local_highscore.json"
        self.create_legacy_json(legacy_file, {"old": "data"})
        
        # Create existing file in target location
        target_file = self.data_dir / "local_highscore.json"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        self.create_legacy_json(target_file, {"new": "data"})
        
        result = self.adapter.migrate()
        
        # Should not have copied the file
        self.assertEqual(result.files_copied, 0)
        
        # Target file should be unchanged
        data = json.loads(target_file.read_text())
        self.assertEqual(data, {"new": "data"})
    
    def test_migrate_creates_marker(self):
        """Test that migration creates proper marker file."""
        # Create legacy file
        self.create_legacy_file(self.base_path / "local_highscore.json")
        
        result = self.adapter.migrate()
        
        # Check marker was created
        marker_path = self.data_dir / MigrationAdapter.MARKER_FILE
        self.assertTrue(marker_path.exists())
        
        # Check marker content
        marker_content = marker_path.read_text()
        self.assertIn("PDoom1 Migration Completed", marker_content)
        self.assertIn("Files copied: 1", marker_content)
        self.assertIn("local_highscore.json", marker_content)
    
    def test_migrate_idempotent(self):
        """Test that migration is idempotent."""
        # Create legacy file
        self.create_legacy_file(self.base_path / "local_highscore.json")
        
        # First migration
        result1 = self.adapter.migrate()
        self.assertEqual(result1.files_copied, 1)
        
        # Second migration should do nothing
        result2 = self.adapter.migrate()
        self.assertEqual(result2.files_copied, 0)
        self.assertFalse(result2.marker_created)  # Marker already exists
    
    def test_migration_logging(self):
        """Test that migration produces appropriate log messages."""
        # Create legacy file
        self.create_legacy_file(self.base_path / "local_highscore.json")
        
        self.adapter.migrate()
        
        # Check log messages
        log_messages = " ".join(self.log_capture)
        self.assertIn("MIGRATION:", log_messages)
        self.assertIn("legacy file(s)", log_messages)


if __name__ == '__main__':
    unittest.main()
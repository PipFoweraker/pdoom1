"""Tests for the data directory and persistence adapter systems."""

import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest

from src.services.data_directory import DataDirectoryManager, get_data_manager
from src.services.persistence_adapter import (
    get_file_path, load_json_file, save_json_file,
    get_onboarding_progress, save_onboarding_progress
)


class TestDataDirectoryManager:
    """Test the data directory management system."""
    
    def test_data_directory_creation(self):
        """Test that data directory is created properly."""
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['PDOOM1_DATA_DIR'] = temp_dir
            
            # Create a new manager instance
            manager = DataDirectoryManager()
            
            # Check that the directory was created
            assert manager.data_directory.exists()
            assert manager.data_directory.is_dir()
            
            # Check subdirectories were created
            expected_subdirs = ['configs', 'logs', 'leaderboards', 'sessions', 'saves']
            for subdir in expected_subdirs:
                assert (manager.data_directory / subdir).exists()
            
            # Clean up
            del os.environ['PDOOM1_DATA_DIR']
    
    def test_file_migration(self):
        """Test that legacy files are migrated properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['PDOOM1_DATA_DIR'] = str(Path(temp_dir) / "data")
            
            # Create a legacy file
            legacy_dir = Path(temp_dir) / "legacy"
            legacy_dir.mkdir()
            legacy_file = legacy_dir / "test_file.json"
            legacy_data = {"test": "data", "migrated": False}
            
            with open(legacy_file, 'w') as f:
                json.dump(legacy_data, f)
            
            # Change to legacy directory to simulate old working directory
            old_cwd = os.getcwd()
            os.chdir(legacy_dir)
            
            try:
                manager = DataDirectoryManager()
                
                # Test migration
                migrated_path = manager.migrate_file_if_needed("test_file.json", show_migration_notice=False)
                
                # Check that file was migrated
                assert migrated_path.exists()
                assert migrated_path == manager.get_data_path("test_file.json")
                
                with open(migrated_path, 'r') as f:
                    migrated_data = json.load(f)
                
                assert migrated_data == legacy_data
                
            finally:
                os.chdir(old_cwd)
                del os.environ['PDOOM1_DATA_DIR']
    
    def test_no_migration_if_new_file_exists(self):
        """Test that migration doesn't overwrite existing new files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['PDOOM1_DATA_DIR'] = str(Path(temp_dir) / "data")
            
            manager = DataDirectoryManager()
            
            # Create both legacy and new files
            legacy_dir = Path(temp_dir) / "legacy"
            legacy_dir.mkdir()
            
            legacy_file = legacy_dir / "test_file.json"
            new_file = manager.get_data_path("test_file.json")
            
            legacy_data = {"source": "legacy"}
            new_data = {"source": "new"}
            
            with open(legacy_file, 'w') as f:
                json.dump(legacy_data, f)
            
            new_file.parent.mkdir(parents=True, exist_ok=True)
            with open(new_file, 'w') as f:
                json.dump(new_data, f)
            
            # Change to legacy directory
            old_cwd = os.getcwd()
            os.chdir(legacy_dir)
            
            try:
                # Migration should prefer existing new file
                result_path = manager.migrate_file_if_needed("test_file.json", show_migration_notice=False)
                
                with open(result_path, 'r') as f:
                    result_data = json.load(f)
                
                # Should have the new file data, not legacy
                assert result_data == new_data
                
            finally:
                os.chdir(old_cwd)
                del os.environ['PDOOM1_DATA_DIR']


class TestPersistenceAdapter:
    """Test the persistence adapter functions."""
    
    def test_get_file_path(self):
        """Test that get_file_path returns appropriate paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['PDOOM1_DATA_DIR'] = temp_dir
            
            # Test legacy file mapping
            path = get_file_path('onboarding_progress.json')
            assert path.parent.name == temp_dir.split(os.sep)[-1]  # Should be in data dir
            
            # Test new file (should go to data dir)
            path = get_file_path('new_file.json')
            assert path.parent.name == temp_dir.split(os.sep)[-1]
            
            del os.environ['PDOOM1_DATA_DIR']
    
    def test_load_save_json_file(self):
        """Test JSON file loading and saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['PDOOM1_DATA_DIR'] = temp_dir
            
            test_data = {"test": "data", "number": 42}
            filename = "test_data.json"
            
            # Test saving
            success = save_json_file(filename, test_data)
            assert success
            
            # Test loading
            loaded_data = load_json_file(filename)
            assert loaded_data == test_data
            
            # Test loading non-existent file with default
            default_data = {"default": True}
            loaded_default = load_json_file("nonexistent.json", default_data)
            assert loaded_default == default_data
            
            del os.environ['PDOOM1_DATA_DIR']
    
    def test_onboarding_progress_functions(self):
        """Test onboarding progress convenience functions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ['PDOOM1_DATA_DIR'] = temp_dir
            
            # Test loading (may get migrated existing file or defaults)
            progress = get_onboarding_progress()
            assert 'tutorial_enabled' in progress
            assert 'is_first_time' in progress  # Don't assume value since it might migrate
            
            # Test saving and loading custom data
            custom_progress = {
                'tutorial_enabled': False,
                'is_first_time': False,
                'completed_steps': ['welcome', 'resources'],
                'seen_mechanics': ['hire_staff'],
                'tutorial_dismissed': True
            }
            
            success = save_onboarding_progress(custom_progress)
            assert success
            
            loaded_progress = get_onboarding_progress()
            assert loaded_progress == custom_progress
            
            del os.environ['PDOOM1_DATA_DIR']


if __name__ == "__main__":
    # Run a simple smoke test
    print("Testing data directory system...")
    
    test_data_dir = TestDataDirectoryManager()
    test_data_dir.test_data_directory_creation()
    print("✓ Data directory creation test passed")
    
    test_adapter = TestPersistenceAdapter()
    test_adapter.test_load_save_json_file()
    print("✓ JSON file operations test passed")
    
    test_adapter.test_onboarding_progress_functions()
    print("✓ Onboarding progress functions test passed")
    
    print("All tests passed! Data directory system is working correctly.")

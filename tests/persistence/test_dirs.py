"""Tests for data directory resolution and PDOOM1_DATA_DIR override."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pdoom1.services.data_paths import get_data_dir, get_save_dir, get_log_dir, ensure_dir


class TestDataDirectoryResolution(unittest.TestCase):
    """Test cross-platform data directory resolution."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear environment variables
        self.original_env = {}
        for key in ["PDOOM1_DATA_DIR", "PDOOM1_TEST_DATA_DIR", "APPDATA", "XDG_DATA_HOME"]:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
    
    def tearDown(self):
        """Clean up test environment."""
        # Restore environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_pdoom1_data_dir_override(self):
        """Test PDOOM1_DATA_DIR environment override."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "custom_data"
            os.environ["PDOOM1_DATA_DIR"] = str(test_path)
            
            result = get_data_dir()
            
            self.assertEqual(result, test_path)
            self.assertTrue(result.exists())
    
    def test_pdoom1_test_data_dir_override(self):
        """Test PDOOM1_TEST_DATA_DIR environment override."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test_data"
            os.environ["PDOOM1_TEST_DATA_DIR"] = str(test_path)
            
            result = get_data_dir()
            
            self.assertEqual(result, test_path)
            self.assertTrue(result.exists())
    
    def test_data_dir_precedence(self):
        """Test that PDOOM1_DATA_DIR has precedence over PDOOM1_TEST_DATA_DIR."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "data"
            test_path = Path(temp_dir) / "test"
            
            os.environ["PDOOM1_DATA_DIR"] = str(data_path)
            os.environ["PDOOM1_TEST_DATA_DIR"] = str(test_path)
            
            result = get_data_dir()
            
            self.assertEqual(result, data_path)
            self.assertTrue(data_path.exists())
            self.assertFalse(test_path.exists())
    
    @patch('sys.platform', 'win32')
    def test_windows_default_path(self):
        """Test Windows default data directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            appdata_path = Path(temp_dir) / "AppData" / "Roaming"
            appdata_path.mkdir(parents=True)
            os.environ["APPDATA"] = str(appdata_path)
            
            result = get_data_dir()
            expected = appdata_path / "pdoom1"
            
            self.assertEqual(result, expected)
    
    @patch('sys.platform', 'win32')
    def test_windows_fallback_path(self):
        """Test Windows fallback when APPDATA is not set."""
        # Don't set APPDATA
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/home/user")
            
            # Patch ensure_dir to avoid creating directories
            with patch('pdoom1.services.data_paths.ensure_dir'):
                result = get_data_dir()
                expected = Path("/home/user/AppData/Roaming/pdoom1")
                
                self.assertEqual(result, expected)
    
    @patch('sys.platform', 'darwin')
    def test_macos_default_path(self):
        """Test macOS default data directory path."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/Users/testuser")
            
            # Patch ensure_dir to avoid creating directories
            with patch('pdoom1.services.data_paths.ensure_dir'):
                result = get_data_dir()
                expected = Path("/Users/testuser/Library/Application Support/pdoom1")
                
                self.assertEqual(result, expected)
    
    @patch('sys.platform', 'linux')
    def test_linux_xdg_data_home(self):
        """Test Linux with XDG_DATA_HOME set."""
        with tempfile.TemporaryDirectory() as temp_dir:
            xdg_path = Path(temp_dir) / "data"
            os.environ["XDG_DATA_HOME"] = str(xdg_path)
            
            result = get_data_dir()
            expected = xdg_path / "pdoom1"
            
            self.assertEqual(result, expected)
    
    @patch('sys.platform', 'linux')
    def test_linux_default_path(self):
        """Test Linux default when XDG_DATA_HOME is not set."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/home/testuser")
            
            # Patch ensure_dir to avoid creating directories
            with patch('pdoom1.services.data_paths.ensure_dir'):
                result = get_data_dir()
                expected = Path("/home/testuser/.local/share/pdoom1")
                
                self.assertEqual(result, expected)
    
    def test_get_save_dir(self):
        """Test save directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["PDOOM1_DATA_DIR"] = temp_dir
            
            result = get_save_dir()
            expected = Path(temp_dir) / "saves"
            
            self.assertEqual(result, expected)
            self.assertTrue(result.exists())
            self.assertTrue(result.is_dir())
    
    def test_get_log_dir(self):
        """Test log directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            os.environ["PDOOM1_DATA_DIR"] = temp_dir
            
            result = get_log_dir()
            expected = Path(temp_dir) / "logs"
            
            self.assertEqual(result, expected)
            self.assertTrue(result.exists())
            self.assertTrue(result.is_dir())
    
    def test_ensure_dir(self):
        """Test ensure_dir function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "nested" / "directory"
            
            # Directory shouldn't exist initially
            self.assertFalse(test_path.exists())
            
            # ensure_dir should create it
            ensure_dir(test_path)
            self.assertTrue(test_path.exists())
            self.assertTrue(test_path.is_dir())
            
            # Calling again should not raise an error
            ensure_dir(test_path)
            self.assertTrue(test_path.exists())


if __name__ == '__main__':
    unittest.main()
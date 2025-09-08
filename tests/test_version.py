"""
Tests for version management system.

These tests ensure version consistency across the codebase and proper
functionality of the centralized version system.
"""

import unittest
from src.services.version import (
    __version__, 
    get_version, 
    get_display_version, 
    get_version_info,
    VERSION_MAJOR,
    VERSION_MINOR, 
    VERSION_PATCH
)
from src.services.game_logger import GameLogger
from src.core.game_state import GameState


class TestVersionSystem(unittest.TestCase):
    """Test the centralized version management system."""
    
    def test_version_constants(self):
        """Test that version constants are properly defined."""
        self.assertIsInstance(__version__, str)
        self.assertIsInstance(VERSION_MAJOR, int)
        self.assertIsInstance(VERSION_MINOR, int)
        self.assertIsInstance(VERSION_PATCH, int)
        
        # Version should be in semantic version format
        parts = __version__.split('.')
        self.assertEqual(len(parts), 3)
        self.assertTrue(all(part.isdigit() for part in parts))
    
    def test_get_version(self):
        """Test get_version() function."""
        version = get_version()
        self.assertIsInstance(version, str)
        self.assertTrue(len(version) > 0)
        # Basic version should at least contain the base version
        self.assertIn(__version__, version)
    
    def test_get_display_version(self):
        """Test get_display_version() function."""
        display = get_display_version()
        self.assertIsInstance(display, str)
        self.assertTrue(display.startswith('v'))
        self.assertIn(__version__, display)
    
    def test_get_version_info(self):
        """Test get_version_info() function returns complete info."""
        info = get_version_info()
        self.assertIsInstance(info, dict)
        
        required_keys = [
            'version', 'full_version', 'display_version', 
            'major', 'minor', 'patch', 'prerelease', 'build'
        ]
        for key in required_keys:
            self.assertIn(key, info)
        
        # Check version consistency
        self.assertEqual(info['version'], __version__)
        self.assertEqual(info['major'], VERSION_MAJOR)
        self.assertEqual(info['minor'], VERSION_MINOR)
        self.assertEqual(info['patch'], VERSION_PATCH)


class TestVersionIntegration(unittest.TestCase):
    """Test that version system integrates properly with game components."""
    
    def test_game_logger_uses_current_version(self):
        """Test that GameLogger defaults to current version."""
        logger = GameLogger("test_seed")
        expected_version = get_display_version()
        self.assertEqual(logger.game_version, expected_version)
    
    def test_game_logger_custom_version(self):
        """Test that GameLogger accepts custom version."""
        custom_version = "v9.9.9-test"
        logger = GameLogger("test_seed", custom_version)
        self.assertEqual(logger.game_version, custom_version)
    
    def test_game_state_logger_integration(self):
        """Test that GameState's logger uses correct version."""
        gs = GameState("test_seed")
        expected_version = get_display_version()
        self.assertEqual(gs.logger.game_version, expected_version)


class TestVersionConsistency(unittest.TestCase):
    """Test that version is consistent across all files and components."""
    
    def test_version_in_main_window_title(self):
        """Test that main.py uses the correct version in window title."""
        # Read main.py and check it uses get_display_version()
        with open('main.py', 'r') as f:
            main_content = f.read()
        
        # Should import and use get_display_version
        self.assertIn('from src.services.version import get_display_version', main_content)
        self.assertIn('get_display_version()', main_content)
    
    def test_changelog_mentions_correct_version(self):
        """Test that CHANGELOG.md mentions the current version."""
        current_version = __version__
        
        with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
            changelog_content = f.read()
        
        # Should mention current version in changelog
        self.assertIn(f'[{current_version}]', changelog_content)
    
    def test_release_workflow_version_validation(self):
        """Test that release workflow has version validation."""
        with open('.github/workflows/release.yml', 'r') as f:
            workflow_content = f.read()
        
        # Should have version validation steps
        self.assertIn('validate-version', workflow_content)
        self.assertIn('version consistency', workflow_content.lower())
        self.assertIn('get_display_version', workflow_content)


class TestVersionSemantics(unittest.TestCase):
    """Test that version follows semantic versioning rules."""
    
    def test_version_is_semantic(self):
        """Test that version follows SemVer format."""
        # Should be MAJOR.MINOR.PATCH
        parts = __version__.split('.')
        self.assertEqual(len(parts), 3)
        
        major, minor, patch = parts
        self.assertTrue(major.isdigit())
        self.assertTrue(minor.isdigit())  
        self.assertTrue(patch.isdigit())
    
    def test_version_components_match(self):
        """Test that version string matches component constants."""
        expected = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
        self.assertEqual(__version__, expected)


if __name__ == '__main__':
    unittest.main()
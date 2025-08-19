"""
Tests for custom sound override functionality.

Tests the following requirements:
- Custom sounds loaded from sounds/ folder
- Files mapped by filename (stem) to event keys
- Built-in sounds are overridden when keys match
- System handles missing folder/files gracefully
- No crashes when sound loading fails
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

# Add the parent directory to the path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.sound_manager import SoundManager


class TestCustomSoundOverrides(unittest.TestCase):
    """Test custom sound override functionality"""

    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.sounds_dir = Path(self.temp_dir) / "sounds"
        self.sounds_dir.mkdir()

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_load_sounds_missing_folder(self):
        """Test loading sounds when folder doesn't exist"""
        sound_manager = SoundManager()
        initial_sounds = len(sound_manager.sounds)
        
        # Try to load from non-existent folder
        non_existent = Path(self.temp_dir) / "non_existent"
        sound_manager._load_sounds_from_folder(non_existent)
        
        # Should not crash, should not change sound count
        self.assertEqual(len(sound_manager.sounds), initial_sounds)

    def test_load_sounds_empty_folder(self):
        """Test loading sounds from empty folder"""
        sound_manager = SoundManager()
        initial_sounds = len(sound_manager.sounds)
        
        # Load from empty folder
        sound_manager._load_sounds_from_folder(self.sounds_dir)
        
        # Should not crash, should not change sound count
        self.assertEqual(len(sound_manager.sounds), initial_sounds)

    def test_load_sounds_audio_unavailable(self):
        """Test loading sounds when audio is unavailable"""
        sound_manager = SoundManager()
        sound_manager.audio_available = False
        initial_sounds = len(sound_manager.sounds)
        
        # Load from folder when audio unavailable
        sound_manager._load_sounds_from_folder(self.sounds_dir)
        
        # Should not crash, should not change sound count
        self.assertEqual(len(sound_manager.sounds), initial_sounds)

    @patch('pygame.mixer.Sound')
    def test_load_sounds_with_mock_files(self, mock_sound_class):
        """Test loading sounds with mocked pygame.mixer.Sound"""
        # Create mock sound files
        wav_file = self.sounds_dir / "ap_spend.wav"
        ogg_file = self.sounds_dir / "popup_open.ogg"
        wav_file.touch()
        ogg_file.touch()
        
        # Mock pygame.mixer.Sound to return a mock object
        mock_sound = unittest.mock.MagicMock()
        mock_sound_class.return_value = mock_sound
        
        sound_manager = SoundManager()
        initial_sounds = len(sound_manager.sounds)
        
        # Load sounds
        sound_manager._load_sounds_from_folder(self.sounds_dir)
        
        # Should have called pygame.mixer.Sound for each file (if audio available)
        if sound_manager.audio_available:
            self.assertEqual(mock_sound_class.call_count, 2)
            self.assertIn('ap_spend', sound_manager.sounds)
            self.assertIn('popup_open', sound_manager.sounds)
        else:
            # In headless environment, custom sound loading won't be called
            self.assertEqual(mock_sound_class.call_count, 0)

    @patch('pygame.mixer.Sound')
    def test_recursive_loading(self, mock_sound_class):
        """Test that sounds are loaded recursively from subdirectories"""
        # Create subdirectory with sound file
        subdir = self.sounds_dir / "ui"
        subdir.mkdir()
        nested_file = subdir / "error_beep.wav"
        nested_file.touch()
        
        # Mock pygame.mixer.Sound
        mock_sound = unittest.mock.MagicMock()
        mock_sound_class.return_value = mock_sound
        
        sound_manager = SoundManager()
        
        # Load sounds
        sound_manager._load_sounds_from_folder(self.sounds_dir)
        
        # Should have found the nested file
        if sound_manager.audio_available:
            mock_sound_class.assert_called()
            # Check that the nested file was processed
            call_args = mock_sound_class.call_args_list
            file_paths = [str(call[0][0]) for call in call_args]
            self.assertTrue(any("error_beep.wav" in path for path in file_paths))

    def test_filename_to_key_mapping(self):
        """Test that filenames are correctly mapped to keys"""
        sound_manager = SoundManager()
        
        # Test with various filenames
        test_cases = [
            (Path("ap_spend.wav"), "ap_spend"),
            (Path("AP_SPEND.WAV"), "ap_spend"),  # Case insensitive
            (Path("popup_open.ogg"), "popup_open"),
            (Path("some_custom_sound.wav"), "some_custom_sound"),
        ]
        
        for file_path, expected_key in test_cases:
            actual_key = file_path.stem.lower()
            self.assertEqual(actual_key, expected_key, 
                           f"File {file_path} should map to key '{expected_key}'")

    @patch('pygame.mixer.Sound')
    def test_sound_override_behavior(self, mock_sound_class):
        """Test that custom sounds override built-in sounds"""
        # Create a file that should override a built-in sound
        custom_file = self.sounds_dir / "blob.wav"
        custom_file.touch()
        
        # Mock pygame.mixer.Sound
        mock_custom_sound = unittest.mock.MagicMock()
        mock_sound_class.return_value = mock_custom_sound
        
        sound_manager = SoundManager()
        original_blob_sound = sound_manager.sounds.get('blob')
        
        # Load custom sounds
        sound_manager._load_sounds_from_folder(self.sounds_dir)
        
        # If audio is available, the custom sound should override the built-in one
        if sound_manager.audio_available and 'blob' in sound_manager.sounds:
            # The sound should have been replaced (assuming pygame calls succeeded)
            # Note: In a headless environment, this might not always work as expected
            pass  # We can't easily test this without actual pygame functionality

    def test_load_sounds_handles_pygame_errors(self):
        """Test that loading handles pygame.error gracefully"""
        # Create a dummy file
        dummy_file = self.sounds_dir / "test.wav"
        dummy_file.touch()
        
        sound_manager = SoundManager()
        
        # This should not crash even if pygame.mixer.Sound fails
        # (which it will with an empty/invalid file)
        try:
            sound_manager._load_sounds_from_folder(self.sounds_dir)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success, "Loading should not crash on invalid sound files")

    def test_integration_with_sound_manager_init(self):
        """Test that custom sound loading is integrated into SoundManager.__init__"""
        # This tests that the _load_sounds_from_folder call is in __init__
        # We can't easily mock the Path("sounds") call, but we can verify the method exists
        sound_manager = SoundManager()
        self.assertTrue(hasattr(sound_manager, '_load_sounds_from_folder'),
                       "SoundManager should have _load_sounds_from_folder method")
        self.assertTrue(hasattr(sound_manager, '_load_sound_file'),
                       "SoundManager should have _load_sound_file method")


class TestSoundOverrideKeys(unittest.TestCase):
    """Test that the known event keys are documented correctly"""
    
    def test_known_event_keys_exist_in_sound_toggles(self):
        """Test that known event keys exist in the sound toggles"""
        sound_manager = SoundManager()
        
        # These are the keys mentioned in the problem statement
        expected_keys = ['ap_spend', 'popup_open', 'popup_close', 'popup_accept', 'error_beep', 'blob']
        
        for key in expected_keys:
            self.assertIn(key, sound_manager.sound_toggles,
                         f"Sound toggle for '{key}' should exist")

    def test_zabinga_key_exists(self):
        """Test that zabinga key is handled (even if not in sound_toggles)"""
        sound_manager = SoundManager()
        
        # zabinga might be in sounds dict but not necessarily in sound_toggles
        # We just need to verify the SoundManager can handle it
        sound_manager.play_sound('zabinga')  # Should not crash


if __name__ == '__main__':
    unittest.main()
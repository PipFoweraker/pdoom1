'''
Tests for Settings functionality.
'''

import tempfile
import json
import os
from pathlib import Path

from src.services.settings import Settings


class TestSettings:
    '''Test cases for Settings service.'''
    
    def test_default_initialization(self):
        '''Test Settings initializes with correct defaults.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Check default values
            assert settings.get('version') == '1.0.0'
            assert isinstance(settings.get('device_uuid'), str)
            assert len(settings.get('device_uuid')) == 36  # UUID length
            
            # Audio defaults
            assert settings.get('audio.master_volume') == 0.7
            assert settings.get('audio.sfx_volume') == 0.8
            assert settings.get('audio.music_volume') == 0.6
            assert settings.get('audio.muted') is False
            
            # Telemetry defaults
            assert settings.get('telemetry.enabled') is True
            
            # Gameplay defaults
            assert settings.get('gameplay.difficulty') == 'normal'
            assert settings.get('gameplay.auto_save') is True
    
    def test_persistence(self):
        '''Test settings persistence across instances.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            
            # Create first instance and modify settings
            settings1 = Settings(settings_file)
            original_uuid = settings1.get('device_uuid')
            settings1.set('audio.master_volume', 0.5)
            settings1.set('telemetry.enabled', False)
            
            # Create second instance - should load saved settings
            settings2 = Settings(settings_file)
            assert settings2.get('device_uuid') == original_uuid  # Should be same UUID
            assert settings2.get('audio.master_volume') == 0.5
            assert settings2.get('telemetry.enabled') is False
    
    def test_dot_notation_access(self):
        '''Test getting and setting values with dot notation.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Test getting nested values
            assert settings.get('audio.master_volume') == 0.7
            assert settings.get('telemetry.enabled') is True
            
            # Test setting nested values
            settings.set('audio.master_volume', 0.9)
            assert settings.get('audio.master_volume') == 0.9
            
            # Test creating new nested paths
            settings.set('new.nested.value', 'test')
            assert settings.get('new.nested.value') == 'test'
            
            # Test non-existent paths return default
            assert settings.get('non.existent.path') is None
            assert settings.get('non.existent.path', 'default') == 'default'
    
    def test_volume_methods(self):
        '''Test volume-specific convenience methods.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Test getting volumes
            assert settings.get_volume('master') == 0.7
            assert settings.get_volume('sfx') == 0.8
            assert settings.get_volume('music') == 0.6
            
            # Test setting volumes
            settings.set_volume('master', 0.5)
            assert settings.get_volume('master') == 0.5
            
            # Test volume clamping
            settings.set_volume('sfx', 1.5)  # Should clamp to 1.0
            assert settings.get_volume('sfx') == 1.0
            
            settings.set_volume('music', -0.1)  # Should clamp to 0.0
            assert settings.get_volume('music') == 0.0
    
    def test_mute_methods(self):
        '''Test mute-specific convenience methods.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Initial state should be unmuted
            assert settings.is_muted() is False
            
            # Test muting
            settings.set_muted(True)
            assert settings.is_muted() is True
            assert settings.get('audio.muted') is True
            
            # Test unmuting
            settings.set_muted(False)
            assert settings.is_muted() is False
            assert settings.get('audio.muted') is False
    
    def test_telemetry_methods(self):
        '''Test telemetry-specific convenience methods.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Initial state should have telemetry enabled
            assert settings.is_telemetry_enabled() is True
            
            # Test disabling telemetry
            settings.set_telemetry_enabled(False)
            assert settings.is_telemetry_enabled() is False
            assert settings.get('telemetry.enabled') is False
            
            # Test enabling telemetry
            settings.set_telemetry_enabled(True)
            assert settings.is_telemetry_enabled() is True
            assert settings.get('telemetry.enabled') is True
    
    def test_device_uuid_persistence(self):
        '''Test device UUID is generated once and persisted.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            
            # Create first instance
            settings1 = Settings(settings_file)
            uuid1 = settings1.get_device_uuid()
            assert isinstance(uuid1, str)
            assert len(uuid1) == 36
            
            # Create second instance - should have same UUID
            settings2 = Settings(settings_file)
            uuid2 = settings2.get_device_uuid()
            assert uuid1 == uuid2
    
    def test_atomic_writes(self):
        '''Test that settings writes are atomic.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Modify a setting
            settings.set('test.value', 'test_data')
            
            # File should exist and be valid JSON
            assert settings_file.exists()
            with open(settings_file, 'r') as f:
                data = json.load(f)
                assert data['test']['value'] == 'test_data'
            
            # Temporary file should not exist
            temp_file = settings_file.with_suffix('.tmp')
            assert not temp_file.exists()
    
    def test_corrupted_settings_recovery(self):
        '''Test recovery from corrupted settings file.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            
            # Create corrupted settings file
            with open(settings_file, 'w') as f:
                f.write('invalid json content')
            
            # Settings should recover gracefully and create new defaults
            settings = Settings(settings_file)
            assert settings.get('version') == '1.0.0'
            assert isinstance(settings.get('device_uuid'), str)
            assert settings.get('audio.master_volume') == 0.7
    
    def test_partial_settings_merge(self):
        '''Test merging with partial/incomplete settings.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            
            # Create partial settings file (missing some default keys)
            partial_settings = {
                'version': '1.0.0',
                'device_uuid': 'test-uuid-1234',
                'audio': {
                    'master_volume': 0.5
                    # Missing sfx_volume, music_volume, muted
                }
                # Missing telemetry, gameplay sections
            }
            
            with open(settings_file, 'w') as f:
                json.dump(partial_settings, f)
            
            # Settings should merge with defaults
            settings = Settings(settings_file)
            assert settings.get('device_uuid') == 'test-uuid-1234'  # Preserved
            assert settings.get('audio.master_volume') == 0.5  # Preserved
            assert settings.get('audio.sfx_volume') == 0.8  # Default added
            assert settings.get('telemetry.enabled') is True  # Default added
    
    def test_version_migration(self):
        '''Test settings version migration.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            
            # Create old version settings
            old_settings = {
                'version': '0.9.0',
                'device_uuid': 'test-uuid-1234',
                'audio': {
                    'master_volume': 0.5
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(old_settings, f)
            
            # Settings should migrate version and merge with defaults
            settings = Settings(settings_file)
            assert settings.get('version') == '1.0.0'  # Updated
            assert settings.get('device_uuid') == 'test-uuid-1234'  # Preserved
            assert settings.get('audio.master_volume') == 0.5  # Preserved
            assert settings.get('audio.sfx_volume') == 0.8  # Added from defaults
    
    def test_file_permissions(self):
        '''Test settings file is created with appropriate permissions.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            Settings(settings_file)
            
            # File should exist
            assert settings_file.exists()
            
            # Should be readable and writable
            assert os.access(settings_file, os.R_OK)
            assert os.access(settings_file, os.W_OK)
    
    def test_concurrent_access_safety(self):
        '''Test settings handles concurrent access safely.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            
            # Create two settings instances for same file
            settings1 = Settings(settings_file)
            settings2 = Settings(settings_file)
            
            # Modify settings from both instances
            settings1.set('audio.master_volume', 0.3)
            settings2.set('audio.sfx_volume', 0.9)
            
            # Both should be able to read their changes
            assert settings1.get('audio.master_volume') == 0.3
            assert settings2.get('audio.sfx_volume') == 0.9
            
            # Create new instance to verify persistence
            settings3 = Settings(settings_file)
            # Should have the latest saved state
            assert settings3.get('audio.sfx_volume') == 0.9
    
    def test_edge_case_values(self):
        '''Test handling of edge case values.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Test various data types
            settings.set('test.string', 'test_value')
            settings.set('test.integer', 42)
            settings.set('test.float', 3.14159)
            settings.set('test.boolean', True)
            settings.set('test.null', None)
            settings.set('test.list', [1, 2, 3])
            settings.set('test.dict', {'nested': 'value'})
            
            # Verify all types are preserved
            assert settings.get('test.string') == 'test_value'
            assert settings.get('test.integer') == 42
            assert settings.get('test.float') == 3.14159
            assert settings.get('test.boolean') is True
            assert settings.get('test.null') is None
            assert settings.get('test.list') == [1, 2, 3]
            assert settings.get('test.dict') == {'nested': 'value'}
    
    def test_deep_nesting(self):
        '''Test deeply nested setting paths.'''
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_file = Path(temp_dir) / 'test_settings.json'
            settings = Settings(settings_file)
            
            # Create deeply nested path
            deep_path = 'level1.level2.level3.level4.value'
            settings.set(deep_path, 'deep_value')
            
            # Should be able to retrieve the value
            assert settings.get(deep_path) == 'deep_value'
            
            # Should be able to retrieve intermediate levels
            assert isinstance(settings.get('level1.level2'), dict)
            assert isinstance(settings.get('level1.level2.level3'), dict)
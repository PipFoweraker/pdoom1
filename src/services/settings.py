"""
Settings management for PDoom1.

Provides versioned JSON settings with atomic writes and device UUID generation.
Handles audio preferences, telemetry toggles, and other user settings.
"""

import json
import uuid
import os
import copy
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
from .data_paths import get_settings_file


class Settings:
    """
    Manages persistent user settings with atomic writes and versioning.
    
    Features:
    - Versioned JSON schema for forward compatibility
    - Atomic writes to prevent corruption
    - Device UUID generation and persistence
    - Audio preferences (volume, mute state)
    - Telemetry opt-in/out
    """
    
    CURRENT_VERSION = "1.0.0"
    
    DEFAULT_SETTINGS = {
        "version": CURRENT_VERSION,
        "device_uuid": None,  # Generated on first run
        "audio": {
            "master_volume": 0.7,
            "sfx_volume": 0.8,
            "music_volume": 0.6,
            "muted": False
        },
        "telemetry": {
            "enabled": True,  # User can opt out
            "analytics_uuid": None  # Separate from device UUID
        },
        "gameplay": {
            "difficulty": "normal",
            "auto_save": True
        }
    }
    
    def __init__(self, settings_file: Optional[Path] = None):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Custom path to settings file (defaults to platform standard)
        """
        self.settings_file = settings_file or get_settings_file()
        self._settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults."""
        if not self.settings_file.exists():
            settings = copy.deepcopy(self.DEFAULT_SETTINGS)
            settings["device_uuid"] = str(uuid.uuid4())
            settings["telemetry"]["analytics_uuid"] = str(uuid.uuid4())
            self._save_settings(settings)
            return settings
            
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Handle version migration if needed
            if settings.get("version") != self.CURRENT_VERSION:
                settings = self._migrate_settings(settings)
                
            # Ensure all default keys exist
            settings = self._merge_defaults(settings)
            
            return settings
            
        except (json.JSONDecodeError, IOError, KeyError) as e:
            # Corrupt or invalid settings file
            print(f"Warning: Invalid settings file, creating new one. Error: {e}")
            settings = self.DEFAULT_SETTINGS.copy()
            settings["device_uuid"] = str(uuid.uuid4())
            settings["telemetry"]["analytics_uuid"] = str(uuid.uuid4())
            self._save_settings(settings)
            return settings
    
    def _merge_defaults(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user settings with defaults to ensure all keys exist."""
        def deep_merge(default: Dict, user: Dict) -> Dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(copy.deepcopy(self.DEFAULT_SETTINGS), settings)
    
    def _migrate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate settings from older versions."""
        # For now, just update version and merge with defaults
        settings["version"] = self.CURRENT_VERSION
        return self._merge_defaults(settings)
    
    def _save_settings(self, settings: Dict[str, Any]) -> None:
        """Atomically save settings to file."""
        # Use atomic write to prevent corruption
        temp_file = self.settings_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            # Atomic move (platform-specific)
            if os.name == 'nt':  # Windows
                if self.settings_file.exists():
                    os.remove(self.settings_file)
                os.rename(temp_file, self.settings_file)
            else:  # Unix-like systems
                os.rename(temp_file, self.settings_file)
                
        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                os.remove(temp_file)
            raise e
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value by dot notation path."""
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value by dot notation path."""
        keys = key.split('.')
        settings = self._settings
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in settings or not isinstance(settings[k], dict):
                settings[k] = {}
            settings = settings[k]
        
        # Set the value
        settings[keys[-1]] = value
        
        # Save immediately
        self.save()
    
    def save(self) -> None:
        """Save current settings to file."""
        self._save_settings(self._settings)
    
    def get_device_uuid(self) -> str:
        """Get the unique device identifier."""
        return self._settings["device_uuid"]
    
    def is_telemetry_enabled(self) -> bool:
        """Check if telemetry is enabled."""
        return self._settings.get("telemetry", {}).get("enabled", False)
    
    def set_telemetry_enabled(self, enabled: bool) -> None:
        """Enable or disable telemetry."""
        self.set("telemetry.enabled", enabled)
    
    def get_volume(self, channel: str = "master") -> float:
        """Get volume for a specific channel."""
        return self.get(f"audio.{channel}_volume", 0.7)
    
    def set_volume(self, channel: str, volume: float) -> None:
        """Set volume for a specific channel."""
        volume = max(0.0, min(1.0, volume))  # Clamp to [0,1]
        self.set(f"audio.{channel}_volume", volume)
    
    def is_muted(self) -> bool:
        """Check if audio is muted."""
        return self.get("audio.muted", False)
    
    def set_muted(self, muted: bool) -> None:
        """Set audio mute state."""
        self.set("audio.muted", muted)
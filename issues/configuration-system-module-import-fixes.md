# Configuration System Module Import and Default Fixes

**Created**: September 11, 2025  
**Type**: Bug Fix  
**Priority**: High  
**Status**: Open  
**Branch**: stable-alpha  

## Background

Based on analysis of `issues/configuration-system-import-failures.md` and `issues/sound-system-default-configuration.md`, there are critical issues with the configuration system that are causing multiple test failures and poor default user experience.

## Problem Analysis

### 1. Module Import Failures
**Affected Tests:**
- `test_config_manager.py::TestConfigManager::test_default_config_generation`
- `test_config_manager.py::TestConfigSystemIntegration::test_get_current_config_function`
- `test_config_manager.py::TestConfigSystemIntegration::test_initialize_config_system`

**Root Cause:** `ModuleNotFoundError: No module named 'config_manager'`

### 2. Missing Configuration Keys
**Error:** `KeyError: 'safety_level'` in default config
**Affected Tests:** Settings flow integration tests

### 3. Sound System Default Issues
**Error:** `AssertionError: False is not true : Sound should be enabled by default`
**Problem:** New installations have sound disabled, poor UX

## Coding Solutions from Issue Analysis

### 1. Fix Module Import Structure
```python
# Current issue: import config_manager fails
# Solution: Proper module structure and imports

# src/services/config_manager.py (ensure this exists)
from pathlib import Path
from typing import Dict, Any, Optional
import json

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("configs/default.json")
        self.config_data = {}
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration with all required keys"""
        default_config = {
            "sound_enabled": True,  # Fix: Sound enabled by default
            "safety_level": 1,      # Fix: Add missing safety_level key
            "volume": {
                "master": 0.7,
                "sfx": 0.8,
                "music": 0.6
            },
            "graphics": {
                "fullscreen": False,
                "resolution": [1024, 768]
            },
            "gameplay": {
                "auto_save": True,
                "difficulty": "normal"
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge loaded config with defaults to ensure all keys exist
                self.config_data = {**default_config, **loaded_config}
            except (json.JSONDecodeError, IOError):
                self.config_data = default_config
        else:
            self.config_data = default_config
            self._save_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot notation support"""
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save current configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f, indent=2)
```

### 2. Fix Import Structure
```python
# src/__init__.py (ensure proper package structure)
from .services.config_manager import ConfigManager

# tests/test_config_manager.py (fix imports)
import sys
from pathlib import Path

# Add src directory to path for tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.config_manager import ConfigManager  # Now this should work

# Alternative: Use relative imports
from src.services.config_manager import ConfigManager
```

### 3. Update Default Configuration Files
```json
// configs/default.json - Fix missing keys and defaults
{
  "sound_enabled": true,
  "safety_level": 1,
  "volume": {
    "master": 0.7,
    "sfx": 0.8,
    "music": 0.6
  },
  "graphics": {
    "fullscreen": false,
    "resolution": [1024, 768]
  },
  "gameplay": {
    "auto_save": true,
    "difficulty": "normal"
  },
  "ui": {
    "theme": "default",
    "font_size": 12
  }
}
```

### 4. Global Configuration Integration
```python
# src/core/globals.py or src/services/__init__.py
"""Global configuration instance for application-wide access"""

from .config_manager import ConfigManager

# Global instance that can be imported anywhere
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config

# src/services/sound_manager.py (fix default enabled state)
from .config_manager import config

class SoundManager:
    def __init__(self):
        # Fix: Use config system for default enabled state
        self.enabled = config.get('sound_enabled', True)  # Default True
        # ... rest of initialization
```

## Implementation Plan

### Phase 1: Module Structure Fix (1 day)
- [ ] Ensure `src/services/config_manager.py` exists with complete implementation
- [ ] Fix Python path issues in test files
- [ ] Add proper `__init__.py` files for package structure
- [ ] Test basic import functionality

### Phase 2: Configuration Schema Fix (1 day)
- [ ] Add all missing configuration keys (`safety_level`, etc.)
- [ ] Update `configs/default.json` with proper defaults
- [ ] Implement configuration merging (loaded + defaults)
- [ ] Add configuration validation

### Phase 3: Sound System Integration (1 day)
- [ ] Fix sound enabled default to `True`
- [ ] Update sound manager to use config system
- [ ] Test sound initialization with new defaults
- [ ] Verify test passes for default sound configuration

### Phase 4: Test Fixes and Validation (1 day)
- [ ] Fix all failing configuration tests
- [ ] Add comprehensive config manager tests
- [ ] Test settings flow integration
- [ ] Validate all configuration keys are accessible

## Testing Strategy

### Unit Tests Fix
```python
# tests/test_config_manager.py
def test_config_manager_import():
    """Test that config_manager can be imported successfully"""
    from src.services.config_manager import ConfigManager
    assert ConfigManager is not None

def test_default_config_generation():
    """Test that default config includes all required keys"""
    config = ConfigManager()
    
    # Test all required keys exist
    assert config.get('sound_enabled') is True  # Should be True by default
    assert config.get('safety_level') is not None
    assert config.get('volume.master') is not None
    
def test_sound_enabled_default():
    """Test that sound is enabled by default for new installations"""
    config = ConfigManager()
    assert config.get('sound_enabled') is True
```

### Integration Tests
```python
def test_global_config_access():
    """Test that global config instance works across modules"""
    from src.services import config
    from src.services.sound_manager import SoundManager
    
    # Sound manager should use global config
    sound_manager = SoundManager()
    assert sound_manager.enabled is True  # Should match config default
```

## Expected Outcomes

### Technical Fixes
1. **Import Resolution** - All `config_manager` imports work correctly
2. **Complete Configuration Schema** - All required keys present with sensible defaults
3. **Sound System Defaults** - New installations have sound enabled by default
4. **Test Suite Stability** - All configuration-related tests pass consistently

### User Experience Improvements
1. **Better Defaults** - New users get optimal settings out of the box
2. **Reliable Configuration** - Config system doesn't crash on missing keys
3. **Consistent Behavior** - Sound and other features work immediately

## Success Criteria

- [ ] All configuration test failures resolved
- [ ] `import config_manager` works from all test files
- [ ] `safety_level` and other missing keys accessible via config system
- [ ] Sound enabled by default for new installations (test passes)
- [ ] No configuration-related crashes during startup
- [ ] Settings flow integration tests pass

## References

- `issues/configuration-system-import-failures.md` - Original import failure analysis
- `issues/sound-system-default-configuration.md` - Sound default issues
- `configs/default.json` - Current configuration file
- Test failure outputs for specific error details

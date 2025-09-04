# Configuration System Module Import Failures

## Description
Multiple tests are failing due to missing or incorrectly located configuration management modules.

## Affected Tests
- `test_config_manager.py::TestConfigManager::test_default_config_generation`
- `test_config_manager.py::TestConfigSystemIntegration::test_get_current_config_function`
- `test_config_manager.py::TestConfigSystemIntegration::test_initialize_config_system`
- `test_settings_flow.py::TestSettingsFlow::test_complete_flow_integration`
- `test_settings_flow.py::TestSettingsFlow::test_settings_keyboard_navigation`

## Error Details
```
ModuleNotFoundError: No module named 'config_manager'
KeyError: 'safety_level'
AssertionError: False is not true
```

## Root Cause
1. `config_manager` module not found in expected location
2. Missing configuration keys (`safety_level`) in default config
3. Configuration system integration not properly initialized

## Expected Behavior
- `import config_manager` should work from test files
- Default configuration should include all required keys
- Configuration system should initialize properly

## Investigation Areas
1. Location of `config_manager.py` file
2. Python path and module imports
3. Default configuration schema
4. Settings flow integration

## Priority
High - Affects core configuration functionality

## Labels
- bug
- configuration
- module-import
- settings
- testing

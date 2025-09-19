# Configuration System Documentation

P(Doom) features multiple configuration systems:

**[TARGET] Enhanced Settings System (Recommended)**: Modern settings UI with categorical organization, seed management, and community features. See [DEVELOPERGUIDE.md - Enhanced Settings System Architecture](DEVELOPERGUIDE.md#enhanced-settings-system-architecture) for full details.

**[GEAR][EMOJI] Legacy Configuration System (Below)**: Original JSON-based config system for advanced modding and custom game rules.

---

## Legacy Configuration System

P(Doom) features a flexible configuration system that allows players and modders to customize game balance, UI settings, and advanced parameters. This system supports multiple named configurations stored locally.

## Table of Contents
- [Overview](#overview)
- [Player Guide](#player-guide)
- [Developer Guide](#developer-guide)
- [Configurable Parameters](#configurable-parameters)
- [Config File Format](#config-file-format)
- [Modding Support](#modding-support)
- [Troubleshooting](#troubleshooting)

## Overview

The configuration system provides:
- **Multiple named configurations** stored as JSON files in the `configs/` directory
- **Default config generation** with balanced game settings
- **Runtime config switching** through the main menu (planned)
- **Backward compatibility** with existing game saves
- **Modding support** through advanced configuration options

### Architecture

The system follows P(Doom)'s existing patterns:
- JSON-based storage matching tutorial_settings.json and local_highscore.json
- Centralized management through `config_manager.py`
- Integration with the main menu overlay system
- Local-only storage (no cloud sync)

## Player Guide

### Basic Usage

1. **Default Configuration**: The game automatically creates a `default.json` config with balanced settings on first run
2. **Config Selection**: Choose configurations through the main menu (coming soon)
3. **Custom Configs**: Create copies of existing configs to modify

### Current Limitations

- Config selection UI is not yet implemented in the main menu
- Config switching requires restart (runtime switching planned)
- All configs are stored locally only

## Developer Guide

### Using the Config Manager

```python
from config_manager import config_manager, get_current_config, initialize_config_system

# Initialize the system (call once at startup)
initialize_config_system()

# Get current configuration
config = get_current_config()
starting_money = config['starting_resources']['money']

# List available configs
configs = config_manager.list_available_configs()

# Switch configurations
success = config_manager.switch_config('hardcore')

# Create custom configs
custom_config = config_manager.get_default_config()
custom_config['starting_resources']['money'] = 500
config_manager.save_config('hardcore', custom_config)
```

### Integration Points

The config system is designed to integrate with:
- **GameState initialization**: Apply starting resources and limits
- **Main menu system**: Config selection overlay
- **Action point calculation**: Use configured AP bonuses
- **Event system**: Apply difficulty modifiers
- **UI scaling**: Window and font size settings

### Adding New Configurable Parameters

1. Add the parameter to `get_default_config()` in `config_manager.py`
2. Update the relevant game system to use `get_current_config()`
3. Add validation to the test suite in `test_config_manager.py`
4. Document the parameter in this file

## Configurable Parameters

### Starting Resources
```json
"starting_resources": {
  "money": 1000,           // Starting funds
  "staff": 2,              // Initial team size
  "reputation": 50,        // Starting reputation
  "action_points": 3,      // AP per turn
  "doom": 25,              // Initial p(Doom) %
  "compute": 0             // Starting compute resources
}
```

### Action Point System
```json
"action_points": {
  "base_ap_per_turn": 3,     // Base AP granted each turn
  "staff_ap_bonus": 0.5,     // AP bonus per regular staff
  "admin_ap_bonus": 1.0,     // AP bonus per admin assistant
  "max_ap_per_turn": 10      // Maximum AP per turn
}
```

### Resource Limits
```json
"resource_limits": {
  "max_doom": 100,           // P(Doom) ceiling
  "max_reputation": 200,     // Reputation cap
  "max_money": 1000000,      // Practical money limit
  "max_staff": 100           // Staff limit for performance
}
```

### Milestone Thresholds
```json
"milestones": {
  "manager_threshold": 9,         // Staff count for manager milestone
  "board_spending_threshold": 10000, // Spending for board member
  "enhanced_events_turn": 8,      // Turn for enhanced events
  "scrollable_log_turn": 5        // Turn for scrollable log
}
```

### UI Settings
```json
"ui": {
  "window_scale": 0.8,           // Screen size percentage
  "font_scale": 1.0,             // Font size multiplier
  "animation_speed": 1.0,        // Animation speed
  "tooltip_delay": 500,          // Tooltip delay (ms)
  "show_balance_changes": true,  // Resource change indicators
  "show_keyboard_shortcuts": true // Button shortcuts
}
```

### Audio Settings
```json
"audio": {
  "sound_enabled": true,         // Master audio toggle
  "master_volume": 1.0,          // Volume level (0.0-1.0)
  "ui_sounds": true,             // UI feedback sounds
  "feedback_sounds": true        // Action feedback sounds
}
```

### Tutorial and Help
```json
"tutorial": {
  "tutorial_enabled": true,      // Interactive tutorial system (step-by-step guidance)
  "first_time_help": true,       // Context-sensitive hints (Factorio-style, show once)
  "show_tips": true,             // General gameplay tips
  "auto_help_on_errors": true    // Error help system
}
```
**Note**: `tutorial_enabled` controls the interactive tutorial, while `first_time_help` controls context-sensitive hints that appear once when encountering new mechanics.

### Gameplay Settings
```json
"gameplay": {
  "auto_delegation": true,       // Auto-use delegation
  "show_opponent_intel": true,   // Show opponent info
  "event_frequency": 1.0,        // Event probability multiplier
  "difficulty_modifier": 1.0     // General difficulty
}
```

### Advanced Settings (Modding)
```json
"advanced": {
  "debug_mode": false,           // Debug features
  "log_level": "INFO",           // Logging level
  "enable_experimental_features": false,
  "custom_event_weights": {},    // Event probability overrides
  "custom_action_costs": {},     // Action cost overrides
  "custom_upgrade_costs": {}     // Upgrade cost overrides
}
```

## Config File Format

Configuration files are stored as JSON in the `configs/` directory:

```
configs/
[EMOJI][EMOJI][EMOJI] default.json          # Default balanced config
[EMOJI][EMOJI][EMOJI] hardcore.json         # Example custom config
[EMOJI][EMOJI][EMOJI] experimental.json     # Example modded config

current_config.json       # Tracks selected config
```

### Example Config File
```json
{
  "config_name": "Hardcore Mode",
  "description": "Challenging settings for experienced players",
  "version": "1.0.0",
  "starting_resources": {
    "money": 500,
    "staff": 1,
    "reputation": 25,
    "action_points": 2,
    "doom": 35,
    "compute": 0
  },
  "resource_limits": {
    "max_doom": 100,
    "max_reputation": 150,
    "max_money": 500000,
    "max_staff": 50
  },
  // ... other sections
}
```

### Metadata Fields
- `config_name`: Display name for the configuration
- `description`: Brief description of the config's purpose
- `version`: Config format version for compatibility

## Modding Support

### Custom Event Weights
Override default event probabilities:
```json
"custom_event_weights": {
  "competitor_breakthrough": 0.5,  // Reduce competitor events
  "funding_opportunity": 2.0       // Increase funding events
}
```

### Custom Action Costs
Modify action point costs:
```json
"custom_action_costs": {
  "hire_staff": 2,                 // Make hiring more expensive
  "research": 1                    // Make research cheaper
}
```

### Custom Upgrade Costs
Adjust upgrade pricing:
```json
"custom_upgrade_costs": {
  "compute_upgrade": 1500,         // Increase compute cost
  "reputation_boost": 800          // Decrease reputation cost
}
```

### Debug Features
Enable development tools:
```json
"advanced": {
  "debug_mode": true,              // Enable debug overlay
  "log_level": "DEBUG",            // Verbose logging
  "enable_experimental_features": true
}
```

## Troubleshooting

### Common Issues

**Config file not found**: The system automatically creates `default.json` if missing.

**Invalid JSON**: The game falls back to default config and logs a warning.

**Config won't switch**: Ensure the target config file exists and contains valid JSON.

**Settings not applying**: Some settings require a game restart (runtime switching planned).

### File Locations
- **Config directory**: `configs/` (created automatically)
- **Current selection**: `current_config.json` (tracks active config)
- **Default config**: `configs/default.json` (auto-generated)

### Backup and Reset
- **Backup configs**: Copy the entire `configs/` directory
- **Reset to defaults**: Delete `configs/default.json` to regenerate
- **Clear selection**: Delete `current_config.json` to reset to default

### Advanced Debugging
Enable detailed logging by setting:
```json
"advanced": {
  "debug_mode": true,
  "log_level": "DEBUG"
}
```

This will provide detailed information about config loading, validation, and application.

---

For more information:
- [Player Guide](PLAYERGUIDE.md) - General game instructions
- [Developer Guide](DEVELOPERGUIDE.md) - Development and modding
- [config_manager.py](config_manager.py) - Implementation details
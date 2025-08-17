# Runtime Data Management

P(Doom) uses a standardised, cross-platform approach to storing runtime data including saves, logs, and configuration files. This document describes the directory structure, environment overrides, and migration behaviour.

## Default Data Locations

P(Doom) follows platform conventions for storing user data:

### Windows
- **Default**: `%APPDATA%\pdoom1\`
- **Fallback**: `~\AppData\Roaming\pdoom1\` (if APPDATA environment variable is unset)

### macOS
- **Default**: `~/Library/Application Support/pdoom1/`

### Linux/Unix
- **Default**: `$XDG_DATA_HOME/pdoom1/` (if XDG_DATA_HOME is set)
- **Fallback**: `~/.local/share/pdoom1/` (following XDG Base Directory Specification)

## Directory Structure

Within the data directory, P(Doom) organises files as follows:

```
pdoom1/
├── saves/              # Game save files
├── logs/               # Game session logs
├── settings.json       # User preferences
├── leaderboard.json    # Local high scores
└── .migration_done     # Migration completion marker
```

## Environment Override

For development and testing purposes, you can override the default data directory:

### PDOOM1_DATA_DIR
Set this environment variable to specify a custom data directory location:

```bash
# Linux/macOS
export PDOOM1_DATA_DIR="/path/to/custom/data"

# Windows (Command Prompt)
set PDOOM1_DATA_DIR=C:\path\to\custom\data

# Windows (PowerShell)
$env:PDOOM1_DATA_DIR = "C:\path\to\custom\data"
```

This override takes precedence over all platform-specific defaults and is useful for:
- Development environments
- Portable installations
- Testing different configurations
- Custom deployment scenarios

## Legacy Data Migration

P(Doom) automatically handles migration of data from older versions that may have stored files in the repository directory or other legacy locations.

### Migration Behaviour

1. **Automatic Detection**: On first run, P(Doom) scans for legacy files in common locations:
   - `./logs/` directory
   - `./saves/` or `./save/` directories
   - JSON files in the repository root (`local_highscore.json`, `onboarding_progress.json`, etc.)

2. **Safe Migration**: Legacy files are **copied** (not moved) to the new data directory, preserving the original files for safety.

3. **One-Time Notice**: A single informational message is logged during the first migration:
   ```
   MIGRATION: Successfully copied N legacy file(s) to [data directory]
   ```

4. **Idempotent Operation**: Subsequent runs detect the completed migration and remain silent.

5. **Migration Marker**: A `.migration_done` file is created in the data directory with timestamp and migration details.

### Legacy Locations Detected

The migration system automatically detects and migrates:

- **Directory patterns**: `saves`, `save`, `logs`, `runtime`
- **File patterns**: `*.json` files in the repository root
- **Specific files**: `local_highscore.json`, `onboarding_progress.json`, `tutorial_settings.json`, `game_settings.json`

### Migration File Placement

- **Logs**: Files from legacy `logs/` directories → `{data_dir}/logs/`
- **Saves**: Files from legacy `saves/` or `save/` directories → `{data_dir}/saves/`
- **JSON files**: Root JSON files → `{data_dir}/` (data directory root)
- **Other directories**: Preserved with original structure under `{data_dir}/`

## Developer Notes

### Programmatic Access

Use the runtime paths facade for accessing data locations:

```python
from pdoom1.runtime_paths import get_save_path, get_log_path, get_data_directory

# Get paths for specific files
save_file = get_save_path("game_session")  # Returns: {data_dir}/saves/game_session.json
log_file = get_log_path("debug_2024")      # Returns: {data_dir}/logs/debug_2024.txt

# Get directory paths
data_dir = get_data_directory()            # Returns: {data_dir}/
```

### Testing Override

For automated testing, use `PDOOM1_TEST_DATA_DIR` which takes precedence over `PDOOM1_DATA_DIR` but is lower priority than the main override.

### Manual Migration Reset

To re-test migration behaviour:
1. Remove the `.migration_done` marker file from the data directory
2. Restart P(Doom) with legacy files present

## Privacy and Data Management

- **Local Storage Only**: All data remains on the local machine
- **No Telemetry**: Data directories contain no personal information beyond game preferences
- **User Control**: Data can be relocated using environment variables
- **Transparent Migration**: Legacy files are preserved during migration for user confidence

## Troubleshooting

### Migration Issues
- Check file permissions in both source and target directories
- Verify `PDOOM1_DATA_DIR` is writable if using custom location
- Review migration log messages for specific error details

### Path Resolution Issues
- Ensure environment variables are set correctly in your shell
- Verify platform-specific directory conventions are accessible
- Use absolute paths when setting `PDOOM1_DATA_DIR`
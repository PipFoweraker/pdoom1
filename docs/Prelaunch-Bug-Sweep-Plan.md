# Prelaunch Bug Sweep Plan

This document outlines the comprehensive scaffolding implementation for PDoom1's prelaunch bug sweep, focusing on foundational modules that will support future gameplay fixes.

## 🎯 Objectives

1. **Establish foundational services** for audio, settings, timing, and data persistence
2. **Create local scoring system** with JSON persistence and atomic writes
3. **Implement privacy-conscious telemetry** with user opt-out and size limits
4. **Provide cross-platform data storage** using platform-appropriate directories
5. **Add comprehensive testing** with CI/CD pipeline for headless environments

## 🏗️ Architecture Overview

```
pdoom1/
├── services/           # Core game services
│   ├── audio_manager.py    # pygame.mixer wrapper with persistent settings
│   ├── game_clock.py       # Game time (starts 01/Jul/14, +1 week/tick)
│   ├── settings.py         # Versioned JSON settings with atomic writes
│   ├── data_paths.py       # Cross-platform data directories
│   └── telemetry.py        # JSONL logging with 10MB cap
├── scores/             # Scoring and leaderboards
│   ├── local_store.py      # Local JSON leaderboard
│   └── remote_store_stub.py # Placeholder for online scores
└── __init__.py         # Package interface
```

## 📋 Implementation Checklist

### Core Package Structure
- [x] Create `pdoom1/` package with proper `__init__.py`
- [x] Create `pdoom1/services/` subpackage
- [x] Create `pdoom1/scores/` subpackage

### Services Implementation
- [x] **AudioManager** (`services/audio_manager.py`)
  - pygame.mixer wrapper with graceful headless fallback
  - Persistent volume settings (master, SFX, music)
  - Mute state persistence
  - Sound caching and preloading
  
- [x] **GameClock** (`services/game_clock.py`)
  - Starts at July 1, 2014 (01/Jul/14)
  - Advances +1 week per tick (configurable)
  - DD/Mon/YY date format
  - Persistent state with atomic writes
  
- [x] **Settings** (`services/settings.py`)
  - Versioned JSON schema for forward compatibility
  - Device UUID generation and persistence
  - Audio preferences, telemetry toggles
  - Atomic writes to prevent corruption
  
- [x] **DataPaths** (`services/data_paths.py`)
  - Cross-platform user data directories
  - Windows: `%APPDATA%/PDoom1/`
  - macOS: `~/Library/Application Support/PDoom1/`
  - Linux: `~/.local/share/pdoom1/`
  
- [x] **TelemetryLogger** (`services/telemetry.py`)
  - JSONL format for easy parsing
  - 10MB total size cap with automatic cleanup
  - Privacy-conscious with user opt-out
  - Event logging (game_start, level_complete, errors)

### Scoring System
- [x] **LocalLeaderboard** (`scores/local_store.py`)
  - Versioned JSON schema
  - Score sorting and ranking
  - Game mode filtering
  - Player statistics
  
- [x] **RemoteLeaderboard** (`scores/remote_store_stub.py`)
  - Stub implementation for future online features
  - Mock responses for testing
  - Interface for when HTTPS API is implemented

### Data Schemas
- [x] **settings.schema.json** - JSON schema for settings validation
- [x] **leaderboard.schema.json** - JSON schema for leaderboard validation

### Testing & CI
- [x] **test_clock.py** - Game clock functionality tests
- [x] **test_settings.py** - Settings persistence and migration tests  
- [x] **test_scores.py** - Local leaderboard tests
- [x] **CI workflow** (`.github/workflows/tests.yml`) - Headless pygame testing

### Documentation
- [x] **This implementation plan** (`docs/Prelaunch-Bug-Sweep-Plan.md`)
- [x] **PR description template** (`docs/PR_DESCRIPTION.md`)
- [x] **Asset placeholder READMEs** (`assets/sfx/README.md`, `assets/hats/README.md`)

### Dependencies
- [x] **requirements.txt** - Updated with new dependencies
- [x] **requirements-dev.txt** - Development and testing dependencies

## 🔧 Technical Specifications

### Audio Management
- **Persistent Settings**: Volume levels saved to `settings.json`
- **Headless Compatibility**: SDL dummy driver for CI environments
- **Error Handling**: Graceful degradation when audio unavailable
- **Format Support**: WAV, OGG via pygame.mixer

### Game Clock
- **Start Date**: July 1, 2014 00:00:00
- **Advancement**: +1 week per tick (configurable)
- **Format**: DD/Mon/YY (e.g., "01/Jul/14", "08/Jul/14")
- **Persistence**: JSON state file with atomic writes
- **Time Zone**: UTC (no local time complications)

### Settings Management
- **Schema Version**: "1.0.0" (semantic versioning)
- **Device UUID**: Generated once, persisted locally
- **Atomic Writes**: Temp file + rename for corruption prevention
- **Defaults**: Sensible defaults merged with user preferences
- **Migration**: Forward-compatible schema evolution

### Telemetry System
- **Format**: JSONL (newline-delimited JSON)
- **Size Limit**: 10MB total across all log files
- **Retention**: Oldest files deleted first when over limit
- **Privacy**: User opt-out respected, no personal data
- **Events**: game_start, game_end, level_complete, errors, settings_change

### Local Scoring
- **Capacity**: 100 entries by default (configurable)
- **Sorting**: Highest scores first
- **Data**: Score, player name, date, level, game mode, duration
- **UUID**: Unique identifier per entry
- **Persistence**: Atomic JSON writes

## 🧪 Testing Strategy

### Unit Tests
1. **Clock Tests** - Date formatting, advancement, persistence
2. **Settings Tests** - Defaults, migration, atomic writes, corruption recovery
3. **Scores Tests** - Add/sort/rank, game mode filtering, statistics

### CI Environment
- **Headless pygame**: SDL dummy drivers for audio
- **Cross-platform**: Linux (primary), Windows/macOS compatibility
- **Dependencies**: Minimal, pygame + standard library mostly

### Test Data
- **Isolated**: Each test uses temporary directories
- **Deterministic**: Fixed timestamps and UUIDs for reproducible results
- **Edge Cases**: Corruption, missing files, invalid JSON

## 🔒 Privacy & Security

### Data Collection
- **Opt-in Telemetry**: Users can disable entirely
- **Device UUID**: Local only, not transmitted
- **No Personal Data**: No names, emails, or identifying information
- **Local Storage**: All data stays on user's device

### File Security
- **Atomic Writes**: Prevent corruption during power loss
- **Permissions**: User-only access on Unix systems
- **Validation**: JSON schema validation for data integrity
- **Cleanup**: Automatic removal of oversized logs

## 🚀 Future Extensions

This scaffolding enables future implementations:

1. **Online Leaderboards** - Replace stub with HTTPS API calls
2. **Daily Challenges** - Use game clock for time-based events
3. **Analytics Dashboard** - Parse telemetry JSONL for insights
4. **Settings Sync** - Cloud backup of user preferences
5. **Achievement System** - Track progress in telemetry events

## 🎮 Integration Points

### Existing Game Code
- **Non-breaking**: All new modules are additive
- **Optional**: Game works without scaffolding if needed
- **Gradual Adoption**: Can integrate services one at a time

### Service Usage Examples
```python
# Audio with persistent settings
audio = AudioManager()
audio.play_sound(Path("assets/sfx/shot.wav"))
audio.set_volume("sfx", 0.8)

# Game time progression
clock = GameClock()
current_date = clock.get_formatted_date()  # "01/Jul/14"
clock.tick()  # Advance one week

# Score tracking
leaderboard = LocalLeaderboard()
entry = ScoreEntry(score=1000, player_name="Player1", level_reached=5)
success, rank = leaderboard.add_score(entry)

# Event logging (if enabled)
telemetry = TelemetryLogger()
telemetry.log_game_start("normal", "normal")
telemetry.log_level_complete(level=1, time_seconds=45.2, score=250)
```

## ✅ Success Criteria

1. **All tests pass** in CI environment with headless pygame
2. **All modules import** correctly under `pdoom1` package
3. **Cross-platform compatibility** verified on Windows/Linux/macOS
4. **No breaking changes** to existing game functionality
5. **Documentation complete** with clear usage examples
6. **Privacy compliance** with opt-out telemetry and local-only data

This scaffolding provides a solid foundation for implementing specific gameplay fixes while maintaining code quality, user privacy, and cross-platform compatibility.
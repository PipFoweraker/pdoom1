# P(Doom) Music System

**Status**: Implemented v0.1
**Date**: 2025-11-20
**Issue**: #457

---

## Overview

The music system provides context-aware background music with crossfade transitions and volume controls integrated into the settings menu.

## Features

### Audio Infrastructure
- SUCCESS **Music Bus**: Separate audio bus (index 2) for music playback
- SUCCESS **Volume Control**: Dedicated Music Volume slider in settings (0-100%)
- SUCCESS **Persistence**: Music volume saved to user config file
- SUCCESS **Real-time Updates**: Volume changes apply immediately

### MusicManager Autoload
- SUCCESS **Track Management**: Organizes music by game context
- SUCCESS **Crossfade**: Smooth 2-second transitions between tracks
- SUCCESS **Context-Aware**: Different music for menus, gameplay, and game over
- SUCCESS **Continuous Playback**: Automatically advances to next track

## Music Library

### Menu Music (Welcome Screen)
- `PDoom1 seleciton beeyoowee.wav` - Selection/UI sound
- `PDOOMN ST1 (safe).mp3` - Safe zone menu music

### Gameplay Music (Active Game)
- `PDoom1 Descent gradient.mp3` - Descent/progression theme
- `PDoom1 Local maxima.mp3` - Optimization theme
- `PDoom1 Power spike.mp3` - Intensity/challenge theme
- `PDoom1 Undetected sandbagging.mp3` - Tension/deception theme

### Defeat Music (Game Over)
- `PDoom Out_of_distribution.mp3` - Loss/failure theme

### Victory Music
- Reserved for future implementation

## Technical Architecture

### File Structure
```
godot/
|--- autoload/
|   `--- music_manager.gd          # Music system singleton
|--- assets/audio/music/            # Music track files
`--- scenes/
    `--- settings_menu.tscn         # Music volume slider
```

### Audio Buses
```
Master (0)
|--- SFX (1)
`--- Music (2)   <-  Music tracks play here
```

### Autoload Order
1. `GameConfig` - Loads music_volume setting
2. `MusicManager` - Initializes music system
3. Other autoloads...

## Usage Examples

### Play Context Music
```gdscript
# In welcome screen
MusicManager.play_context(MusicManager.MusicContext.MENU)

# In gameplay
MusicManager.play_context(MusicManager.MusicContext.GAMEPLAY)

# On game over
MusicManager.play_context(MusicManager.MusicContext.DEFEAT)
```

### Volume Control
```gdscript
# Set volume (0-100)
MusicManager.set_volume(80)

# Volume is also controlled via GameConfig
GameConfig.set_setting("music_volume", 50)
```

### Music Control
```gdscript
# Stop music
MusicManager.stop_music()

# Pause/Resume
MusicManager.pause_music()
MusicManager.resume_music()

# Enable/Disable
MusicManager.set_music_enabled(false)
```

## Settings Menu Integration

The Music Volume slider follows the established UI pattern:

**Location**: Settings Menu > Audio Settings > Music Volume

**Components**:
- Label: "Music Volume:"
- HSlider: 0-100 range, default 80%
- ValueLabel: Shows current percentage

**Integration**:
```gdscript
# In settings_menu.gd
@onready var music_volume_slider = $VBox/.../MusicVolumeRow/Slider
@onready var music_volume_label = $VBox/.../MusicVolumeRow/ValueLabel

func _on_music_volume_changed(value: float):
    music_volume_label.text = "%d%%" % int(value)
    GameConfig.set_setting("music_volume", int(value), false)
```

## Music Track Organization

Tracks are organized by context in `MusicManager.music_library`:

```gdscript
enum MusicContext {
    MENU,      # Welcome screen, settings
    GAMEPLAY,  # Active game session
    VICTORY,   # Win screen
    DEFEAT     # Loss screen
}

var music_library = {
    MusicContext.MENU: [...],
    MusicContext.GAMEPLAY: [...],
    MusicContext.DEFEAT: [...]
}
```

## Crossfade System

### Dual AudioStreamPlayer Architecture
- `player_a` and `player_b` for seamless crossfading
- `active_player` - Currently audible track
- `inactive_player` - Used for next track during crossfade

### Crossfade Process
1. New track loads on inactive player at -80 dB (silent)
2. Both players run simultaneously
3. Tween fades active player to -80 dB over 2 seconds
4. Tween fades inactive player to 0 dB over 2 seconds
5. Players swap roles, old track stops

### Benefits
- No audio gaps between tracks
- Professional smooth transitions
- Maintains game atmosphere

## Configuration Persistence

Music volume is saved in `user://config.cfg`:

```ini
[audio]
master_volume=80
sfx_volume=80
music_volume=80
```

## Future Enhancements

- [ ] Victory music tracks
- [ ] Dynamic music based on doom level (adaptive music)
- [ ] Music intensity scaling with game events
- [ ] Playlist management (shuffle, repeat modes)
- [ ] Per-track volume normalization
- [ ] Music visualizer in settings
- [ ] Custom music folder support

## Testing

### Manual Tests
1. **Volume Control**
   - Open Settings > Adjust Music Volume slider
   - Verify volume changes in real-time
   - Save settings and restart - volume persists

2. **Context Switching**
   - Launch game from welcome screen
   - Verify menu music plays
   - Start game - music crossfades to gameplay
   - Trigger game over - music changes to defeat theme

3. **Crossfade Quality**
   - Let tracks play through to next track
   - Verify smooth 2-second crossfade
   - No audio pops or gaps

4. **Persistence**
   - Set custom volume (e.g., 30%)
   - Close and reopen game
   - Verify volume setting retained

### Automated Tests
```gdscript
# Future: Add GUT tests for MusicManager
# - Test context switching
# - Test volume calculations
# - Test crossfade timing
```

## Troubleshooting

### Music Not Playing
1. Check audio bus configuration in `default_bus_layout.tres`
2. Verify Music bus (index 2) exists
3. Check music files exist in `assets/audio/music/`
4. Verify volume not set to 0%

### Crossfade Issues
1. Check `CROSSFADE_DURATION` constant (2.0 seconds)
2. Verify both players initialized correctly
3. Check for tween conflicts

### Volume Not Persisting
1. Verify `GameConfig.save_config()` called in settings
2. Check file permissions on `user://config.cfg`
3. Verify `music_volume` key in config file

## Code References

- MusicManager: [autoload/music_manager.gd](../godot/autoload/music_manager.gd)
- GameConfig: [autoload/game_config.gd](../godot/autoload/game_config.gd:14) (music_volume variable)
- Settings Menu UI: [scenes/settings_menu.tscn](../godot/scenes/settings_menu.tscn:178) (MusicVolumeRow)
- Settings Menu Logic: [scripts/ui/settings_menu.gd](../godot/scripts/ui/settings_menu.gd:108) (_on_music_volume_changed)
- Welcome Screen: [scripts/ui/welcome_screen.gd](../godot/scripts/ui/welcome_screen.gd:51) (plays MENU context)
- Game Controller: [scripts/game_controller.gd](../godot/scripts/game_controller.gd:50) (plays GAMEPLAY context)

---

**Implementation Notes**:
- Follows existing autoload pattern (similar to NotificationManager, ThemeManager)
- Consistent UI styling matching current settings menu design
- Uses AI Safety-themed track names (descent gradient, local maxima, power spike, etc.)
- Music files placed in `godot/assets/audio/music/` from original `sounds/musicdump/20_nov_2025/`

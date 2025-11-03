# Custom Sound Overrides

This directory allows you to override built-in sound effects with custom audio files.

## How to Use

1. **Place sound files** (.wav or .ogg) in this directory
2. **Name files to match event keys** - the filename becomes the sound key
3. **Restart the game** - custom sounds load automatically on startup

## Supported File Formats

- **WAV** (.wav) - Recommended for compatibility
- **OGG** (.ogg) - Good compression, smaller file sizes

## Available Event Keys

Name your files to match these event keys to override built-in sounds:

**Basic Game Sounds:**
- `ap_spend.wav` - Action Point spend sound
- `popup_open.wav` - Popup dialog open sound  
- `popup_close.wav` - Popup dialog close sound
- `popup_accept.wav` - Popup dialog accept/confirm sound
- `error_beep.wav` - Error feedback sound (easter egg)
- `blob.wav` - Employee hiring sound
- `zabinga.wav` - Research paper completion celebration

**Enhanced Feedback Sounds (v0.9.1+):**
- `milestone.wav` - Achievement milestone celebrations (manager hiring, board members)
- `warning.wav` - Cautionary alerts for doom level increases
- `danger.wav` - Urgent alerts for critical doom levels (80%+)
- `success.wav` - Positive feedback for successful actions
- `research_complete.wav` - Major research breakthrough fanfare

## Examples

```bash
# Override the AP spend sound
cp my_click_sound.wav ap_spend.wav

# Override the celebration sound
cp my_celebration.ogg zabinga.ogg

# Override popup sounds
cp open_sound.wav popup_open.wav
cp close_sound.wav popup_close.wav

# Override milestone achievements  
cp triumph_fanfare.wav milestone.wav

# Override warning alerts
cp alert_tone.wav warning.wav

# Override danger alerts
cp alarm_sound.wav danger.wav
```

## Subdirectories

You can organize sounds in subdirectories - they will be loaded recursively:

```
sounds/
|-- ui/
|   |-- popup_open.wav
|   `-- popup_close.wav
|-- gameplay/
|   |-- ap_spend.wav
|   `-- blob.wav
`-- celebration/
    `-- zabinga.wav
```

## Technical Notes

- Files are loaded during game startup after built-in sounds are created
- Custom sounds automatically override built-in sounds when keys match
- Invalid or corrupted sound files are ignored gracefully
- The system only works when audio hardware is available
- File names are case-insensitive (AP_SPEND.WAV works the same as ap_spend.wav)

## Audio Specifications

For best results:
- **Sample Rate**: 22050 Hz or 44100 Hz
- **Bit Depth**: 16-bit recommended  
- **Channels**: Mono or Stereo
- **Duration**: Keep sound effects under 3 seconds for good UX

## Testing Your Sounds

After adding custom sound files:
1. Restart the game
2. Trigger the associated game events to hear your custom sounds
3. Check that the sounds play at appropriate moments

For example, to test `ap_spend.wav`, perform any action that costs Action Points in the game.
# Sound Effects Assets

This directory will contain sound effect files for PDoom1.

## Supported Formats
- **WAV** - Recommended for short sound effects
- **OGG** - Good compression for longer sounds

## Naming Convention
- Use descriptive names: `shot.wav`, `explosion.wav`, `footstep.wav`
- Use lowercase with underscores for spaces
- Include variant numbers if multiple versions: `shot_01.wav`, `shot_02.wav`

## Organization
```
sfx/
├── weapons/          # Weapon-related sounds
├── ambient/          # Background/environment sounds
├── ui/               # User interface sounds
└── enemy/            # Enemy-related sounds
```

## Audio Specifications
- **Sample Rate**: 22050 Hz or 44100 Hz
- **Bit Depth**: 16-bit recommended
- **Channels**: Mono or Stereo
- **Length**: Keep under 10 seconds for sound effects

## Usage
Sound effects are loaded and played through the AudioManager service:

```python
from pdoom1.services.audio_manager import AudioManager

audio = AudioManager()
audio.play_sound(Path("assets/sfx/weapons/shot.wav"))
```

## License
All sound effects must be compatible with the project license or properly attributed if using external sources.
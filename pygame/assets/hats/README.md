# Hat Assets

This directory will contain hat/cosmetic assets for PDoom1 characters.

## File Formats
- **PNG** - Recommended for sprites with transparency
- **GIF** - For simple animations
- **JSON** - For hat metadata and positioning

## Naming Convention
- Use descriptive names: `fedora.png`, `top_hat.png`, `baseball_cap.png`
- Use lowercase with underscores for spaces
- Include size suffix if multiple resolutions: `fedora_32x32.png`

## Hat Specifications
- **Base Size**: 32x32 pixels (can be smaller if hat is small)
- **Transparency**: Use alpha channel for non-rectangular hats
- **Positioning**: Hats should be positioned to sit on top of character head
- **Style**: Match the pixel art style of the base game

## Metadata Format
Each hat should have a corresponding JSON file with metadata:

```json
{
  'name': 'Fedora',
  'description': 'A classic fedora hat',
  'rarity': 'common',
  'unlock_condition': 'score_1000',
  'offset_x': 0,
  'offset_y': -8,
  'animated': false
}
```

## Organization
```
hats/
? common/           # Common/default hats
? rare/            # Rare unlockable hats
? legendary/       # Legendary/special hats
? seasonal/        # Holiday/seasonal hats
```

## Unlock Conditions
- `score_X` - Unlock at score threshold
- `level_X` - Unlock at level
- `time_played_X` - Unlock after playtime
- `achievement_X` - Unlock via specific achievement
- `default` - Available from start

## Integration
Hats will be integrated through the cosmetics system:

```python
# Future implementation
cosmetics.equip_hat('fedora')
cosmetics.get_available_hats(player_stats)
```

## License
All hat assets must be original creations or properly licensed for use in the project.
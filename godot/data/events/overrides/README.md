# Event Overrides

This directory contains game-balance overrides for pdoom-data events.

## Principle

**pdoom-data owns facts and defaults; pdoom1 owns balance tuning via overrides.**

Never modify pdoom-data for game balance. Instead, create override files here that deep-merge onto base events.

## How Overrides Work

1. EventService loads base events from `data/historical_events.json` (pdoom-data export)
2. Override files in this directory are loaded and merged onto matching events
3. Only specified fields are overridden; unspecified fields keep their base values

## File Format

Each override file is a JSON object mapping event IDs to override values:

```json
{
  "event_id_here": {
    "impacts": [
      {"variable": "money", "change": -50000}
    ],
    "rarity": "legendary",
    "pdoom_impact": 10
  }
}
```

## Available Override Fields

- `impacts` - Array of `{variable, change}` pairs (replaces base impacts)
- `rarity` - Override rarity tier: "common", "rare", or "legendary"
- `pdoom_impact` - Direct doom impact value
- `category` - Override event category
- `title` - Override display title
- `description` - Override description text

## Creating an Override

1. Find the event ID in `data/historical_events.json`
2. Create a JSON file (any name) in this directory
3. Add the event ID as a key with your override values
4. Restart the game to apply changes

## Example

See `example.json` for a working example of tuning the FTX collapse event.

## Variable Mapping

pdoom-data uses different variable names. See `balancing/variable_mapping.json` for the full mapping:

| pdoom-data | Game Variable |
|------------|---------------|
| cash       | money         |
| stress     | doom          |
| vibey_doom | doom          |
| reputation | reputation    |
| papers     | papers        |

## Tips

- Start with small adjustments and playtest
- Use `rarity` to control how often major events appear
- Negative money changes should account for early-game economy
- Doom impacts above 10 are very significant

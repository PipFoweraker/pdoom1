# Scenario Pack System

P(Doom) supports custom scenarios through a simple JSON-based mod system. Scenarios can modify starting conditions, add custom events, and create entirely new gameplay experiences.

## Quick Start

1. Create a `.json` file in `godot/data/scenarios/`
2. Define your scenario with at least a `title` and `description`
3. Launch the game - your scenario appears in the Custom Game setup screen

## Scenario Format

Scenarios are defined as JSON files with the following structure:

```json
{
  "title": "Your Scenario Name",
  "description": "A brief description shown in the scenario selector",
  "author": "Your Name",
  "version": "1.0",
  "starting_resources": {
    "money": 245000,
    "compute": 100,
    "research": 0,
    "papers": 0,
    "reputation": 50,
    "doom": 50,
    "action_points": 3,
    "stationery": 100
  },
  "config": {
    "start_year": 2017,
    "start_month": 7,
    "start_day": 3
  },
  "events": []
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Display name for the scenario (shown in dropdown) |
| `description` | string | Brief description (shown below dropdown) |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `author` | string | "Unknown" | Scenario creator name |
| `version` | string | "1.0" | Scenario version |
| `starting_resources` | object | {} | Override starting resource values |
| `config` | object | {} | Configuration overrides |
| `events` | array | [] | Custom events for this scenario |

## Starting Resources

Override any of the following starting values:

| Resource | Default | Description |
|----------|---------|-------------|
| `money` | 245000 | Starting funds ($) |
| `compute` | 100 | Computational resources |
| `research` | 0 | Research points |
| `papers` | 0 | Published papers |
| `reputation` | 50 | Lab reputation (0-100) |
| `doom` | 50 | P(Doom) meter (0-100, lose at 100) |
| `action_points` | 3 | Actions per turn |
| `stationery` | 100 | Office supplies |

Only include resources you want to change - unspecified values use defaults.

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `start_year` | int | 2017 | Starting year |
| `start_month` | int | 7 | Starting month (1-12) |
| `start_day` | int | 3 | Starting day of month |

## Custom Events

Events trigger during gameplay based on conditions. Add custom events to create scenario-specific narrative moments:

```json
{
  "events": [
    {
      "id": "my_custom_event",
      "name": "Event Title",
      "description": "What the player sees when the event triggers.",
      "type": "popup",
      "trigger_type": "turn_exact",
      "trigger_turn": 5,
      "repeatable": false,
      "options": [
        {
          "id": "option_a",
          "text": "Choose this option",
          "costs": {"money": 1000},
          "effects": {"reputation": 5},
          "message": "Feedback shown after choosing"
        },
        {
          "id": "option_b",
          "text": "Choose this instead",
          "costs": {},
          "effects": {},
          "message": "Nothing happens"
        }
      ]
    }
  ]
}
```

### Event Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique event identifier |
| `name` | string | Yes | Event title shown to player |
| `description` | string | Yes | Event description text |
| `type` | string | Yes | Currently only "popup" is supported |
| `trigger_type` | string | Yes | How the event triggers (see below) |
| `repeatable` | boolean | No | Can this event trigger multiple times? |
| `options` | array | Yes | Player choices (at least one required) |

### Trigger Types

| Type | Additional Fields | Description |
|------|-------------------|-------------|
| `turn_exact` | `trigger_turn` | Triggers on exact turn number |
| `random` | `probability`, `min_turn` | Random chance each turn after min_turn |
| `turn_and_resource` | `trigger_turn`, `trigger_condition` | Turn + resource condition |

### Event Options

Each option in the `options` array:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique option identifier |
| `text` | string | Button text shown to player |
| `costs` | object | Resources required (deducted on selection) |
| `effects` | object | Resource changes applied on selection |
| `message` | string | Feedback message shown after selection |

### Costs and Effects

Both use the same format - a dictionary of resource changes:

```json
{
  "money": 5000,
  "compute": -10,
  "reputation": 5,
  "doom": -3,
  "action_points": 1
}
```

Positive values add resources, negative values subtract them.

## Example Scenarios

### Bootstrap Mode
Extra resources for learning the game:
```json
{
  "title": "Bootstrap Mode",
  "description": "Start with extra funding. Perfect for learning.",
  "starting_resources": {
    "money": 500000,
    "compute": 200,
    "reputation": 60,
    "doom": 40
  }
}
```

### Crisis Mode
Challenging start with higher doom:
```json
{
  "title": "Crisis Mode",
  "description": "The AI race is heating up. Can you turn the tide?",
  "starting_resources": {
    "money": 150000,
    "doom": 65
  },
  "config": {
    "start_year": 2020
  }
}
```

### Sandbox Mode
Unlimited resources for experimentation:
```json
{
  "title": "Sandbox Mode",
  "description": "Unlimited resources. Just explore and have fun.",
  "starting_resources": {
    "money": 10000000,
    "compute": 1000,
    "action_points": 5,
    "doom": 30
  }
}
```

## File Locations

| Location | Description |
|----------|-------------|
| `godot/data/scenarios/` | Built-in scenarios (shipped with game) |
| `user://scenarios/` | User-created scenarios (platform-specific user directory) |

The user directory varies by platform:
- **Windows**: `%APPDATA%\Godot\app_userdata\P(Doom)\scenarios\`
- **macOS**: `~/Library/Application Support/Godot/app_userdata/P(Doom)/scenarios/`
- **Linux**: `~/.local/share/godot/app_userdata/P(Doom)/scenarios/`

## Tips for Scenario Authors

1. **Start simple** - Begin with just resource overrides before adding events
2. **Test incrementally** - Add one event at a time and test each
3. **Balance carefully** - Extreme resource values can break gameplay
4. **Use unique IDs** - Event and option IDs must be unique within your scenario
5. **Keep descriptions short** - UI space is limited

## Troubleshooting

### Scenario not appearing
- Check file is valid JSON (use a JSON validator)
- Ensure file has `.json` extension
- Verify `title` and `description` fields exist

### Events not triggering
- Check `trigger_type` matches your trigger fields
- Verify turn numbers (game starts at turn 0)
- Check `repeatable` flag if expecting multiple triggers

### Resource changes not working
- Verify resource names are spelled correctly
- Check that values are numbers, not strings

# Historical Data Integration Guide

**Purpose**: Document how historical AI safety/capabilities data flows into P(Doom)

---

## Overview

P(Doom) uses real historical events from the AI safety and capabilities landscape to create an authentic "default timeline". This timeline represents what happens if the player takes no action - the baseline p(doom) they're trying to improve upon.

### Time Loop Concept

- **Default Start Date**: July 1, 2017 (configurable)
- **Timeline**: 2017 - Present (expandable backward in time)
- **Historical Accuracy**: Real events trigger on their actual dates
- **Player Influence**: Some events can be influenced, others are historical facts

---

## Data Flow Architecture

```
+-----------------------------------------------------------+
| pdoom-data Repository (separate repo)                   |
|                                                          |
| raw/  ->  cleaned/  ->  transformed/                          |
|                                                          |
| - Alignment Research Dataset                            |
| - Historical papers, conferences                        |
| - Organization founding dates                           |
| - Funding rounds, governance events                     |
`-----------------------------------------------------------`
                            v 
              [Automated Sync Pipeline]
                            v 
+-----------------------------------------------------------+
| pdoom1 Game Repository                                  |
|                                                          |
| shared/data/historical_timeline/                        |
| godot/data/historical_timeline/                         |
|                                                          |
| Python Loader: src/data/historical_timeline_loader.py  |
| Godot Loader: godot/scripts/data/timeline_loader.gd    |
`-----------------------------------------------------------`
                            v 
              [Game Loads Events at Runtime]
                            v 
+-----------------------------------------------------------+
| Gameplay                                                |
|                                                          |
| - Events trigger based on game date                     |
| - Player can interact with some events                  |
| - Default timeline establishes baseline p(doom)         |
`-----------------------------------------------------------`
```

---

## Directory Structure

### pdoom1 Repository

```
pdoom1/
|--- shared/data/
|   |--- historical_timeline/      # Timeline events (Python)
|   |   |--- 2017.json
|   |   |--- 2018.json
|   |   `--- ...
|   |--- researchers/              # Researcher profiles (Python)
|   `--- organizations/            # Organization data (Python)
|
|--- godot/data/
|   |--- historical_timeline/      # Timeline events (Godot)
|   |   |--- 2017.json
|   |   |--- 2018.json
|   |   `--- ...
|   |--- researchers/              # Researcher profiles (Godot)
|   `--- organizations/            # Organization data (Godot)
|
|--- src/data/
|   `--- historical_timeline_loader.py  # Python data loader
|
|--- godot/scripts/data/
|   `--- timeline_loader.gd       # Godot data loader
|
`--- scripts/
    |--- sync_from_pdoom_data.sh  # Sync script
    `--- validate_historical_data.py  # Validation script
```

---

## Event Data Format

### Timeline Event Structure

```json
{
  "year": 2017,
  "default_timeline_events": [
    {
      "event_id": "unique_event_id",
      "trigger_date": "2017-08-11",
      "trigger_turn": 6,
      "trigger_condition": "always | player_has_safety_researchers >= 1",
      "type": "capability | paper_publication | governance | ...",
      "name": "Event Title",
      "description": "Brief description for UI",
      "detailed_description": "Longer context for tooltips",
      "game_effect": {
        "doom_increase": 2.0,
        "doom_decrease": -1.0,
        "reputation_boost": 5,
        "unlocks_research_option": "research_id"
      },
      "player_can_influence": true,
      "historical_fact": true,
      "source": "https://source-url.com",
      "attribution": "Source name",
      "tags": ["tag1", "tag2"],
      "related_orgs": ["OpenAI", "DeepMind"],
      "related_people": ["Researcher Name"],
      "options": [
        {
          "id": "option_id",
          "text": "Player choice text",
          "costs": {"action_points": 1, "money": 5000},
          "effects": {"research": 10, "doom": -0.5}
        }
      ]
    }
  ],
  "background_events": [
    {
      "event_id": "background_event_id",
      "date": "2017-12-04",
      "name": "Conference Name",
      "description": "Flavor text event",
      "appears_in_log": true,
      "flavor_text_only": true
    }
  ]
}
```

### Event Types

- **capability**: Major AI capabilities milestone
- **paper_publication**: Research paper published
- **conference**: AI safety/ML conference
- **org_founding**: Organization launch
- **funding**: Funding round announcement
- **governance**: Policy/regulatory event

### Trigger Conditions

- `"always"`: Event always triggers on date
- `"player_has_safety_researchers >= N"`: Requires N safety researchers
- `"turn >= N"`: After turn N
- Complex conditions: Can evaluate game state

---

## Using the Data Loaders

### Python Usage

```python
from src.data.historical_timeline_loader import TimelineLoader

# Initialize loader
loader = TimelineLoader()

# Load all events from 2017 onwards
events = loader.load_all_events(start_year=2017)

# Load specific year
year_2018 = loader.load_year(2018)

# Get events for specific date
today_events = loader.get_events_for_date("2017-08-11")

# Filter by type
papers = loader.get_events_by_type("paper_publication")

# Filter by tag
safety_events = loader.get_events_by_tag("safety")

# Get available years
years = loader.get_available_years()
```

### Godot Usage

```gdscript
# Create loader
var loader = TimelineLoader.new()

# Load all events from 2017 onwards
var events = loader.load_all_events(2017)

# Load specific year
var year_2018 = loader.load_year(2018)

# Get events for specific date
var today_events = loader.get_events_for_date("2017-08-11")

# Filter by type
var papers = loader.get_events_by_type("paper_publication")

# Filter by tag
var safety_events = loader.get_events_by_tag("safety")

# Get available years
var years = loader.get_available_years()

# Static convenience function
var quick_events = TimelineLoader.load_timeline(2017)
```

---

## Syncing Data from pdoom-data

### Manual Sync

```bash
# From pdoom1 repository root
./scripts/sync_from_pdoom_data.sh ../pdoom-data

# Or specify custom path
./scripts/sync_from_pdoom_data.sh /path/to/pdoom-data
```

### What Gets Synced

1. **Timeline Events**: `pdoom-data/transformed/timeline_events/`  ->  `shared/data/historical_timeline/` and `godot/data/historical_timeline/`
2. **Researcher Profiles**: `pdoom-data/transformed/researcher_profiles/`  ->  `shared/data/researchers/` and `godot/data/researchers/`
3. **Organizations**: `pdoom-data/cleaned/organizations/`  ->  `shared/data/organizations/` and `godot/data/organizations/`

### Sync Manifest

After sync, check `shared/data/SYNC_MANIFEST.json` for details:

```json
{
  "sync_date": "2025-11-03T12:34:56Z",
  "pdoom_data_commit": "abc123...",
  "pdoom_data_branch": "main",
  "files_synced": {
    "timeline_events": 9,
    "researcher_profiles": 50,
    "organizations": 20
  }
}
```

---

## Validation

### Running Validation

```bash
# Basic validation
python scripts/validate_historical_data.py

# Verbose output
python scripts/validate_historical_data.py --verbose

# Expected output
=== P(Doom) Historical Data Validation ===

Validating timeline events...
  [OK] 2017.json
  [OK] 2018.json
  ...

[SUCCESS] All historical data validated successfully
   Files checked: 18
```

### What Gets Validated

1. **JSON Syntax**: All files must be valid JSON
2. **Required Fields**: Events must have id, date, type, name, etc.
3. **Date Formats**: Dates must be YYYY-MM-DD
4. **Event Types**: Must use valid event type
5. **Source URLs**: Must be valid URLs
6. **Year Matching**: File year must match data year

### Integration with CI/CD

Validation runs automatically in GitHub Actions before builds:

```yaml
- name: Validate historical data
  run: python scripts/validate_historical_data.py
```

Builds fail if validation fails, ensuring data integrity.

---

## Weekly Build Integration

### Build Pipeline

1. **Data Sync** (if pdoom-data updated)
   - Automated PR created in pdoom1
   - Validation runs on PR
   - Merge after review

2. **Pre-Build Validation**
   - `validate_historical_data.py` runs
   - Checks all JSON files
   - Fails build if errors found

3. **Build Process**
   - Historical data included in builds
   - Python: Files copied to dist/
   - Godot: Files exported with game

4. **Release**
   - Weekly builds include latest historical data
   - Manifest shows data version
   - League cycles use updated timeline

---

## Adding New Events

### Quick Process

1. **Add to pdoom-data** (separate repo)
   - Create/update year file in `transformed/timeline_events/`
   - Follow event schema
   - Include source attribution

2. **Validate**
   ```bash
   python scripts/validate_data.py
   ```

3. **Sync to pdoom1**
   ```bash
   ./scripts/sync_to_pdoom1.sh
   ```

4. **Test in pdoom1**
   ```bash
   python src/data/historical_timeline_loader.py
   python scripts/validate_historical_data.py
   ```

5. **Commit & PR**
   - Automated or manual
   - Both repos updated

---

## Best Practices

### Data Quality

1. **Source Everything**: Every event needs a source URL
2. **Verify Dates**: Cross-reference multiple sources
3. **Meaningful Effects**: Game effects should reflect real impact
4. **Player Agency**: Mark which events players can influence

### Development Workflow

1. **Never Edit Directly in pdoom1**: Always edit in pdoom-data
2. **Always Validate**: Run validation before committing
3. **Test Both Versions**: Check Python and Godot loaders
4. **Document Sources**: Maintain SOURCES.md in pdoom-data

### Performance

1. **Lazy Loading**: Load years as needed, not all at once
2. **Caching**: Godot loader caches loaded years
3. **Filtering**: Use type/tag filters to reduce data size

---

## Troubleshooting

### Sync Issues

**Problem**: Sync script can't find pdoom-data
```bash
ERROR: pdoom-data repository not found at ../pdoom-data
```

**Solution**: Specify correct path
```bash
./scripts/sync_from_pdoom_data.sh /correct/path/to/pdoom-data
```

### Validation Errors

**Problem**: Invalid JSON
```
2017.json: Invalid JSON: Expecting ',' delimiter: line 45 column 5
```

**Solution**: Fix JSON syntax, use JSON linter

**Problem**: Missing required field
```
2018.json/event_123: Missing required field 'source'
```

**Solution**: Add missing field to event

### Loading Errors

**Problem**: Events not loading in game
```python
FileNotFoundError: Timeline data not found: shared/data/historical_timeline
```

**Solution**: Run sync script or create directories manually

---

## Future Enhancements

### Planned Features

1. **Event Dependencies**: Events that unlock other events
2. **Dynamic Effects**: Game effects that scale with player state
3. **Alternative Histories**: "What if" scenarios
4. **Community Events**: Player-submitted events

### Extensibility

The data format is designed to be extended:
- Add new event types
- Add new trigger conditions
- Add new game effects
- Add new metadata fields

Just update the schema documentation and validation scripts.

---

## Related Documentation

- [PDOOM_DATA_INTEGRATION_PLAN.md](../../PDOOM_DATA_INTEGRATION_PLAN.md) - Full integration plan
- [GitHub Issue #431](https://github.com/PipFoweraker/pdoom1/issues/431) - Documentation refinement
- pdoom-data repository (to be created) - Data source repository

---

**Last Updated**: 2025-11-03
**Status**: Initial Implementation Complete
**Next Steps**: Create pdoom-data repository, expand timeline to 2018-2025

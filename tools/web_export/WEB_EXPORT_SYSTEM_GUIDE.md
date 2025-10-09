# P(Doom)1 Web Export System

This directory contains the web export functionality that enables global leaderboards by providing leaderboard data in a format compatible with the [pdoom1-website](https://github.com/PipFoweraker/pdoom1-website) repository.

## Overview

The web export system addresses the 'Data Requests for Main Repository' outlined in the website's [leaderboard integration specification](https://github.com/PipFoweraker/pdoom1-website/blob/main/docs/03-integrations/leaderboard-integration-spec.md).

## Components

### Core Scripts

- **`export_leaderboards.py`** - Main export script and CLI interface
- **`api_format.py`** - Converts internal leaderboard format to web API format  
- **`privacy_filter.py`** - Applies privacy controls and anonymization

### Command Line Interface

The exact CLI interface requested by the website:

```bash
# Export all leaderboards for web consumption
python -m src.leaderboard export --format web --output ./web_export/

# Export specific seed
python -m src.leaderboard export --seed party-demo-seed --output ./web_data/

# Show available leaderboards
python -m src.leaderboard list

# Check system status
python -m src.leaderboard status
```

Alternative direct interface:

```bash
# Direct tool access
python tools/web_export/export_leaderboards.py --output ./web_export/
python tools/web_export/export_leaderboards.py --status
```

## Features

### GLOBAL Web API Format
- **Compatible JSON Structure**: Matches the exact format expected by pdoom1-website
- **Metadata Fields**: Includes game version, timestamps, player counts, and export source
- **Entry Format**: Standard fields like `score`, `player_name`, `date`, `level_reached`, plus game-specific metrics

### SECURE Privacy Protection  
- **Anonymous Player Names**: Uses deterministic lab name generation for consistent anonymization
- **Configurable Levels**: `none`, `standard`, `strict` anonymization levels
- **Sensitive Data Filtering**: Rounds or excludes sensitive numerical data
- **Privacy Manifest**: Generates documentation of privacy controls applied

### METRICS Export Options
- **Individual Seeds**: Export leaderboards for specific game seeds
- **Combined Leaderboard**: Creates unified leaderboard for general display
- **Batch Export**: Process all available leaderboards at once
- **Metadata Tracking**: Detailed export logs and statistics

## Output Format

### Individual Leaderboard Files
```json
{
  'meta': {
    'generated': '2025-10-09T21:37:14.150421Z',
    'game_version': 'v0.9.1',
    'total_seeds': 1,
    'total_players': 4,
    'export_source': 'game-repository',
    'api_version': '1.0.0',
    'config_hash': 'c53217a3',
    'note': 'Exported from actual game leaderboard data',
    'privacy_filtered': true,
    'anonymization_level': 'standard',
    'privacy_notice': 'Player names have been anonymized...'
  },
  'seed': 'party-demo-seed',
  'economic_model': 'Bootstrap_v0.4.1',
  'entries': [
    {
      'score': 25,
      'player_name': 'Atlas Computing',
      'date': '2025-09-13T16:01:32.035414',
      'level_reached': 25,
      'game_mode': 'Bootstrap_v0.4.1',
      'duration_seconds': 4.1e-05,
      'entry_uuid': 'cacd160c-6c5f-42f5-a073-d06db9cf70c7',
      'final_money': 100000,
      'final_staff': 5,
      'final_reputation': 50,
      'final_doom': 25,
      'final_compute': 10000,
      'research_papers_published': 0,
      'technical_debt_accumulated': 0
    }
  ]
}
```

### Export Metadata
```json
{
  'export_timestamp': '2025-10-09T21:37:35.892019',
  'game_version': 'v0.9.1',
  'export_tool_version': '1.0.0',
  'privacy_filtered': true,
  'exported_leaderboards': [
    {
      'seed': 'party-demo-seed',
      'filename': 'leaderboard_party-demo-seed.json',
      'entry_count': 4,
      'top_score': 25
    }
  ]
}
```

## Integration with pdoom1-website

This export system provides the missing functionality identified in the website repository:

1. SUCCESS **Web Export Command**: `python -m src.leaderboard export --format web --output ./web_export/`
2. SUCCESS **API-Compatible JSON Format**: Matches website's expected leaderboard structure
3. SUCCESS **Privacy-Compliant Export**: Anonymous/pseudonymous options with configurable filtering
4. SUCCESS **Folder Structure**: Located in `tools/web_export/` as requested

### Website Integration Workflow

1. **Game Side**: Players play games, leaderboard data accumulates locally
2. **Export**: Run web export command to generate website-compatible JSON files
3. **Transfer**: Copy exported files to website repository's data directory
4. **Website Side**: Website displays leaderboards using the exported data via API endpoints

## Privacy & Security

### Anonymization Features
- **Deterministic Names**: Same player gets same anonymous lab name across exports
- **Lab Name Pool**: 20 realistic AI lab names for variety
- **Sensitive Data Rounding**: Financial/technical metrics rounded to preserve privacy
- **UUID Handling**: Can hash UUIDs in strict mode while preserving uniqueness

### Compliance
- **Opt-in Design**: Respects existing privacy manager settings
- **Data Minimization**: Only exports competitive game metrics
- **Purpose Limitation**: Data used only for leaderboards
- **Transparency**: Privacy manifest documents all filtering applied

## Technical Details

### Dependencies
- Uses existing `src.scores.enhanced_leaderboard` system
- Compatible with `src.services.leaderboard` privacy manager
- Leverages `src.services.version` for version tracking

### File Structure
```
tools/web_export/
|--- __init__.py              # Module interface
|--- export_leaderboards.py   # Main export functionality
|--- api_format.py           # Web format conversion
|--- privacy_filter.py       # Privacy controls
`--- README.md              # This documentation
```

### Error Handling
- Graceful handling of corrupted leaderboard files
- Detailed error reporting for debugging
- Fallback options for missing data
- Validation of export format

## Development

### Adding New Export Formats
To add support for new output formats, extend the `WebAPIFormatter` class in `api_format.py`.

### Customizing Privacy Controls
Modify the `PrivacyFilter` class in `privacy_filter.py` to adjust anonymization strategies.

### Testing Changes
```bash
# Test with sample data
python tools/web_export/api_format.py
python tools/web_export/privacy_filter.py

# Test full export
python tools/web_export/export_leaderboards.py --status
python tools/web_export/export_leaderboards.py --seed test-seed --output ./test_export/
```

## Status

SUCCESS **READY FOR PRODUCTION**

This web export system successfully provides the missing functionality needed to enable global leaderboards between the P(Doom)1 game and the pdoom1-website repository. All requirements from the website's integration specification have been implemented and tested.

The system is currently exporting **31 entries across 20 leaderboards** from actual game data, with full privacy protection and website-compatible formatting.
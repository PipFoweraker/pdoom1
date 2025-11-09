# PDoom1 Shared Data Schemas

This directory contains JSON Schema definitions for data integration between pdoom1 and pdoom-data repositories.

## Schema Files

### event.schema.json
Defines the structure for historical AI safety timeline events.

**Purpose**: Validate event data before integration into the game

**Required fields**:
- `id`: Unique event identifier (lowercase, underscores)
- `type`: Event category (paper_publication, conference, org_founding, funding, capability, governance)
- `date`: ISO 8601 date (YYYY-MM-DD)
- `year`: Event year
- `title`: Event title (max 200 chars)
- `description`: Brief description for game UI (max 500 chars)
- `source_url`: Reference URL
- `attribution`: Source citation

**Optional fields**:
- `month`, `day`: Numeric date components
- `detailed_description`: Extended context
- `game_impact`: Game mechanic effects (doom_change, reputation_change, money_change, triggers_research_unlock)
- `tags`: Categorization tags
- `related_orgs`: Associated organization IDs
- `related_people`: Associated researcher names

### organization.schema.json
Defines the structure for AI safety organizations.

**Purpose**: Validate organization data for game representation

**Required fields**:
- `id`: Unique organization identifier
- `name`: Organization name
- `type`: Category (safety, frontier, governance, academic, nonprofit)
- `description`: What the organization does

**Optional fields**:
- `founded_date`: ISO 8601 founding date
- `focus_areas`: Research areas (interpretability, alignment, governance, etc.)
- `funding_level`: Resource level (bootstrap, seed, well-funded, major)
- `website`: Organization website URL
- `source_url`: Reference URL
- `game_representation`: Game-specific flags (appears_as_rival, appears_as_partner, funding_events)

### researcher.schema.json
Defines the structure for researcher profiles.

**Purpose**: Validate researcher data for game characters and citations

**Required fields**:
- `id`: Unique researcher identifier
- `name`: Researcher name
- `specialization`: Primary area (safety, capabilities, interpretability, alignment, governance, policy, theory)

**Optional fields**:
- `affiliated_orgs`: Organization IDs
- `notable_work`: Array of publications (title, year, url)
- `public_profile`: Bio/profile URL
- `use_in_game`: Game usage flags (as_hireable_character, as_rival_researcher, name_in_papers)

## Usage

### Validation in Python

```python
import json
import jsonschema

# Load schema
with open('shared/schemas/event.schema.json') as f:
    event_schema = json.load(f)

# Load data to validate
with open('data/events/2018.json') as f:
    events_data = json.load(f)

# Validate
jsonschema.validate(instance=events_data, schema=event_schema)
```

### Integration with validate_historical_data.py

The validation script in `scripts/validate_historical_data.py` should be updated to use these schemas for comprehensive validation.

## Schema Versioning

Schemas follow semantic versioning via the `$id` field:
- Current: v1.0.0 (implicit - initial version)
- Breaking changes require major version bump
- New optional fields require minor version bump
- Documentation/fixes require patch version bump

## Related Documentation

- [PDOOM_DATA_INTEGRATION_PLAN.md](../../docs/guides/PDOOM_DATA_INTEGRATION_PLAN.md) - Overall integration strategy
- [validate_historical_data.py](../../scripts/validate_historical_data.py) - Validation script
- [PYTHON_TO_GODOT_MIGRATION.md](../../docs/PYTHON_TO_GODOT_MIGRATION.md) - Migration context

## CI/CD Integration

These schemas will be used in the CI/CD pipeline (Issue #439) to:
1. Validate all data before builds
2. Generate validation reports
3. Block deployment on schema violations
4. Track data quality metrics

## Contributing

When updating schemas:
1. Update the schema file
2. Update this README
3. Update validation scripts
4. Add/update tests
5. Document in CHANGELOG.md

**Note**: Schemas are shared between repositories. Changes should be coordinated between pdoom1 and pdoom-data teams.

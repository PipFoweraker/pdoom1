# Mechanics Documentation Workflow

This document describes the automated workflow for maintaining game mechanics documentation that stays in sync with the game code.

## Overview

The mechanics documentation system has three main components:

1. **Game Data Extraction** - Automatically extracts values from GDScript files
2. **Documentation Generation** - Updates markdown docs with current game data
3. **Website Export** - Prepares docs for pdoom-website consumption

## Files and Scripts

### Documentation Files
- [`docs/mechanics/README.md`](README.md) - Index of all mechanics
- [`docs/mechanics/reputation.md`](reputation.md) - Reputation & public opinion system
- [`docs/mechanics/.mechanics_data.json`](.mechanics_data.json) - Cached game data (auto-generated)

### Automation Scripts
- [`scripts/generate_mechanics_docs.py`](../../scripts/generate_mechanics_docs.py) - Extract game data and update docs
- [`scripts/sync_website_docs.py`](../../scripts/sync_website_docs.py) - Export docs for website
- [`.github/workflows/docs-sync.yml`](../../.github/workflows/docs-sync.yml) - CI automation

## Workflow

### 1. Making Game Code Changes

When you modify game constants or default values in GDScript files:

```bash
# Example: Change reputation starting value in game_state.gd
var reputation: float = 60.0  # Changed from 50.0
```

### 2. Update Documentation (Automatic)

The documentation will update automatically via CI/CD, but you can also run locally:

```bash
# Regenerate mechanics docs from current game code
python scripts/generate_mechanics_docs.py

# Check if docs are in sync (useful in pre-commit)
python scripts/generate_mechanics_docs.py --check
```

This updates [`docs/mechanics/reputation.md`](reputation.md) with the new value:

```markdown
## Game Data (Auto-Generated)

| Variable | Default Value | Type | Source |
|----------|---------------|------|--------|
| `reputation` | `60.0` | float | [godot/scripts/core/game_state.gd:10](../../godot/scripts/core/game_state.gd#L10) |
```

### 3. Export for Website

When ready to publish to the website:

```bash
# Export all docs to website format
python scripts/sync_website_docs.py

# Output goes to _website_export/docs/mechanics/
```

This creates website-ready markdown with:
- YAML front-matter for static site generators
- Transformed links for website navigation
- Image path corrections

### 4. Website Integration

The pdoom-website can pull from `_website_export/`:

```bash
# In pdoom-website repo
rsync -av ../pdoom1/_website_export/docs/ content/docs/

# Or use the manifest
python sync_from_pdoom1.py --manifest ../pdoom1/_website_export/manifest.json
```

## CI/CD Automation

The [`.github/workflows/docs-sync.yml`](../../.github/workflows/docs-sync.yml) workflow:

### On Pull Requests
- ✅ Checks if mechanics docs are in sync with game code
- ⚠️ **Fails the PR** if docs are out of sync
- 💬 Comments on PR with documentation preview
- 📦 Uploads website export as artifact

### On Main Branch Push
- 🔄 Auto-updates docs if game code changed
- 📝 Auto-commits updated docs
- 📦 Exports website docs

### Triggers
The workflow runs when these files change:
- `godot/scripts/core/game_state.gd`
- `godot/scripts/core/actions.gd`
- `godot/scripts/core/events.gd`
- `docs/mechanics/**`
- Documentation scripts

## Manual Override

If you need to edit documentation manually:

### Adding Narrative Content
Edit the markdown files directly - only the "Game Data (Auto-Generated)" section will be overwritten:

```markdown
# Reputation & Public Opinion

> Your narrative content here - won't be touched!

## Current Mechanics

Your strategic analysis here...

## Game Data (Auto-Generated)
<!-- This section will be regenerated -->
```

### Preventing Auto-Generation
To temporarily disable auto-generation for a file:

```python
# In scripts/generate_mechanics_docs.py
def update_reputation_doc(self, mechanic_data: MechanicData):
    """Update reputation.md with current game data."""
    # Comment this out to skip
    # doc_file = self.output_dir / "reputation.md"
    pass  # Temporarily disabled
```

## Adding New Mechanics Pages

To add a new mechanic (e.g., `funding.md`):

1. **Create the markdown file**:
```bash
touch docs/mechanics/funding.md
```

2. **Write the template**:
```markdown
# Funding & Investors

> **Status**: 🟡 Stub - Under active development

## Current Mechanics

### Game Data (Auto-Generated)
*Will be populated automatically*

## Planned Enhancements 🚧
...
```

3. **Add to the generator**:
```python
# In scripts/generate_mechanics_docs.py
def extract_all_data(self):
    mechanics = {
        "reputation": ...,
        "funding": MechanicData(  # NEW
            name="funding",
            constants={
                k: v for k, v in game_state_constants.items()
                if k == "money"  # Track money changes
            },
            description="Funding & Investors System",
            related_files=[
                "godot/scripts/core/game_state.gd",
                "godot/scripts/ui/funding_dialog.gd"  # If exists
            ],
            last_updated=datetime.now().isoformat()
        )
    }
```

4. **Add update method**:
```python
def generate_all(self):
    # ...
    self.update_reputation_doc(mechanics["reputation"])
    self.update_funding_doc(mechanics["funding"])  # NEW
```

5. **Run the generator**:
```bash
python scripts/generate_mechanics_docs.py
```

## Data Extraction Details

### Currently Extracted
- **Game State Variables**: Default values from `game_state.gd`
- **Constants**: Named constants from GDScript files
- **Source Locations**: File path and line number for each value

### Data Format (JSON Cache)
```json
{
  "reputation": {
    "name": "reputation",
    "description": "Reputation & Public Opinion System",
    "constants": {
      "reputation": {
        "name": "reputation",
        "value": 50.0,
        "type": "float",
        "source_file": "godot/scripts/core/game_state.gd",
        "line_number": 10,
        "comment": null
      }
    },
    "related_files": [...],
    "last_updated": "2025-11-26T16:08:51.123456"
  }
}
```

### Future Extraction Targets
- 🚧 Action costs and effects from `actions.gd`
- 🚧 Event probabilities from `events.gd`
- 🚧 Researcher trait definitions
- 🚧 Upgrade costs and effects

## Best Practices

### For Game Developers
1. **Add comments** to important constants in GDScript - they'll appear in docs
2. **Run `--check` before committing** to catch doc drift
3. **Don't edit auto-generated sections** - they'll be overwritten

### For Documentation Writers
1. **Focus on narrative/strategy** - let automation handle data
2. **Use stub status markers** to show work-in-progress
3. **Link to GitHub issues** for planned enhancements

### For CI/CD
1. **Keep docs in sync** - PRs fail if docs are stale
2. **Review auto-commits** on main branch for accuracy
3. **Download artifacts** to preview website exports

## Troubleshooting

### Docs out of sync
```bash
# Check what's out of sync
python scripts/generate_mechanics_docs.py --check

# Fix it
python scripts/generate_mechanics_docs.py
```

### CI workflow failing
- Check if you modified game values without regenerating docs
- Run `generate_mechanics_docs.py` locally and commit changes

### Wrong data extracted
- Check regex patterns in `GameDataExtractor` class
- Ensure GDScript follows expected format
- Add specific parsing logic if needed

---

**Last updated**: 2025-11-26
**Related Issues**: [#186 - Public Opinion & Media System](https://github.com/PipFoweraker/pdoom1/issues/186)

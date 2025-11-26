# Session Summary: Mechanics Documentation Workflow

**Date**: 2025-11-26
**Focus**: Automated game mechanics documentation with data extraction
**Related Issue**: [#186 - Public Opinion & Media System](https://github.com/PipFoweraker/pdoom1/issues/186)

## Overview

Created an automated documentation system that keeps player-facing game mechanics docs in sync with the actual game code. Documentation updates automatically when game constants change, ensuring accuracy and reducing maintenance overhead.

## What Was Built

### 1. Documentation Structure

Created `docs/mechanics/` for player-facing game mechanic documentation:

```
docs/mechanics/
├── README.md              # Index of all mechanics
├── reputation.md          # Reputation & public opinion (stub)
├── WORKFLOW.md           # Developer guide for the system
└── .mechanics_data.json  # Cached game data (auto-generated)
```

**Key Features:**
- Stub documentation for reputation mechanic (Issue #186)
- Auto-generated game data sections
- Status markers (🟢 Complete, 🟡 Stub, ⚪ Planned)
- Links to source code with line numbers
- Future enhancement tracking

### 2. Data Extraction Script

**File**: `scripts/generate_mechanics_docs.py`

**Capabilities:**
- Extracts default values from `game_state.gd`
- Parses GDScript variables with types and comments
- Generates markdown tables with current game values
- Creates JSON cache of extracted data
- Validates documentation sync with `--check` flag

**Example Output:**
```markdown
## Game Data (Auto-Generated)

| Variable | Default Value | Type | Source |
|----------|---------------|------|--------|
| `reputation` | `50.0` | float | [godot/scripts/core/game_state.gd:10](../../godot/scripts/core/game_state.gd#L10) |
```

**Data Tracked:**
- Resources: money, compute, research, papers, doom, action_points, stationery
- Personnel: safety_researchers, capability_researchers, compute_engineers, managers
- Reputation: reputation

### 3. Website Export Integration

**File**: `scripts/sync_website_docs.py` (enhanced)

**Changes:**
- Added `sync_mechanics_docs()` method
- Exports mechanics pages to `_website_export/docs/mechanics/`
- Adds YAML front-matter for static site generators
- Transforms links for website navigation

**Front-matter Example:**
```yaml
---
title: "Reputation & Public Opinion"
slug: "reputation"
category: "mechanics"
updated: "2025-11-26"
---
```

### 4. CI/CD Automation

**File**: `.github/workflows/docs-sync.yml`

**Workflow Triggers:**
- Game code changes in `godot/scripts/core/*.gd`
- Mechanics docs changes in `docs/mechanics/**`
- Documentation script changes
- Manual dispatch

**PR Checks:**
- ✅ Validates docs are in sync with code
- ⚠️ Fails PR if docs are stale
- 💬 Comments with documentation preview
- 📦 Uploads website export as artifact

**Main Branch:**
- 🔄 Auto-updates docs when game code changes
- 📝 Auto-commits updated documentation
- 📦 Exports website docs

## Technical Details

### Game Data Extraction

**Regex Pattern for Variables:**
```python
var_pattern = r'^var\s+(\w+):\s*(\w+)\s*=\s*([^#]+)(?:#\s*(.+))?'
```

Extracts:
- Variable name
- Type (float, int, String, etc.)
- Default value
- Inline comment (if present)

**Example Extraction:**
```gdscript
var reputation: float = 50.0  # Public opinion metric
```
→
```json
{
  "reputation": {
    "name": "reputation",
    "value": 50.0,
    "type": "float",
    "source_file": "godot/scripts/core/game_state.gd",
    "line_number": 10,
    "comment": "Public opinion metric"
  }
}
```

### Sync Check Logic

The `--check` flag compares:
1. Current game code values
2. Cached values in `.mechanics_data.json`
3. Reports differences for CI validation

**Exit codes:**
- `0` - Docs in sync
- `1` - Docs out of sync (triggers CI failure)

### Incremental Updates

The system only regenerates the "Game Data (Auto-Generated)" section:

```python
# Find and replace game data section
game_data_pattern = r'## Game Data \(Auto-Generated\).*?---\n\n'
content = re.sub(game_data_pattern, '', content, flags=re.DOTALL)

# Insert new data after "Current Mechanics" section
content = re.sub(
    current_mechanics_pattern,
    r'\1' + game_data_section,
    content,
    flags=re.DOTALL
)
```

**Preserves:**
- Narrative content
- Strategic analysis
- Planned enhancements
- Developer notes

**Replaces:**
- Game data tables
- Source code links
- Last updated timestamps

## Integration with Issue #186

The reputation documentation stub sets up for implementing the **Public Opinion & Media System** enhancement:

### Current State Documented
- Basic reputation tracking (0-100)
- Limited uses (funding, recruitment)
- Simple gain/loss mechanics

### Planned Enhancements Outlined
1. Multi-dimensional public sentiment
2. Media cycle events
3. PR action system
4. Strategic integration

### Documentation Ready For Implementation
When implementing Issue #186, developers can:
1. Update game code with new features
2. Run `generate_mechanics_docs.py` to extract new data
3. Expand narrative sections with new mechanics
4. Documentation stays accurate automatically

## Workflow Benefits

### For Developers
- **No manual doc updates** - Values sync automatically
- **CI catches drift** - PRs fail if docs are stale
- **Source code links** - Easy navigation to implementation
- **Version tracking** - JSON cache shows data changes

### For Players
- **Always accurate** - Docs match current game version
- **Clear source** - Links to exact code locations
- **Status visibility** - Know what's implemented vs planned
- **Strategic guidance** - Narrative content explains mechanics

### For Website
- **Clean export** - Ready for static site generators
- **Front-matter** - Proper categorization and metadata
- **Transformed links** - Website-compatible URLs
- **Artifact uploads** - Preview exports in PR

## Files Created/Modified

### New Files
- `docs/mechanics/README.md` - Mechanics index
- `docs/mechanics/reputation.md` - Reputation mechanic stub
- `docs/mechanics/WORKFLOW.md` - Developer workflow guide
- `docs/mechanics/.mechanics_data.json` - Data cache
- `scripts/generate_mechanics_docs.py` - Data extraction script
- `.github/workflows/docs-sync.yml` - CI automation

### Modified Files
- `scripts/sync_website_docs.py` - Added mechanics export

### Generated Files
- `_website_export/docs/mechanics/*` - Website export
- `_website_export/manifest.json` - Export manifest

## Usage Examples

### Update Docs Locally
```bash
# Regenerate from current game code
python scripts/generate_mechanics_docs.py

# Check if docs are in sync
python scripts/generate_mechanics_docs.py --check

# Export for website
python scripts/sync_website_docs.py
```

### Change Game Values
```gdscript
// In godot/scripts/core/game_state.gd
var reputation: float = 60.0  // Changed from 50.0
```

```bash
# Update docs
python scripts/generate_mechanics_docs.py

# Commit both changes
git add godot/scripts/core/game_state.gd docs/mechanics/
git commit -m "feat: Increase starting reputation to 60"
```

### Add New Mechanic
```bash
# 1. Create stub page
touch docs/mechanics/funding.md

# 2. Add to generator (scripts/generate_mechanics_docs.py)
# 3. Run generator
python scripts/generate_mechanics_docs.py

# 4. Website export
python scripts/sync_website_docs.py
```

## Future Enhancements

### Planned Extraction Targets
- **Action costs** - Parse `actions.gd` for AP/money costs
- **Event probabilities** - Extract event chances from `events.gd`
- **Researcher traits** - Document trait effects
- **Upgrade definitions** - Track upgrade costs and benefits
- **Doom sources** - Extract doom mechanics

### Advanced Features
- **Diff visualization** - Show value changes between versions
- **Historical tracking** - Graph value changes over time
- **Balance analysis** - Detect overpowered/underpowered mechanics
- **Formula extraction** - Parse complex calculations
- **Cross-reference validation** - Ensure related mechanics stay consistent

### Website Integration
- **Live preview** - Preview docs in PR comments
- **Search indexing** - Extract keywords for search
- **Interactive tables** - Sortable/filterable data
- **Version comparison** - Compare mechanics across versions

## Next Steps

1. **Implement Issue #186** - Build out public opinion system
   - Add multi-dimensional sentiment tracking
   - Create media cycle events
   - Implement PR actions
   - Update reputation.md with new features

2. **Expand Mechanic Coverage**
   - Create funding.md for investor relationships
   - Create personnel.md for hiring/management
   - Create doom.md for P(Doom) mechanics

3. **Enhance Extraction**
   - Parse action definitions from actions.gd
   - Extract event data from events.gd
   - Add trait/upgrade parsing

4. **Website Deployment**
   - Integrate with pdoom-website static site
   - Set up automated syncing from CI
   - Add search functionality

## Success Metrics

- ✅ Documentation auto-updates when game code changes
- ✅ CI catches documentation drift in PRs
- ✅ Website can consume exported docs
- ✅ Developers save time on doc maintenance
- ✅ Players get accurate, current information

## Related Issues

- [#186 - Public Opinion & Media System](https://github.com/PipFoweraker/pdoom1/issues/186) - Next enhancement to implement
- [#395 - Advanced Funding Relationship System](https://github.com/PipFoweraker/pdoom1/issues/395) - Future docs target
- [#437 - Automated Blog Publishing](https://github.com/PipFoweraker/pdoom1/issues/437) - Similar automation pattern

---

**Session completed**: 2025-11-26
**Time invested**: ~2 hours
**Lines of code**: ~600 (Python + YAML + Markdown)
**Files created**: 7
**Documentation pages**: 3 (with room for growth)

# pdoom-data Integration Plan
## Historical AI Safety Timeline Data Repository

**Created**: 2025-11-03
**Status**: Planning Phase
**Related Repository**: pdoom-data (separate repo for cleaned historical data)

---

## 1. Overview

### Philosophy
P(Doom) is a **strategic simulation game** set in a time loop starting July 1, 2017 (configurable). The game uses **real historical events** from the AI safety and capabilities landscape as the "default timeline" - what happens if the player takes no action. The player's goal is to improve upon this baseline p(doom) through strategic intervention.

### Data Flow Architecture
```
Alignment Research Dataset (external)
    ↓
pdoom-data repository (cleaning & transformation)
    ↓ [automated sync pipeline]
pdoom1 game repository (consumption & integration)
    ↓
Weekly builds & league cycles
```

### Key Principle
**Historical events are facts, not fiction.** We extract, clean, and integrate real:
- Safety paper publications
- Conference announcements
- Organization founding dates
- Funding rounds
- Capabilities milestones
- Governance developments

---

## 2. pdoom-data Repository Structure

### Proposed Directory Layout
```
pdoom-data/
├── README.md                          # Repository purpose and usage
├── LICENSE                            # Data licensing (likely MIT + attributions)
├── SOURCES.md                         # Attribution and source tracking
├── CONTRIBUTING.md                    # How to contribute data
│
├── raw/                               # Unprocessed source data
│   ├── alignment_research_dataset/    # From StampyAI
│   ├── arxiv_safety_papers/           # arXiv scrapes
│   ├── org_announcements/             # Press releases, blog posts
│   └── funding_trackers/              # Crunchbase, press releases
│
├── cleaned/                           # Processed, validated data
│   ├── events/
│   │   ├── safety_papers.json         # Paper publications with dates
│   │   ├── conferences.json           # AI safety conferences
│   │   ├── org_founding.json          # Organization launches
│   │   ├── funding_rounds.json        # Funding announcements
│   │   ├── capabilities.json          # Major AI capabilities milestones
│   │   └── governance.json            # Regulatory/policy events
│   │
│   ├── organizations/
│   │   ├── safety_orgs.json           # MIRI, FLI, CHAI, etc.
│   │   ├── frontier_labs.json         # OpenAI, Anthropic, DeepMind, etc.
│   │   └── governance_bodies.json     # Policy orgs
│   │
│   ├── people/
│   │   ├── researchers.json           # Real researcher names, specializations
│   │   └── thought_leaders.json       # Public figures in AI safety
│   │
│   └── concepts/
│       ├── alignment_topics.json      # Technical concepts from the field
│       ├── threat_models.json         # Real threat models discussed
│       └── research_agendas.json      # Actual research agendas
│
├── transformed/                       # Game-ready formats
│   ├── timeline_events/               # Events with game trigger logic
│   │   ├── 2017.json
│   │   ├── 2018.json
│   │   ├── 2019.json
│   │   ├── 2020.json
│   │   ├── 2021.json
│   │   ├── 2022.json
│   │   ├── 2023.json
│   │   ├── 2024.json
│   │   └── 2025.json
│   │
│   ├── researcher_profiles/           # Game character data
│   │   ├── safety_researchers.json
│   │   ├── capabilities_researchers.json
│   │   └── governance_researchers.json
│   │
│   └── event_templates/               # Reusable event structures
│       ├── paper_publication_template.json
│       ├── org_founding_template.json
│       └── funding_round_template.json
│
├── scripts/                           # Data processing tools
│   ├── extract_from_ard.py            # Alignment Research Dataset extraction
│   ├── validate_dates.py              # Date validation and normalization
│   ├── transform_for_game.py          # Convert to game format
│   ├── generate_timeline.py           # Create year-based timeline files
│   ├── sync_to_pdoom1.sh              # Copy transformed data to game repo
│   └── validate_data.py               # Schema validation
│
├── tests/                             # Data validation tests
│   ├── test_schema_validation.py
│   ├── test_date_parsing.py
│   └── test_game_integration.py
│
└── docs/
    ├── EXTRACTION_GUIDE.md            # How to extract from sources
    ├── TRANSFORMATION_SPEC.md         # Data format specifications
    ├── TIMELINE_COVERAGE.md           # What years/events are covered
    ├── INTEGRATION_API.md             # How pdoom1 consumes this data
    └── BUILD_PIPELINE.md              # Weekly build integration
```

---

## 3. Data Schema Specifications

### Event Schema (cleaned/events/*.json)
```json
{
  "events": [
    {
      "id": "unique_event_id",
      "type": "paper_publication | conference | org_founding | funding | capability | governance",
      "date": "YYYY-MM-DD",
      "year": 2017,
      "month": 7,
      "day": 1,
      "title": "Event Title",
      "description": "Brief description for game UI",
      "detailed_description": "Longer context for tooltips/logs",
      "source_url": "https://...",
      "attribution": "Source name",
      "game_impact": {
        "doom_change": 0.0,
        "reputation_change": 0,
        "money_change": 0,
        "triggers_research_unlock": false
      },
      "tags": ["interpretability", "governance", "gpt-release"],
      "related_orgs": ["OpenAI", "Anthropic"],
      "related_people": ["Paul Christiano", "Eliezer Yudkowsky"]
    }
  ]
}
```

### Organization Schema (cleaned/organizations/*.json)
```json
{
  "organizations": [
    {
      "id": "org_id",
      "name": "Organization Name",
      "type": "safety | frontier | governance",
      "founded_date": "YYYY-MM-DD",
      "description": "What they do",
      "focus_areas": ["interpretability", "alignment"],
      "funding_level": "bootstrap | well-funded | major",
      "website": "https://...",
      "source_url": "https://...",
      "game_representation": {
        "appears_as_rival": false,
        "appears_as_partner": true,
        "funding_events": ["event_id_1", "event_id_2"]
      }
    }
  ]
}
```

### Researcher Profile Schema (cleaned/people/researchers.json)
```json
{
  "researchers": [
    {
      "id": "researcher_id",
      "name": "Researcher Name",
      "specialization": "safety | capabilities | interpretability | alignment | governance",
      "affiliated_orgs": ["MIRI", "OpenAI"],
      "notable_work": [
        {
          "title": "Paper Title",
          "year": 2019,
          "url": "https://arxiv.org/..."
        }
      ],
      "public_profile": "https://...",
      "use_in_game": {
        "as_hireable_character": true,
        "as_rival_researcher": false,
        "name_in_papers": true
      }
    }
  ]
}
```

---

## 4. Game-Ready Timeline Format

### Timeline Event Format (transformed/timeline_events/2017.json)
```json
{
  "year": 2017,
  "default_timeline_events": [
    {
      "event_id": "openai_dota2_announcement",
      "trigger_date": "2017-08-11",
      "trigger_turn": 6,
      "trigger_condition": "always",
      "type": "capability_milestone",
      "name": "OpenAI Dota 2 Bot Announced",
      "description": "OpenAI announces bot that can beat amateur Dota 2 players",
      "game_effect": {
        "doom_increase": 2.0,
        "capability_research_boost": 5,
        "media_attention": true
      },
      "player_can_influence": false,
      "historical_fact": true,
      "source": "https://openai.com/blog/dota-2/"
    },
    {
      "event_id": "concrete_problems_in_ai_safety",
      "trigger_date": "2017-07-25",
      "trigger_turn": 4,
      "trigger_condition": "player_has_safety_researchers >= 1",
      "type": "paper_publication",
      "name": "Concrete Problems in AI Safety Published",
      "description": "Foundational safety research paper from DeepMind/OpenAI collaboration",
      "game_effect": {
        "doom_decrease": -1.0,
        "reputation_boost": 5,
        "unlocks_research_option": "interpretability_basics"
      },
      "player_can_influence": true,
      "historical_fact": true,
      "source": "https://arxiv.org/abs/1606.06565",
      "options": [
        {
          "id": "study_paper",
          "text": "Assign researchers to study this paper",
          "costs": {"action_points": 1},
          "effects": {"research": 10, "doom": -0.5}
        },
        {
          "id": "ignore",
          "text": "Note for later",
          "costs": {},
          "effects": {}
        }
      ]
    }
  ],
  "background_events": [
    {
      "event_id": "neurips_2017",
      "date": "2017-12-04",
      "name": "NeurIPS 2017 Conference",
      "description": "Major AI conference with safety track",
      "appears_in_log": true,
      "flavor_text_only": true
    }
  ]
}
```

---

## 5. Automated Sync Pipeline

### Pipeline Architecture
```
┌─────────────────────────────────────────────────────────┐
│ pdoom-data Repository                                   │
│                                                          │
│ 1. Manual/Scripted Data Entry                          │
│    ↓                                                     │
│ 2. Validation Scripts (test_*.py)                       │
│    ↓                                                     │
│ 3. Transformation Scripts (transform_for_game.py)       │
│    ↓                                                     │
│ 4. Generate Timeline Files (generate_timeline.py)       │
│    ↓                                                     │
│ 5. Git Commit & Push                                    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ Automated Sync (GitHub Actions)                         │
│                                                          │
│ On pdoom-data push:                                     │
│   - Trigger pdoom1 workflow                             │
│   - Clone both repos                                    │
│   - Run sync_to_pdoom1.sh                              │
│   - Create PR in pdoom1 with updated data              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ pdoom1 Repository                                       │
│                                                          │
│ 1. Receive updated data in shared/data/                │
│ 2. Run integration tests                                │
│ 3. Merge PR if tests pass                              │
│ 4. Weekly build includes new historical events         │
│ 5. Deploy to league/release cycle                       │
└─────────────────────────────────────────────────────────┘
```

### Sync Script (scripts/sync_to_pdoom1.sh)
```bash
#!/bin/bash
# Automated data sync from pdoom-data to pdoom1
# Usage: ./sync_to_pdoom1.sh [pdoom1_repo_path]

set -e  # Exit on error

PDOOM_DATA_REPO="$(pwd)"
PDOOM1_REPO="${1:-../pdoom1}"

echo "=== pdoom-data → pdoom1 Sync Pipeline ==="
echo "Source: $PDOOM_DATA_REPO"
echo "Target: $PDOOM1_REPO"

# Validate pdoom1 repo exists
if [ ! -d "$PDOOM1_REPO" ]; then
    echo "ERROR: pdoom1 repository not found at $PDOOM1_REPO"
    exit 1
fi

# Create target directories if they don't exist
mkdir -p "$PDOOM1_REPO/shared/data/historical_timeline"
mkdir -p "$PDOOM1_REPO/shared/data/researchers"
mkdir -p "$PDOOM1_REPO/shared/data/organizations"
mkdir -p "$PDOOM1_REPO/godot/data/historical_timeline"
mkdir -p "$PDOOM1_REPO/godot/data/researchers"
mkdir -p "$PDOOM1_REPO/godot/data/organizations"

# Sync timeline events (Python version)
echo "Syncing timeline events (Python)..."
rsync -av --delete \
  "$PDOOM_DATA_REPO/transformed/timeline_events/" \
  "$PDOOM1_REPO/shared/data/historical_timeline/"

# Sync timeline events (Godot version)
echo "Syncing timeline events (Godot)..."
rsync -av --delete \
  "$PDOOM_DATA_REPO/transformed/timeline_events/" \
  "$PDOOM1_REPO/godot/data/historical_timeline/"

# Sync researcher profiles (Python version)
echo "Syncing researcher profiles (Python)..."
rsync -av --delete \
  "$PDOOM_DATA_REPO/transformed/researcher_profiles/" \
  "$PDOOM1_REPO/shared/data/researchers/"

# Sync researcher profiles (Godot version)
echo "Syncing researcher profiles (Godot)..."
rsync -av --delete \
  "$PDOOM_DATA_REPO/transformed/researcher_profiles/" \
  "$PDOOM1_REPO/godot/data/researchers/"

# Sync organizations (Python version)
echo "Syncing organizations (Python)..."
rsync -av --delete \
  "$PDOOM_DATA_REPO/cleaned/organizations/" \
  "$PDOOM1_REPO/shared/data/organizations/"

# Sync organizations (Godot version)
echo "Syncing organizations (Godot)..."
rsync -av --delete \
  "$PDOOM_DATA_REPO/cleaned/organizations/" \
  "$PDOOM1_REPO/godot/data/organizations/"

# Generate sync manifest
echo "Generating sync manifest..."
cat > "$PDOOM1_REPO/shared/data/SYNC_MANIFEST.json" <<EOF
{
  "sync_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "pdoom_data_commit": "$(git -C $PDOOM_DATA_REPO rev-parse HEAD)",
  "files_synced": {
    "timeline_events": $(ls -1 "$PDOOM_DATA_REPO/transformed/timeline_events/" | wc -l),
    "researcher_profiles": $(ls -1 "$PDOOM_DATA_REPO/transformed/researcher_profiles/" | wc -l),
    "organizations": $(ls -1 "$PDOOM_DATA_REPO/cleaned/organizations/" | wc -l)
  }
}
EOF

echo "=== Sync Complete ==="
echo "Next steps:"
echo "  1. cd $PDOOM1_REPO"
echo "  2. Review changes: git diff"
echo "  3. Run tests: python -m pytest tests/"
echo "  4. Commit: git add shared/data godot/data && git commit -m 'chore: sync historical data from pdoom-data'"
```

### GitHub Actions Workflow (pdoom-data/.github/workflows/sync-to-pdoom1.yml)
```yaml
name: Sync Data to pdoom1

on:
  push:
    branches:
      - main
    paths:
      - 'transformed/**'
      - 'cleaned/**'
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout pdoom-data
        uses: actions/checkout@v4
        with:
          path: pdoom-data

      - name: Checkout pdoom1
        uses: actions/checkout@v4
        with:
          repository: PipFoweraker/pdoom1
          token: ${{ secrets.PDOOM1_PAT }}
          path: pdoom1

      - name: Run sync script
        run: |
          cd pdoom-data
          chmod +x scripts/sync_to_pdoom1.sh
          ./scripts/sync_to_pdoom1.sh ../pdoom1

      - name: Create Pull Request in pdoom1
        uses: peter-evans/create-pull-request@v5
        with:
          path: pdoom1
          token: ${{ secrets.PDOOM1_PAT }}
          commit-message: "chore: sync historical data from pdoom-data"
          branch: data-sync-${{ github.sha }}
          title: "Data Sync: Historical Timeline Update"
          body: |
            ## Automated Data Sync

            This PR contains updated historical timeline data from pdoom-data.

            **Source Commit**: ${{ github.sha }}
            **Sync Date**: ${{ github.event.head_commit.timestamp }}

            ### Changes
            - Timeline events updated
            - Researcher profiles updated
            - Organization data updated

            ### Validation
            Please ensure:
            - [ ] All JSON files are valid
            - [ ] Integration tests pass
            - [ ] No game-breaking changes

            **Auto-generated by pdoom-data sync workflow**
```

---

## 6. Build Integration for Weekly Launches

### Pre-Build Data Validation
```python
# pdoom1/scripts/validate_historical_data.py
"""
Pre-build validation script to ensure historical data integrity
Run during CI/CD before building releases
"""

import json
import os
from pathlib import Path
from datetime import datetime

def validate_timeline_files():
    """Ensure all timeline files are valid JSON with required fields"""
    timeline_dir = Path("shared/data/historical_timeline")
    errors = []

    for year_file in timeline_dir.glob("*.json"):
        try:
            with open(year_file) as f:
                data = json.load(f)

            # Validate structure
            if "year" not in data:
                errors.append(f"{year_file.name}: Missing 'year' field")

            if "default_timeline_events" not in data:
                errors.append(f"{year_file.name}: Missing 'default_timeline_events'")

            # Validate each event
            for event in data.get("default_timeline_events", []):
                required = ["event_id", "trigger_date", "type", "name"]
                for field in required:
                    if field not in event:
                        errors.append(
                            f"{year_file.name}/{event.get('event_id', 'unknown')}: "
                            f"Missing required field '{field}'"
                        )

        except json.JSONDecodeError as e:
            errors.append(f"{year_file.name}: Invalid JSON - {e}")
        except Exception as e:
            errors.append(f"{year_file.name}: Error - {e}")

    return errors

def validate_researchers():
    """Validate researcher profile data"""
    researcher_files = Path("shared/data/researchers").glob("*.json")
    errors = []

    for file in researcher_files:
        try:
            with open(file) as f:
                data = json.load(f)

            for researcher in data.get("researchers", []):
                if "id" not in researcher or "name" not in researcher:
                    errors.append(
                        f"{file.name}: Researcher missing id or name"
                    )

        except Exception as e:
            errors.append(f"{file.name}: Error - {e}")

    return errors

if __name__ == "__main__":
    print("=== Validating Historical Data ===")

    timeline_errors = validate_timeline_files()
    researcher_errors = validate_researchers()

    all_errors = timeline_errors + researcher_errors

    if all_errors:
        print("\n❌ VALIDATION FAILED\n")
        for error in all_errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("\n✅ All historical data validated successfully")
        exit(0)
```

### Weekly Build Integration
```yaml
# pdoom1/.github/workflows/weekly-release.yml
name: Weekly Release Build

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight UTC
  workflow_dispatch:

jobs:
  validate-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Validate historical data
        run: python scripts/validate_historical_data.py

  build-python:
    needs: validate-data
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests with historical data
        run: python -m pytest tests/ -v

      - name: Build executable
        run: python -m PyInstaller pdoom.spec

      - name: Upload Python build
        uses: actions/upload-artifact@v3
        with:
          name: pdoom-python-weekly
          path: dist/

  build-godot:
    needs: validate-data
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Godot
        uses: chickensoft-games/setup-godot@v1
        with:
          version: 4.3

      - name: Verify historical data in Godot
        run: |
          godot --headless --script scripts/verify_godot_data.gd

      - name: Export Godot builds
        run: |
          mkdir -p build
          godot --headless --export-release "Windows Desktop" build/pdoom-windows.exe
          godot --headless --export-release "Linux/X11" build/pdoom-linux.x86_64

      - name: Upload Godot builds
        uses: actions/upload-artifact@v3
        with:
          name: pdoom-godot-weekly
          path: build/

  create-release:
    needs: [build-python, build-godot]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download all artifacts
        uses: actions/download-artifact@v3

      - name: Generate release notes
        run: |
          echo "# P(Doom) Weekly Release - $(date +%Y-%m-%d)" > RELEASE_NOTES.md
          echo "" >> RELEASE_NOTES.md
          echo "## Historical Data Status" >> RELEASE_NOTES.md
          cat shared/data/SYNC_MANIFEST.json >> RELEASE_NOTES.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: weekly-${{ github.run_number }}
          name: Weekly Build - $(date +%Y-%m-%d)
          body_path: RELEASE_NOTES.md
          files: |
            pdoom-python-weekly/*
            pdoom-godot-weekly/*
```

---

## 7. Documentation Standards

### Required Documentation in pdoom-data

#### README.md Template
```markdown
# pdoom-data

Historical AI Safety & Capabilities Timeline Data

## Purpose

This repository contains curated historical data about AI safety research,
capabilities development, and governance events from 2017 onwards. The data
is used by the P(Doom) strategic simulation game to create an accurate
historical timeline.

## Structure

- `raw/` - Original source data (for attribution)
- `cleaned/` - Processed, validated data
- `transformed/` - Game-ready formats
- `scripts/` - Data processing tools

## Usage

### For Game Developers

Data automatically syncs to pdoom1 repository via GitHub Actions.

### For Contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add historical events.

### For Researchers

All data includes source attribution. See [SOURCES.md](SOURCES.md) for
complete bibliography.

## Data Quality

- All dates verified against primary sources
- 100% source attribution required
- Automated validation on every commit
- Community review process for new events

## License

Data: CC-BY 4.0 (facts + descriptions)
Code: MIT

See [LICENSE](LICENSE) for details.
```

#### SOURCES.md Template
```markdown
# Data Sources

## Primary Sources

### Alignment Research Dataset
- **Source**: https://github.com/StampyAI/alignment-research-dataset
- **Version**: v2.1
- **License**: MIT
- **Coverage**: 2017-2025 safety research papers

### Organization Announcements
- OpenAI Blog: https://openai.com/blog
- Anthropic News: https://anthropic.com/news
- DeepMind Blog: https://deepmind.google/discover/blog/

### Funding Data
- Crunchbase AI Safety Companies
- Public funding announcements (press releases)

### Governance Events
- EU AI Act timeline
- US AI Executive Orders
- International agreements

## Attribution Requirements

Every event in this repository includes:
1. Primary source URL
2. Extraction date
3. Verification method
4. License information

## Data Integrity

All dates cross-referenced with multiple sources where possible.
```

#### CONTRIBUTING.md Template
```markdown
# Contributing to pdoom-data

## Adding Historical Events

### Requirements
1. Event must have occurred between July 1, 2017 and present
2. Event must be verifiable with primary source
3. Event must be relevant to AI safety/capabilities/governance

### Process

1. **Research**: Find primary source (paper, announcement, press release)

2. **Create Event**: Add to appropriate file in `cleaned/events/`
   ```json
   {
     "id": "unique_event_id",
     "type": "paper_publication",
     "date": "2019-07-15",
     "title": "Event Title",
     "source_url": "https://...",
     "attribution": "Source name"
   }
   ```

3. **Validate**: Run validation script
   ```bash
   python scripts/validate_data.py
   ```

4. **Submit PR**: Include verification in PR description

### Review Process

1. Automated validation checks
2. Community review (2 approvals required)
3. Source verification
4. Integration test with pdoom1

## Questions?

Open an issue or contact maintainers.
```

---

## 8. Implementation Roadmap

### Week 1: Foundation (Nov 4-10, 2025)
- [x] Write integration plan
- [ ] Create GitHub issue for documentation refinement (remove "satirical")
- [ ] Request access to Alignment Research Dataset
- [ ] Design data schemas
- [ ] Create pdoom-data repository structure

### Week 2: Initial Data Extraction (Nov 11-17, 2025)
- [ ] Extract 2017-2019 events from Alignment Research Dataset
- [ ] Identify 20-30 key historical events
- [ ] Create validation scripts
- [ ] Write initial documentation (README, SOURCES, CONTRIBUTING)

### Week 3: Transformation Pipeline (Nov 18-24, 2025)
- [ ] Build transformation scripts (cleaned → transformed)
- [ ] Generate first timeline JSON files
- [ ] Create sync script (pdoom-data → pdoom1)
- [ ] Write integration tests

### Week 4: pdoom1 Integration (Nov 25-Dec 1, 2025)
- [ ] Update pdoom1 to load timeline data
- [ ] Implement TimelineManager (Python + Godot)
- [ ] Add data validation to CI/CD
- [ ] Test historical event triggering

### Week 5: Automation (Dec 2-8, 2025)
- [ ] Set up GitHub Actions for auto-sync
- [ ] Integrate with weekly build pipeline
- [ ] Create PR automation
- [ ] Document build process

### Week 6: Launch (Dec 9-15, 2025)
- [ ] Deploy first weekly build with historical data
- [ ] Monitor for issues
- [ ] Gather community feedback
- [ ] Plan expansion to 2020-2025

---

## 9. Success Metrics

### Data Repository (pdoom-data)
- ✅ 50+ historical events per year (2017-2025)
- ✅ 100% source attribution
- ✅ <5% validation error rate
- ✅ Automated sync to pdoom1
- ✅ Community contribution process

### Game Integration (pdoom1)
- ✅ Historical events trigger correctly by date
- ✅ Player can influence some events
- ✅ Default timeline = realistic doom trajectory
- ✅ No build failures due to data issues
- ✅ Weekly releases include updated data

### Development Workflow
- ✅ Zero manual copy-paste between repos
- ✅ Automated validation catches errors
- ✅ PR process for data updates
- ✅ Integration tests verify game compatibility
- ✅ Build pipeline includes data checks

---

## 10. Risk Mitigation

### Potential Issues

**Data Quality**
- Risk: Inaccurate dates or attributions
- Mitigation: Multi-source verification, community review

**Legal/Ethics**
- Risk: Using real names without permission
- Mitigation: Public figures only, factual information, opt-out process

**Build Failures**
- Risk: Bad data breaks weekly builds
- Mitigation: Validation scripts, staging environment, rollback process

**Sync Failures**
- Risk: Data out of sync between repos
- Mitigation: Automated sync, manifest files, version tracking

**Code Sprawl**
- Risk: Duplicate code in both repos
- Mitigation: Clear separation (data vs game logic), documentation

---

## Next Actions

### Immediate (Today)
1. Write this plan ✅
2. Create GitHub issue for documentation refinement
3. Request WebFetch access to examine Alignment Research Dataset

### Short-term (This Week)
4. Create pdoom-data repository skeleton
5. Write first 5-10 sample events (2017-2018)
6. Build sync script prototype
7. Test integration with pdoom1

### Medium-term (Next 2 Weeks)
8. Extract full 2017-2019 timeline
9. Set up GitHub Actions
10. Integrate with weekly build
11. Document everything

---

**Last Updated**: 2025-11-03
**Status**: Active Implementation
**Next Review**: 2025-11-10
